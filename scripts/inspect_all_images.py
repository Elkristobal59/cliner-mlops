with open("docs/demoday_soutenance.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = list(re.finditer(r'data:image\/[^\"\']+', text))
print(f"Total data:image references found: {len(matches)}")
for i, m in enumerate(matches):
    start = max(0, m.start() - 150)
    end = min(len(text), m.start() + 50)
    snippet = text[start:end]
    snippet_clean = re.sub(r'data:image\/[^\"\']+', 'data:image/...', snippet)
    print(f"--- Match {i+1} ---")
    print(snippet_clean)
