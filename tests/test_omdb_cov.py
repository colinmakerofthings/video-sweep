import pytest
from unittest.mock import patch
import requests
from video_sweep.omdb import query_omdb, get_api_key_from_config, get_suggested_name


# Test get_api_key_from_config exception handling
@patch("video_sweep.omdb.toml.load", side_effect=Exception("fail"))
def test_get_api_key_from_config_exception(mock_toml):
    assert get_api_key_from_config() is None


# Test query_omdb: fuzzy search with no matches
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_fuzzy_no_match(mock_get, mock_key):
    # direct fails, search returns no results
    def side_effect(*args, **kwargs):
        url = args[0]
        if "t=" in url or kwargs.get("params", {}).get("t"):
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        elif "s=" in url or kwargs.get("params", {}).get("s"):
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    assert query_omdb("NoMatchTitle", "2020") is None


# Test query_omdb: fuzzy search with match below threshold
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_fuzzy_below_threshold(mock_get, mock_key):
    def side_effect(*args, **kwargs):
        url = args[0]
        if "t=" in url or kwargs.get("params", {}).get("t"):
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        elif "s=" in url or kwargs.get("params", {}).get("s"):
            return type(
                "resp",
                (),
                {
                    "status_code": 200,
                    "json": (
                        lambda *a, **k: {
                            "Response": "True",
                            "Search": [{"Title": "X", "Year": "2020", "imdbID": "id1"}],
                        }
                    ),
                },
            )()
        elif "i=" in url or kwargs.get("params", {}).get("i"):
            return type(
                "resp",
                (),
                {
                    "status_code": 200,
                    "json": (
                        lambda *a, **k: {
                            "Response": "True",
                            "Title": "X",
                            "Year": "2020",
                        }
                    ),
                },
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    # Title and candidate are too different, so threshold not met
    assert query_omdb("ZZZZZZZZZZ", "2020") is None


# Test query_omdb: title with only non-alphabetic characters
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_title_nonalpha(mock_get, mock_key):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Response": "False"}
    assert query_omdb("1234567890!@#$", "2020") is None


# Test get_suggested_name with missing title or year
@pytest.mark.parametrize(
    "data,expected",
    [
        ({"Title": "Movie"}, None),
        ({"Year": "2020"}, None),
        ({}, None),
    ],
)
def test_get_suggested_name_missing(data, expected):
    assert get_suggested_name(data) == expected


# New tests for HTTP error codes
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_http_429_rate_limit(mock_get, mock_key):
    """Test query_omdb with HTTP 429 (rate limit)."""
    mock_get.return_value.status_code = 429
    mock_get.return_value.json.return_value = {}
    result = query_omdb("Movie", "2020")
    # Should fallback to fuzzy search, eventually return None
    assert result is None


@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_http_500_server_error(mock_get, mock_key):
    """Test query_omdb with HTTP 500 (server error)."""
    mock_get.return_value.status_code = 500
    mock_get.return_value.json.return_value = {}
    result = query_omdb("Movie", "2020")
    # Should fallback to fuzzy search, eventually return None
    assert result is None


@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_http_503_service_unavailable(mock_get, mock_key):
    """Test query_omdb with HTTP 503 (service unavailable)."""
    mock_get.return_value.status_code = 503
    mock_get.return_value.json.return_value = {}
    result = query_omdb("Movie", "2020")
    assert result is None


@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_http_401_unauthorized(mock_get, mock_key):
    """Test query_omdb with HTTP 401 (unauthorized/invalid API key)."""
    mock_get.return_value.status_code = 401
    mock_get.return_value.json.return_value = {"Error": "Invalid API key"}
    result = query_omdb("Movie", "2020")
    assert result is None


# Test network timeout
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_timeout(mock_get, mock_key):
    """Test query_omdb with network timeout."""
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
    # Should handle timeout gracefully
    with pytest.raises(requests.exceptions.Timeout):
        query_omdb("Movie", "2020")


# Test malformed JSON response
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_malformed_json(mock_get, mock_key):
    """Test query_omdb when response.json() throws exception."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = ValueError("Invalid JSON")
    # Should handle JSON error gracefully
    with pytest.raises(ValueError):
        query_omdb("Movie", "2020")


# Test search response missing imdbID
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_search_missing_imdbid(mock_get, mock_key):
    """Test fuzzy search when result is missing imdbID."""

    def side_effect(*args, **kwargs):
        params = kwargs.get("params", {})
        if "t" in params:
            # Direct search fails
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        elif "s" in params:
            # Search returns result without imdbID
            return type(
                "resp",
                (),
                {
                    "status_code": 200,
                    "json": (
                        lambda *a, **k: {
                            "Response": "True",
                            "Search": [
                                {"Title": "Movie", "Year": "2020"}  # Missing imdbID
                            ],
                        }
                    ),
                },
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    result = query_omdb("Movie", "2020")
    assert result is None


# Test search response missing Search key
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_search_missing_search_key(mock_get, mock_key):
    """Test fuzzy search when response is missing Search key."""

    def side_effect(*args, **kwargs):
        params = kwargs.get("params", {})
        if "t" in params:
            # Direct search fails
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        elif "s" in params:
            # Search returns True but no Search key
            return type(
                "resp",
                (),
                {
                    "status_code": 200,
                    "json": (lambda *a, **k: {"Response": "True"}),  # Missing Search
                },
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    result = query_omdb("Movie", "2020")
    assert result is None


# Test ID lookup failure
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_id_lookup_fails(mock_get, mock_key):
    """Test when ID lookup (third request) fails."""

    def side_effect(*args, **kwargs):
        params = kwargs.get("params", {})
        if "t" in params:
            # Direct search fails
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        elif "s" in params:
            # Search succeeds
            return type(
                "resp",
                (),
                {
                    "status_code": 200,
                    "json": (
                        lambda *a, **k: {
                            "Response": "True",
                            "Search": [
                                {"Title": "Movie", "Year": "2020", "imdbID": "tt123"}
                            ],
                        }
                    ),
                },
            )()
        elif "i" in params:
            # ID lookup fails
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    result = query_omdb("Movie", "2020")
    assert result is None


# Test fuzzy search with year matching
@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_fuzzy_year_match(mock_get, mock_key):
    """Test fuzzy search year matching logic."""

    def side_effect(*args, **kwargs):
        params = kwargs.get("params", {})
        if "t" in params:
            # Direct search fails
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        elif "s" in params:
            # Search returns multiple results with different years
            return type(
                "resp",
                (),
                {
                    "status_code": 200,
                    "json": (
                        lambda *a, **k: {
                            "Response": "True",
                            "Search": [
                                {"Title": "Movie", "Year": "2019", "imdbID": "tt119"},
                                {"Title": "Movie", "Year": "2020", "imdbID": "tt120"},
                                {"Title": "Movie", "Year": "2021", "imdbID": "tt121"},
                            ],
                        }
                    ),
                },
            )()
        elif "i" in params:
            # ID lookup
            params_i = params.get("i", "")
            if "120" in params_i:
                return type(
                    "resp",
                    (),
                    {
                        "status_code": 200,
                        "json": (
                            lambda *a, **k: {
                                "Response": "True",
                                "Title": "Movie",
                                "Year": "2020",
                                "imdbID": "tt120",
                            }
                        ),
                    },
                )()
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: {"Response": "False"})},
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    result = query_omdb("Movie", "2020")
    # Should prefer year match
    assert result is not None
    assert result["Year"] == "2020"
