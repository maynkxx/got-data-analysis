import pandas as pd
import json

# ── Load raw data ──────────────────────────────────────────
ratings = pd.read_csv("data/raw/got_imdb.csv")
episode_details = pd.read_csv("data/raw/Game_of_Thrones.csv")
predictions = pd.read_csv("data/raw/character-predictions.csv")
deaths = pd.read_csv("data/raw/character-deaths.csv")
battles = pd.read_csv("data/raw/battles.csv")

with open("data/raw/episodes.json", "r") as f:
    episodes_json = json.load(f)

# ══════════════════════════════════════════════════════════
# CLEAN 1 — Master episodes dataframe
# ══════════════════════════════════════════════════════════
# Rename episode_details columns for clarity
episode_details = episode_details.rename(columns={
    "Season": "season",
    "No. of Episode (Season)": "episode",
    "No. of Episode (Overall)": "episode_overall",
    "Title of the Episode": "title",
    "Running Time (Minutes)": "runtime",
    "Directed by": "director",
    "Written by": "writer",
    "Original Air Date": "air_date",
    "U.S. Viewers (Millions)": "viewers",
    "IMDb Rating": "imdb_rating_detail",
    "Rotten Tomatoes Rating (Percentage)": "rotten_tomatoes",
    "Synopsis": "synopsis"
})

ratings = ratings.rename(columns={
    "Season": "season",
    "Episode": "episode",
    "AirDate": "air_date_ratings",
    "Title": "title_ratings",
    "Rating": "rating",
    "Counts": "vote_count",
    "Desc": "description"
})

# Merge on season + episode
episodes = pd.merge(
    episode_details[["season", "episode", "episode_overall", "title",
                     "runtime", "director", "writer", "air_date",
                     "viewers", "rotten_tomatoes", "synopsis"]],
    ratings[["season", "episode", "rating", "vote_count", "description"]],
    on=["season", "episode"],
    how="inner"
)

print(f"✅ Master episodes: {episodes.shape[0]} rows × {episodes.shape[1]} columns")
print(episodes[["season", "episode", "title", "rating", "viewers", "vote_count"]].head(5))

# ══════════════════════════════════════════════════════════
# CLEAN 2 — Character profiles dataframe
# ══════════════════════════════════════════════════════════
chars = predictions[[
    "name", "house", "male", "culture", "isNoble",
    "isMarried", "isPopular", "popularity",
    "numDeadRelations", "isAlive", "actual", "age"
]].copy()

# Standardize column names
chars = chars.rename(columns={
    "male": "is_male",
    "isNoble": "is_noble",
    "isMarried": "is_married",
    "isPopular": "is_popular",
    "numDeadRelations": "dead_relations",
    "isAlive": "is_alive",
    "actual": "actually_died"
})

# Fill missing house with "Unknown"
chars["house"] = chars["house"].fillna("Unknown")
chars["age"] = chars["age"].fillna(-1)  # -1 = age unknown

print(f"\n✅ Character profiles: {chars.shape[0]} rows × {chars.shape[1]} columns")
print(chars[["name", "house", "is_alive", "popularity"]].head(5))

# ══════════════════════════════════════════════════════════
# CLEAN 3 — Deaths dataframe
# ══════════════════════════════════════════════════════════
deaths_clean = deaths[["Name", "Allegiances", "Gender", "Nobility"]].copy()
deaths_clean = deaths_clean.rename(columns={
    "Name": "name",
    "Allegiances": "allegiance",
    "Gender": "gender",
    "Nobility": "nobility"
})
deaths_clean["allegiance"] = deaths_clean["allegiance"].fillna("Unknown")

print(f"\n✅ Deaths: {deaths_clean.shape[0]} rows × {deaths_clean.shape[1]} columns")

# ══════════════════════════════════════════════════════════
# CLEAN 4 — Battles dataframe
# ══════════════════════════════════════════════════════════
battles_clean = battles[[
    "name", "year", "attacker_king", "defender_king",
    "attacker_1", "defender_1", "attacker_outcome",
    "battle_type", "major_death", "major_capture",
    "location", "region"
]].copy()

battles_clean["attacker_king"] = battles_clean["attacker_king"].fillna("Unknown")
battles_clean["defender_king"] = battles_clean["defender_king"].fillna("Unknown")
battles_clean["attacker_outcome"] = battles_clean["attacker_outcome"].fillna("Unknown")

print(f"\n✅ Battles: {battles_clean.shape[0]} rows × {battles_clean.shape[1]} columns")

# ══════════════════════════════════════════════════════════
# CLEAN 5 — Screen time from episodes.json
# ══════════════════════════════════════════════════════════
from datetime import datetime

def parse_time(t):
    """Convert 'H:MM:SS' or 'M:SS' to total seconds"""
    try:
        parts = t.strip().split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        return 0
    return 0

screentime_records = []

for ep in episodes_json["episodes"]:
    season = ep.get("seasonNum")
    episode_num = ep.get("episodeNum")
    episode_title = ep.get("episodeTitle", "")
    scenes = ep.get("scenes", [])

    for scene in scenes:
        start = parse_time(scene.get("sceneStart", "0:00"))
        end = parse_time(scene.get("sceneEnd", "0:00"))
        duration = max(end - start, 0)
        characters_in_scene = scene.get("characters", [])

        for char in characters_in_scene:
            name = char.get("name", "")
            if name:
                screentime_records.append({
                    "season": season,
                    "episode": episode_num,
                    "episode_title": episode_title,
                    "character": name,
                    "scene_duration": duration
                })

screentime = pd.DataFrame(screentime_records)

screentime_agg = screentime.groupby(
    ["character", "season"]
)["scene_duration"].sum().reset_index()
screentime_agg.columns = ["character", "season", "total_screentime"]

screentime_total = screentime.groupby(
    "character"
)["scene_duration"].sum().reset_index()
screentime_total.columns = ["character", "total_screentime_overall"]

print(f"\n✅ Screen time records: {len(screentime)} scene appearances")
print(f"✅ Unique characters with screen time: {screentime['character'].nunique()}")
print(screentime_total.sort_values("total_screentime_overall", ascending=False).head(10))

# ══════════════════════════════════════════════════════════
# SAVE cleaned data
# ══════════════════════════════════════════════════════════
episodes.to_csv("data/cleaned/episodes_clean.csv", index=False)
chars.to_csv("data/cleaned/characters_clean.csv", index=False)
deaths_clean.to_csv("data/cleaned/deaths_clean.csv", index=False)
battles_clean.to_csv("data/cleaned/battles_clean.csv", index=False)
screentime_agg.to_csv("data/cleaned/screentime_by_season.csv", index=False)
screentime_total.to_csv("data/cleaned/screentime_total.csv", index=False)

print("\n✅ All cleaned files saved to data/cleaned/")