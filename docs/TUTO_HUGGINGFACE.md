# 🚀 Tutoriel : Comment utiliser notre modèle IA "In-House" (Qwen 7B Fine-Tuné)

Salut l'équipe ! 
J'ai terminé l'entraînement de notre modèle d'extraction clinique sur le dataset CHIA. Plutôt que de s'échanger des gros fichiers ZIP par mail pour se partager les poids du modèle, **j'ai tout hébergé sur HuggingFace** (le standard de l'industrie).

Voici la procédure ultra-simple pour que vous puissiez faire tourner le modèle et l'application Streamlit sur vos propres machines Lightning AI.

---

## Étape 1 : Mettre à jour le code (GitHub)
Sur votre terminal Lightning AI, assurez-vous d'avoir la dernière version de notre dépôt :
```bash
cd clinicalapp
git pull origin main
```

## Étape 2 : Modifier le chemin du modèle dans le code
Dans les scripts d'inférence ou dans le code de notre application Web (Streamlit), vous allez trouver une variable qui indique où chercher le modèle Fine-Tuné.

Avant, le code cherchait sur mon disque dur local :
```python
# ANCIEN CODE
ADAPTER_DIR = "models/qwen_7b_chia_finetuned"
```

Vous devez simplement remplacer ce chemin par le nom de mon dépôt HuggingFace (je vous donnerai le nom exact, par exemple `Elkristobal59/qwen-7b-chia-ner`) :
```python
# NOUVEAU CODE
ADAPTER_DIR = "Elkristobal59/qwen-7b-chia-ner"
```

## Étape 3 : Lancer l'application
C'est tout ! Il ne vous reste plus qu'à lancer l'application Streamlit normalement :
```bash
streamlit run app.py
```

**Que va-t-il se passer sous le capot ?**
1. Au premier lancement, la librairie `transformers` de votre ordinateur va détecter que `Elkristobal59/qwen-7b-chia-ner` n'est pas un dossier local.
2. Elle va se connecter toute seule aux serveurs d'HuggingFace.
3. Elle va télécharger l'adaptateur de 200 Mo et le mettre en cache sur votre Lightning AI.
4. L'application va fusionner ça avec le modèle de base Qwen 14 Go et tout fonctionnera de manière transparente !

*Note : Le premier lancement prendra quelques minutes à cause du téléchargement, mais les lancements suivants seront instantanés.*

---

## 💡 Astuce de sécurité (Git)
Faites attention de ne jamais `git add` ou `git commit` le dossier `models/` si vous téléchargez des choses manuellement. GitHub bloque les fichiers de plus de 100 Mo et cela bloquerait notre dépôt commun. Gardez le modèle dans le cloud HuggingFace !
