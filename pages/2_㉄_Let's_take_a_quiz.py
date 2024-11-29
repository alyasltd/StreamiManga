import streamlit as st
import pandas as pd
import random
from PIL import Image, ImageFilter
import requests
from io import BytesIO
import time

st.set_page_config(page_title="Let's Take a Quiz!", page_icon="㉄")

st.markdown("# Let's Take a Quiz クイズをやってみましょう！㉄")
st.sidebar.header("How well do you know anime characters? 😶‍🌫️")

# Add an explanatory text at the top of the page
st.markdown("""
Welcome to the **Anime Character Quiz** page! 🌟 

In this interactive quiz, you'll test your knowledge of popular anime characters. Here's how it works:

- **Choose an anime**: Select your favorite anime or pick "All" to include characters from a variety of series.
- **Guess the character**: You'll be presented with a blurred image of a character and multiple-choice options to identify them.
- **Hints available**: If you're unsure, click the "Hint" button to reveal traits or characteristics about the character.
- **Score tracking**: The quiz consists of 5 questions, and your score will be displayed at the end.

Are you ready to show off your anime knowledge and have some fun? Let’s start! 🤓✨
""")

logo_path = "StreamiManga/images/streami.png"
st.sidebar.image(logo_path, use_column_width=True)

# Load the CSV file of characters
data = pd.read_csv("StreamiManga/data/character/anime_planet_characters.csv")

# Function to blur the image from a URL
def blur_image(url):
    """Floute une image depuis son URL."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=10))
    return blurred_img

# Initialize session state variables
if 'quiz_started' not in st.session_state:
    st.session_state.update({
        'quiz_started': False,
        'anime_selected': False,
        'question_index': 0,
        'score': 0,
        'current_character': None,
        'selected_anime': None,
        'filtered_data': None,
        'options': None,
        'used_characters': [],
        'show_selectbox': True,
        'selected_option': None,
        'show_hint': False
    })

# Function to handle selectbox submission
def submit_action(option):
    st.session_state.show_selectbox = False
    st.session_state.selected_option = option
    st.session_state.anime_selected = True
    st.session_state.quiz_started = True
    if option != "All":
        st.session_state.filtered_data = data[data['Manga Associé'] == option]
    else:
        st.session_state.filtered_data = data

# Display selectbox if not hidden
if st.session_state.show_selectbox:
    animes = ["All"] + list(data['Manga Associé'].dropna().unique())
    selected_anime = st.selectbox("Choose an anime", animes)
    submit_button = st.button("Start the Quiz", on_click=submit_action, args=(selected_anime,))

# Display the selected option and start the quiz
if not st.session_state.show_selectbox and st.session_state.anime_selected:
    st.write(f"**Selected anime**: {st.session_state.selected_option}")

    # Quiz logic for 5 questions
    if st.session_state.question_index < 5:
        if st.session_state.current_character is None:
            available_data = st.session_state.filtered_data[
                ~st.session_state.filtered_data['Nom'].isin(st.session_state.used_characters)
            ]
            st.session_state.current_character = available_data.sample(1).iloc[0]
            st.session_state.used_characters.append(st.session_state.current_character['Nom'])
        
        character = st.session_state.current_character
        blurred_image = blur_image(character['Image'])

        # Display the quiz card using columns
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(blurred_image, caption="Who Am I ?", use_column_width=True)

        with col2:
            st.subheader(f"Question {st.session_state.question_index + 1} / 5")
            if st.session_state.options is None:
                options = st.session_state.filtered_data['Nom'].tolist()
                if len(options) > 4:
                    options = [character['Nom']] + random.sample([name for name in options if name != character['Nom']], 3)
                else:
                    options = [character['Nom']] + [name for name in options if name != character['Nom']]
                random.shuffle(options)
                st.session_state.options = options

            guess = st.radio("Guess the character:", st.session_state.options, key=st.session_state.question_index)

            # Bouton Indice (Hint)
            if st.button("Hint", key=f"hint_{st.session_state.question_index}"):
                st.session_state.show_hint = True

            if st.session_state.show_hint:
                traits = character['Tags']
                st.info(f"Hint: {traits}")
            
            if st.button("Next"):
                if guess == character['Nom']:
                    st.success("Correct!")
                    st.session_state.score += 1
                    time.sleep(2)
                else:
                    st.error(f"Wrong answer. The correct answer was {character['Nom']}.")
                    time.sleep(2)
                st.session_state.question_index += 1
                st.session_state.current_character = None
                st.session_state.options = None
                st.session_state.show_hint = False
                st.rerun()

            if st.button("Stop the Quiz"):
                st.session_state.update({
                    'quiz_started': False,
                    'anime_selected': False,
                    'question_index': 0,
                    'score': 0,
                    'current_character': None,
                    'selected_anime': None,
                    'filtered_data': None,
                    'options': None,
                    'used_characters': [],
                    'show_selectbox': True,
                    'selected_option': None,
                    'show_hint': False
                })
                st.success("Quiz stopped.")
                st.rerun()

    else:
        st.write(f"Quiz over! Your score is {st.session_state.score} / 5.")
        if st.button("Play Again"):
            st.session_state.update({
                'quiz_started': False,
                'anime_selected': False,
                'question_index': 0,
                'score': 0,
                'current_character': None,
                'selected_anime': None,
                'filtered_data': None,
                'options': None,
                'used_characters': [],
                'show_selectbox': True,
                'selected_option': None,
                'show_hint': False
            })
            st.rerun()