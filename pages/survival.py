import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import numpy as np

TC = "#000000"
GRID = "rgba(0,0,0,0.12)"
BG = "rgba(0,0,0,0)"

# ── Load data ──────────────────────────────────────────────
chars = pd.read_csv("data/cleaned/characters_clean.csv")
screentime = pd.read_csv("data/cleaned/screentime_total.csv")

# ── Clean house names ──────────────────────────────────────
def clean_house(h):
    h = str(h).strip()
    if h.lower() in ["unknown", "nan", ""]:
        return "Unknown"
    if not h.startswith("House "):
        known = ["Stark","Lannister","Targaryen","Baratheon","Greyjoy",
                 "Tyrell","Martell","Tully","Arryn","Bolton","Frey",
                 "Mormont","Tarly","Clegane","Reed","Karstark"]
        if h in known:
            return f"House {h}"
    return h

chars["house"] = chars["house"].apply(clean_house)

# ── Merge screen time ──────────────────────────────────────
df = chars.merge(screentime, left_on="name", right_on="character", how="left")
df["total_screentime_overall"] = df["total_screentime_overall"].fillna(0)
df["screentime_mins"] = (df["total_screentime_overall"] / 60).round(1)

# ── Use is_alive as single source of truth ─────────────────
# is_alive = 1 → survived the show
# is_alive = 0 → died during the show
df["fate"] = df["is_alive"].map({1: "Survived", 0: "Died"})
df["house_short"] = df["house"].str.replace("House ", "", regex=False)

# Only characters who appeared on screen
df_vis = df[df["screentime_mins"] > 0].copy()

# ══════════════════════════════════════════════════════════
# CHART 1 — Screen time vs popularity scatter
# ══════════════════════════════════════════════════════════
fig1 = px.scatter(
    df_vis,
    x="screentime_mins",
    y="popularity",
    color="fate",
    color_discrete_map={"Survived": "#27AE60", "Died": "#E74C3C"},
    size="screentime_mins",
    size_max=45,
    hover_name="name",
    hover_data={
        "house_short": True,
        "screentime_mins": ":.1f",
        "popularity": ":.2f",
        "fate": True,
    },
    labels={
        "screentime_mins": "Total Screen Time (minutes)",
        "popularity": "Popularity Score (0 to 1)",
        "fate": "Fate",
        "house_short": "House",
    },
    title="Screen Time vs Popularity — Who Survived the Show?",
)

fig1.update_layout(
    plot_bgcolor="white", paper_bgcolor=BG, height=520,
    font=dict(color=TC),
    title_font=dict(color=TC, size=17),
    legend=dict(
        title=dict(text="Fate:", font=dict(color=TC)),
        font=dict(color=TC),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#cccccc", borderwidth=1,
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
    ),
    margin=dict(l=70, r=60, t=90, b=60),
)
fig1.update_xaxes(
    showline=True, linecolor=TC, linewidth=1,
    showgrid=True, gridcolor=GRID,
    title_font=dict(color=TC, size=13),
    tickfont=dict(color=TC, size=11),
    zeroline=False,
)
fig1.update_yaxes(
    showline=True, linecolor=TC, linewidth=1,
    showgrid=True, gridcolor=GRID,
    title_font=dict(color=TC, size=13),
    tickfont=dict(color=TC, size=11),
    zeroline=False,
)

# ══════════════════════════════════════════════════════════
# CHART 2 — Death rate by house (TV show only)
# Using is_alive from character-predictions dataset
# which tracks TV show survival status
# ══════════════════════════════════════════════════════════

# Known TV show survivors to correct dataset gaps
tv_survivors = {
    "Jon Snow", "Tyrion Lannister", "Arya Stark", "Sansa Stark",
    "Bran Stark", "Samwell Tarly", "Gilly", "Daenerys Targaryen",
    "Yara Greyjoy", "Theon Greyjoy", "Brienne of Tarth",
    "Davos Seaworth", "Bronn", "Podrick Payne", "Grey Worm",
    "Gendry", "Tormund Giantsbane", "Ghost", "Drogon",
    "Robin Arryn", "Edmure Tully", "Hot Pie", "Meera Reed",
    "Howland Reed", "Olenna Tyrell"
}

