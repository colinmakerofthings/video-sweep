import pytest
from unittest.mock import patch
from video_sweep.renamer import (
    sanitize_filename,
    movie_new_filename,
    series_new_filename,
    validate_movie_name,
)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Movie: The Test?", "Movie The Test"),
        ("A<Bad>|Name*", "ABadName"),
        ("Good.Name-2023", "Good.Name-2023"),
    ],
)
def test_sanitize_filename(name, expected):
    assert sanitize_filename(name) == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("TestMovie.2022.mp4", "TestMovie [2022].mp4"),
        ("2022TestMovie.mp4", "2022.mp4"),
        ("NoYearHere.mp4", None),
    ],
)
def test_movie_new_filename(filename, expected):
    assert movie_new_filename(filename) == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        (
            "SeriesName (2014) - S04E01 - Other text.mkv",
            ("SeriesName", 4, "S04E01", "SeriesName S04E01.mkv"),
        ),
        ("Show SXXEYY.mkv", None),
    ],
)
def test_series_new_filename(filename, expected):
    assert series_new_filename(filename) == expected


@pytest.mark.parametrize(
    "title,year,current,expected",
    [
        ("Movie", "2022", "Movie [2022].mp4", True),
        ("Movie", "2022", "Other [2022].mp4", False),
        ("Movie", "2022", "Movie.mp4", False),
    ],
)
def omdb_mock(title, year):
    return {"Title": title, "Year": year}


@pytest.mark.parametrize(
    "title,year,current,expected",
    [
        ("Movie", "2022", "Other [2022].mp4", False),
        ("Movie", "2022", "Movie.mp4", False),
    ],
)
def test_validate_movie_name(title, year, current, expected):
    with patch("video_sweep.renamer.query_omdb", side_effect=omdb_mock):
        result, _ = validate_movie_name(title, year, current)
        assert result == expected
