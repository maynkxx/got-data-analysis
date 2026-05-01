import pandas as pd

import plotly.graph_objects as go

episodes = pd.read_csv("data/cleaned/episodes_clean.csv")

TC = "#000000"

GRID = "rgba(0,0,0,0.12)"

BG = "rgba(0,0,0,0)"

events = [

    {"season": 1, "episode": 9,  "label": "Ned Stark executed",     "ay": -40, "ax": 0},

    {"season": 2, "episode": 9,  "label": "Battle of Blackwater",   "ay": -40, "ax": 0},

    {"season": 3, "episode": 9,  "label": "Red Wedding",            "ay": -40, "ax": 0},

    {"season": 4, "episode": 9,  "label": "Battle of Castle Black", "ay": -40, "ax": 0},

    {"season": 5, "episode": 8,  "label": "Hardhome",               "ay": -40, "ax": 0},

    {"season": 6, "episode": 9,  "label": "Battle of the Bastards", "ay": -40, "ax": -60},

    {"season": 6, "episode": 10, "label": "Cersei burns the Sept",  "ay": -70, "ax": 0},

    {"season": 7, "episode": 4,  "label": "Loot Train Attack",      "ay": -40, "ax": 60},

    {"season": 8, "episode": 3,  "label": "The Long Night",         "ay": -40, "ax": -50},

    {"season": 8, "episode": 6,  "label": "Series Finale",          "ay": -70, "ax": -50},

]

def get_overall(season, episode):

    row = episodes[(episodes["season"] == season) & (episodes["episode"] == episode)]

    if not row.empty:

        return row["episode_overall"].values[0]

    return None

for e in events:

    e["episode_overall"] = get_overall(e["season"], e["episode"])

season_starts = episodes.groupby("season")["episode_overall"].min().reset_index()

season_colors = [

    "rgba(231,76,60,0.07)", "rgba(52,152,219,0.07)",

    "rgba(46,204,113,0.07)", "rgba(155,89,182,0.07)",

    "rgba(241,196,15,0.07)", "rgba(26,188,156,0.07)",

    "rgba(230,126,34,0.07)", "rgba(149,165,166,0.10)"

]

fig = go.Figure()

for i, row in season_starts.iterrows():

    season = int(row["season"])

    x_start = row["episode_overall"] - 0.5

    x_end = (season_starts[season_starts["season"] == season + 1]["episode_overall"].values[0] - 0.5

             if season < 8 else episodes["episode_overall"].max() + 0.5)

    fig.add_vrect(x0=x_start, x1=x_end, fillcolor=season_colors[i], layer="below", line_width=0)

    fig.add_annotation(

        x=(x_start + x_end) / 2, y=7.12,

        text=f"S{season}", showarrow=False,

        font=dict(size=11, color="#444444")

    )

fig.add_trace(go.Bar(

    x=episodes["episode_overall"], y=episodes["vote_count"],

    name="Vote Count", marker_color="rgba(0,0,0,0.07)",

    yaxis="y2",

    hovertemplate="Episode %{x}<br>Votes: %{y:,}<extra></extra>",

))

fig.add_trace(go.Scatter(

    x=episodes["episode_overall"], y=episodes["rating"],

    mode="lines+markers", name="IMDb Rating",

    line=dict(color="#C0392B", width=2.5),

    marker=dict(size=6, color="#C0392B"),

    hovertemplate=(

        "<b>%{customdata[0]}</b><br>S%{customdata[1]}E%{customdata[2]}<br>"

        "Rating: %{y}<br>Votes: %{customdata[3]:,}<extra></extra>"

    ),

    customdata=episodes[["title", "season", "episode", "vote_count"]].values,

))

