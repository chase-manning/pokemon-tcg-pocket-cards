import os
import re

import pytest

from .conftest import CARDS_DIR

REQUIRED_FIELDS = ["id", "name", "rarity", "pack", "health", "image", "fullart", "ex", "artist", "type"]

VALID_TYPES = {
    "Grass", "Fire", "Water", "Lightning", "Psychic",
    "Fighting", "Darkness", "Metal", "Dragon", "Colorless", "Fairy",
    "Trainer",
}

VALID_RARITIES = {"◊", "◊◊", "◊◊◊", "◊◊◊◊", "☆", "☆☆", "☆☆☆", "♕", "Promo"}

FULLART_RARITIES = {"☆", "☆☆", "☆☆☆", "♕"}

IMAGE_URL_PREFIX = (
    "https://raw.githubusercontent.com/chase-manning/"
    "pokemon-tcg-pocket-cards/refs/heads/main/images/cards/"
)

ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*-\d{1,3}$")

FOSSIL_NAMES = {"Helix Fossil", "Dome Fossil", "Old Amber", "Jaw Fossil", "Sail Fossil"}


class TestV4Structure:
    def test_is_non_empty_list(self, cards):
        assert isinstance(cards, list)
        assert len(cards) > 0

    def test_all_entries_are_dicts(self, cards):
        for i, card in enumerate(cards):
            assert isinstance(card, dict), f"Entry {i} is not a dict"


class TestCardFields:
    def test_all_required_fields_present(self, cards):
        for card in cards:
            for field in REQUIRED_FIELDS:
                assert field in card, f"Card {card.get('id', '?')} missing field '{field}'"

    def test_no_extra_fields(self, cards):
        expected = set(REQUIRED_FIELDS)
        for card in cards:
            extra = set(card.keys()) - expected
            assert not extra, f"Card {card['id']} has unexpected fields: {extra}"

    def test_no_none_values(self, cards):
        for card in cards:
            for field in REQUIRED_FIELDS:
                assert card[field] is not None, f"Card {card['id']} has None for '{field}'"

    def test_all_values_are_strings(self, cards):
        for card in cards:
            for field in REQUIRED_FIELDS:
                assert isinstance(card[field], str), (
                    f"Card {card['id']} field '{field}' is {type(card[field]).__name__}, expected str"
                )


class TestCardId:
    def test_id_format(self, cards):
        for card in cards:
            assert ID_PATTERN.match(card["id"]), (
                f"Card ID '{card['id']}' doesn't match expected format (e.g. 'a1-001')"
            )

    def test_no_duplicate_ids(self, cards):
        ids = [card["id"] for card in cards]
        seen = set()
        duplicates = []
        for card_id in ids:
            if card_id in seen:
                duplicates.append(card_id)
            seen.add(card_id)
        assert not duplicates, f"Duplicate card IDs found: {duplicates}"

    def test_ids_are_sorted_within_expansion(self, cards):
        """Cards from the same expansion should appear in numerical order."""
        from collections import defaultdict

        by_prefix = defaultdict(list)
        for card in cards:
            prefix = card["id"].rsplit("-", 1)[0]
            number = int(card["id"].rsplit("-", 1)[1])
            by_prefix[prefix].append(number)

        for prefix, numbers in by_prefix.items():
            assert numbers == sorted(numbers), (
                f"Cards with prefix '{prefix}' are not in sorted order"
            )


class TestCardName:
    def test_name_not_empty(self, cards):
        for card in cards:
            assert card["name"].strip(), f"Card {card['id']} has empty name"

    def test_name_reasonable_length(self, cards):
        for card in cards:
            assert len(card["name"]) <= 60, (
                f"Card {card['id']} name is suspiciously long: '{card['name']}'"
            )
            assert len(card["name"]) >= 2, (
                f"Card {card['id']} name is suspiciously short: '{card['name']}'"
            )

    def test_name_no_html_tags(self, cards):
        for card in cards:
            assert "<" not in card["name"] and ">" not in card["name"], (
                f"Card {card['id']} name contains HTML: '{card['name']}'"
            )


class TestCardRarity:
    def test_rarity_is_valid(self, cards):
        for card in cards:
            assert card["rarity"] in VALID_RARITIES, (
                f"Card {card['id']} has invalid rarity: '{card['rarity']}'"
            )

    def test_promo_rarity_only_on_promo_cards(self, cards):
        for card in cards:
            if card["rarity"] == "Promo":
                prefix = card["id"].rsplit("-", 1)[0]
                assert prefix.startswith("p"), (
                    f"Card {card['id']} has Promo rarity but is not a promo card"
                )


