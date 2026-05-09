from multiposter import get_op_client
from candidate_manager import get_zip_client

def match_candidats_offre(offre_id):
    op_client = get_op_client()
    zip_client = get_zip_client()
    
    # 1. On récupère l'offre sur OP-
    offre = op_client.table("annonces").select("*").eq("id", offre_id).single().execute()
    
    # 2. On récupère les candidats sur ZIP
    candidats = zip_client.table("profiles").select("*").eq("role", "candidat").execute()
    
    # Logique de scoring (ton code existant dans processor.py peut être appelé ici)
    return "Analyse en cours..."
