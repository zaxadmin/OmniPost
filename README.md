# 🚀 OmniPost : Recrutement Intelligent & Multidiffusion 1-Clic

**OmniPost** est une solution logicielle innovante conçue pour simplifier radicalement le processus de recrutement des TPE, PME et entreprises en forte croissance. L'objectif est de permettre une diffusion universelle des offres et un tri automatisé des candidatures en un temps record.

---

## 👩‍💻 Créatrice du Projet
Ce projet a été conçu et initialisé par **RAKOTOBE Liliane**.

---

## ✨ La Vision "1-Clic"
OmniPost répond à la problématique du temps perdu dans le sourcing et le tri manuel :
1. **Saisie Simplifiée :** L'intelligence du système génère la fiche de poste à partir d'un intitulé.
2. **Cochage de Critères :** Sélection rapide des impératifs (Permis, Expérience, Langues).
3. **Diffusion Omnicanale :** Publication simultanée sur LinkedIn, Indeed, France Travail et via mailing-list d'agences d'intérim.
4. **Matching Intelligent :** L'algorithme trie les CV reçus et classe les candidats par pertinence (Vert/Orange/Rouge).

---

## 🛠️ Fonctionnalités Validées (MVP)

### 📡 Module de Multidiffusion
- Automatisation de l'envoi vers les APIs des plateformes d'emploi majeures.
- Envoi de templates d'emails structurés aux partenaires de recrutement.

### 🛡️ Protection de la Vie Privée (Mode Discrétion)
- Masquage automatique des coordonnées directes (téléphone, adresse exacte) sur les annonces publiques pour éviter les sollicitations directes non filtrées.

### 🧠 Analyse IA & Parsing de CV
- **Extraction de texte :** Lecture automatisée des formats PDF et Word.
- **Scoring Engine :** Système de notation basé sur les compétences réelles extraites du CV par rapport aux besoins cochés par l'employeur.

### 🔄 Gestion Dynamique des Flux
- Capacité de changer l'adresse email de réception et de diffusion à la volée pour une gestion multi-sites ou multi-services.

---

## 🏗️ Architecture du Code

| Fichier | Description |
| :--- | :--- |
| `account_manager.py` | Contrôle et basculement des comptes emails. |
| `multiposter.py` | Automatisation de la diffusion sur les canaux externes. |
| `cv_parser.py` | Moteur de lecture et d'analyse des fichiers CV. |
| `matcher.py` | Logique de calcul des scores (Matching). |
| `candidate_manager.py` | Gestion des réponses automatiques aux candidats. |
| `data_structure.json` | Définition des règles métier et du formulaire. |

---

## 📋 État d'avancement du Projet

- [x] **Étape 1 :** Conception, Architecture et Design.
- [x] **Étape 2 :** Moteur de Connexion et Sécurité.
- [x] **Étape 3 :** Module de Multidiffusion (APIs & Emails).
- [x] **Étape 4 :** Analyse IA et Scoring de CV.
- [x] **Étape 5 :** Gestion des Candidats (Relances et Refus 1-clic).

---

## 🚀 Installation

```bash
# Cloner le projet
git clone [https://github.com/votre-utilisateur/OmniPost.git](https://github.com/votre-utilisateur/OmniPost.git)

# Installer les outils nécessaires
pip install -r requirements.txt

# Configurer vos accès
cp .env.example .env
