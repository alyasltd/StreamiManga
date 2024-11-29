import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import BucketedRandomProjectionLSH
from pyspark.sql import functions as F
import time

st.set_page_config(page_title="Wants some Recommandations ?", page_icon="🙋🏻‍♀️")

st.markdown("# Wants some Recommandations おすすめを知りたいですか ？")
st.sidebar.header("We'll predict your next favorite anime ! 🔮")

# Add an explanatory text at the top of the page
st.markdown("""
### How Does the Recommendation Work? 🤔

Welcome to the **Anime Recommendation Page**! 🎉 Here, we use advanced data analysis and machine learning to suggest anime that you might enjoy based on your favorite selections. Here's a breakdown of how this process works:

1. **Feature Extraction**: We start by analyzing various features of each anime, such as genres, type, popularity, score, and more. These features are encoded using one-hot encoding and standardized for uniformity.

2. **Genre Weighting**: The system applies a special emphasis on matching genres. If you select an anime with certain genres, those genres are given more weight in the feature analysis, making the recommendations more tailored to your tastes.

3. **Similarity Analysis**: Using a machine learning technique called *Locality Sensitive Hashing (LSH)*, we identify anime that are similar to your favorite based on cosine similarity. This method helps us find the most relevant anime from a vast dataset quickly and efficiently.

4. **Recommendations**: Once similar anime are found, we display the top matches (excluding your original selection). The results are shown with essential details like the score, number of episodes, and genres, accompanied by an image of the anime.

### Ready to discover your next favorite anime? Select an anime from the dropdown and see the magic unfold! ✨
""")

logo_path = "StreamiManga/images/streami.png"  
# Display the logo image in the sidebar
st.sidebar.image(logo_path, use_column_width=True)

# Start Spark session for PySpark
spark = SparkSession.builder.appName("AnimeRecommendation").getOrCreate()

# Load the anime dataset
anime_info_df = pd.read_csv("StreamiManga/data/anime/anime-dataset-2023.csv")

# Save the 'Image URL' column before dropping it
image_url_df = anime_info_df[['anime_id', 'Image URL']]

# Drop unnecessary columns
anime_info_df = anime_info_df.drop(columns=['Image URL', 'Premiered', 'Aired', 'Status', 'Duration', 'Rating'])

# Remove rows containing 'UNKNOWN' in any column
anime_info_df = anime_info_df.replace('UNKNOWN', np.nan).dropna()

# Filter to only include anime with a Score above 8
anime_info_df = anime_info_df[anime_info_df['Score'].astype(float) > 8]

