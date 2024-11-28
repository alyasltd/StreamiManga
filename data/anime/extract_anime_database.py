import zipfile
import os

zip_path = "/Users/alyazouzou/Documents/m2/open_data/projet/data/anime/archive.zip"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(os.getcwd()) 

