import streamlit as st

import pandas as pd

import plotly.graph_objects as go

TC = "#000000"

GRID = "rgba(0,0,0,0.12)"

BG = "rgba(0,0,0,0)"

def show():

    st.title(" Game of Thrones — A Data Story")

    st.markdown("### *What does the data say about why GOT captured and then lost its audience?*")

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Seasons", "8")

    col2.metric("Episodes", "73")

    col3.metric("Characters", "1,946")

    col4.metric("Scene Appearances", "12,114")

    col5.metric("Peak Rating", "9.9 ")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:

        st.subheader("About this project")

        st.markdown("""
        Game of Thrones was one of the most culturally significant TV shows ever made —
        and one of the most controversial endings in television history.

        This project uses **real data** to tell the story of GOT's rise and fall:

        -  **Ratings Story** — IMDb ratings mapped against 10 key plot events across all 73 episodes
        -  **Character Network** — Interactive graph of 120+ characters built from 12,114 scene appearances
        -  **Survival Analysis** — Screen time vs survival modeled with logistic regression
        """)

    with col_right:

        st.subheader("Key finding")

        st.info("""
        **The data proves it:**

        Popularity score is the strongest predictor of survival (coef: -0.28).

        The more fans loved a character, the less likely they were to die.

        GOT traded narrative risk for audience safety. Fans noticed.
        """)

    st.markdown("---")

    st.subheader("Season by season — the rise and fall")

    episodes = pd.read_csv("data/cleaned/episodes_clean.csv")

    season_avg = episodes.groupby("season")["rating"].mean().reset_index()

    season_avg.columns = ["Season", "Avg Rating"]

    season_avg["Season"] = "S" + season_avg["Season"].astype(str)

    bar_colors = ["#E74C3C" if s == "S8" else "#2980B9" for s in season_avg["Season"]]

    fig = go.Figure(go.Bar(

        x=season_avg["Season"],

        y=season_avg["Avg Rating"].round(2),

        marker_color=bar_colors,

        text=season_avg["Avg Rating"].round(2),

        textposition="outside",

        textfont=dict(color=TC, size=13),

    ))

    overall_avg = episodes["rating"].mean()

    fig.add_hline(

        y=overall_avg, line_dash="dash", line_color="rgba(0,0,0,0.35)",

        annotation_text=f"Series avg: {overall_avg:.2f}",

        annotation_font_color=TC,

        annotation_position="top left"

    )

    fig.update_layout(

        yaxis=dict(

            range=[5, 10], title="Avg IMDb Rating",

            showgrid=True, gridcolor=GRID,

            showline=True, linecolor="#000000",

            title_font=dict(color=TC, size=13),

            tickfont=dict(color=TC, size=11),

            zeroline=False,

        ),

        xaxis=dict(

            title="Season", showgrid=False,

            showline=True, linecolor="#000000",

            title_font=dict(color=TC, size=13),

            tickfont=dict(color=TC, size=11),

        ),

        plot_bgcolor="white",

        paper_bgcolor=BG,

        height=380,

        margin=dict(l=60, r=40, t=50, b=40),

        showlegend=False,

        font=dict(color=TC),

    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("Season 8 (red) avg rating: 6.33 — the steepest drop in the show's history")
