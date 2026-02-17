from flask import Flask
from routes.search import search_bp
from routes.song import song_bp
from routes.stream import stream_bp
from routes.lyrics import lyrics_bp
from routes.charts import charts_bp

app = Flask(__name__)

app.register_blueprint(search_bp)
app.register_blueprint(song_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(lyrics_bp)
app.register_blueprint(charts_bp)

@app.route('/')
def index():
    return {
        "app": "LightMusic API",
        "version": "1.0",
        "endpoints": [
            "GET /search?q=query&type=songs",
            "GET /song/<video_id>",
            "GET /stream/<video_id>",
            "GET /lyrics/<video_id>",
            "GET /charts?country=ID",
        ]
    }

# ← TAMBAHKAN DI SINI
@app.route('/debug/<video_id>')
def debug(video_id):
    from ytmusicapi import YTMusic
    ytm = YTMusic()
    data = ytm.get_song(video_id)
    streaming = data.get('streamingData', {})
    formats = streaming.get('adaptiveFormats', [])
    if formats:
        return {"format_keys": list(formats[0].keys()), "sample": formats[0]}
    return {"error": "tidak ada format"}

if __name__ == '__main__':
    app.run(debug=True, port=5000)