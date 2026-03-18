#!/usr/bin/env python3
"""
AlphaAI Viral Ad Generator - Simplified Version
Creates high-converting short-form vertical ads for TikTok/Instagram/YouTube Shorts
"""

import subprocess
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "ads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_DIR = Path(__file__).parent / "marketing_assets" / "videos"

# Hooks for different variations
HOOKS = {
    "main": "This AI trades crypto\\nfor you 24/7",
    "v1": "I built an AI that\\ntrades crypto for me",
    "v2": "This bot\\nnever sleeps",
    "v3": "Stop trading\\nmanually"
}

def create_viral_ad(hook_key, hook_text, output_name):
    """Create a single viral ad video with text overlays"""
    print(f"\n🎬 Creating: {output_name}")
    print(f"   Hook: {hook_text.replace(chr(92)+'n', ' ')}")
    
    input_video = VIDEO_DIR / "agents_showcase.mp4"
    output_video = OUTPUT_DIR / f"{output_name}.mp4"
    
    if not input_video.exists():
        print(f"   ❌ Source video not found: {input_video}")
        return None
    
    # Build complex filter with all text overlays
    # Text timing: Hook(0-2), Problem(2-5), Solution(5-9), Proof(9-13), CTA(13-16)
    
    filter_complex = f'''
[0:v]
scale=1280:720,
crop=405:720:437:0,
scale=720:1280,
drawtext=text='{hook_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,2)',
drawtext=text='Most people lose money\\ntrading...':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=44:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,2,5)',
drawtext=text='AlphaAI uses multiple\\nAI agents to scan markets':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=38:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.15:enable='between(t,5,7.5)',
drawtext=text='and find trades\\nautomatically':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=38:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.15:enable='between(t,7.5,9)',
drawtext=text='+12%% last month':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=56:fontcolor=#00FF94:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-50:enable='between(t,9,11)',
drawtext=text='(paper trading)':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=32:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+30:enable='between(t,9,11)',
drawtext=text='Live signals. Real data.':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=40:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,11,13)',
drawtext=text='Try it free':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=#00FF94:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,13,16)',
drawtext=text='link in bio':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=36:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+40:enable='between(t,13,16)'
[outv]
'''.replace('\n', '')
    
    # FFmpeg command
    cmd = [
        "/usr/bin/ffmpeg", "-y",
        "-i", str(input_video),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-t", "16",
        "-r", "30",
        str(output_video)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            size_mb = os.path.getsize(output_video) / (1024 * 1024)
            print(f"   ✅ Created: {output_video.name} ({size_mb:.1f} MB)")
            return str(output_video)
        else:
            print(f"   ❌ FFmpeg error")
            print(f"   {result.stderr[-800:]}")
            return None
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout")
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def create_all_ads():
    """Create all ad variations"""
    print("=" * 60)
    print("🚀 AlphaAI Viral Ad Generator")
    print("   Creating TikTok/Reels vertical ads (720x1280)")
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
        print(f"   - {r['name']}")
    
    print(f"\n📁 Output: {OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    create_all_ads()
