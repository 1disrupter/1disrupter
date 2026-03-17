#!/usr/bin/env python3
"""
AlphaAI Marketing Image Generator using Gemini Nano Banana
Generates professional marketing visuals for the platform
"""

import asyncio
import os
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

# Output directory
OUTPUT_DIR = Path(__file__).parent / "marketing_assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Marketing image prompts for AlphaAI
MARKETING_PROMPTS = {
    "hero_banner": """
        Create a sleek, futuristic hero banner for a crypto AI hedge fund platform called "AlphaAI".
        Show a sophisticated AI brain made of glowing neural networks, connected to floating cryptocurrency symbols (Bitcoin, Ethereum).
        Use a dark navy/black background with electric purple (#7B61FF) and neon green (#00FF94) accents.
        Professional, high-tech, Wall Street meets Silicon Valley aesthetic.
        Wide landscape format suitable for website header.
        No text in the image.
    """,
    
    "ai_trading_agents": """
        Create an illustration of 4 AI trading agents working together in a futuristic trading floor.
        Each agent should be represented as a sleek robot or holographic AI assistant, each with a distinct color glow.
        Floating holographic screens showing charts, candlesticks, and trading data surround them.
        Dark background with purple (#7B61FF) and cyan accents.
        Modern, clean, and professional tech aesthetic.
        No text in the image.
    """,
    
    "smart_contract": """
        Create a visualization of a blockchain smart contract for a DeFi hedge fund.
        Show a glowing, translucent cube or vault made of interconnected blockchain nodes.
        Digital coins (ETH) flowing in and out through secure pathways.
        Purple (#7B61FF) and gold accents on a dark gradient background.
        Represents security, transparency, and automation.
        No text in the image.
    """,
    
    "performance_dashboard": """
        Create a futuristic 3D holographic dashboard showing trading performance metrics.
        Include floating charts, upward trending lines, pie charts, and percentage numbers.
        Green (#00FF94) indicates profits, purple (#7B61FF) for primary elements.
        Dark background with depth and glass-morphism effects.
        Professional financial technology aesthetic.
        No text in the image.
    """,
    
    "investor_portal": """
        Create an illustration of a premium investor portal experience.
        Show a person (silhouette or minimal) interacting with a large floating holographic interface.
        The interface displays portfolio allocation, AI agent performance, and market data.
        Sleek, luxury fintech aesthetic with dark theme and purple/green accents.
        No text in the image.
    """
}


async def generate_single_image(name: str, prompt: str) -> dict:
    """Generate a single marketing image"""
    print(f"\n🎨 Generating: {name}...")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        return {"name": name, "success": False, "error": "EMERGENT_LLM_KEY not found"}
    
    try:
        # Create new chat instance for each image
        chat = LlmChat(
            api_key=api_key,
            session_id=f"alphaai-marketing-{name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            system_message="You are a professional graphic designer creating marketing materials for a fintech company."
        )
        
        # Configure for Nano Banana image generation
        chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
        
        # Create message
        msg = UserMessage(text=prompt.strip())
        
        # Generate image
        text, images = await chat.send_message_multimodal_response(msg)
        
        if images and len(images) > 0:
            # Save the image
            img = images[0]
            image_bytes = base64.b64decode(img['data'])
            
            # Determine file extension
            ext = "png" if "png" in img.get('mime_type', 'png') else "jpg"
            filename = f"{name}.{ext}"
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            print(f"   ✅ Saved: {filepath}")
            return {
                "name": name,
                "success": True,
                "path": str(filepath),
                "size_kb": len(image_bytes) / 1024
            }
        else:
            print(f"   ❌ No image generated")
            return {"name": name, "success": False, "error": "No image in response", "text": text}
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {"name": name, "success": False, "error": str(e)}


async def generate_all_marketing_images():
    """Generate all marketing images"""
    print("=" * 60)
    print("🚀 AlphaAI Marketing Image Generator")
    print("   Using Gemini Nano Banana via Emergent LLM Key")
    print("=" * 60)
    
    results = []
    
    for name, prompt in MARKETING_PROMPTS.items():
        result = await generate_single_image(name, prompt)
        results.append(result)
        # Small delay between requests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Generation Summary")
    print("=" * 60)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for r in successful:
        print(f"   - {r['name']}: {r['path']} ({r['size_kb']:.1f} KB)")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for r in failed:
            print(f"   - {r['name']}: {r.get('error', 'Unknown error')}")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    return results


async def generate_single(image_name: str):
    """Generate a single image by name"""
    if image_name not in MARKETING_PROMPTS:
        print(f"❌ Unknown image: {image_name}")
        print(f"   Available: {', '.join(MARKETING_PROMPTS.keys())}")
        return
    
    result = await generate_single_image(image_name, MARKETING_PROMPTS[image_name])
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Generate specific image
        image_name = sys.argv[1]
        asyncio.run(generate_single(image_name))
    else:
        # Generate all images
        asyncio.run(generate_all_marketing_images())
