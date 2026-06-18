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
        # အင်္ဂလိပ်စာသား (သို့) အလိုအလျောက်ပြောင်းထားတဲ့ စာသားကို ယူမယ်
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'my'])
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        return f"Error: Transcript ဆွဲထုတ်လို့မရပါ (ဗီဒီယိုမှာ Captions ပိတ်ထားတာ ဖြစ်နိုင်ပါတယ်) - {str(e)}"

# Gemini AI သုံးပြီး မြန်မာလို Recap လုပ်ပေးမယ့် Function
def generate_myanmar_recap(transcript_text):
    try:
        # ဗီဒီယိုအရှည်တွေအတွက် gemini-1.5-flash သို့မဟုတ် gemini-1.5-pro က အကောင်းဆုံးပါ
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an expert content summarizer. Translate and recap the following YouTube video transcript into natural, engaging, and professional Myanmar (Burmese) language. 
        
        Guidelines:
        1. Don't do literal translation. Make it sound like a natural Myanmar script/storytelling.
        2. Create a "Summary" section at the top.
        3. Break down key takeaways into bullet points with headings.
        4. Use clear paragraphs.
        
        Transcript:
        {transcript_text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- Streamlit UI Design ---
st.set_page_config(page_title="YouTube Myanmar Recapper", page_icon="🎥", layout="centered")

st.title("🎥 YouTube Video Myanmar Recapper")
st.write("YouTube Link ထည့်လိုက်ရုံနဲ့ ဗီဒီယိုတစ်ခုလုံးရဲ့ အနှစ်ချုပ်ကို သဘာဝကျတဲ့ မြန်မာလို ဖတ်ရှုနိုင်ပါပြီ။")

# User Input
video_url = st.text_input("YouTube Video URL ကို ဒီမှာ ထည့်ပါ:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Recap လုပ်မယ် ✨"):
    if video_url:
        video_id = get_video_id(video_url)
        
        if video_id:
            # YouTube Thumbnail ပြသခြင်း
            st.image(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg", width=400)
            
            with st.spinner("ဗီဒီယို စာသားများကို ဆွဲထုတ်နေသည်...⏳"):
                transcript = get_youtube_transcript(video_id)
            
            if "Error" in transcript:
                st.error(transcript)
            else:
                with st.spinner("Gemini AI က မြန်မာလို သဘာဝကျအောင် အနှစ်ချုပ်နေသည်...🤖✍️"):
                    recap_result = generate_myanmar_recap(transcript)
                
                st.success("ပြီးပါပြီ။ ✨")
                st.subheader("📝 မြန်မာလို အနှစ်ချုပ် စကရစ်ဖ်")
                st.markdown(recap_result)
        else:
            st.error("မှန်ကန်သော YouTube Link ဖြစ်ပါစေ။")
    else:
        st.warning("ကျေးဇူးပြု၍ Link တစ်ခုခု ထည့်ပေးပါ။")
      
