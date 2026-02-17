from ytmusicapi import YTMusic

# Mode publik — tanpa login dulu
ytm = YTMusic()

def search(query, filter_type="songs", limit=20):
    try:
        results = ytm.search(query, filter=filter_type, limit=limit)
        simplified = []
        for item in results:
            # Ambil field yang kita butuhkan saja
            song = {
                "id":        item.get("videoId", ""),
                "title":     item.get("title", ""),
                "artist":    item["artists"][0]["name"] if item.get("artists") else "",
                "album":     item["album"]["name"] if item.get("album") else "",
                "duration":  item.get("duration", ""),
                "thumbnail": item["thumbnails"][-1]["url"] if item.get("thumbnails") else "",
            }
            if song["id"]:  # hanya yang punya videoId
                simplified.append(song)
        return simplified
    except Exception as e:
        raise Exception(f"Search gagal: {str(e)}")


def get_song(video_id):
    try:
        data = ytm.get_song(video_id)
        details = data.get("videoDetails", {})
        return {
            "id":          details.get("videoId", ""),
            "title":       details.get("title", ""),
            "artist":      details.get("author", ""),
            "duration":    int(details.get("lengthSeconds", 0)),
            "thumbnail":   details["thumbnail"]["thumbnails"][-1]["url"]
                           if details.get("thumbnail") else "",
            "description": details.get("shortDescription", "")[:200],
        }
    except Exception as e:
        raise Exception(f"Get song gagal: {str(e)}")


def get_lyrics(video_id):
    try:
        # Cari browseId untuk lirik
        result = ytm.get_watch_playlist(video_id)
        lyrics_id = result.get("lyrics", "")
        if not lyrics_id:
            return {"lyrics": "Lirik tidak tersedia", "source": "-"}
        lyrics = ytm.get_lyrics(lyrics_id)
        return {
            "lyrics": lyrics.get("lyrics", "Tidak tersedia"),
            "source": lyrics.get("source", "YouTube Music")
        }
    except Exception as e:
        return {"lyrics": "Lirik tidak tersedia", "source": "-"}


def get_charts(country="ID"):
    try:
        charts = ytm.get_charts(country=country)
        top_songs = []
        if charts.get("songs") and charts["songs"].get("items"):
            for item in charts["songs"]["items"][:20]:
                top_songs.append({
                    "id":        item.get("videoId", ""),
                    "title":     item.get("title", ""),
                    "artist":    item["artists"][0]["name"] if item.get("artists") else "",
                    "thumbnail": item["thumbnails"][-1]["url"] if item.get("thumbnails") else "",
                    "rank":      item.get("rank", 0),
                })
        return {
            "country": country,
            "top_songs": top_songs
        }
    except Exception as e:
        raise Exception(f"Charts gagal: {str(e)}")