import streamlit as st
import pandas as pd
import random
from PIL import Image, ImageFilter
import requests
from io import BytesIO
import time

# Charger le fichier CSV des personnages
data = pd.read_csv("projet/data/anime_planet_characters.csv")

def blur_image(url):
    """Floute une image depuis son URL."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return blurred_img

# Initialiser la session pour stocker l'état du jeu
if 'quiz_started' not in st.session_state:
    st.session_state.update({
        'quiz_started': False,
        'anime_selected': False,
        'question_index': 0,
        'score': 0,
        'current_character': None,
        'selected_anime': None,
        'filtered_data': data,
        'options': None,
        'used_characters': []
    })

# Écran de sélection de l'anime
if not st.session_state.anime_selected:
    st.title("Bienvenue dans le Quiz Anime !")
    st.write("Sélectionnez un anime pour commencer le quiz.")
    
    animes = ["Tous"] + list(data['Manga Associé'].dropna().unique())
    selected_anime = st.selectbox("Choisir un anime", animes)
    start_quiz = st.button("Commencer le quiz")
    
    if start_quiz:
        # Mettre à jour les données filtrées et marquer l'anime comme sélectionné
        if selected_anime != "Tous":
            st.session_state.filtered_data = data[data['Manga Associé'] == selected_anime]
            st.session_state.selected_anime = selected_anime
        else:
            st.session_state.filtered_data = data
            st.session_state.selected_anime = None
        st.session_state.anime_selected = True
        st.session_state.quiz_started = True

# Quiz de 5 questions
if st.session_state.quiz_started and st.session_state.anime_selected:
    # Sélection d'un personnage pour chaque question
    if st.session_state.question_index < 5:
        if st.session_state.current_character is None:
            # Filtrer les données pour ne pas réutiliser les personnages déjà utilisés
            available_data = st.session_state.filtered_data[
                ~st.session_state.filtered_data['Nom'].isin(st.session_state.used_characters)
            ]
            st.session_state.current_character = available_data.sample(1).iloc[0]
            # Ajouter le personnage utilisé à la liste des personnages utilisés
            st.session_state.used_characters.append(st.session_state.current_character['Nom'])
        
        character = st.session_state.current_character
        blurred_image = blur_image(character['Image'])

        # Affichage de la question et de l'image floutée
        st.subheader(f"Question {st.session_state.question_index + 1} / 5")
        st.image(blurred_image, caption="Qui suis-je ?")

        # Préparation des options de réponse, mais seulement une fois
        if st.session_state.options is None:
            options = st.session_state.filtered_data['Nom'].tolist()
            
            # Si on a moins de 4 personnages, inclure tous les noms possibles
            if len(options) > 4:
                options = [character['Nom']] + random.sample([name for name in options if name != character['Nom']], 3)
            else:
                options = [character['Nom']] + [name for name in options if name != character['Nom']]

            random.shuffle(options)
            st.session_state.options = options

        # Interface utilisateur pour le choix de réponse
        guess = st.radio("Choisissez le personnage:", st.session_state.options, key=st.session_state.question_index)
        
        if st.button("Valider"):
            # Vérification de la réponse
            if guess == character['Nom']:
                st.success("Bonne réponse !")
                st.session_state.score += 1
                time.sleep(2)
            else:
                st.error(f"Mauvaise réponse. La bonne réponse était {character['Nom']}.")
                time.sleep(2)
            # Préparer la question suivante
            st.session_state.question_index += 1
            st.session_state.current_character = None
            st.session_state.options = None  # Reset options for the next question
            st.rerun()
            
        # Ajouter le bouton pour arrêter le quiz
        if st.button("Arrêter le quiz"):
            st.session_state.update({
                'quiz_started': False,
                'anime_selected': False,
                'question_index': 0,
                'score': 0,
                'current_character': None,
                'selected_anime': None,
                'filtered_data': data,
                'options': None,
                'used_characters': []
            })
            st.success("Quiz arrêté.")
            st.rerun()
    
    # Fin du quiz
    else:
        st.write(f"Partie terminée ! Vous avez obtenu un score de {st.session_state.score} / 5.")
        
        # Réinitialiser les variables pour jouer à nouveau
        if st.button("Rejouer"):
            st.session_state.update({
                'quiz_started': False,
                'anime_selected': False,
                'question_index': 0,
                'score': 0,
                'current_character': None,
                'selected_anime': None,
                'filtered_data': data,
                'options': None,
                'used_characters': []
            })
            st.rerun() 