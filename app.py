import streamlit as st
import requests
import base64
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTIONS ---
def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    if style == "Classique": pdf.set_font("Times", 'B', 16)
    elif style == "Moderne": pdf.set_font("Arial", 'B', 18)
    else: pdf.set_font("Courier", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

def afficher_cgv():
    st.markdown("""
    ### 📜 Conditions Générales de Vente (CGV)
    1. **Objet :** Services d'optimisation de carrière (zipngo).
    2. **Tarifs :** Candidat 6€/3mois | Recruteur 39€/mois.
    3. **Gestion profil :** Accès actif 3 mois, puis mise en veille automatique.
    4. **Limites Gratuit :** 1 CV optimisé/mois, 1 campagne/mois.
    5. **Données :** Collecte minimale. Aucune revente à des tiers.
    """)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.info("Bienvenue sur zipngo. Utilisez votre espace dédié pour gérer votre carrière ou vos recrutements.")
    
    st.markdown("---")
    with st.expander("📜 Lire les Conditions Générales de Vente"):
        afficher_cgv()
    
    st.checkbox("J'accepte les Conditions Générales de Vente", key="accept_cgv")

    st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        © 2026 zipngo.zaxx.app<br>
        <strong>Créatrice : Liliane RAKOTOBE</strong> | 
        <a href='mailto:creationsites06@gmail.com'>📧 Contact</a>
    </div>
    """, unsafe_allow_html=True)

with tab_candidat:
    st.header("Mon Espace Candidat")
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🚀 Campagne"])
    
    with dossiers[0]: # 📂 Candidatures
        st.subheader("📊 Mon Statut & Offres")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🟢 Accès Gratuit")
            st.write("• 1 CV optimisé / mois\n• 1 campagne / mois\n• Profil actif 3 mois")
            if st.button("Tester le mode gratuit"): st.info("Accès découverte activé.")
        with col2:
            st.markdown("#### 💎 Mode Premium")
            st.write("• 3 CVs optimisés / semaine\n• 20 mails par jour\n• Priorité totale")
            if st.button("🚀 Booster ma carrière"): st.info("Redirection vers le paiement...")

    with dossiers[1]: # 📅 Entretiens
        st.subheader("📅 Mes Entretiens")
        st.write("### ⏳ À confirmer")
        try:
            a_confirmer = supabase.table("entretiens").select("*").eq("statut", "A_CONFIRMER").execute().data
            if a_confirmer:
                for e in a_confirmer:
                    with st.expander(f"Proposition : {e['poste']} - {e['date_heure'][:16]}"):
                        if st.button("✅ Confirmer ce rendez-vous", key=e['id']):
                            supabase.table("entretiens").update({"statut": "CONFIRME"}).eq("id", e['id']).execute()
                            st.rerun()
            else: st.info("Aucune proposition en attente.")
        except: st.warning("Connexion aux entretiens en cours...")

    with dossiers[2]: # 📄 CVs
        st.subheader("📄 Mes CVs enregistrés")
        try:
            response = supabase.table("cvs").select("id, poste_vise, created_at, contenu").order("created_at", desc=True).execute()
            for item in response.data:
                with st.expander(f"CV pour {item['poste_vise']} - {item.get('created_at', 'N/A')[:10]}"):
                    st.write(item.get('contenu', ''))
        except: st.write("Aucun CV enregistré.")

    with dossiers[3]: # ✨ Relooking
        st.subheader("✨ Relooking & Analyse")
        up = st.file_uploader("Upload CV", type=["pdf"])
        if up and st.button("🚀 Lancer l'analyse"):
            reader = PdfReader(up)
            texte = "".join([p.extract_text() for p in reader.pages])
            res = client.chat.completions.create(messages=[{"role": "user", "content": f"Analyse ce CV : {texte}"}], model="llama-3.3-70b-versatile")
            st.info(res.choices[0].message.content)
            
        poste = st.text_input("Poste visé")
        if st.button("Valider et Produire"):
            if up and poste:
                res = client.chat.completions.create(messages=[{"role": "user", "content": f"Réécris pour {poste} : {texte}"}], model="llama-3.3-70b-versatile")
                contenu = res.choices[0].message.content
                supabase.table("cvs").insert({"user_email": "test@test.com", "nom_fichier": f"CV_{poste}.pdf", "contenu": contenu, "poste_vise": poste}).execute()
                st.session_state.cv_final = contenu
                st.success("CV produit et sauvegardé !")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Structure de gestion employeur en cours de déploiement.")
