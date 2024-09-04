import streamlit as st
import pandas as pd
import numpy as np

from openai import OpenAI
client = OpenAI(api_key=st.secrets["openai_api_key"])

import oss2
oss_auth = oss2.Auth(st.secrets["oss_id"], st.secrets["oss_key"])
oss_bucket = oss2.Bucket(oss_auth, st.secrets["oss_ip"] , st.secrets["oss_bucket"])

import requests
import time
import random
import re
import base64
import json
Group_Prob = [0.2, 0.2, 0.2, 0.2, 0.2]

import io
import os
currentPath = os.getcwd().replace('\\','/')
import sys
sys.path.append(currentPath+'ffmpeg')
sys.path.append(currentPath+'ffprobe')
from pydub import AudioSegment

import moviepy.editor as mp
from io import BytesIO

import tempfile


def initialize_responses_df():
    if 'responses_df' not in st.session_state:
        data = {
            'Timestamp_LA': [],
            'Test_Group': [],
            'Age_Range': [],
            'Gender': [],
            'Education_Level': [],
            'Household_Income': [],
            'Ethnicity': [],
            'Product_Choice_1': [],
            'Product_Choice_2': [],
            'Product_Choice_3': [],
            "Prompt": [],
            "Script": [],
            "Video_url": [],
            "Satisfaction": [],
            "Accuracy": [],
            "Persuasiveness": [],
            "Credibility": [],
            "Engagement": [],
            "Relevance": [],
            "Creativity": [],
            "Memorability": [],
            "Effectiveness": []
        }
        st.session_state.responses_df = pd.DataFrame(data)
    
    if 'demographics_complete' not in st.session_state:
        st.session_state.demographics_complete = False

    if 'product_choice_complete' not in st.session_state:
        st.session_state.product_choice_complete = False

    if 'group' not in st.session_state:
        st.session_state.group = ""

    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    if 'script' not in st.session_state:
        st.session_state.script = ""

def get_last_index():
    return len(st.session_state.responses_df) - 1

def add_row_to_responses_df(row_data):
    st.session_state.responses_df.loc[len(st.session_state.responses_df)] = row_data

def update_responses_df(row_index, column_name, value):
    st.session_state.responses_df.at[row_index, column_name] = value

def display_responses_df():
    st.dataframe(st.session_state.responses_df)

def get_gpt_response(prompt, using_model="gpt-4o"):
    response = client.chat.completions.create(
      model=using_model,
      messages=[
        {"role": "user", "content": prompt},
      ]
    )
    return response.choices[0].message.content

