import streamlit as st
from datetime import date

# Configuration de la page
st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀", layout="wide")

# --- DATA DES DIFFUSEURS (GRATUIT VS PAYANT) ---
DIFFUSEURS_INFO = {
    "LinkedIn": {"Gratuit": "1 annonce/mois (limitée)", "Payant": "Sponsorisation (Prix variable)", "Tag": "Premium"},
    "Indeed": {"Gratuit": "Standard (Visibilité basse)", "Payant": "Annonces Sponsorisées (Par clic)", "Tag": "Budget"},
    "France Travail": {"Gratuit": "Illimité (Public)", "Payant": "Aucun", "Tag": "Gratuit"},
    "Hellowork": {"Gratuit": "Aucun", "Payant": "Abonnement ou Unité", "Tag": "Pro"},
    "Monster": {"Gratuit": "Essai 7 jours", "Payant": "Pack Annonces", "Tag": "Pro"}
}

st.title("🚀 OmniPost : Gestionnaire de Diffusion")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 Créer une Offre", "🔑 Comptes & Tarifs", "📁 Candidatures Triées"])

# --- ONGLET 1 : ÉDITION & DIFFUSION ---
with tab1:
    st.header("Nouvelle Annonce")
    c1, c2, c3 = st.columns(3)
    with c1:
        metier = st.selectbox("Métier", ["Conducteur de Travaux", "Chef de Projet IT", "Commercial", "Assistant Logistique"])
        lieu = st.text_input("Localisation", placeholder="ex: Bordeaux")
    with c2:
        type_contrat = st.selectbox("Contrat", ["CDI", "CDD", "Alternance"])
        salaire = st.number_input("Salaire (K€)", 20, 150, 35)
    with c3:
        demande_lm = st.toggle("Lettre de Motivation obligatoire", value=True)
        urgent = st.toggle("🚨 Option Urgent (Payant sur certains sites)")

    st.divider()
    st.subheader("Sélection des canaux de diffusion")
    
    # Affichage des plateformes avec rappel des prix
    choix_plateformes = st.multiselect(
        "Choisissez où diffuser :",
        list(DIFFUSEURS_INFO.keys()),
        help="Certains canaux appliquent des frais de sponsorisation."
    )
    
    # Rappel dynamique des coûts selon la sélection
    if choix_plateformes:
        cols = st.columns(len(choix_plateformes))
        for i, p in enumerate(choix_plateformes):
            with cols[i]:
                st.caption(f"**{p}**")
                if "Payant" in DIFFUSEURS_INFO[p] and DIFFUSEURS_INFO[p]["Payant"] != "Aucun":
                    st.warning(f"💰 {DIFFUSEURS_INFO[p]['Payant']}")
                else:
                    st.success("✅ 100% Gratuit")

    if st.button("🚀 LANCER LA DIFFUSION"):
        if metier and lieu and choix_plateformes:
            st.balloons()
            st.success("Diffusion en cours sur les réseaux sélectionnés !")
        else:
            st.error("Veuillez remplir les informations et choisir au moins un diffuseur.")

# --- ONGLET 2 : COMPTES & TABLEAU DES TARIFS ---
with tab2:
    st.header("Récapitulatif des Partenariats")
    
    # Création du tableau comparatif
    data_table = []
    for k, v in DIFFUSEURS_INFO.items():
        data_table.append({"Diffuseur": k, "Option Gratuite": v["Gratuit"], "Option Payante": v["Payant"]})
    
    st.table(data_table)
    
    st.divider()
    st.subheader("🔑 Vos Identifiants")
    col_a, col_b = st.columns(2)
    with col_a:
        st.text_input("Identifiant LinkedIn")
        st.text_input("Clé API Indeed", type="password")
    with col_b:
        st.text_input("Identifiant France Travail")
        st.text_input("Identifiant Monster")

# --- ONGLET 3 : TRI DES CV ---
with tab3:
    st.header("Dossiers Candidats")
    st.info("Les CV arrivant sur rakotobelili63@gmail.com sont triés ici.")
    # (Le code de tri reste le même que précédemment)
    st.write("Aucune nouvelle candidature aujourd'hui.")

# --- FOOTER ---
st.markdown("---")
footer = """
    <div style="text-align: center; color: #888; font-size: 12px;">
        Créé par <a href="mailto:rakotobelili63@gmail.com" style="color: #3b82f6;">RAKOTOBE Liliane</a>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
