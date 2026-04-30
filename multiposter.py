import requests

class OmniPostDistributor:
    """Gère la multidiffusion des offres sur les canaux FR et Internationaux."""

    def __init__(self, job_data, selected_channels, language="fr"):
        self.job_data = job_data
        self.channels = selected_channels
        self.language = language

    def broadcast_all(self):
        """Lance la diffusion sur tous les canaux sélectionnés."""
        report = {}
        print(f"🌍 Starting broadcast in {self.language.upper()}...")

        for channel in self.channels:
            if channel in ["LinkedIn", "Glassdoor", "Monster"]:
                report[channel] = self._post_to_global_api(channel)
            elif channel == "France Travail":
                report[channel] = self._post_to_local_api("France Travail")
            elif channel == "Agencies":
                report[channel] = self._email_partners()
        
        return report

    def _post_to_global_api(self, platform_name):
        """Simule l'envoi vers une API internationale (Monster, Glassdoor, etc.)."""
        print(f"📤 [GLOBAL] Posting job to {platform_name}...")
        return "SUCCESS"

    def _post_to_local_api(self, platform_name):
        """Simule l'envoi vers une plateforme spécifique (ex: France Travail)."""
        print(f"📤 [LOCAL] Publication sur {platform_name}...")
        return "SUCCESS"

    def _email_partners(self):
        """Envoie l'offre aux agences d'intérim."""
        lang_header = "Nouvelle offre" if self.language == "fr" else "New Job Opening"
        print(f"📧 Sending automated emails to agencies with header: {lang_header}")
        return "SENT"

# Exemple : 
# poster = OmniPostDistributor(data, ["LinkedIn", "Monster"], language="en")
