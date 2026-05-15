import streamlit as st
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="zipngo.zaxx | Recruitment & ATS", layout="wide")

# --- SYSTÈME DE TRADUCTION INTÉGRAL ---
T = {
    "Français": {
        "intro": "La plateforme de dispatch mondial d'offres d'emploi et de relooking CV optimisé ATS.",
        "desc": "zipngo.zaxx sécurise vos échanges : les identités, noms d'entreprises et coordonnées directes sont révélés uniquement après un accord mutuel post-entretien.",
        "user": "Identifiant Candidat", 
        "pw": "Mot de passe", 
        "login": "VALIDER L'ACCÈS",
        "create": "CRÉER MON COMPTE CANDIDAT", 
        "forgot": "Mot de passe oublié ?", 
        "signup_t": "Rejoindre l'aventure zipngo",
        "name": "Prénom & Nom", 
        "email": "Email de contact", 
        "submit": "VALIDER MON INSCRIPTION", 
        "back": "Retour à la connexion",
        "menu_1": "🌍 Dispatch Offres",
        "menu_2": "📄 Relooking & ATS",
        "menu_3": "🤝 Entretien Sécurisé",
        "menu_4": "⚙️ Mon Profil"
    },
    "English (US)": {
        "intro": "The global job dispatch platform and ATS-optimized CV makeover service.",
        "desc": "zipngo.zaxx secures your exchanges: identities, company names, and direct contacts are only revealed after mutual post-interview agreement.",
        "user": "Candidate ID", 
        "pw": "Password", 
        "login": "VALIDATE ACCESS",
        "create": "CREATE CANDIDATE ACCOUNT", 
        "forgot": "Forgot password?", 
        "signup_t": "Join the zipngo adventure",
        "name": "Full Name", 
        "email": "Contact Email", 
        "submit": "VALIDATE REGISTRATION", 
        "back": "Back to login",
        "menu_1": "🌍 Job Dispatch",
        "menu_2": "📄 CV Makeover & ATS",
        "menu_3": "🤝 Secure Interview",
        "menu_4": "⚙️ My Profile"
    },
    "Malagasy": {
        "intro": "Fandefasana tolotra asa manerantany sy fanamboarana CV ho matihanina.",
        "desc": "zipngo.zaxx dia miaro ny mombamomba anao : ny anarana sy ny fifandraisana dia miafina mandra-pifanaraka aorian'ny dinidinika.",
        "user": "Anarana", 
        "pw": "Teny miafina", 
        "login": "HIDITRA",
        "create": "HANOKATRA KAONTY", 
        "forgot": "Adino ny teny miafina?", 
        "signup_t": "Fidirana ato amin'ny zipngo",
        "name": "Anarana feno", 
        "email": "Email", 
        "submit": "ALFAY NY FISORATANA", 
        "back": "Hiverina",
        "menu_1": "🌍 Tolotra Asa",
        "menu_2": "📄 Fanamboarana CV",
        "menu_3": "🤝 Dinidinika Voaaro",
        "menu_4": "⚙️ Momba ahy"
    }
}

