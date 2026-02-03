from video_sweep.omdb import get_api_key_from_config, get_suggested_name


def test_get_api_key_from_config_env(monkeypatch):
    monkeypatch.setenv("OMDB_API_KEY", "testkey")
    assert get_api_key_from_config() == "testkey"


def test_get_api_key_from_config_none(monkeypatch):
    monkeypatch.delenv("OMDB_API_KEY", raising=False)
    assert get_api_key_from_config() == "4645ab2e"


def test_get_suggested_name_valid():
    data = {"Title": "Test Movie", "Year": "2020"}
    assert get_suggested_name(data) == "Test Movie (2020)"


def test_get_suggested_name_none():
    assert get_suggested_name(None) is None
    assert get_suggested_name({}) is None
