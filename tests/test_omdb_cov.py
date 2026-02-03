import pytest
from unittest.mock import patch
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
