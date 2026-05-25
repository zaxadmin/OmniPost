import streamlit as st
from groq import Groq
from supabase import create_client
import streamlit.components.v1 as components
import json
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | .zaxx.app", layout="wide")

client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- ÉTAT SESSION ---
if "auth" not in st.session_state:
    st.session_state.update({
        "auth": False, "cgv_validee": False, "bienvenue_vue": False, 
        "user_type": None, "user_email": None, "entretiens": [], "is_premium": False
    })

# --- EN-TÊTE GLOBAL (Langue & Remote) ---
col1, col2 = st.columns([1, 6])
with col1:
    liste_langues = ["Français", "English", "Malagasy", "Español", "Deutsch", "Português", "Italiano", "Русский", "中文", "日本語", "العربية", "हिन्दी", "한국어", "Nederlands", "Türkçe", "Polski", "Svenska", "Tiếng Việt", "Bahasa Indonesia", "ไทย"]
    st.session_state["langue"] = st.selectbox("🌐", liste_langues, label_visibility="collapsed")
    st.session_state["remote"] = st.checkbox("💻 Remote")

# --- FONCTIONS ---
def generer_ia(prompt):
    consigne = f"Réponds en {st.session_state['langue']}."
    if st.session_state["remote"]: consigne += " Priorise les opportunités Remote."
    res = client_groq.chat.completions.create(messages=[{"role": "system", "content": consigne}, {"role": "user", "content": prompt}], model="llama3-8b-8192")
    return res.choices[0].message.content

# --- AUTHENTIFICATION & CGV ---
if not st.session_state.auth:
    st.markdown('# zip<span style="color:#1E90FF;">ngo</span> 👍', unsafe_allow_html=True)
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"):
        st.session_state.update({"auth": True, "user_type": role})
        st.rerun()
elif not st.session_state.cgv_validee:
    st.write("## 📜 CGVU & Mode d'emploi\nUtilisez le mode Remote pour cibler l'international. Les emails seront en FR ou EN uniquement si le mode Remote est actif.")
    if st.checkbox("J'accepte"):
        if st.button("Continuer"): st.session_state.cgv_validee = True; st.rerun()
else:
    # --- NAVIGATION ---
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Tiroir Entretien", "Prospection B2B", "Info & Premium"])
    
    if menu == "Dashboard":
        if st.session_state.user_type == "Employeur":
            st.header("📊 Candidatures")
            for c in [{"nom": "Jean"}, {"nom": "Marie"}]:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"Candidat : {c['nom']}")
                if c2.button("👍", key=f"up_{c['nom']}"): st.session_state.entretiens.append(c); st.rerun()
                c3.button("👎", key=f"down_{c['nom']}")
        else:
            st.header("🚀 Optimisation CV")
            cv = st.text_area("CV :")
            if st.button("Analyser"): st.write(generer_ia(f"Optimise ce CV : {cv}"))

    elif menu == "Tiroir Entretien":
        st.header("📹 Entretien Vidéo")
        for ent in st.session_state.entretiens:
            if st.button(f"Lancer visio avec {ent['nom']}"):
                components.iframe(f"https://meet.jit.si/zipngo-{ent['nom']}", height=600)

    elif menu == "Prospection B2B":
        st.header("🔍 Prospection IA")
        brut = st.text_area("Données annuaire :")
        if st.button("Traiter"):
            res = generer_ia(f"Extrais (nom, email, tel) en JSON : {brut}")
            supabase.table("prospection").insert(json.loads(res)).execute()
            st.success("Enregistré !")
        # Envoi Mailto intelligent
        emails = [e['email'] for e in supabase.table("prospection").select("email").execute().data]
        if emails:
            lang_mail = "Français" if st.session_state["langue"] == "Français" and not st.session_state["remote"] else "English"
            sujet = "Candidature" if lang_mail == "Français" else "Job Application"
            st.markdown(f'[📩 Envoyer mail groupé ({lang_mail})]({"mailto:?bcc=" + ",".join(emails) + "&subject=" + sujet})')

    elif menu == "Info & Premium":
        st.write("💎 Premium : Contactez creationsites06@gmail.com")
        
    if st.sidebar.button("Déconnexion"): st.session_state.clear(); st.rerun()

st.markdown("---")
st.write(f"© {date.today().year} zipngo | RAKOTOBE Liliane")
