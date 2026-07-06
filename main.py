from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import uuid
import time

app = FastAPI(title="My Social Downloader")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Social Downloader</h1>"

@app.get("/download")
async def download_video(url: str, audio: bool = False):
    for attempt in range(3):
        try:
            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            file_id = str(uuid.uuid4())
            ext = "mp3" if audio else "%(ext)s"
            output_template = os.path.join(download_dir, f"{file_id}.{ext}")
            
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'http_headers': {'Accept-Language': 'en-US,en;q=0.9'},
            }
            
            if audio:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
            
            return FileResponse(
                path=downloaded_file,
                filename=os.path.basename(downloaded_file),
                media_type="application/octet-stream"
            )
            
        except Exception as e:
            if attempt < 2:
                time.sleep(4)
                continue
            raise HTTPException(status_code=400, detail=f"Failed: {str(e)[:200]}")