import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Gemini API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="YouTube Myanmar Recap",
    page_icon="🎬"
)

st.title("🎬 YouTube Myanmar Recap")

url = st.text_input("YouTube URL")

# Extract Video ID
def get_video_id(url):
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path[1:]

    return parse_qs(parsed.query).get("v", [""])[0]


# Transcript
def get_transcript(video_id):

    transcript = YouTubeTranscriptApi.get_transcript(
        video_id
    )

    text = " ".join(
        [x["text"] for x in transcript]
    )

    return text


# Long Video Support
def chunk_text(text, size=10000):

    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])

    return chunks


# Summary
def summarize(text):

    prompt = f"""
You are an expert Burmese content creator.

Convert the transcript into a natural Burmese recap script.

Requirements:

- Natural Burmese
- Easy to understand
- Storytelling style
- Keep important points
- No direct translation
- Suitable for YouTube narration

Transcript:

{text}
"""

    response = model.generate_content(prompt)

    return response.text


def create_recap(transcript):

    chunks = chunk_text(transcript)

    partials = []

    for chunk in chunks:
        partials.append(
            summarize(chunk)
        )

    merged = "\n".join(partials)

    final_prompt = f"""
Combine all summaries below into one complete Burmese recap script.

{merged}
"""

    final = model.generate_content(
        final_prompt
    )

    return final.text


if st.button("Generate Recap"):

    if url:

        with st.spinner("Processing..."):

            try:

                video_id = get_video_id(url)

                transcript = get_transcript(video_id)

                recap = create_recap(
                    transcript
                )

                st.success("Done")

                st.text_area(
                    "Myanmar Recap Script",
                    recap,
                    height=500
                )

                st.download_button(
                    "Download Script",
                    recap,
                    file_name="recap.txt"
                )

            except Exception as e:

                st.error(str(e))
