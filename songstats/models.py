import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional, List, Dict, Any, Union


@dataclass
class AudioFeature:
    key: str
    value: Union[float, str, timedelta]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFeature':
        key = key = str(data.get('key', ''))
        raw_value = data.get('value')

        if key == 'duration':
            try:
                minutes, seconds = map(int, raw_value.split(':'))
                value = timedelta(minutes=minutes, seconds=seconds)
            except (ValueError, AttributeError):
                logging.warning(f"Invalid duration format: {raw_value}")
                value = timedelta(0)

        elif key == 'key':
            value = str(raw_value) if raw_value is not None else ''

        else:
            try:
                value = float(raw_value)
            except (ValueError, TypeError):
                logging.warning(f"Invalid float value for {key}: {raw_value}")
                value = 0.0

        return cls(key=key, value=value)


@dataclass
class Link:
    source: str
    external_id: str
    url: str
    isrc: Optional[str] = None


@dataclass
class ArtistInfo:
    name: str
    songstats_artist_id: str
    avatar: Optional[str] = None
    site_url: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    links: List['Link'] = field(default_factory=list)
    related_artists: List['ArtistInfo'] = field(default_factory=list)

    def __str__(self):
        return self.name


@dataclass
class Collaborator:
    name: str
    roles: List[str]
    songstats_collaborator_id: str


@dataclass
class Label:
    name: str
    songstats_label_id: str


@dataclass
class Distributor:
    name: str


@dataclass
class Playlist:
    name: str
    external_url: str
    artwork: str
    owner_name: str
    top_position: int
    top_position_date: str
    added_at: str
    removed_at: Optional[str] = None
    current_position: Optional[int] = None
    followers_count: Optional[int] = None
    spotifyid: Optional[str] = None
    spotify_userid: Optional[str] = None
    applemusicid: Optional[str] = None
    curator_name: Optional[str] = None
    curator_id: Optional[str] = None
    playlist_country_code: Optional[str] = None
    playlist_type: Optional[str] = None
    amazonid: Optional[str] = None
    rank: Optional[int] = None
    region: Optional[str] = None
    deezerid: Optional[str] = None
    deezer_userid: Optional[str] = None
    chart_type: Optional[str] = None


@dataclass
class Chart:
    name: str
    top_position: int
    top_position_date: str
    added_at: str
    removed_at: Optional[str] = None
    current_position: Optional[int] = None
    location_type: Optional[str] = None
    shazamid: Optional[str] = None
    external_url: Optional[str] = None
    applemusicid: Optional[str] = None
    chart_type: Optional[str] = None
    followers_count: Optional[int] = None
    owner_name: Optional[str] = None
    artwork: Optional[str] = None
    deezerid: Optional[str] = None
    deezer_userid: Optional[str] = None


@dataclass
class Video:
    external_id: str
    title: str
    view_count: int
    like_count: int
    comment_count: int
    upload_date: str
    image_url: str
    dislike_count: Optional[int] = None


@dataclass
class ShortVideo:
    external_id: str
    title: str
    view_count: int
    like_count: int
    comment_count: int
    upload_date: str
    image_url: str


@dataclass
class TrackStats:
    source: str
    streams_total: Optional[int] = None
    popularity_current: Optional[int] = None
    playlists_current: Optional[int] = None
    playlists_total: Optional[int] = None
    playlists_editorial_current: Optional[int] = None
    playlists_editorial_total: Optional[int] = None
    playlist_reach_current: Optional[int] = None
    playlist_reach_total: Optional[int] = None
    charts_current: Optional[int] = None
    charts_total: Optional[int] = None
    shazams_total: Optional[int] = None
    engagement_rate_total: Optional[float] = None
    videos_total: Optional[int] = None
    video_views_total: Optional[int] = None
    video_likes_total: Optional[int] = None
    video_comments_total: Optional[int] = None
    shorts_total: Optional[int] = None
    short_views_total: Optional[int] = None
    short_likes_total: Optional[int] = None
    short_comments_total: Optional[int] = None
    creator_reach_total: Optional[int] = None
    favorites_total: Optional[int] = None
    reposts_total: Optional[int] = None
    playlists: List[Playlist] = field(default_factory=list)
    charts: List[Chart] = field(default_factory=list)
    videos: List[Video] = field(default_factory=list)
    shorts: List[ShortVideo] = field(default_factory=list)


@dataclass
class HistoricStats:
    date: str
    streams_total: Optional[int] = None
    popularity_current: Optional[int] = None
    playlists_current: Optional[int] = None
    playlists_total: Optional[int] = None
    playlists_editorial_current: Optional[int] = None
    playlists_editorial_total: Optional[int] = None
    playlist_reach_current: Optional[int] = None
    playlist_reach_total: Optional[int] = None
    charts_current: Optional[int] = None
    charts_total: Optional[int] = None
    shazams_total: Optional[int] = None
    engagement_rate_total: Optional[float] = None
    videos_total: Optional[int] = None
    video_views_total: Optional[int] = None
    video_likes_total: Optional[int] = None
    video_comments_total: Optional[int] = None
    shorts_total: Optional[int] = None
    short_views_total: Optional[int] = None
    short_likes_total: Optional[int] = None
    short_comments_total: Optional[int] = None
    creator_reach_total: Optional[int] = None
    favorites_total: Optional[int] = None
    reposts_total: Optional[int] = None
    total_supports: Optional[int] = None
    unique_supports: Optional[int] = None
    dj_charts_total: Optional[int] = None


@dataclass
class Activity:
    source: str
    activity_text: str
    activity_type: str
    activity_date: str
    activity_tier: int
    activity_url: Optional[str] = None
    activity_avatar: Optional[str] = None


@dataclass
class TrackInfo:
    songstats_track_id: str
    title: str
    artists: List[ArtistInfo]
    release_date: str
    avatar: Optional[str] = None
    site_url: Optional[str] = None
    labels: List[Label] = field(default_factory=list)
    distributors: List[Distributor] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    collaborators: List[Collaborator] = field(default_factory=list)
    audio_features: List[AudioFeature] = field(default_factory=list)

    def __str__(self):
        return f"{', '.join(str(a) for a in self.artists)} - {self.title}"

    def get_audio_feature(self, feature_name: str) -> Optional[float]:
        for feature in self.audio_features:
            if feature.key == feature_name:
                return feature.value
        return None

    @property
    def isrc(self) -> Optional[str]:
        for link in self.links:
            if link.isrc:
                return link.isrc
        return None

    @property
    def isrcs(self) -> Optional[List[str]]:
        return [l.isrc for l in self.links if l.isrc is not None]
