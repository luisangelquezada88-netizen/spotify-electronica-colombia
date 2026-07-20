from datetime import datetime
import re

from src.mongo import get_collection


def parse_search_query(search_query):
    term = None
    year = None
    if search_query:
        m = re.search(r'^(.*?)\s+year:(\d{4})$', search_query.strip())
        if m:
            term = m.group(1).strip() or None
            year = int(m.group(2))
        else:
            term = search_query.strip() or None
    return term, year


def build_doc(doc):
    artist_names = doc.get('artist_names') or []
    release_date = doc.get('release_date')
    release_year = None
    release_date_parsed = None

    if release_date:
        try:
            release_date_parsed = datetime.strptime(release_date, '%Y-%m-%d')
            release_year = release_date_parsed.year
        except ValueError:
            release_date_parsed = None

    search_term, search_year = parse_search_query(doc.get('search_query'))
    duration_ms = doc.get('duration_ms')

    return {
        'spotify_track_id': doc.get('spotify_track_id'),
        'spotify_uri': doc.get('spotify_uri'),
        'spotify_url': doc.get('spotify_url'),
        'track_name': doc.get('track_name'),
        'album_name': doc.get('album_name'),
        'album_id': doc.get('album_id'),
        'artist_ids': doc.get('artist_ids') or [],
        'artist_names': artist_names,
        'artist_count': len(artist_names),
        'duration_ms': duration_ms,
        'duration_min': round(duration_ms / 60000, 2) if isinstance(duration_ms, (int, float)) else None,
        'explicit': bool(doc.get('explicit')) if doc.get('explicit') is not None else None,
        'popularity': doc.get('popularity'),
        'popularity_filled': doc.get('popularity') if doc.get('popularity') is not None else 0,
        'preview_url': doc.get('preview_url'),
        'has_preview': bool(doc.get('preview_url')),
        'release_date': release_date,
        'release_date_parsed': release_date_parsed,
        'release_year': release_year,
        'search_query': doc.get('search_query'),
        'search_term': search_term,
        'search_year': search_year,
        'source_curated_id': str(doc.get('_id')),
    }


def main():
    source = get_collection('curated_tracks')
    target = get_collection('analysis_tracks')

    target.delete_many({})
    docs = [build_doc(doc) for doc in source.find({})]

    if docs:
        target.insert_many(docs)

    print(f'analysis_tracks: {len(docs)}')


if __name__ == '__main__':
    main()