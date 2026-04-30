import streamlit as st

# Cette ligne est pour tromper l'erreur Vercel
app = "handler" 

def main():
    st.set_page_config(page_title="OmniPost - Rakotobe Liliane")
    st.title("🚀 OmniPost")
    st.write("Créé par **RAKOTOBE Liliane**")

    lang = st.sidebar.radio("Langue / Language", ["Français", "English"])
    
    st.header("Configuration" if lang == "Français" else "Setup")
    email = st.text_input("Email", "contact@entreprise.com")
    
    if st.button("Diffuser" if lang == "Français" else "Broadcast"):
        st.balloons()
        st.success("Succès !" if lang == "Français" else "Success!")

if __name__ == "__main__":
    main()
