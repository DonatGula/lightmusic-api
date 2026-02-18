from flask import Blueprint, Response, request, current_app
from utils.response import success, error
from pytubefix import YouTube
import requests
import re

stream_bp = Blueprint('stream', __name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 Chrome/96.0.4664.45 Mobile Safari/537.36',
    'Referer':    'https://www.youtube.com/',
    'Origin':     'https://www.youtube.com',
}

def get_cache():
    return current_app.config.get('CACHE')

def get_best_stream(video_id: str):
    """Ambil stream dengan cache 5 jam."""
    cache     = get_cache()
    cache_key = f'stream_{video_id}'

    # Cek cache dulu
    cached = cache.get(cache_key)
    if cached:
        print(f'✅ Cache hit: {video_id}')
        return cached

    print(f'📡 Fetching stream: {video_id}')
    yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')

    stream = (
        yt.streams.get_by_itag(140) or   # mp4 128kbps — terbaik
        yt.streams.get_by_itag(139) or   # mp4 48kbps
        yt.streams.filter(only_audio=True, mime_type='audio/mp4').order_by('abr').last() or
        yt.streams.filter(only_audio=True).order_by('abr').last()
    )

    if not stream:
        raise Exception('Tidak ada stream tersedia')

    result = {
        'url':       stream.url,
        'title':     yt.title,
        'author':    yt.author,
        'duration':  yt.length,
        'thumbnail': yt.thumbnail_url,
        'bitrate':   stream.abr,
        'mime_type': stream.mime_type,
        'itag':      stream.itag,
        'filesize':  stream.filesize,
    }

    # Simpan ke cache 5 jam
    cache.set(cache_key, result, timeout=18000)
    print(f'💾 Cached: {video_id}')
    return result


@stream_bp.route('/stream/<video_id>')
def do_stream(video_id):
    try:
        data = get_best_stream(video_id)
        return success({
            'stream_url': data['url'],
            'title':      data['title'],
            'author':     data['author'],
            'duration':   data['duration'],
            'thumbnail':  data['thumbnail'],
            'bitrate':    data['bitrate'],
            'mime_type':  data['mime_type'],
        })
    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/download/<video_id>')
def download_info(video_id):
    try:
        data      = get_best_stream(video_id)
        safe      = re.sub(r'[^\w\s-]', '', data['title']).strip()
        safe      = re.sub(r'\s+', '_', safe)
        return success({
            'stream_url': data['url'],
            'title':      data['title'],
            'author':     data['author'],
            'duration':   data['duration'],
            'thumbnail':  data['thumbnail'],
            'filename':   f'{safe}.mp3',
            'filesize':   data['filesize'] or 0,
            'bitrate':    data['bitrate'],
        })
    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/play/<video_id>')
def play(video_id):
    try:
        data = get_best_stream(video_id)

        req_headers = dict(HEADERS)
        if 'Range' in request.headers:
            req_headers['Range'] = request.headers['Range']

        r = requests.get(
            data['url'],
            headers=req_headers,
            stream=True,
            timeout=30,
        )

        # URL expired (403) → hapus cache, ambil fresh
        if r.status_code == 403:
            cache     = get_cache()
            cache_key = f'stream_{video_id}'
            cache.delete(cache_key)
            print(f'🔄 Cache expired, refresh: {video_id}')

            data = get_best_stream(video_id)  # fresh URL
            r    = requests.get(
                data['url'],
                headers=req_headers,
                stream=True,
                timeout=30,
            )

        resp_headers = {
            'Content-Type':                r.headers.get('Content-Type', 'audio/mp4'),
            'Accept-Ranges':               'bytes',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control':               'no-cache',
        }
        if 'Content-Length' in r.headers:
            resp_headers['Content-Length'] = r.headers['Content-Length']
        if 'Content-Range' in r.headers:
            resp_headers['Content-Range']  = r.headers['Content-Range']

        def generate():
            for chunk in r.iter_content(chunk_size=16384):
                if chunk:
                    yield chunk

        return Response(generate(), status=r.status_code, headers=resp_headers)

    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/download-file/<video_id>')
def download_file(video_id):
    try:
        data = get_best_stream(video_id)

        safe     = re.sub(r'[^\w\s-]', '', data['title']).strip()
        safe     = re.sub(r'\s+', '_', safe)
        filename = f'{safe}.mp3'

        # Cek URL masih valid
        test = requests.head(data['url'], headers=HEADERS, timeout=10)
        if test.status_code == 403:
            # Hapus cache, ambil fresh
            cache = get_cache()
            cache.delete(f'stream_{video_id}')
            data  = get_best_stream(video_id)

        def generate():
            r = requests.get(
                data['url'],
                headers=HEADERS,
                stream=True,
                timeout=60,
            )
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            status=200,
            headers={
                'Content-Type':                'audio/mp4',
                'Content-Disposition':         f'attachment; filename="{filename}"',
                'Content-Length':              str(data['filesize'] or ''),
                'Access-Control-Allow-Origin': '*',
            }
        )
    except Exception as e:
        return error(str(e), 500)


@stream_bp.route('/cache/clear/<video_id>')
def clear_cache(video_id):
    """Manual clear cache untuk video tertentu."""
    cache = get_cache()
    cache.delete(f'stream_{video_id}')
    return success({'cleared': video_id})


@stream_bp.route('/cache/clear-all')
def clear_all_cache():
    """Clear semua cache."""
    cache = get_cache()
    cache.clear()
    return success({'cleared': 'all'})