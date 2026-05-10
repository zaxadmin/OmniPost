import streamlit as st
from supabase import create_client
from ai_engine import generate_job_description, analyze_cv_with_ai

# Connexion invisible à la base de données
supabase = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

# Détection du mode (Candidat ou Employeur)
is_candidat = st.query_params.get("view") == "candidat"

if is_candidat:
    # --- VUE CANDIDAT ---
    st.title("🚀 Postuler à l'offre")
    nom = st.text_input("Votre Nom complet")
    cv_txt = st.text_area("Collez votre CV ici")
    
    if st.button("Soumettre ma candidature"):
        # Analyse silencieuse
        res = analyze_cv_with_ai(cv_txt, "Offre en cours")
        supabase.table("candidatures").insert({
            "nom_candidat": nom, "cv_texte": cv_txt, "score_matching": res['score']
        }).execute()
        st.success("Candidature envoyée ! L'employeur vous contactera si votre profil est retenu.")

else:
    # --- VUE EMPLOYEUR (Dashboard OmniPost) ---
    st.title("💼 Dashboard OmniPost")
    t1, t2 = st.tabs(["📢 Créer une offre", "📂 Candidatures & Pouce Orange"])
    
    with t1:
        titre = st.text_input("Titre du poste")
        if st.button("🪄 Rédiger avec l'IA"):
            st.session_state.desc = generate_job_description(titre)
        st.text_area("Description de l'offre", value=st.session_state.get('desc', ''), height=250)

    with t2:
        st.subheader("Sélection des candidats")
        data = supabase.table("candidatures").select("*").order("score_matching", desc=True).execute()
        for c in data.data:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"**{c['nom_candidat']}**")
            col2.write(f"Score : {c['score_matching']}%")
            # LE POUCE ORANGE
            if col3.button("🟠 Valider", key=c['id']):
                supabase.table("candidatures").update({"status": "valide"}).eq("id", c['id']).execute()
                st.toast(f"{c['nom_candidat']} validé !")
