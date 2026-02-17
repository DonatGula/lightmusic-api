from flask import Blueprint, request
from services.ytmusic import search
from utils.response import success, error

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def do_search():
    q = request.args.get('q', '').strip()
    type_ = request.args.get('type', 'songs')  # songs/artists/albums
    limit = int(request.args.get('limit', 20))

    if not q:
        return error("Parameter 'q' wajib diisi")
    if type_ not in ['songs', 'artists', 'albums', 'playlists']:
        return error("type harus: songs, artists, albums, atau playlists")

    try:
        results = search(q, filter_type=type_, limit=limit)
        return success(results, f"Ditemukan {len(results)} hasil")
    except Exception as e:
        return error(str(e), 500)