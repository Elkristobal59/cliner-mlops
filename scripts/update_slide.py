import os

html_path = os.path.join("docs", "demoday_soutenance.html")
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """<section>
            <h2>Architecture RAG : BioBERT x Qwen</h2>
            <div class="mermaid">
flowchart TD
    %% Couleurs et Styles
    classDef input fill:#f8f9fa,stroke:#ced4da,stroke-width:2px,color:#212529;
    classDef biobert fill:#d1e7dd,stroke:#0f5132,stroke-width:2px,color:#0f5132;
    classDef qwen fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#856404;
    classDef output fill:#cff4fc,stroke:#055160,stroke-width:2px,color:#055160;
    classDef script fill:#e2e3e5,stroke:#383d41,stroke-width:2px,color:#383d41;

    %% Composants
    A["📄 Document Source - (Fichier .txt ou PDF parsé)"]:::input
    B["🤖 BioBERT (Retriever) - Recherche Vectorielle"]:::biobert
    C["🧠 Qwen 7B (Generator) - Fine-Tuné sur CHIA"]:::qwen
    D["⚙️ remap_offsets.py - (Script Python)"]:::script
    E["📋 Format Final BRAT - (Fichier .ann)"]:::output

    %% Flux de données
    A -- "Texte Brut Complet - (ex: 50 pages)" --> B
    B -- "Vecteurs & Filtrage" --> B
    B -- "Chunks Pertinents - (ex: 3 paragraphes)" --> C
    C -- "Prompt + Chunks" --> C
    C -- "Extraction Structurée - (Fichier .json)" --> D
    A -. "Texte Brut Original" .-> D
    D -- "Calcul des coordonnées (Offsets)" --> E
            </div>
            <p style="font-size: 16px; margin-top: 20px;">Le texte brut est filtré par BioBERT, puis classifié au format JSON par Qwen Fine-Tuné.</p>
        </section>"""

new_block = """<section>
            <h2>Architecture RAG Hybride : IA x Algorithmique</h2>
            <div class="mermaid">
flowchart TD
    %% Couleurs et Styles
    classDef input fill:#f8f9fa,stroke:#ced4da,stroke-width:2px,color:#212529;
    classDef biobert fill:#d1e7dd,stroke:#0f5132,stroke-width:2px,color:#0f5132;
    classDef qwen fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#856404;
    classDef tfidf fill:#f2dede,stroke:#a94442,stroke-width:2px,color:#a94442;
    classDef output fill:#cff4fc,stroke:#055160,stroke-width:2px,color:#055160;
    classDef script fill:#e2e3e5,stroke:#383d41,stroke-width:2px,color:#383d41;

    %% Source
    A["📄 Document Protocole Clinique<br>(Fichier .txt ou PDF parsé)"]:::input

    %% Branche 1 : IA / NER Qwen
    B["🤖 BioBERT (Retriever)<br>Recherche Vectorielle (top-K=15)"]:::biobert
    C["🧠 Qwen 7B (Generator)<br>Fine-Tuné QLoRA (75 tokens/s)"]:::qwen
    D["⚙️ remap_offsets.py<br>(Script Python)"]:::script
    E["📋 Format BRAT (.ann)<br>Score F1 : 58.3%"]:::output

    %% Branche 2 : TF-IDF / Éligibilité
    T["📐 Module Algorithmique TF-IDF<br>Découpage exact (0% Hallucination)"]:::tfidf
    F["✨ Interface Streamlit / API<br>JSON Consolidé Patient"]:::output

    %% Flux Branche 1 (NER)
    A -- "Branche 1 : Texte Brut<br>(chunk_size=2000)" --> B
    B -->|"Chunks Pertinents"| C
    C -->|"JSON : condition & medications"| D
    D --> E
    D -->|"Entités NER"| F

    %% Flux Branche 2 (TF-IDF)
    A -- "Branche 2 : Texte Intégral<br>(Paragraphes d'éligibilité)" --> T
    T -->|"Texte exact : inclusion_criteria"| F
            </div>
            <p style="font-size: 15px; margin-top: 15px;"><b>Séparation en 2 branches :</b> L'IA (Qwen 7B) s'occupe de l'extraction chirurgicale NER, tandis que l'algorithme TF-IDF sécurise l'extraction exacte des critères d'éligibilité sans hallucination.</p>
        </section>"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Updated demoday_soutenance.html successfully!")
else:
    print("ERROR: Could not find old_block exact match in demoday_soutenance.html!")
    # Let's try searching for a substring
    idx = content.find("Architecture RAG : BioBERT x Qwen")
    if idx != -1:
        print("Found title at index:", idx)
