import streamlit as st
import yt_dlp
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

# YouTube ကနေ အသံဖိုင် သီးသန့်ဒေါင်းမည့် function
def download_youtube_audio(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            audio_path = f"downloads/{video_id}.m4a"
            return audio_path
    except Exception as e:
        return f"Error: {str(e)}"

# အသံဖိုင်ကို Gemini ထံပို့ပြီး မြန်မာလို အနှစ်ချုပ်ခိုင်းမည့် function
def generate_recap_from_audio(audio_path):
    try:
        st.write("အသံဖိုင်ကို AI ထံသို့ ပေးပို့နေသည်...🤖")
        # အသံဖိုင်ကို Gemini cloud ပေါ် တင်ခြင်း
        audio_file = genai.upload_file(path=audio_path)
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = """
        Listen to this audio carefully. Translate, breakdown and recap the entire content into natural, engaging, flowing, and professional Myanmar (Burmese) language.
        Format it beautifully with an 'အကျဉ်းချုပ် (Summary)' section and key insights in bullet points.
        """
        
        response = model.generate_content([audio_file, prompt])
        
        # ပြီးရင် ဖုန်း/Server ထဲက အသံဖိုင်ကို ပြန်ဖျက်ပစ်မယ်
        genai.delete_file(audio_file.name)
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

# UI App
st.title("🎥 YT Myanmar Voice Recapper")
st.write("စာတန်းထိုး မလိုတော့ပါ။ ဗီဒီယိုထဲက အသံကို နားထောင်ပြီး မြန်မာလို အနှစ်ချုပ်ပေးမည့်စနစ်")

video_url = st.text_input("YouTube URL ကို ထည့်ပါ:")

if st.button("Recap လုပ်မယ် ✨"):
    if video_url:
        video_id = get_video_id(video_url)
        if video_id:
            st.image(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg", width=300)
            
            # ဒေါင်းလုဒ်ဆွဲမယ့် Folder ဆောက်ခြင်း
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
                
            with st.spinner("ဗီဒီယိုထဲမှ အသံကို သီးသန့် ခွဲထုတ်နေသည်...⏳ (ဗီဒီယိုအရှည်ပေါ်မူတည်ပြီး အချိန်အနည်းငယ်ကြာနိုင်ပါသည်)"):
                audio_result = download_youtube_audio(video_url)
            
            if "Error" in audio_result:
                st.error(audio_result)
            else:
                with st.spinner("Gemini AI က အသံကို နားထောင်ပြီး မြန်မာလို အနှစ်ချုပ်နေသည်...🎧✍️"):
                    recap_result = generate_recap_from_audio(audio_result)
                
                st.success("ပြီးပါပြီ။ ✨")
                st.subheader("📝 မြန်မာလို အနှစ်ချုပ် စကရစ်ဖ်")
                st.markdown(recap_result)
        else:
            st.error("မှန်ကန်သော YouTube Link ဖြစ်ပါစေ။")
            
