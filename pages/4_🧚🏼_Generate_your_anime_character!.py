import streamlit as st
import torch
from diffusers import DiffusionPipeline
from PIL import Image
import os

# Set the environment variable
os.environ["HUGGINGFACE_HUB_TOKEN"] = st.secrets["HUGGINGFACE_TOKEN"]

st.set_page_config(page_title="Generate Your Anime Character !", page_icon="🧚🏼", layout="wide")

st.markdown("# Generate Your Own Anime Character 自分だけのアニメキャラクターを生成する ？ 🪄")
st.sidebar.header("Let Your words be a reality ! 🪄")

logo_path = "/images/streami.png"
# Display the logo image in the sidebar
st.sidebar.image(logo_path, use_column_width=True)

# Check if CUDA is available and use it if possible
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the pre-trained model (cached to improve performance)
@st.cache_resource
def load_model():
    pipe = DiffusionPipeline.from_pretrained(
        "Ojimi/anime-kawai-diffusion",
        use_auth_token=st.secrets["HUGGINGFACE_TOKEN"]  # Authentication token from Streamlit secrets
    )
    pipe = pipe.to(device)
    return pipe

pipe = load_model()

# Main content input field and button
st.write("Enter a creative prompt above and click 'Generate Image' to see the result!")
prompt = st.text_input("Enter your anime prompt:", "1girl, animal ears, long hair, solo, cat ears, choker, bare shoulders, red eyes, fang, looking at viewer, animal ear fluff, upper body, black hair, blush, closed mouth, off shoulder, bangs, bow, collarbone")
negative_prompt = st.text_input("Enter negative prompt (optional):", "lowres, bad anatomy")

# Button to generate the image
generate_button = st.button("Generate Image")

if generate_button:
    with st.spinner("Generating your anime character... ⏳"):
        try:
            # Generate the image
            image = pipe(prompt, negative_prompt=negative_prompt).images[0]
            
            # Display the image with limited width
            st.image(image, caption="Generated Anime Character", use_column_width=False, width=400)
            st.success("Image generation completed!")
            
            # Save and add a download option
            img_path = "generated_image.png"
            image.save(img_path)
            with open(img_path, "rb") as file:
                st.download_button(
                    label="Download Image",
                    data=file,
                    file_name="anime_character.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")