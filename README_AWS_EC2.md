# ☁️ Guide : Déploiement et Fine-Tuning sur AWS EC2 GPU (FinOps)

Ce guide décrit la mise en œuvre de l'infrastructure de calcul GPU sur **AWS EC2** (`g4dn.xlarge` avec Nvidia Tesla T4 16 Go) pour exécuter l'API d'inférence vLLM et le réentraînement LoRA de Qwen-7B.

---

## 🏗️ 1. Spécifications de l'Instance Recommandée

* **Type d'instance :** `g4dn.xlarge` (4 vCPU, 16 Go RAM, 1x GPU NVIDIA T4 16 Go VRAM)
* **AMI :** *Deep Learning OSS Nvidia Driver AMI GPU PyTorch (Ubuntu 22.04)*
* **Coût à la demande :** ~0.526 $/heure (~0.16 $/heure en Spot Instance).
* **Règle FinOps :** L'instance est démarrée uniquement pour les jobs d'entraînement (~20 min) et pour la soutenance, puis éteinte immédiatement via `07_mlops_reentrainement/ec2_manager.py`.

---

## 🚀 2. Démarrage Automatisé via Python (boto3)

Depuis votre machine locale ou un workflow GitHub Actions :

```bash
# Allumage de l'instance
python 07_mlops_reentrainement/ec2_manager.py --action start --instance-id i-0123456789abcdef0

# Exécution du cycle complet (Drift -> Fine-Tuning -> Auto-Kill)
python 07_mlops_reentrainement/run_pipeline.py
```

---

## 🐳 3. Exécution Docker sur l'Instance EC2

Une fois connecté sur l'instance :

```bash
# Cloner le projet
git clone https://github.com/Elkristobal59/cliner-mlops.git
cd cliner-mlops

# Lancer le conteneur MLOps
docker build -t cliner-mlops-worker 07_mlops_reentrainement/
docker run --gpus all -v $(pwd)/models:/app/models cliner-mlops-worker
```

---

## 🌐 4. Exposer l'API Backend d'Inférence

Pour faire communiquer Streamlit avec l'API sur AWS EC2 :

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Dans les règles de groupe de sécurité (*Security Group*) de votre instance EC2, ouvrez le port `8000` (FastAPI) et le port `5000` (MLflow).
Sur votre application Streamlit (ou dans votre dashboard Render), renseignez l'URL :
```env
BACKEND_API_URL=http://<IP_PUBLIQUE_EC2>:8000
```
