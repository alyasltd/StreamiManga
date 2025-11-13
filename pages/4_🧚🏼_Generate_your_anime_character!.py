import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Generate Your Anime Character !", page_icon="🧚🏼", layout="wide")

st.markdown("# Generate Your Own Anime Character 自分だけのアニメキャラクターを作ってみよう！🪄")
st.sidebar.header("Let Your words be a reality ! 🪄")

logo_path = "images/streami.png"
st.sidebar.image(logo_path, use_column_width=True)

# HuggingFace API
HF_API_KEY = st.secrets["HF_API_KEY"]  # ← SAFE
API_URL = "https://api-inference.huggingface.co/models/lllyasviel/sd-tiny"

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def generate_image(prompt: str, negative_prompt: str = ""):
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# User inputs
prompt = st.text_input("Enter your anime prompt:", "1 girl, cat ears, black hair, red eyes, cute anime style")
negative_prompt = st.text_input("Enter negative prompt (optional):", "lowres, bad anatomy")

if st.button("Generate Image"):
    with st.spinner("Generating your anime character... ⏳"):
        try:
            img_bytes = generate_image(prompt, negative_prompt)
            image = Image.open(io.BytesIO(img_bytes))

            st.image(image, caption="Generated Anime Character", width=400)

            # Download
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button(
                label="Download Image",
                data=buf.getvalue(),
                file_name="anime_character.png",
                mime="image/png"
            )

            st.success("Image generation completed!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
