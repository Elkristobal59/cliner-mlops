📚 Le Voyage de la Donnée : La Chaîne de Montage de CliNER (Simple & Complet)


1️⃣ ÉTAPE 1 : La Récolte des Données (0% IA • 100% Informatique classique)

📥 Ce qui entre : Les mots-clés que l'utilisateur tape sur son écran dans Streamlit (par exemple : maladie "Glioblastoma").
⚙️ Ce qu'on fait : L'application Streamlit appelle le site officiel américain des essais cliniques (ClinicalTrials.gov) pour lui demander tous les essais sur cette maladie. Le site nous envoie en retour un gros fichier informatique appelé JSON (qui ressemble à un dictionnaire géant, très difficile à lire pour un humain). Notre code Python lit ce dictionnaire et garde uniquement les cases utiles (le titre de l'essai, son identifiant, et le texte des critères d'admission).

📤 Ce qui sort : Un tableau de données propre (un DataFrame Pandas, un peu comme un tableau Excel en mémoire de l'ordinateur). Ce tableau s'affiche sur votre écran : c'est la Summary Table.

🌉 LE PONT vers l'Étape 2 (D'où vient le texte en anglais ?) : Dans ce "tableau Excel" en mémoire, chaque ligne correspond à un essai clinique. Il y a une colonne officielle qui s'appelle précisément EligibilityCriteria. Dans chaque case de cette colonne se trouve le texte brut en anglais qui explique qui peut participer à l'essai. 👉 Le Pont : Quand vous choisissez un essai dans le menu déroulant de l'Étape 2, le programme va tout simplement copier le texte en anglais qui se trouve dans la case de ce tableau pour l'envoyer à l'intelligence artificielle !

2️⃣ ÉTAPE 2 : Le Surligneur Intelligent – Le NER (🚨 C'est ICI que commence l'IA !)

📥 Ce qui entre : Le texte brut en anglais des critères d'admission (qu'on vient juste de copier de la colonne de notre tableau à la fin de l'Étape 1).

🧠 Ce qu'on fait (L'IA Qwen Fine-Tuné) : Notre grand modèle d'intelligence artificielle (Qwen) lit ce texte. Grâce à son entraînement spécifique (Fine-Tuning), son seul travail ici est de faire du surlignage automatique : il détecte, extrait et classe les mots médicaux importants (les maladies, les médicaments) sous forme d'un dictionnaire JSON strict.

📤 Ce qui sort : Une liste informatisée (un petit fichier JSON) qui dit par exemple : "Le mot 'Temozolomide' du caractère 105 au caractère 117 est un Médicament (Drug)". Sur votre écran (dans l'onglet Visualisation), l'application utilise cette liste pour colorier les mots en bleu, vert ou rouge !

🌉 LE PONT vers l'Étape 3 (Pourquoi on conserve ce résultat ?) : On ne jette rien ! À la fin de cette étape, pour chaque essai clinique, on a en mémoire de l'ordinateur un duo précieux :
Le texte brut en anglais.
La liste des mots médicaux importants surlignés par l'IA. 👉 Le Pont : Notre code prend ce duo pour aller l'enregistrer définitivement dans notre base de données afin de construire notre Chatbot !

3️⃣ ÉTAPE 3 : La Vectorisation et le Stockage dans la Base (La Mémoire du Chatbot)

Pour qu'un Chatbot puisse répondre à des questions plus tard, il ne peut pas juste lire des tableaux Excel ; il lui faut une base de données spéciale capable de comprendre le "sens" ou le thème médical des mots.

📥 Ce qui entre : Le duo (Texte brut de l'essai + Liste des mots médicaux surlignés) qu'on vient de récupérer à la fin de l'Étape 2.

🧠 Ce qu'on fait (L'IA d'Embedding BioBERT) : Avant de ranger ce texte dans la base de données, on le passe dans un modèle mathématique. Ce modèle transforme le texte médical et ses mots surlignés en une liste de 768 chiffres (par exemple : [0.014, -0.285, 0.912...]). Cette liste de chiffres s'appelle un Vecteur. C'est le code-barres du sens médical : deux textes qui parlent de la même maladie auront des listes de chiffres très proches !

📤 Ce qui sort (Ce qui est sauvegardé en base) : Une ligne écrite définitivement dans notre base de données Supabase (qui utilise l'outil pgvector pour stocker et comparer des chiffres). Chaque ligne enregistrée en base contient 3 cases : | nct_id (l'identifiant) | text_content (le texte brut) | embedding (le vecteur de 768 chiffres) |

🌉 LE PONT vers l'Étape 4 (À quoi sert cette base ?) : Cette base de données est désormais remplie et permanente. 👉 Le Pont : Quand un médecin voudra poser une question au Chatbot, le Chatbot ira chercher dans cette base les essais dont le "code-barres de chiffres" ressemble le plus à celui de la question du médecin !

4️⃣ ÉTAPE 4 : Le Chatbot RAG (L'IA Générative Qwen 2.5)
Nous sommes maintenant dans l'onglet « 4. Chatbot RAG ». C'est l'étape finale où l'on pose une question.

📥 Ce qui entre : La question que l'utilisateur écrit en français ou en anglais dans le chat (par exemple : "Quels sont les traitements pour le glioblastome ?").

🔍 Ce qu'on fait en 1er (La Recherche dans Supabase / Retrieval) :
La question de l'utilisateur est transformée par l'IA en une liste de 768 chiffres (un vecteur).

La base de données Supabase compare la liste de chiffres de la question avec toutes les listes de chiffres stockées à l'Étape 3.

Ce qui sort de la base : Supabase sélectionne et nous renvoie les 5 essais cliniques les plus pertinents par rapport au sens de la question. On récupère ainsi le vrai texte brut de ces 5 essais !

🌉 LE PONT FINAL (Comment on nourrit le grand LLM Qwen) : Le grand modèle d'IA (Qwen 2.5) ne devine pas la réponse dans le vide : il lui faut un document de lecture. 👉 Le Pont : Notre code Python prend les textes des 5 essais sortis de la base Supabase et les colle ensemble dans un seul gros paragraphe. Puis, notre code crée une consigne de lecture (qu'on appelle le Prompt) et l'envoie à Qwen :
"Bonjour Qwen, tu es un médecin expert. Voici les 5 essais cliniques officiels trouvés dans notre base de données : [Texte collé des 5 essais]. En lisant UNIQUEMENT ces 5 textes, réponds à la question suivante de l'utilisateur : Quels sont les traitements pour le glioblastome ?"

🧠 Ce qu'on fait en 2ème (La Génération via Qwen) : Le super-modèle Qwen lit la consigne, lit attentivement les 5 textes fournis, et rédige une synthèse claire.

📤 Ce qui sort (Le résultat final) : La réponse en langage naturel qui s'affiche sur votre écran, ultra-fiable et sans aucune invention, puisqu'elle est directement dictée par les textes de l'Étape 1 !