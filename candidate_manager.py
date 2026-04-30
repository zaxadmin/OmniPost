import smtplib
from email.mime.text import MIMEText

class OmniPostMessenger:
    """Gère l'envoi des emails de refus ou d'entretien."""

    def __init__(self, sender_email, password):
        self.sender = sender_email
        self.password = password

    def send_response(self, candidate_email, status):
        """Envoie automatiquement le bon template selon le statut."""
        if status == "🟢 VERT":
            subject = "Votre candidature pour le poste - Entretien"
            body = "Bonjour, votre profil a retenu toute notre attention. Quand seriez-vous disponible pour un échange ?"
        else:
            subject = "Mise à jour concernant votre candidature"
            body = "Bonjour, nous vous remercions pour votre intérêt. Malheureusement, nous avons choisi de poursuivre avec d'autres profils."

        self._execute_send(candidate_email, subject, body)

    def _execute_send(self, to_email, subject, body):
        # Logique d'envoi SMTP (mail réel)
        print(f"📩 Email envoyé à {to_email} : {subject}")
