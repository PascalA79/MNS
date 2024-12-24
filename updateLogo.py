from utility import save_image_from_url

image_url = "https://cdn.discordapp.com/icons/860051225398214677/9101ee588061de94cb470b4bb5575938.webp?size=160"
filename = "app/static/favicon.ico"  # Nom du fichier que vous voulez donner à l'image
Image_created = save_image_from_url(image_url, filename, size=(32,32), format='ICO')
if Image_created:
    print("Image créée avec succès")
else:
    print("Erreur lors de la création de l'image")

