# Pokemon TCG Pocket Cards

An open source repo for data on the Pokemon TCG Cards.  
Useful for building Pokemon TCG Pocket tools such as websites.  
Feel free to use the data however you like.

It might be best to use it as a an API like:  
`https://raw.githubusercontent.com/chase-manning/pokemon-tcg-pocket-cards/refs/heads/main/v4.json`  
So that whenever there are changes and additions you can get them right away.

If there's anything missing or wrong, feel free to raise a PR.

## Data Source

The source data is from [Limitless TCG](https://pocket.limitlesstcg.com/cards).  
The source data is downloaded using [Pokémon TCG Pocket Web Scraper](https://github.com/LucachuTW/CARDS-PokemonPocket-scrapper).  
And then transposed using `scripts/transpose-format.js`.

## Projects Using This API

- [Pocket Decks Top](https://pocketdecks.top/) A website showing a tier list of the best Pokemon TCG Pocket Decks based on tournaments resuts, updated weekly every Monday
- [Pocket Card Collection](https://github.com/rhuangabrielsantos/pokemon-tcg-pocket-cards) A collection tracker that lets you save your cards across devices using Google Sign-in, showing your progress towards completing each pack's collection
- [PTCGP Pack Opener](https://github.com/rohannishant/ptcgp-pack-opener) A website for simulating opening Pokemon TCG Pocket Packs
- [All Your Poke Cards](https://github.com/manelbrioude/allyourpokecards) A site for showing info on all your Poke Cards

If you've built something using this API, feel free to submit a PR to add it to this list!
