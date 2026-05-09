import streamlit as st
from supabase import create_client

def get_op_client():
    # Utilise les secrets configurés dans GitHub
    return create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

def diffuser_annonce(details_poste):
    client = get_op_client()
    try:
        # Enregistrement dans la table annonces de OP-
        result = client.table("annonces").insert(details_poste).execute()
        st.success("🚀 Annonce publiée avec succès dans l'organisation OP- !")
        return result
    except Exception as e:
        st.error(f"Erreur de publication : {e}")
        return None
