import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime

st.set_page_config(page_title="Utilisateurs DHIS2 - Analyse", layout="wide")
st.title("🔐 Analyse des Utilisateurs DHIS2")

# Connexion DHIS2 avec en-tête encodé
def get_auth_header(username, password):
    token = f"{username}:{password}"
    encoded = base64.b64encode(token.encode()).decode("utf-8")
    return {"Authorization": f"Basic {encoded}"}

# Récupération des utilisateurs
def get_users(dhis2_url, headers):
    url = f"{dhis2_url}/api/users.json"
    params = {
        "fields": "id,name,created,userCredentials[username],organisationUnits[id,name]",
        "paging": "false"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("users", [])
    else:
        st.error("❌ Échec de récupération des utilisateurs.")
        return []

# Dernières connexions
def get_user_logins(dhis2_url, headers):
    url = f"{dhis2_url}/api/userCredentials?fields=username,lastLogin&paging=false"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("userCredentials", [])
    return []

# Interface
with st.sidebar:
    st.header("🔧 Paramètres de Connexion")
    dhis2_url = st.text_input("🌐 URL DHIS2", value="https://togo.dhis2.org/dhis")
    username = st.text_input("👤 Nom d'utilisateur")
    password = st.text_input("🔑 Mot de passe", type="password")

if dhis2_url and username and password:
    headers = get_auth_header(username, password)

    if st.sidebar.button("📥 Charger les données"):
        with st.spinner("Connexion à DHIS2 et chargement des données..."):
            users = get_users(dhis2_url, headers)
            logins = get_user_logins(dhis2_url, headers)
            login_map = {entry["username"]: entry.get("lastLogin") for entry in logins}

            data = []
            for user in users:
                uname = user.get("userCredentials", {}).get("username", "")
                org_units = ", ".join([ou["name"] for ou in user.get("organisationUnits", [])])
                last_login = login_map.get(uname)
                data.append({
                    "Nom complet": user.get("name", ""),
                    "Nom d'utilisateur": uname,
                    "Date de création": user.get("created", ""),
                    "Unités d'organisation": org_units,
                    "Dernière connexion": last_login
                })

            df = pd.DataFrame(data)
            df["Date de création"] = pd.to_datetime(df["Date de création"])
            df["Dernière connexion"] = pd.to_datetime(df["Dernière connexion"], errors="coerce")
            df["Jours depuis dernière connexion"] = (pd.Timestamp.now() - df["Dernière connexion"]).dt.days
            df["Doublon (Nom complet)"] = df.duplicated("Nom complet", keep=False).map({True: "Oui", False: "Non"})

            st.success(f"✅ {len(df)} utilisateurs chargés depuis DHIS2.")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Télécharger les données (CSV)",
                data=csv,
                file_name="utilisateurs_dhis2.csv",
                mime="text/csv"
            )
