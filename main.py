from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import uuid

app = FastAPI(title="My Social Downloader")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Show the nice page at the main address
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/download")
async def download_video(url: str):
    try:
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        file_id = str(uuid.uuid4())
        output_template = os.path.join(download_dir, f"{file_id}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
        
        return FileResponse(
            path=downloaded_file,
            filename=os.path.basename(downloaded_file),
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        error_str = str(e).lower()
        if "drm" in error_str or "spotify" in error_str or "apple" in error_str:
            raise HTTPException(
                status_code=400, 
                detail="❌ DRM Protected. Spotify, Apple Music etc. are not supported."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"❌ Failed to download. Reason: {str(e)[:250]}"
            )