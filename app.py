import streamlit as st, pandas as pd, io, json, re
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

LANGUES = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais", "Chinois", "Japonais", "Russe", "Arabe", "Néerlandais", "Suédois", "Polonais", "Turc", "Coréen", "Hindi", "Vietnamien", "Thaï", "Indonésien", "Grec"]

# --- FONCTIONS ---
def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse ce CV pour {metier}. Retourne JSON: {{header, sidebar, main, mots_cles_ajoutes}}. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())

def appliquer_design_geometrique(pdf, data):
    h, s, m = data.get('header', {}), data.get('sidebar', {}), data.get('main', {})
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F'); pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, h.get('nom', 'N/A'), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, h.get('contact', ''))
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, s.get('contenu', ''))
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, h.get('titre_poste', ''), ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, m.get('titre', ''), ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, m.get('corps', ''))

# --- UI PRINCIPALE ---
st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

# Gestion du Magic Link
params = st.query_params
if "access_token" in params:
    try:
        supabase.auth.set_session(access_token=params["access_token"], refresh_token=None)
        st.query_params.clear(); st.rerun()
    except: st.error("Lien invalide.")

session = supabase.auth.get_session()

if not session:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email")
        role = st.radio("Espace souhaité :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("Envoyer le lien de connexion"):
            supabase.auth.sign_in_with_otp({
                "email": email, 
                "options": {"data": {"role": role}, "email_redirect_to": "https://zipngo.streamlit.app/"}
            })
            st.info("Lien envoyé ! Vérifiez votre boîte mail.")
else:
    role = session.user.user_metadata.get("role", "Candidat")
    st.write(f"Connecté en tant que : **{role}**")
    if st.button("Déconnexion"): supabase.auth.sign_out(); st.rerun()

    is_admin = session.user.email == "creationsites06@gmail.com"

    if role == "Candidat":
        tabs = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
        with tabs[0]:
            st.subheader("📋 Historique des candidatures")
            query = supabase.table("candidatures").select("*")
            if not is_admin: query = query.eq("user_id", session.user.id)
            st.table(pd.DataFrame(query.execute().data))
        with tabs[1]:
            nom = st.text_input("Nom du fichier"); up = st.file_uploader("Upload", type=["pdf"])
            if up and st.button("💾 Enregistrer"): supabase.table("cvs").insert({"user_id": session.user.id, "nom_fichier": nom, "contenu": up.getvalue().hex()}).execute()
        with tabs[2]:
            metier = st.text_area("Intitulé du poste..."); up_cv = st.file_uploader("Upload CV", type=["pdf"])
            if up_cv and metier and st.button("🚀 Optimiser & Designer"):
                txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
                pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, obtenir_contenu_structure(txt, metier))
                pdf_bytes = pdf.output(dest='S')
                st.download_button("⬇️ Télécharger", pdf_bytes.encode('latin-1'), "CV_Optimise.pdf")
        with tabs[3]:
            domaine = st.text_input("Métier"); ville = st.text_input("Ville"); emails_input = st.text_area("Emails")
            if st.button("✅ Préparer l'envoi"):
                link = f"mailto:?bcc={emails_input.replace(chr(10),',')}&subject=Candidature&body=Poste {domaine} à {ville}"
                st.markdown(f'<a href="{link}">📤 Ouvrir messagerie</a>', unsafe_allow_html=True)
        with tabs[4]:
            st.subheader("📅 Réservation Planning")
            for slot in supabase.table("agenda").select("*").execute().data:
                if st.button(f"Réserver {slot['creneau']}", key=slot['id']): st.success("RDV pris !")

    elif role == "Employeur":
        st.subheader("💼 Espace Employeur")
        with st.expander("📝 Rédiger offre"):
            metier = st.text_input("Poste"); langue = st.selectbox("Langue", LANGUES)
            if st.button("✨ Générer IA"):
                st.write(client.chat.completions.create(messages=[{"role":"user", "content":f"Annonce pour {metier} en {langue}"}], model="llama-3.3-70b-versatile").choices[0].message.content)

st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
