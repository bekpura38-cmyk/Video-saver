import asyncio
import os
import re
import urllib.request
import urllib.parse
import json
from dataclasses import dataclass
import yt_dlp

MAX_SIZE = 50 * 1024 * 1024  # 50 MB


def is_valid_url(text: str) -> bool:
    return bool(re.match(r"https?://\S+", text.strip()))


def detect_platform(url: str) -> str:
    u = url.lower()
    if "tiktok.com" in u:
        return "tiktok"
    if "instagram.com" in u:
        return "instagram"
    return "unsupported"


@dataclass
class DownloadResult:
    success: bool
    path: str = None
    file_size: int = 0
    error: str = ""
    is_audio: bool = False
    platform: str = ""


def _save_file(url: str, path: str, headers: dict = None) -> bool:
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception:
        return False


def _find_file(base_path: str) -> str | None:
    if os.path.exists(base_path):
        return base_path
    base = base_path.rsplit(".", 1)[0]
    for ext in ["mp4", "webm", "mkv", "mov", "m4v"]:
        c = f"{base}.{ext}"
        if os.path.exists(c):
            return c
    return None


def _download_tiktok(url: str) -> DownloadResult:
    # 1-usul: tikwm.com API
    try:
        api_url = "https://www.tikwm.com/api/"
        data = urllib.parse.urlencode({"url": url, "hd": 1}).encode()
        req = urllib.request.Request(
            api_url, data=data,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())

        if result.get("code") == 0:
            video_data = result.get("data", {})
            video_url = video_data.get("hdplay") or video_data.get("play")
            if video_url:
                vid_id = video_data.get("id", "tiktok")
                path = f"/tmp/{vid_id}.mp4"
                ok = _save_file(video_url, path, {"User-Agent": "Mozilla/5.0"})
                if ok:
                    size = os.path.getsize(path)
                    if size <= MAX_SIZE:
                        return DownloadResult(success=True, path=path, file_size=size, platform="tiktok")
                    os.remove(path)
                    return DownloadResult(success=False, error="size", platform="tiktok")
    except Exception:
        pass

    # 2-usul: yt-dlp
    opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.tiktok.com/",
        },
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw = ydl.prepare_filename(info)
            path = _find_file(raw)
            if path:
                size = os.path.getsize(path)
                if size <= MAX_SIZE:
                    return DownloadResult(success=True, path=path, file_size=size, platform="tiktok")
                os.remove(path)
                return DownloadResult(success=False, error="size", platform="tiktok")
    except Exception:
        pass

    return DownloadResult(success=False, error="error", platform="tiktok")


def _download_instagram(url: str) -> DownloadResult:
    for fmt in ["best[height<=480][ext=mp4]", "best[ext=mp4]", "best"]:
        opts = {
            "format": fmt,
            "outtmpl": "/tmp/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
                ),
            },
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                raw = ydl.prepare_filename(info)
                path = _find_file(raw)
                if path:
                    size = os.path.getsize(path)
                    if size <= MAX_SIZE:
                        return DownloadResult(success=True, path=path, file_size=size, platform="instagram")
                    os.remove(path)
                    return DownloadResult(success=False, error="size", platform="instagram")
        except Exception as e:
            err = str(e).lower()
            if any(w in err for w in ["login", "private", "sign in"]):
                return DownloadResult(success=False, error="private", platform="instagram")
            continue

    return DownloadResult(success=False, error="error", platform="instagram")


def _do_download(url: str) -> DownloadResult:
    platform = detect_platform(url)
    if platform == "tiktok":
        return _download_tiktok(url)
    elif platform == "instagram":
        return _download_instagram(url)
    return DownloadResult(success=False, error="unsupported", platform="other")


async def download_video(url: str) -> DownloadResult:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _do_download, url)
