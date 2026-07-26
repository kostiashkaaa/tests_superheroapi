import re

import requests

API_URL = "https://akabab.github.io/superhero-api/api/all.json"


def parse_height_cm(height):
    # height это список типа ["6'8", "203 cm"], если рост неизвестен - ["-", "-"]
    if not height:
        return None

    for value in height:
        if not value:
            continue
        match = re.search(r"(\d+(?:\.\d+)?)\s*cm", value, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def has_job(occupation):
    if occupation is None:
        return False
    occupation = occupation.strip()
    return occupation not in ("", "-")


def find_tallest_hero(heroes, gender, employed):
    if not heroes:
        return None

    gender = gender.strip().lower()
    best = None
    tallest = -1

    for hero in heroes:
        appearance = hero.get("appearance") or {}
        work = hero.get("work") or {}

        hero_gender = (appearance.get("gender") or "").strip().lower()
        if hero_gender != gender:
            continue

        if has_job(work.get("occupation")) != employed:
            continue

        height_cm = parse_height_cm(appearance.get("height"))
        if height_cm is None:
            continue

        if height_cm > tallest:
            tallest = height_cm
            best = hero

    return best


def fetch_heroes(api_url=API_URL):
    response = requests.get(api_url, timeout=10)  # таймаут, чтобы не зависнуть если сайт не отвечает
    response.raise_for_status()
    return response.json()


def get_tallest_hero(gender, employed, api_url=API_URL):
    heroes = fetch_heroes(api_url)
    return find_tallest_hero(heroes, gender, employed)


if __name__ == "__main__":
    hero = get_tallest_hero(gender="Male", employed=True)
    if hero:
        print(hero["name"], hero["appearance"]["height"][1])
    else:
        print("hero not found")
