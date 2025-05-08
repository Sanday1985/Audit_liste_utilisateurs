import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

st.set_page_config(page_title="Analyse des Utilisateurs DHIS2", layout="wide")

st.sidebar.header("🔧 Paramètres de Connexion")
url = st.sidebar.text_input("🌐 URL DHIS2", value="https://togo.dhis2.org/dhis")
username = st.sidebar.text_input("👤 Nom d'utilisateur")
password = st.sidebar.text_input("🔑 Mot de passe", type="password")

if st.sidebar.button("📥 Charger les données"):
    with st.spinner("Chargement des utilisateurs..."):
        api_url = f"{url}/api/users.json?fields=id,displayName,userCredentials[username,lastLogin],organisationUnits[id,name]&paging=false"
        response = requests.get(api_url, auth=HTTPBasicAuth(username, password))

        if response.status_code != 200:
            st.error(f"Erreur lors de l'accès à l'API : {response.status_code}")
        else:
            data = response.json()
            users = []

            for user in data.get("users", []):
                display_name = user.get("displayName", "")
                username = user.get("userCredentials", {}).get("username", "")
                last_login_raw = user.get("userCredentials", {}).get("lastLogin")
                last_login = (
                    datetime.strptime(last_login_raw, "%Y-%m-%dT%H:%M:%S.%f")
                    if last_login_raw else None
                )
                org_units = [ou["name"] for ou in user.get("organisationUnits", [])]
                users.append({
                    "Nom complet": display_name,
                    "Nom d'utilisateur": username,
                    "Dernière connexion": last_login,
                    "Unités d'organisation": ", ".join(org_units),
                })

            df = pd.DataFrame(users)
            df["Jours depuis dernière connexion"] = df["Dernière connexion"].apply(
                lambda x: (datetime.now() - x).days if pd.notnull(x) else "Inconnu"
            )
            df["Doublon (Nom complet)"] = df.duplicated(subset=["Nom complet"], keep=False).map({True: "Oui", False: "Non"})

            # Interface de sélection d’unité d’organisation
            all_org_units = sorted(set(sum((row.split(", ") for row in df["Unités d'organisation"]), [])))
            selected_unit = st.selectbox("🏥 Sélectionnez une unité d'organisation", ["Toutes"] + all_org_units)

            if selected_unit != "Toutes":
                df = df[df["Unités d'organisation"].str.contains(selected_unit)]

            st.success(f"{len(df)} utilisateurs affichés.")
            st.dataframe(df, use_container_width=True)
