import streamlit as st
import pafy_tweaked as pafy
import google.generativeai as genai
import os, re, urllib.request

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

# YouTube ကနေ အသံ Stream URL ကို တိုက်ရိုက်ယူပြီး ဖိုင်ယာယီဒေါင်းမည့် function
def process_youtube_audio(url, video_id):
    try:
        video = pafy.new(url)
        best_audio = video.getbestaudio(preftype="m4a")
        audio_url = best_audio.url
        
        # ယာယီသိမ်းမည့်လမ်းကြောင်း
        local_filename = f"downloads_{video_id}.m4a"
        
        # Audio Stream ကို ဖိုင်အဖြစ် ခဏသိမ်းခြင်း
        urllib.request.urlretrieve(audio_url, local_filename)
        return local_filename
    except Exception as e:
        return f"Error: {str(e)}"

# အသံဖိုင်ကို Gemini ထံပို့ပြီး မြန်မာလို အနှစ်ချုပ်ခိုင်းမည့် function
def generate_recap_from_audio(audio_path):
    try:
        st.write("အသံဒေတာများကို AI ထံသို့ ချိတ်ဆက်နေသည်...🤖")
        audio_file = genai.upload_file(path=audio_path)
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = """
        Listen to this audio carefully. Translate, breakdown, and recap the entire content into natural, engaging, flowing, and professional Myanmar (Burmese) language.
        Format it beautifully with an 'အကျဉ်းချုပ် (Summary)' section and key insights in bullet points. Do not do word-for-word translation; make it sound like a great Myanmar script.
        """
        
        response = model.generate_content([audio_file, prompt])
        
        # အသုံးပြုပြီးသား ဖိုင်များကို Cloud ပေါ်နှင့် local ထဲမှ ပြန်ဖျက်ခြင်း
        genai.delete_file(audio_file.name)
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return response.text
    except Exception as e:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return f"AI Error: {str(e)}"

# UI App
st.title("🎥 YT Myanmar Stream Recapper")
st.write("ဗီဒီယိုထဲက အသံကို တိုက်ရိုက်နားထောင်ပြီး မြန်မာလို အနှစ်ချုပ်ပေးမည့်စနစ်အသစ်")

video_url = st.text_input("YouTube URL ကို ထည့်ပါ:")

if st.button("Recap လုပ်မယ် ✨"):
    if video_url:
        video_id = get_video_id(video_url)
        if video_id:
            st.image(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg", width=300)
            
            with st.spinner("ဗီဒီယိုထဲမှ အသံလမ်းကြောင်းကို ရှာဖွေနေသည်...⏳"):
                audio_result = process_youtube_audio(video_url, video_id)
            
            if "Error" in audio_result:
                st.error("YouTube က လှမ်းပိတ်ထားသဖြင့် ဒေါင်းလုဒ်ဆွဲ၍မရပါ။ အခြားလင့်ခ်တစ်ခုဖြင့် ပြန်စမ်းကြည့်ပေးပါ။")
                st.debug(audio_result)
            else:
                with st.spinner("Gemini AI က အသံကို နားထောင်ပြီး မြန်မာလို အနှစ်ချုပ်နေသည်...🎧✍️"):
                    recap_result = generate_recap_from_audio(audio_result)
                
                st.success("ပြီးပါပြီ။ ✨")
                st.subheader("📝 မြန်မာလို အနှစ်ချုပ် စကရစ်ဖ်")
                st.markdown(recap_result)
        else:
            st.error("မှန်ကန်သော YouTube Link ဖြစ်ပါစေ။")
            
