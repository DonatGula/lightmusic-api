from flask import Blueprint, Response, request
from utils.response import success, error
from pytubefix import YouTube
import requests

stream_bp = Blueprint('stream', __name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 Chrome/96.0.4664.45 Mobile Safari/537.36',
    'Referer':    'https://www.youtube.com/',
    'Origin':     'https://www.youtube.com',
}

def get_best_stream(video_id: str):
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    
    # Prioritas: mp4 128kbps (itag 140) — paling kompatibel
    stream = (
        yt.streams.get_by_itag(140) or                                          # mp4 128kbps
        yt.streams.get_by_itag(139) or                                          # mp4 48kbps
        yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by('abr').last() or
        yt.streams.filter(only_audio=True).order_by('abr').last()
    )
    
    if not stream:
        raise Exception("Tidak ada stream tersedia")
    
    return stream, yt


@stream_bp.route('/stream/<video_id>')
def do_stream(video_id):
    try:
        stream, yt = get_best_stream(video_id)
        return success({
            "stream_url": stream.url,
            "title":      yt.title,
            "author":     yt.author,
            "duration":   yt.length,
            "thumbnail":  yt.thumbnail_url,
            "bitrate":    stream.abr,
            "mime_type":  stream.mime_type,
            "itag":       stream.itag,
        })
    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/play/<video_id>')
def play(video_id):
    """
    Railway fetch dari Google, lalu pipe ke client.
    Solve masalah IP mismatch.
    Pakai range request agar seek bisa jalan.
    """
    try:
        stream, yt = get_best_stream(video_id)
        stream_url = stream.url

        # Forward range header dari client (untuk seek)
        req_headers = dict(HEADERS)
        if 'Range' in request.headers:
            req_headers['Range'] = request.headers['Range']

        r = requests.get(
            stream_url,
            headers=req_headers,
            stream=True,
            timeout=30,
        )

        # Tentukan status code (206 untuk partial content)
        status_code = r.status_code

        # Response headers ke client
        resp_headers = {
            'Content-Type':                  r.headers.get('Content-Type', 'audio/mp4'),
            'Accept-Ranges':                 'bytes',
            'Access-Control-Allow-Origin':   '*',
            'Cache-Control':                 'no-cache',
        }
        if 'Content-Length' in r.headers:
            resp_headers['Content-Length'] = r.headers['Content-Length']
        if 'Content-Range' in r.headers:
            resp_headers['Content-Range'] = r.headers['Content-Range']

        def generate():
            for chunk in r.iter_content(chunk_size=16384):  # 16KB chunks
                if chunk:
                    yield chunk

        return Response(
            generate(),
            status=status_code,
            headers=resp_headers,
        )

    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/play/<video_id>', methods=['OPTIONS'])
def play_options(video_id):
    """Handle CORS preflight."""
    return Response(headers={
        'Access-Control-Allow-Origin':  '*',
        'Access-Control-Allow-Headers': 'Range, Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
    })