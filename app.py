import streamlit as st, datetime, pandas as pd, io, json, re, urllib.parse
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTIONS ---
def envoyer_lien_magique(email):
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.success(f"Lien magique envoyé à {email}. Vérifiez vos emails.")
    except Exception as e: st.error(f"Erreur : {e}")

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"""Analyse ce CV pour le poste '{metier}'. 
    Retourne UNIQUEMENT un objet JSON. Structure: 
    {{"header": {{"nom": "...", "titre_poste": "...", "contact": "..."}}, 
      "sidebar": {{"contenu": "..."}}, 
      "main": {{"titre": "...", "corps": "..."}}, 
      "mots_cles_ajoutes": "..."}}
    CV: {txt_cv}"""
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    content = res.choices[0].message.content.strip()
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    return json.loads(json_match.group()) if json_match else json.loads(content)

def appliquer_design_geometrique(pdf, data):
    h, s, m = data.get('header', {}), data.get('sidebar', {}), data.get('main', {})
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, h.get('nom', 'N/A'), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, h.get('contact', ''))
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, s.get('contenu', ''))
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, h.get('titre_poste', ''), ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, m.get('titre', ''), ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, m.get('corps', ''))

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar:
    if "access_token" in st.query_params: st.rerun()
    session = supabase.auth.get_session()
    if session: st.success(f"Connecté : {session.user.email}")
    else:
        email_in = st.text_input("Votre email")
        if st.button("Envoyer mon lien"): envoyer_lien_magique(email_in)
    st.markdown("---")
    st.link_button("Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    st.link_button("Premium Recruteur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

tabs = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "🔄 Matching"])

with tabs[0]: st.write("Optimisez votre carrière avec zipngo.")

with tabs[1]:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[0]:
        st.subheader("📋 Historique des candidatures")
        user = supabase.auth.get_user()
        if user and user.user:
            try:
                res = supabase.table("candidatures").select("*").eq("user_id", user.user.id).execute()
                if res.data: st.table(pd.DataFrame(res.data))
                else: st.info("Aucune candidature.")
            except: st.warning("Vérifiez la table 'candidatures' dans Supabase.")
    with dossiers[1]:
        nom = st.text_input("Nom du doc")
        up = st.file_uploader("Upload", type=["pdf", "txt"])
        if st.button("💾 Enregistrer"):
            user = supabase.auth.get_user()
            if user and user.user:
                supabase.table("cvs").insert({"user_id": user.user.id, "nom_fichier": nom, "contenu": str(up.getvalue())}).execute()
                st.success("Enregistré !")
    with dossiers[2]:
        metier = st.text_area("Intitulé du poste...")
        up_cv = st.file_uploader("Upload CV", type=["pdf"])
        if up_cv and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.download_button("⬇️ Télécharger CV", data=pdf.output(dest='S').encode('latin-1'), file_name="CV_Optimise.pdf")
    with dossiers[3]:
        st.subheader("🌐 Sourcing Assisté")
        domaine = st.text_input("Métier ciblé", placeholder="Infirmière, ASH...")
        ville = st.text_input("Ville")
        modele = f"Madame, Monsieur,\n\nActuellement à la recherche d'une opportunité en tant que {domaine} dans la région de {ville}, je me permets de vous adresser ma candidature.\n\nTrès intéressé(e) par vos activités, je souhaiterais vivement mettre mes compétences au service de vos équipes.\n\nVous trouverez mon CV ci-joint. Je reste à votre entière disposition pour un entretien.\n\nCordialement,\n\n[Votre Nom]\n[Votre Téléphone]"
        emails_input = st.text_area("Collez ici les 20 emails (séparés par une virgule ou ligne)")
        if st.button("✅ Préparer l'envoi"):
            emails = [e.strip() for e in re.split(r'[,\n]+', emails_input) if '@' in e][:20]
            if emails:
                dest, cc_cache = emails[0], ",".join(emails[1:])
                full_link = f"mailto:{dest}?bcc={cc_cache}&subject=Candidature-{domaine}&body=" + urllib.parse.quote(modele)
                st.markdown(f'<a href="{full_link}" target="_blank" style="padding: 10px; background: #4169E1; color: white; text-decoration: none; border-radius: 5px;">📤 Ouvrir ma messagerie</a>', unsafe_allow_html=True)
                user = supabase.auth.get_user()
                if user and user.user:
                    supabase.table("candidatures").insert({"user_id": user.user.id, "intitule_poste": domaine, "statut": "Email préparé"}).execute()
            else: st.error("Veuillez coller au moins un email.")
    with dossiers[4]:
        if st.button("👍 Débloquer l'agenda"): st.session_state.agenda = True

with tabs[2]:
    metier = st.text_input("Métier")
    if st.button("✅ Diffuser"):
        user = supabase.auth.get_user()
        if user and user.user:
            supabase.table("mes_offres").insert({"user_id": user.user.id, "intitule": metier}).execute()

with tabs[3]:
    if st.button("👍 Valider fin entretien"): st.success("Anonymat levé.")

st.markdown("---")
st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b> <a href='mailto:creationsites06@gmail.com'>📧</a></div>", unsafe_allow_html=True)
