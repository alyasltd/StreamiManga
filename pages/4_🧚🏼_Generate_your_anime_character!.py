import streamlit as st
import os
from huggingface_hub import InferenceClient
from PIL import Image
import io

st.set_page_config(page_title="Generate Your Anime Character!", page_icon="🧚🏼", layout="wide")

st.markdown("# Generate Your Own Anime Character 自分だけのアニメキャラクターを作ってみよう！🪄")
st.sidebar.header("Let Your words be a reality ! 🪄")

logo_path = "images/streami.png"
st.sidebar.image(logo_path, use_column_width=True)

# Load HF token safely from Streamlit secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

# Create inference client
client = InferenceClient(
    provider="nebius",
    api_key=HF_TOKEN,
)

MODEL_ID = "black-forest-labs/FLUX.1-schnell"

# Prompt inputs
st.write("Enter a creative prompt and click 'Generate Image' to see your anime character!")
prompt = st.text_input(
    "Enter your anime prompt:",
    "cute anime girl with cat ears, pastel colors, big sparkling eyes, soft shading"
)

if st.button("Generate Image"):
    with st.spinner("Generating your anime character... ⏳"):
        try:
            # Generate image using HF Nebius API
            image = client.text_to_image(prompt, model=MODEL_ID)

            # Display image
            st.image(image, caption="Generated Anime Character", width=400)

            # Download option
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button(
                label="Download Image",
                data=buf.getvalue(),
                file_name="anime_character.png",
                mime="image/png"
            )

            st.success("Image generation completed! ✨")

        except Exception as e:
            st.error(f"An error occurred: {e}")
