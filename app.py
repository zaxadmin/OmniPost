import streamlit as st
import datetime
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
# Assure-toi que tes secrets sont bien configurés dans Streamlit Cloud ou .streamlit/secrets.toml
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
    with st.expander("📜 Lire les Conditions Générales de Vente"):
        afficher_cgv()
    st.checkbox("J'accepte les Conditions Générales de Vente", key="accept_cgv")
    st.markdown("<div style='text-align: center; margin-top: 50px;'>© 2026 zipngo.zaxx.app | <strong>Créatrice : Liliane RAKOTOBE</strong></div>", unsafe_allow_html=True)

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🚀 Campagne"])
    
    with dossiers[0]: # 📂 Candidatures
        st.subheader("📊 Mon Statut & Historique Sourcing")
        col1, col2 = st.columns(2)
        with col1: st.write("🟢 **Accès Gratuit :** 1 campagne/mois.")
        with col2: st.write("💎 **Mode Premium :** 20 mails/jour.")
        
        st.markdown("---")
        try:
            historique = supabase.table("sourcing").select("*").order("id", desc=True).execute().data
            for h in historique:
                with st.expander(f"📅 {h.get('date')} | Destinataire : {h.get('email_destinataire')}"):
                    st.write(f"**Objet :** {h.get('objet')}")
                    st.write(f"**Message :** {h.get('message')}")
        except: st.info("Aucun historique de sourcing trouvé.")

    with dossiers[4]: # 🌐 Sourcing
        st.subheader("🌐 Prospection Spontanée (Campagne 1+19)")
        destinataire = st.text_input("Destinataire principal")
        copie_cachee = st.text_area("19 autres emails en copie cachée (séparez par des virgules)")
        objet = st.text_input("Objet du mail")
        message = st.text_area("Message")
        
        if st.button("🚀 Envoyer à 20 contacts"):
            if destinataire and message:
                supabase.table("sourcing").insert({
                    "email_destinataire": destinataire,
                    "objet": objet,
                    "message": message,
                    "date": str(datetime.date.today())
                }).execute()
                st.success("Campagne lancée et enregistrée dans votre historique !")
            else: st.warning("Veuillez remplir les champs obligatoires.")

    with dossiers[3]: # ✨ Relooking
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            reader = PdfReader(up)
            texte_cv = "".join([p.extract_text() for p in reader.pages])
            if st.button("🔍 Lancer le Scan ATS"):
                res = client.chat.completions.create(messages=[{"role": "user", "content": f"Scan ATS critique : {texte_cv}"}], model="llama-3.3-70b-versatile")
                st.info(res.choices[0].message.content)
            
            poste_vise = st.text_input("Poste visé")
            template = st.selectbox("Style", ["Classique", "Moderne", "Professionnel"])
            
            if st.button("🚀 Produire et Enregistrer mon CV"):
                res = client.chat.completions.create(messages=[{"role": "user", "content": f"Optimise pour {poste_vise} : {texte_cv}"}], model="llama-3.3-70b-versatile")
                contenu_final = res.choices[0].message.content
                supabase.table("cvs").insert({"user_email": "test@test.com", "nom_fichier": f"CV_{poste_vise}.pdf", "contenu": contenu_final, "poste_vise": poste_vise}).execute()
                st.session_state.cv_final = contenu_final
                st.success("✅ CV produit et enregistré !")

        if 'cv_final' in st.session_state:
            nom_pdf = "mon_cv_relooker.pdf"
            creer_pdf_cv_pro(st.session_state.cv_final, nom_pdf, template)
            with open(nom_pdf, "rb") as f: st.download_button(f"📥 Télécharger le CV ({template})", f, nom_pdf)

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
