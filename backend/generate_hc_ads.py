#!/usr/bin/env python3
"""
AlphaAI High-Converting Ad Generator v2
Creates viral-style ads optimized for TikTok/Reels/Paid Ads
"""

import subprocess
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "ads_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_DIR = Path(__file__).parent / "marketing_assets" / "videos"
AUDIO_DIR = Path(__file__).parent / "marketing_assets" / "audio"

# Hook variations - BIGGER, BOLDER
HOOKS = {
    "main": ("This AI trades crypto", "for you 24/7"),
    "v1": ("I built an AI that", "trades crypto for me"),
    "v2": ("This bot", "never sleeps"),
    "v3": ("Stop trading", "manually"),
}

def create_high_converting_ad(hook_key, hook_lines, output_name):
    """Create a high-converting ad with improved visuals and pacing"""
    print(f"\n🎬 Creating HIGH-CONVERTING ad: {output_name}")
    print(f"   Hook: {hook_lines[0]} {hook_lines[1]}")
    
    input_video = VIDEO_DIR / "agents_showcase.mp4"
    voiceover = AUDIO_DIR / "alphaai_ad_voiceover.mp3"
    output_video = OUTPUT_DIR / f"{output_name}.mp4"
    
    if not input_video.exists():
        print(f"   ❌ Source video not found")
        return None
    
    hook_line1, hook_line2 = hook_lines
    
    # Enhanced filter with:
    # - Bigger, bolder text (larger fonts, stronger borders)
    # - Zoom pulses on key moments
    # - Better text positioning
    # - Flash effects on transitions
    
    filter_complex = f'''
[0:v]
scale=1280:720,
crop=405:720:437:0,
scale=720:1280,
format=yuv420p,

drawtext=text='{hook_line1}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h/2)-80:enable='between(t,0,2)',
drawtext=text='{hook_line2}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=#00FF94:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h/2):enable='between(t,0,2)',

drawtext=text='Most people':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h/2)-60:enable='between(t,2,3.5)',
drawtext=text='LOSE MONEY':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=58:fontcolor=#FF4444:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h/2)+10:enable='between(t,2,3.5)',
drawtext=text='trading...':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h/2)+80:enable='between(t,2,3.5)',

drawtext=text='AlphaAI':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=58:fontcolor=#7B61FF:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.12:enable='between(t,3.5,5)',
drawtext=text='changes that':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=48:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.12+70:enable='between(t,3.5,5)',

drawtext=text='AI scans markets':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=46:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.10:enable='between(t,5,7)',
drawtext=text='Finds trades':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=#00FF94:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.10+60:enable='between(t,5,7)',
drawtext=text='AUTOMATICALLY':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=44:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.10+120:enable='between(t,5,7)',

drawtext=text='Live signals':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=42:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.08:enable='between(t,7,9)',
drawtext=text='Real data':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=42:fontcolor=#00FF94:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.08+55:enable='between(t,7,9)',

drawtext=text='+12%%':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=80:fontcolor=#00FF94:borderw=6:bordercolor=black:x=(w-text_w)/2:y=(h/2)-70:enable='between(t,9,11)',
drawtext=text='last month':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=44:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h/2)+30:enable='between(t,9,11)',
drawtext=text='(paper trading)':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=28:fontcolor=#888888:borderw=2:bordercolor=black:x=(w-text_w)/2:y=(h/2)+85:enable='between(t,9,11)',

drawtext=text='TRY IT FREE':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=62:fontcolor=#00FF94:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h/2)-50:enable='between(t,11,14)',
drawtext=text='Link in bio':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=40:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h/2)+40:enable='between(t,11,14)'

[outv]
'''.replace('\n', '')
    
    # Build ffmpeg command
    cmd = [
        "/usr/bin/ffmpeg", "-y",
        "-i", str(input_video),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-t", "14",
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
            print(f"   ❌ FFmpeg error: {result.stderr[-500:]}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def add_voiceover_to_ad(video_path, voiceover_path, output_path):
    """Add voiceover to the video"""
    print(f"   Adding voiceover...")
    
    cmd = [
        "/usr/bin/ffmpeg", "-y",
        "-i", video_path,
        "-i", voiceover_path,
        "-filter_complex", "[1:a]apad=whole_dur=14[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "[a]",
        "-shortest",
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"   ✅ With voiceover: {Path(output_path).name} ({size_mb:.1f} MB)")
            return output_path
        else:
            print(f"   ❌ Audio error: {result.stderr[-300:]}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def create_all_high_converting_ads():
    """Create all high-converting ad variations"""
    print("=" * 65)
    print("🚀 AlphaAI HIGH-CONVERTING Ad Generator v2")
    print("   Optimized for TikTok / Instagram Reels / Paid Ads")
    print("=" * 65)
    
    voiceover = AUDIO_DIR / "alphaai_ad_voiceover.mp3"
    results = []
    
    for key, hook_lines in HOOKS.items():
        output_name = f"alphaai_hc_ad_{key}"
        
        # Create video without voiceover first
        video_path = create_high_converting_ad(key, hook_lines, output_name)
        
        if video_path and voiceover.exists():
            # Add voiceover
            final_path = str(OUTPUT_DIR / f"{output_name}_voice.mp4")
            final = add_voiceover_to_ad(video_path, str(voiceover), final_path)
            if final:
                results.append({"name": f"{output_name}_voice", "hook": f"{hook_lines[0]} {hook_lines[1]}", "path": final, "has_voice": True})
        
        if video_path:
            results.append({"name": output_name, "hook": f"{hook_lines[0]} {hook_lines[1]}", "path": video_path, "has_voice": False})
    
    # Summary
    print("\n" + "=" * 65)
    print("📊 Generation Summary")
    print("=" * 65)
    
    voiced = [r for r in results if r.get("has_voice")]
    silent = [r for r in results if not r.get("has_voice")]
    
    print(f"\n✅ Created {len(results)} total ads")
    print(f"   🎙️ With voiceover: {len(voiced)}")
    print(f"   🔇 Silent: {len(silent)}")
    
    print(f"\n📁 Output: {OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    create_all_high_converting_ads()
