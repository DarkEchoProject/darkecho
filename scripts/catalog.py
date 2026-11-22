"""Validate source metadata before it can produce public pages."""
from datetime import date, datetime
import re


def validate_catalog(catalog):
    date.fromisoformat(catalog['updatedAt'])
    videos = catalog.get('videos')
    if not isinstance(videos, list) or not videos:
        raise ValueError('The video catalog must be a nonempty list')
    seen = set()
    for video in videos:
        identifier = video['id']
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', identifier) or identifier in seen:
            raise ValueError('Invalid or duplicate video ID: ' + identifier)
        seen.add(identifier)
        for field in ['title', 'sourceTitle', 'summary', 'topic', 'channelName']:
            if not isinstance(video[field], str) or not video[field].strip():
                raise ValueError(f'{identifier}: missing {field}')
        if video['channel'] not in {'darkecho', 'extreme', 'nasser'}:
            raise ValueError(identifier + ': unknown channel')
        if not re.fullmatch(r'https://www\.youtube\.com/(?:@[^ /]+|channel/[^ /]+)', video['channelUrl']):
            raise ValueError(identifier + ': invalid channel URL')
        for field in ['seconds', 'views']:
            if type(video[field]) is not int or video[field] < (1 if field == 'seconds' else 0):
                raise ValueError(f'{identifier}: invalid {field}')
        match = re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', video['duration'])
        if not match or not any(match.groups()):
            raise ValueError(identifier + ': invalid ISO duration')
        seconds = sum(int(value or 0) * scale for value, scale in zip(match.groups(), [3600, 60, 1]))
        if seconds != video['seconds']:
            raise ValueError(identifier + ': duration differs from seconds')
        if video['format'] != ('clip' if seconds <= 180 else 'video'):
            raise ValueError(identifier + ': incorrect running-time category')
        published = datetime.fromisoformat(video['uploadDate'].replace('Z', '+00:00'))
        if published.tzinfo is None:
            raise ValueError(identifier + ': publication timestamp needs a timezone')
        if video['thumbnail'] != f'assets/thumbs/{identifier}-640.webp':
            raise ValueError(identifier + ': thumbnail does not match video ID')
    return seen
