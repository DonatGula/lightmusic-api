from flask import Flask, send_file
from flask_cors import CORS
from routes.search import search_bp
from routes.song import song_bp
from routes.stream import stream_bp
from routes.lyrics import lyrics_bp
from routes.charts import charts_bp

app = Flask(__name__)
CORS(app)  # ← izinkan semua origin

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
        "Sumber": "https://ytmusicapi.readthedocs.io/en/stable/index.html",
        "dev":"natgul",
        "endpoints": [
            "GET /search?q=query&type=songs",
            "GET /song/<video_id>",
            "GET /stream/<video_id>",
            "GET /lyrics/<video_id>",
            "GET /charts?country=ID",
        ]
    }

@app.route('/api')
def explorer():
    return send_file('api-explorer.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)


@app.route('/debug/<video_id>')
def debug_stream(video_id):
    """Cek format apa yang tersedia untuk video ini."""
    try:
        from pytubefix import YouTube
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        
        streams = []
        for s in yt.streams.filter(only_audio=True):
            streams.append({
                "itag":      s.itag,
                "mime_type": s.mime_type,
                "abr":       s.abr,
                "codecs":    s.codecs,
                "url_preview": s.url[:80] + "..."
            })
        
        return {
            "title":   yt.title,
            "streams": streams
        }
    except Exception as e:
        return {"error": str(e)}
