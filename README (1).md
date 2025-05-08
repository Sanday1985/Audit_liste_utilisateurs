
# 🩺 Détection des doublons et suivi d'activité des utilisateurs dans DHIS2

Application **Streamlit** pour :
- détecter les utilisateurs **dupliqués** (doublons sur le champ `name`)
- afficher la **date de création** de chaque compte utilisateur
- extraire la **date de la dernière commande** (ex. dernier envoi de données)
- calculer le **nombre de jours depuis la dernière activité**
- permettre le **téléchargement du rapport en CSV**

---

## 📁 Fichiers inclus

- `app.py` : le script principal de l'application Streamlit
- `requirements.txt` : dépendances nécessaires
- `README.md` : ce fichier

---

## ⚙️ Installation

Clonez le dépôt GitHub :

```bash
git clone https://github.com/<ton-utilisateur>/detection-doubles-rma.git
cd detection-doubles-rma
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

---

## 🚀 Lancer l'application

Dans le terminal :

```bash
streamlit run app.py
```

---

## 🛠️ Fonctionnalités

- Connexion sécurisée à l’API DHIS2 via **nom d’utilisateur + mot de passe**
- Analyse des utilisateurs liés à une **unité d’organisation spécifique**
- Identification des **doublons** selon le champ `name`
- Affichage de la **date de création** de chaque utilisateur
- Extraction de la **date de dernière activité (commande)**
- Calcul du **nombre de jours d'inactivité**
- **Export CSV** des résultats analysés

---

## 🔐 Sécurité

Les identifiants ne sont pas enregistrés. L'authentification se fait via HTTPS avec la méthode de base de l’API DHIS2.

---

## 📦 Exemple de dépendances (`requirements.txt`)

```txt
streamlit
pandas
requests
openpyxl
```

---

## 🙌 Contribuer

Les contributions sont bienvenues pour :
- ajouter la connexion par **token personnel (PAT)**
- améliorer les filtres de sélection
- intégrer plus d’indicateurs d’activité utilisateur

---

## 📄 Licence

Ce projet est open-source sous licence MIT.
