import mysql.connector
from mysql.connector import Error
import json

class Registrar:
    def __init__(self):
        """Initializes the connection to the MySQL database for data logging."""
        try:
            # Match these credentials with your local MySQL setup
            self.connection = mysql.connector.connect(
                host='localhost',
                database='curator_db',
                user='root',
                password='your_password'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("Registrar: Connected to MySQL Vault Archive.")
        except Error as e:
            print(f"Registrar Database Connection Error: {e}")
            self.connection = None

    def execute_registration(self, verdict, dossier):
        """
        Takes the final verdict and commits or handles the data in MySQL 
        depending on what the Historian discovered.
        """
        if not self.connection:
            print("Registrar Error: No database connection available.")
            return False

        try:
            if verdict == "NEW_SUBJECT":
                # Check if it's an AI file based on your analyst's subject label
                if "Fictional" in dossier.get("subject_label", ""):
                    query = """
                        INSERT INTO synthetic_register 
                        (subject_label, painting_type, ai_attribution, p_hash, art_style) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    # Convert the Python dictionary breakdown to a JSON string for MySQL JSON column
                    ai_json = json.dumps(dossier.get("ai_attribution", {}))
                    
                    values = (
                        dossier.get("subject_label"),
                        dossier.get("painting_type"),
                        ai_json,
                        dossier.get("phash"),
                        dossier.get("art_style", "Unknown")
                    )
                    
                    self.cursor.execute(query, values)
                    self.connection.commit()
                    print(f"[✓] SUCCESS: Brand new synthetic asset saved to archive. ID: {self.cursor.lastrowid}")
                
                else:
                    # Logic for archiving a brand new confirmed analog/real masterpiece
                    query = """
                        INSERT INTO primary_register 
                        (subject_label, painting_type, p_hash, authenticity_score) 
                        VALUES (%s, %s, %s, %s)
                    """
                    values = (
                        dossier.get("subject_label"),
                        dossier.get("painting_type"),
                        dossier.get("phash"),
                        100 # Default pure score for clean pass
                    )
                    self.cursor.execute(query, values)
                    self.connection.commit()
                    print(f"[✓] SUCCESS: Brand new verified real asset cataloged. ID: {self.cursor.lastrowid}")

            elif verdict == "CONFIRMED_DUPLICATE":
                print(f"[!] NOTICE: Entry ignored. System bypassed saving to prevent file duplication.")

            elif verdict == "TAMPERED_VERSION":
                print(f"[⚠] WARNING: Data manipulation alert logged. No records overwritten.")

            return True

        except Error as e:
            print(f"Registrar execution failed: {e}")
            self.connection.rollback() # Undo any broken operations
            return False

if __name__ == "__main__":
    print("--- RUNNING REGISTRAR TEST ---")
    
    # A fake complete payload mimicking the outputs of your pipeline
    sample_verdict = "NEW_SUBJECT"
    sample_dossier = {
        "subject_label": 'Subject: "Fictional Human"',
        "painting_type": "Portrait",
        "art_style": "18th-Century Neoclassicism",
        "ai_attribution": {"Stable Diffusion": 70, "Grok": 30},
        "phash": "A1B2C3D4E5F67890", # Change this string between tests to avoid MySQL Duplicate errors
        "forensic_flags": ["FFT_Pattern_Detected"]
    }
    
    registrar = Registrar()
    
    if registrar.connection:
        registrar.execute_registration(sample_verdict, sample_dossier)
    else:
        print("\n[!] Test run skipped: Confirm local MySQL server configuration defaults match script.")
