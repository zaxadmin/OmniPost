import streamlit as st
from supabase import create_client

# Connexion directe à OP- via les secrets GitHub du dépôt zip
def get_op_client():
    return create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

def publish_to_all(job_details):
    client = get_op_client()
    # Logique pour envoyer vers les API (LinkedIn, Indeed, etc.)
    # Et sauvegarde dans la table 'annonces' de OP-
    try:
        client.table("annonces").insert(job_details).execute()
        st.success("Annonce multidiffusée et enregistrée dans OP-")
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement dans OP- : {e}")
