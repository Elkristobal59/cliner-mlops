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

# Recherche de la Slide 1 jusqu'à la Slide 2 pour un remplacement complet et propre
pattern = r'<!-- Slide 1 : Titre -->.*?<!-- Slide 2 : Le Problème -->'

new_slide1 = f'''<!-- Slide 1 : Titre -->
            <section data-transition="zoom" data-background="#000b18" style="text-align: center;">
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; width: 100%; padding: 10px 0;">
                    
                    <!-- Badge Demo Day -->
                    <div style="background: rgba(0, 210, 255, 0.12); border: 1px solid rgba(0, 210, 255, 0.4); padding: 8px 26px; border-radius: 50px; color: #00d2ff; font-size: 0.85em; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 30px; box-shadow: 0 0 20px rgba(0, 210, 255, 0.25); display: inline-block;">
                        DEMO DAY • 03 AOÛT 2026
                    </div>

                    <!-- Logo CliNER Central -->
                    <div style="margin-bottom: 25px;">
                        <img src="{logo_data_uri}" alt="CliNER Logo" style="max-height: 230px; margin: 0 auto; display: block; border-radius: 20px; box-shadow: 0 15px 50px rgba(0, 210, 255, 0.4); border: 1px solid rgba(0, 210, 255, 0.3);">
                    </div>

                    <!-- Sous-titre explicatif -->
                    <p style="font-size: 1.35em; color: #ffffff; font-weight: 600; text-shadow: 0 2px 10px rgba(0,0,0,0.8); margin: 5px auto 35px auto; max-width: 850px; line-height: 1.4;">
                        Un moteur NER (Named Entity Recognition) au service du médical
                    </p>

                    <!-- Boîte Équipe -->
                    <div class="glass-box" style="background: rgba(0, 20, 40, 0.65); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 16px; padding: 18px 45px; text-align: center; display: inline-block; box-shadow: 0 15px 40px rgba(0,0,0,0.6); backdrop-filter: blur(12px);">
                        <p style="font-size: 0.75em; margin: 0 0 8px 0; color: #00d2ff; font-weight: 800; letter-spacing: 3px; text-transform: uppercase;">L'ÉQUIPE JEDHA AIFS01</p>
                        <p style="font-size: 0.95em; margin: 0; font-weight: 600; color: #ffffff; line-height: 1.6;">Patrick Mouliom • Christopher Gilleron<br>Jérémie Becker • Arnaud Hoarau • Karim Atebata</p>
                    </div>

                </div>
            </section>

            <!-- Slide 2 : Le Problème -->'''

new_content, count = re.subn(pattern, new_slide1, content, count=1, flags=re.DOTALL)

if count > 0:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Slide 1 mise a jour avec succes : centrage parfait et mise en page moderne !")
else:
    print("Erreur : Section Slide 1 introuvable dans le HTML.")
