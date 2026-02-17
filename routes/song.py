from flask import Blueprint
from services.ytmusic import get_song
from utils.response import success, error

song_bp = Blueprint('song', __name__)

@song_bp.route('/song/<video_id>')
def detail_song(video_id):
    try:
        data = get_song(video_id)
        return success(data)
    except Exception as e:
        return error(str(e), 500)