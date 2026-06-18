import streamlit as st
import tempfile
import time
from google import genai

# --------------------
# PAGE CONFIG
# --------------------

st.set_page_config(
    page_title="Myanmar Video Recap",
    page_icon="🎬"
)

st.title("🎬 Myanmar Video Recap")

# --------------------
# GEMINI CLIENT
# --------------------

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# --------------------
# OPTIONS
# --------------------

length = st.selectbox(
    "Script Length",
    ["Short", "Medium", "Long"]
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

video_file = st.file_uploader(
    "Upload Video",
    type=["mp4", "mov", "mkv"]
)

# --------------------
# GENERATE
# --------------------

if st.button("Generate Recap"):

    if video_file is None:
        st.warning("Upload a video first.")
        st.stop()

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as tmp:

            tmp.write(video_file.read())
            video_path = tmp.name

        st.info("Uploading video...")

        uploaded_file = client.files.upload(
            file=video_path
        )

        status_box = st.empty()

        while True:

            file_info = client.files.get(
                name=uploaded_file.name
            )

            state = file_info.state.name

            status_box.info(
                f"Status: {state}"
            )

            if state == "ACTIVE":
                status_box.success(
                    "Video ready!"
                )
                break

            if state == "FAILED":
                st.error(
                    "Video processing failed."
                )
                st.stop()

            time.sleep(5)

        prompt = f"""
Analyze this video and create:

1. Viral YouTube Title
2. Thumbnail Text
3. Burmese Recap Script
4. Description
5. Hashtags

Style:
{style}

Length:
{length}

Requirements:
- Natural Burmese language
- Storytelling style
- Easy narration
- Strong opening hook
- Keep important details

Return format:

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

        with st.spinner(
            "Generating recap..."
        ):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    file_info,
                    prompt
                ]
            )

        result = response.text

        st.success("Done!")

        st.text_area(
            "Result",
            result,
            height=700
        )

        st.download_button(
            "Download Script",
            result,
            file_name="myanmar_recap.txt"
        )

    except Exception as e:

        st.error(str(e))
