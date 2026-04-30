# 🚀 OmniPost : Recrutement Intelligent & Multidiffusion 1-Clic

**OmniPost** est une application SaaS conçue pour les patrons et recruteurs pressés. Elle permet de diffuser une offre d'emploi sur tous les canaux majeurs et de trier automatiquement les CV reçus, tout en protégeant la vie privée de l'employeur.

---

## ✨ La Promesse "1-Clic"
1. **Saisissez** le métier (l'IA génère la fiche de poste).
2. **Cochez** vos critères (Permis, Expérience, Langues).
3. **Diffusez** partout (LinkedIn, Indeed, France Travail, Agences d'intérim).
4. **Recrutez** (L'app trie les CV et vous donne les "Matchs Verts").

---

## 🛠️ Fonctionnalités Clés

### 📡 Multidiffusion Automatisée
- Publication instantanée via APIs (LinkedIn, Indeed, France Travail).
- Envoi automatique d'emails structurés à une liste personnalisée d'agences d'intérim.

### 🛡️ Mode Discrétion (Confidentialité)
- Masquage automatique du numéro de téléphone et de l'adresse exacte.
- Seul l'email de candidature est exposé pour filtrer les appels intempestifs.

### 🧠 Tri & Scoring IA (Vert/Orange/Rouge)
- **Parsing PDF/Word :** Extraction automatique du texte des CV reçus par email.
- **Matching Engine :** Comparaison des compétences du candidat avec les critères cochés par l'employeur.
- **Classification :** Les candidats sont classés par couleur pour une lecture instantanée.

### 🔄 Flexibilité des Flux
- Gestion multi-comptes : Changez l'adresse email de réception des candidatures à tout moment selon vos besoins.

---

## 🏗️ Architecture du Projet

Le projet est structuré de manière modulaire pour être robuste et évolutif :

| Fichier | Rôle |
| :--- | :--- |
| `account_manager.py` | Gestion des comptes emails et des accès diffuseurs. |
| `multiposter.py` | Moteur de diffusion vers les jobboards et agences. |
| `cv_parser.py` | Intelligence Artificielle pour la lecture des CV (PDF/Word). |
| `matcher.py` | Algorithme de scoring et de classification (Matching). |
| `data_structure.json` | Logique métier et modèles de formulaires. |

---

## 📋 État d'avancement (Checklist)

- [x] **Étape 1 :** Conception et Architecture (Workflow, JSON).
- [x] **Étape 2 :** Moteur de Connexion (Email, Sécurité).
- [x] **Étape 3 :** Multidiffusion (APIs, Templates Agences).
- [x] **Étape 4 :** Analyse IA (Parsing CV, Scoring).
- [ ] **Étape 5 :** Gestion des Candidats (Relances et Refus 1-clic) - *En cours*.

---

## 🚀 Installation & Lancement

1. Clonez le dépôt :
   ```bash
   git clone [https://github.com/votre-compte/OmniPost.git](https://github.com/votre-compte/OmniPost.git)
