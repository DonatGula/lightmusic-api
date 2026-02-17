from flask import Blueprint, Response, redirect
from utils.response import success, error
from pytubefix import YouTube
import requests

stream_bp = Blueprint('stream', __name__)

def get_audio_stream(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt  = YouTube(url)
    stream = (
        yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by('abr').last() or
        yt.streams.filter(only_audio=True).order_by('abr').last()
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
    """
    Redirect ke stream URL langsung.
    Flutter stream dari Google langsung — tidak lewat Railway.
    Tidak ada timeout masalah!
    """
    try:
        data = get_audio_stream(video_id)
        # Redirect ke URL Google langsung
        return redirect(data['stream_url'], code=302)
    except Exception as e:
        return error(str(e), 500)