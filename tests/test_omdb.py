from unittest.mock import patch
from video_sweep.omdb import query_omdb, get_suggested_name

# Mock OMDb responses for testing
MOCK_MOVIE = {"Title": "Waterworld", "Year": "1995", "Response": "True"}
MOCK_MOVIE_SUGGEST = {
    "Title": "Vicky Cristina Barcelona",
    "Year": "2008",
    "Response": "True",
}
MOCK_NOT_FOUND = {"Response": "False"}


@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_direct_match(mock_get, mock_key):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_MOVIE
    result = query_omdb("Waterworld", "1995")
    assert result["Title"] == "Waterworld"
    assert result["Year"] == "1995"


@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_fuzzy_match(mock_get, mock_key):
    # First call: direct fails, second: search returns list, third: id lookup
    def side_effect(*args, **kwargs):
        url = args[0]
        if "t=" in url or kwargs.get("params", {}).get("t"):
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: MOCK_NOT_FOUND)},
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
                            "Search": [
                                {
                                    "Title": "Vicky Cristina Barcelona",
                                    "Year": "2008",
                                    "imdbID": "tt0497465",
                                }
                            ],
                        }
                    ),
                },
            )()
        elif "i=" in url or kwargs.get("params", {}).get("i"):
            return type(
                "resp",
                (),
                {"status_code": 200, "json": (lambda *a, **k: MOCK_MOVIE_SUGGEST)},
            )()
        return type("resp", (), {"status_code": 404, "json": (lambda *a, **k: {})})()

    mock_get.side_effect = side_effect
    result = query_omdb("Vicky Cristina Barcelonaz", "2008")
    assert result["Title"] == "Vicky Cristina Barcelona"
    assert result["Year"] == "2008"


@patch("video_sweep.omdb.get_api_key_from_config", return_value="dummykey")
@patch("video_sweep.omdb.requests.get")
def test_query_omdb_no_match(mock_get, mock_key):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_NOT_FOUND
    result = query_omdb("Nonexistent Movie", "2020")
    assert result is None


def test_get_suggested_name():
    data = {"Title": "Waterworld", "Year": "1995"}
    assert get_suggested_name(data) == "Waterworld (1995)"
    assert get_suggested_name({}) is None
    assert get_suggested_name(None) is None
