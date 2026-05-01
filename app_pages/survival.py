import streamlit as st
import sys
sys.path.append(".")
from pages.survival import fig1, fig2, fig3, fig4, accuracy

def show():
    st.title("⚔️ Survival Analysis")
    st.markdown("*Does screen time protect you? Does popularity make you immortal?*")

    # ── Data transparency note ─────────────────────────────
    st.warning("""
    **A note on data quality**

    The datasets used in this analysis are fan-compiled and sourced from Kaggle.
    They are based on a mix of book and show data, and many characters have
    missing values for fields like age, house, and nobility status.

    The prediction model achieves modest accuracy due to these limitations.
    The charts and findings below are based on the available data and should
    be interpreted as directional insights rather than definitive conclusions.
    All results shown are based on characters with recorded screen time only.
    """)

    st.markdown("---")

    # ── Chart 1 ────────────────────────────────────────────
    st.subheader("Screen time vs popularity — who survived?")
    st.markdown("""
    Each dot is a character. **🟢 Green = survived** the show. **🔴 Red = died.**
    Dot size reflects total screen time. Characters with more screen time
    cluster to the right and are almost entirely green — the show protected
    its most visible characters, especially in later seasons.
    Hover over any dot to see the character's name, house, and screen time.
    """)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ── Chart 2 ────────────────────────────────────────────
    st.subheader("Death rate by house")
    st.markdown("""
    Shows what percentage of named characters from each house died during the show.
    The label on each bar shows the exact count (e.g. **100% — 3/3** means
    all 3 characters from that house died). Only houses with 3 or more
    characters with screen time are included.
    """)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Chart 3 ────────────────────────────────────────────
    st.subheader("What actually predicts death?")
    st.markdown(f"""
    A logistic regression model was trained on screen time, house, nobility,
    and popularity to predict whether a character would die.

    **Model accuracy: {accuracy:.1%}** — modest, which is expected given
    the incomplete data. The direction of the coefficients is still meaningful.

    **How to read this chart:**
    - 🔴 Red bar = this factor increases death risk
    - 🟢 Green bar = this factor protects from death
    - Hover over each bar for a plain English explanation

    **Key insight:** Popularity Score is the strongest protective factor.
    The more audiences loved a character, the less likely the show killed them.
    """)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Chart 4 ────────────────────────────────────────────
    st.subheader("Characters who cheated death")
    st.markdown("""
    These are characters who **actually survived** the show but whose profile
    (house, nobility, screen time, popularity) suggested a high death probability.
    Every character shown here is confirmed alive at the end of Season 8.
    Hover over each bar to see the full details.

    *Note: Results are based on available data only. Characters with missing
    data fields may not appear even if they are notable survivors.*
    """)
    st.plotly_chart(fig4, use_container_width=True)