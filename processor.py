from cv_parser import OmniPostParser
from matcher import OmniPostMatcher

def process_new_candidate(pdf_file, required_skills):
    parser = OmniPostParser()
    matcher = OmniPostMatcher()

    # 1. On lit le CV
    content = parser.extract_text_from_pdf(pdf_file)
    
    # 2. On cherche les compétences
    found = parser.search_keywords(content, required_skills)
    
    # 3. On donne le verdict
    verdict = matcher.calculate_score(required_skills, found)
    
    return {
        "candidate": pdf_file,
        "matching_skills": found,
        "status": verdict
    }

# Exemple d'utilisation : 
# result = process_new_candidate("cv_jean_dupont.pdf", ["Permis B", "Anglais"])
