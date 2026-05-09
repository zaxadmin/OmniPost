import streamlit as st
from supabase import create_client

def get_op_client():
    return create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

def diffuser_annonce(details_poste):
    client = get_op_client()
    try:
        # On ajoute l'ID du recruteur pour le suivi
        details_poste["recruiter_id"] = st.session_state.user.id
        result = client.table("annonces").insert(details_poste).execute()
        st.success("🚀 Diffusé sur OP- et enregistré !")
        return result
    except Exception as e:
        st.error(f"Erreur : {e}")
