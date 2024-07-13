import requests
from PIL import Image
from io import BytesIO

def create_ico_from_image_url(image_url, output_file="output.ico", size=(32, 32)):
    try:
        # Récupérer l'image depuis l'URL
        response = requests.get(image_url)
        image_data = response.content
        
        # Ouvrir l'image avec PIL
        img = Image.open(BytesIO(image_data))
        
        # Redimensionner l'image si nécessaire
        img = img.resize(size)
        
        # Créer un fichier ICO
        img.save(output_file, format="ICO")
        
        print(f"Fichier ICO créé avec succès: {output_file}")
    
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Exemple d'utilisation
image_url = "https://cdn.discordapp.com/icons/860051225398214677/9101ee588061de94cb470b4bb5575938.webp?size=160"
filename = "app/static/favicon.ico"  # Nom du fichier que vous voulez donner à l'image
create_ico_from_image_url(image_url, filename, size=(32,32))
