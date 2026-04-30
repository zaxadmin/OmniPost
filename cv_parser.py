import pdfminer.high_level

class OmniPostParser:
    """Outil de lecture automatique des fichiers CV."""

    def extract_text_from_pdf(self, pdf_path):
        """Transforme un CV PDF en texte lisible par l'IA."""
        try:
            text = pdfminer.high_level.extract_text(pdf_path)
            return text.lower() # On met tout en minuscule pour faciliter la recherche
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du PDF : {e}")
            return ""

    def search_keywords(self, cv_text, keywords):
        """Recherche les compétences clés dans le texte du CV."""
        found = []
        for word in keywords:
            if word.lower() in cv_text:
                found.append(word)
        return found