# Center selection box using custom CSS
st.markdown("""
    <style>
    .css-1y4p8pa, .css-18e3th9, .css-1cpxqw2 {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)


favorite_anime = st.selectbox("Select your favorite anime:", anime_info_df['English name'].values)

# Retrieve anime_id and genres for the selected anime
selected_anime = anime_info_df[anime_info_df['English name'] == favorite_anime].iloc[0]
selected_anime_id = selected_anime['anime_id']
selected_anime_genres = selected_anime['Genres'].split(", ")

# ---- Step 1: Feature Engineering ----
# Handling 'Genres' - assuming it's a comma-separated list
if 'Genres' in anime_info_df.columns:
    anime_info_df['Genres'] = anime_info_df['Genres'].astype(str).apply(lambda x: x.split(',') if isinstance(x, str) else [])
    mlb_genres = MultiLabelBinarizer()
    genres_encoded = pd.DataFrame(mlb_genres.fit_transform(anime_info_df['Genres']), columns=mlb_genres.classes_, index=anime_info_df.index)
    anime_info_df = pd.concat([anime_info_df, genres_encoded], axis=1)

# One-hot encoding for other categorical columns: 'Type', 'Producers', 'Licensors', 'Studios', 'Source'
for col in ['Type', 'Producers', 'Licensors', 'Studios', 'Source']:
    if col in anime_info_df.columns:
        anime_info_df[col] = anime_info_df[col].astype(str).fillna('')
        mlb = MultiLabelBinarizer()
        encoded = pd.DataFrame(mlb.fit_transform(anime_info_df[col].apply(lambda x: x.split(', ') if isinstance(x, str) else [])),
                               columns=[f"{col}_{cls}" for cls in mlb.classes_], index=anime_info_df.index)
        anime_info_df = pd.concat([anime_info_df, encoded], axis=1)

# Keep a copy of original numeric columns for display purposes
original_numeric_columns = anime_info_df[['anime_id', 'Score', 'Episodes']].copy()

# Standardize numeric features: 'Score', 'Episodes', 'Rank', 'Popularity', 'Favorites', 'Scored By', 'Members'
numeric_columns = ['Score', 'Episodes', 'Rank', 'Popularity', 'Favorites', 'Scored By', 'Members']
scaler = StandardScaler()
for feature in numeric_columns:
    anime_info_df[feature] = scaler.fit_transform(anime_info_df[[feature]])

# ---- Step 2: Apply Dynamic Weighting ----
# Define a weighting factor for genres that match the selected anime's genres
genre_weight_factor = 7.0  # Example factor; can be adjusted

# Apply weighting to matching genre columns
for genre in selected_anime_genres:
    if genre in anime_info_df.columns:
        anime_info_df[genre] *= genre_weight_factor

# ---- Step 3: Create Feature Vectors ----
# Select only the feature columns for the vector
feature_columns = [col for col in anime_info_df.columns if col not in ['anime_id', 'Name', 'English name', 'Other name', 'Synopsis', 'Genres', 'Producers', 'Licensors', 'Studios', 'Source', 'Type']]
anime_info_df['features'] = anime_info_df[feature_columns].values.tolist()

# Convert lists of features to dense vectors (e.g., numpy arrays) for each anime
anime_info_df['features'] = anime_info_df['features'].apply(lambda x: np.array(x, dtype=float))

# ---- Step 4: Prepare PySpark DataFrame for LSH ----
# Convert each list of features into a PySpark dense vector
anime_info_df['features'] = anime_info_df['features'].apply(lambda x: Vectors.dense(x))

# Create a PySpark DataFrame with anime_id and features columns
anime_spark_df = spark.createDataFrame(anime_info_df[['anime_id', 'features']])

# ---- Step 5: Fit LSH Model and Find Nearest Neighbors ----

# LSH model for cosine similarity
lsh = BucketedRandomProjectionLSH(inputCol="features", outputCol="hashes", bucketLength=2.0, numHashTables=3)
lsh_model = lsh.fit(anime_spark_df)

# Get the feature vector for the selected anime
player_of_interest = anime_spark_df.filter(F.col("anime_id") == selected_anime_id).select("features")

# Find the top 4 nearest neighbors (including the anime itself)
nearest_neighbors = lsh_model.approxNearestNeighbors(anime_spark_df, player_of_interest.first()['features'], numNearestNeighbors=4)

# Extract IDs of nearest neighbors, excluding the selected anime itself
similar_anime_ids = [row['anime_id'] for row in nearest_neighbors.collect() if row['anime_id'] != selected_anime_id][:3]

# ---- Step 5: Display recommendations using original values ----
# Retrieve similar anime information from the original DataFrame
recommended_anime_df = anime_info_df[anime_info_df['anime_id'].isin(similar_anime_ids)]

# Merge 'Image URL' and original numeric columns back to the recommended anime DataFrame
recommended_anime_df = pd.merge(recommended_anime_df, image_url_df, on='anime_id', how='left')
recommended_anime_df = pd.merge(recommended_anime_df, original_numeric_columns, on='anime_id', how='left', suffixes=('', '_original'))

# Display the recommendations with original 'Score' and 'Episodes'
st.write("Recommended anime based on your selection:")
for _, row in recommended_anime_df.iterrows():
    st.markdown(f"""
    <div style="border:1px solid #333; padding: 5px; border-radius: 5px; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; box-shadow: 2px 2px 8px rgba(255, 255, 255, 0.1);">
        <div style="flex: 1;">
            <img src="{row['Image URL']}" alt="{row['English name']}" style="width: 100px; border-radius: 5px;">
        </div>
        <div style="flex: 2; color: #ddd;">
        <h3 style="margin: 0; font-size: 16px; color: #fff;">
            {row['English name']} ({row['Other name']})
        </h3>
            <p style="margin: 3px 0; font-size: 14px;"><strong>Genres :</strong> {', '.join(row['Genres'])}</p>
            <p style="margin: 3px 0; font-size: 14px;"><strong>Score :</strong> {row['Score_original']}</p>
            <p style="margin: 3px 0; font-size: 14px;"><strong>Episodes :</strong> {row['Episodes_original']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)