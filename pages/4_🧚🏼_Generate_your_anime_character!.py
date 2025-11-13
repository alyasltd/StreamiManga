import streamlit as st
import requests
import io
from PIL import Image

st.set_page_config(page_title="Generate Your Anime Character!", page_icon="🧚🏼", layout="wide")

st.markdown("# Generate Your Own Anime Character 自分だけのアニメキャラクターを作ってみよう！🪄")
st.sidebar.header("Let Your words be a reality ! 🪄")

# Sidebar logo
st.sidebar.image("images/streami.png", use_column_width=True)

# HuggingFace API Config
HF_TOKEN = st.secrets["HF_TOKEN"]  # <-- SAFE
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Function to call HF
def generate_image(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)

    # Check for JSON error response
    if response.headers.get("content-type") == "application/json":
        return None, response.json()

    return response.content, None


# Prompt input
prompt = st.text_input(
    "Enter your anime prompt:",
    "cute anime girl with cat ears, big sparkling eyes, pastel colors, soft glow"
)

# Generate button
if st.button("Generate Image"):
    with st.spinner("Generating your anime character... ⏳"):
        img_bytes, error = generate_image(prompt)

        if error:
            st.error("🚨 HuggingFace API Error:")
            st.code(error)
        else:
            # Convert bytes to image
            image = Image.open(io.BytesIO(img_bytes))

            # Display the image
            st.image(image, caption="Generated Anime Character", width=400)

            # Download button
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button(
                label="Download Image",
                data=buf.getvalue(),
                file_name="anime_character.png",
                mime="image/png"
            )

            st.success("Image generation completed! ✨")
