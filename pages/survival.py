import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import numpy as np

# ── Load data ──────────────────────────────────────────────
chars = pd.read_csv("data/cleaned/characters_clean.csv")
screentime = pd.read_csv("data/cleaned/screentime_total.csv")

# ── Merge screen time into character profiles ──────────────
df = chars.merge(screentime, left_on="name", right_on="character", how="left")
df["total_screentime_overall"] = df["total_screentime_overall"].fillna(0)
df["screentime_mins"] = (df["total_screentime_overall"] / 60).round(1)

# Only keep characters with some screen time for meaningful analysis
df_screen = df[df["screentime_mins"] > 0].copy()
print(f"Characters with screen time: {len(df_screen)}")
print(f"Dead: {df_screen['actually_died'].sum()} | Alive: {(df_screen['actually_died'] == 0).sum()}")

# ══════════════════════════════════════════════════════════
# CHART 1 — Screen time vs survival scatter plot
# ══════════════════════════════════════════════════════════
df_screen["status"] = df_screen["is_alive"].map({1: "Alive", 0: "Dead"})
df_screen["house_short"] = df_screen["house"].str.replace("House ", "").str.replace("Unknown", "No House")

fig1 = px.scatter(
    df_screen,
    x="screentime_mins",
    y="popularity",
    color="status",
    color_discrete_map={"Alive": "#2ECC71", "Dead": "#E74C3C"},
    size="screentime_mins",
    size_max=40,
    hover_name="name",
    hover_data={"house_short": True, "screentime_mins": True, "popularity": True, "status": True},
    labels={
        "screentime_mins": "Total Screen Time (minutes)",
        "popularity": "Popularity Score",
        "status": "Fate",
        "house_short": "House"
    },
    title="Screen Time vs Popularity — Who Survived?"
)

fig1.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=60, r=60, t=80, b=60),
)
fig1.update_xaxes(showgrid=True, gridcolor="rgba(200,200,200,0.3)")
fig1.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.3)")

# ══════════════════════════════════════════════════════════
# CHART 2 — Death rate by house
# ══════════════════════════════════════════════════════════
house_stats = (
    df_screen.groupby("house")
    .agg(
        total=("name", "count"),
        dead=("actually_died", "sum")
    )
    .reset_index()
)
house_stats["death_rate"] = (house_stats["dead"] / house_stats["total"] * 100).round(1)
house_stats["house_short"] = house_stats["house"].str.replace("House ", "")

# Keep only houses with 3+ characters
house_stats = house_stats[house_stats["total"] >= 3].sort_values("death_rate", ascending=True)

fig2 = go.Figure(go.Bar(
    x=house_stats["death_rate"],
    y=house_stats["house_short"],
    orientation="h",
    marker=dict(
        color=house_stats["death_rate"],
        colorscale="RdYlGn_r",
        showscale=True,
        colorbar=dict(title="Death %")
    ),
    text=[f"{r}%" for r in house_stats["death_rate"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Death rate: %{x}%<extra></extra>",
))

fig2.update_layout(
    title="Death Rate by House — Which House Is Most Dangerous to Be In?",
    xaxis=dict(title="Death Rate (%)", showgrid=True, gridcolor="rgba(200,200,200,0.3)"),
    yaxis=dict(title=""),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500,
    margin=dict(l=150, r=80, t=80, b=60),
)

# ══════════════════════════════════════════════════════════
# CHART 3 — Logistic Regression survival prediction
# ══════════════════════════════════════════════════════════
# Prepare features
model_df = df_screen.copy()

# Encode house as numeric
le = LabelEncoder()
model_df["house_encoded"] = le.fit_transform(model_df["house"].fillna("Unknown"))

features = ["screentime_mins", "house_encoded", "is_noble", "is_popular", "popularity", "dead_relations"]
target = "actually_died"

model_df = model_df.dropna(subset=features + [target])
X = model_df[features]
y = model_df[target]

print(f"\nModel dataset: {len(model_df)} characters")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# Train model
clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel accuracy: {accuracy:.1%}")
print(classification_report(y_test, y_pred, target_names=["Survived", "Died"]))

# Feature importance chart
feature_names = ["Screen Time", "House", "Is Noble", "Is Popular", "Popularity Score", "Dead Relations"]
coefficients = clf.coef_[0]

coef_df = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients
}).sort_values("coefficient", ascending=True)

colors = ["#E74C3C" if c > 0 else "#2ECC71" for c in coef_df["coefficient"]]

fig3 = go.Figure(go.Bar(
    x=coef_df["coefficient"],
    y=coef_df["feature"],
    orientation="h",
    marker_color=colors,
    text=[f"{c:+.2f}" for c in coef_df["coefficient"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Coefficient: %{x:.3f}<extra></extra>",
))

fig3.add_vline(x=0, line_dash="dash", line_color="gray")

fig3.update_layout(
    title=f"What Predicts Death? — Logistic Regression Coefficients (Accuracy: {accuracy:.1%})",
    xaxis=dict(
        title="Coefficient (Red = increases death risk, Green = decreases death risk)",
        showgrid=True, gridcolor="rgba(200,200,200,0.3)"
    ),
    yaxis=dict(title=""),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=400,
    margin=dict(l=150, r=80, t=80, b=60),
)

# ══════════════════════════════════════════════════════════
# CHART 4 — Top characters most likely to have died
# ══════════════════════════════════════════════════════════
model_df["death_probability"] = clf.predict_proba(X)[:, 1]

# Show top 20 characters by death probability who actually survived
risky_survivors = (
    model_df[model_df["actually_died"] == 0]
    .nlargest(15, "death_probability")
    [["name", "death_probability", "house", "screentime_mins"]]
)

fig4 = go.Figure(go.Bar(
    x=risky_survivors["death_probability"] * 100,
    y=risky_survivors["name"],
    orientation="h",
    marker_color="#E67E22",
    text=[f"{p*100:.1f}%" for p in risky_survivors["death_probability"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Death probability: %{x:.1f}%<extra></extra>",
))

fig4.update_layout(
    title="Characters Who Should Have Died (But Didn't) — Model Predictions",
    xaxis=dict(title="Predicted Death Probability (%)", range=[0, 110]),
    yaxis=dict(title=""),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500,
    margin=dict(l=180, r=80, t=80, b=60),
)

if __name__ == "__main__":
    print("\nOpening all charts...")
    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()