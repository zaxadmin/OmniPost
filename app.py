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
    prompt = f"""Analyse ce CV pour le poste '{metier}'. Retourne UNIQUEMENT un objet JSON. Structure: 
    {{"header": {{"nom": "...", "titre_poste": "...", "contact": "..."}}, "sidebar": {{"contenu": "..."}}, 
      "main": {{"titre": "...", "corps": "..."}}, "mots_cles_ajoutes": "..."}}
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

tabs = st.tabs(["🏠 Accueil", "📖 Mode d'emploi", "🚀 Candidat", "💼 Employeur", "🔄 Matching"])

with tabs[0]:
    st.title("zipngo | Gestion Professionnelle")
    st.write("Bienvenue sur zipngo, votre espace dédié à l'organisation de vos candidatures.")

with tabs[1]:
    st.subheader("📖 Mode d'emploi")
    st.markdown("1. **Gestion des CVs** : Enregistrez vos documents. 2. **Sourcing** : Préparez vos envois. 3. **Suivi** : Historique complet.")

with tabs[2]:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[0]:
        st.subheader("📋 Historique des candidatures")
        user = supabase.auth.get_user()
        if user and user.user:
            res = supabase.table("candidatures").select("*").eq("user_id", user.user.id).execute()
            if res.data: st.table(pd.DataFrame(res.data))
    
    with dossiers[1]:
        st.subheader("📄 Mes documents")
        nom = st.text_input("Nom du fichier")
        up = st.file_uploader("Upload", type=["pdf"])
        cgv_cv = st.checkbox("J'accepte les CGV pour enregistrer")
        if st.button("💾 Enregistrer"):
            if cgv_cv and up and nom:
                user = supabase.auth.get_user()
                supabase.table("cvs").insert({"user_id": user.user.id, "nom_fichier": nom, "contenu": up.getvalue().hex()}).execute()
            elif not cgv_cv: st.error("Vérifiez accepter les CGV.")
        
        user = supabase.auth.get_user()
        if user and user.user:
            res = supabase.table("cvs").select("id, nom_fichier, contenu").eq("user_id", user.user.id).execute()
            for cv in res.data:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📄 {cv['nom_fichier']}")
                c2.download_button("⬇️", bytes.fromhex(cv['contenu']), f"{cv['nom_fichier']}.pdf", key=f"dl_{cv['id']}")
    
    with dossiers[2]:
        metier = st.text_area("Intitulé du poste...")
        up_cv = st.file_uploader("Upload CV", type=["pdf"])
        if up_cv and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            pdf_bytes = pdf.output(dest='S')
            user = supabase.auth.get_user()
            supabase.table("cvs").insert({"user_id": user.user.id, "nom_fichier": f"Relooké_{metier}", "contenu": pdf_bytes.hex()}).execute()
            st.success("CV enregistré !")
            st.download_button("⬇️ Télécharger", pdf_bytes.encode('latin-1'), "CV_Optimise.pdf")

    with dossiers[3]:
        st.subheader("🌐 Sourcing")
        domaine = st.text_input("Métier", "Infirmière")
        ville = st.text_input("Ville")
        modele = f"Madame, Monsieur,\n\nCandidature pour {domaine} à {ville}.\n\nVous trouverez mon CV ci-joint.\n\nCordialement."
        emails_input = st.text_area("Collez les 20 emails")
        if st.button("✅ Préparer l'envoi"):
            emails = [e.strip() for e in re.split(r'[,\n]+', emails_input) if '@' in e][:20]
            if emails:
                link = f"mailto:{emails[0]}?bcc={','.join(emails[1:])}&subject=Candidature&body=" + urllib.parse.quote(modele)
                st.markdown(f'<a href="{link}" target="_blank">📤 Ouvrir messagerie</a>', unsafe_allow_html=True)

    with dossiers[4]:
        st.subheader("🎤 Entraînement & Planning")
        reponse = st.text_area("Répondez à cette question : 'Quels sont vos points forts ?'")
        if st.button("Analyser ma réponse"):
            fb = client.chat.completions.create(messages=[{"role": "user", "content": f"Feedback entretien : {reponse}"}], model="llama-3.3-70b-versatile")
            st.write(fb.choices[0].message.content)
        
        st.markdown("---")
        st.subheader("📅 Mes propositions")
        user = supabase.auth.get_user()
        if user and user.user:
            res_match = supabase.table("candidatures").select("*").eq("user_id", user.user.id).eq("statut", "match").execute()
            for match in res_match.data:
                st.success(f"Recruteur intéressé ! 👍")
                heure = st.selectbox(f"Choisir créneau", ["09:00", "14:00"], key=match['id'])
                if st.button("Confirmer", key=f"btn_{match['id']}"):
                    supabase.table("candidatures").update({"statut": f"RDV {heure}"}).eq("id", match['id']).execute()
        else:
            st.info("Veuillez vous connecter pour voir vos propositions de rendez-vous.")

with tabs[3]:
    metier = st.text_input("Métier")
    cgv_offres = st.checkbox("J'accepte les CGV pour diffuser")
    if st.button("✅ Diffuser"):
        if cgv_offres:
            user = supabase.auth.get_user()
            if user and user.user:
                supabase.table("mes_offres").insert({"user_id": user.user.id, "intitule": metier}).execute()
        else: st.error("Veuillez accepter les CGV.")

with tabs[4]:
    if st.button("👍 Valider fin entretien"): st.success("Anonymat levé.")

st.markdown("---")
with st.expander("📜 Conditions Générales de Vente (CGV)"):
    st.markdown("Nos services sont fournis 'en l'état'. L'utilisation de zipngo implique l'acceptation de ces conditions.")

st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b> <a href='mailto:creationsites06@gmail.com'>📧</a></div>", unsafe_allow_html=True)
