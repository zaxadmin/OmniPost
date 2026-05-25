import streamlit as st
import imaplib
import email
import requests
from groq import Groq
from supabase import create_client

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
SALON_FIXE = "https://meet.jit.si/zipngo-entretien-privé"

# --- FONCTIONS ---
def envoyer_email(dest, bcc, sujet, contenu):
    return requests.post("https://api.resend.com/emails", 
        headers={"Authorization": f"Bearer {st.secrets['RESEND_API_KEY']}"},
        json={"from": "contact@zipngo.zaxx.app", "to": dest, "bcc": bcc, "subject": sujet, "html": contenu}).status_code == 200

# --- UI ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span></h1>", unsafe_allow_html=True)
tab_home, tab_candidat, tab_employeur, tab_cgv = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "📜 CGV"])

with tab_home:
    st.title("L'avenir du recrutement")
    st.write("Bienvenue sur la plateforme qui connecte les talents sans frontières.")

with tab_candidat:
    st.header("Interface Candidat")
    with st.expander("📖 Mode d'emploi"):
        st.write("1. Inscrivez-vous. 2. Sourcez vos entreprises. 3. Lancez votre campagne BCC.")
    
    sub_tabs = st.tabs(["📋 Inscription", "🌐 Sourcing", "🚀 Campagne"])
    with sub_tabs[0]:
        with st.form("candidat_form"):
            nom = st.text_input("Nom")
            email_c = st.text_input("Email")
            accept = st.checkbox("J'accepte les CGV")
            if st.form_submit_button("S'inscrire"):
                if accept:
                    try:
                        supabase.table("candidats").insert({"nom": nom, "email": email_c}).execute()
                        st.success("Profil créé !")
                    except Exception as e:
                        st.error(f"Erreur technique : {e}")
                else: st.warning("Acceptez les CGV.")

    with sub_tabs[1]:
        secteur = st.text_input("Secteur")
        if st.button("Chercher"):
            res = client.chat.completions.create(messages=[{"role": "user", "content": f"Liste 5 entreprises en {secteur} avec emails RH."}], model="llama-3.3-70b-versatile")
            st.markdown(res.choices[0].message.content)

    with sub_tabs[2]:
        dest = st.text_input("Destinataire principal")
        bcc_raw = st.text_area("19 emails en BCC (séparés par virgules)")
        if st.button("Envoyer campagne"):
            bcc_list = [e.strip() for e in bcc_raw.split(",")]
            envoyer_email(dest, bcc_list, "Candidature Spontanée", "Madame, Monsieur, voici ma candidature.")
            st.success("Campagne lancée !")

with tab_employeur:
    st.header("Interface Employeur")
    email_in = st.text_input("Email de réception")
    pwd_in = st.text_input("Mot de passe App (16 car.)", type="password")
    
    if st.button("🚀 Lancer le Tri IA"):
        try:
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
        except Exception as e:
            st.error(f"Erreur de connexion mail : {e}")

with tab_cgv:
    st.markdown("### Conditions Générales de Vente")
    st.write("Abonnements : Candidat 6€/3mois | Recruteur 39€/mois.")
