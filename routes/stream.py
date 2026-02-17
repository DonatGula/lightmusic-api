from flask import Blueprint
from utils.response import success, error
import yt_dlp

stream_bp = Blueprint('stream', __name__)

def get_stream_url(video_id):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "stream_url": info['url'],
            "quality":    info.get('abr', 'unknown'),
            "ext":        info.get('ext', 'm4a'),
        }

@stream_bp.route('/stream/<video_id>')
def do_stream(video_id):
    try:
        data = get_stream_url(video_id)
        return success(data)
    except Exception as e:
        return error(str(e), 500)