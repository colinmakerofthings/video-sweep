from video_sweep import omdb


def test_get_api_key_from_config_success(tmp_path, monkeypatch):
    # Write a config.toml with an API key
    config_path = tmp_path / "config.toml"
    config_path.write_text('[omdb]\napi_key = "abc123"\n')
    monkeypatch.setattr(omdb, "__file__", str(tmp_path / "fake.py"))
    monkeypatch.setattr(omdb.os.path, "abspath", lambda x: str(config_path))
    monkeypatch.setattr(omdb.os.path, "join", lambda *a: str(config_path))
    import importlib

    importlib.reload(omdb)
    assert omdb.get_api_key_from_config() == "abc123"


def test_get_api_key_from_config_missing(monkeypatch):
    monkeypatch.setattr(omdb.toml, "load", lambda path: {})
    assert omdb.get_api_key_from_config() is None


def test_query_omdb_no_api_key(monkeypatch):
    monkeypatch.setattr(omdb, "get_api_key_from_config", lambda: None)
    assert omdb.query_omdb("title") is None


def test_get_suggested_name_none():
    assert omdb.get_suggested_name(None) is None
    assert omdb.get_suggested_name({}) is None


def test_get_suggested_name_valid():
    data = {"Title": "Test Movie", "Year": "2020"}
    assert omdb.get_suggested_name(data) == "Test Movie (2020)"
