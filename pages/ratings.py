import pandas as pd
import plotly.graph_objects as go

# ── Load cleaned data ──────────────────────────────────────
episodes = pd.read_csv("data/cleaned/episodes_clean.csv")

# ── Key plot events to annotate on the chart ──────────────
events = [
    {"season": 1, "episode": 9,  "label": "Ned Stark executed",      "ay": -40, "ax": 0},
    {"season": 2, "episode": 9,  "label": "Battle of Blackwater",    "ay": -40, "ax": 0},
    {"season": 3, "episode": 9,  "label": "Red Wedding",             "ay": -40, "ax": 0},
    {"season": 4, "episode": 9,  "label": "Battle of Castle Black",  "ay": -40, "ax": 0},
    {"season": 5, "episode": 8,  "label": "Hardhome",                "ay": -40, "ax": 0},
    {"season": 6, "episode": 9,  "label": "Battle of the Bastards",  "ay": -40, "ax": -60},
    {"season": 6, "episode": 10, "label": "Cersei burns the Sept",   "ay": -70, "ax": 0},
    {"season": 7, "episode": 4,  "label": "Loot Train Attack",       "ay": -40, "ax": 60},
    {"season": 8, "episode": 3,  "label": "The Long Night",          "ay": -40, "ax": -50},
    {"season": 8, "episode": 6,  "label": "Series Finale",           "ay": -70, "ax": -50},
]

# Map events to episode_overall number
def get_overall(season, episode):
    row = episodes[
        (episodes["season"] == season) &
        (episodes["episode"] == episode)
    ]
    if not row.empty:
        return row["episode_overall"].values[0]
    return None

for e in events:
    e["episode_overall"] = get_overall(e["season"], e["episode"])

# ── Season boundary markers ────────────────────────────────
season_starts = episodes.groupby("season")["episode_overall"].min().reset_index()

# ── Build the chart ────────────────────────────────────────
fig = go.Figure()

# Season background shading
season_colors = [
    "rgba(255,200,200,0.15)", "rgba(200,220,255,0.15)",
    "rgba(200,255,220,0.15)", "rgba(255,240,200,0.15)",
    "rgba(240,200,255,0.15)", "rgba(200,255,255,0.15)",
    "rgba(255,220,240,0.15)", "rgba(220,220,220,0.20)"
]

for i, row in season_starts.iterrows():
    season = int(row["season"])
    x_start = row["episode_overall"] - 0.5
    x_end = (season_starts[season_starts["season"] == season + 1]["episode_overall"].values[0] - 0.5
             if season < 8 else episodes["episode_overall"].max() + 0.5)
    fig.add_vrect(
        x0=x_start, x1=x_end,
        fillcolor=season_colors[i],
        layer="below", line_width=0,
    )
    fig.add_annotation(
        x=(x_start + x_end) / 2,
        y=7.1,
        text=f"S{season}",
        showarrow=False,
        font=dict(size=11, color="#888"),
    )

# Vote count as background bar (secondary axis)
fig.add_trace(go.Bar(
    x=episodes["episode_overall"],
    y=episodes["vote_count"],
    name="Vote count",
    marker_color="rgba(180,180,180,0.3)",
    yaxis="y2",
    hovertemplate="Episode %{x}<br>Votes: %{y:,}<extra></extra>",
))

# Rating line
fig.add_trace(go.Scatter(
    x=episodes["episode_overall"],
    y=episodes["rating"],
    mode="lines+markers",
    name="IMDb Rating",
    line=dict(color="#E63946", width=2.5),
    marker=dict(size=6, color="#E63946"),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "S%{customdata[1]}E%{customdata[2]}<br>"
        "Rating: %{y}<br>"
        "Votes: %{customdata[3]:,}<extra></extra>"
    ),
    customdata=episodes[["title", "season", "episode", "vote_count"]].values,
))

# Event annotations
for e in events:
    if e["episode_overall"] is None:
        continue
    ep_row = episodes[episodes["episode_overall"] == e["episode_overall"]]
    rating = ep_row["rating"].values[0]

    fig.add_annotation(
        x=e["episode_overall"],
        y=rating,
        text=e["label"],
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#333",
        ax=e["ax"],
        ay=e["ay"],
        font=dict(size=9.5, color="#333"),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#ccc",
        borderwidth=1,
        borderpad=3,
    )

# Layout
fig.update_layout(
    title=dict(
        text="Game of Thrones — IMDb Ratings Across All 73 Episodes",
        font=dict(size=18)
    ),
    xaxis=dict(
        title="Episode (Overall)",
        showgrid=False,
        range=[0.5, 73.5]
    ),
    yaxis=dict(
        title="IMDb Rating",
        range=[7.0, 10.0],
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)"
    ),
    yaxis2=dict(
        title="Vote Count",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=550,
    margin=dict(l=60, r=60, t=80, b=60),
)

if __name__ == "__main__":
    fig.show()