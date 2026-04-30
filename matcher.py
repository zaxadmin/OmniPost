class OmniPostMatcher:
    """Attribue un score de compatibilité aux candidats."""

    def calculate_score(self, required_skills, found_skills):
        """
        Calcule le score :
        - 🟢 Vert : 100% des critères trouvés
        - 🟡 Orange : > 50% des critères trouvés
        - 🔴 Rouge : < 50% ou critère éliminatoire manquant
        """
        if not required_skills:
            return "🟢 VERT"

        match_count = len(set(required_skills) & set(found_skills))
        percentage = (match_count / len(required_skills)) * 100

        if percentage == 100:
            return "🟢 VERT (Match Parfait)"
        elif percentage >= 50:
            return "🟡 ORANGE (À vérifier)"
        else:
            return "🔴 ROUGE (Écart trop important)"
