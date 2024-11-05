import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import BucketedRandomProjectionLSH
from pyspark.sql import functions as F
import time

# Start Spark session for PySpark
spark = SparkSession.builder.appName("AnimeRecommendation").getOrCreate()

# Load the anime dataset
anime_info_df = pd.read_csv("/Users/alyazouzou/Documents/m2/open_data/projet/data/anime/anime-dataset-2023.csv")

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

# Streamlit user interface
st.title("Anime Recommendation System")
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

# Retrieve similar anime information from the original DataFrame
recommended_anime_df = anime_info_df[anime_info_df['anime_id'].isin(similar_anime_ids)]

# Display recommendations in Streamlit
st.write("Recommended anime based on your selection:")
for _, row in recommended_anime_df.iterrows():
    st.write(f"**{row['English name']}** - Genres: {', '.join(row['Genres'])} - Score: {row['Score']}")
