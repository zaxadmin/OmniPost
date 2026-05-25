import streamlit as st
import imaplib
import email
import io
import requests
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
SALON_FIXE = "https://meet.jit.si/zipngo-entretien-privé"

# --- FONCTIONS ---
def envoyer_email(dest, bcc, sujet, contenu):
    return requests.post("https://api.resend.com/emails", 
        headers={"Authorization": f"Bearer {st.secrets['RESEND_API_KEY']}"},
        json={"from": "contact@zipngo.zaxx.app", "to": dest, "bcc": bcc, "subject": sujet, "html": contenu}).status_code == 200

# --- UI PRINCIPALE ---
st.markdown("<div><span style='color:#000080; font-size:3rem; font-weight:bold;'>zip</span><span style='color:#4169E1; font-size:3rem; font-weight:bold;'>ngo</span>.zaxx.app</div>", unsafe_allow_html=True)
tab_home, tab_candidat, tab_employeur, tab_cgv = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "📜 CGV"])

# --- TAB CANDIDAT ---
with tab_candidat:
    st.header("Interface Candidat")
    with st.expander("📖 Mode d'emploi"):
        st.write("1. Inscrivez-vous. 2. Sourcez vos entreprises. 3. Relookez votre CV. 4. Candidature")
    
    sub_tabs = st.tabs(["📋 Inscription", "🌐 Sourcing", "🚀 Campagne"])
    with sub_tabs[0]:
        with st.form("candidat_form"):
            nom = st.text_input("Nom")
            email_c = st.text_input("Email")
            accept = st.checkbox("J'accepte les CGV")
            if st.form_submit_button("S'inscrire"):
                if accept:
                    supabase.table("candidats").insert({"nom": nom, "email": email_c}).execute()
                    st.success("Profil créé !")
                else: st.warning("Acceptez les CGV.")

    with sub_tabs[1]:
        secteur = st.text_input("Secteur")
        if st.button("Chercher"):
            res = client.chat.completions.create(messages=[{"role": "user", "content": f"Liste 5 entreprises en {secteur} avec emails RH."}], model="llama-3.3-70b-versatile")
            st.markdown(res.choices[0].message.content)

    with sub_tabs[2]:
        dest = st.text_input("Destinataire principal")
        bcc_list = st.text_area("19 emails en BCC (séparés par virgules)").split(",")
        if st.button("Candidater"):
            envoyer_email(dest, bcc_list, "Candidature", "Voici ma candidature.")
            st.success("Campagne lancée !")

# --- TAB EMPLOYEUR ---
with tab_employeur:
    st.header("Interface Employeur")
    with st.expander("⚙️ Configurer Tri"):
        email_in = st.text_input("Email de réception")
        pwd_in = st.text_input("Mot de passe app", type="password")
        if st.button("Sauvegarder config"):
            supabase.table("recruteurs").upsert({"email_recruteur": email_in, "email_tri": email_in, "password_tri": pwd_in}).execute()

    if st.button("🚀 Lancer le Tri IA"):
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_in, pwd_in)
        mail.select("inbox")
        _, messages = mail.search(None, 'UNSEEN')
        for num in messages[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            st.write(f"Candidature de : {msg.get('From')}")
        
        if st.button("👍 Proposer Entretien"):
            envoyer_email(email_in, [], "Invitation Entretien", f"Rejoignez-moi ici : {SALON_FIXE}")
            st.success("Invitation envoyée !")

# --- TAB CGV ---
with tab_cgv:
    st.markdown("### Conditions Générales de Vente")
    st.write("Offres Premium : 6€ (Candidat/3 mois) | 39€ (Recruteur/mois).")
