#!/usr/bin/env python3
"""
AlphaAI Ad Voiceover - Timed for 16 second viral ad
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from emergentintegrations.llm.openai import OpenAITextToSpeech

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Short punchy voiceover timed for 16 seconds (~40-50 words)
AD_VOICEOVER = """
This AI trades crypto for you, twenty-four seven.

Most traders lose money. AlphaAI changes that.

Four AI agents scan markets and find trades automatically.

Plus twelve percent last month on paper trading. Live signals. Real data.

Try it free. Link in bio.
"""


async def generate_ad_voiceover():
    """Generate voiceover for viral ad"""
    print("🎙️ Generating ad voiceover (16 seconds)...")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        print("❌ EMERGENT_LLM_KEY not found")
        return None
    
    try:
        tts = OpenAITextToSpeech(api_key=api_key)
        
        audio_bytes = await tts.generate_speech(
            text=AD_VOICEOVER.strip(),
            model="tts-1-hd",
            voice="onyx",  # Deep, confident
            speed=1.15,    # Faster for punchy ad feel
            response_format="mp3"
        )
        
        output_path = OUTPUT_DIR / "alphaai_ad_voiceover.mp3"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Saved: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(generate_ad_voiceover())
