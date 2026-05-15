class Analyst:
  def analyze_image(self, image_path):
    subject = self._get_subject_labels(image_path)
    p_type = self._get_painting_type(image_path)
