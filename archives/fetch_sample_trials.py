import requests
import json
import os

def main():
    output_dir = os.path.join("data", "sample_studies_jeremie")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Téléchargement de 10 études cliniques complètes depuis l'API de ClinicalTrials.gov...")
    
    # On récupère 10 études au hasard (API v2)
    url = "https://clinicaltrials.gov/api/v2/studies?pageSize=10"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        studies = data.get("studies", [])
        
        for study in studies:
            # Récupérer le NCT ID pour nommer le fichier
            nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "UNKNOWN")
            
            file_path = os.path.join(output_dir, f"{nct_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(study, f, indent=4, ensure_ascii=False)
            print(f" - Enregistré : {nct_id}.json")
            
        print(f"\n✅ Terminé ! Tu peux trouver les 10 fichiers JSON dans le dossier : {output_dir}")
    else:
        print(f"Erreur lors de l'appel à l'API: {response.status_code}")

if __name__ == "__main__":
    main()