def generate_ad_script_prompt():
    #st.title("Generated Ad Script Prompt for Head & Shoulders Shampoo")
    group = np.random.choice(['1','2','3','4','5'],1,p=Group_Prob)[0]
    st.session_state['group'] = group
    
    if not st.session_state.responses_df.empty:
        
        user_data = st.session_state.responses_df.iloc[-1]

        
        prod_info = pd.read_csv('product_info.csv',index_col = [0])
        choosed_sofa = prod_info.loc[user_data['Product_Choice_1']]
        choosed_tooth = prod_info.loc[user_data['Product_Choice_2']]
        choosed_shampoo = prod_info.loc[user_data['Product_Choice_3']]

        shampoo = 'The favorite shampoo of this user is ' + str(choosed_shampoo.description_from_gpt)
        tooth = 'The favorite toothpaste of this user is ' + str(choosed_tooth.description_from_gpt)
        sofa = 'The favorite sofa chair of this user is ' + str(choosed_sofa.description_from_gpt)
        pre = f"""
        
        For your reference, here are 3 of his/her purchase preference history:  
        1. {sofa}  
        2. {tooth}  
        3. {shampoo}  
        """
        
        prompt1 = "Prompt: /"
        prompt2 = f"Prompt: Create an engaging and persuasive script for a Head & Shoulders shampoo ad in the narrative."
        prompt3 = f"Prompt: Create an engaging and persuasive script for a Head & Shoulders shampoo ad targeting a {user_data['Age_Range']} year old {user_data['Gender']} with a {user_data['Education_Level']} education level. The ad should resonate with individuals having a household income of {user_data['Household_Income']} and belonging to the {user_data['Ethnicity']} ethnicity in the narrative. "
        prompt4 = f"""
                    {prompt2}  
                    {pre}  """
        prompt5 = f"""
                    {prompt3}  
                    {pre}  """

        remind_info = f"""\nRemind!:  
        1. The scene description takes the same amount of time as the storyteller's statement.
           Format: 
           [Scene: last ? seconds: ...]
           Narrator: ...
           [Scene: last ? seconds: ...]
           Narrator: ...
           ...
        2. Make sure there is only one narrator and no dialogue from other characters.  
        3. Also, make sure that only one character appears in the ad.
        4. Just output the script and the time info in plaintext, no other formart information like '```plaintext' or '```markdown' or '### Head & Shoulders Shampoo Ad Script' is needed.  
        5. The format requirements is strict."""
        prompt2 = prompt2 + remind_info
        prompt3 = prompt3 + remind_info
        prompt4 = prompt4 + remind_info
        prompt5 = prompt5 + remind_info

       
        instrument1 = "Default Ad without any AI help." 
        instrument2 = "Ad with AI but not personalized."    
        instrument3 = "Ad with AI personalized with Demographics."
        instrument4 = "Ad with AI personalized with Product Choices."
        instrument5 = "Ad with AI personalized with Demographics and Product Choices."

        instrument = locals()['instrument'+str(group)]
        prompt = locals()['prompt'+str(group)]

        # st.write("Group"+group+": "+instrument)
        # st.markdown(prompt.replace('$','\$'))
        last_index = get_last_index()
        st.session_state.responses_df.loc[last_index, 'Test_Group'] = "Group"+group
        st.session_state.responses_df.loc[last_index, 'Prompt'] = prompt
        # st.write("Script:")

        script = "Default"if group =='1' else get_gpt_response(prompt, "gpt-4o")
        
        st.session_state.responses_df.loc[last_index, 'Script'] = script
        # st.write(script)
        # st.dataframe(st.session_state.responses_df) 
        st.session_state['group'] = group
        st.session_state['prompt'] = prompt
        st.session_state['script'] = script

def generate_ai_audio():
    if st.session_state.group != "1":
        pattern = r'(?:\[Narrator\]?[:]?|Narrator:)\s*([^\[]*)'
        narrator_paragraphs = re.findall(pattern, st.session_state.script+'\n', re.DOTALL | re.MULTILINE)
        script = '\n'.join(paragraph.strip() for paragraph in narrator_paragraphs )
        
        # Generate Audio with elevenlabs
        model_url = "https://api.elevenlabs.io/v1/text-to-speech/Mu5jxyqZOLIGltFpfalg/with-timestamps"

        payload = {
            "voice_settings": {
                "similarity_boost": 0.8,
                "stability": 0.3
            },
            "text": script
        }
        headers = {
            "xi-api-key": st.secrets['elevenlabs_key'],
            "Content-Type": "application/json"
        }
        response_audio = requests.request("POST", model_url, json=payload, headers=headers)

        json_string = response_audio.content.decode("utf-8")
        response_dict = json.loads(json_string)
        audio_bytes = base64.b64decode(response_dict["audio_base64"])
        

        sentences = script.splitlines()
        char_index = 0
        start_timestamps = []
        durations = []
        
        for sentence in sentences:
            sentence_start_time = response_dict['alignment']['character_start_times_seconds'][char_index]
            sentence_end_time = response_dict['alignment']['character_end_times_seconds'][char_index + len(sentence) - 1]
            duration = sentence_end_time - sentence_start_time
            
            start_timestamps.append(sentence_start_time)
            durations.append(duration)
            
            char_index += len(sentence) + 1  # +1 to account for the newline character
        
        # # Export the modified audio to a byte stream

        # Upload modified audio to OSS
        audio_name = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1, 100)) + '.mp3'
        oss_bucket.put_object(audio_name, audio_bytes)
        
        st.session_state.audio_dict = {
            'audio_name': audio_name,
            'audio_bytes': audio_bytes, # audio_bytes = base64.b64decode(response_dict["audio_base64"])
            'audio_url': oss_bucket.sign_url('GET', audio_name, 180),

            'narrator_start_timestamps': start_timestamps,  # A list records duration of each sentence
            'narrator_durations': durations
        }
        st.audio(audio_bytes)


