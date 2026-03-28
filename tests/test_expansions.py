import os
import re

import pytest

from .conftest import PACKS_DIR

IMAGE_URL_PREFIX = (
    "https://raw.githubusercontent.com/chase-manning/"
    "pokemon-tcg-pocket-cards/refs/heads/main/images/packs/"
)

EXPANSION_REQUIRED_FIELDS = ["id", "name", "packs"]
PACK_REQUIRED_FIELDS = ["id", "name", "image"]

EXPANSION_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*$")


class TestExpansionsStructure:
    def test_is_non_empty_list(self, expansions):
        assert isinstance(expansions, list)
        assert len(expansions) > 0

    def test_all_entries_are_dicts(self, expansions):
        for i, exp in enumerate(expansions):
            assert isinstance(exp, dict), f"Entry {i} is not a dict"


class TestExpansionFields:
    def test_all_required_fields_present(self, expansions):
        for exp in expansions:
            for field in EXPANSION_REQUIRED_FIELDS:
                assert field in exp, f"Expansion {exp.get('id', '?')} missing field '{field}'"

    def test_no_extra_fields(self, expansions):
        expected = set(EXPANSION_REQUIRED_FIELDS)
        for exp in expansions:
            extra = set(exp.keys()) - expected
            assert not extra, f"Expansion {exp['id']} has unexpected fields: {extra}"


class TestExpansionId:
    def test_id_format(self, expansions):
        for exp in expansions:
            assert EXPANSION_ID_PATTERN.match(exp["id"]), (
                f"Expansion ID '{exp['id']}' doesn't match expected format"
            )

    def test_no_duplicate_ids(self, expansions):
        ids = [exp["id"] for exp in expansions]
        seen = set()
        duplicates = []
        for eid in ids:
            if eid in seen:
                duplicates.append(eid)
            seen.add(eid)
        assert not duplicates, f"Duplicate expansion IDs: {duplicates}"


class TestExpansionName:
    def test_name_not_empty(self, expansions):
        for exp in expansions:
            assert exp["name"].strip(), f"Expansion {exp['id']} has empty name"

    def test_name_is_string(self, expansions):
        for exp in expansions:
            assert isinstance(exp["name"], str), (
                f"Expansion {exp['id']} name is not a string"
            )

    def test_name_reasonable_length(self, expansions):
        for exp in expansions:
            assert 2 <= len(exp["name"]) <= 60, (
                f"Expansion {exp['id']} name has unusual length: '{exp['name']}'"
            )


class TestExpansionPacks:
    def test_packs_is_non_empty_list(self, expansions):
        for exp in expansions:
            assert isinstance(exp["packs"], list), (
                f"Expansion {exp['id']} packs is not a list"
            )
            assert len(exp["packs"]) > 0, (
                f"Expansion {exp['id']} has no packs"
            )

    def test_pack_has_required_fields(self, expansions):
        for exp in expansions:
            for pack in exp["packs"]:
                for field in PACK_REQUIRED_FIELDS:
                    assert field in pack, (
                        f"Pack in expansion {exp['id']} missing field '{field}'"
                    )

    def test_pack_no_extra_fields(self, expansions):
        expected = set(PACK_REQUIRED_FIELDS)
        for exp in expansions:
            for pack in exp["packs"]:
                extra = set(pack.keys()) - expected
                assert not extra, (
                    f"Pack {pack['id']} has unexpected fields: {extra}"
                )

    def test_pack_id_starts_with_expansion_id(self, expansions):
        for exp in expansions:
            for pack in exp["packs"]:
                assert pack["id"].startswith(exp["id"]), (
                    f"Pack '{pack['id']}' doesn't start with expansion ID '{exp['id']}'"
                )

    def test_no_duplicate_pack_ids(self, expansions):
        all_ids = []
        for exp in expansions:
            for pack in exp["packs"]:
                all_ids.append(pack["id"])
        seen = set()
        duplicates = []
        for pid in all_ids:
            if pid in seen:
                duplicates.append(pid)
            seen.add(pid)
        assert not duplicates, f"Duplicate pack IDs: {duplicates}"

    def test_pack_name_not_empty(self, expansions):
        for exp in expansions:
            for pack in exp["packs"]:
                assert pack["name"].strip(), (
                    f"Pack {pack['id']} has empty name"
                )

    def test_pack_values_are_strings(self, expansions):
        for exp in expansions:
            for pack in exp["packs"]:
                for field in PACK_REQUIRED_FIELDS:
                    assert isinstance(pack[field], str), (
                        f"Pack {pack['id']} field '{field}' is not a string"
                    )


class TestPackImages:
    def test_pack_image_url_format(self, expansions):
        for exp in expansions:
            for pack in exp["packs"]:
                assert pack["image"].startswith(IMAGE_URL_PREFIX), (
                    f"Pack {pack['id']} image URL doesn't start with expected prefix.\n"
                    f"  Got: {pack['image']}"
                )

    def test_pack_image_url_matches_id(self, expansions):
        for exp in expansions:
            for pack in exp["packs"]:
                filename = pack["image"].split("/")[-1]
                name_without_ext = filename.rsplit(".", 1)[0]
                assert name_without_ext == pack["id"], (
                    f"Pack {pack['id']} image filename '{filename}' "
                    f"doesn't match pack ID"
                )

    def test_pack_image_file_exists(self, expansions):
        missing = []
        for exp in expansions:
            for pack in exp["packs"]:
                filename = pack["image"].split("/")[-1]
                path = os.path.join(PACKS_DIR, filename)
                if not os.path.exists(path):
                    missing.append(pack["id"])
        assert not missing, f"Missing pack image files: {missing}"
