# 🚀 OmniPost

**OmniPost** est une application SaaS de recrutement "Low Cost" conçue pour les entreprises de toutes tailles. Son objectif est de simplifier le processus de recrutement en permettant de diffuser une offre partout en un clic et de trier automatiquement les candidats.

## ✨ Fonctionnalités (Étape 1)
- **Formulaire Express :** Création d'offre par simple cochage (Intitulé, Salaire, Lieu, Permis, Langues).
- **Mode Discrétion :** Publication d'annonces sans téléphone ni adresse exacte (uniquement ville).
- **Centralisation :** Un seul point d'entrée pour toutes les plateformes (LinkedIn, Indeed, France Travail).
- **Tri Intelligent :** Analyse automatique des CV reçus sur la boîte mail connectée.

## 📋 Spécifications du Formulaire
Le formulaire de création d'offre est structuré pour minimiser la saisie :
- **Variables obligatoires :** Salaire, Lieu, Type de contrat.
- **Variables de tri :** Années d'expérience, Diplômes, Permis/CACES, Langues.
- **Badge Inclusivité :** Option "Handi-friendly".

## 🏗️ Architecture du Projet
- **Frontend :** Interface utilisateur simplifiée pour le "1-clic".
- **Backend :** Moteur de connexion email (IMAP) et multidiffusion.
- **Database :** PostgreSQL pour stocker les modèles d'annonces et les scores des candidats.
