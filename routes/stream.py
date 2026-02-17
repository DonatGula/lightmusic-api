from flask import Blueprint, Response
from utils.response import success, error
from pytubefix import YouTube
import requests

stream_bp = Blueprint('stream', __name__)

YT_OPTS = {
    'use_oauth': False,
    'allow_oauth_cache': False,
}

def get_audio_stream(video_id: str):
    """Ambil stream audio pakai pytubefix — tidak butuh cookies."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url, **YT_OPTS)

    # Pilih audio stream terbaik
    stream = (
        yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by('abr').last() or
        yt.streams.filter(only_audio=True).order_by('abr').last() or
        yt.streams.get_audio_only()
    )

    if not stream:
        raise Exception("Tidak ada stream audio tersedia")

    return {
        "stream_url": stream.url,
        "title":      yt.title,
        "author":     yt.author,
        "duration":   yt.length,
        "thumbnail":  yt.thumbnail_url,
        "bitrate":    stream.abr,
        "mime_type":  stream.mime_type,
    }


@stream_bp.route('/stream/<video_id>')
def do_stream(video_id):
    try:
        data = get_audio_stream(video_id)
        return success(data)
    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/play/<video_id>')
def play(video_id):
    """Proxy audio stream — Flutter tinggal pakai URL ini."""
    try:
        data = get_audio_stream(video_id)
        stream_url = data['stream_url']

        req = requests.get(stream_url, stream=True, headers={
            'User-Agent':  'Mozilla/5.0',
            'Referer':     'https://www.youtube.com/',
        }, timeout=10)

        def generate():
            for chunk in req.iter_content(chunk_size=8192):
                yield chunk

        return Response(
            generate(),
            content_type=req.headers.get('Content-Type', 'audio/mp4'),
            headers={
                'Accept-Ranges':  'bytes',
                'Content-Length': req.headers.get('Content-Length', ''),
                'Cache-Control':  'no-cache',
            }
        )
    except Exception as e:
        return error(str(e), 500)