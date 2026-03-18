#!/usr/bin/env python3
"""
AlphaAI Viral Ad Generator
Creates high-converting short-form ads for TikTok/Instagram/YouTube Shorts
"""

import subprocess
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "ads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_DIR = Path(__file__).parent / "marketing_assets" / "videos"
AUDIO_DIR = Path(__file__).parent / "marketing_assets" / "audio"

# Hooks for different variations
HOOKS = {
    "main": "This AI trades crypto for you 24/7",
    "v1": "I built an AI that trades crypto for me...",
    "v2": "This bot never sleeps...",
    "v3": "Stop trading manually..."
}

# Text overlays with timestamps (start, end, text, position)
# Position: "top", "center", "bottom"
TEXT_OVERLAYS = [
    # HOOK (0-2s)
    (0, 2, "{hook}", "center", "large"),
    
    # PROBLEM (2-5s)
    (2, 5, "Most people lose money trading...", "center", "medium"),
    
    # SOLUTION (5-9s)
    (5, 7, "AlphaAI uses multiple AI agents", "top", "medium"),
    (7, 9, "to scan markets and find trades automatically", "top", "medium"),
    
    # PROOF (9-13s)
    (9, 11, "+12% last month (paper trading)", "center", "large"),
    (11, 13, "Live signals. Real data.", "center", "medium"),
    
    # CTA (13-16s)
    (13, 16, "Try it free — link in bio", "center", "large"),
]


def create_drawtext_filter(text, start, end, position, size):
    """Create ffmpeg drawtext filter for text overlay"""
    
    # Font sizes
    sizes = {
        "large": 56,
        "medium": 42,
        "small": 32
    }
    fontsize = sizes.get(size, 42)
    
    # Position calculations for 720x1280 vertical video
    if position == "top":
        y_pos = "h*0.12"
    elif position == "center":
        y_pos = "(h-text_h)/2"
    else:  # bottom
        y_pos = "h*0.82"
    
    # Escape special characters for ffmpeg
    escaped_text = text.replace("'", "'\\''").replace(":", "\\:")
    
    # Create drawtext filter with fade in/out
    filter_str = (
        f"drawtext=text='{escaped_text}':"
        f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"fontsize={fontsize}:"
        f"fontcolor=white:"
        f"borderw=3:"
        f"bordercolor=black:"
        f"x=(w-text_w)/2:"
        f"y={y_pos}:"
        f"enable='between(t,{start},{end})':"
        f"alpha='if(lt(t,{start}+0.3),t-{start},if(gt(t,{end}-0.3),{end}-t,1))*3'"
    )
    
    return filter_str


def create_viral_ad(hook_key, hook_text, output_name):
    """Create a single viral ad video"""
    print(f"\n🎬 Creating: {output_name}")
    print(f"   Hook: {hook_text}")
    
    input_video = VIDEO_DIR / "agents_showcase.mp4"
    output_video = OUTPUT_DIR / f"{output_name}.mp4"
    
    if not input_video.exists():
        print(f"   ❌ Source video not found: {input_video}")
        return None
    
    # Build text overlay filters
    text_filters = []
    for start, end, text, pos, size in TEXT_OVERLAYS:
        # Replace {hook} placeholder with actual hook text
        actual_text = text.replace("{hook}", hook_text)
        text_filters.append(create_drawtext_filter(actual_text, start, end, pos, size))
    
    # Combine all text filters
    text_filter_chain = ",".join(text_filters)
    
    # Complete filter chain:
    # 1. Scale and crop to 9:16 (720x1280) - crop center of landscape video
    # 2. Add subtle zoom effect
    # 3. Add all text overlays
    filter_complex = (
        # Crop center to approximate 9:16 from 16:9, then scale
        "[0:v]scale=1280:720,crop=405:720:437:0,scale=720:1280,"
        # Add slight zoom pulse effect
        "zoompan=z='1+0.02*sin(2*PI*t/4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=30,"
        # Add all text overlays
        f"{text_filter_chain}"
        "[outv]"
    )
    
    # FFmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_video),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-t", "16",  # 16 seconds
        "-r", "30",
        str(output_video)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            size_mb = os.path.getsize(output_video) / (1024 * 1024)
            print(f"   ✅ Created: {output_video} ({size_mb:.1f} MB)")
            return str(output_video)
        else:
            print(f"   ❌ FFmpeg error: {result.stderr[-500:]}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def create_all_ads():
    """Create all ad variations"""
    print("=" * 60)
    print("🚀 AlphaAI Viral Ad Generator")
    print("   Creating high-converting TikTok/Reels ads")
    print("=" * 60)
    
    results = []
    
    for key, hook in HOOKS.items():
        output_name = f"alphaai_ad_{key}"
        result = create_viral_ad(key, hook, output_name)
        results.append({"name": output_name, "hook": hook, "path": result})
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Generation Summary")
    print("=" * 60)
    
    successful = [r for r in results if r["path"]]
    print(f"\n✅ Created {len(successful)}/{len(results)} ads")
    
    for r in successful:
        print(f"   - {r['name']}: \"{r['hook'][:30]}...\"")
    
    print(f"\n📁 Output: {OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    create_all_ads()
