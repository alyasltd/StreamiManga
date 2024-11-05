import streamlit as st
import requests
import time

# Configuration de la page
st.set_page_config(page_title="Page d'accueil - Animés", layout="wide")

# CSS personnalisé pour le fond noir, les styles, l'espacement, et un podium amélioré
st.markdown(
    """
    <style>
    body {
        background-color: #000;
        color: #fff;
    }
    .anime-container {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        background-color: #1a1a1a;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        gap: 20px;
        position: relative;
        width: 80%;
        margin: auto;
    }
    .anime-details {
        flex: 2;
        text-align: left;
    }
    .anime-image {
        flex: 1;
        text-align: center;
    }
    .anime-image img {
        width: 100%;
        max-width: 500px;
        height: auto;
        border: 2px solid #555;
        border-radius: 10px;
    }
    .anime-trailer {
        margin-top: 20px;
    }
    .top3-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 30px;
        margin-top: 80px; /* Espace plus grand entre le carrousel et le Top 3 */
        position: relative;
        height: 400px; /* Augmente la hauteur totale pour les grandes images */
    }
    .top3-container img {
        width: 200px; /* Agrandit les images */
        height: auto;
        border: 3px solid #555;
        border-radius: 10px;
    }
    .footer {
        text-align: center;
        padding: 20px;
        background-color: #111;
        color: #fff;
        margin-top: 40px;
    }
    .podium {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 30px;
        margin-top: 30px; /* Espace entre les images et le podium */
    }
    .podium div {
        width: 120px; /* Largeur augmentée pour un podium plus imposant */
        background-color: #333;
        border-radius: 5px;
        text-align: center;
        font-size: 32px; /* Texte plus grand pour les médailles */
        color: white;
        font-weight: bold;
        padding-top: 10px;
    }
    .first-place {
        height: 100px; /* Hauteur augmentée pour la 1ère place */
        background-color: #ffd700;
    }
    .second-place {
        height: 80px; /* Hauteur augmentée pour la 2ème place */
        background-color: #c0c0c0;
    }
    .third-place {
        height: 60px; /* Hauteur augmentée pour la 3ème place */
        background-color: #cd7f32;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fonction pour récupérer les animés top
@st.cache_data(ttl=3600)  # Cache les données pendant 1 heure
def get_top_anime():
    response = requests.get("https://api.jikan.moe/v4/top/anime")
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        return []

# Récupération des animés top
top_anime = get_top_anime()

# Vérification si les données ont été récupérées
if not top_anime:
    st.error("Impossible de récupérer les animés populaires.")
else:
    # Initialiser l'index de l'animation dans st.session_state s'il n'existe pas
    if 'anime_index' not in st.session_state:
        st.session_state['anime_index'] = 0

    # Titre principal
    st.title("🎬 Animés Populaires")

    # Conteneur pour le carrousel
    carousel_placeholder = st.empty()

    # Ajouter un espace vide avant le titre Top 3
    st.markdown("<br><br>", unsafe_allow_html=True)  # Espace vide plus grand

    # Section fixe des Top 3 des Animés de Tous les Temps (en dehors du carrousel)
    st.header("🏆 Top 3 des Animés de Tous les Temps")

    # Récupération des titres tronqués pour les trois premiers animés
    first_anime = top_anime[0]
    second_anime = top_anime[1]
    third_anime = top_anime[2]

    # Extraction du titre avant les deux-points
    first_anime_title = first_anime['title'].split(":")[0]
    second_anime_title = second_anime['title'].split(":")[0]
    third_anime_title = third_anime['title'].split(":")[0]

    st.markdown(f"""
        <div class="top3-container">
            <div style="width: 200px; height: auto; position: relative;">
                <img src="{third_anime['images']['jpg']['large_image_url']}" alt="{third_anime_title}">
                <p style="text-align: center;">{third_anime_title}</p>
            </div>
            <div style="width: 200px; height: auto; position: relative; margin-top: 50px;">
                <img src="{first_anime['images']['jpg']['large_image_url']}" alt="{first_anime_title}">
                <p style="text-align: center;">{first_anime_title}</p>
            </div>
            <div style="width: 200px; height: auto; position: relative;">
                <img src="{second_anime['images']['jpg']['large_image_url']}" alt="{second_anime_title}">
                <p style="text-align: center;">{second_anime_title}</p>
            </div>
        </div>
        
        <div class="podium">
            <div class="third-place">🥉</div>
            <div class="first-place">🥇</div>
            <div class="second-place">🥈</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div class="footer">
            <p>© 2023 Mon Application d'Animés</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Boucle infinie pour le carrousel
    while True:
        with carousel_placeholder.container():
            # Afficher les détails de l'animé sélectionné
            selected_anime = top_anime[st.session_state['anime_index']]
            col_details, col_image = st.columns([2, 3])

            with col_details:
                title = selected_anime['title']
                title_japanese = selected_anime.get('title_japanese', 'Titre original non disponible')
                synopsis = selected_anime['synopsis'] if selected_anime['synopsis'] else "Synopsis non disponible."
                synopsis = synopsis[:300] + "..." if len(synopsis) > 300 else synopsis
                rank = selected_anime.get('rank', 'N/A')
                score = selected_anime.get('score', 'N/A')

                st.markdown(f"### {title}")
                st.markdown(f"#### *{title_japanese}*")
                st.markdown(f"**Synopsis :** {synopsis}")
                st.markdown(f"**Classement :** {rank}")
                st.markdown(f"**Score :** {score} / 10")

                trailer_url = selected_anime.get('trailer', {}).get('embed_url', None)
                if trailer_url:
                    st.markdown(f"""
                        <div class='anime-trailer'>
                            <iframe src="{trailer_url}" width="500" height="270" frameborder="0" allowfullscreen></iframe>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<div class='anime-trailer'>Trailer non disponible.</div>", unsafe_allow_html=True)
                    
            with col_image:
                image_url = selected_anime['images']['jpg']['large_image_url']
                st.markdown(f"<div class='anime-image'><img src='{image_url}'></div>", unsafe_allow_html=True)

        # Incrémenter l'index pour le prochain élément du carrousel
        st.session_state['anime_index'] = (st.session_state['anime_index'] + 1) % len(top_anime)
        
        # Pause de 7 secondes pour l'affichage de chaque animé
        time.sleep(7)