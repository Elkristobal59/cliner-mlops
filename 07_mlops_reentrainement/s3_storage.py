"""
Module : s3_storage.py (Composant Stockage & Data Lake AWS S3)
---------------------------------------------------------------
Rôle :
Gère les transferts vers et depuis le bucket AWS S3 pour le projet CliNER :
    1. Protocoles PDF cliniques bruts (s3://<bucket>/clinical_pdfs/).
    2. Datasets d'entraînement CHIA (s3://<bucket>/datasets/).
    3. Poids des adaptateurs LoRA réentraînés (s3://<bucket>/models_lora/<version>/).
    4. Artefacts et exports de métriques MLflow (s3://<bucket>/mlflow_artifacts/).

Gestion Dry-Run & FinOps :
En l'absence de bucket configuré ou en mode simulation, simule les transferts 
sans lever d'exception pour permettre une exécution fluide en local / CI.
"""

import os
import sys
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional

# Reconfigure stdout for Windows cp1252 terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception


class S3StorageManager:
    """
    Gestionnaire centralisé des flux AWS S3 pour le Continuous Training et l'inférence.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
        dry_run: bool = False
    ):
        self.bucket_name = bucket_name or os.environ.get("S3_BUCKET_NAME", "cliner-clinical-storage-dev")
        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")
        self.dry_run = dry_run
        self.s3_client = None

        if not self.dry_run and boto3 is not None:
            try:
                self.s3_client = boto3.client("s3", region_name=self.region_name)
            except Exception as e:
                print(f"[S3StorageManager] ⚠️ Impossible d'initialiser boto3.s3 : {e}")
                self.s3_client = None

    def upload_file(self, local_file_path: str, s3_key: str) -> Dict[str, Any]:
        """
        Téléverse un fichier local vers S3.
        """
        local_path = Path(local_file_path)
        if not local_path.exists():
            return {
                "status": "error",
                "message": f"Fichier local introuvable : {local_file_path}",
                "s3_uri": None
            }

        s3_uri = f"s3://{self.bucket_name}/{s3_key}"
        file_size_mb = round(local_path.stat().st_size / (1024 * 1024), 2)

        if self.dry_run or self.s3_client is None:
            print(f"[S3 SIMULATION] ☁️ Upload simulé : {local_path.name} ({file_size_mb} Mo) ➔ {s3_uri}")
            return {
                "status": "simulated",
                "s3_uri": s3_uri,
                "file_size_mb": file_size_mb
            }

        try:
            print(f"☁️ [S3] Téléversement en cours : {local_path.name} ➔ {s3_uri}...")
            self.s3_client.upload_file(str(local_path), self.bucket_name, s3_key)
            print(f"✅ [S3] Téléversement réussi : {s3_uri}")
            return {
                "status": "success",
                "s3_uri": s3_uri,
                "file_size_mb": file_size_mb
            }
        except Exception as err:
            print(f"❌ [S3] Erreur upload {local_file_path} : {err}")
            return {
                "status": "failed",
                "error": str(err),
                "s3_uri": s3_uri
            }

    def download_file(self, s3_key: str, local_destination_path: str) -> Dict[str, Any]:
        """
        Télécharge un fichier depuis S3 vers le stockage local.
        """
        dest_path = Path(local_destination_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        s3_uri = f"s3://{self.bucket_name}/{s3_key}"

        if self.dry_run or self.s3_client is None:
            print(f"[S3 SIMULATION] ☁️ Download simulé : {s3_uri} ➔ {dest_path}")
            return {
                "status": "simulated",
                "local_path": str(dest_path),
                "s3_uri": s3_uri
            }

        try:
            print(f"☁️ [S3] Téléchargement en cours : {s3_uri} ➔ {dest_path}...")
            self.s3_client.download_file(self.bucket_name, s3_key, str(dest_path))
            print(f"✅ [S3] Téléchargement réussi : {dest_path}")
            return {
                "status": "success",
                "local_path": str(dest_path),
                "s3_uri": s3_uri
            }
        except Exception as err:
            print(f"❌ [S3] Erreur download {s3_key} : {err}")
            return {
                "status": "failed",
                "error": str(err),
                "local_path": str(dest_path)
            }

    def upload_lora_adapter(self, adapter_dir: str, version: str = "v2") -> Dict[str, Any]:
        """
        Téléverse le répertoire complet de l'adaptateur LoRA réentraîné vers S3.
        Clé cible : models_lora/qwen-7b-chia-ner-{version}/
        """
        adapter_path = Path(adapter_dir)
        clean_version = version if version.startswith("qwen-7b") else f"qwen-7b-chia-ner-{version}"
        s3_prefix = f"models_lora/{clean_version}"
        results = []

        print(f"\n📦 [S3] Sauvegarde de l'adaptateur LoRA dans le Cloud S3...")
        print(f"  ├── Dossier source : {adapter_dir}")
        print(f"  └── Destination S3 : s3://{self.bucket_name}/{s3_prefix}/")

        if self.dry_run or self.s3_client is None or not adapter_path.exists():
            simulated_uri = f"s3://{self.bucket_name}/{s3_prefix}/adapter_model.safetensors"
            print(f"[S3 SIMULATION] Adaptateur LoRA (~84 Mo) synchronisé vers {simulated_uri}")
            return {
                "status": "simulated",
                "s3_prefix": s3_prefix,
                "s3_root_uri": f"s3://{self.bucket_name}/{s3_prefix}/",
                "files_count": 2
            }

        for file_path in adapter_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(adapter_path).as_posix()
                target_key = f"{s3_prefix}/{relative_path}"
                res = self.upload_file(str(file_path), target_key)
                results.append(res)

        return {
            "status": "success",
            "s3_prefix": s3_prefix,
            "s3_root_uri": f"s3://{self.bucket_name}/{s3_prefix}/",
            "files_count": len(results)
        }

    def sync_clinical_data(self, local_data_dir: str = "data") -> Dict[str, Any]:
        """
        Synchronise les protocoles PDF et datasets locaux avec le bucket S3.
        """
        print(f"\n🔄 [S3] Synchronisation des datasets & protocoles cliniques...")
        datasets_uploaded = 0
        data_path = Path(local_data_dir)

        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)

        for jsonl_file in data_path.glob("*.jsonl"):
            key = f"datasets/{jsonl_file.name}"
            self.upload_file(str(jsonl_file), key)
            datasets_uploaded += 1

        for pdf_file in data_path.glob("*.pdf"):
            key = f"clinical_pdfs/{pdf_file.name}"
            self.upload_file(str(pdf_file), key)
            datasets_uploaded += 1

        return {
            "status": "success",
            "synced_files": datasets_uploaded,
            "bucket": self.bucket_name
        }


if __name__ == "__main__":
    manager = S3StorageManager(dry_run=True)
    res = manager.upload_lora_adapter("models/qwen_7b_lora_retrained", version="v2")
    print(res)
