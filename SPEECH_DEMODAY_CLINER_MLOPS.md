# SPEECH DEMO DAY - CliNER-MLOps
**Formation Architecte en Intelligence Artificielle - RNCP 41993 Niveau 7**  
**Équipe :** Patrick Mouliom • Christopher Gilleron • Arnaud Hoarau • Karim Atebata  
**Format :** 4 orateurs × 2 minutes = 8 minutes chrono (Découpage exact sur les 6 slides)

> **Repère d'élocution :** ~270 mots par orateur = exactement 2 minutes à un rythme naturel et posé (~135-140 mots/min).  
> **Conseil clé :** Marquez une pause silencieuse d'une seconde après les chiffres percutants (*« 80 % »*, *« 3 secondes »*, *« 0,17 € »*).

---

## ORATEUR 1 — Slides 1 & 2 (00:00 ➔ 02:00)
### *Titre, Contexte & Pourquoi ce projet ? Un problème qui coûte des vies !*

---

**[SLIDE 1 — Titre & Mission]**  
Bonjour à toutes et à tous.

Aujourd'hui, nous vous présentons **CliNER** : une intelligence artificielle clinique conçue pour résoudre l'un des plus grands goulots d'étranglement de la médecine moderne : **trouver le bon essai clinique pour le bon patient, en 3 secondes au lieu de 45 minutes.**

**[SLIDE 2 — Le Problème & La Solution CliNER]**  
Pour comprendre l'enjeu, imaginez un médecin oncologue face à un patient atteint d'un cancer agressif en échec thérapeutique. Un traitement novateur existe peut-être dans un essai clinique à 50 km de là. Mais personne ne le sait.

Pourquoi ? Parce qu'il existe aujourd'hui **450 000 essais cliniques dans le monde**, et que chaque protocole fait **100 à 200 pages de jargon médico-légal en anglais**. Pour un seul patient, le médecin devrait passer **45 minutes** à éplucher 40 critères d'inclusion et d'exclusion. En consultation de 15 minutes, c'est tout simplement impossible.

Résultat : **80 % des essais cliniques mondiaux sont en retard de recrutement**. Des cohortes restent à moitié vides, et des molécules prometteuses sont abandonnées avant même d'avoir pu sauver des vies.

On pourrait penser : *"Pourquoi ne pas donner ces PDF à ChatGPT ?"*  
C'est impensable en médecine : une IA généraliste invente des posologies, ignore les négations critiques, et surtout, envoie des données de santé confidentielles sur des serveurs étrangers.

**Voici ce que CliNER change :**  
En **3 secondes**, notre IA lit le protocole officiel, extrait chirurgicalement chaque critère d'éligibilité, et fournit au médecin un tableau clair et structuré.  
* **Zéro invention** : le modèle ne cite que le texte légal vérifié.  
* **100 % souverain** : toutes les données restent en France, dans le respect strict du RGPD et des normes de santé.

Mais le plus parlant, c'est de le voir en direct. Je passe la parole pour la démonstration de l'application !

---

## ORATEUR 2 — Slide 3 (02:00 ➔ 04:00)
### *Démonstration Live — L'application en action sur le terrain*

---

**[SLIDE 3 — Démonstration Live - Voyez par vous-même !]**  
*(L'orateur projette et manipule l'interface Streamlit en direct)*

Merci ! Mettons-nous immédiatement dans la peau du médecin hospitalier.

**[Action 1 — Recherche en temps réel]**  
Je me connecte sur l'interface sécurisée de CliNER. Dans la barre de recherche, je tape la pathologie de mon patient, par exemple : *"Cancer du poumon"*.  
En temps réel et en un quart de seconde, CliNER interroge la base mondiale officielle **ClinicalTrials.gov V2**. Sans réveiller de GPU lourd, il identifie instantanément toutes les études ouvertes au recrutement.