for e in events:

    if e["episode_overall"] is None:

        continue

    ep_row = episodes[episodes["episode_overall"] == e["episode_overall"]]

    rating = ep_row["rating"].values[0]

    fig.add_annotation(

        x=e["episode_overall"], y=rating,

        text=e["label"], showarrow=True,

        arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="#333333",

        ax=e["ax"], ay=e["ay"],

        font=dict(size=9.5, color="#000000"),

        bgcolor="rgba(255,255,255,0.9)",

        bordercolor="rgba(0,0,0,0.25)",

        borderwidth=1, borderpad=3,

    )

fig.update_layout(

    title=dict(text="Game of Thrones — IMDb Ratings Across All 73 Episodes", font=dict(color=TC, size=17)),

    xaxis=dict(

        title="Episode (Overall)",

        showgrid=False,

        showline=True, linecolor=TC, linewidth=1,

        range=[0.5, 73.5],

        title_font=dict(color=TC, size=13),

        tickfont=dict(color=TC, size=11),

        zeroline=False,

    ),

    yaxis=dict(

        title="IMDb Rating",

        range=[7.0, 10.2],

        showgrid=True, gridcolor=GRID,

        showline=True, linecolor=TC, linewidth=1,

        title_font=dict(color=TC, size=13),

        tickfont=dict(color=TC, size=11),

        zeroline=False,

    ),

    yaxis2=dict(

        title="Vote Count",

        overlaying="y", side="right",

        showgrid=False,

        showline=True, linecolor=TC, linewidth=1,

        title_font=dict(color=TC, size=13),

        tickfont=dict(color=TC, size=11),

        zeroline=False,

    ),

    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=TC)),

    hovermode="x unified",

    plot_bgcolor="white",

    paper_bgcolor=BG,

    height=520,

    margin=dict(l=60, r=70, t=80, b=60),

    font=dict(color=TC),

)

season_avg = episodes.groupby("season").agg(

    avg_rating=("rating", "mean"),

    avg_viewers=("viewers", "mean"),

    total_votes=("vote_count", "sum")

).reset_index()

bar_colors = ["#2980B9","#27AE60","#E67E22","#8E44AD","#C0392B","#16A085","#D35400","#7F8C8D"]

fig2 = go.Figure()

fig2.add_trace(go.Bar(

    x=[f"Season {s}" for s in season_avg["season"]],

    y=season_avg["avg_rating"].round(2),

    marker_color=bar_colors,

    text=season_avg["avg_rating"].round(2),

    textposition="outside",

    textfont=dict(color=TC, size=13),

    hovertemplate=(

        "<b>%{x}</b><br>Avg Rating: %{y}<br>"

        "Avg Viewers: %{customdata[0]:.2f}M<br>"

        "Total Votes: %{customdata[1]:,}<extra></extra>"

    ),

    customdata=season_avg[["avg_viewers", "total_votes"]].values,

))

overall_avg = episodes["rating"].mean()

fig2.add_hline(

    y=overall_avg, line_dash="dash", line_color="rgba(0,0,0,0.35)",

    annotation_text=f"Series avg: {overall_avg:.2f}",

    annotation_font_color=TC,

    annotation_position="top left"

)

fig2.update_layout(

    title=dict(text="Average IMDb Rating by Season", font=dict(color=TC, size=17)),

    xaxis=dict(

        title="Season",

        showgrid=False,

        showline=True, linecolor=TC, linewidth=1,

        title_font=dict(color=TC, size=13),

        tickfont=dict(color=TC, size=11),

        zeroline=False,

    ),

    yaxis=dict(

        title="Average IMDb Rating",

        range=[5, 10.8],

        showgrid=True, gridcolor=GRID,

        showline=True, linecolor=TC, linewidth=1,

        title_font=dict(color=TC, size=13),

        tickfont=dict(color=TC, size=11),

        zeroline=False,

    ),

    plot_bgcolor="white",

    paper_bgcolor=BG,

    height=460,

    margin=dict(l=60, r=60, t=80, b=60),

    showlegend=False,

    font=dict(color=TC),

)

if __name__ == "__main__":

    fig.show()

    fig2.show()