# def generate_ai_video():
#     if st.session_state.group != "1":
#         # Prepare the scene's script
#         script = st.session_state.script+'\n'
#         pattern = r'\[Scene: last (\d+) seconds: (.*?)\]'
#         matches = re.findall(pattern, script)
#         formatted_scenes = [[int(seconds), description] for seconds, description in matches]
#         if len(formatted_scenes) == len(st.session_state.audio_dict['narrator_durations']):
#             formatted_scenes = [[st.session_state.audio_dict['narrator_durations'][i], description] for i, [seconds, description] in enumerate(formatted_scenes)]
        
#         # Generate Video with ai video api
#         url = "https://api.aivideoapi.com/runway/generate/text"

#         responses = []
#         response_urls = []

#         for seconds, description in formatted_scenes:
#             payload = {
#             "text_prompt": "masterpiece, cinematic, "+ description,
#             "model": "gen3",
#             "width": 1344,
#             "height": 768,
#             "motion": 5,
#             "seed": 0,
#             "upscale": True,
#             "interpolate": True,
#             "callback_url": "",
#             "time": 5 if seconds <= 5 else 10
#             }

        
#             headers = {
#                 "accept": "application/json",
#                 "content-type": "application/json",
#                 "Authorization": st.secrets['aivideoapi_token'],
#             }

#             response = requests.post(url, json=payload, headers=headers)
#             responses.append(response.json())
        
#         video_urls = []
#         st.session_state.video_urls = video_urls

#         for response in responses:
#             st.dataframe(pd.DataFrame({'uuid': [response['uuid']]}))
#             uuid = response['uuid']
#             status_url = f"https://api.aivideoapi.com/status?uuid={uuid}"

#             headers_status = {
#                 "accept": "application/json",
#                 "Authorization": st.secrets['aivideoapi_token']
#             }

#             while True:
#                 response_status = requests.get(status_url, headers=headers_status)
#                 status_json = response_status.json()
                
#                 if status_json["status"] == "success":
#                     video_urls.append(status_json["url"])
#                     break
#                 elif status_json["status"] in ["in queue", "submitted"]:
#                     time.sleep(5)  # Wait and recheck the status
#                 else:
#                     print(f"Error generating video: {status_json}")
#                     break
        
#         if len(video_urls) == len(responses):
#             st.session_state.video_urls = video_urls
          

