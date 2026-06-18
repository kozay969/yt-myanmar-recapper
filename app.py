import streamlit as st
import youtube_transcript_api
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
        # Transcript list ကို အရင်ဆွဲထုတ်မယ်
        transcript_list = youtube_transcript_api.YouTubeTranscriptApi.list_transcripts(video_id)
        
        # ၁။ လူကိုယ်တိုင် ထည့်ထားတဲ့ (Official) အင်္ဂလိပ် သို့ မြန်မာ စာတန်းထိုးကို အရင်ရှာမယ်
        try:
            t_data = transcript_list.find_transcript(['en', 'my']).fetch()
        except:
            # ၂။ မရှိရင် အလိုအလျောက် ဖန်တီးထားတဲ့ (Auto-generated) အင်္ဂလိပ် စာတန်းထိုးကို ရှာမယ်
            try:
                t_data = transcript_list.find_generated_transcript(['en']).fetch()
            except:
                # ၃။ လုံးဝမရရင် ရှိတဲ့ ပထမဆုံး စာတန်းထိုးကို ယူမယ်
                t_data = transcript_list.find_transcript([]).fetch()
                
        return " ".join([item['text'] for item in t_data])
    except Exception as e:
        return f"Error: Transcript ဆွဲထုတ်လို့မရပါ - {str(e)}"

def generate_myanmar_recap(transcript_text):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Prompt ကို ပိုပြီး ရှင်းရှင်းလင်းလင်း ပြင်ထားပါတယ်
        prompt = f"""
        You are an expert storyteller. Please breakdown, summarize and recap the following video transcript into very natural, flowing, and engaging Myanmar (Burmese) language.
        Format it with a main summary and key highlights in bullet points.
        
        Transcript:
        {transcript_text}
        """
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
