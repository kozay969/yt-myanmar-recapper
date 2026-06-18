import streamlit as st
import google.generativeai as genai
import tempfile

st.set_page_config(
    page_title="Myanmar Video Recap",
    page_icon="🎬"
)

st.title("🎬 Myanmar Video Recap")

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

video_file = st.file_uploader(
    "Upload Video",
    type=["mp4","mov","mkv"]
)

if st.button("Generate Recap"):

    if video_file:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as tmp:

            tmp.write(
                video_file.read()
            )

            path = tmp.name

        with st.spinner(
            "Uploading video..."
        ):

            uploaded = genai.upload_file(
                path=path
            )

        prompt = """
Analyze this video and create:

1. Viral Title
2. Thumbnail Text
3. Burmese Recap Script
4. Description
5. Hashtags

Use natural Burmese language.
"""

        with st.spinner(
            "Generating..."
        ):

            response = model.generate_content(
                [uploaded, prompt]
            )

        result = response.text

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
