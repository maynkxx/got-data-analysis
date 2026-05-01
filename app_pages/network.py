import streamlit as st

import streamlit.components.v1 as components

def show():

    st.title(" Character Network")

    st.markdown("*Every node is a character. Every edge is a shared scene. The more scenes two characters share, the thicker the connection.*")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.markdown(" **Yellow** = Lannister")

    col2.markdown(" **Grey** = Stark")

    col3.markdown(" **Red** = Targaryen")

    col4, col5, col6 = st.columns(3)

    col4.markdown(" **Green** = Tyrell")

    col5.markdown(" **Blue** = Tully")

    col6.markdown(" **Faded** = Dead character")

    st.markdown("*Hover over any node to see character details. Scroll to zoom. Drag to explore.*")

    st.markdown("---")

    try:

        with open("assets/network.html", "r", encoding="utf-8") as f:

            html = f.read()

        components.html(html, height=750, scrolling=False)

    except FileNotFoundError:

        st.error("Network file not found. Run: python3 pages/network.py")
