import json
import requests
from bs4 import BeautifulSoup
import re

series_map = {
    "pa": {"endpoint": "P-A", "PacksNumber": 6},
    "a1": {"endpoint": "A1?pack=0", "PacksNumber": 3},
    "a1a": {"endpoint": "A1a", "PacksNumber": 1},
    "a2": {"endpoint": "A2?pack=0", "PacksNumber": 2},
    "a2a": {"endpoint": "A2a", "PacksNumber": 1},
    "a2b": {"endpoint": "A2b", "PacksNumber": 1},
}

BASE_URL = "https://pocket.limitlesstcg.com/cards/"

vx_counter = 1
current_cards_in_volume = 0


def fetch_pack_name(card_id):
    global vx_counter, current_cards_in_volume

    series_prefix = card_id.split("-")[0].lower()

    if series_prefix == "pa":
        card_number = card_id.replace("pa-", "").lstrip("0")
        url = f"{BASE_URL}P-A/{card_number}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Error accessing {url}: {e}")
            return "Error"

        soup = BeautifulSoup(response.text, "html.parser")
        card_prints_div = soup.find("div", class_="card-prints-current")

        if card_prints_div:
            text = card_prints_div.get_text(strip=True)
            match = re.search(
                r"(Shop|Campaign|Missions|Premium Missions|Promo pack|Wonder Pick)",
                text,
            )
            if match:
                pack_name = match.group(0)
                print(f"✅ Pack Found: {pack_name}")

                if "Promo pack" in pack_name:
                    if current_cards_in_volume == 5:
                        vx_counter += 1
                        current_cards_in_volume = 0
                    current_cards_in_volume += 1

                return pack_name

            else:
                print(f"⚠️ No pack found for {card_id}. Setting as null.")
                return "null"

        print(f"⚠️ Prefix {series_prefix} not found in series_map.")
        return "Unknown"

    endpoint = series_map[series_prefix]["endpoint"]
    packs_number = series_map[series_prefix]["PacksNumber"]

    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error accessing {url}: {e}")
        return "Error"

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.text.split(" (")[0]

        if packs_number == 1:
            return title_text
        else:
            return f"Shared({title_text})"
    else:
        print("⚠️ Could not extract the page title.")
        return "Unknown"


def process_json(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    global vx_counter

    cards_with_null_pack = []

    for card in data:
        card_id = card["id"]
        pack = card["pack"]
        if pack == "Every":
            new_pack = fetch_pack_name(card_id)
            if "Promo pack" in new_pack:
                new_pack = f"Promo V{vx_counter}"

            if new_pack != "Unknown" and new_pack != pack:
                print(f"🔄 Updated pack for {card_id}: {pack} ➝ {new_pack}")
                card["pack"] = new_pack

            if new_pack == "null":
                cards_with_null_pack.append(card_id)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Processing complete! Corrected JSON saved to: {output_file}")

    if cards_with_null_pack:
        print("\n⚠️ Cards with 'null' pack (need manual adjustment):")
        for card_id in cards_with_null_pack:
            print(f"- {card_id}")
    else:
        print("\n✅ All cards have been updated successfully.")


process_json("../v4.json", "../v4_fixed.json")