# --- THÈME ET CSS PERSONNALISÉ ---
def apply_zip_theme():
    st.markdown("""
    <style>
        /* Couleurs principales et fond */
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        
        /* Barre latérale */
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        
        /* Boutons */
        .stButton>button { 
            background: #1A237E !important; color: #00E5FF !important; 
            border-radius: 25px; border: 2px solid #00E5FF; 
            font-weight: bold; width: 100%; transition: 0.3s;
        }
        .stButton>button:hover { border: 2px solid #FFFFFF; color: #FFFFFF !important; }
        
        /* Cartes d'entretien */
        .secure-card { 
            padding: 20px; border: 2px dashed #1A237E; border-radius: 15px; 
            background: #f9f9f9; text-align: center; margin-bottom: 10px;
        }
        
        /* Panel ATS */
        .ats-panel { 
            padding: 15px; border-radius: 10px; background: #E3F2FD; 
            border-left: 5px solid #00E5FF; margin: 10px 0; 
        }
        
        /* Footer */
        .footer-zip { text-align: center; padding: 20px; margin-top: 50px; border-top: 1px solid #eee; }
        .legal-link-zip { color: #94a3b8; text-decoration: none; font-size: 11px; margin: 0 10px; }
        .legal-content { font-size: 10px; line-height: 1.4; text-align: justify; display: none; margin-top: 10px; }
        #mentions_z:target, #cgv_z:target { display: block; padding: 10px; background: #fcfcfc; }
        
        .orange-thumb { color: #FF9800; font-size: 60px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE L'ÉTAT (SESSION) ---
if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "interview_step" not in st.session_state: st.session_state.interview_step = "offer"

apply_zip_theme()

# --- ESPACE NON AUTHENTIFIÉ ---
if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        # Choix de la langue en haut
        lang_choice = st.selectbox("🌐 Language", list(T.keys()), key="lang_selector")
        text = T[lang_choice]
        
        st.markdown('<div class="orange-thumb">👍</div>', unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center; color:#1A237E; font-size: 52px; margin-top:-20px;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        # Présentation complète
        st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:18px; color:#1A237E;'>{text['intro']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#64748b; font-size:14px; font-style:italic;'>{text['desc']}</p>", unsafe_allow_html=True)
        
        st.divider()

        if st.session_state.z_view == "login":
            st.text_input(text["user"])
            st.text_input(text["pw"], type="password")
            if st.button(text["login"]): 
                st.session_state.z_auth = True
                st.rerun()
            
            st.markdown("---")
            if st.button(text["create"]): 
                st.session_state.z_view = "signup"
                st.rerun()
            st.button(text["forgot"], on_click=lambda: st.session_state.update({"z_view": "forgot"}))

        elif st.session_state.z_view == "signup":
            st.subheader(text["signup_t"])
            st.text_input(text["name"])
            st.text_input(text["email"])
            st.text_input(text["pw"], type="password", key="signup_pw")
            if st.button(text["submit"]): 
                st.success("Compte créé avec succès ! Connectez-vous.")
                st.session_state.z_view = "login"
                st.rerun()
            st.button(text["back"], on_click=lambda: st.session_state.update({"z_view": "login"}))

# --- ESPACE MEMBRE CONNECTÉ ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='color:#1A237E;'>zip<span style='color:#00E5FF;'>ngo</span></h2>", unsafe_allow_html=True)
        menu = st.radio("Navigation", [T[st.session_state.lang_selector]["menu_1"], 
                                      T[st.session_state.lang_selector]["menu_2"], 
                                      T[st.session_state.lang_selector]["menu_3"],
                                      T[st.session_state.lang_selector]["menu_4"]])
        
        st.divider()
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.z_auth = False
            st.rerun()

    # --- MODULE : ENTRETIEN SÉCURISÉ ---
    if "Entretien" in menu or "Interview" in menu or "Dinidinika" in menu:
        st.header("🤝 Protocole d'Entretien Sécurisé")
        
        if st.session_state.interview_step == "offer":
            st.info("💡 Un recruteur est intéressé par votre profil ! Il propose 2 créneaux de rencontre anonyme.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="secure-card"><b>CRÉNEAU 1</b><br>Lundi 18 Mai<br>09:30 (Heure Locale)</div>', unsafe_allow_html=True)
                if st.button("CHOISIR LE CRÉNEAU 1"):
                    st.session_state.interview_step = "confirmed"
                    st.rerun()
            
            with col_b:
                st.markdown('<div class="secure-card"><b>CRÉNEAU 2</b><br>Mardi 19 Mai<br>14:00 (Heure Locale)</div>', unsafe_allow_html=True)
                if st.button("CHOISIR LE CRÉNEAU 2"):
                    st.session_state.interview_step = "confirmed"
                    st.rerun()
            
            st.divider()
            if st.button("❌ DÉCLINER L'ENTRETIEN / SUPPRIMER L'OFFRE"):
                st.warning("Offre déclinée.")

        elif st.session_state.interview_step == "confirmed":
            st.success("✅ Entretien planifié ! Le lien de visioconférence sécurisé sera généré ici à l'heure du RDV.")
            st.markdown("""
            ### 🔒 État de vos données (Mode Anonyme)
            Pour votre sécurité, les informations suivantes sont actuellement **masquées** :
            * **Votre Nom/Prénom :** Masqué
            * **Votre Email/Téléphone :** Masqué
            * **Identité du Recruteur :** Masqué (ID: REQ-992)
            * **Nom de l'Entreprise :** Masqué
            """)
            st.info("Après l'entretien, si vous et le recruteur confirmez vouloir rester en contact, vos coordonnées respectives seront révélées.")
            
            if st.button("L'ENTRETIEN EST TERMINÉ : REVELER LES INFOS ?"):
                st.session_state.interview_step = "revealed"
                st.rerun()

        elif st.session_state.interview_step == "revealed":
            st.balloons()
            st.subheader("🎉 Accord Mutuel Établi !")
            st.markdown('<div class="ats-panel">Voici les coordonnées complètes pour la suite de vos échanges :</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("**RECRUTEUR**")
                st.write("👤 Nom : Jean Dupont")
                st.write("🏢 Entreprise : Global Tech Solutions")
            with c2:
                st.write("**COORDONNÉES**")
                st.write("📧 Email : j.dupont@globaltech.com")
                st.write("📞 Tel : +33 6 12 34 56 78")

    # --- MODULE : RELOOKING ATS ---
    elif "Relooking" in menu or "Makeover" in menu or "Fanamboarana" in menu:
        st.header("📄 Optimisation ATS & Relooking CV")
        st.write("Uploadez votre CV pour vérifier sa compatibilité avec les algorithmes de recrutement mondiaux.")
        
        uploaded_file = st.file_uploader("Choisir un fichier (PDF uniquement)", type=["pdf"])
        if uploaded_file:
            st.markdown('<div class="ats-panel">🔍 **Analyse en cours...**</div>', unsafe_allow_html=True)
            st.markdown('<div class="ats-panel" style="background:#FFEBEE; border-left-color:#F44336;">⚠️ **Score ATS actuel : 42/100**<br>Points critiques : Mots-clés manquants, format de date non standard.</div>', unsafe_allow_html=True)
            
            if st.button("✨ LANCER LE RELOOKING AUTOMATIQUE"):
                st.success("Optimisation terminée !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9; border-left-color:#2E7D32;">✅ **Nouveau Score ATS : 98/100**<br>Votre CV est désormais optimisé pour les systèmes de dispatch mondial.</div>', unsafe_allow_html=True)

# --- PIED DE PAGE COMMUN (LÉGAL) ---
st.markdown(f"""
<div class="footer-zip">
    <a href="#mentions_z" class="legal-link-zip">Mentions Légales</a> | 
    <a href="#cgv_z" class="legal-link-zip">Conditions Générales (CGV)</a>
    <div id="mentions_z" class="legal-content">
        <b>Mentions Légales :</b> zipngo.zaxx est une solution éditée par <b>Liliane RAKOTOBE</b>.<br>
        Conformément au RGPD, vous disposez d'un droit de suppression totale de vos données sur simple demande par email.
    </div>
    <div id="cgv_z" class="legal-content">
        <b>CGV :</b> Les données sensibles (coordonnées) sont protégées par le protocole de sécurité zipngo jusqu'à validation post-entretien.<br>
        Tout compte inactif pendant plus de <b>90 jours</b> sera automatiquement mis en veille ou supprimé.
    </div>
    <p>© 2026 zipngo.zaxx | Créatrice : Liliane RAKOTOBE <a href="mailto:creationsites06@gmail.com" style="text-decoration:none;">✉️</a></p>
</div>
""", unsafe_allow_html=True)
