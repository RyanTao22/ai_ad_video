import streamlit as st
import datetime
import pytz
from helpers import add_row_to_responses_df, initialize_responses_df

def survey_page():
    st.title("Demographics Survey")

    age = st.selectbox("Age Range", ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
    gender = st.radio("Gender", ["Male", "Female", "Non-binary / third gender", "Prefer not to say"])
    education = st.selectbox("Highest Education Level", ["Some high school or less", "High school diploma or GED", "Some college, but no degree received",
                                                         "Associates or technical degree", "Bachelor's", "Graduate or professional degree (MA, MS, MBA, PhD, JD, MD, DDS etc.)", "Prefer not to say"])
    income = st.selectbox("Household Income Range Before Taxes During the Past 12 Months", ["<25,000", "25,000-49,999", "50,000-74,999", "75,000-99,999", "100,000-149,999", "150,000+", "Prefer not to say"])
    ethnicity = st.selectbox("Ethnicity", ["American Indian or Alaska Native", "Asian", "Black or African American", "Hispanic or Latino", "Native Hawaiian or Other Pacific Islander",
                                           "White", "Middle Eastern", "Multiracial/Mixed ethnicity", "Other/Not specified"])

    if st.button("Save"):
        LA_time = datetime.datetime.now(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S')
        row_data = [LA_time, None, age, gender, education, income, ethnicity, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        add_row_to_responses_df(row_data)
        st.session_state.demographics_complete = True
        st.switch_page("pages/2_product_choice_page.py")  # 跳转到产品选择页面

if __name__ == "__main__":
    if 'responses_df' not in st.session_state:
        initialize_responses_df()
        st.switch_page("pages/1_survey_page.py")
    survey_page()
