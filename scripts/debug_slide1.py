import re

with open("docs/demoday_soutenance.html", "r", encoding="utf-8") as f:
    c = f.read()

s = c.find("<!-- Slide 1 : Titre -->")
e = c.find("<!-- Slide 2 : Le Problème -->")

if s != -1 and e != -1:
    content = c[s:e]
    # Remplacer le base64 pour affichage lisible
    clean = re.sub(r'data:image/[^"\'\s]+', 'BASE64_IMAGE', content)
    print("=== CONTENU ACTUEL DE LA SLIDE 1 ===")
    print(clean)
else:
    print("Section non trouvée !", s, e)
