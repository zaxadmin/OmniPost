# 🔄 Workflow Logique d'OmniPost

Ce document détaille le parcours utilisateur et technique de l'application.

## 1. Configuration Initiale (Une seule fois)
- L'employeur connecte son compte email professionnel (OAuth2/IMAP).
- L'employeur enregistre ses accès aux diffuseurs (LinkedIn, Indeed, etc.).
- Création d'une liste de diffusion pour les agences d'intérim partenaires.

## 2. Création de l'Offre (Le 1-Clic)
- **Saisie :** L'employeur tape le métier, l'app suggère la fiche de poste.
- **Cochage :** Sélection des impératifs (Permis, Expérience, Langues).
- **Options :** Activation par défaut du "Mode Discrétion" (Masquage Tel/Adresse).
- **Validation :** Un seul bouton pour lancer la machine.

## 3. Diffusion et Sourcing
- **Multi-publication :** Envoi simultané aux API des sites d'emploi.
- **Alerte Agences :** Envoi d'un email structuré aux agences d'intérim.
- **Sourcing Inversé :** L'app scanne les bases de données publiques pour proposer des profils "Matchs" immédiatement.

## 4. Analyse et Tri (Le moteur de gain de temps)
- **Réception :** L'app intercepte les CV arrivant sur l'email.
- **Parsing :** Extraction du texte des PDF/Word.
- **Scoring :** Comparaison automatique avec les critères cochés à l'étape 2.
- **Classification :** - 🟢 **Vert :** Profil idéal (Toutes cases cochées).
    - 🟡 **Orange :** Profil intéressant (Manque 1 critère secondaire).
    - 🔴 **Rouge :** Ne correspond pas (Critère éliminatoire manquant).

## 5. Gestion des Candidats
- Bouton de relance rapide ou bouton de refus automatique en un clic.
