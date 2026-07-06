from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import uuid
import shutil
from typing import Optional

app = FastAPI(title="My Social Downloader")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Welcome to Social Downloader</h1><p>Go to /static/index.html if this page is blank.</p>"

@app.post("/download")
async def download_video(
    url: str = Form(...),
    cookie_file: Optional[UploadFile] = File(None)
):
    cookie_path = None
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
        
        if cookie_file:
            cookie_path = f"cookies_{uuid.uuid4()}.txt"
            with open(cookie_path, "wb") as f:
                shutil.copyfileobj(cookie_file.file, f)
            ydl_opts['cookiefile'] = cookie_path
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
        
        return FileResponse(
            path=downloaded_file,
            filename=os.path.basename(downloaded_file),
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)[:300]}")
    finally:
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)