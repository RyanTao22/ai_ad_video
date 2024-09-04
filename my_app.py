import streamlit as st
from helpers import initialize_responses_df

# Initialize session state variables
initialize_responses_df()


# Sidebar navigation
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio("Go to", ["Survey Page", "Product Choice Page", "Video", "Score the Video"], key='page')

if page_selection == "Survey Page":
    st.switch_page("pages/1_survey_page.py")
elif page_selection == "Product Choice Page":
    st.switch_page("pages/2_product_choice_page.py")
elif page_selection == "Video":
    st.switch_page("pages/3_video_page.py")
elif page_selection == "Score the Video":
    st.switch_page("pages/4_score_video_page.py")

