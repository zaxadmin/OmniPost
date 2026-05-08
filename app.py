import streamlit as st
import pandas as pd
import streamlit_webrtc as webrtc
from PIL import Image

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(
    page_title="OmniPost.app", 
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
    <style>
    :root {
        --primary-blue: #00467F;
        --secondary-cyan: #4FA9D1;
        --validation-green: #22c55e;
    }
    
    h1, h2, h3 { color: var(--primary-blue) !important; }
    
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: var(--secondary-cyan);
        color: white;
    }

    /* FOOTER DISCRET */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #64748b;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #e2e8f0;
        z-index: 100;
    }
    .footer a {
        color: var(--primary-blue);
        text-decoration: none;
        font-size: 20px;
        vertical-align: middle;
        margin-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DONNÉES DE SESSION ---
if 'cv_list' not in st.session_state:
    st.session_state.cv_list = [
        {"Nom": "Marc Riva", "Score": 96, "Statut": "En attente", "Handicap": True, "Valide": True},
        {"Nom": "Alice Vion", "Score": 84, "Statut": "En attente", "Handicap": False, "Valide": True},
        {"Nom": "Jean Test", "Score": 0, "Statut": "Écarté (Critères manquants)", "Handicap": False, "Valide": False}
    ]

# --- 3. SIDEBAR (LOGO) ---
with st.sidebar:
    try:
        # Utilisation du nom exact : logo_omnipost.jpg
        logo = Image.open('logo_omnipost.jpg')
        st.image(logo, use_container_width=True)
    except:
        st.title("🚀 OMNIPOST")
    
    st.divider()
    st.subheader("📩 Flux de Réception")
    email_target = st.text_input("Boîte de réception", "recrutement@entreprise.com")

# --- 4. DASHBOARD ---
st.title("Dashboard de Recrutement Intelligent")

tabs = st.tabs(["📢 Diffusion", "📂 Tiroir à CV", "📹 Salon Vidéo"])

with tabs[0]:
    st.subheader("Configuration de l'offre")
    c1, c2 = st.columns(2)
    with c1:
        job = st.text_input("Poste", placeholder="ex: Comptable")
        st.toggle("♿ Ouvert aux personnes en situation de handicap", value=True)
    with c2:
        st.checkbox("Permis B Obligatoire")
        st.text_input("Diplôme minimum")
    if st.button("🚀 Lancer la diffusion"):
        st.success("Offre diffusée.")

with tabs[1]:
    st.subheader("Analyse et Classement IA")
    if st.button("🔄 Synchroniser les emails"):
        st.session_state.cv_list.append({"Nom": "Sophie L.", "Score": 91, "Statut": "En attente", "Handicap": False, "Valide": True})
        st.rerun()

    df = pd.DataFrame(st.session_state.cv_list)
    qualifies = df[df['Valide'] == True].sort_values(by="Score", ascending=False)
    
    for i, row in qualifies.iterrows():
        with st.expander(f"#{list(qualifies.index).index(i) + 1} - {row['Nom']} ({row['Score']}%)", expanded=True):
            col_info, col_btn, col_sim = st.columns([4, 2, 2])
            with col_info:
                st.progress(row['Score'] / 100)
            with col_btn:
                st.write(f"Statut : {row['Statut']}")
                if st.button("📩 Envoyer Offre", key=f"m_{i}"):
                    st.toast("Envoyé !")
            with col_sim:
                if st.button("👍 Simulation Accord", key=f"v_{i}"):
                    st.session_state.cv_list[i]['Statut'] = "🤝 Validé"
                    st.rerun()

with tabs[2]:
    st.subheader("Entretien Vidéo")
    confirmes = [c['Nom'] for c in st.session_state.cv_list if c['Statut'] == "🤝 Validé"]
    if confirmes:
        st.selectbox("Candidat prêt :", confirmes)
        webrtc.webrtc_streamer(key="call", rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    else:
        st.warning("Aucun candidat n'a encore validé la proposition.")

# --- 5. FOOTER (SIGNATURE & MAILTO DISCRET) ---
st.markdown(f"""
    <div class="footer">
        Créée par <b>RAKOTOBE Liliane</b> 
        <a href="mailto:creationsites06@gmail.com" title="Envoyer un email">📩</a>
    </div>
    """, unsafe_allow_html=True)
