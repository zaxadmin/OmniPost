import pdfminer.high_level
import io

class OmniPostParser:
    def extract_text_from_pdf(self, pdf_file):
        try:
            # On lit directement le binaire envoyé par Streamlit
            text = pdfminer.high_level.extract_text(io.BytesIO(pdf_file.getvalue()))
            return text.lower()
        except Exception as e:
            st.error(f"Erreur de lecture PDF : {e}")
            return ""

    def save_parsed_cv(self, candidate_id, text_content):
        # On sauvegarde le texte brut dans ZIP pour que l'IA puisse le relire plus tard
        from candidate_manager import get_zip_client
        zip_client = get_zip_client()
        zip_client.table("cv_data").upsert({
            "candidate_id": candidate_id,
            "raw_text": text_content
        }).execute()
