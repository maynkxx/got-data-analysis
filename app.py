import streamlit as st

st.set_page_config(

    page_title="Game of Thrones — Data Story",

    page_icon="",

    layout="wide",

    initial_sidebar_state="expanded"

)

st.sidebar.title(" GOT Data Story")

st.sidebar.markdown("---")

page = st.sidebar.radio(

    "Navigate",

    [

        " Overview",

        " Ratings Story",

        " Character Network",

        " Survival Analysis",

        " Conclusions"

    ]

)

st.sidebar.markdown("---")

st.sidebar.caption("Data sources: Kaggle · IMDb · Jeffrey Lancaster")

st.sidebar.caption("Built with Python · Plotly · NetworkX · Streamlit")

if page == " Overview":

    from app_pages import overview

    overview.show()

elif page == " Ratings Story":

    from app_pages import ratings

    ratings.show()

elif page == " Character Network":

    from app_pages import network

    network.show()

elif page == " Survival Analysis":

    from app_pages import survival

    survival.show()

elif page == " Conclusions":

    from app_pages import conclusions

    conclusions.show()
