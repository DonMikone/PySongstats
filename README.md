# songstats-py

Python client for Songstats API. Please note that this wrapper does not provide the API's entire functions.

## Installation

```bash
pip install songstats-py
```

## Usage

### Testing Mode

The client supports a testing mode that uses mock endpoints:

```python
from songstats import SongstatsClient

# Production mode (default)
client = SongstatsClient("your_api_key")

# Testing mode (uses mock API)
test_client = SongstatsClient(testing=True)

# All endpoints will use the mock server in testing mode
mock_track = test_client.track.info("TEST123")
```

**Note:** The testing endpoint doesn't require a real API key and returns static mock data.

### Basic Example

```python
from songstats import SongstatsClient

# Initialize client with your API key
client = SongstatsClient("your_api_key")

# Get track info by ISRC
track = client.track.info("USUG12200981")
print(f"{track.title} by {', '.join(a.name for a in track.artists)}")
print(f"Release date: {track.release_date}")
print(f"Danceability: {track.get_audio_feature('danceability')}")

# Get current stats
stats = client.track.current_stats("USUG12200981")
for stat in stats:
    print(f"{stat.source}: {stat.streams_total} streams")

# Get artist info
artist = client.artist.info("abc123artistid")
print(f"{artist.name} has {len(artist.related_artists)} related artists")
```

### Available Methods

#### Tracks
- `client.track.info(isrc: str) -> TrackInfo`
- `client.track.current_stats(isrc: str) -> List[TrackStats]`
- `client.track.historic_stats(isrc: str) -> Dict[str, List[HistoricStats]]`
- `client.track.latest_activities(isrc: str, editorial: bool = False) -> List[Activity]`

#### Artists
- `client.artist.info(artist_id: str) -> ArtistInfo`

#### Status
- `client.status.info() -> Dict[str, Any]`

## Models Overview

Key data models returned by the API:

- `TrackInfo`: Core track metadata
- `TrackStats`: Current platform statistics
- `HistoricStats`: Historical data points
- `ArtistInfo`: Artist details and relations
- `Activity`: Recent track activities

## Error Handling

The client raises specific exceptions for API errors:

```python
from songstats.exceptions import APIError, RateLimitException

try:
    track = client.track.info("invalid_isrc")
except RateLimitException:
    print("Rate limit exceeded - please wait")
except APIError as e:
    print(f"API Error {e.status_code}: {e.message}")
```

## Development

Install dependencies:
```bash
pip install -e .
```

Run tests:
```bash
pytest
```