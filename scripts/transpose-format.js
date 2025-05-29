const fs = require("fs");

const inputDir = "./scripts/cards_data.json";
const inputList = JSON.parse(fs.readFileSync(inputDir, "utf8"));

const getId = (data) => {
  const paddedId = data.id.padStart(3, "0");
  const setMapping = {
    "Genetic Apex  (A1)": "a1",
    "Mythical Island  (A1a)": "a1a",
    "Promo-A": "pa",
    "Space-Time Smackdown  (A2)": "a2",
    "Triumphant Light  (A2a)": "a2a",
    "Shining Revelry  (A2b)": "a2b",
    "Celestial Guardians  (A3)": "A3",
    "Extradimensional Crisis  (A3a)": "A3a",
  };
  const setId = setMapping[data.set_details];
  if (!setId) throw new Error(`Set ID not found for ${data.set_details}`);
  return `${setId}-${paddedId}`;
};

const newCards = [];
for (const card of inputList) {
  const id = getId(card);
  const name = card.name;
  let rarity = card.rarity;
  if (rarity === "Crown Rare") rarity = "♕";
  if (id.startsWith("pa")) rarity = "Promo";
  let pack = card.pack;
  if (pack.endsWith(" pack")) pack = pack.slice(0, -5);
  const health = card.hp;
  const image = card.image;
  const fullart = card.fullart;
  const ex = card.ex;
  const artist = card.artist;
  const type = card.type;
  newCards.push({
    id,
    name,
    rarity,
    pack,
    health,
    image,
    fullart,
    ex,
    artist,
    type,
  });
}

const outputDir = "./scripts/pokemon_cards_transposed.json";
fs.writeFileSync(outputDir, JSON.stringify(newCards, null, 2));