**[Action 2 — Le tableau interactif]**  
Le praticien visualise un tableau synthétique complet : identifiant officiel NCT, statut de recrutement, phase clinique et molécules testées. Il peut filtrer et trier d'un clic pour repérer l'étude la plus prometteuse pour son patient.

**[Action 3 — L'extraction NER en 3 secondes]**  
C'est ici que la magie de notre IA opère. Le médecin clique sur un essai pour lancer l'analyse du protocole.  
Regardez le chrono : **1... 2... 3 secondes.**  
Au lieu de forcer le praticien à lire 150 pages de document brut, CliNER a extrait et segmenté automatiquement tous les critères clés :  
* En vert, les **conditions médicales** requises (*cancer non à petites cellules, stade IV*).  
* Les **médicaments et thérapies préalables** autorisés.  
* Les **seuils biologiques stricts** : la fonction rénale, le taux de plaquettes, l'âge.  
* Et en rouge, les **contre-indications absolues** qui éliminent immédiatement un risque pour le malade.

**[Action 4 — L'assistant conversationnel médical]**  
Et si le médecin a un doute spécifique, il pose sa question en langage naturel à notre assistant RAG :  
*« Mon patient a 72 ans et un diabète de type 2, est-il éligible ? »*  
L'assistant répond en 1 seconde et lui surligne le paragraphe exact du document officiel, sans aucune hallucination.

Le gain est immédiat : 45 minutes d'examen de dossier ramenées à 3 secondes.  
Mais comment ce système fonctionne-t-il sous le capot ? Je passe la parole pour vous dévoiler le circuit complet de la donnée.

---

## ORATEUR 3 — Slide 4 (04:00 ➔ 06:00)
### *Comment ça marche ? — Le circuit complet de la donnée*

---

**[SLIDE 4 — Schéma d'architecture vulgarisé plein écran]**  
Merci ! Derrière cette interface intuitive se cache une architecture d'ingénierie moderne pensée autour de deux circuits complémentaires.

**[1. Le Circuit Supérieur : L'expérience du médecin en direct]**  
Regardons d'abord le flux du haut : c'est ce qui se passe quand le médecin clique sur *"Chercher"*.
1. **L'accès :** La requête part de l'application Streamlit vers notre orchestrateur central FastAPI.
2. **Le coffre-fort :** Le protocole complet est archivé dans notre Data Lake AWS S3, un stockage sécurisé garantissant la conservation réglementaire des données médicales sur 15 à 25 ans.
3. **Le duo d'IA (Le secret de notre rapidité) :**  
   Au lieu de saturer un gros modèle avec 150 pages, nous utilisons un premier modèle ultra-rapide, **BioBERT**, couplé à une base vectorielle. En **12 millisecondes**, il élimine 98 % du texte administratif inutile pour n'isoler que les 2 paragraphes d'éligibilité.
4. **L'expert clinique :** Ces 2 paragraphes sont transmis à notre modèle de langage spécialisé **Qwen 7B**, adapté par nos soins. En **3 secondes**, il restitue les critères parfaitement formatés en JSON.

**[2. Le Circuit Inférieur : La boucle d'amélioration automatique (MLOps)]**  
Mais une IA médicale ne doit jamais devenir obsolète. C'est tout le rôle de notre pipeline MLOps automatisé, visible en bas :
* Chaque semaine, un robot planifié interroge les nouveaux essais mondiaux.
* Notre algorithme de détection de dérive — la distance mathématique de **Wasserstein** — vérifie si le vocabulaire de la médecine évolue : de nouvelles molécules, de nouveaux variants de maladies.
* Si une dérive est détectée, le système réveille automatiquement un serveur GPU dans le cloud pour **réentraîner l'IA en 20 minutes chrono**.
* Et tout cela respecte une stricte démarche **FinOps** : ce réentraînement hebdomadaire nous coûte seulement **0,17 €**, soit moins que le prix d'un café !
* Les performances sont tracées sur MLflow, validées par une batterie de 9 tests automatisés, et le modèle mis à jour est redéployé sans aucune interruption pour les hôpitaux.

Je laisse la parole pour vous expliquer pourquoi notre moteur NER ne se trompe jamais sur les critères médicaux, et nos perspectives en production.

---

## ORATEUR 4 — Slides 5 & 6 (06:00 ➔ 08:00)
### *Le Secret du NER, Améliorations en Production & Clôture*

---

**[SLIDE 5 — Le Secret du NER & Améliorations Envisagées]**  
Merci ! Le cœur scientifique de notre projet, c'est le **NER** : la Reconnaissance d'Entités Médicales.

**Pourquoi une IA classique échoue sans NER ?**  
Si vous donnez 150 pages d'un bloc à un LLM classique, il se noie. Il confond une inclusion avec une contre-indication. Pire : il rate les négations, par exemple en lisant *"le patient ne doit pas avoir d'antécédent cardiaque"* comme une autorisation d'entrer dans l'essai. En médecine, une telle erreur peut être fatale.

**Avec notre NER chirurgical :**  
Notre modèle a été entraîné sur le standard mondial **CHIA**, composé de 1 000 protocoles annotés manuellement par des médecins de Columbia University.  
L'IA isole chaque entité dans son contexte : la pathologie, la molécule, la posologie, le seuil biologique.  
* **Résultat :** **58,3 % de F1-score strict** sur les critères les plus complexes, soit **+31 % de précision** par rapport à une IA généraliste, avec **zéro hallucination**.

**Et pour demain ? Les améliorations envisagées en production :**  
1. **Sur-spécialisation par domaine :** Grâce à des adaptateurs LoRA légers de quelques mégaoctets, créer des modules experts par spécialité (cardiologie, oncologie, neurologie) pour dépasser 75 % de précision.
2. **Connexion directe au Dossier Patient (DPI) :** Relier CliNER aux logiciels hospitaliers (comme Orbis) pour matcher automatiquement les patients dès leur admission.
3. **Alertes en temps réel :** Notifier automatiquement le médecin dès qu'un nouvel essai compatible s'ouvre dans le monde.
4. **Déploiement On-Premise :** Installer le modèle directement sur les serveurs internes de l'hôpital, pour un fonctionnement 100 % hors ligne sans dépendance au cloud.

**[SLIDE 6 — Remerciements & Clôture]**  
Pour conclure, CliNER prouve qu'avec une ingénierie MLOps rigoureuse, l'intelligence artificielle peut redonner du temps précieux aux soignants, débloquer les essais cliniques, et surtout, apporter plus vite des traitements vitaux aux patients.

Un grand merci de la part de toute notre équipe — Patrick, Christopher, Arnaud et Karim.  
Nous sommes désormais à votre entière disposition pour répondre à toutes vos questions !

---

## ⏱️ Grille Récapitulative du Déroulement (8 min)

| Participant | Slides | Timing | Rôle & Focus Clé |
| :--- | :---: | :---: | :--- |
| **Orateur 1** | **Slide 1 & 2** | `00:00 ➔ 02:00` | **Le Choc du Problème :** 80% des essais en retard, 150 pages de protocole, 45 min par patient, la promesse CliNER (3 secondes, souverain). |
| **Orateur 2** | **Slide 3** | `02:00 ➔ 04:00` | **La Démo Live :** Recherche instantanée ClinicalTrials.gov, filtrage du tableau, extraction NER des critères en 3s, question au RAG. |
| **Orateur 3** | **Slide 4** | `04:00 ➔ 06:00` | **L'Architecture & Circuit de la Donnée :** Flux 1 (BioBERT 12 ms + Qwen LoRA 3s + S3) & Flux 2 (Boucle MLOps automatique à 0,17 €). |
| **Orateur 4** | **Slide 5 & 6** | `06:00 ➔ 08:00` | **Le Secret du NER & Avenir :** Pourquoi pas de risque d'erreur, CHIA 58.3%, LoRA par spécialité, intégration DPI hospitalier & Clôture équipe. |
