import streamlit as st
import requests
import time

# Configuration de la page
st.set_page_config(
    page_title="ようこそ",
    page_icon="👋",
    layout="wide"
)
img_path = "images/welcome.png" 
# Display the image at the top of the page
st.image(img_path, use_column_width=True)

# Initialize the language state if it doesn't exist
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

if st.sidebar.button("Switch to Japanese" if st.session_state['language'] == 'English' else "Switch to English"):
    # Toggle the language
    st.session_state['language'] = 'Japanese' if st.session_state['language'] == 'English' else 'English'

# Display content based on the current language
if st.session_state['language'] == 'English':
    st.sidebar.title("Welcome to the StreamiManga App! 🎥🎌")
    st.markdown("""
    Dive into the world of anime where data meets entertainment! 🚀🎌  
    We are students passionate about anime who created this site to share our love for this genre and analyze viewing trends.  
    - 📊 Explore viewership statistics and trends.  
    - 🤖 Get AI-powered recommendations tailored to your taste.  
    - 🎮 Test your anime knowledge with a fun quiz.  
    - 📺 Discover the most popular shows currently trending.  
    - 🎨 Generate unique anime characters using advanced diffusion models.  

    Join us and uncover the magic of anime! 💖✨
    """)
else:
    st.sidebar.title("StreamiManga アプリへようこそ！ 🎥🎌")
    st.markdown("""
    アニメの世界へようこそ！ここではデータとエンターテインメントが融合します！🚀🎌  
    私たちはアニメに情熱を持つ学生で、このサイトを作り、このジャンルへの愛を共有し、視聴傾向を分析しています。  
    - 📊 視聴者統計とトレンドを探る。  
    - 🤖 あなたの好みに合わせたAIによるおすすめをゲット。  
    - 🎮 楽しいクイズでアニメの知識をテスト。  
    - 📺 現在話題の人気番組を発見。  
    - 🎨 高度な拡散モデルを使用してユニークなアニメキャラクターを生成。  

    アニメの魔法を一緒に体験しましょう！💖✨
    """)

#st.sidebar.title("✨ Welcome to the StreamiManga App! 🎥🌟")
logo_path = "images/streami.png"  
# Display the logo image in the sidebar
st.sidebar.image(logo_path, use_column_width=True)


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

# Filtrer pour garder uniquement les animés avec un trailer
top_anime_with_trailers = [anime for anime in top_anime if anime.get('trailer', {}).get('embed_url')]

# Vérification si les données ont été récupérées
if not top_anime_with_trailers:
    st.error("Could not get popular animes with trailers.")
else:
    # Initialiser l'index de l'animation dans st.session_state s'il n'existe pas
    if 'anime_index' not in st.session_state:
        st.session_state['anime_index'] = 0

    st.title("Most Popular Animes at the moment")
    carousel_placeholder = st.empty()

    # CSS personnalisé
    st.markdown(
        """
        <style>
        .anime-card {
            display: flex;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            gap: 15px;
            flex-wrap: wrap;
            transition: transform 0.1s ease-out;
            transform: perspective(1000px);
            will-change: transform;
        }

        

        .anime-image-container {
            position: relative;
            width: 300px;
            border-radius: 5px;
            flex: 0 0 300px;
            overflow: hidden;
        }
        .anime-image {
            width: 100%;
            border-radius: 5px;
        }
        .anime-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 50px;
            background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
        }
        .anime-rating {
            position: absolute;
            bottom: 10px;
            left: 10px;
            padding: 3px 8px;
            font-size: 10px;
            color: #fff;
        }
        .anime-details {
            flex: 2;
        }
        .anime-right-section {
            flex: 3;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .anime-header {
            padding: 3px 8px;
            border: 1px solid #333;
            border-radius: 5px;
            display: inline-block;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .anime-title {
            font-size: 28px;
            margin: 10px 0;
            font-weight: bold;
        }
        .anime-meta {
            font-size: 14px;
            margin: 5px 0;
        }
        .anime-stats {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        .anime-stats div {
            margin-right: 15px;
            display: flex;
            align-items: center;
        }
        .anime-stats div span {
            font-size: 15px;
            font-weight: bold;
            margin-right: 5px;
        }
        .tag {
            display: inline-block;
            background-color: #292928;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 12px;
            margin-right: 5px;
            color: #fff;
            text-decoration: none;
        }
        .tag a {
            color: inherit; /* This ensures the link takes the color of its parent */
            text-decoration: none; /* Removes underline */
        }

        .tag:hover {
            background-color: #444;
        }

        .tag a:hover {
            color: inherit; /* Keeps the hover color the same as the tag */
        }
        iframe {
            margin-top: 10px;
            border-radius: 5px;
            width: 100%;
            height: 250px; /* Augmenter la hauteur pour une meilleure visibilité */
        }
        .synopsis {
            margin-top: 15px;
            font-size: 15px;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Boucle infinie pour le carrousel
    while True:
        with carousel_placeholder.container():
            # Afficher les détails de l'animé sélectionné
            selected_anime = top_anime_with_trailers[st.session_state['anime_index']]
            title = selected_anime['title']
            image_url = selected_anime['images']['jpg']['large_image_url']
            score = selected_anime.get('score', 'N/A')
            rank = selected_anime.get('rank', 'N/A')
            users = selected_anime.get('scored_by', 'N/A')
            status = selected_anime.get('status', 'N/A')
            start_date = selected_anime.get('aired', {}).get('string', 'N/A')
            episodes = selected_anime.get('episodes', 'N/A')
            genres = selected_anime.get('genres', [])
            trailer_url = selected_anime['trailer']['embed_url']
            synopsis = selected_anime.get('synopsis', 'Synopsis not available.')
            rating = selected_anime.get('rating', 'N/A')

            status_color = "lightblue" if status == "Finished Airing" else "lightgreen" if status == "Currently Airing" else "orange"

            # Affichage des détails de l'animé
            st.markdown(
                f"""
                <div class="anime-card">
                    <div class="anime-image-container">
                        <img src="{image_url}" class="anime-image">
                        <div class="anime-overlay"></div>
                        <div class="anime-rating">{rating}</div>
                    </div>
                    <div class="anime-details">
                        <div class="anime-header" style="color: {status_color};">{status}</div>
                        <h2 class="anime-title">{title}</h2>
                        <div class="anime-stats">
                            <div><span>⭐</span> {score}</div>
                            <div>{users} users</div>
                            <div># {rank} Ranking</div>
                        </div>
                        <div class="anime-meta">
                            Start Date: {start_date} | Episodes: {episodes}
                        </div>
                        <div>
                            {" ".join([
                                f'<a href="{genre["url"]}" target="_blank" class="tag" style="color: #fff; text-decoration: none;">{genre["name"]}</a>' 
                                for genre in genres
                            ])}
                        </div>
                    </div>
                    <div class="anime-right-section">
                        <iframe src="{trailer_url}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
                                                <p class="synopsis"> {synopsis[:300]}...</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Incrémenter l'index pour le prochain élément du carrousel
        st.session_state['anime_index'] = (st.session_state['anime_index'] + 1) % len(top_anime_with_trailers)
        
        # Pause de 18 secondes pour l'affichage de chaque animé
        time.sleep(6)


