import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from datetime import datetime, timezone
import numpy as np
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset
from evidently.ui.workspace import RemoteWorkspace
from evidently.ui.dashboards import DashboardPanelPlot, PanelMetric

UI_URL = "http://localhost:8000"
print(f"Connexion au serveur Evidently UI sur {UI_URL}...")

try:
    ws = RemoteWorkspace(UI_URL)
    projects = ws.search_project("chris")
    if not projects:
        projects = ws.search_project("cliner_monitoring")
    
    if projects:
        project = projects[0]
        print(f"Projet existant trouvé : '{project.name}' (ID: {project.id})")
    else:
        project = ws.create_project("cliner_monitoring")
        project.description = "Surveillance continue du Data Drift sur les protocoles cliniques (CliNER-MLOps)"
        project.save()
        print(f"Nouveau projet créé : '{project.name}' (ID: {project.id})")

    # 1. Données de référence (Gold Standard CHIA)
    np.random.seed(42)
    n_samples = 60
    ref_df = pd.DataFrame({
        "char_count": np.random.normal(450, 80, n_samples).clip(150, 900),
        "word_count": np.random.normal(70, 15, n_samples).clip(20, 150),
        "avg_word_len": np.random.normal(6.2, 0.4, n_samples),
        "digit_ratio": np.random.normal(0.04, 0.015, n_samples).clip(0.01, 0.12),
        "uppercase_ratio": np.random.normal(0.06, 0.02, n_samples).clip(0.01, 0.15),
    })

    # 2. Données de production (avec dérive mesurée)
    prod_df = pd.DataFrame({
        "char_count": np.random.normal(620, 110, n_samples).clip(200, 1100),
        "word_count": np.random.normal(95, 20, n_samples).clip(30, 200),
        "avg_word_len": np.random.normal(6.8, 0.5, n_samples),
        "digit_ratio": np.random.normal(0.08, 0.025, n_samples).clip(0.02, 0.20),
        "uppercase_ratio": np.random.normal(0.09, 0.03, n_samples).clip(0.02, 0.22),
    })

    # 3. Calcul du rapport
    print("Calcul du rapport Data Drift...")
    data_report = Report(
        [
            DataDriftPreset(drift_share=0.3, method="psi", threshold=0.2),
            DataSummaryPreset(),
        ],
        include_tests=True,
    )

    report_run = data_report.run(
        reference_data=ref_df,
        current_data=prod_df,
        timestamp=datetime.now(timezone.utc),
    )

    # 4. Ajout du run au Workspace
    report_ref = ws.add_run(
        project.id,
        report_run,
        include_data=True,
        name="Protocole Run 1 — Nouveaux essais cliniques",
    )
    print(f"✅ Snapshot enregistré dans le Workspace : {report_ref.id}")

    # 5. Configuration des Panneaux du Dashboard
    project = ws.get_project(str(project.id))
    existing_titles = {panel.title for panel in project.dashboard.model().panels}

    panels = [
        DashboardPanelPlot(
            title="Nombre de protocoles analysés",
            size="half",
            values=[PanelMetric(legend="Protocoles", metric="RowCount")],
            plot_params={"plot_type": "line"},
        ),
        DashboardPanelPlot(
            title="Proportion de caractéristiques en dérive (Drift Share)",
            size="half",
            values=[PanelMetric(
                metric="DriftedColumnsCount",
                metric_labels={"value_type": "share"},
                legend="Part de dérive (0 à 1)",
            )],
            plot_params={"plot_type": "line"},
        ),
    ]

    for panel in panels:
        if panel.title not in existing_titles:
            project.dashboard.add_panel(panel, tab="Summary")

    project.save()
    print("✅ Panneaux du Dashboard configurés avec succès !")
    print("\n👉 Vous pouvez maintenant rafraîchir (F5) la page http://localhost:8000 dans votre navigateur !")

except Exception as e:
    print(f"Erreur : {e}", file=sys.stderr)
    raise
