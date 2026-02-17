from flask import Blueprint, Response
from utils.response import success, error
from ytmusicapi import YTMusic
import yt_dlp
import requests
import tempfile
import os

stream_bp = Blueprint('stream', __name__)
ytm = YTMusic()

def get_ydl_opts():
    opts = {
        # Urutan prioritas format — coba satu per satu sampai berhasil
        'format': 'bestaudio/bestaudio*',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        # Jangan filter format yang tidak dikenal
        'allow_unplayable_formats': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'tv_embedded', 'web'],
            }
        },
    }

    cookies_content = os.environ.get('YT_COOKIES', '')
    if cookies_content:
        tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, encoding='utf-8'
        )
        tmp.write(cookies_content)
        tmp.close()
        opts['cookiefile'] = tmp.name
    elif os.path.exists('cookies.txt'):
        opts['cookiefile'] = 'cookies.txt'

    return opts


def get_stream_url(video_id):
    ydl_opts = get_ydl_opts()
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
    try:
        data = get_stream_url(video_id)
        stream_url = data['stream_url']

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