from flask import Blueprint
from services.ytmusic import get_lyrics
from utils.response import success

lyrics_bp = Blueprint('lyrics', __name__)

@lyrics_bp.route('/lyrics/<video_id>')
def do_lyrics(video_id):
    data = get_lyrics(video_id)
    return success(data)