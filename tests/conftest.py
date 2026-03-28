import json
import os
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_JSON_PATH = os.path.join(ROOT_DIR, "v4.json")
EXPANSIONS_JSON_PATH = os.path.join(ROOT_DIR, "expansions.json")
CARDS_DIR = os.path.join(ROOT_DIR, "images", "cards")
PACKS_DIR = os.path.join(ROOT_DIR, "images", "packs")


@pytest.fixture(scope="session")
def cards():
    with open(V4_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def expansions():
    with open(EXPANSIONS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
