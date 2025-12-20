#!/usr/bin/env python3
"""
Script to update pack names for cards in v4.json using the same logic
as transpose-format.py's fetch_pack_name function.
"""

import json
import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
BASE_URL = "https://pocket.limitlesstcg.com/cards/"
V4_JSON_PATH = Path(__file__).parent / "v4.json"
PROGRESS_LOG_PATH = Path(__file__).parent / "update_pack_names_progress.txt"
TEST_MODE = False  # Set to False to process all cards
TEST_LIMIT = 50  # Number of cards to process in test mode
START_INDEX = 0  # Start from this index (useful for resuming after a failure)

# Series mapping from transpose-format.py
series_map = {
    "a1": {"endpoint": "A1?pack=0", "PacksNumber": 3},
    "a1a": {"endpoint": "A1a", "PacksNumber": 1},
    "a2": {"endpoint": "A2?pack=0", "PacksNumber": 2},
    "a2a": {"endpoint": "A2a", "PacksNumber": 1},
    "a2b": {"endpoint": "A2b", "PacksNumber": 1},
    "a3": {"endpoint": "A3?pack=0", "PacksNumber": 2},
    "a3a": {"endpoint": "A3a", "PacksNumber": 1},
    "a3b": {"endpoint": "A3b", "PacksNumber": 1},
    "a4": {"endpoint": "A4", "PacksNumber": 2},
    "a4a": {"endpoint": "A4a", "PacksNumber": 1},
    "a4b": {"endpoint": "A4b", "PacksNumber": 1},
    "b1": {"endpoint": "B1", "PacksNumber": 3},
    "pb": {"endpoint": "P-B", "PacksNumber": 3},
    "b1a": {"endpoint": "B1a", "PacksNumber": 1},
}


def fetch_pack_name(card_id):
    """
    Fetch pack name for a card from Limitless TCG API.
    Fetches the individual card page and checks for pack name in card-prints-current.
    """
    series_prefix = card_id.split("-")[0].lower()
    card_number = card_id.split("-")[1].lstrip("0")  # Remove leading zeros

    if series_prefix not in series_map:
        print(f"⚠️  Unknown series prefix: {series_prefix}")
        return "Error"

    # Fetch individual card page (e.g., /cards/A1/1)
    # Convert series prefix: capitalize first letter, keep rest as-is
    # "a1" -> "A1", "a1a" -> "A1a", "a2b" -> "A2b"
    series_upper = series_prefix[0].upper(
    ) + series_prefix[1:] if len(series_prefix) > 1 else series_prefix.upper()
    url = f"{BASE_URL}{series_upper}/{card_number}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ❌ Error accessing {url}: {e}")
        return "Error"

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for pack name in card-prints-current div
    card_prints_current = soup.find("div", class_="card-prints-current")
    if card_prints_current:
        text = card_prints_current.get_text()
        # Check if there's a pack name (format: "· PackName pack")
        if " pack" in text:
            # Extract pack name - look for text before " pack"
            # Format is usually: "#1 · ◊ · Mewtwo  pack"
            parts = text.split("·")
            for part in parts:
                if " pack" in part:
                    pack_name = part.strip().replace(" pack", "").strip()
                    if pack_name:
                        print(f"  ✅ Pack Found: {pack_name}")
                        return pack_name

    # If no pack name found, it's a shared card
    # Get expansion name from title
    # Title format: "CardName • ExpansionName (Set) #Number"
    # We want to extract just "ExpansionName"
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.text
        # Extract the part between "•" and "("
        if "•" in title_text and " (" in title_text:
            # Format: "CardName • ExpansionName (Set)"
            expansion_part = title_text.split("•")[1].split(" (")[0].strip()
            expansion_name = expansion_part.strip()
        else:
            # Fallback: take everything before "("
            expansion_name = title_text.split(" (")[0].strip()
        print(f"  ✅ No pack found, using Shared({expansion_name})")
        return f"Shared({expansion_name})"

    return "Unknown"


def should_skip_card(card_id):
    """Check if a card should be skipped (pa, pb, or a4b)."""
    series_prefix = card_id.split("-")[0].lower()
    return series_prefix in ["pa", "pb", "a4b"]


def save_json(cards):
    """Save JSON data to file."""
    with open(V4_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)


def log_progress(index, total):
    """Log progress to file and console."""
    progress_text = f"Progress: {index}/{total} cards processed"
    print(f"  📝 {progress_text}")
    # Write to progress log file
    with open(PROGRESS_LOG_PATH, "w", encoding="utf-8") as f:
        f.write(f"Last processed index: {index}\n")
        f.write(f"Total cards: {total}\n")
        f.write(f"Progress: {index}/{total} ({100*index/total:.1f}%)\n")


def main():
    print("📂 Loading v4.json...")
    with open(V4_JSON_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    total_cards = len(cards)
    print(f"📊 Total cards in JSON: {total_cards}")

    # Determine end index
    if TEST_MODE:
        end_index = min(START_INDEX + TEST_LIMIT, total_cards)
        print(f"🧪 TEST MODE: Processing cards {START_INDEX} to {end_index-1}")
    else:
        end_index = total_cards
        print(
            f"🚀 PRODUCTION MODE: Processing all cards from index {START_INDEX}")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for i in range(START_INDEX, end_index):
        card = cards[i]
        card_id = card["id"]
        current_pack = card.get("pack", "")

        print(
            f"\n[{i+1}/{end_index}] Processing index {i}: {card_id} ({card.get('name', 'Unknown')})")
        print(f"  Current pack: {current_pack}")

        # Skip cards with pa, pb, or a4b prefixes
        if should_skip_card(card_id):
            print(f"  ⏭️  Skipping (pa/pb/a4b)")
            skipped_count += 1
            # Still save and log progress for skipped cards
            save_json(cards)
            log_progress(i + 1, total_cards)
            continue

        # Fetch new pack name
        new_pack = fetch_pack_name(card_id)

        if new_pack == "Error" or new_pack == "Unknown":
            print(f"  ⚠️  Could not determine pack name")
            error_count += 1
            # Still save and log progress for errors
            save_json(cards)
            log_progress(i + 1, total_cards)
            continue

        if new_pack != current_pack:
            card["pack"] = new_pack
            print(f"  🔄 Updated pack: {current_pack} → {new_pack}")
            updated_count += 1
        else:
            print(f"  ✅ Pack name already correct: {new_pack}")

        # Save after each card is processed
        save_json(cards)
        log_progress(i + 1, total_cards)

    # Print summary
    print("\n" + "="*50)
    print("Update complete!")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Processed: {end_index - START_INDEX} cards")
    print(f"Last processed index: {end_index - 1}")
    print("="*50)

    # Clean up progress log if completed
    if end_index >= total_cards:
        if PROGRESS_LOG_PATH.exists():
            PROGRESS_LOG_PATH.unlink()
            print("✅ Progress log file cleaned up")


if __name__ == "__main__":
    main()
