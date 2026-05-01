import streamlit as st

def show():

    st.title(" Conclusions")

    st.markdown("### What does the data say about why Game of Thrones lost its audience?")

    st.markdown("---")

    st.markdown("""
    ### 1. The decline was not sudden — it was a pattern

    Season 5 was the first season to fall below the series average rating of 8.83.
    The show recovered in Season 6 (its best creative season after Season 4),
    but the structural cracks were already visible. Season 8's collapse to 6.33
    was the culmination of a trend, not a surprise.

    ---

    ### 2. The show stopped killing its fan favourites

    This is the most important finding in this analysis.

    In Seasons 1-4, GOT built its reputation on being unpredictable —
    Ned Stark, Robb Stark, Catelyn Stark, Joffrey, Oberyn, Tywin.
    Major fan-favourite characters died constantly.

    The logistic regression model shows that **popularity score is the strongest
    predictor of survival (coefficient: -0.28)**. The more audiences loved a character,
    the less likely they were to die — particularly in Seasons 7 and 8.

    The show traded its greatest strength (narrative risk) for audience safety.
    Audiences — consciously or not — noticed.

    ---

    ### 3. The network tells its own story

    The character network of Seasons 1-4 was sprawling and complex —
    dozens of storylines, houses, and power centres competing simultaneously.

    By Season 8, the network had collapsed to a small core of survivors,
    all converging on a single plot. The structural complexity that made
    the show great had been simplified away.

    ---

    ### 4. House Tyrell, Tarly, and Reed were completely wiped out

    Three houses reached 100% death rates. House Martell hit 85.7%.
    The show systematically eliminated entire power blocs to simplify
    its endgame — further evidence of narrative consolidation over complexity.

    ---

    ### The one-sentence answer

    **Game of Thrones lost its audience when it stopped being willing
    to kill the characters audiences loved most — and the data proves it.**
    """)

    st.markdown("---")

    st.markdown("*Built by Mayank | Python · Pandas · Plotly · NetworkX · Scikit-learn · Streamlit*")
