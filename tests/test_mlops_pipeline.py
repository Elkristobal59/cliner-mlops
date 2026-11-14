"""
Tests Unitaires et d'Intégration MLOps — Quality Gate CI/CD (PyTest)
====================================================================
Suite de 5 tests essentiels validant la chaîne CI/CD/CT et la sécurité FinOps :
1. test_1_wasserstein_drift_detection       : Détection de dérive Wasserstein (BioBERT 768d) vs stabilité FinOps.
2. test_2_evidently_drift_report_generation : Génération des rapports de monitoring Evidently AI (HTML & JSON).
3. test_3_ec2_finops_autokill_lifecycle     : Cycle de vie AWS EC2 GPU (Start -> Stop Auto-Kill, billing_active=False).
4. test_4_qlora_finetuning_and_s3_upload    : Réentraînement QLoRA 4-bit (CHIA) et versionnage vers AWS S3.
5. test_5_end_to_end_mlops_orchestration    : Intégration bout-en-bout de l'orchestrateur et audit XML ISO 13485.
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# Résolution des chemins pour imports propres
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MLOPS_DIR = PROJECT_ROOT / "mlops_reentrainement"
if str(MLOPS_DIR) not in sys.path:
    sys.path.insert(0, str(MLOPS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from drift_detection import EmbeddingDriftDetector
from ec2_manager import EC2GPUManager
from finetune_lora import run_lora_finetuning
from s3_storage import S3StorageManager
from run_pipeline import orchestrate_mlops_pipeline
from monitoring_evidently import generate_drift_report


class TestMLOpsQualityGate:
    """Suite des 5 tests essentiels de la Quality Gate CI/CD GitHub Actions."""

    # --------------------------------------------------------------------------
    # Test 1 : Détection de Dérive Sémantique (Wasserstein W1 sur BioBERT 768d)
    # --------------------------------------------------------------------------
    def test_1_wasserstein_drift_detection(self):
        """Vérifie le déclenchement sur dérive (W1 > 0.08) et le blocage FinOps sur distribution stable."""
        detector = EmbeddingDriftDetector(threshold=0.08)
        ref_vecs = detector._generate_synthetic_baseline(n_samples=50, dim=768)

        # Cas A : Dérive sémantique critique -> doit déclencher le réentraînement
        drifted_vecs = detector._generate_synthetic_drifted(n_samples=5, dim=768, drift_magnitude=0.40)
        drift_metrics = detector.compute_drift_metrics(ref_vecs, drifted_vecs)
        assert drift_metrics["wasserstein_distance"] >= 0.08
        assert drift_metrics["drift_detected"] is True

        # Cas B : Distribution stable -> ne doit pas allumer le GPU (0,00 €)
        stable_detector = EmbeddingDriftDetector(threshold=0.20)
        stable_vecs = stable_detector._generate_synthetic_baseline(n_samples=5, dim=768)
        stable_metrics = stable_detector.compute_drift_metrics(ref_vecs, stable_vecs)
        assert stable_metrics["wasserstein_distance"] < 0.20
        assert stable_metrics["drift_detected"] is False

    # --------------------------------------------------------------------------
    # Test 2 : Génération du Rapport de Monitoring Evidently AI (HTML & JSON)
    # --------------------------------------------------------------------------
    def test_2_evidently_drift_report_generation(self):
        """Vérifie la génération des rapports Data Drift Evidently AI (HTML et JSON structuré)."""
        report_info = generate_drift_report(log_to_mlflow=False)
        assert os.path.exists(report_info["html_path"])
        assert os.path.exists(report_info["json_path"])

        with open(report_info["json_path"], "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "features" in data
        assert "summary" in data
        assert "timestamp" in data

    # --------------------------------------------------------------------------
    # Test 3 : Cycle de Vie FinOps AWS EC2 GPU & Garantie Auto-Kill
    # --------------------------------------------------------------------------
    def test_3_ec2_finops_autokill_lifecycle(self):
        """Valide le démarrage JIT et l'extinction forcée (Auto-Kill) coupant la facturation AWS."""
        manager = EC2GPUManager(instance_id="i-test-gpu-001", dry_run=True)

        assert manager.get_status() in ["stopped", "running", "unknown"]

        start_res = manager.start()
        assert start_res["status"] == "running"

        stop_res = manager.stop()
        assert stop_res["status"] == "stopped"
        assert stop_res["billing_active"] is False

    # --------------------------------------------------------------------------
    # Test 4 : Fine-Tuning QLoRA 4-bit (Qwen2.5-7B) & Versionnage AWS S3
    # --------------------------------------------------------------------------
    def test_4_qlora_finetuning_and_s3_upload(self, tmp_path):
        """Valide l'entraînement de l'adaptateur QLoRA sur CHIA et son envoi vers le bucket S3."""
        train_res = run_lora_finetuning(
            dataset_path=str(PROJECT_ROOT / "data" / "train_dataset.jsonl"),
            epochs=1,
            learning_rate=2e-4,
            dry_run=True
        )
        assert train_res["status"] == "success"
        assert train_res["final_loss"] == 0.284
        assert train_res["f1_score"] == 0.583

        s3 = S3StorageManager(bucket_name="cliner-mlops", dry_run=True)
        test_file = tmp_path / "adapter_config.json"
        test_file.write_text(json.dumps({"r": 16, "lora_alpha": 32}), encoding="utf-8")
        up_res = s3.upload_file(str(test_file), "models_lora/qwen-7b-chia-ner-v2/adapter_config.json")
        assert up_res["status"] in ["simulated", "success"]
        assert up_res["s3_uri"].startswith("s3://cliner-mlops/models_lora/")

    # --------------------------------------------------------------------------
    # Test 5 : Orchestration MLOps Bout-en-Bout & Journal d'Audit XML ISO 13485
    # --------------------------------------------------------------------------
    def test_5_end_to_end_mlops_orchestration(self):
        """Valide l'orchestration complète (run_pipeline.py), l'Auto-Kill et la conformité XML."""
        report = orchestrate_mlops_pipeline(
            threshold=0.08,
            force_retrain=True,
            dry_run=True,
            instance_id="i-test-001"
        )
        assert report["status"] == "success"
        assert "evidently_report_generated" in report["steps_completed"]
        assert "finetune_completed" in report["steps_completed"]
        assert "ec2_auto_killed" in report["steps_completed"]

        xml_path = report.get("xml_journal_path")
        assert xml_path and os.path.exists(xml_path)
        root = ET.parse(xml_path).getroot()
        assert root.tag == "PipelineExecution"
        assert root.attrib["status"] == "SUCCESS"
