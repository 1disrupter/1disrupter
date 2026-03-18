#!/usr/bin/env python3
"""
AlphaAI Voiceover Generator - Timed for 28 second video
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from emergentintegrations.llm.openai import OpenAITextToSpeech

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "marketing_assets" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Voiceover timed for 28-second video (approximately 80-90 words for natural pacing)
TIMED_VOICEOVER = """
Introducing AlphaAI. The future of autonomous crypto trading.

Four AI agents work around the clock. Analyzing markets. Executing trades. Managing risk.

The Arbitrage Agent. The Momentum Agent. The Funding Agent. And our AI Research Lab.

Your capital secured by blockchain smart contracts. Full transparency. Complete control.

AlphaAI. Intelligent investing. The future of trading is here.
"""


async def generate_timed_voiceover():
    """Generate voiceover timed for video"""
    print("🎙️ Generating timed voiceover for 28-second video...")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        print("❌ EMERGENT_LLM_KEY not found")
        return None
    
    try:
        tts = OpenAITextToSpeech(api_key=api_key)
        
        # Generate with slightly faster speed to fit 28 seconds
        audio_bytes = await tts.generate_speech(
            text=TIMED_VOICEOVER.strip(),
            model="tts-1-hd",
            voice="onyx",  # Deep, authoritative
            speed=1.05,    # Slightly faster
            response_format="mp3"
        )
        
        output_path = OUTPUT_DIR / "alphaai_voiceover_28sec.mp3"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Saved: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(generate_timed_voiceover())
