from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import uuid
import shutil

app = FastAPI(title="My Social Downloader")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Improved homepage with cookie upload
@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    # We'll update index.html later to include cookie upload
    return html

@app.post("/download")
async def download_video(
    url: str = Form(...),
    cookie_file: UploadFile = File(None)
):
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
        
        # If user uploads cookies
        cookie_path = None
        if cookie_file:
            cookie_path = f"cookies_{uuid.uuid4()}.txt"
            with open(cookie_path, "wb") as f:
                shutil.copyfileobj(cookie_file.file, f)
            ydl_opts['cookiefile'] = cookie_path
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
        
        # Clean up cookie file
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)
        
        return FileResponse(
            path=downloaded_file,
            filename=os.path.basename(downloaded_file),
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        if "cookie" in str(e).lower() or "login" in str(e).lower():
            detail = "Cookie authentication failed. Make sure your cookies are fresh."
        else:
            detail = f"Download failed: {str(e)[:200]}"
        raise HTTPException(status_code=400, detail=detail)