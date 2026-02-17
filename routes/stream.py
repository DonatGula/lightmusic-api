from flask import Blueprint, Response
from utils.response import success, error
from ytmusicapi import YTMusic
from urllib.parse import parse_qs, unquote
import yt_dlp
import requests

stream_bp = Blueprint('stream', __name__)
ytm = YTMusic()

def get_stream_url(video_id):
    """Gunakan yt-dlp hanya untuk extract URL yang sudah di-decode."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt',
        'extract_flat': False,
        'skip_download': True,
        # Paksa pakai web client biasa, bukan YouTube Music
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],
            }
        },
    }
    url = f"https://music.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "stream_url": info['url'],
            "mimeType":   info.get('acodec', 'unknown'),
            "bitrate":    info.get('abr', 0),
            "ext":        info.get('ext', 'webm'),
            "duration":   info.get('duration', 0),
            "title":      info.get('title', ''),
        }

@stream_bp.route('/stream/<video_id>')
def do_stream(video_id):
    try:
        data = get_stream_url(video_id)
        return success(data)
    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/play/<video_id>')
def play(video_id):
    """
    Proxy audio stream langsung ke Flutter/browser.
    Flutter tinggal pakai URL: /play/<video_id>
    """
    try:
        data = get_stream_url(video_id)
        stream_url = data['stream_url']

        # Proxy stream dari Google ke client
        req = requests.get(stream_url, stream=True, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.youtube.com/',
        })

        def generate():
            for chunk in req.iter_content(chunk_size=4096):
                yield chunk

        return Response(
            generate(),
            content_type=req.headers.get('Content-Type', 'audio/webm'),
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': req.headers.get('Content-Length', ''),
            }
        )
    except Exception as e:
        return error(str(e), 500)