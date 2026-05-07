import streamlit as st
import pandas as pd
import streamlit_webrtc as webrtc
from PIL import Image

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="OmniPost.app", 
    page_icon="🚀",
    layout="wide"
)

# --- 2. STYLE PERSONNALISÉ (COULEURS DU LOGO) ---
st.markdown("""
    <style>
    :root {
        --primary-blue: #00467F;
        --secondary-cyan: #4FA9D1;
        --validation-green: #22c55e;
        --bg-light: #f8fafc;
    }
    
    /* Style général et titres */
    h1, h2, h3 { color: var(--primary-blue) !important; }
    
    /* Personnalisation des boutons */
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: var(--secondary-cyan);
        color: white;
    }

    /* Style des cartes de candidats */
    .candidat-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-left: 6px solid var(--secondary-cyan);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* FOOTER FIXE */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: var(--primary-blue);
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #e2e8f0;
        z-index: 100;
    }
    .footer a {
        color: var(--secondary-cyan);
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE DE DONNÉES (SESSION) ---
if 'cv_list' not in st.session_state:
    st.session_state.cv_list = [
        {"Nom": "Marc Riva", "Score": 96, "Statut": "En attente", "Handicap": True, "Valide": True},
        {"Nom": "Alice Vion", "Score": 84, "Statut": "En attente", "Handicap": False, "Valide": True},
        {"Nom": "Jean Test", "Score": 0, "Statut": "Écarté (Critères manquants)", "Handicap": False, "Valide": False}
    ]

# --- 4. BARRE LATÉRALE (LOGO) ---
with st.sidebar:
    try:
        # Assurez-vous que l'image est enregistrée sous ce nom
        logo = Image.open('logo_final.png')
        st.image(logo, use_container_width=True)
    except:
        st.title("🚀 OMNIPOST")
    
    st.divider()
    st.subheader("📩 Flux de Réception")
    email_target = st.text_input("Boîte de réception", "recrutement@entreprise.com")
    st.caption("L'IA scanne les CV arrivant sur cette adresse.")

# --- 5. CORPS DU DASHBOARD ---
st.title("Dashboard de Recrutement Intelligent")

tabs = st.tabs(["📢 Annonce & Critères", "📂 Tiroir à CV (Tri IA)", "📹 Salon Vidéo"])

# ONGLET 1 : DIFFUSION
with tabs[0]:
    st.subheader("Configuration de l'offre")
    c1, c2 = st.columns(2)
    with c1:
        job = st.text_input("Poste à pourvoir", placeholder="ex: Comptable")
        inclusion = st.toggle("♿ Ouvert aux personnes en situation de handicap", value=True)
    with c2:
        st.write("**🛡️ Filtres de tri automatiques**")
        p_req = st.checkbox("Permis B Obligatoire")
        d_req = st.text_input("Diplôme minimum", placeholder="ex: BTS")

    if st.button("🚀 Lancer la diffusion"):
        st.success(f"Annonce diffusée. Mention handicap intégrée.")

# ONGLET 2 : TIROIR À CV
with tabs[1]:
    st.subheader(f"Candidatures pour : {job if job else 'Poste non défini'}")
    
    if st.button("🔄 Synchroniser les nouveaux emails"):
        with st.spinner("Analyse sémantique et tri des CV..."):
            # Simulation d'ajout
            st.session_state.cv_list.append({"Nom": "Sophie L.", "Score": 91, "Statut": "En attente", "Handicap": False, "Valide": True})
            st.rerun()

    # Séparation Qualifiés / Écartés
    df = pd.DataFrame(st.session_state.cv_list)
    qualifies = df[df['Valide'] == True].sort_values(by="Score", ascending=False)
    ecartes = df[df['Valide'] == False]

    st.markdown("### 🏆 Profils Qualifiés (Classés par pertinence)")
    for i, row in qualifies.iterrows():
        st.markdown(f'<div class="candidat-card">', unsafe_allow_html=True)
        col_rank, col_info, col_btn, col_sim = st.columns([1, 4, 2, 2])
        
        with col_rank:
            st.markdown(f"<h2 style='color: var(--secondary-cyan); margin:0;'>#{list(qualifies.index).index(i) + 1}</h2>", unsafe_allow_html=True)
        
        with col_info:
            h_icon = " ♿" if row['Handicap'] else ""
            st.write(f"**{row['Nom']}**{h_icon}")
            st.write(f"Matching : {row['Score']}%")
            st.progress(row['Score'] / 100)
        
        with col_btn:
            st.write(f"Statut : **{row['Statut']}**")
            if st.button("📩 Envoyer Offre", key=f"mail_{i}"):
                st.toast(f"Proposition envoyée à {row['Nom']}")
        
        with col_sim:
            if st.button("👍 Simulation : Accord", key=f"ok_{i}"):
                st.session_state.cv_list[i]['Statut'] = "🤝 Validé"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📂 Voir les profils écartés (Critères non remplis)"):
        st.table(ecartes[['Nom', 'Statut']])

# ONGLET 3 : SALON VIDÉO
with tabs[2]:
    st.subheader("Entretien Vidéo Direct")
    # Liste des candidats ayant validé
    confirmes = [c['Nom'] for c in st.session_state.cv_list if c['Statut'] == "🤝 Validé"]
    
    if confirmes:
        c_choice = st.selectbox("Candidat prêt pour l'appel :", confirmes)
        st.info(f"Connexion WebRTC sécurisée avec {c_choice}")
        webrtc.webrtc_streamer(key="video_call", rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    else:
        st.warning("Aucun candidat n'a encore validé la proposition via le bouton 'Accord'.")

# --- 6. FOOTER FINAL ---
st.markdown(f"""
    <div class="footer">
        Créée par <b>RAKOTOBE Liliane</b> | 
        <a href="mailto:creationsites06@gmail.com">
            📩 Me contacter : creationsites06@gmail.com
        </a>
    </div>
    """, unsafe_allow_html=True)
