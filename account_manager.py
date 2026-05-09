import streamlit as st
from supabase import create_client

def update_active_email(new_email):
    # On sauvegarde la config dans la table 'settings' de OP-
    supabase_op = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])
    try:
        supabase_op.table("settings").upsert({
            "key": "active_sender_email", 
            "value": new_email,
            "updated_by": st.session_state.user['id']
        }).execute()
        st.success(f"📧 Email de diffusion mis à jour : {new_email}")
    except Exception as e:
        st.error(f"Erreur de mise à jour : {e}")
