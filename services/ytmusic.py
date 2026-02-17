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

        # Coba beberapa kemungkinan struktur response
        songs_data = None

        if charts.get("songs"):
            songs_data = charts["songs"].get("items", [])
        elif charts.get("videos"):
            songs_data = charts["videos"].get("items", [])
        elif charts.get("trending"):
            songs_data = charts["trending"].get("items", [])

        # Kalau semua kosong, ambil key apapun yang ada items-nya
        if not songs_data:
            for key, val in charts.items():
                if isinstance(val, dict) and val.get("items"):
                    songs_data = val["items"]
                    break

        if not songs_data:
            # Fallback: return lagu populer via search
            results = ytm.search("top hits indonesia 2024", filter="songs", limit=20)
            for item in results:
                if item.get("videoId"):
                    top_songs.append({
                        "id":        item.get("videoId", ""),
                        "title":     item.get("title", ""),
                        "artist":    item["artists"][0]["name"] if item.get("artists") else "",
                        "thumbnail": item["thumbnails"][-1]["url"] if item.get("thumbnails") else "",
                        "rank":      len(top_songs) + 1,
                    })
        else:
            for i, item in enumerate(songs_data[:20]):
                video_id = (
                    item.get("videoId") or
                    item.get("video", {}).get("videoId") or
                    ""
                )
                title = (
                    item.get("title") or
                    item.get("video", {}).get("title") or
                    "Unknown"
                )
                artists = (
                    item.get("artists") or
                    item.get("video", {}).get("artists") or
                    []
                )
                thumbnails = (
                    item.get("thumbnails") or
                    item.get("video", {}).get("thumbnails") or
                    []
                )
                if video_id:
                    top_songs.append({
                        "id":        video_id,
                        "title":     title,
                        "artist":    artists[0]["name"] if artists else "Unknown",
                        "thumbnail": thumbnails[-1]["url"] if thumbnails else "",
                        "rank":      item.get("rank", i + 1),
                    })

        return {"country": country, "top_songs": top_songs}

    except Exception as e:
        # Ultimate fallback — search hits Indonesia
        try:
            results = ytm.search("lagu hits indonesia", filter="songs", limit=20)
            top_songs = []
            for item in results:
                if item.get("videoId"):
                    top_songs.append({
                        "id":        item.get("videoId", ""),
                        "title":     item.get("title", ""),
                        "artist":    item["artists"][0]["name"] if item.get("artists") else "",
                        "thumbnail": item["thumbnails"][-1]["url"] if item.get("thumbnails") else "",
                        "rank":      len(top_songs) + 1,
                    })
            return {"country": country, "top_songs": top_songs}
        except:
            raise Exception(f"Charts gagal: {str(e)}")