from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import uuid

app = FastAPI(title="My Social Downloader")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Social Downloader</h1><p>Site is running. Visit /static/index.html</p>"

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
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)[:250]}")