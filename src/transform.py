from typing import Any


def transform_track_item(track: dict[str, Any], query: str) -> dict[str, Any]:
    album = track.get("album", {})
    artists = track.get("artists", [])
    external_urls = track.get("external_urls", {})

    return {
        "spotify_track_id": track.get("id"),
        "track_name": track.get("name"),
        "artist_names": [artist.get("name") for artist in artists],
        "artist_ids": [artist.get("id") for artist in artists],
        "album_id": album.get("id"),
        "album_name": album.get("name"),
        "release_date": album.get("release_date"),
        "duration_ms": track.get("duration_ms"),
        "explicit": track.get("explicit"),
        "popularity": track.get("popularity"),
        "preview_url": track.get("preview_url"),
        "spotify_url": external_urls.get("spotify"),
        "spotify_uri": track.get("uri"),
        "search_query": query,
    }


def transform_search_results(search_result: dict[str, Any], query: str) -> list[dict[str, Any]]:
    items = search_result.get("tracks", {}).get("items", [])
    return [transform_track_item(track, query) for track in items if track.get("id")]