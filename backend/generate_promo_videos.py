#!/usr/bin/env python3
"""
AlphaAI Promotional Video Generator using Sora 2
Creates professional promo videos for social media platforms
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

# Output directory
OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Video prompts for AlphaAI - designed for different social media platforms
VIDEO_PROMPTS = {
    # Main promotional video - Hero style
    "hero_promo": {
        "prompt": """
            Cinematic tech advertisement for AlphaAI crypto hedge fund.
            Open with a glowing neural network brain in dark space, pulsing with purple and green energy.
            The brain transforms into a constellation of connected nodes representing blockchain.
            Camera zooms through digital trading dashboards showing rising charts and candlesticks.
            Bitcoin and Ethereum symbols orbit around a central futuristic vault.
            Sleek AI robots analyze holographic market data in a command center.
            End with the brain-blockchain hybrid glowing brighter, radiating success.
            Color palette: deep navy, electric purple (#7B61FF), neon green (#00FF94), gold accents.
            Professional, premium, cutting-edge fintech aesthetic. No text overlays.
        """,
        "size": "1792x1024",  # Widescreen for YouTube/website
        "duration": 8
    },
    
    # Instagram/TikTok vertical video
    "social_vertical": {
        "prompt": """
            Vertical video for social media showcasing AI trading technology.
            Sleek futuristic interface with holographic trading charts floating in dark space.
            Purple and green glowing neural pathways connect different data points.
            A sophisticated AI assistant robot with a glowing chest emblem analyzes crypto markets.
            Coins (Bitcoin, Ethereum) flow through secure digital pathways into a vault.
            Dynamic camera movements, modern transitions, premium fintech feel.
            Color scheme: dark background, purple (#7B61FF), neon green (#00FF94).
            Fast-paced, engaging, suitable for short-form social content. No text.
        """,
        "size": "1024x1792",  # Portrait for Instagram Reels/TikTok
        "duration": 4
    },
    
    # Square video for Instagram/Twitter feed
    "social_square": {
        "prompt": """
            Square format video for social media feed.
            Central focus: A glowing AI brain made of circuits, surrounded by orbiting cryptocurrency symbols.
            The brain pulses with intelligence, analyzing market patterns shown as flowing data streams.
            Secure blockchain vault materializes, showing fund security and transparency.
            Four AI agents appear briefly - each with different colored glows (purple, cyan, gold, green).
            Premium dark theme with electric purple and green neon accents.
            Smooth, hypnotic motion perfect for auto-play feeds. No text overlays.
        """,
        "size": "1024x1024",  # Square for Instagram/Twitter
        "duration": 4
    },
    
    # Trading agents showcase
    "agents_showcase": {
        "prompt": """
            Showcase of AI trading agents in a futuristic command center.
            Four sophisticated robots stand at holographic workstations in a dark tech environment.
            Each robot has distinct glowing colors: purple (Arbitrage), cyan (Momentum), gold (Research), green (Funding).
            They analyze different trading strategies on floating holographic screens.
            Camera pans across the room showing their coordinated work.
            Data flows between them as green streams of light.
            Professional, powerful, showcasing autonomous AI trading capabilities.
            Dark background with purple and green accent lighting. No text.
        """,
        "size": "1280x720",  # Standard HD
        "duration": 8
    }
}


def generate_video(name: str, config: dict) -> str:
    """Generate a single promotional video"""
    print(f"\n🎬 Generating video: {name}")
    print(f"   Size: {config['size']}, Duration: {config['duration']}s")
    print(f"   This may take 3-5 minutes...")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        print("   ❌ EMERGENT_LLM_KEY not found in environment")
        return None
    
    try:
        # Create video generator
        video_gen = OpenAIVideoGeneration(api_key=api_key)
        
        # Generate video
        output_path = str(OUTPUT_DIR / f"{name}.mp4")
        
        video_bytes = video_gen.text_to_video(
            prompt=config["prompt"].strip(),
            model="sora-2",
            size=config["size"],
            duration=config["duration"],
            max_wait_time=600  # 10 minutes max
        )
        
        if video_bytes:
            video_gen.save_video(video_bytes, output_path)
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"   ✅ Video saved: {output_path} ({file_size:.1f} MB)")
            return output_path
        else:
            print(f"   ❌ No video bytes returned")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def generate_all_videos():
    """Generate all promotional videos"""
    print("=" * 70)
    print("🎬 AlphaAI Promotional Video Generator")
    print("   Using Sora 2 via Emergent LLM Key")
    print("=" * 70)
    
    results = []
    
    for name, config in VIDEO_PROMPTS.items():
        result = generate_video(name, config)
        results.append({
            "name": name,
            "success": result is not None,
            "path": result,
            "size": config["size"],
            "duration": config["duration"]
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Generation Summary")
    print("=" * 70)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for r in successful:
        print(f"   - {r['name']}: {r['path']}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for r in failed:
            print(f"   - {r['name']}")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    return results


def generate_single(video_name: str):
    """Generate a single video by name"""
    if video_name not in VIDEO_PROMPTS:
        print(f"❌ Unknown video: {video_name}")
        print(f"   Available: {', '.join(VIDEO_PROMPTS.keys())}")
        return None
    
    return generate_video(video_name, VIDEO_PROMPTS[video_name])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_name = sys.argv[1]
        generate_single(video_name)
    else:
        # Generate just the main hero promo by default (saves credits)
        print("Generating hero promotional video...")
        generate_single("hero_promo")
