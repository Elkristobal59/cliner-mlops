import re
import base64
import os

def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    b64_str = base64.b64encode(data).decode("utf-8")
    ext = os.path.splitext(path)[1].lower().replace('.', '')
    if ext == 'jpg':
        ext = 'jpeg'
    return f"data:image/{ext};base64,{b64_str}"

html_path = "docs/demoday_soutenance.html"
logo_path = "docs/cliner_logo.png"
app_path = "docs/visuel_app.png"

print("Reading images...")
logo_b64 = get_base64_image(logo_path)
app_b64 = get_base64_image(app_path)

print("Reading HTML...")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# We want to replace the first and second img src tags
pattern = r'(<img[^>]*?src=")(data:image/[^"]+)(")'
matches = list(re.finditer(pattern, html_content))
print(f"Found {len(matches)} base64 images in HTML.")

if len(matches) >= 2:
    # Replace second one first so indices don't shift for first one
    m2 = matches[1]
    html_content = html_content[:m2.start(2)] + app_b64 + html_content[m2.end(2):]
    
    m1 = matches[0]
    html_content = html_content[:m1.start(2)] + logo_b64 + html_content[m1.end(2):]
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully updated both images in demoday_soutenance.html!")
else:
    print("Error: Could not find at least 2 images.")
