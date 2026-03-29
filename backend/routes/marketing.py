"""
AlphaAI Marketing & Documentation Routes
PDF exports, marketing assets, video assets, and ad generation.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import subprocess
from pathlib import Path
from database import db, EMERGENT_LLM_KEY, logger
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api")

async def download_comprehensive_pdf():
    """Download the comprehensive project documentation PDF"""
    pdf_path = Path(__file__).parent / "reports" / "AlphaAI_Complete_Technical_Documentation.pdf"
    
    if not pdf_path.exists():
        # Generate if not exists
        import subprocess
        subprocess.run(["python", str(Path(__file__).parent / "generate_comprehensive_report.py")], check=True)
    
    if pdf_path.exists():
        return FileResponse(
            path=str(pdf_path),
            filename="AlphaAI_Complete_Technical_Documentation.pdf",
            media_type="application/pdf"
        )
    
    raise HTTPException(status_code=404, detail="PDF report not found. Please run the generator script.")

@router.post("/export/regenerate-pdf")
async def regenerate_comprehensive_pdf():
    """Regenerate the comprehensive project documentation PDF"""
    import subprocess
    try:
        result = subprocess.run(
            ["python", str(Path(__file__).parent / "generate_comprehensive_report.py")],
            capture_output=True,
            text=True,
            check=True
        )
        pdf_path = Path(__file__).parent / "reports" / "AlphaAI_Complete_Technical_Documentation.pdf"
        return {
            "success": True,
            "message": "PDF regenerated successfully",
            "path": str(pdf_path),
            "download_url": "/api/export/comprehensive-pdf"
        }
    except subprocess.CalledProcessError as e:
        return {"success": False, "message": f"Generation failed: {e.stderr}"}

# ============= MARKETING ASSETS ENDPOINTS =============

@router.get("/marketing/assets")
async def list_marketing_assets():
    """List all available marketing assets"""
    assets_dir = Path(__file__).parent / "marketing_assets"
    if not assets_dir.exists():
        return {"assets": [], "message": "No marketing assets generated yet"}
    
    assets = []
    for f in assets_dir.iterdir():
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            assets.append({
                "name": f.stem,
                "filename": f.name,
                "url": f"/api/marketing/image/{f.name}",
                "size_kb": round(f.stat().st_size / 1024, 1)
            })
    
    return {"assets": assets, "count": len(assets)}

@router.get("/marketing/image/{filename}")
async def get_marketing_image(filename: str):
    """Get a specific marketing image"""
    assets_dir = Path(__file__).parent / "marketing_assets"
    filepath = assets_dir / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    media_type = "image/jpeg" if filepath.suffix.lower() in ['.jpg', '.jpeg'] else "image/png"
    return FileResponse(path=str(filepath), media_type=media_type)

@router.post("/marketing/generate/{image_name}")
async def generate_marketing_image(image_name: str):
    """Generate a specific marketing image using Nano Banana"""
    import subprocess
    try:
        result = subprocess.run(
            ["python", str(Path(__file__).parent / "generate_marketing_images.py"), image_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Generated {image_name}",
                "url": f"/api/marketing/image/{image_name}.jpg"
            }
        else:
            return {"success": False, "message": result.stderr or "Generation failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============= VIDEO ASSETS ENDPOINTS =============

@router.get("/marketing/videos")
async def list_marketing_videos():
    """List all available marketing videos"""
    videos_dir = Path(__file__).parent / "marketing_assets" / "videos"
    if not videos_dir.exists():
        return {"videos": [], "message": "No marketing videos generated yet"}
    
    videos = []
    for f in videos_dir.iterdir():
        if f.suffix.lower() in ['.mp4', '.webm', '.mov']:
            videos.append({
                "name": f.stem,
                "filename": f.name,
                "url": f"/api/marketing/video/{f.name}",
                "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
            })
    
    return {"videos": videos, "count": len(videos)}

@router.get("/marketing/video/{filename}")
async def get_marketing_video(filename: str, request: Request):
    """Get a specific marketing video with proper range support for playback"""
    videos_dir = Path(__file__).parent / "marketing_assets" / "videos"
    filepath = videos_dir / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_size = filepath.stat().st_size
    
    # Handle range requests for video seeking
    range_header = request.headers.get("range")
    
    if range_header:
        # Parse range header
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            
            if start >= file_size:
                raise HTTPException(status_code=416, detail="Range not satisfiable")
            
            end = min(end, file_size - 1)
            content_length = end - start + 1
            
            def iter_file_range():
                with open(filepath, "rb") as f:
                    f.seek(start)
                    remaining = content_length
                    while remaining > 0:
                        chunk_size = min(8192, remaining)
                        data = f.read(chunk_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            from starlette.responses import StreamingResponse
            return StreamingResponse(
                iter_file_range(),
                status_code=206,
                media_type="video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                }
            )
    
    # No range - return full file
    return FileResponse(
        path=str(filepath),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
        }
    )

@router.post("/marketing/generate-video/{video_name}")
async def generate_marketing_video(video_name: str, background_tasks: BackgroundTasks):
    """Generate a specific marketing video using Sora 2 (runs in background)"""
    import subprocess
    
    # Available video types
    available = ["hero_promo", "social_short", "agents_showcase", "security_promo"]
    if video_name not in available:
        return {"success": False, "message": f"Unknown video. Available: {available}"}
    
    # Run in background since video generation takes 2-5 minutes
    def generate():
        subprocess.run(
            ["python", str(Path(__file__).parent / "generate_promo_videos.py"), video_name],
            capture_output=True,
            text=True,
            timeout=600
        )
    
    background_tasks.add_task(generate)
    
    return {
        "success": True,
        "message": f"Video generation started for '{video_name}'. Check /api/marketing/videos in 3-5 minutes.",
        "video_name": video_name
    }

# ============= VIRAL ADS ENDPOINTS =============

@router.get("/marketing/ads")
async def list_viral_ads():
    """List all viral ad variations"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads"
    ads = []
    if ads_dir.exists():
        for f in ads_dir.iterdir():
            if f.suffix.lower() == '.mp4':
                ads.append({
                    "name": f.stem.replace("_", " ").title(),
                    "filename": f.name,
                    "url": f"/api/marketing/ad/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    return {"ads": ads, "count": len(ads)}

@router.get("/marketing/ad/{filename}")
async def get_viral_ad(filename: str, request: Request):
    """Get a specific viral ad video"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads"
    filepath = ads_dir / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Ad not found")
    
    file_size = filepath.stat().st_size
    range_header = request.headers.get("range")
    
    if range_header:
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            content_length = end - start + 1
            
            def iter_file_range():
                with open(filepath, "rb") as f:
                    f.seek(start)
                    remaining = content_length
                    while remaining > 0:
                        chunk = min(8192, remaining)
                        data = f.read(chunk)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            from starlette.responses import StreamingResponse
            return StreamingResponse(
                iter_file_range(),
                status_code=206,
                media_type="video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                }
            )
    
    return FileResponse(path=str(filepath), media_type="video/mp4")

@router.get("/marketing/ads/preview")
async def ads_preview_page():
    """HTML page to preview viral ads"""
    from fastapi.responses import HTMLResponse
    
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads"
    ads = []
    if ads_dir.exists():
        # Sort by name to show main first
        for f in sorted(ads_dir.iterdir()):
            if f.suffix.lower() == '.mp4':
                ads.append({
                    "name": f.stem.replace("_", " ").title().replace("Alphaai Ad ", ""),
                    "filename": f.name,
                    "url": f"/api/marketing/ad/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    
    ad_cards = ""
    for ad in ads:
        highlight = "border: 2px solid #00FF94;" if "voice" in ad["filename"] else ""
        label = "⭐ WITH VOICEOVER" if "voice" in ad["filename"] else ""
        ad_cards += f'''
        <div class="ad-card" style="{highlight}">
            <h3>{ad["name"]} {label}</h3>
            <p class="size">{ad["size_mb"]} MB</p>
            <video controls preload="auto" playsinline>
                <source src="{ad["url"]}" type="video/mp4">
            </video>
            <a href="{ad["url"]}" download="{ad["filename"]}" class="btn">⬇️ Download</a>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>AlphaAI Viral Ads - TikTok/Reels Ready</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0a15, #1a1033);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #7B61FF; text-align: center; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #00FF94; margin-bottom: 30px; font-size: 14px; }}
        .ads-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .ad-card {{
            background: rgba(30, 30, 50, 0.8);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }}
        .ad-card h3 {{ color: #fff; margin: 0 0 5px 0; font-size: 14px; }}
        .ad-card .size {{ color: #888; margin: 0 0 10px 0; font-size: 12px; }}
        video {{
            width: 100%;
            max-height: 350px;
            border-radius: 8px;
            background: #000;
        }}
        .btn {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #7B61FF;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 13px;
        }}
        .specs {{ 
            background: rgba(0,255,148,0.1); 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px;
            text-align: center;
        }}
        .specs span {{ 
            display: inline-block; 
            margin: 0 15px; 
            color: #00FF94;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AlphaAI Viral Ads</h1>
        <p class="subtitle">TikTok • Instagram Reels • YouTube Shorts Ready</p>
        
        <div class="specs">
            <span>📐 9:16 Vertical</span>
            <span>⏱️ 16 seconds</span>
            <span>📱 720x1280</span>
            <span>🎯 4 Hook Variations</span>
        </div>
        
        <div class="ads-grid">
            {ad_cards if ads else '<p>No ads generated yet</p>'}
        </div>
    </div>
</body>
</html>'''
    return HTMLResponse(content=html)

@router.get("/marketing/preview")
async def video_preview_page():
    """HTML page to preview all marketing videos"""
    from fastapi.responses import HTMLResponse
    
    videos_dir = Path(__file__).parent / "marketing_assets" / "videos"
    videos = []
    if videos_dir.exists():
        # Sort to show main promo first
        files = sorted(videos_dir.iterdir(), key=lambda x: x.stat().st_size, reverse=True)
        for f in files:
            if f.suffix.lower() == '.mp4' and 'outro_clip' not in f.name:
                videos.append({
                    "name": f.stem.replace("_", " ").title(),
                    "filename": f.name,
                    "url": f"/api/marketing/video/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    
    video_cards = ""
    for v in videos:
        video_cards += f'''
        <div class="video-card">
            <h3>{v["name"]} ({v["size_mb"]} MB)</h3>
            <video controls preload="auto" playsinline>
                <source src="{v["url"]}" type="video/mp4">
            </video>
            <div class="buttons">
                <a href="{v["url"]}" download="{v["filename"]}" class="btn download">⬇️ Download MP4</a>
            </div>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>AlphaAI Marketing Videos</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a15;
            color: white;
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #7B61FF; text-align: center; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 30px; }}
        .video-card {{
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #333;
        }}
        .video-card h3 {{ color: #00FF94; margin: 0 0 15px 0; }}
        video {{
            width: 100%;
            max-height: 500px;
            border-radius: 8px;
            background: #000;
            display: block;
        }}
        .buttons {{ margin-top: 15px; }}
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            margin-right: 10px;
        }}
        .download {{ background: #7B61FF; color: white; }}
        .download:hover {{ background: #6B51EF; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 AlphaAI Marketing Videos</h1>
        <p class="subtitle">Click play button to watch • Click download to save</p>
        {video_cards if videos else '<p style="text-align:center">No videos available</p>'}
    </div>
</body>
</html>'''
    return HTMLResponse(content=html)

# ============= HIGH-CONVERTING ADS V2 =============

@router.get("/marketing/ads-v2")
async def list_hc_ads():
    """List high-converting ad variations v2"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads_v2"
    ads = []
    if ads_dir.exists():
        for f in sorted(ads_dir.iterdir()):
            if f.suffix.lower() == '.mp4':
                ads.append({
                    "name": f.stem,
                    "url": f"/api/marketing/ad-v2/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1),
                    "has_voice": "voice" in f.name
                })
    return {"ads": ads, "count": len(ads)}

@router.get("/marketing/ad-v2/{filename}")
async def get_hc_ad(filename: str, request: Request):
    """Get a high-converting ad video v2"""
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads_v2"
    filepath = ads_dir / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Ad not found")
    return FileResponse(path=str(filepath), media_type="video/mp4")

@router.get("/marketing/ads-v2/preview")
async def hc_ads_preview_page():
    """Preview page for high-converting ads v2"""
    from fastapi.responses import HTMLResponse
    
    ads_dir = Path(__file__).parent / "marketing_assets" / "ads_v2"
    ads = []
    if ads_dir.exists():
        for f in sorted(ads_dir.iterdir()):
            if f.suffix.lower() == '.mp4' and 'voice' in f.name:
                hook = f.stem.replace("alphaai_hc_ad_", "").replace("_voice", "").upper()
                ads.append({
                    "name": hook,
                    "filename": f.name,
                    "url": f"/api/marketing/ad-v2/{f.name}",
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 1)
                })
    
    hooks = {
        "MAIN": "This AI trades crypto for you 24/7",
        "V1": "I built an AI that trades crypto for me",
        "V2": "This bot never sleeps",
        "V3": "Stop trading manually"
    }
    
    ad_cards = ""
    for ad in ads:
        hook_text = hooks.get(ad["name"], ad["name"])
        star = "⭐ RECOMMENDED" if ad["name"] == "MAIN" else ""
        ad_cards += f'''
        <div class="ad-card">
            <div class="badge">{star}</div>
            <h3>Hook: {ad["name"]}</h3>
            <p class="hook-text">"{hook_text}"</p>
            <video controls preload="auto" playsinline>
                <source src="{ad["url"]}" type="video/mp4">
            </video>
            <a href="{ad["url"]}" download class="btn">⬇️ Download</a>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>AlphaAI High-Converting Ads v2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(180deg, #0a0a15 0%, #1a1033 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #7B61FF; text-align: center; font-size: 28px; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #00FF94; margin-bottom: 20px; font-size: 14px; }}
        .specs {{
            display: flex; justify-content: center; gap: 20px;
            background: rgba(123,97,255,0.1); padding: 12px; border-radius: 8px;
            margin-bottom: 25px; flex-wrap: wrap;
        }}
        .specs span {{ color: #00FF94; font-size: 13px; }}
        .ads-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}
        .ad-card {{
            background: rgba(30, 30, 50, 0.9);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #333;
            position: relative;
        }}
        .ad-card .badge {{
            position: absolute; top: 10px; right: 10px;
            background: #00FF94; color: black; padding: 3px 8px;
            border-radius: 4px; font-size: 10px; font-weight: bold;
        }}
        .ad-card h3 {{ color: #7B61FF; font-size: 14px; margin-bottom: 5px; }}
        .ad-card .hook-text {{ color: #aaa; font-size: 12px; margin-bottom: 12px; font-style: italic; }}
        video {{
            width: 100%; max-height: 400px;
            border-radius: 8px; background: #000;
        }}
        .btn {{
            display: block; text-align: center;
            margin-top: 10px; padding: 10px;
            background: #7B61FF; color: white;
            text-decoration: none; border-radius: 6px;
            font-weight: 500;
        }}
        .btn:hover {{ background: #6B51EF; }}
        .structure {{
            background: rgba(0,0,0,0.3); padding: 15px;
            border-radius: 8px; margin-bottom: 20px;
        }}
        .structure h3 {{ color: #00FF94; margin-bottom: 10px; font-size: 14px; }}
        .structure table {{ width: 100%; font-size: 12px; }}
        .structure td {{ padding: 4px 8px; border-bottom: 1px solid #333; }}
        .structure td:first-child {{ color: #7B61FF; width: 60px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 High-Converting Ads v2</h1>
        <p class="subtitle">Optimized for TikTok • Instagram Reels • YouTube Shorts • Paid Ads</p>
        
        <div class="specs">
            <span>📐 9:16 Vertical</span>
            <span>⏱️ 14 seconds</span>
            <span>📱 720x1280</span>
            <span>🎙️ With Voiceover</span>
            <span>🎯 4 Hook Variations</span>
        </div>
        
        <div class="structure">
            <h3>📋 Ad Structure</h3>
            <table>
                <tr><td>0-2s</td><td><b>HOOK</b> - Attention grabber</td></tr>
                <tr><td>2-3.5s</td><td><b>PROBLEM</b> - "Most people LOSE MONEY"</td></tr>
                <tr><td>3.5-7s</td><td><b>SOLUTION</b> - "AlphaAI finds trades automatically"</td></tr>
                <tr><td>7-11s</td><td><b>PROOF</b> - "+12% last month (paper trading)"</td></tr>
                <tr><td>11-14s</td><td><b>CTA</b> - "TRY IT FREE - Link in bio"</td></tr>
            </table>
        </div>
        
        <div class="ads-grid">
            {ad_cards}
        </div>
    </div>
</body>
</html>'''
    return HTMLResponse(content=html)

# ============= STRIPE SUBSCRIPTION ENDPOINTS =============
