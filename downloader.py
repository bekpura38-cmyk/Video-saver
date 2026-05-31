import asyncio
import os
import re
from dataclasses import dataclass

import yt_dlp

MAX_SIZE = 50 * 1024 * 1024  # 50 MB

QUALITY_FORMATS = {
    "360":  "best[height<=360][ext=mp4]/best[height<=360]/best",
    "480":  "best[height<=480][ext=mp4]/best[height<=480]/best",
    "720":  "best[height<=720][ext=mp4]/best[height<=720]/best",
    "1080": "best[height<=1080][ext=mp4]/best[height<=1080]/best",
    "best": "best[ext=mp4]/best",
    "audio": "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio",
}

QUALITY_LABELS = {
    "360": "360p", "480": "480p",
    "720": "720p HD", "1080": "1080p Full HD",
    "best": "Best", "audio": "MP3 Audio",
}

INSTAGRAM_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
}

TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
    ),
}


def is_valid_url(text: str) -> bool:
    return bool(re.match(r"https?://\S+", text.strip()))


def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    if "tiktok.com" in url_lower:
        return "tiktok"
    if "instagram.com" in url_lower:
        return "instagram"
    return "other"


@dataclass
class DownloadResult:
    success: bool
    path: str = None
    file_size: int = 0
    error: str = ""
    is_audio: bool = False
    platform: str = ""


def _find_file(base_path: str) -> str | None:
    if os.path.exists(base_path):
        return base_path
    base = base_path.rsplit(".", 1)[0]
    for ext in ["mp4", "webm", "mkv", "mov", "m4v", "m4a", "mp3", "ogg"]:
        candidate = f"{base}.{ext}"
        if os.path.exists(candidate):
            return candidate
    return None


def _do_download(url: str, quality: str) -> DownloadResult:
    platform = detect_platform(url)
    is_audio = quality == "audio"

    # Platform ga qarab format tanlash
    if platform == "instagram":
        fmt = "best[ext=mp4]/best"
    elif platform == "tiktok":
        fmt = "best[ext=mp4]/best"
    else:
        fmt = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["720"])

    ydl_opts = {
        "format": fmt,
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 3,
        "noplaylist": True,
    }

    # Platform uchun maxsus sozlamalar
    if platform == "instagram":
        ydl_opts["http_headers"] = INSTAGRAM_HEADERS
        ydl_opts["extractor_args"] = {"instagram": {"api": ["graphql"]}}

    elif platform == "tiktok":
        ydl_opts["http_headers"] = TIKTOK_HEADERS

    if is_audio:
        ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_path = ydl.prepare_filename(info)

        path = _find_file(raw_path)
        if not path:
            return DownloadResult(success=False, error="error", platform=platform)

        size = os.path.getsize(path)
        if size > MAX_SIZE:
            os.remove(path)
            return DownloadResult(success=False, error="size", platform=platform)

        return DownloadResult(
            success=True,
            path=path,
            file_size=size,
            is_audio=is_audio or path.endswith((".mp3", ".m4a", ".ogg")),
            platform=platform,
        )

    except yt_dlp.utils.ExtractorError as e:
        err = str(e).lower()
        if any(w in err for w in ["login", "private", "sign in", "age", "restricted"]):
            return DownloadResult(success=False, error="private", platform=platform)
        return DownloadResult(success=False, error="error", platform=platform)
    except Exception:
        return DownloadResult(success=False, error="error", platform=platform)


async def download_video(url: str, quality: str) -> DownloadResult:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _do_download, url, quality)
