#!/usr/bin/env python3
"""
AlphaAI Branded Marketing Image Generator
Creates branded images with AlphaAI highlighted, then combines them
"""

import asyncio
import os
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

# Output directory
OUTPUT_DIR = Path(__file__).parent / "marketing_assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Branded prompts with AlphaAI highlighted
BRANDED_PROMPTS = {
    "hero_banner_branded": """
        Create a premium hero banner for "AlphaAI" - an AI-powered crypto hedge fund.
        Center composition: A majestic glowing AI brain made of neural network circuits.
        The brain should have "ALPHA" integrated into the left hemisphere design and "AI" into the right.
        Connected to floating Bitcoin (₿) and Ethereum (◊) symbols via energy streams.
        Background: Dark navy gradient with matrix-style falling code.
        Color scheme: Electric purple (#7B61FF) for AI elements, neon green (#00FF94) for crypto.
        Futuristic cityscape silhouette at the bottom.
        Professional, cutting-edge fintech aesthetic. Wide 16:9 landscape format.
        Make it look like a premium hedge fund advertisement.
    """,
    
    "trading_agents_branded": """
        Create an illustration showcasing "AlphaAI" trading agents - 4 sophisticated AI robots.
        Each robot should have a glowing chest emblem suggesting "αAI" (Alpha AI logo).
        Agent 1 (purple glow): Analyzing candlestick charts - "Arbitrage Agent"
        Agent 2 (cyan glow): Tracking momentum indicators - "Momentum Agent"  
        Agent 3 (green glow): Monitoring funding rates - "Funding Agent"
        Agent 4 (gold glow): Running neural networks - "Research Lab"
        They stand in a futuristic trading command center with holographic displays.
        Dark background, premium tech aesthetic.
        The agents should look powerful and intelligent, representing AlphaAI's autonomous trading.
    """,
    
    "smart_contract_branded": """
        Create a visualization of "AlphaAI" smart contract vault.
        Central element: A glowing hexagonal vault/safe made of blockchain nodes.
        The vault should have "αAI" symbol prominently displayed on its front face.
        Digital ETH coins and tokens flowing in through secure quantum tunnels.
        Shield/security elements surrounding the vault representing protection.
        Connected to multiple strategy nodes (smaller hexagons) representing fund allocation.
        Color scheme: Purple (#7B61FF) vault, green (#00FF94) for secure connections, gold accents.
        Dark space-like background with subtle grid lines.
        Represents security, transparency, and decentralized fund management.
    """
}


async def generate_branded_image(name: str, prompt: str) -> dict:
    """Generate a single branded marketing image"""
    print(f"\n🎨 Generating branded: {name}...")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        return {"name": name, "success": False, "error": "EMERGENT_LLM_KEY not found"}
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"alphaai-branded-{name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            system_message="You are a world-class graphic designer creating premium marketing materials for AlphaAI, a cutting-edge crypto hedge fund platform."
        )
        
        chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
        
        msg = UserMessage(text=prompt.strip())
        text, images = await chat.send_message_multimodal_response(msg)
        
        if images and len(images) > 0:
            img = images[0]
            image_bytes = base64.b64decode(img['data'])
            
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
            return {"name": name, "success": False, "error": "No image in response"}
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {"name": name, "success": False, "error": str(e)}


def combine_images_vertical(image_paths: list, output_path: str, add_branding: bool = True):
    """Combine multiple images vertically into one composite"""
    print(f"\n🔗 Combining {len(image_paths)} images...")
    
    # Load all images
    images = []
    for path in image_paths:
        if Path(path).exists():
            img = Image.open(path)
            images.append(img)
            print(f"   Loaded: {path} ({img.size[0]}x{img.size[1]})")
    
    if not images:
        print("   ❌ No images to combine")
        return None
    
    # Calculate dimensions
    max_width = max(img.size[0] for img in images)
    total_height = sum(img.size[1] for img in images)
    
    # Add space for header and footer branding
    header_height = 80 if add_branding else 0
    footer_height = 60 if add_branding else 0
    spacing = 10  # Space between images
    
    final_height = total_height + header_height + footer_height + (spacing * (len(images) - 1))
    
    # Create composite image with dark background
    composite = Image.new('RGB', (max_width, final_height), color=(10, 10, 25))
    draw = ImageDraw.Draw(composite)
    
    # Add header branding
    if add_branding:
        # Header background gradient effect (simplified as solid)
        draw.rectangle([(0, 0), (max_width, header_height)], fill=(20, 15, 40))
        
        # Add AlphaAI text
        try:
            # Try to use a nice font, fallback to default
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw "AlphaAI" title
        title = "AlphaAI"
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (max_width - title_width) // 2
        
        # Purple glow effect (draw text multiple times with slight offset)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            draw.text((title_x + offset[0], 20 + offset[1]), title, fill=(123, 97, 255, 100), font=font_large)
        draw.text((title_x, 20), title, fill=(123, 97, 255), font=font_large)
        
        # Subtitle
        subtitle = "AI-Powered Decentralized Hedge Fund"
        sub_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        sub_width = sub_bbox[2] - sub_bbox[0]
        draw.text(((max_width - sub_width) // 2, 58), subtitle, fill=(0, 255, 148), font=font_small)
    
    # Paste images
    y_offset = header_height
    for i, img in enumerate(images):
        # Center image horizontally
        x_offset = (max_width - img.size[0]) // 2
        composite.paste(img, (x_offset, y_offset))
        y_offset += img.size[1] + spacing
    
    # Add footer branding
    if add_branding:
        footer_y = final_height - footer_height
        draw.rectangle([(0, footer_y), (max_width, final_height)], fill=(20, 15, 40))
        
        try:
            font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_footer = ImageFont.load_default()
        
        footer_text = "© 2026 AlphaAI Platform | Autonomous AI Trading | Smart Contract Security"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((max_width - footer_width) // 2, footer_y + 20), footer_text, fill=(150, 150, 150), font=font_footer)
    
    # Save composite
    composite.save(output_path, quality=95)
    print(f"   ✅ Composite saved: {output_path}")
    print(f"   📐 Final size: {composite.size[0]}x{composite.size[1]}")
    
    return output_path


async def generate_all_branded_and_combine():
    """Generate all branded images and combine them"""
    print("=" * 70)
    print("🚀 AlphaAI BRANDED Marketing Image Generator")
    print("   Using Gemini Nano Banana via Emergent LLM Key")
    print("=" * 70)
    
    results = []
    image_paths = []
    
    # Generate each branded image
    for name, prompt in BRANDED_PROMPTS.items():
        result = await generate_branded_image(name, prompt)
        results.append(result)
        if result.get("success"):
            image_paths.append(result["path"])
        await asyncio.sleep(2)  # Small delay between requests
    
    # Combine all successful images
    if len(image_paths) >= 2:
        print("\n" + "=" * 70)
        print("📦 Creating Combined Composite Image")
        print("=" * 70)
        
        composite_path = str(OUTPUT_DIR / "alphaai_combined_marketing.jpg")
        combine_images_vertical(image_paths, composite_path, add_branding=True)
        
        results.append({
            "name": "alphaai_combined_marketing",
            "success": True,
            "path": composite_path,
            "type": "composite"
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Generation Summary")
    print("=" * 70)
    
    successful = [r for r in results if r.get("success")]
    print(f"\n✅ Generated: {len(successful)} images")
    for r in successful:
        print(f"   - {r['name']}: {r['path']}")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"\n🎯 Combined image: {OUTPUT_DIR}/alphaai_combined_marketing.jpg")
    
    return results


if __name__ == "__main__":
    asyncio.run(generate_all_branded_and_combine())