class TestCardType:
    def test_type_is_valid(self, cards):
        for card in cards:
            assert card["type"] in VALID_TYPES, (
                f"Card {card['id']} has invalid type: '{card['type']}'"
            )


class TestCardHealth:
    def test_pokemon_have_numeric_health(self, cards):
        for card in cards:
            if card["type"] != "Trainer":
                assert card["health"].isdigit(), (
                    f"Pokemon card {card['id']} ({card['name']}) has non-numeric health: '{card['health']}'"
                )

    def test_health_in_reasonable_range(self, cards):
        for card in cards:
            if card["health"] and card["health"].isdigit():
                hp = int(card["health"])
                assert 10 <= hp <= 400, (
                    f"Card {card['id']} has health {hp} outside reasonable range"
                )

    def test_trainer_health_empty_unless_fossil(self, cards):
        """Trainers should have empty health, except fossils which have HP."""
        for card in cards:
            if card["type"] == "Trainer" and card["health"] != "":
                assert card["name"] in FOSSIL_NAMES, (
                    f"Trainer card {card['id']} ({card['name']}) has health '{card['health']}' "
                    f"but is not a known fossil card"
                )


class TestCardImage:
    def test_image_url_format(self, cards):
        for card in cards:
            expected = f"{IMAGE_URL_PREFIX}{card['id']}.png"
            assert card["image"] == expected, (
                f"Card {card['id']} image URL doesn't match expected format.\n"
                f"  Expected: {expected}\n"
                f"  Got:      {card['image']}"
            )

    def test_image_file_exists(self, cards):
        missing = []
        for card in cards:
            path = os.path.join(CARDS_DIR, f"{card['id']}.png")
            if not os.path.exists(path):
                missing.append(card["id"])
        assert not missing, (
            f"{len(missing)} card images missing locally: {missing[:20]}"
        )


class TestCardFlags:
    def test_fullart_is_yes_or_no(self, cards):
        for card in cards:
            assert card["fullart"] in ("Yes", "No"), (
                f"Card {card['id']} has invalid fullart value: '{card['fullart']}'"
            )

    def test_ex_is_yes_or_no(self, cards):
        for card in cards:
            assert card["ex"] in ("Yes", "No"), (
                f"Card {card['id']} has invalid ex value: '{card['ex']}'"
            )

    def test_ex_flag_matches_name(self, cards):
        """If ex='Yes', the name should contain 'ex' as a word."""
        for card in cards:
            has_ex_in_name = "ex" in card["name"].split(" ")
            if card["ex"] == "Yes":
                assert has_ex_in_name, (
                    f"Card {card['id']} has ex='Yes' but name '{card['name']}' doesn't contain 'ex'"
                )
            if has_ex_in_name:
                assert card["ex"] == "Yes", (
                    f"Card {card['id']} name '{card['name']}' contains 'ex' but ex='{card['ex']}'"
                )

    def test_fullart_matches_rarity(self, cards):
        """Fullart cards should have a fullart rarity (star/crown), except promos."""
        for card in cards:
            if card["rarity"] == "Promo":
                continue
            if card["fullart"] == "Yes":
                assert card["rarity"] in FULLART_RARITIES, (
                    f"Card {card['id']} is fullart but has rarity '{card['rarity']}'"
                )
            if card["rarity"] in FULLART_RARITIES:
                assert card["fullart"] == "Yes", (
                    f"Card {card['id']} has fullart rarity '{card['rarity']}' but fullart='No'"
                )


class TestCardPack:
    def test_pack_not_empty(self, cards):
        for card in cards:
            assert card["pack"].strip(), f"Card {card['id']} has empty pack"

    def test_pack_not_error(self, cards):
        errors = [c for c in cards if c["pack"] == "Error"]
        assert not errors, (
            f"{len(errors)} card(s) have pack='Error': "
            + ", ".join(f"{c['id']} ({c['name']})" for c in errors)
        )


class TestCardArtist:
    def test_artist_not_empty(self, cards):
        for card in cards:
            assert card["artist"].strip(), f"Card {card['id']} has empty artist"

    def test_artist_not_unknown(self, cards):
        unknowns = [c for c in cards if c["artist"] == "Unknown"]
        assert not unknowns, (
            f"{len(unknowns)} card(s) have artist='Unknown': "
            + ", ".join(f"{c['id']} ({c['name']})" for c in unknowns[:20])
        )

    def test_artist_reasonable_length(self, cards):
        for card in cards:
            assert len(card["artist"]) <= 80, (
                f"Card {card['id']} artist is suspiciously long: '{card['artist']}'"
            )
