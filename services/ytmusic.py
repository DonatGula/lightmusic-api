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