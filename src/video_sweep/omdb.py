import os
import requests
import toml


def get_api_key_from_config():
    # Check environment variable first
    env_key = os.environ.get("OMDB_API_KEY")
    if env_key:
        return env_key
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "config.toml"
    )
    config_path = os.path.abspath(config_path)
    try:
        config = toml.load(config_path)
        return config.get("omdb", {}).get("api_key")
    except Exception:
        return None


def query_omdb(title, year=None):
    """
    Query OMDb API for a movie by title and optional year.
    Returns dict with OMDb result or None if not found or no API key.
    """
    api_key = get_api_key_from_config()
    if not api_key:
        return None
    params = {"t": title, "apikey": api_key}
    if year:
        params["y"] = str(year)
    response = requests.get("http://www.omdbapi.com/", params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return data

    # Fallback: use OMDb search endpoint and fuzzy match
    from difflib import SequenceMatcher

    def fuzzy_search(search_title, intended_title, intended_year=None):
        search_params = {"s": search_title, "apikey": api_key}
        search_response = requests.get("http://www.omdbapi.com/", params=search_params)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get("Response") == "True" and "Search" in search_data:
                best_match = None
                best_score = 0.0
                for item in search_data["Search"]:
                    candidate_title = item.get("Title", "")
                    candidate_year = item.get("Year", "")
                    ratio = SequenceMatcher(
                        None, candidate_title.lower(), intended_title.lower()
                    ).ratio()
                    if intended_year:
                        if candidate_year == str(intended_year):
                            score = ratio + 0.2
                        else:
                            score = ratio - 0.2
                    else:
                        score = ratio
                    if score > best_score:
                        best_match = item
                        best_score = score
                threshold = 0.8 if intended_year else 0.9
                if best_match and best_score >= threshold:
                    imdb_id = best_match.get("imdbID")
                    if imdb_id:
                        id_params = {"i": imdb_id, "apikey": api_key}
                        id_response = requests.get(
                            "http://www.omdbapi.com/", params=id_params
                        )
                        if id_response.status_code == 200:
                            id_data = id_response.json()
                            if id_data.get("Response") == "True":
                                return id_data
        return None

    # First try with full title
    result = fuzzy_search(title, title, year)
    if result:
        return result
    # Try with simplified title (alphabetic words only)
    import re

    words = re.findall(r"[A-Za-z]+", title)
    if words:
        simplified_title = " ".join(words)
        if simplified_title != title:
            result = fuzzy_search(simplified_title, simplified_title, year)
            if result:
                return result
        # Try with progressively shorter substrings
        for i in range(len(words) - 1, 1, -1):
            short_title = " ".join(words[:i])
            result = fuzzy_search(short_title, short_title, year)
            if result:
                return result
    return None


def get_suggested_name(omdb_data):
    """
    Return suggested filename from OMDb data (Title (Year)).
    """
    if not omdb_data:
        return None
    title = omdb_data.get("Title")
    year = omdb_data.get("Year")
    if title and year:
        return f"{title} ({year})"
    return None
