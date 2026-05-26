Voici la version inversée de l'onglet tab_home, avec le descriptif positionné au-dessus des formulaires de connexion comme demandé :
```python
with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Texte descriptif en premier
    col_text1, col_text2 = st.columns(2)
    with col_text1:
        st.subheader("🚀 Espace Candidat")
        st.write("Optimisez votre CV, ciblez les entreprises et gérez vos candidatures avec simplicité.")
    with col_text2:
        st.subheader("💼 Espace Recruteur")
        st.write("Centralisez vos candidatures, triez les profils pertinents et gagnez un temps précieux.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Connexion en dessous
    col_conn1, col_conn2 = st.columns(2)
    with col_conn1:
        email_cand = st.text_input("Email Candidat", key="cand_email")
        if st.button("Connexion Candidat"):
            supabase.auth.sign_in_with_otp({"email": email_cand})
            st.success("Lien envoyé par email.")
            
    with col_conn2:
        email_rec = st.text_input("Email Recruteur", key="rec_email")
        if st.button("Connexion Recruteur"):
            supabase.auth.sign_in_with_otp({"email": email_rec})
            st.success("Lien envoyé par email.")
    
    st.markdown("---")
    st.markdown("""
    ### Bienvenue sur **zipngo**
    Nous transformons la complexité du marché de l'emploi en opportunités concrètes.
    * **Pour les Talents :** Valorisation sur-mesure et ciblage direct.
    * **Pour les Recruteurs :** Clarté décisionnelle et automatisation des tâches.
    """)

```
Tu peux remplacer le bloc with tab_home: actuel par celui-ci. L'organisation est maintenant plus naturelle pour l'utilisateur : il lit d'abord ce que la plateforme lui apporte avant de passer à l'action de connexion.
