class Analyst:
  def analyze_image(self, image_path):
    # 1. Gather Metadata & Physical Traits
    subject = self._get_subject_labels(image_path)
    p_type = self._get_painting_type(image_path)

    # 2. Run Forensic Scans
    ai_signatures = self._detect_ai_artifacts(image_path)

    # 3. Package for the Historian
    dossier = {
        "subject_label": subject,
        "painting_type": p_type,
        "ai_attribution": ai_signatures,
        "phash": self._generate_phash(image_path),
        "forensic_flags": self._get_flags()
    }
return dossier
