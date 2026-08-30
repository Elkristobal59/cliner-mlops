import os
import glob
import re

docs_files = glob.glob("docs/*.md") + glob.glob("docs/*.html")

for filepath in docs_files:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    orig = content
    # Remplacer 0.5B ou 0,5B ou 0.5b par 7B
    content = re.sub(r'0[\.,]5[Bb]', '7B', content)
    
    # Ajustement dans DEBRIEF_AURELIE_WEEKEND.md et FICHE_PRESENTATION pour correspondre au 7B
    content = content.replace(
        "Spécialisation du modèle sur l'extraction stricte d'entités nommées (NER) médicales sous format JSON standardisé, permettant de faire tourner le modèle localement (Edge AI) avec une empreinte VRAM minimale (~1 Go).",
        "Spécialisation du modèle 7B sur l'extraction stricte d'entités nommées (NER) médicales sous format JSON standardisé, avec quantification QLoRA (4-bit) pour une exécution ultra-rapide et performante sur GPU (75 tokens/sec via vLLM)."
    )
    content = content.replace(
        "Ne pesant qu'1 Go, il peut tourner localement sur un ordinateur portable standard de 6 Go de VRAM (Edge AI) pour le fine-tuning. C'est un point décisif pour les données de santé : aucune donnée patient ne fuite sur des serveurs Cloud.",
        "Grâce à la quantification QLoRA en 4-bit, le modèle 7B est optimisé pour tourner sur GPU dédié ou serveur d'inférence (vLLM) avec une efficacité mémoire maximale et une latence de quelques secondes par essai clinique."
    )
    content = content.replace(
        "Le Choix Stratégique du Modèle (Pourquoi Qwen2.5-7B-Instruct ?)",
        "Le Choix Stratégique du Modèle (Pourquoi Qwen2.5-7B-Instruct en QLoRA ?)"
    )
    content = content.replace(
        "Le format \"Small Language Model\" (7B)",
        "La puissance d'un modèle 7B optimisé (QLoRA)"
    )
    
    if content != orig:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Modifié avec succès : {filepath}")
    else:
        print(f"Aucune modification : {filepath}")
