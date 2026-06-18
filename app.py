import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Local မှာစမ်းရင် .env ကို သုံးဖို့
load_dotenv()

# Google Gemini API Config (Streamlit Cloud ပေါ်တင်ရင် Secrets ကနေ ဖတ်မယ်)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key မတွေ့ပါ။ ကျေးဇူးပြု၍ GEMINI_API_KEY ကို ထည့်သွင်းပေးပါ။")

# YouTube Link ကနေ Video ID ကို ဆွဲထုတ်တဲ့ Function
def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# YouTube Transcript (စာသား) ဆွဲထုတ်တဲ့ Function
def get_youtube_transcript(video_id):
    try:
        # ဒီနေရာမှာ အရင်က သတ်ပုံမှားသွားတဲ့ get_transcript ကို သေချာပြင်ထားပါတယ်
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'my'])
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        return f"Error: Transcript ဆွဲထုတ်လို့မရပါ (ဗီဒီယိုမှာ Captions ပိတ်ထားတာ ဖြစ်နိုင်ပါတယ်) - {str(e)}"

# Gemini AI သုံးပြီး မြန်မာလို Recap လုပ်ပေးမယ့် Function
def generate_myanmar_recap(transcript_text):
    try:
        # ဗီဒီယိုအရှည်တွေအတွက် gemini-1.5-flash က အကောင်းဆုံးပါ
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an expert content summarizer and storyteller. Translate and recap the following YouTube video transcript into natural, engaging, flowing, and professional Myanmar (Burmese) language. 
        
        Guidelines:
        1. Don't do word-for-word translation. Make it sound like a natural Myanmar video script or detailed story recap.
        2. Create an "အကျဉ်းချုပ် (Summary)" section at the top.
        3. Break down key insights, events, or takeaways into clear bullet points with headings.
        4. Use conversational but polite Myanmar tone. Avoid robotic translations.
        
        Transcript:
        {transcript_text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- Streamlit UI Design ---
st.set_page_config(page_title="YouTube Myanmar Recapper", page_icon="🎥", layout="centered")

st.title("🎥 YouTube Video Myanmar
         
