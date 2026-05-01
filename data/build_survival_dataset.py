import json

import pandas as pd

from collections import defaultdict

def clean_name(name):

    return str(name).strip().lower()

with open("data/raw/episodes.json") as f:

    episodes = json.load(f)

screentime_df = pd.read_csv("data/cleaned/screentime_total.csv")

chars_df = pd.read_csv("data/cleaned/characters_clean.csv")

screentime_df["name_clean"] = screentime_df["character"].apply(clean_name)

chars_df["name_clean"] = chars_df["name"].apply(clean_name)

last_seen = defaultdict(int)

for ep in episodes["episodes"]:

    season = ep["season"]

    for scene in ep.get("scenes", []):

        for c in scene.get("characters", []):

            if c.get("name"):

                name = clean_name(c["name"])

                last_seen[name] = max(last_seen[name], season)

last_seen_df = pd.DataFrame([

    {"name_clean": k, "last_seen_season": v}

    for k, v in last_seen.items()

])

print(f"Characters found in episodes.json: {len(last_seen_df)}")

df = last_seen_df.merge(

    screentime_df[["name_clean", "total_screentime_overall"]],

    on="name_clean",

    how="left"

)

df = df.merge(

    chars_df[["name_clean", "name", "house", "is_noble", "popularity"]],

    on="name_clean",

    how="left"

)

df["total_screentime_overall"] = df["total_screentime_overall"].fillna(0)

df["screentime_mins"] = (df["total_screentime_overall"] / 60).round(1)

df["survived"] = (df["last_seen_season"] == 8).astype(int)

df["fate"] = df["survived"].map({1: "Survived", 0: "Died/Removed"})

df = df[df["screentime_mins"] > 0].copy()

print(f"\nCharacters with screen time: {len(df)}")

print(f"Survived: {df['survived'].sum()} | Died/Removed: {(df['survived']==0).sum()}")

print("\nSample sanity check:")

test_chars = [

    "jon snow",

    "tyrion lannister",

    "daenerys targaryen",

    "eddard stark",

    "robb stark",

    "cersei lannister"

]

for name in test_chars:

    row = df[df["name_clean"] == name]

    if not row.empty:

        print(

            f"{row['name'].values[0]} → "

            f"last_seen_season={row['last_seen_season'].values[0]}, "

            f"fate={row['fate'].values[0]}"

        )

output_path = "data/cleaned/survival_clean.csv"

df.to_csv(output_path, index=False)

print(f"\n Saved to {output_path}")