def add_audio_to_video():
    # 获取音频URL和视频URL
    #audio_url = st.session_state.audio_dict['audio_url']
    audio_bytes = st.session_state.audio_dict['audio_bytes']  # 假设已经从base64解码
    audio_start_timestamps = st.session_state.audio_dict['narrator_start_timestamps']  # 每句话的开始时间戳
    
    #video_urls = st.session_state.video_urls\
    video_urls = ['https://files.aivideoapi.com/video/20240904/ac7ded0d-9461-4514-a899-5e2925474b16.mp4',
                  'https://files.aivideoapi.com/video/20240902/3a7a6ee0-3afc-4594-a01f-574858b88d03.mp4',
                  'https://files.aivideoapi.com/video/20240902/0e0b3ba2-0a6b-4915-a29a-296711e31ba5.mp4',
                  'https://files.aivideoapi.com/video/20240902/318cefa5-48eb-4e33-939b-ce991dd72395.mp4',
                  'https://files.aivideoapi.com/video/20240816/ab4ba7da-1740-41dc-a5a7-3fc516829adf.mp4',
                  'https://files.aivideoapi.com/video/20240815/85d1d6e9-1f95-40cd-a4fc-6237d8841773.mp4',
                  'https://files.aivideoapi.com/video/20240902/0e0b3ba2-0a6b-4915-a29a-296711e31ba5.mp4',
                  'https://files.aivideoapi.com/video/20240902/318cefa5-48eb-4e33-939b-ce991dd72395.mp4',
                  'https://files.aivideoapi.com/video/20240816/ab4ba7da-1740-41dc-a5a7-3fc516829adf.mp4',
                  'https://files.aivideoapi.com/video/20240815/85d1d6e9-1f95-40cd-a4fc-6237d8841773.mp4',
                  'https://files.aivideoapi.com/video/20240904/ac7ded0d-9461-4514-a899-5e2925474b16.mp4',
                  'https://files.aivideoapi.com/video/20240902/3a7a6ee0-3afc-4594-a01f-574858b88d03.mp4',
                  'https://files.aivideoapi.com/video/20240902/0e0b3ba2-0a6b-4915-a29a-296711e31ba5.mp4',
                  'https://files.aivideoapi.com/video/20240902/318cefa5-48eb-4e33-939b-ce991dd72395.mp4']
    video_urls = video_urls[0:len(audio_start_timestamps)]
    if not video_urls:
        return  # 没有视频则返回
    
    # 将音频加载为音频剪辑（使用临时文件）
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_file.flush()
        audio_clip = mp.AudioFileClip(temp_audio_file.name)

    # 视频片段容器，用来合并所有视频
    final_clips = []
    
    for i, video_url in enumerate(video_urls):
        # 下载并加载视频文件
        video_response = requests.get(video_url)
        
        # 使用临时文件保存视频
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(video_response.content)
            temp_video_file.flush()
            video_clip = mp.VideoFileClip(temp_video_file.name)
        
        # 获取对应的音频起始时间
        start_time = audio_start_timestamps[i]
        
        # 剪辑视频以与音频对齐
        video_duration = video_clip.duration
        audio_start = start_time
        if i + 1 < len(audio_start_timestamps):
            audio_end = audio_start_timestamps[i + 1]
        else:
            audio_end = audio_clip.duration
        
        # 截取音频段
        sentence_audio = audio_clip.subclip(audio_start, audio_end)
        
        # 使视频的时长与音频相同
        video_clip = video_clip.subclip(0, min(video_duration, sentence_audio.duration))
        
        # 将音频片段添加到视频
        final_video = video_clip.set_audio(sentence_audio)
        
        # 添加到视频片段列表
        final_clips.append(final_video)
    
    # 合并所有视频片段
    final_combined_video = mp.concatenate_videoclips(final_clips)
    
    # 使用临时文件保存最终视频
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_final_video_file:
        final_combined_video.write_videofile(temp_final_video_file.name, codec='libx264', audio_codec='aac')
        
        # 将临时文件写入到BytesIO
        video_buffer = BytesIO()
        with open(temp_final_video_file.name, 'rb') as f:
            video_buffer.write(f.read())
        
        video_buffer.seek(0)  # 将指针回到开始位置以进行上传
    
    # 上传到OSS
    video_name = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1, 100)) + '.mp4'
    oss_bucket.put_object(video_name, video_buffer)
    
    # 假设这里是保存最终视频的URL逻辑
    final_video_url = oss_bucket.sign_url('GET', video_name, 180)
    last_index = get_last_index()
    st.session_state.responses_df.loc[last_index, 'Video_url'] = final_video_url
    st.video(final_video_url)
