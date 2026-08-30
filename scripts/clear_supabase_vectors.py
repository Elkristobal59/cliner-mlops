import os
import psycopg2
from dotenv import load_dotenv

def clear_vector_db():
    load_dotenv()
    db_url = os.getenv("SUPABASE_DATABASE_URL")
    if not db_url:
        print("❌ Erreur : SUPABASE_DATABASE_URL introuvable dans le fichier .env")
        return

    try:
        print("🔌 Connexion à Supabase...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Compter le nombre de lignes avant
        cur.execute("SELECT count(*) FROM clinical_trials_data_biobert")
        count_before = cur.fetchone()[0]
        print(f"📊 Nombre de chunks actuels (pollués) : {count_before}")

        # Vider la table
        print("🗑️ Vidage de la table vectorielle en cours...")
        cur.execute("TRUNCATE TABLE clinical_trials_data_biobert;")
        conn.commit()

        print("✅ Base de données vectorielle nettoyée avec succès !")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erreur lors du nettoyage : {e}")

if __name__ == "__main__":
    confirm = input("⚠️ Attention, cela va effacer TOUS les anciens vecteurs de la base Supabase. Continuer ? (o/n) : ")
    if confirm.lower() == 'o':
        clear_vector_db()
    else:
        print("Annulé.")
