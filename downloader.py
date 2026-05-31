"""
downloader.py — yt-dlp bilan video yuklab olish
"""
import asyncio
import os
import re
from dataclasses import dataclass

import yt_dlp

MAX_SIZE = 50 * 1024 * 1024  # 50 MB

QUALITY_FORMATS: dict[str, str] = {
    "144":  "bestvideo[height<=144]+bestaudio/best[height<=144]/worst",
    "360":  "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    "480":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "720":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "best": "bestvideo+bestaudio/best",
    "audio": "bestaudio/best",
}

QUALITY_LABELS: dict[str, str] = {
    "144": "144p", "360": "360p", "480": "480p",
    "720": "720p HD", "1080": "1080p Full HD",
    "best": "Best", "audio": "MP3 Audio",
}


@dataclass
class DownloadResult:
    success: bool
    path: str | None = None
    file_size: int = 0
    error: str = ""          # 'size' | 'error' | ''
    is_audio: bool = False


def is_valid_url(text: str) -> bool:
    return bool(re.match(r"https?://\S+", text.strip()))


def _do_download(url: str, quality: str) -> DownloadResult:
    fmt = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["720"])
    is_audio = quality == "audio"

    ydl_opts: dict = {
        "format": fmt,
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
    }

    if is_audio:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if is_audio:
                path = f"/tmp/{info['id']}.mp3"
            else:
                path = ydl.prepare_filename(info)
                if not path.endswith(".mp4"):
                    path = path.rsplit(".", 1)[0] + ".mp4"

        if not os.path.exists(path):
            return DownloadResult(success=False, error="error")

        size = os.path.getsize(path)
        if size > MAX_SIZE:
            os.remove(path)
            return DownloadResult(success=False, error="size")

        return DownloadResult(success=True, path=path,
                              file_size=size, is_audio=is_audio)
    except Exception:
        return DownloadResult(success=False, error="error")


async def download_video(url: str, quality: str) -> DownloadResult:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _do_download, url, quality)
