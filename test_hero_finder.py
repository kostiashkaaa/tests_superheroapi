from unittest.mock import Mock, patch

import pytest
import requests

from hero_finder import (
    get_tallest_hero,
    find_tallest_hero,
    fetch_heroes,
    parse_height_cm,
    has_job,
    API_URL,
)


def make_hero(name, gender, height, occupation):
    return {
        "name": name,
        "appearance": {"gender": gender, "height": height},
        "work": {"occupation": occupation},
    }


def make_mock_response(json_data):
    resp = Mock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.fixture
def heroes_sample():
    return [
        make_hero("Bob", "Male", ["5'9", "175 cm"], "Engineer"),
        make_hero("Rex", "male", ["6'8", "203 cm"], "Adventurer"),  # разный регистр gender
        make_hero("Max", "Male", ["7'0", "213 cm"], "-"),  # выше всех, но без работы
        make_hero("Ann", "Female", ["5'2", "157 cm"], "Doctor"),
        make_hero("Ivy", "Female", ["6'1", "185 cm"], "-"),
        make_hero("Tom", "Male", ["-", "-"], "Pilot"),  # рост неизвестен
        make_hero("Nora", "-", ["6'0", "182 cm"], "-"),
    ]


def test_parse_height_normal():
    assert parse_height_cm(["6'8", "203 cm"]) == 203.0


def test_parse_height_decimal():
    assert parse_height_cm(["5'11", "180.5 cm"]) == 180.5


def test_parse_height_case_insensitive():
    assert parse_height_cm(["6'8", "203 CM"]) == 203.0


def test_parse_height_unknown():
    assert parse_height_cm(["-", "-"]) is None


def test_parse_height_none():
    assert parse_height_cm(None) is None


def test_parse_height_empty_list():
    assert parse_height_cm([]) is None


def test_parse_height_missing_metric():
    assert parse_height_cm(["6'8"]) is None


def test_parse_height_empty_strings():
    assert parse_height_cm(["", ""]) is None


def test_has_job_dash():
    assert has_job("-") is False


def test_has_job_empty_string():
    assert has_job("") is False


def test_has_job_none():
    assert has_job(None) is False


def test_has_job_whitespace():
    assert has_job("   ") is False


def test_has_job_dash_padded():
    assert has_job("  -  ") is False


def test_has_job_with_occupation():
    assert has_job("Businessman") is True


def test_has_job_long_occupation():
    assert has_job("Musician, adventurer, author; formerly talk show host") is True


def test_find_tallest_empty_list():
    assert find_tallest_hero([], gender="Male", employed=True) is None


def test_find_tallest_male_with_job(heroes_sample):
    hero = find_tallest_hero(heroes_sample, gender="Male", employed=True)
    assert hero["name"] == "Rex"


def test_find_tallest_male_without_job(heroes_sample):
    hero = find_tallest_hero(heroes_sample, gender="Male", employed=False)
    assert hero["name"] == "Max"


def test_find_tallest_female_with_job(heroes_sample):
    hero = find_tallest_hero(heroes_sample, gender="Female", employed=True)
    assert hero["name"] == "Ann"


def test_find_tallest_female_without_job(heroes_sample):
    hero = find_tallest_hero(heroes_sample, gender="Female", employed=False)
    assert hero["name"] == "Ivy"


def test_gender_case_insensitive(heroes_sample):
    hero = find_tallest_hero(heroes_sample, gender="MALE", employed=True)
    assert hero["name"] == "Rex"


def test_find_tallest_no_match(heroes_sample):
    assert find_tallest_hero(heroes_sample, gender="Alien", employed=True) is None


def test_unknown_height_is_skipped(heroes_sample):
    hero = find_tallest_hero(heroes_sample, gender="Male", employed=True)
    assert hero["name"] != "Tom"


def test_find_tallest_tie_returns_first():
    heroes = [
        make_hero("First Tall", "Male", ["6'0", "200 cm"], "Pilot"),
        make_hero("Second Tall", "Male", ["6'0", "200 cm"], "Pilot"),
    ]
    hero = find_tallest_hero(heroes, gender="Male", employed=True)
    assert hero["name"] == "First Tall"


def test_find_tallest_single_hero():
    heroes = [make_hero("Only One", "Female", ["5'5", "165 cm"], "Teacher")]
    hero = find_tallest_hero(heroes, gender="Female", employed=True)
    assert hero["name"] == "Only One"


def test_missing_appearance_key():
    heroes = [
        {"name": "Broken Hero", "work": {"occupation": "Pilot"}},
        make_hero("Normal Hero", "Male", ["6'0", "182 cm"], "Pilot"),
    ]
    hero = find_tallest_hero(heroes, gender="Male", employed=True)
    assert hero["name"] == "Normal Hero"


def test_missing_work_key():
    heroes = [
        {"name": "No Work Field", "appearance": {"gender": "Male", "height": ["6'5", "195 cm"]}},
        make_hero("Normal Hero", "Male", ["6'0", "182 cm"], "Pilot"),
    ]
    hero = find_tallest_hero(heroes, gender="Male", employed=True)
    assert hero["name"] == "Normal Hero"


@patch("hero_finder.requests.get")
def test_fetch_heroes_returns_json(mock_get):
    expected = [make_hero("Mock Hero", "Male", ["6'0", "182 cm"], "Pilot")]
    mock_get.return_value = make_mock_response(expected)

    result = fetch_heroes()

    assert result == expected
    mock_get.assert_called_once_with(API_URL, timeout=10)


@patch("hero_finder.requests.get")
def test_fetch_heroes_custom_url(mock_get):
    mock_get.return_value = make_mock_response([])

    fetch_heroes(api_url="https://example.com/custom.json")

    mock_get.assert_called_once_with("https://example.com/custom.json", timeout=10)


@patch("hero_finder.requests.get")
def test_fetch_heroes_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 error")
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        fetch_heroes()


@patch("hero_finder.requests.get")
def test_fetch_heroes_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("network down")

    with pytest.raises(requests.ConnectionError):
        fetch_heroes()


@patch("hero_finder.requests.get")
def test_get_tallest_hero_end_to_end(mock_get):
    heroes = [
        make_hero("Short Employed Man", "Male", ["5'5", "165 cm"], "Clerk"),
        make_hero("Tall Employed Man", "Male", ["6'9", "205 cm"], "Detective"),
        make_hero("Tall Unemployed Man", "Male", ["7'2", "218 cm"], "-"),
    ]
    mock_get.return_value = make_mock_response(heroes)

    hero = get_tallest_hero(gender="Male", employed=True)

    assert hero["name"] == "Tall Employed Man"


@patch("hero_finder.requests.get")
def test_get_tallest_hero_no_match(mock_get):
    heroes = [make_hero("Solo Hero", "Female", ["5'5", "165 cm"], "-")]
    mock_get.return_value = make_mock_response(heroes)

    hero = get_tallest_hero(gender="Male", employed=True)

    assert hero is None


@patch("hero_finder.requests.get")
def test_get_tallest_hero_network_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("network down")

    with pytest.raises(requests.ConnectionError):
        get_tallest_hero(gender="Male", employed=True)
