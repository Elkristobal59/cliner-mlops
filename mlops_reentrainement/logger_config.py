"""
Module : logger_config.py
-------------------------
Configuration industrielle du Logging et Journalisation Structurée pour CliNER-MLOps.
Conforme aux standards d'ingénierie logicielle (Guide Stéphane Robert) :
- Handlers : StreamHandler (console) + RotatingFileHandler (rotation 5 Mo / 5 archives).
- Formatage standardisé avec horodatage, sévérité, module et ligne de code.
- Générateur de journaux d'exécution médico-légaux au format XML (traçabilité HDS/RGPD).
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Optional

# Répertoire central des logs
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)

DEFAULT_LOG_FILE = os.path.join(LOGS_DIR, "cliner_api.log")
DEFAULT_XML_DIR = os.path.join(LOGS_DIR, "execution_journals")
os.makedirs(DEFAULT_XML_DIR, exist_ok=True)


def get_logger(name: str = "cliner_mlops", log_file: str = DEFAULT_LOG_FILE, level: int = logging.INFO) -> logging.Logger:
    """
    Crée ou retourne un logger configuré avec sortie Console et RotatingFileHandler.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    # Format standardisé : Date/Heure | Niveau | Logger | [Fichier:Ligne] | Message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | [%(filename)s:%(lineno)d] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler (Max 5 Mo, 5 fichiers de rotation = 25 Mo max)
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[WARN] Impossible d'initialiser RotatingFileHandler sur {log_file}: {e}")

    return logger


def export_execution_xml(
    execution_id: str,
    status: str,
    steps: Optional[List[Dict[str, Any]]] = None,
    stage: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    output_dir: str = DEFAULT_XML_DIR
) -> str:
    """
    Génère un journal d'exécution structuré au format XML pour traçabilité médico-légale et audit.
    
    Args:
        execution_id: Identifiant unique de l'exécution (ex: 'run_20260921_143000')
        status: Statut global ('SUCCESS', 'WARNING', 'FAILED', 'ERROR')
        steps: Liste de dictionnaires décrivant chaque étape : [{'name': ..., 'status': ..., 'latency_ms': ...}]
        stage: Nom de l'étape unique si appel ponctuel (API)
        details: Détails supplémentaires pour l'étape unique
        metrics: Métriques clés (loss, f1_score, precision, drift_score, latency_sec)
        metadata: Métadonnées environnement (OS, version python, worker)
        output_dir: Répertoire de sauvegarde
        
    Returns:
        str: Chemin absolu du fichier XML généré.
    """
    root = ET.Element("PipelineExecution")
    root.set("id", execution_id)
    root.set("status", status)
    root.set("timestamp", datetime.now(timezone.utc).isoformat())

    # Environnement / Métadonnées
    env_node = ET.SubElement(root, "Environment")
    env_meta = metadata or {}
    env_node.set("python_version", sys.version.split()[0])
    env_node.set("platform", sys.platform)
    for k, v in env_meta.items():
        env_node.set(str(k), str(v))

    # Normalisation des étapes
    step_list: List[Dict[str, Any]] = []
    if steps:
        step_list.extend(steps)
    elif stage:
        single_step = {"name": stage, "status": status}
        if details:
            single_step.update(details)
        step_list.append(single_step)

    # Étapes d'exécution
    steps_node = ET.SubElement(root, "ExecutionSteps")
    for step in step_list:
        s_elem = ET.SubElement(steps_node, "Step")
        s_elem.set("name", str(step.get("name", "unknown_step")))
        s_elem.set("status", str(step.get("status", "SUCCESS")))
        if "latency_ms" in step:
            s_elem.set("latency_ms", f"{float(step['latency_ms']):.2f}")
        for k, v in step.items():
            if k not in ["name", "status", "latency_ms"]:
                s_elem.set(str(k), str(v))

    # Métriques
    if metrics:
        metrics_node = ET.SubElement(root, "Metrics")
        for k, v in metrics.items():
            m_elem = ET.SubElement(metrics_node, "Metric")
            m_elem.set("name", str(k))
            m_elem.set("value", str(v))

    # Formatage XML lisible avec indentation
    xml_str = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(xml_str)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    # Écriture dans le fichier horodaté
    xml_filename = f"{execution_id}.xml"
    xml_path = os.path.join(output_dir, xml_filename)
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    # Sauvegarde également sous le nom 'latest_execution.xml' pour consultation rapide via API
    latest_path = os.path.join(output_dir, "latest_execution.xml")
    try:
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
    except Exception:
        pass

    return xml_path
