import os
import base64
import re

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

html_path = os.path.join("docs", "demoday_soutenance.html")
logo_path = os.path.join("docs", "cliner_logo.png")

print("Lecture du fichier HTML...")
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

print("Encodage du logo en base64...")
logo_b64 = get_base64_image(logo_path)
logo_data_uri = f"data:image/png;base64,{logo_b64}"

# Recherche et remplacement de la section Slide 1
# On cherche <!-- Slide 1 : Titre --> suivi de <section ...> jusqu'à <div style="...">
pattern = r'(<!-- Slide 1 : Titre -->\s*)<section[^>]*>\s*<div[^>]*>'

# Nouveau contenu propre : fond sombre élégant + logo en élément <img> pour une lisibilité parfaite
replacement = (
    r'\1<section data-transition="zoom" data-background="#000b18">\n'
    r'                <div style="background: rgba(0, 15, 30, 0.85); padding: 40px; border-radius: 20px; border: 1px solid rgba(0, 210, 255, 0.3); backdrop-filter: blur(10px); box-shadow: 0 20px 50px rgba(0,0,0,0.8);">\n'
    f'                    <img src="{logo_data_uri}" style="max-height: 180px; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0, 210, 255, 0.4);">\n'
)

new_content, count = re.subn(pattern, replacement, content, count=1)

if count > 0:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ Slide 1 mise à jour avec succès : fond sombre élégant + logo intégré en en-tête !")
else:
    print("❌ Erreur : Section Slide 1 introuvable dans le HTML.")
