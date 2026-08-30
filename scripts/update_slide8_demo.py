import os
import base64
import re

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

html_path = os.path.join("docs", "demoday_soutenance.html")
app_img_path = os.path.join("docs", "visuel_app.png")

print("Lecture du fichier HTML...")
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

print("Encodage de visuel_app.png en base64...")
app_b64 = get_base64_image(app_img_path)
app_data_uri = f"data:image/png;base64,{app_b64}"

pattern = r'<!-- Slide 8 : Demo -->.*?(\s*</div>\s*</div>\s*<script)'

new_slide8 = f'''<!-- Slide 8 : Demo -->
            <section data-transition="zoom" data-background="#000b18" style="text-align: center;">
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; width: 100%; padding: 10px 0;">
                    <h1 style="text-shadow: 0 0 25px rgba(0, 210, 255, 0.6); color: #ffffff; font-size: 3.2em; font-weight: 800; margin-bottom: 5px;">DÉMO EN DIRECT</h1>
                    <p style="color: #00d2ff; font-size: 1.35em; margin-top: 5px; margin-bottom: 25px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;">Découvrez le moteur CliNER en action</p>
                    
                    <div style="margin-bottom: 35px;">
                        <img src="{app_data_uri}" alt="Capture Application Streamlit" style="max-height: 380px; max-width: 85%; margin: 0 auto; display: block; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 30px rgba(0, 210, 255, 0.3); border: 2px solid rgba(0, 210, 255, 0.4);">
                    </div>
                    
                    <div>
                        <a href="https://protocole-clinique.streamlit.app" target="_blank" class="demo-btn" style="display: inline-block; background: linear-gradient(135deg, #00d2ff 0%, #0072ff 100%); color: #fff; font-size: 1.2em; font-weight: bold; padding: 16px 40px; border-radius: 50px; text-decoration: none; box-shadow: 0 10px 30px rgba(0, 210, 255, 0.5); transition: transform 0.3s ease, box-shadow 0.3s ease;">
                            <i class="fa-solid fa-play" style="margin-right: 10px;"></i> Lancer l'Application Streamlit
                        </a>
                    </div>
                </div>
            </section>\\1'''

new_content, count = re.subn(pattern, new_slide8, content, count=1, flags=re.DOTALL)

if count > 0:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Slide 8 (Démo en direct) mise a jour avec succes avec le nouveau visuel de l'application !")
else:
    print("Erreur : Section Slide 8 introuvable dans le HTML.")