# Known TV show deaths to correct dataset gaps  
tv_dead = {
    "Cersei Lannister", "Jaime Lannister", "Joffrey Baratheon",
    "Tywin Lannister", "Robb Stark", "Catelyn Stark", "Ned Stark",
    "Margaery Tyrell", "Loras Tyrell", "Mace Tyrell",
    "Oberyn Martell", "Doran Martell", "Trystane Martell",
    "Ellaria Sand", "Stannis Baratheon", "Renly Baratheon",
    "Khal Drogo", "Viserys Targaryen", "Missandei",
    "Jorah Mormont", "Lyanna Mormont", "The Night King",
    "Ramsay Bolton", "Roose Bolton", "Walder Frey",
    "Sandor Clegane", "Gregor Clegane", "Euron Greyjoy",
    "Petyr Baelish", "Varys", "Melisandre", "Beric Dondarrion",
    "Rickon Stark", "Hodor", "Shireen Baratheon",
    "Tommen Baratheon", "Myrcella Baratheon",
}

def get_tv_status(row):
    name = row["name"]
    if name in tv_survivors:
        return 0  # alive
    if name in tv_dead:
        return 1  # dead
    return 1 - row["is_alive"]  # fallback to dataset

df_vis["tv_died"] = df_vis.apply(get_tv_status, axis=1)

house_stats = (
    df_vis.groupby("house_short")
    .agg(
        total=("name", "count"),
        died=("tv_died", "sum"),
    )
    .reset_index()
)
house_stats["death_pct"] = (
    house_stats["died"] / house_stats["total"] * 100
).round(1)
house_stats = house_stats[
    (house_stats["total"] >= 3) &
    (~house_stats["house_short"].isin(["Unknown", "Brave Companions"]))
].sort_values("death_pct", ascending=True)

fig2 = go.Figure(go.Bar(
    x=house_stats["death_pct"],
    y=house_stats["house_short"],
    orientation="h",
    marker=dict(
        color=house_stats["death_pct"],
        colorscale="RdYlGn_r",
        cmin=0, cmax=100,
        showscale=True,
        colorbar=dict(
            title="Death %",
            tickfont=dict(color=TC, size=11),
            title_font=dict(color=TC, size=12),
        )
    ),
    text=[f"{r}%  ({int(d)}/{t})" for r, d, t in zip(
        house_stats["death_pct"],
        house_stats["died"],
        house_stats["total"]
    )],
    textposition="outside",
    textfont=dict(color=TC, size=11),
    hovertemplate=(
        "<b>House %{y}</b><br>"
        "Death rate: %{x}%<br>"
        "%{customdata[0]} died out of %{customdata[1]}<extra></extra>"
    ),
    customdata=house_stats[["died", "total"]].values,
))
fig2.update_layout(
    title=dict(
        text="Death Rate by House — Which House Was Most Dangerous? (TV Show)",
        font=dict(color=TC, size=17)
    ),
    xaxis=dict(
        title="Percentage of Characters Who Died (%)",
        range=[0, 130],
        showgrid=True, gridcolor=GRID,
        showline=True, linecolor=TC, linewidth=1,
        title_font=dict(color=TC, size=13),
        tickfont=dict(color=TC, size=11),
        zeroline=False,
    ),
    yaxis=dict(
        title="",
        showgrid=False,
        showline=True, linecolor=TC, linewidth=1,
        tickfont=dict(color=TC, size=12),
    ),
    plot_bgcolor="white", paper_bgcolor=BG,
    height=max(400, len(house_stats) * 36),
    margin=dict(l=120, r=160, t=80, b=60),
    font=dict(color=TC),
)
# ══════════════════════════════════════════════════════════
# CHART 3 — Logistic regression coefficients
# ══════════════════════════════════════════════════════════
model_df = df_vis.copy()
le = LabelEncoder()
model_df["house_enc"] = le.fit_transform(model_df["house"].fillna("Unknown"))

feature_cols = [
    "screentime_mins",
    "house_enc",
    "is_noble",
    "is_popular",
    "popularity",
    "dead_relations",
]
feature_labels = [
    "Screen Time (mins)",
    "House",
    "Is Noble",
    "Is Popular (binary)",
    "Popularity Score",
    "Dead Family Members",
]
tooltips = [
    "More screen time slightly increases recorded death risk in this dataset",
    "House membership has minimal effect on survival",
    "Noble characters die at slightly higher rates",
    "Being marked as popular (binary) correlates with higher death rate",
    "Higher popularity score strongly protects from death",
    "More dead relatives correlates with higher survival in this dataset",
]

