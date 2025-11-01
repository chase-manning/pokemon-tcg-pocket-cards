import json
import os
import random
import time
import requests
from PIL import Image
import io

# Configuration
EXPANSIONS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "expansions.json")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
GITHUB_BASE_URL = "https://raw.githubusercontent.com/chase-manning/pokemon-tcg-pocket-cards/refs/heads/main/images"
TEST_LIMIT = 100  # Only process first 3 packs for testing


def ensure_images_directory():
    """Create images directory if it doesn't exist."""
    os.makedirs(IMAGES_DIR, exist_ok=True)


def image_exists(pack_id):
    """Check if image file already exists in images directory."""
    image_path = os.path.join(IMAGES_DIR, f"{pack_id}.png")
    return os.path.exists(image_path)


def is_github_url(image_url):
    """Check if image URL is already in GitHub format."""
    return image_url.startswith(GITHUB_BASE_URL)


def download_and_convert_image(image_url, pack_id):
    """Download image from URL and convert to PNG format."""
    print(f"  📥 Downloading image from: {image_url}")

    # Wait random time between 0 and 1 seconds
    wait_time = random.uniform(0, 1)
    print(f"  ⏳ Waiting {wait_time:.2f} seconds...")
    time.sleep(wait_time)

    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # Open image from bytes
        img = Image.open(io.BytesIO(response.content))

        # Convert to RGBA if necessary (for transparency support)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Save as PNG
        output_path = os.path.join(IMAGES_DIR, f"{pack_id}.png")
        img.save(output_path, 'PNG')
        print(f"  ✅ Saved image to: {output_path}")

        return True
    except Exception as e:
        print(f"  ❌ Error downloading/converting image: {e}")
        return False


def update_image_url(pack):
    """Update pack's image URL to GitHub format."""
    pack_id = pack["id"]
    new_url = f"{GITHUB_BASE_URL}/{pack_id}.png"
    pack["image"] = new_url
    return new_url


def save_json(data):
    """Save JSON data back to expansions.json."""
    print(f"  💾 Saving updated JSON to: {EXPANSIONS_JSON_PATH}")
    with open(EXPANSIONS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    print("🚀 Starting pack image download and update process...")
    print(f"📂 Loading JSON from: {EXPANSIONS_JSON_PATH}")

    # Load JSON data
    with open(EXPANSIONS_JSON_PATH, "r", encoding="utf-8") as f:
        expansions = json.load(f)

    # Count total packs
    total_packs = sum(len(exp["packs"]) for exp in expansions)
    print(f"📊 Total packs across all expansions: {total_packs}")
    print(f"🧪 Processing first {TEST_LIMIT} packs for testing...")

    # Ensure images directory exists
    ensure_images_directory()

    # Process packs (limited to first TEST_LIMIT for testing)
    processed = 0
    skipped = 0
    updated = 0

    for expansion in expansions:
        expansion_id = expansion["id"]
        expansion_name = expansion["name"]

        for pack in expansion["packs"]:
            if processed >= TEST_LIMIT:
                break

            pack_id = pack["id"]
            pack_name = pack.get("name", "Unknown")
            image_url = pack.get("image", "")

            print(
                f"\n[{processed+1}/{TEST_LIMIT}] Processing pack: {pack_id} ({pack_name}) - Expansion: {expansion_name} ({expansion_id})")

            # Check if image file already exists
            has_image_file = image_exists(pack_id)

            # Check if URL is already in GitHub format
            has_github_url = is_github_url(image_url)

            if has_image_file and has_github_url:
                print(
                    f"  ⏭️  Skipping: Image file exists and URL is already in GitHub format")
                skipped += 1
                processed += 1
                continue

            needs_download = not has_image_file
            needs_url_update = not has_github_url

            # Download image if needed
            if needs_download:
                if not image_url:
                    print(f"  ⚠️  No image URL found, skipping download")
                    skipped += 1
                    processed += 1
                    continue

                # Download from serebii.net URLs
                if "serebii.net" in image_url:
                    success = download_and_convert_image(image_url, pack_id)
                    if not success:
                        print(
                            f"  ⚠️  Failed to download image, skipping URL update")
                        skipped += 1
                        processed += 1
                        continue
                    needs_download = False  # Now we have it
                else:
                    print(
                        f"  ⚠️  Image URL is not from serebii.net, skipping download")

            # Update URL if needed
            if needs_url_update or needs_download:
                new_url = update_image_url(pack)
                print(f"  🔄 Updated image URL to: {new_url}")
                updated += 1

                # Save JSON after each update
                save_json(expansions)
                print(f"  ✅ Progress saved!")

            processed += 1

        if processed >= TEST_LIMIT:
            break

    print(f"\n📊 Summary:")
    print(f"  - Processed: {processed}")
    print(f"  - Updated: {updated}")
    print(f"  - Skipped: {skipped}")
    print(f"\n✅ Done!")


if __name__ == "__main__":
    main()
