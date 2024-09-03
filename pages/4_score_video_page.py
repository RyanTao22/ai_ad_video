import streamlit as st
from sqlalchemy import create_engine
from helpers import update_responses_df, get_last_index, display_responses_df, initialize_responses_df

def score_advertisement():
    st.header("Score the Advertising Videos")
    st.write("Please score the advertising videos you watched on the bottom 3 pages.")
    display_responses_df()

    satisfaction = st.slider("Satisfaction (1-10)", 1, 10, 6)
    accuracy = st.slider("Accuracy (1-10)", 1, 10, 6)
    persuasiveness = st.slider("Persuasiveness (1-10)", 1, 10, 6)
    credibility = st.slider("Credibility (1-10)", 1, 10, 6)
    engagement = st.slider("Engagement (1-10)", 1, 10, 6)
    relevance = st.slider("Relevance (1-10)", 1, 10, 6)
    creativity = st.slider("Creativity (1-10)", 1, 10, 6)
    memorability = st.slider("Memorability (1-10)", 1, 10, 6)
    effectiveness = st.slider("Effectiveness (1-10)", 1, 10, 6)

    if st.button("Complete"):
        last_index = get_last_index()
        update_responses_df(last_index, 'Satisfaction', satisfaction)
        update_responses_df(last_index, 'Accuracy', accuracy)
        update_responses_df(last_index, 'Persuasiveness', persuasiveness)
        update_responses_df(last_index, 'Credibility', credibility)
        update_responses_df(last_index, 'Engagement', engagement)
        update_responses_df(last_index, 'Relevance', relevance)
        update_responses_df(last_index, 'Creativity', creativity)
        update_responses_df(last_index, 'Memorability', memorability)
        update_responses_df(last_index, 'Effectiveness', effectiveness)
        st.dataframe(st.session_state.responses_df.iloc[-1,:].to_frame().T)    

        engine = create_engine(f'mysql+pymysql://{st.secrets["username"]}:{st.secrets["password"]}@{st.secrets["db_url"]}:{st.secrets["port"]}/{st.secrets["database"]}?charset=utf8mb4')
        with engine.begin() as conn:
            st.session_state.responses_df.iloc[-1,:].to_frame().T.to_sql(name=st.secrets['db_table'], con=conn, if_exists='append', index=False)
        
        st.write("Thank you for scoring the advertisement.")
        st.write("You have completed the survey. You can now close the tab to finish.")
        # if st.button("Back to Main"):
        #     st.switch_page("your_app.py")  # 返回主页面

if __name__ == "__main__":
    if 'responses_df' not in st.session_state or st.session_state.product_choice_complete == False:
        initialize_responses_df()
        st.switch_page("pages/1_survey_page.py")
    score_advertisement()
