import streamlit as st
import torch
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
from PIL import Image
import os
from huggingface_hub import login
login()

st.set_page_config(page_title="Generate Your Anime Character !", page_icon="🧚🏼", layout="wide")

st.markdown("# Generate Your Own Anime Character 自分だけのアニメキャラクターを生成する ？ 🪄")
st.sidebar.header("Let Your words be a reality ! 🪄")

logo_path = "images/streami.png"  
# Display the logo image in the sidebar
st.sidebar.image(logo_path, use_column_width=True)

# Check if CUDA is available and use it if possible
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the pre-trained model (cached to improve performance)
@st.cache_resource
def load_model():
    base_model = "Linaqruf/animagine-xl"
    lora_model_id = "Linaqruf/pastel-anime-xl-lora"
    lora_filename = "pastel-anime-xl.safetensors"
    
    pipe = StableDiffusionXLPipeline.from_pretrained(
        base_model,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
        variant="fp16"
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.to(device)
    
    # Load the LoRA weights
    pipe.load_lora_weights(lora_model_id, weight_name=lora_filename)
    return pipe

pipe = load_model()

# Main content input field and button
st.write("Enter a creative prompt above and click 'Generate Image' to see the result!")
prompt = st.text_input("Enter your anime prompt:", "face focus, blond, blue eyes, upper body")
negative_prompt = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

# Button to generate the image
generate_button = st.button("Generate Image")

if generate_button:
    with st.spinner("Generating your anime character... ⏳"):
        image = pipe(
            prompt,
            negative_prompt=negative_prompt,
            width=512,
            height=512,
            guidance_scale=12,
            num_inference_steps=50
        ).images[0]
        
        # Display the image with limited width
        st.image(image, caption="Generated Anime Character", use_column_width=False, width=400)
        st.success("Image generation completed!")
