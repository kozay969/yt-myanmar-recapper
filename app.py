import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os, re

# API Key configuration
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key မတွေ့ပါ။")

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    try:
        t_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'my'])
        return " ".join([item['text'] for item in t_list])
    except Exception as e:
        return f"Error: Transcript ဆွဲထုတ်လို့မရပါ - {str(e)}"

def generate_myanmar_recap(transcript_text):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Please recap the following video transcript into natural, engaging Myanmar language. Create a summary and key takeaways: {transcript_text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

# UI App
st.title("🎥 YT Myanmar Recapper")
st.write("YouTube Video အနှစ်ချုပ် စကရစ်ဖ် ထုတ်ပေးမည့် App")

video_url = st.text_input("YouTube URL ကို ထည့်ပါ:")

if st.button("Recap လုပ်မယ် ✨"):
    if video_url:
        video_id = get_video_id(video_url)
        if video_id:
            st.image(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg", width=300)
            
            with st.spinner("စာသားများ ဆွဲထုတ်နေသည်...⏳"):
                transcript = get_youtube_transcript(video_id)
            
            if "Error" in transcript:
                st.error(transcript)
            else:
                with st.spinner("မြန်မာလို အနှစ်ချုပ်နေသည်...🤖✍️"):
                    recap_result = generate_myanmar_recap(transcript)
                st.success("ပြီးပါပြီ။ ✨")
                st.subheader("📝 မြန်မာလို အနှစ်ချုပ်")
                st.markdown(recap_result)
        else:
            st.error("မှန်ကန်သော YouTube Link ဖြစ်ပါစေ။")
            
