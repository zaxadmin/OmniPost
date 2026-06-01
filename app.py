import streamlit as st, pandas as pd, io, json, re, urllib.parse
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
def envoyer_lien_magique(email):
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.success(f"Lien envoyé à {email}.")
    except Exception as e: st.error(f"Erreur : {e}")

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse ce CV pour {metier}. Retourne JSON: {{header, sidebar, main, mots_cles_ajoutes}}. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    content = res.choices[0].message.content.strip()
    return json.loads(re.search(r'\{.*\}', content, re.DOTALL).group())

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
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar:
    # --- GESTION DU TOKEN (CORRECTE) ---
    params = st.query_params
    if "access_token" in params:
        try:
            supabase.auth.set_session(access_token=params["access_token"], refresh_token=None)
            st.query_params.clear()
            st.rerun()
        except Exception as e: st.error(f"Erreur : {e}")
    
    session = supabase.auth.get_session()
    if session:
        st.success(f"Connecté : {session.user.email}")
        # Accès administrateur total
        profil = st.radio("Accéder en tant que :", ["Candidat", "Employeur"])
        if st.button("Déconnexion"): supabase.auth.sign_out(); st.rerun()
        st.markdown("---")
        st.link_button("Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
        st.link_button("Premium Recruteur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")
    else:
        email_in = st.text_input("Votre email")
        if st.button("Envoyer mon lien magique"): envoyer_lien_magique(email_in)
        profil = None

# --- LOGIQUE D'ACCÈS ILLIMITÉ (ADMIN) ---
is_admin = session and session.user.email == "creationsites06@gmail.com"

if profil == "Candidat":
    tabs = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with tabs[0]:
        st.subheader("📋 Historique des candidatures")
        if session:
            query = supabase.table("candidatures").select("*")
            if not is_admin: query = query.eq("user_id", session.user.id)
            st.table(pd.DataFrame(query.execute().data))
    with tabs[1]:
        nom = st.text_input("Nom du fichier"); up = st.file_uploader("Upload", type=["pdf"])
        if up and st.button("💾 Enregistrer"): supabase.table("cvs").insert({"user_id": session.user.id, "nom_fichier": nom, "contenu": up.getvalue().hex()}).execute()
    with tabs[2]:
        metier = st.text_area("Intitulé du poste...")
        up_cv = st.file_uploader("Upload CV", type=["pdf"])
        if up_cv and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            pdf_bytes = pdf.output(dest='S')
            supabase.table("cvs").insert({"user_id": session.user.id, "nom_fichier": f"Relooké_{metier}", "contenu": pdf_bytes.hex()}).execute()
            st.success("CV enregistré !"); st.download_button("⬇️ Télécharger", pdf_bytes.encode('latin-1'), "CV_Optimise.pdf")
    with tabs[3]:
        st.subheader("🌐 Sourcing")
        domaine = st.text_input("Métier"); ville = st.text_input("Ville")
        modele = f"Madame, Monsieur, je vous contacte pour le poste de {domaine} à {ville}."
        emails_input = st.text_area("Collez les 20 emails")
        if st.button("✅ Préparer l'envoi"):
            emails = [e.strip() for e in re.split(r'[,\n]+', emails_input) if '@' in e][:20]
            link = f"mailto:{emails[0]}?bcc={','.join(emails[1:])}&subject=Candidature&body={urllib.parse.quote(modele)}"
            st.markdown(f'<a href="{link}" target="_blank">📤 Ouvrir messagerie</a>', unsafe_allow_html=True)
    with tabs[4]:
        st.subheader("📅 Réservation Planning")
        agendas = supabase.table("agenda").select("*").execute()
        for slot in agendas.data:
            if st.button(f"Réserver {slot['creneau']}", key=f"s_{slot['id']}"):
                res = supabase.rpc("reserver_creneau", {"p_agenda_id": slot['id'], "p_candidat_id": session.user.id, "p_candidature_id": None}).execute()
                if res.data: st.success("RDV confirmé !"); st.rerun()
                else: st.error("Déjà pris.")

elif profil == "Employeur":
    st.subheader("💼 Espace Employeur")
    with st.expander("📝 Rédiger offre"):
        metier = st.text_input("Poste"); langue = st.selectbox("Langue", LANGUES)
        if st.button("✨ Générer IA"):
            st.session_state.annonce = client.chat.completions.create(messages=[{"role":"user", "content":f"Annonce pour {metier} en {langue}"}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.write(st.session_state.annonce)
    c1, c2 = st.columns(2)
    with c1: st.subheader("🎯 Matches"); st.write("Candidats matchés")
    with c2: st.subheader("📂 Vivier"); st.write("Base de données")

else:
    st.info("Veuillez vous connecter via le Magic Link.")

st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
