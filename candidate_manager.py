import streamlit as st
from supabase import create_client

# Ce gestionnaire utilise le projet ZIP
def get_zip_client():
    return create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])

def get_all_candidates():
    client = get_zip_client()
    return client.table("profiles").select("*").eq("role", "candidat").execute()
