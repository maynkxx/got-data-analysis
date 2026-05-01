import streamlit as st

import sys

sys.path.append(".")

from pages.ratings import fig, fig2

def show():

    st.title(" The Ratings Story")

    st.markdown("*IMDb ratings across all 73 episodes — mapped against the moments that defined the show*")

    st.markdown("---")

    st.subheader("Episode-by-episode ratings with key plot events")

    st.markdown("""
    Each annotation marks a moment that caused a measurable audience reaction.
    The **Red Wedding** (S3E9) produced the biggest single-episode spike.
    The **Series Finale** (S8E6) produced the biggest single-episode drop.
    """)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Average rating by season")

    st.markdown("""
    Season 4 was the peak at **9.31**. Season 8 collapsed to **6.33** —
    a drop of nearly 3 full rating points from the show's best season.
    """)

    st.plotly_chart(fig2, use_container_width=True)
