import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Who Watches Animes ?", page_icon="📺", layout="wide")

st.markdown("# Who Watches Animes アニメを見ているのは誰？📺")
st.sidebar.header("Who Are Anime Fans? 🤔")

# Cache for loading the logo
@st.cache_resource
def load_logo():
    return "images/streami.png"

logo_path = load_logo()
st.sidebar.image(logo_path, use_column_width=True)

# Cache for loading datasets
@st.cache_data
def load_data():
    anime_data_path = 'data/anime/anime-dataset-2023.csv'
    user_details_path = 'data/user/users-details-2023.csv'
    user_scores_path = 'data/user/user_scores_filtered.csv'
    anime_filtered_path = 'data/anime/anime-filtered.csv'

    anime_df = pd.read_csv(anime_data_path)
    user_details_df = pd.read_csv(user_details_path)
    user_scores_df = pd.read_csv(user_scores_path)
    anime_filtered_df = pd.read_csv(anime_filtered_path)
    return anime_df, user_details_df, user_scores_df, anime_filtered_df

anime_df, user_details_df, user_scores_df, anime_filtered_df = load_data()

# Convert the Score column to numeric values, handling errors
anime_df['Score'] = pd.to_numeric(anime_df['Score'], errors='coerce')

# Creating tabs
tab1, tab2, tab3 = st.tabs(["Explanation", "General Overview", "Anime Selection"])

with tab1:
    st.subheader("About This Page")
    st.markdown("""
    Welcome to the **Who Watches Animes?** dashboard! This page provides insights into anime viewership and allows you to explore detailed statistics and user data. Here's a quick overview of what you'll find in the different tabs:

    - **General Overview**: This tab presents a summary of various anime statistics, including the distribution of different types of anime and the gender distribution among viewers. You can also explore the average episodes watched and average days spent watching anime, categorized by gender.
    
    - **Anime Selection**: This tab allows you to select a specific anime and view detailed information about it, such as its popularity, score, members, and completion statistics. You'll also see the average rating given by male and female viewers and a pie chart showing the gender distribution of viewers who have rated the anime.
    
    Enjoy exploring the data and learning more about anime viewership! 🎉
    """)

with tab2:
    st.subheader("General Overview")

    # Cache computation of the average score
    @st.cache_data
    def calculate_average_score(dataframe):
        return dataframe['Score'].mean()

    average_score = calculate_average_score(anime_df)

    # CSS for styling and animation
    st.markdown("""
        <style>
        .average-score {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            font-size: 2em;
            font-weight: bold;
        }
        .average-score .score-value, .average-score .star {
        margin-left: 10px;
        animation: bounce 1s infinite;
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-10px);
            }
            60% {
                transform: translateY(-5px);
            }
        }
        .description {
            font-size: 0.8em;
            margin-right: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="average-score">
            <span class="description">The user's average score for an anime is</span>
            <span class="score-value">{average_score:.2f} /10</span>
            <span class="star">⭐ !</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Cache computation of anime type counts
    @st.cache_data
    def compute_type_counts(dataframe):
        dataframe['Type'] = dataframe['Genres'].apply(lambda x: x.split(',')[0] if pd.notnull(x) else 'Unknown')
        counts = dataframe['Type'].value_counts()
        return counts[counts.index != 'UNKNOWN']  # Remove 'Unknown'

    type_counts = compute_type_counts(anime_df)

    fig_bar = px.bar(
        type_counts,
        x=type_counts.index,
        y=type_counts.values,
        title="Distribution of Anime Types",
        labels={'x': 'Type', 'y': 'Count'},
        template="plotly_dark"
    )
    fig_bar.update_layout(
        plot_bgcolor='#0f1116',
        paper_bgcolor='#0f1116',
        font_color='white'
    )

    gender_counts = user_details_df['Gender'].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=gender_counts.index,
        values=gender_counts.values,
        hoverinfo='label+percent+value',
        marker=dict(colors=['bluepink', 'pink'])
    )])
    fig_pie.update_layout(
        title="Gender distribution among viewers",
        template="plotly_dark",
        plot_bgcolor='#0f1116',
        paper_bgcolor='#0f1116',
        font_color='white'
    )

    col1, spacer, col2 = st.columns([2, 1, 2])
    with col1:
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # Average episodes watched by gender
    filtered_user_details_df = user_details_df[user_details_df['Gender'] != 'Non-Binary']
    avg_episodes_by_gender = filtered_user_details_df.groupby('Gender')['Episodes Watched'].mean()
    avg_days_watched_by_gender = filtered_user_details_df.groupby('Gender')['Days Watched'].mean()

    col1, col2 = st.columns(2)

    with col1:
        show_avg_episodes = st.checkbox("Show average episodes watched by gender")
        if show_avg_episodes:
            st.bar_chart(avg_episodes_by_gender)

    with col2:
        show_avg_days = st.checkbox("Show average days watched by gender")
        if show_avg_days:
            st.bar_chart(avg_days_watched_by_gender)

with tab3:
    st.subheader("Anime Selection")

    # Selection of an anime in a selectbox
    selected_anime = st.selectbox("Select an anime:", anime_filtered_df['Name'].unique())
    
    # Validation button
    if st.button("Show Details"):
        # Filter details of the selected anime
        anime_details = anime_filtered_df[anime_filtered_df['Name'] == selected_anime]
        anime_image = anime_df[anime_df['Name'] == selected_anime]['Image URL'].values
        
        if not anime_details.empty:
            st.write("### Details for:", selected_anime)
            
            # Column layout for image, details, and pie chart
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
            
            with col1:
                # Display the image with styling
                if len(anime_image) > 0:
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <img src="{anime_image[0]}" style="width: 80%; border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);" alt="Anime Image">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.write("No image available.")
            
            with col2:
                st.markdown(
                    f"""
                    <div style="padding: 10px; font-size: 1.2em; line-height: 1.5;">
                        <p><strong>Popularity:</strong> {anime_details['Popularity'].values[0]}</p>
                        <p><strong>Score:</strong> {anime_details['Score'].values[0]}</p>
                        <p><strong>Members:</strong> {anime_details['Members'].values[0]}</p>
                        <p><strong>Watching:</strong> {anime_details['Watching'].values[0]}</p>
                        <p><strong>Completed:</strong> {anime_details['Completed'].values[0]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Merge and filter for user scores
                selected_anime_id = anime_details['anime_id'].values[0]
                user_scores_for_anime = user_scores_df[user_scores_df['anime_id'] == selected_anime_id]
                user_scores_merged = user_details_df.merge(user_scores_for_anime, left_on='Mal ID', right_on='user_id', how='inner')
                user_scores_merged = user_scores_merged[user_scores_merged['Gender'].isin(['Male', 'Female'])]

                if not user_scores_merged.empty:
                    avg_score_by_gender = user_scores_merged.groupby('Gender')['rating'].mean()
                    st.markdown("### Average score by gender:")
                    st.dataframe(avg_score_by_gender.reset_index())
                    
            with col3:
                if not user_scores_merged.empty:
                    gender_counts = user_scores_merged['Gender'].value_counts()
                    color_map = {'Male': 'blue', 'Female': 'pink'}
                    fig_pie = px.pie(
                        values=gender_counts.values,
                        names=gender_counts.index,
                        title=f"Viewer distribution by gender for {selected_anime}",
                        color=gender_counts.index,
                        color_discrete_map=color_map
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.write("No user data available for this anime.")
