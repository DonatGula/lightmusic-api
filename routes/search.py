from flask import Blueprint, request, current_app
from utils.response import success, error
from services.ytmusic import search as yt_search

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def do_search():
    q     = request.args.get('q', '').strip()
    type_ = request.args.get('type', 'songs')
    limit = int(request.args.get('limit', 20))

    if not q:
        return error('Query kosong', 400)

    # Cache search result 30 menit
    cache     = current_app.config.get('CACHE')
    cache_key = f'search_{q}_{type_}_{limit}'
    cached    = cache.get(cache_key)

    if cached:
        print(f'✅ Search cache hit: {q}')
        return success(cached)

    try:
        results = yt_search(q, filter_type=type_, limit=limit)
        cache.set(cache_key, results, timeout=1800)  # 30 menit
        return success(results)
    except Exception as e:
        return error(str(e), 500)