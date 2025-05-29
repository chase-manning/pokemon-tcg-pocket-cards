import json
import requests
import os
import re
from bs4 import BeautifulSoup


BASE_URL = "https://pocket.limitlesstcg.com/cards/"

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "pokemon_cards_transposed.json")
os.makedirs(output_dir, exist_ok=True)


set_mapping = {
    "Genetic Apex  (A1)": "a1",
    "Mythical Island  (A1a)": "a1a",
    "Promo-A": "pa",
    "Space-Time Smackdown  (A2)": "a2",
    "Triumphant Light  (A2a)": "a2a",
    "Shining Revelry  (A2b)": "a2b",
    "Celestial Guardians  (A3)": "a3",
    "Extradimensional Crisis  (A3a)": "a3a",
}

series_map = {
    "pa": {"endpoint": "P-A", "PacksNumber": 6},
    "a1": {"endpoint": "A1?pack=0", "PacksNumber": 3},
    "a1a": {"endpoint": "A1a", "PacksNumber": 1},
    "a2": {"endpoint": "A2?pack=0", "PacksNumber": 2},
    "a2a": {"endpoint": "A2a", "PacksNumber": 1},
    "a2b": {"endpoint": "A2b", "PacksNumber": 1},
    "a3": {"endpoint": "A3?pack=0", "PacksNumber": 2},
    "a3a": {"endpoint": "A3a", "PacksNumber": 1},
}


def get_id(data):
    padded_id = data["id"].zfill(3)
    set_id = set_mapping.get(data["set_details"])
    if not set_id:
        raise ValueError(f"Set ID not found for {data['set_details']}")
    return f"{set_id}-{padded_id}"


vx_counter = 1
current_cards_in_volume = 0


def fetch_pack_name(card_id):
    global vx_counter, current_cards_in_volume

    series_prefix = card_id.split("-")[0].lower()

    if series_prefix == "pa":
        card_number = card_id.replace("pa-", "").lstrip("0")
        url = f"{BASE_URL}P-A/{card_number}"
    else:
        endpoint = series_map[series_prefix]["endpoint"]
        url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error accessing {url}: {e}")
        return "Error"

    soup = BeautifulSoup(response.text, "html.parser")

    if series_prefix == "pa":
        card_prints_div = soup.find("div", class_="card-prints-current")
        if card_prints_div:
            text = card_prints_div.get_text(strip=True)
            match = re.search(
                r"(Shop|Campaign|Missions|Premium Missions|Promo pack|Wonder Pick)", text)
            if match:
                pack_name = match.group(0)
                print(f"✅ Pack Found: {pack_name}")

                if "Promo pack" in pack_name:
                    if current_cards_in_volume == 5:
                        vx_counter += 1
                        current_cards_in_volume = 0
                    current_cards_in_volume += 1

                return pack_name
            return "Error"
        return "Error"
    else:
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.text.split(" (")[0]
            if series_map[series_prefix]["PacksNumber"] == 1:
                return title_text
            else:
                return f"Shared({title_text})"
        return "Unknown"


def main():
    input_file_path = os.path.join(
        os.path.dirname(__file__), "cards_data.json")

    print("📂 Lendo dados do arquivo local...")
    with open(input_file_path, "r", encoding="utf-8") as f:
        input_list = json.load(f)

    print("🔄 Formatando cards...")
    new_cards = []
    for card in input_list:
        card_id = get_id(card)
        name = card.get("name")
        rarity = card.get("rarity")

        if rarity == "Crown Rare":
            rarity = "♕"
        if card_id.startswith("pa"):
            rarity = "Promo"

        pack = card.get("pack", "")
        if pack.endswith(" pack"):
            pack = pack[:-5]

        new_cards.append({
            "id": card_id,
            "name": name,
            "rarity": rarity,
            "pack": pack,
            "health": card.get("hp"),
            "image": card.get("image"),
            "fullart": card.get("fullart"),
            "ex": card.get("ex"),
            "artist": card.get("artist"),
            "type": card.get("type"),
        })

    print(f"💾 Salvando JSON formatado em: {output_path}")
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(new_cards, f, ensure_ascii=False, indent=2)

    print("🔍 Corrigindo packs 'Every' com scraping...")
    correct_packs(output_path, output_path)


def correct_packs(input_file, output_file):
    global vx_counter
    cards_with_null_pack = []

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for card in data:
        card_id = card["id"]
        pack = card["pack"]
        if pack == "Every":
            new_pack = fetch_pack_name(card_id)
            if "Promo pack" in new_pack:
                new_pack = f"Promo V{vx_counter}"

            if new_pack != "Unknown" and new_pack != pack:
                print(f"🔄 Atualizado {card_id}: {pack} ➝ {new_pack}")
                card["pack"] = new_pack

            if new_pack == "null":
                cards_with_null_pack.append(card_id)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Arquivo final salvo em: {output_file}")

    if cards_with_null_pack:
        print("\n⚠️ Cards com 'null' no pack (ajuste manual necessário):")
        for card_id in cards_with_null_pack:
            print(f"- {card_id}")
    else:
        print("\n✅ Todos os packs foram corrigidos com sucesso.")


if __name__ == "__main__":
    main()
