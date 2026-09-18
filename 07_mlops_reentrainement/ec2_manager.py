"""
Module : ec2_manager.py (Composant FinOps / Cloud Infrastructure)
------------------------------------------------------------------
Rôle :
Gestionnaire automatisé du cycle de vie de l'instance AWS EC2 GPU (ex: g4dn.xlarge / g5.xlarge).
Assure la mise sous tension à la demande, l'attente du démarrage, l'exécution distante, 
et l'extinction systématique (Auto-Kill) dès la fin des opérations.

Objectif FinOps :
Réduire la facture Cloud de 95% en ne payant que pour les ~20 minutes de fine-tuning utiles, 
évitant ainsi de laisser tourner une machine GPU 24h/24.

Usage :
    python ec2_manager.py --action start --instance-id i-0123456789abcdef0
    python ec2_manager.py --action stop  --instance-id i-0123456789abcdef0
    python ec2_manager.py --action status --dry-run
"""

import os
import sys
import time
import argparse
from typing import Dict, Any, Optional

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


class EC2GPUManager:
    """
    Gestionnaire FinOps pour instance AWS EC2 avec GPU.
    Supporte un mode simulation (dry-run) pour les démonstrations locales et examens.
    """

    def __init__(self, instance_id: Optional[str] = None, region: str = "eu-west-3", dry_run: bool = False):
        self.instance_id = instance_id or os.getenv("AWS_EC2_GPU_INSTANCE_ID", "i-09f18a47bce42gpu")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "eu-west-3")
        self.dry_run = dry_run or (os.getenv("MOCK_AWS_EC2", "true").lower() == "true")
        
        self.ec2_client = None
        if not self.dry_run and boto3 is not None:
            try:
                self.ec2_client = boto3.client("ec2", region_name=self.region)
            except Exception as e:
                print(f"[WARN] Connexion AWS impossible ({e}). Basculement en mode simulation FinOps.")
                self.dry_run = True
        else:
            self.dry_run = True

    def get_status(self) -> str:
        """Récupère l'état actuel de l'instance (running, stopped, pending, stopping)."""
        if self.dry_run:
            return "stopped"
        try:
            resp = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            state = resp["Reservations"][0]["Instances"][0]["State"]["Name"]
            return state
        except Exception as e:
            print(f"[ERROR] Impossible de lire le statut EC2 : {e}")
            return "unknown"

    def start(self, timeout_sec: int = 180) -> Dict[str, Any]:
        """
        Démarre l'instance EC2 GPU et attend qu'elle soit en état 'running'.
        """
        print(f"🚀 [FinOps] Démarrage de l'instance GPU AWS : {self.instance_id} ({self.region})...")
        if self.dry_run:
            print("⏳ [DRY-RUN] Envoi de la commande 'ec2:StartInstances'...")
            time.sleep(1.5)
            print("✅ [DRY-RUN] Instance passée en état 'running' (IP Publique : 54.198.42.105)")
            return {
                "status": "running",
                "instance_id": self.instance_id,
                "public_ip": "54.198.42.105",
                "mode": "simulation"
            }

        try:
            self.ec2_client.start_instances(InstanceIds=[self.instance_id])
            print("⏳ Attente de l'état 'running'...")
            waiter = self.ec2_client.get_waiter("instance_running")
            waiter.wait(InstanceIds=[self.instance_id], WaiterConfig={"Delay": 5, "MaxAttempts": timeout_sec // 5})
            
            # Récupération de l'IP publique
            resp = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            inst = resp["Reservations"][0]["Instances"][0]
            public_ip = inst.get("PublicIpAddress", "N/A")
            print(f"✅ Instance en ligne avec succès ! IP publique : {public_ip}")
            return {
                "status": "running",
                "instance_id": self.instance_id,
                "public_ip": public_ip,
                "mode": "aws_live"
            }
        except ClientError as e:
            print(f"❌ Erreur lors du démarrage EC2 : {e}")
            return {"status": "error", "error": str(e)}

    def stop(self) -> Dict[str, Any]:
        """
        Éteint l'instance immédiatement pour couper la facturation à la seconde (FinOps).
        """
        print(f"🛑 [FinOps] Coupure immédiate de l'instance GPU : {self.instance_id} (Auto-Kill FinOps)...")
        if self.dry_run:
            print("⏳ [DRY-RUN] Envoi de la commande 'ec2:StopInstances'...")
            time.sleep(1.0)
            print("🔒 [DRY-RUN] Instance stoppée. Facturation GPU arrêtée. Coût résiduel = 0.00 €.")
            return {
                "status": "stopped",
                "instance_id": self.instance_id,
                "billing_active": False,
                "mode": "simulation"
            }

        try:
            self.ec2_client.stop_instances(InstanceIds=[self.instance_id])
            print("🔒 Instance en cours d'extinction. Les coûts de calcul GPU sont coupés.")
            return {
                "status": "stopping",
                "instance_id": self.instance_id,
                "billing_active": False,
                "mode": "aws_live"
            }
        except ClientError as e:
            print(f"❌ Erreur lors de l'arrêt EC2 : {e}")
            return {"status": "error", "error": str(e)}

    def terminate(self) -> Dict[str, Any]:
        """Détruit définitivement l'instance si celle-ci était éphémère."""
        print(f"🗑️ [FinOps] Destruction de l'instance éphémère : {self.instance_id}...")
        if self.dry_run:
            return {"status": "terminated", "instance_id": self.instance_id, "mode": "simulation"}
        try:
            self.ec2_client.terminate_instances(InstanceIds=[self.instance_id])
            return {"status": "terminating", "instance_id": self.instance_id, "mode": "aws_live"}
        except ClientError as e:
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestionnaire FinOps EC2 GPU")
    parser.add_argument("--action", choices=["start", "stop", "status", "terminate"], default="status")
    parser.add_argument("--instance-id", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    manager = EC2GPUManager(instance_id=args.instance_id, dry_run=args.dry_run)

    if args.action == "start":
        res = manager.start()
    elif args.action == "stop":
        res = manager.stop()
    elif args.action == "terminate":
        res = manager.terminate()
    else:
        status = manager.get_status()
        res = {"instance_id": manager.instance_id, "status": status}

    print(f"Résultat : {res}")
