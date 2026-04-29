import pandas as pd
import json


battles = pd.read_csv("data/raw/battles.csv")
deaths = pd.read_csv("data/raw/character-deaths.csv")
predictions = pd.read_csv("data/raw/character-predictions.csv")
characters = pd.read_csv("data/raw/Game_of_Thrones.csv")
ratings = pd.read_csv("data/raw/got_imdb.csv")

with open("data/raw/episodes.json", "r") as f:
    episodes = json.load(f)


datasets = {
    "battles": battles,
    "deaths": deaths,
    "predictions": predictions,
    "characters": characters,
    "ratings": ratings,
}

for name, df in datasets.items():
    print(f"\n{'='*50}")
    print(f"DATASET: {name}")
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"\nFirst 2 rows:")
    print(df.head(2))


print(f"\n{'='*50}")
print("DATASET: episodes.json")
print(f"Top level keys: {list(episodes.keys())}")
print(f"Number of episodes: {len(episodes.get('episodes', []))}")