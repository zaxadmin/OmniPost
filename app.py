import streamlit as st
from datetime import date

# Configuration globale
st.set_page_config(page_title="zipngo", layout="wide")

# CSS pour le style et le design
st.markdown("""
    <style>
    .title-zip { color: #000080; font-weight: bold; font-size: 3rem; }
    .title-ngo { color: #1E90FF; font-weight: bold; font-size: 3rem; }
    .subtitle-zaxx { color: #808080; font-size: 0.9rem; font-family: monospace; margin-bottom: 20px; }
    .presentation-box { background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #1E90FF; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "user_type": None, "anonymat_leve": False})

# --- PAGE AUTHENTIFICATION ---
if not st.session_state.auth:
    with st.sidebar:
        st.selectbox("🌐 Langue", ["Français", "English", "Malgache", "Español", "Português", "Deutsch", "Italiano", "Mandarin", "日本語", "العربية", "हिन्दी", "Русский", "한국어", "Nederlands", "Polski", "Svenska", "Türkçe", "Ελληνικά", "Magyar", "Tiếng Việt"])

    st.markdown('<span class="title-zip">zip</span><span class="title-ngo">ngo</span> 👍', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-zaxx">.zaxx.app</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="presentation-box">
        <h4>Bienvenue sur zipngo</h4>
        <p>Le pont intelligent entre votre talent et votre futur. Notre IA simplifie votre recrutement en garantissant un anonymat total jusqu'à votre accord mutuel pour l'entretien.</p>
    </div>
    """, unsafe_allow_html=True)
    
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"): st.session_state.update({"auth": True, "user_type": role}); st.rerun()

# --- ESPACE CONNECTÉ ---
else:
    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user_type}**")
        menu = st.radio("Navigation", ["Recherche Talents", "Gestion Entretiens", "Mon Compte"])
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    if menu == "Recherche Talents" and st.session_state.user_type == "Employeur":
        st.header("Talents disponibles")
        if st.button("Sélectionner ce profil 👍"):
            st.success("Profil sélectionné.")

    elif menu == "Gestion Entretiens":
        st.header("🤝 Espace Entretiens")
        if not st.session_state.anonymat_leve:
            if st.button("🤝 Lever l'anonymat (Double accord requis) 👍"):
                st.session_state.anonymat_leve = True
                st.rerun()
        else:
            st.success("Anonymat levé.")
            st.link_button("🎥 Salle Visio", "https://meet.jit.si/zipngo-session")

    elif menu == "Mon Compte":
        st.header("Paramètres")
        st.write("Gestion de votre compte et préférences.")

# --- FOOTER GLOBAL (Accessible partout) ---
st.markdown("---")
col_a, col_b = st.columns([3, 1])
with col_a:
    st.markdown(f"© {date.today().year} **zipngo** | Créatrice : Liliane RAKOTOBE | .zaxx.app")
with col_b:
    st.markdown("Contact : [✉️](mailto:creationsites06@gmail.com)")
