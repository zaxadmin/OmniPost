import streamlit as st
from supabase import create_client
from ai_engine import coach_ia, generate_offer
from fpdf import FPDF

# 1. CONNEXION
supabase = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

# 2. PARAMÈTRES
is_candidat = st.query_params.get("view") == "candidat"
user_email = st.query_params.get("user", "invite@zaxx.app")

if is_candidat:
    st.title("🚀 Mon Assistant Carrière Zaxx")
    menu = st.tabs(["📊 Suivi", "🪄 Coach IA & ATS", "📁 Mon Tiroir"])

    with menu[1]:
        st.subheader("Optimisation ATS & Relooking")
        cv = st.text_area("Collez votre CV actuel")
        mode = st.selectbox("Objectif", ["Relooker (Style & Impact)", "Lettre de Motivation", "Adapter à une offre (Passer l'ATS)"])
        ctx = st.text_input("Collez l'offre d'emploi ou le métier visé") if mode != "Relooker (Style & Impact)" else ""
        
        if st.button("🪄 Transformer mon CV"):
            action_key = "relook" if "Relooker" in mode else ("lettre" if "Lettre" in mode else "adapt")
            with st.spinner("L'IA optimise votre profil pour les recruteurs et les robots ATS..."):
                res = coach_ia(cv, action_key, ctx)
                st.session_state.temp_doc = res
                st.markdown(res)
            
            if st.button("💾 Sauvegarder dans mon Tiroir"):
                supabase.table("tiroir_documents").insert({"user_email": user_email, "type_doc": mode, "contenu": res}).execute()

    with menu[2]:
        st.subheader("📁 Mes Documents & Templates")
        docs = supabase.table("tiroir_documents").select("*").eq("user_email", user_email).execute()
        
        for d in docs.data:
            with st.expander(f"{d['type_doc']} - {d['date_creation']}"):
                st.write(d['contenu'])
                
                # --- SYSTÈME DE TEMPLATES ---
                st.write("---")
                template = st.radio(f"Choisir un style pour ce document :", ["Classique (Sobre)", "Moderne (Épuré)", "Impact (Gras)"], key=f"t_{d['id']}")
                
                if st.download_button(f"📥 Télécharger en mode {template}", data="", file_name="cv_zaxx.pdf", key=f"dl_{d['id']}"):
                    # Logique PDF simplifiée selon le template choisi
                    pdf = FPDF()
                    pdf.add_page()
                    if template == "Classique (Sobre)":
                        pdf.set_font("Arial", size=11)
                    elif template == "Moderne (Épuré)":
                        pdf.set_font("Courier", size=10)
                    else:
                        pdf.set_font("Helvetica", 'B', size=12)
                    
                    pdf.multi_cell(0, 10, txt=d['contenu'].encode('latin-1', 'ignore').decode('latin-1'))
                    # Ici Streamlit gère le téléchargement via le bouton au-dessus