model_df["died_flag"] = (model_df["is_alive"] == 0).astype(int)
model_clean = model_df.dropna(subset=feature_cols + ["died_flag"]).copy()
X = model_clean[feature_cols]
y = model_clean["died_flag"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
clf = LogisticRegression(max_iter=2000, random_state=42, class_weight="balanced")
clf.fit(X_train, y_train)
accuracy = accuracy_score(y_test, clf.predict(X_test))

coef_df = pd.DataFrame({
    "feature": feature_labels,
    "coef": clf.coef_[0],
    "tooltip": tooltips,
}).sort_values("coef", ascending=True)

bar_colors3 = ["#E74C3C" if c > 0 else "#27AE60" for c in coef_df["coef"]]

fig3 = go.Figure(go.Bar(
    x=coef_df["coef"],
    y=coef_df["feature"],
    orientation="h",
    marker_color=bar_colors3,
    text=[f"{c:+.3f}" for c in coef_df["coef"]],
    textposition="outside",
    textfont=dict(color=TC, size=12),
    hovertemplate="<b>%{y}</b><br>Coefficient: %{x:+.3f}<br>%{customdata}<extra></extra>",
    customdata=coef_df["tooltip"].values,
))
fig3.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.35)", line_width=1.5)
fig3.update_layout(
    title=dict(
        text=f"What Predicts Death? — Logistic Regression (Accuracy: {accuracy:.1%})",
        font=dict(color=TC, size=17)
    ),
    xaxis=dict(
        title="🔴 Positive = increases death risk   |   🟢 Negative = protects from death",
        showgrid=True, gridcolor=GRID,
        showline=True, linecolor=TC, linewidth=1,
        title_font=dict(color=TC, size=12),
        tickfont=dict(color=TC, size=11),
        zeroline=False,
    ),
    yaxis=dict(
        showgrid=False,
        showline=True, linecolor=TC,
        tickfont=dict(color=TC, size=12),
        title="",
    ),
    plot_bgcolor="white", paper_bgcolor=BG,
    height=420,
    margin=dict(l=180, r=120, t=80, b=80),
    font=dict(color=TC),
)

# ══════════════════════════════════════════════════════════
# CHART 4 — Characters who survived despite high death risk
# ══════════════════════════════════════════════════════════
model_clean["death_prob"] = clf.predict_proba(X)[:, 1]

# Only characters confirmed alive at end of show
actual_survivors = model_clean[model_clean["is_alive"] == 1].copy()
risky_survivors = actual_survivors.nlargest(15, "death_prob")[
    ["name", "death_prob", "house_short", "screentime_mins"]
]

fig4 = go.Figure(go.Bar(
    x=risky_survivors["death_prob"] * 100,
    y=risky_survivors["name"],
    orientation="h",
    marker=dict(
        color=risky_survivors["death_prob"] * 100,
        colorscale="YlOrRd",
        cmin=50, cmax=100,
        showscale=True,
        colorbar=dict(
            title="Death %",
            tickfont=dict(color=TC, size=11),
            title_font=dict(color=TC, size=12),
        )
    ),
    text=[f"{p*100:.1f}%" for p in risky_survivors["death_prob"]],
    textposition="outside",
    textfont=dict(color=TC, size=12),
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Predicted death probability: %{x:.1f}%<br>"
        "But survived the show!<extra></extra>"
    ),
))
fig4.update_layout(
    title=dict(
        text="Characters Who Cheated Death — Survived Despite High Risk Profile",
        font=dict(color=TC, size=17)
    ),
    xaxis=dict(
        title="Model's Predicted Death Probability (%)",
        range=[0, 120],
        showgrid=True, gridcolor=GRID,
        showline=True, linecolor=TC, linewidth=1,
        title_font=dict(color=TC, size=13),
        tickfont=dict(color=TC, size=11),
        zeroline=False,
    ),
    yaxis=dict(
        showgrid=False,
        showline=True, linecolor=TC,
        tickfont=dict(color=TC, size=12),
        title="",
    ),
    plot_bgcolor="white", paper_bgcolor=BG,
    height=540,
    margin=dict(l=180, r=140, t=80, b=60),
    font=dict(color=TC),
)

if __name__ == "__main__":
    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()