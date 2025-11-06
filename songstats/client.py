import time
from typing import Dict, Any, List, Optional
import requests
from .constants import BASE_URL_PROD, BASE_URL_TEST
from .exceptions import error_map, APIError, RateLimitException, ParameterError
from .models import (
    TrackInfo, TrackStats, HistoricStats,
    ArtistInfo, Activity, AudioFeature, Link,
    Playlist, Chart, Video, ShortVideo, Label, Distributor, Collaborator
)


class TrackEndpoints:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url.rstrip('/')

    def info(self, isrc: str = None, spotify_id: str = None) -> TrackInfo:
        if not isrc and not spotify_id:
            raise ParameterError('At least one of isrc or spotify_id must be provided!')
        if isrc:
            response = self._get("/tracks/info", {"isrc": isrc})
        else:
            response = self._get("/tracks/info", {"spotify_track_id": spotify_id})
        data = response.json()
        return self._parse_track_info(data)

    def current_stats(self, isrc: str) -> List[TrackStats]:
        response = self._get("/tracks/stats", {"isrc": isrc})
        data = response.json()
        return self._parse_stats(data['stats'])

    def historic_stats(self, isrc: str) -> Dict[str, List[HistoricStats]]:
        response = self._get("/tracks/historic_stats", {"isrc": isrc})
        data = response.json()
        return {
            source['source']: [HistoricStats(**entry) for entry in source['data']['history']]
            for source in data['stats']
        }

    def latest_activities(self, isrc: str, editorial: bool = False) -> List[Activity]:
        response = self._get("/tracks/activities", {
            "isrc": isrc,
            "editorial": str(editorial).lower()
        })
        data = response.json()
        return [Activity(**activity) for activity in data['activities']]

    def _parse_track_info(self, data: Dict[str, Any]) -> TrackInfo:
        track_data = data['track_info']
        audio_features = [AudioFeature.from_dict(f) for f in data.get('audio_analysis', [])]

        artists = [
            ArtistInfo(
                name=artist['name'],
                songstats_artist_id=artist['songstats_artist_id']
            ) for artist in track_data.get('artists', [])
        ]

        labels = [
            Label(
                name=label['name'],
                songstats_label_id=label['songstats_label_id']
            ) for label in track_data.get('labels', [])
        ]

        distributors = [
            Distributor(name=dist['name'])
            for dist in track_data.get('distributors', [])
        ]

        genres = track_data.get('genres', [])

        links = [
            Link(
                source=link['source'],
                external_id=link['external_id'],
                url=link['url'],
                isrc=link.get('isrc')
            ) for link in track_data.get('links', [])
        ]

        collaborators = [
            Collaborator(
                name=collab['name'],
                roles=collab['roles'],
                songstats_collaborator_id=collab['songstats_collaborator_id']
            ) for collab in track_data.get('collaborators', [])
        ]

        return TrackInfo(
            songstats_track_id=track_data['songstats_track_id'],
            title=track_data['title'],
            artists=artists,
            release_date=track_data['release_date'],
            avatar=track_data.get('avatar'),
            site_url=track_data.get('site_url'),
            labels=labels,
            distributors=distributors,
            genres=genres,
            links=links,
            collaborators=collaborators,
            audio_features=audio_features
        )

    def _parse_stats(self, stats_data: List[Dict[str, Any]]) -> List[TrackStats]:
        stats = []
        for source_data in stats_data:
            source = source_data['source']
            data = source_data['data']

            playlists = [
                Playlist(
                    name=pl['name'],
                    external_url=pl['external_url'],
                    artwork=pl['artwork'],
                    owner_name=pl['owner_name'],
                    top_position=pl['top_position'],
                    top_position_date=pl['top_position_date'],
                    added_at=pl['added_at'],
                    removed_at=pl.get('removed_at'),
                    current_position=pl.get('current_position'),
                    followers_count=pl.get('followers_count'),
                    spotifyid=pl.get('spotifyid'),
                    spotify_userid=pl.get('spotify_userid'),
                    applemusicid=pl.get('applemusicid'),
                    curator_name=pl.get('curator_name'),
                    curator_id=pl.get('curator_id'),
                    playlist_country_code=pl.get('playlist_country_code'),
                    playlist_type=pl.get('playlist_type'),
                    amazonid=pl.get('amazonid'),
                    rank=pl.get('rank'),
                    region=pl.get('region'),
                    deezerid=pl.get('deezerid'),
                    deezer_userid=pl.get('deezer_userid'),
                    chart_type=pl.get('chart_type')
                ) for pl in data.get('playlists', [])
            ]

            charts = [
                Chart(
                    name=chart['name'],
                    top_position=chart['top_position'],
                    top_position_date=chart['top_position_date'],
                    added_at=chart['added_at'],
                    removed_at=chart.get('removed_at'),
                    current_position=chart.get('current_position'),
                    location_type=chart.get('location_type'),
                    shazamid=chart.get('shazamid'),
                    external_url=chart.get('external_url'),
                    applemusicid=chart.get('applemusicid'),
                    chart_type=chart.get('chart_type'),
                    followers_count=chart.get('followers_count'),
                    owner_name=chart.get('owner_name'),
                    artwork=chart.get('artwork'),
                    deezerid=chart.get('deezerid'),
                    deezer_userid=chart.get('deezer_userid')
                ) for chart in data.get('charts', []) +
                               data.get('track_charts', []) +
                               data.get('album_charts', []) +
                               data.get('features', [])
            ]

            videos = [
                Video(
                    external_id=video['external_id'],
                    title=video.get('title', ''),
                    view_count=video['view_count'],
                    like_count=video['like_count'],
                    comment_count=video['comment_count'],
                    upload_date=video['upload_date'],
                    image_url=video['image_url'],
                    dislike_count=video.get('dislike_count')
                ) for video in data.get('videos', [])
            ]

            shorts = [
                ShortVideo(
                    external_id=short['external_id'],
                    title=short.get('title', ''),
                    view_count=short['view_count'],
                    like_count=short['like_count'],
                    comment_count=short['comment_count'],
                    upload_date=short['upload_date'],
                    image_url=short['image_url']
                ) for short in data.get('shorts', [])
            ]

            stats.append(TrackStats(
                source=source,
                streams_total=data.get('streams_total'),
                popularity_current=data.get('popularity_current'),
                playlists_current=data.get('playlists_current'),
                playlists_total=data.get('playlists_total'),
                playlists_editorial_current=data.get('playlists_editorial_current'),
                playlists_editorial_total=data.get('playlists_editorial_total'),
                playlist_reach_current=data.get('playlist_reach_current'),
                playlist_reach_total=data.get('playlist_reach_total'),
                charts_current=data.get('charts_current'),
                charts_total=data.get('charts_total'),
                shazams_total=data.get('shazams_total'),
                engagement_rate_total=data.get('engagement_rate_total'),
                videos_total=data.get('videos_total'),
                video_views_total=data.get('video_views_total'),
                video_likes_total=data.get('video_likes_total'),
                video_comments_total=data.get('video_comments_total'),
                shorts_total=data.get('shorts_total'),
                short_views_total=data.get('short_views_total'),
                short_likes_total=data.get('short_likes_total'),
                short_comments_total=data.get('short_comments_total'),
                creator_reach_total=data.get('creator_reach_total'),
                favorites_total=data.get('favorites_total'),
                reposts_total=data.get('reposts_total'),
                playlists=playlists,
                charts=charts,
                videos=videos,
                shorts=shorts
            ))
        return stats

    def _get(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        for _ in range(3):
            res = self.session.get(url, params=params)
            if res.status_code == 200:
                return res
            elif res.status_code == 429:
                time.sleep(2)
            elif res.status_code in error_map:
                raise error_map[res.status_code].from_response(res)
            else:
                raise APIError.from_response(res)
        raise RateLimitException("Rate limit exceeded after retries.")


class ArtistEndpoints:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url.rstrip('/')

    def info(self, artist_id: str) -> ArtistInfo:
        response = self._get("/artists/info", {"songstats_artist_id": artist_id})
        data = response.json()
        artist_data = data['artist_info']

        links = [
            Link(
                source=link['source'],
                external_id=link['external_id'],
                url=link['url']
            ) for link in artist_data.get('links', [])
        ]

        related_artists = [
            ArtistInfo(
                name=artist['name'],
                songstats_artist_id=artist['songstats_artist_id'],
                avatar=artist.get('avatar'),
                site_url=artist.get('site_url')
            ) for artist in artist_data.get('related_artists', [])
        ]

        return ArtistInfo(
            songstats_artist_id=artist_data['songstats_artist_id'],
            name=artist_data['name'],
            avatar=artist_data.get('avatar'),
            site_url=artist_data.get('site_url'),
            country=artist_data.get('country'),
            bio=artist_data.get('bio'),
            genres=artist_data.get('genres', []),
            links=links,
            related_artists=related_artists
        )

    def _get(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        res = self.session.get(url, params=params)
        if res.status_code == 200:
            return res
        elif res.status_code in error_map:
            raise error_map[res.status_code].from_response(res)
        else:
            raise APIError.from_response(res)


class StatusEndpoints:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url.rstrip('/')

    def info(self) -> Dict[str, Any]:
        response = self._get("/status")
        return response.json()['status']

    def _get(self, endpoint: str) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        res = self.session.get(url)
        if res.status_code == 200:
            return res
        elif res.status_code in error_map:
            raise error_map[res.status_code].from_response(res)
        else:
            raise APIError.from_response(res)


class CollaboratorEndpoints:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url.rstrip('/')

    def top_tracks(
            self,
            songstats_collaborator_id: Optional[str] = None,
            tidal_artist_id: Optional[str] = None,
            limit: Optional[int] = None,
            metric: Optional[str] = 'streams',
            scope: Optional[str] = 'total',
            source: Optional[str] = 'spotify',
    ) -> Dict[str, Any]:
        """
        Retrieve top tracks for a collaborator.

        Endpoint:
            https://api.songstats.com/enterprise/v1/collaborators/top_tracks

        Parameters:
            songstats_collaborator_id (str, optional): Songstats collaborator ID
            tidal_artist_id (str, optional): TIDAL artist ID
            limit (int, optional): Number of results to return
            metric (str, optional): Metric to use (e.g. 'playlists', 'streams', ...)
            scope (str, optional): Scope for metric (e.g. 'total', 'daily', ...)
            source (str, optional): Source (e.g. 'spotify', 'apple_music', ...)
        """
        if not songstats_collaborator_id and not tidal_artist_id:
            raise ParameterError(
                "At least one of 'songstats_collaborator_id' or 'tidal_artist_id' must be provided."
            )

        params: Dict[str, Any] = {}
        if songstats_collaborator_id:
            params["songstats_collaborator_id"] = songstats_collaborator_id
        if tidal_artist_id:
            params["tidal_artist_id"] = tidal_artist_id
        if limit is not None:
            params["limit"] = limit
        if metric is not None:
            params["metric"] = metric
        if scope is not None:
            params["scope"] = scope
        if source is not None:
            params["source"] = source

        res = self._get("/collaborators/top_tracks", params)
        data = res.json()

        # Alle Track-Einträge aus data[*].top_tracks zu einer flachen Liste zusammenführen
        flat_top_tracks = []
        for entry in data.get("data", []):
            for track in entry.get("top_tracks", []):
                flat_top_tracks.append(track)

        return {
            "result": data.get("result"),
            "message": data.get("message"),
            "data": data.get("data", []),  # Originalstruktur beibehalten
            "top_tracks": flat_top_tracks,
            "collaborator_info": data.get("collaborator_info", {}),
            "source_ids": data.get("source_ids", []),
        }

    def info(
            self,
            songstats_collaborator_id: Optional[str] = None,
            tidal_artist_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve detailed info for a collaborator.

        Endpoint:
            https://api.songstats.com/enterprise/v1/collaborators/info

        Parameters:
            songstats_collaborator_id (str, optional): Songstats collaborator ID
            tidal_artist_id (str, optional): TIDAL artist ID
        """
        if not songstats_collaborator_id and not tidal_artist_id:
            raise ParameterError(
                "At least one of 'songstats_collaborator_id' or 'tidal_artist_id' must be provided."
            )

        params: Dict[str, Any] = {}
        if songstats_collaborator_id:
            params["songstats_collaborator_id"] = songstats_collaborator_id
        if tidal_artist_id:
            params["tidal_artist_id"] = tidal_artist_id

        res = self._get("/collaborators/info", params)
        data = res.json()

        return {
            "result": data.get("result"),
            "message": data.get("message"),
            "collaborator_info": data.get("collaborator_info", {}),
        }

    def catalog(
            self,
            songstats_collaborator_id: Optional[str] = None,
            tidal_artist_id: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            with_links: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve the catalog for a collaborator.

        At least one of songstats_collaborator_id or tidal_artist_id must be provided.
        """
        if not songstats_collaborator_id and not tidal_artist_id:
            raise ParameterError(
                'At least one of songstats_collaborator_id or tidal_artist_id must be provided!'
            )

        params: Dict[str, Any] = {}
        if songstats_collaborator_id:
            params['songstats_collaborator_id'] = songstats_collaborator_id
        if tidal_artist_id:
            params['tidal_artist_id'] = tidal_artist_id
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if with_links:
            params['with_links'] = True

        res = self._get("/collaborators/catalog", params)
        data = res.json()

        catalog_items: List[TrackInfo] = []
        for item in data.get('catalog', []):
            artists = [
                ArtistInfo(
                    name=artist['name'],
                    songstats_artist_id=artist['songstats_artist_id'],
                    avatar=artist.get('avatar'),
                    site_url=artist.get('site_url')
                ) for artist in item.get('artists', [])
            ]

            catalog_items.append(
                TrackInfo(
                    songstats_track_id=item['songstats_track_id'],
                    title=item['title'],
                    artists=artists,
                    release_date=item.get('release_date'),
                    avatar=item.get('avatar'),
                    site_url=item.get('site_url'),
                    labels=[],
                    distributors=[],
                    genres=[],
                    links=[],
                    collaborators=[],
                    audio_features=[]
                )
            )

        return {
            'result': data.get('result'),
            'message': data.get('message'),
            'catalog': catalog_items,
            'collaborator_info': data.get('collaborator_info', {}),
            'tracks_total': data.get('tracks_total', 0),
            'next_url': data.get('next_url')
        }

    def search(
            self,
            q: str,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search collaborators by name and return possible matches.

        Endpoint:
            https://api.songstats.com/enterprise/v1/collaborators/search

        Parameters:
            q (str): Search query (required)
            limit (int, optional): Number of results to return
            offset (int, optional): Offset for pagination
        """
        if not q or not q.strip():
            raise ParameterError("Parameter 'q' (search query) is required.")

        params: Dict[str, Any] = {"q": q.strip()}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        res = self._get("/collaborators/search", params)
        data = res.json()

        return {
            "result": data.get("result"),
            "message": data.get("message"),
            "results": data.get("results", []),
        }

    def _get(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        for _ in range(3):
            res = self.session.get(url, params=params)
            if res.status_code == 200:
                return res
            elif res.status_code == 429:
                time.sleep(2)
            elif res.status_code in error_map:
                raise error_map[res.status_code].from_response(res)
            else:
                raise APIError.from_response(res)
        raise RateLimitException("Rate limit exceeded after retries.")


class SongstatsClient:
    def __init__(self, api_key: Optional[str] = None, testing: bool = False):
        """
        Initialize the Songstats API client

        Args:
            api_key: Your Songstats API key (ignored in testing mode)
            testing: If True, uses the mock API endpoint with fixed test key (default: False)
        """
        self.session = requests.Session()

        if testing:
            self.base_url = BASE_URL_TEST
            api_key = "123"  # Fixed test key
        else:
            if not api_key:
                raise ValueError("API key is required for production mode")
            self.base_url = BASE_URL_PROD

        self.session.headers.update({
            "Accept": "application/json",
            "apikey": api_key
        })

        self._track = TrackEndpoints(self.session, self.base_url)
        self._status = StatusEndpoints(self.session, self.base_url)
        self._artist = ArtistEndpoints(self.session, self.base_url)
        self._collaborator = CollaboratorEndpoints(self.session, self.base_url)

    @property
    def track(self) -> TrackEndpoints:
        return self._track

    @property
    def status(self) -> StatusEndpoints:
        return self._status

    @property
    def artist(self) -> ArtistEndpoints:
        return self._artist

    @property
    def collaborator(self) -> CollaboratorEndpoints:
        return self._collaborator
