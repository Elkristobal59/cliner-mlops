import bs4
import re

file_path = "docs/demoday_soutenance.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace slide 2 content
html = html.replace('Choix Architectural : LLM vs ML ?', 'Choix Architectural : Fine-Tuning (Qwen)')
html = html.replace('Pourquoi ne pas avoir "entraîné" de modèle de zéro ?', 'Pourquoi fine-tuner un LLM plutôt que de partir de zéro ?')
html = html.replace("Extraire de l'information de textes libres ultra-complexes rend un modèle ML classique impuissant.",
                    "Nous avons choisi Qwen-2.5-Coder et l'avons fine-tuné (LoRA) sur 860 études CHIA pour extraire les entités avec une précision maximale.")

# Replace slide 5 content
html = html.replace("BioBERT (L'Expert) : Modèle \"off-the-shelf\" natif PubMed. Il vectorise le corpus clinique avec une précision chirurgicale pour construire un",
                    "Qwen Fine-Tuned (L'Expert NER) : Modèle entraîné spécifiquement sur le dataset CHIA. Il extrait les 9 entités cibles de chaque protocole avec une précision chirurgicale.")

html = html.replace("Llama-3-70B (Le Vulgarisateur)", "Évaluation & Benchmark (Holdout)")
html = html.replace("Un géant généraliste qui traduit le jargon technique en réponses humaines et intelligibles.",
                    "La pipeline est validée sur un sous-ensemble (Test Set) de 130 études possédant un PDF, garantissant qu'aucune donnée d'entraînement ne fuite dans le test final.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML mis à jour.")
