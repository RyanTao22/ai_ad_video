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
        st.audio(audio_bytes)

        # Process the audio with pydub to add silence as needed
        original_audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        modified_audio = AudioSegment.silent(duration=0)  # Start with an empty audio segment

        sentences = script.splitlines()
        char_index = 0
        
        for sentence in sentences:
            sentence_start_time = response_dict['alignment']['character_start_times_seconds'][char_index]
            sentence_end_time = response_dict['alignment']['character_end_times_seconds'][char_index + len(sentence) - 1]
            duration = sentence_end_time - sentence_start_time

            # Extract the audio for this sentence
            start_ms = sentence_start_time * 1000
            end_ms = sentence_end_time * 1000
            sentence_audio = original_audio[start_ms:end_ms]

            # Calculate the silence duration needed to make the total 5 seconds
            silence_duration = max(0, 5000 - int(duration * 1000))

            # Add sentence audio and then add the calculated silence
            modified_audio += sentence_audio + AudioSegment.silent(duration=silence_duration)
            
            char_index += len(sentence) + 1  # +1 to account for the newline character
        
        # # Export the modified audio to a byte stream
        output_io = io.BytesIO()
        modified_audio.export(output_io, format="mp3")
        output_audio_bytes = output_io.getvalue()

        # Upload modified audio to OSS
        audio_name = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1, 100)) + '.mp3'
        oss_bucket.put_object(audio_name, output_audio_bytes)
        
        st.session_state.audio_dict = {
            'audio_name': audio_name,
            'audio_url': oss_bucket.sign_url('GET', audio_name, 180),
            'narrator_timestamp': [5.0 for _ in sentences],  # Each sentence is now 5 seconds long
        }
        st.audio(output_audio_bytes)


def generate_ai_video():
    if st.session_state.group != "1":
        # Prepare the scene's script
        script = st.session_state.script+'\n'
        pattern = r'\[Scene: last (\d+) seconds: (.*?)\]'
        matches = re.findall(pattern, script)
        formatted_scenes = [[int(seconds), description] for seconds, description in matches]
        if len(formatted_scenes) == len(st.session_state.audio_dict['narrator_timestamp']):
            formatted_scenes = [[int(st.session_state.audio_dict['narrator_timestamp'][i]), description] for i, [seconds, description] in enumerate(formatted_scenes)]
        
        # Generate Video with ai video api
        url = "https://api.aivideoapi.com/runway/generate/text"

        responses = []
        response_urls = []

        for seconds, description in formatted_scenes:
            payload = {
            "text_prompt": "masterpiece, cinematic, "+ description,
            "model": "gen3",
            "width": 1344,
            "height": 768,
            "motion": 5,
            "seed": 0,
            "upscale": True,
            "interpolate": True,
            "callback_url": "",
            "time": int(seconds)
            }

        
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": st.secrets['aivideoapi_token'],
            }

            response = requests.post(url, json=payload, headers=headers)
            responses.append(response.json())
        
        video_urls = []

        for response in responses:
            uuid = response['uuid']
            status_url = f"https://api.aivideoapi.com/status?uuid={uuid}"

            headers_status = {
                "accept": "application/json",
                "Authorization": st.secrets['aivideoapi_token']
            }

            while True:
                response_status = requests.get(status_url, headers=headers_status)
                status_json = response_status.json()
                
                if status_json["status"] == "success":
                    video_urls.append(status_json["url"])
                    break
                elif status_json["status"] in ["in queue", "submitted"]:
                    time.sleep(5)  # Wait and recheck the status
                else:
                    print(f"Error generating video: {status_json}")
                    break

        

def add_audio_to_video():
    audio_url = st.session_state.audio_dict['audio_url']
    video_url = st.session_state.video_url
    creatomate_options = {
        # The ID of the template that you created in the template editor
        'template_id': st.secrets['creatomate_template_id'],

        # Modifications that you want to apply to the template
        'modifications': {
            'Video': video_url,
            "Audio": audio_url,
            "BGM": "https://www.chosic.com/wp-content/uploads/2021/06/Sweet(chosic.com).mp3"
        },
    }

    creatomate_response = requests.post(
        'https://api.creatomate.com/v1/renders',
        headers={
            'Authorization': f"Bearer {st.secrets['creatomate_token']}",
            'Content-Type': 'application/json',
        },
        json=creatomate_options
    )

    final_clip_json =creatomate_response.content.decode('utf8').replace("'", '"')
    final_clip_json = json.loads(final_clip_json)
    final_clip = final_clip_json[0]['url']

    while requests.get(final_clip).status_code == 404:
        time.sleep(1)
    st.video(final_clip)
    #st.write(video_url['videos'][0]['resultUrl'])
    index = get_last_index()
    st.session_state.responses_df.loc[index, 'Video_url'] = final_clip

#     return url
