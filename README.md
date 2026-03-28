# Pokemon TCG Pocket Cards

An open source repo for data on the Pokemon TCG Pocket cards.
Useful for building Pokemon TCG Pocket tools such as websites.
Feel free to use the data however you like.

It might be best to use it as an API like:

- Cards data: `https://raw.githubusercontent.com/chase-manning/pokemon-tcg-pocket-cards/refs/heads/main/v4.json`
- Expansions and packs data: `https://raw.githubusercontent.com/chase-manning/pokemon-tcg-pocket-cards/refs/heads/main/expansions.json`

So that whenever there are changes and additions you can get them right away.

If there's anything missing or wrong, feel free to raise a PR.

## Data Source

Card data is scraped from [Limitless TCG](https://pocket.limitlesstcg.com/cards).

## Adding a New Expansion

When a new expansion is released, run a single command to scrape all card data, download images, and update the database:

```bash
pip install -r requirements.txt
python3 scripts/add_expansion.py <SET_CODE>
```

For example:

```bash
python3 scripts/add_expansion.py B2b
```

The script will automatically:

1. Detect the expansion name from Limitless TCG
2. Scrape all cards in the set
3. Download card and pack images
4. Append new cards to `v4.json`
5. Add the expansion to `expansions.json`

### Updating Promo Sets

Promo sets (P-A, P-B) add cards over time rather than all at once. Run the same command to pick up any new cards:

```bash
python3 scripts/add_expansion.py PA
python3 scripts/add_expansion.py PB
```

The script will scrape all cards in the promo set and only add ones not already in the database.

### Options

- `--name "Custom Name"` to override the auto-detected expansion name
- `--skip-images` to skip downloading images

## Projects Using This API

- [Pocket Decks Top](https://pocketdecks.top/) A website showing a tier list of the best Pokemon TCG Pocket Decks based on tournament results, updated weekly every Monday
- [Pocket Card Collection](https://github.com/rhuangabrielsantos/pokemon-tcg-pocket-cards) A collection tracker that lets you save your cards across devices using Google Sign-in, showing your progress towards completing each pack's collection
- [PTCGP Pack Opener](https://github.com/rohannishant/ptcgp-pack-opener) A website for simulating opening Pokemon TCG Pocket Packs
- [All Your Poke Cards](https://github.com/manelbrioude/allyourpokecards) A site for showing info on all your Poke Cards
- [Pokemon Pocket Card Data](https://github.com/nathanrboyer/PokemonPocketCardData) A notebook to help decide which pack to open based on the cards you want to pull
- [Pokemon TCG Pocket Trade Dex](https://github.com/bitmaybewise/pokemon-tcg-pocket-tradedex) A website to facilitate visualization and comparison of cards among players.

If you've built something using this API, feel free to submit a PR to add it to this list!
