class OmniPostI18n:
    """Gère le support multilingue de l'application."""
    
    TRANSLATIONS = {
        "fr": {
            "welcome": "Bienvenue sur OmniPost",
            "btn_post": "Diffuser l'offre",
            "status_green": "🟢 VERT (Match Parfait)",
            "refusal_mail": "Bonjour, nous ne donnons pas suite..."
        },
        "en": {
            "welcome": "Welcome to OmniPost",
            "btn_post": "Post Job",
            "status_green": "🟢 GREEN (Perfect Match)",
            "refusal_mail": "Hello, we have decided to move forward with other candidates..."
        }
    }

    def __init__(self, lang="fr"):
        self.lang = lang

    def get_text(self, key):
        return self.TRANSLATIONS[self.lang].get(key, key)
