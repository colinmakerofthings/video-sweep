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
        (":<>|?*", ""),  # Only special chars
        ("Normal-Movie.Name", "Normal-Movie.Name"),  # Dashes and dots preserved
        ('Quote"Test', "QuoteTest"),  # Double quote removed
        ("Slash/Test", "SlashTest"),  # Forward slash removed
        ("Unicode_ñame", "Unicode_ñame"),  # Unicode preserved
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
        ("2012 (2009).mp4", "2012 [2009].mp4"),  # Year in parentheses
        ("1984.mkv", "1984.mkv"),  # Title starts with year
        ("The.Movie.2021.BluRay.mp4", "The Movie [2021].mp4"),
        ("Movie.2020.2021.avi", "Movie [2020].avi"),  # Multiple years - uses first
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
        ("Show s04e01.mkv", ("Show", 4, "S04E01", "Show S04E01.mkv")),  # Lowercase
        ("S01E01.mkv", ("", 1, "S01E01", " S01E01.mkv")),  # No series name
        (
            "Series-Name S02E03.mkv",
            ("Series Name", 2, "S02E03", "Series Name S02E03.mkv"),
        ),  # Dashes replaced
        (
            "Series.Name S02E03.mkv",
            ("Series Name", 2, "S02E03", "Series Name S02E03.mkv"),
        ),  # Dots replaced
        (
            "Show (2020) s10e05.mkv",
            ("Show", 10, "S10E05", "Show S10E05.mkv"),
        ),  # Year removed, lowercase
        (
            "Multiple Numbers S02E05 2023.mkv",
            ("Multiple Numbers", 2, "S02E05", "Multiple Numbers S02E05.mkv"),
        ),
    ],
)
def test_series_new_filename(filename, expected):
    assert series_new_filename(filename) == expected


def create_omdb_mock(title=None, year=None):
    """Create a reusable OMDb mock function."""

    def mock_func(*args, **kwargs):
        data = {}
        if title:
            data["Title"] = title
        if year:
            data["Year"] = year
        return data if data else None

    return mock_func


@pytest.mark.parametrize(
    "title,year,current,expected_valid",
    [
        ("Movie", "2022", "other", False),  # Query fails (returns None)
        ("Movie", "2022", "Movie", False),  # No year in current name
    ],
)
def test_validate_movie_name_no_omdb_data(title, year, current, expected_valid):
    with patch("video_sweep.renamer.query_omdb", return_value=None):
        result, suggested = validate_movie_name(title, year, current)
        assert result == expected_valid
        assert suggested is None


def test_validate_movie_name_with_omdb_match():
    """Test validate_movie_name when OMDb data matches."""

    def mock_query(*args, **kwargs):
        return {"Title": "The Matrix", "Year": "1999", "imdbID": "tt0133093"}

    def mock_suggested(data):
        return "The Matrix (1999)"

    with patch("video_sweep.renamer.query_omdb", side_effect=mock_query):
        with patch(
            "video_sweep.renamer.get_suggested_name", side_effect=mock_suggested
        ):
            # Note: validate_movie_name compares normalized names. The input name is without extension
            result, suggested = validate_movie_name(
                "The Matrix", "1999", "The Matrix [1999]"
            )
            # After normalization, both should match
            assert result is True
            assert suggested is None  # When correct, no suggestion given


def test_validate_movie_name_with_omdb_mismatch():
    """Test validate_movie_name when OMDb data doesn't match."""

    def mock_query(*args, **kwargs):
        return {"Title": "The Matrix", "Year": "1999", "imdbID": "tt0133093"}

    def mock_suggested(data):
        return "The Matrix (1999)"

    with patch("video_sweep.renamer.query_omdb", side_effect=mock_query):
        with patch(
            "video_sweep.renamer.get_suggested_name", side_effect=mock_suggested
        ):
            result, suggested = validate_movie_name(
                "Wrong Title", "1999", "Wrong Title [1999].mp4"
            )
            assert result is False
            assert suggested == "The Matrix [1999]"


def test_validate_movie_name_missing_title_field():
    """Test validate_movie_name when OMDb response is missing Title."""

    def mock_query(*args, **kwargs):
        return {"Year": "1999"}  # Missing Title

    with patch("video_sweep.renamer.query_omdb", side_effect=mock_query):
        with patch("video_sweep.renamer.get_suggested_name", return_value=None):
            result, suggested = validate_movie_name(
                "Some Movie", "1999", "Some Movie [1999]"
            )
            # When suggested is None, result should be False or None depending on logic
            assert result in (False, None)


def test_validate_movie_name_missing_year_field():
    """Test validate_movie_name when OMDb response is missing Year."""

    def mock_query(*args, **kwargs):
        return {"Title": "The Matrix"}  # Missing Year

    with patch("video_sweep.renamer.query_omdb", side_effect=mock_query):
        with patch("video_sweep.renamer.get_suggested_name", return_value="The Matrix"):
            result, suggested = validate_movie_name(
                "The Matrix", "1999", "The Matrix [1999].mp4"
            )
            # Should still process, just without year in OMDb response
            assert result is False  # Won't match without year
