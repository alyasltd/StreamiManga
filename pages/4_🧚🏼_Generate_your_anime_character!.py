import streamlit as st
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline
import os

st.set_page_config(page_title="Generate Your Anime Character !", page_icon="🧚🏼", layout="wide")

st.markdown("# Generate Your Own Anime Character 自分だけのアニメキャラクターを作ってみよう！🪄")
st.sidebar.header("Let Your words be a reality ! 🪄")

logo_path = "images/streami.png"
st.sidebar.image(logo_path, use_column_width=True)

# Choose model (tiny model to fit Streamlit Cloud)
MODEL_ID = "lllyasviel/sd-tiny"

@st.cache_resource
def load_model():
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32
    ).to("cpu")
    return pipe

# Load once
pipe = load_model()

# Prompt inputs
st.write("Enter a creative prompt above and click 'Generate Image' to see the result!")
prompt = st.text_input("Enter your anime prompt:", "1 girl, cat ears, black hair, red eyes, cute anime style")
negative_prompt = st.text_input("Enter negative prompt (optional):", "lowres, bad anatomy")

# Button
if st.button("Generate Image"):
    with st.spinner("Generating your anime character... ⏳"):
        try:
            # Generate
            result = pipe(prompt, negative_prompt=negative_prompt)
            image = result.images[0]

            # Display
            st.image(image, caption="Generated Anime Character", width=400)

            # Save + download
            img_path = "generated_image.png"
            image.save(img_path)
            with open(img_path, "rb") as f:
                st.download_button(
                    label="Download Image",
                    data=f,
                    file_name="anime_character.png",
                    mime="image/png"
                )

            st.success("Image generation completed!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
