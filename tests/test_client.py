import pytest
from unittest.mock import Mock, patch
from songstats import SongstatsClient
from songstats.exceptions import APIError


@pytest.fixture
def mock_client():
    with patch('requests.Session') as mock_session:
        yield SongstatsClient("test_key")


def test_track_info(mock_client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": "success",
        "track_info": {
            "songstats_track_id": "test123",
            "title": "Test Track",
            "artists": [{"name": "Test Artist", "songstats_artist_id": "art123"}],
            "release_date": "2023-01-01"
        },
        "audio_analysis": []
    }
    mock_client._session.get.return_value = mock_response

    track = mock_client.track.info("TEST123")
    assert track.title == "Test Track"
    assert len(track.artists) == 1


def test_error_handling(mock_client):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"message": "Not found"}
    mock_client._session.get.return_value = mock_response

    with pytest.raises(APIError):
        mock_client.track.info("invalid_isrc")