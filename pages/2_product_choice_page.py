import streamlit as st
from PIL import Image
from helpers import update_responses_df, get_last_index,initialize_responses_df

def product_choice_page():
    st.title("Product Choices")

    product_choices = {
        "Product 1": ["sofa1", 'sofa2', 'sofa3', 'sofa4', 'sofa5', 'sofa6', 'sofa7', 'sofa8', 'sofa9', 'sofa10'],
        "Product 2": ['toothpaste1', 'toothpaste2', 'toothpaste3', 'toothpaste4', 'toothpaste5', 'toothpaste6', 'toothpaste7', 'toothpaste8', 'toothpaste9', 'toothpaste10'],
        "Product 3": ['shampoo1', 'shampoo2', 'shampoo3', 'shampoo4', 'shampoo5', 'shampoo6', 'shampoo7', 'shampoo8', 'shampoo9', 'shampoo10']
    }

    st.subheader("Please choose your favorite product from the following options for living room sofa.")
    sofapic1 = Image.open('pics/sofa.png')
    st.image(sofapic1, caption='Product 1: Living room sofa', use_column_width=True)
    choice1 = st.selectbox("Choose between these products for Product 1: Living room sofa", options=product_choices["Product 1"])

    st.subheader("Please choose your favorite product from the following options for toothpaste.")
    toothpastepic1 = Image.open('pics/toothpaste.png')
    st.image(toothpastepic1, caption='Product 2: Toothpaste', use_column_width=True)
    choice2 = st.selectbox("Choose between these products for Product 2: Toothpaste", options=product_choices["Product 2"])

    st.subheader("Please choose your favorite product from the following options for shampoo.")
    shampoopic1 = Image.open('pics/shampoo.png')
    st.image(shampoopic1, caption='Product 3: Shampoo', use_column_width=True)
    choice3 = st.selectbox("Choose between these products for Product 3: Shampoo", options=product_choices["Product 3"])

    if st.button("Submit"):
        last_index = get_last_index()
        update_responses_df(last_index, 'Product_Choice_1', choice1)
        update_responses_df(last_index, 'Product_Choice_2', choice2)
        update_responses_df(last_index, 'Product_Choice_3', choice3)
        st.session_state.product_choice_complete = True
        st.switch_page("pages/3_video_page.py")  # 跳转到视频页面

if __name__ == "__main__":
    if 'responses_df' not in st.session_state or st.session_state.demographics_complete == False:
        initialize_responses_df()
        st.switch_page("pages/1_survey_page.py")
    product_choice_page()
