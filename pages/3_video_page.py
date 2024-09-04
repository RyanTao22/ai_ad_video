import streamlit as st
from helpers import update_responses_df, get_last_index,initialize_responses_df
from helpers import generate_ad_script_prompt,generate_ai_audio,  add_audio_to_video
#from helpers import generate_ai_video

def play_video():
    
    st.title("Watch the Advertisement Video")
    st.write("It may take a few minutes to prepare the video. Please wait for a moment.")
    st.dataframe(st.session_state.responses_df)

    if st.session_state.video_complete == False:
        if st.session_state.group == "1" :
            video_url = 'https://www.youtube.com/watch?v=9cCVWcdbAlk'
            last_index = get_last_index()
            update_responses_df(last_index, 'Video_url', video_url)
            st.video(video_url)
            st.session_state.video_complete = True
        else:
            generate_ad_script_prompt()
            generate_ai_audio()
            #generate_ai_video()
            add_audio_to_video()
            st.session_state.video_complete = True
            # st.video(url1)


    if st.button("Next"):
        st.switch_page("pages/4_score_video_page.py")  # 跳转到评分页面

if __name__ == "__main__":
    if 'responses_df' not in st.session_state or st.session_state.product_choice_complete == False:
        initialize_responses_df()
        st.switch_page("pages/1_survey_page.py")
    
    
    play_video()
