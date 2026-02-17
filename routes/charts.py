from flask import Blueprint, request
from services.ytmusic import get_charts
from utils.response import success, error

charts_bp = Blueprint('charts', __name__)

@charts_bp.route('/charts')
def do_charts():
    country = request.args.get('country', 'ID').upper()
    try:
        data = get_charts(country)
        return success(data)
    except Exception as e:
        return error(str(e), 500)