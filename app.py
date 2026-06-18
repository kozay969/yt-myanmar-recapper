import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# -----------------------
# Streamlit Config
# -----------------------

st.set_page_config(
    page_title="YouTube Myanmar Recap",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 YouTube Myanmar Recap")

# -----------------------
# Gemini API
# -----------------------

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# -----------------------
# URL Parser
# -----------------------

def get_video_id(url):
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    return parse_qs(
        parsed.query
    ).get(
        "v",
        [""]
    )[0]

# -----------------------
# Transcript Fetch
# -----------------------

def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    text = " ".join(
        item.text
        for item in transcript
    )

    return text

# -----------------------
# Chunking
# -----------------------

def chunk_text(
    text,
    chunk_size=15000
):
    chunks = []

    for i in range(
        0,
        len(text),
        chunk_size
    ):
        chunks.append(
            text[i:i + chunk_size]
        )

    return chunks

# -----------------------
# Summary
# -----------------------

def summarize_chunk(
    text,
    length,
    style
):

    prompt = f"""
You are a professional Burmese YouTube creator.

Create:

1. Viral Title
2. Thumbnail Text
3. Burmese Recap Script
4. Description
5. Hashtags

Style:
{style}

Length:
{length}

Rules:

- Natural Burmese language
- Storytelling tone
- Easy to narrate
- No direct translation
- Keep important facts
- Strong opening hook

Transcript:

{text}

Return exactly in this format:

TITLE:
...

THUMBNAIL:
...

SCRIPT:
...

DESCRIPTION:
...

HASHTAGS:
...
"""

    response = model.generate_content(
        prompt
    )

    return response.text

# -----------------------
# Final Recap
# -----------------------

def create_recap(
    transcript,
    length,
    style
):

    chunks = chunk_text(
        transcript
    )

    partials = []

    for chunk in chunks:
        partials.append(
            summarize_chunk(
                chunk,
                length,
                style
            )
        )

    merged = "\n\n".join(
        partials
    )

    final_prompt = f"""
Combine everything below into ONE final result.

{merged}

Return:

TITLE:
...

THUMBNAIL:
...

SCRIPT:
...

DESCRIPTION:
...

HASHTAGS:
...
"""

    final = model.generate_content(
        final_prompt
    )

    return final.text

# -----------------------
# UI
# -----------------------

url = st.text_input(
    "YouTube URL"
)

length = st.selectbox(
    "Script Length",
    [
        "Short",
        "Medium",
        "Long"
    ]
)

style = st.selectbox(
    "Style",
    [
        "Recap",
        "Storytelling",
        "Documentary",
        "News"
    ]
)

# -----------------------
# Generate
# -----------------------

if st.button(
    "Generate Recap"
):

    if not url:
        st.warning(
            "Please enter a YouTube URL."
        )
        st.stop()

    try:

        with st.spinner(
            "Getting transcript..."
        ):

            video_id = get_video_id(
                url
            )

            transcript = get_transcript(
                video_id
            )

        with st.spinner(
            "Generating recap..."
        ):

            result = create_recap(
                transcript,
                length,
                style
            )

        st.success(
            "Done!"
        )

        st.text_area(
            "Result",
            result,
            height=700
        )

        st.download_button(
            "Download",
            result,
            file_name="recap.txt"
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )
