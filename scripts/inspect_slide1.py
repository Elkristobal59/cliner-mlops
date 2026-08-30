with open("docs/demoday_soutenance.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
# find slide 1 section
m = re.search(r'<!-- Slide 1 : Titre -->.*?<\/section>', text, re.DOTALL)
if m:
    slide1 = m.group(0)
    # truncate base64
    clean = re.sub(r'data:image\/[^\"\']+', 'data:image/...', slide1)
    print(clean)
else:
    print("Slide 1 not found")
