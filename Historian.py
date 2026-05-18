import mysql.connector
from mysql.connector import Error

class Historian:
    def __init__(self):
        """Initializes the connection to the MySQL database."""
        try:
            # Replace these credentials with your actual local MySQL setup
            self.connection = mysql.connector.connect(
                host='localhost',
                database='curator_db',
                user='root',
                password='your_password'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Historian: Connected to MySQL Records.")
        except Error as e:
            print(f"Historian Database Connection Error: {e}")
            self.connection = None

    def audit_dossier(self, dossier):
        """
        Takes the Analyst's dossier and cross-references it with MySQL records.
        Returns a verdict string and an updated results payload.
        """
        if not self.connection:
            return "ERROR: No Database Connection", dossier

        phash = dossier["phash"]
        subject_label = dossier["subject_label"]

        # Step 1: Check for an exact or near-exact match using the pHash
        # We look in the synthetic register first for your AI pieces
        query = "SELECT * FROM synthetic_register WHERE p_hash = %s"
        self.cursor.execute(query, (phash,))
        match = self.cursor.fetchone()

        if match:
            # Step 2: Subject exists. Let's compare the deep details for duplication.
            # We compare what the Analyst found vs what was recorded in MySQL
            details_match = (
                match['art_style'] == dossier['art_style'] and
                match['painting_type'] == dossier['painting_type']
            )
            
            if details_match:
                verdict = "CONFIRMED_DUPLICATE"
                dossier["status_notes"] = f"Matches existing record ID #{match['id']} perfectly."
            else:
                verdict = "TAMPERED_VERSION"
                dossier["status_notes"] = "Subject match found, but internal attributes have been altered."
            
            return verdict, dossier

        # Step 3: If no pHash match in synthetic, check the primary vault (Real Art)
        query = "SELECT * FROM primary_register WHERE p_hash = %s"
        self.cursor.execute(query, (phash,))
        real_match = self.cursor.fetchone()

        if real_match:
            return "CONFIRMED_REAL", dossier

        # Step 4: If it's completely missing from both, it's a brand new subject entry
        return "NEW_SUBJECT", dossier

if __name__ == "__main__":
    print("--- RUNNING HISTORIAN TEST (MOCK DOSSIER) ---")
    
    # This simulates exactly what your analyst.py outputs
    mock_dossier = {
        "subject_label": 'Subject: "Fictional Human"',
        "painting_type": "Portrait",
        "art_style": "18th-Century Neoclassicism",
        "ai_attribution": {"Stable Diffusion": 70, "Grok": 30},
        "phash": "9f8e7d6c5b4a3f2e",
        "forensic_flags": ["FFT_Pattern_Detected"]
    }
    
    historian = Historian()
    
    if historian.connection:
        verdict, final_data = historian.audit_dossier(mock_dossier)
        print(f"Verdict: {verdict}")
        print(f"Processed Dossier: {final_data}")
    else:
        print("\n[!] Test run skipped: Make sure MySQL is running and your credentials are correct.")
