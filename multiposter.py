import requests

class OmniPostDistributor:
    """Gère l'envoi de l'offre vers les différents canaux."""

    def __init__(self, job_data, channels):
        self.job_data = job_data
        self.channels = channels

    def broadcast(self):
        """Lance la diffusion sur tous les canaux sélectionnés."""
        results = {}
        for channel in self.channels:
            if channel == "LinkedIn":
                results["LinkedIn"] = self._post_to_linkedin()
            elif channel == "Indeed":
                results["Indeed"] = self._post_to_indeed()
            elif channel == "Interim_Agencies":
                results["Agencies"] = self._send_to_agencies()
        return results

    def _post_to_linkedin(self):
        print("📤 Envoi vers LinkedIn API...")
        return "Success"

    def _post_to_indeed(self):
        print("📤 Envoi vers Indeed API...")
        return "Success"

    def _send_to_agencies(self):
        print("📧 Envoi de l'offre à la liste d'agences d'intérim...")
        return "Emails Sent"
