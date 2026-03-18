#!/usr/bin/env python3
"""
AlphaAI Voiceover Generator
Creates professional voiceover for the promotional video
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from emergentintegrations.llm.openai import OpenAITextToSpeech

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Professional voiceover script for 28-second video
# Timed to match video sections
VOICEOVER_SCRIPT = """
Introducing AlphaAI. The future of autonomous crypto trading.

AlphaAI is a decentralized hedge fund powered by artificial intelligence. 
Our platform deploys four specialized AI trading agents that work around the clock, 
analyzing markets, executing trades, and managing risk automatically.

The Arbitrage Agent captures price differences across exchanges.
The Momentum Agent rides market trends for maximum gains.
The Funding Agent optimizes yield through DeFi protocols.
And our Research Lab continuously generates and tests new strategies.

Your capital is secured by smart contracts on the blockchain, 
with complete transparency and full investor control.

AlphaAI. Intelligent investing. Autonomous returns. The future of trading is here.
"""

# Shorter version for social media (15 seconds)
SHORT_SCRIPT = """
AlphaAI. The future of autonomous crypto trading.

Four AI agents working 24/7. Analyzing markets. Executing trades. Managing risk.

Your capital secured by blockchain smart contracts.

AlphaAI. Intelligent investing. The future is here.
"""


async def generate_voiceover(script: str, filename: str, voice: str = "onyx"):
    """Generate voiceover audio from script"""
    print(f"\n🎙️ Generating voiceover: {filename}")
    print(f"   Voice: {voice}")
    print(f"   Script length: {len(script)} characters")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        print("   ❌ EMERGENT_LLM_KEY not found")
        return None
    
    try:
        tts = OpenAITextToSpeech(api_key=api_key)
        
        # Generate high-quality speech
        audio_bytes = await tts.generate_speech(
            text=script.strip(),
            model="tts-1-hd",  # High definition quality
            voice=voice,       # Deep, authoritative voice
            speed=0.95,        # Slightly slower for clarity
            response_format="mp3"
        )
        
        # Save audio file
        output_path = OUTPUT_DIR / f"{filename}.mp3"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        file_size = os.path.getsize(output_path) / 1024
        print(f"   ✅ Saved: {output_path} ({file_size:.1f} KB)")
        return str(output_path)
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


async def generate_all_voiceovers():
    """Generate all voiceover versions"""
    print("=" * 60)
    print("🎙️ AlphaAI Voiceover Generator")
    print("   Using OpenAI TTS HD via Emergent LLM Key")
    print("=" * 60)
    
    results = []
    
    # Main voiceover (full length)
    result = await generate_voiceover(
        VOICEOVER_SCRIPT, 
        "alphaai_voiceover_full",
        voice="onyx"  # Deep, authoritative
    )
    results.append({"name": "full", "path": result})
    
    # Short version for social
    result = await generate_voiceover(
        SHORT_SCRIPT,
        "alphaai_voiceover_short", 
        voice="onyx"
    )
    results.append({"name": "short", "path": result})
    
    # Alternative voice version
    result = await generate_voiceover(
        VOICEOVER_SCRIPT,
        "alphaai_voiceover_nova",
        voice="nova"  # Energetic, upbeat
    )
    results.append({"name": "nova", "path": result})
    
    print("\n" + "=" * 60)
    print("📊 Generation Summary")
    print("=" * 60)
    
    for r in results:
        status = "✅" if r["path"] else "❌"
        print(f"   {status} {r['name']}: {r['path'] or 'Failed'}")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    asyncio.run(generate_all_voiceovers())
