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
