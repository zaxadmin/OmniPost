import streamlit as st
from datetime import date

st.set_page_config(page_title="zipngo | .zaxx.app", layout="wide")

# --- FONCTIONS DE CONTENU ---
def afficher_presentation():
    st.markdown("""
    ### Bienvenue sur zipngo 👍
    *Votre talent, votre choix, votre succès.*
    
    La plateforme de télé-candidature intelligente qui remet l'humain au centre du recrutement.
    """)
    st.markdown("""
    * **Pour les Candidats :** Optimisez votre CV, ciblez les entreprises via notre moteur IA et gérez vos entretiens dans un espace 100% sécurisé.
    * **Pour les Employeurs :** Centralisez vos candidatures (interne Zipngo & sources externes), triez-les automatiquement par compatibilité et engagez les meilleurs talents.
    
    **La confiance avant tout :** Notre système d'anonymat protégé par le "double pouce" garantit une confidentialité totale jusqu'au moment de votre entretien vidéo.
    """)

def afficher_cgv():
    st.markdown("## 📜 Conditions Générales de Vente et d'Utilisation (CGVU)")
    st.markdown("""
    **Consigne :** L'employeur doit utiliser une adresse email dédiée au recrutement pour permettre l'analyse par IA.
    **Responsabilité :** RAKOTOBE Liliane décline toute responsabilité sur les contrats passés.
    **Premium :** Facturé via Stripe, non remboursable après activation.
    """)
    st.write("Éditeur : RAKOTOBE Liliane | Contact : creationsites06@gmail.com")

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "user_type": None, "entretiens": [], "is_premium": False})

# --- AUTHENTIFICATION ---
if not st.session_state.auth:
    st.markdown('<span style="color:#000080; font-weight:bold; font-size:3rem;">zip</span><span style="color:#1E90FF; font-weight:bold; font-size:3rem;">ngo</span> 👍', unsafe_allow_html=True)
    
    afficher_presentation()
    
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if role == "Employeur":
        st.info("💡 **Conseil :** Utilisez une adresse email dédiée (ex: recrutement@entreprise.com).")
    
    accept = st.checkbox("J'accepte les CGVU (incluant la recommandation d'email dédié).")
    if st.button("✨ Entrer", disabled=not accept): 
        st.session_state.update({"auth": True, "user_type": role}); st.rerun()
else:
    # --- NAVIGATION ---
    with st.sidebar:
        menu = st.radio("Navigation", ["Dashboard", "Tiroir Entretien", "Mon Compte", "CGV & Mentions"])
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    # --- ESPACE CANDIDAT ---
    if st.session_state.user_type == "Candidat":
        st.header("🚀 Télé-Candidature IA")
        st.write("Bienvenue dans votre espace sécurisé.")

    # --- ESPACE EMPLOYEUR (Tri IA + Engagement) ---
    else:
        st.header("📊 Candidatures (Triées par IA)")
        candidats = [{"nom": "Jean", "source": "zipngo"}, {"nom": "Marie", "source": "France Travail"}]
        for c in candidats:
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{c['nom']}** (Source: {c['source']})")
            if c['source'] == 'zipngo':
                col2.button("👍", key=c['nom'])
            else:
                if col2.button("🟡", key=c['nom']):
                    st.link_button("📩 Répondre", "mailto:candidat@email.com")

    # --- MON COMPTE ---
    if menu == "Mon Compte":
        if not st.session_state.is_premium:
            st.link_button("💎 ACTIVER PREMIUM (Stripe)", "https://buy.stripe.com/votre_lien")
        else:
            st.success("💎 Premium Actif")
    
    if menu == "CGV & Mentions":
        afficher_cgv()

st.markdown("---")
st.markdown(f"© {date.today().year} **zipngo** | Créatrice : RAKOTOBE Liliane")
