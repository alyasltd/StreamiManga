import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL de base pour la première page de personnages
base_url = "https://www.anime-planet.com/characters/all"

# En-tête pour imiter un navigateur
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}

# Liste pour stocker les données des personnages
characters_data = []

# Fonction pour scraper une page donnée
def scrape_characters_page(url):
    response = requests.get(url, headers=headers)  # Ajout des en-têtes
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        characters = soup.select("tr")  # Sélection de chaque ligne de personnage

        for character in characters:
            try:
                # Lien de l'image
                image_tag = character.select_one("td.tableAvatar img")
                image_url = image_tag["src"] if image_tag else None

                # Nom et lien du personnage
                name_tag = character.select_one("td.tableCharInfo a.name")
                name = name_tag.text.strip() if name_tag else None
                profile_link = "https://www.anime-planet.com" + name_tag["href"] if name_tag else None

                # Traits (premier groupe de tags)
                traits_list = [trait.text.strip() for trait in character.select("div.tags:nth-of-type(1) ul li a")]

                # Tags (deuxième groupe de tags)
                tags_list = [tag.text.strip() for tag in character.select("div.tags:nth-of-type(2) ul li a")]

                # Premier Anime associé
                first_anime_tag = character.select_one("td.tableAnime div:nth-of-type(1) ul li")
                anime_title = first_anime_tag.text.strip() if first_anime_tag else "Aucun anime"

                # Premier Manga associé
                first_manga_tag = character.select_one("td.tableAnime div:nth-of-type(2) ul li")
                manga_title = first_manga_tag.text.strip() if first_manga_tag else "Aucun manga"

                # Ajouter les données dans la liste
                characters_data.append({
                    "Nom": name,
                    "Lien Profil": profile_link,
                    "Image": image_url,
                    "Traits": ", ".join(traits_list),
                    "Tags": ", ".join(tags_list),
                    "Anime Associé": anime_title,
                    "Manga Associé": manga_title
                })
                print(f"Personnage '{name}' scrappé avec succès.")
            except Exception as e:
                print(f"Erreur lors de l'extraction d'un personnage : {e}")
    else:
        print(f"Erreur lors du chargement de la page : {url} (Status code: {response.status_code})")

# Scraper la première page
print("Scraping de la première page")
scrape_characters_page(base_url)

# Scraper les pages de 2 à 50
for page in range(2, 51):
    url = f"{base_url}?page={page}"
    print(f"Scraping de la page {page}")
    scrape_characters_page(url)
    time.sleep(2)  # Pause pour éviter de surcharger le serveur

# Convertir les données en DataFrame et sauvegarder en CSV
df = pd.DataFrame(characters_data)
df.to_csv("anime_planet_characters.csv", index=False, encoding="utf-8")
print("Données enregistrées dans 'anime_planet_characters.csv'")
