import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Suivi des utilisateurs DHIS2", layout="wide")
st.title("🔐 Connexion à DHIS2 et Analyse des Utilisateurs")

# --- Connexion à DHIS2
dhis2_url = "https://togo.dhis2.org/dhis"
username = st.text_input("👤 Nom d'utilisateur", type="default")
password = st.text_input("🔑 Mot de passe", type="password")

# Fonction pour récupérer la dernière activité par utilisateur depuis l'API audit
def get_last_activity_per_user(dhis2_url, username, password):
    st.info("⏳ Récupération des activités (audits)...")
    audit_url = f"{dhis2_url}/api/audits/dataValue?fields=user,created&paging=false"
    response = requests.get(audit_url, auth=HTTPBasicAuth(username, password))
    if response.status_code != 200:
        st.warning("⚠️ Impossible de récupérer les données d'audit.")
        return {}

    audits = response.json().get("audits", [])
    activity = {}
    for audit in audits:
        user = audit.get("user")
        created = audit.get("created")
        if user and created:
            created_dt = pd.to_datetime(created)
            if user not in activity or created_dt > activity[user]:
                activity[user] = created_dt
    return activity

if st.button("Se connecter"):
    with st.spinner("Connexion à DHIS2..."):
        response = requests.get(
            f"{dhis2_url}/api/me",
            auth=HTTPBasicAuth(username, password)
        )
        if response.status_code == 200:
            st.success("✅ Connexion réussie.")
            user_info = response.json()
            st.write("👤 Utilisateur :", user_info["displayName"])
        else:
            st.error("❌ Échec de la connexion. Vérifiez les identifiants.")
            st.stop()

    # --- Récupération des utilisateurs
    st.subheader("👥 Récupération des utilisateurs...")
    users_url = f"{dhis2_url}/api/users?fields=id,name,created,userCredentials[username],organisationUnits[id,name]&paging=false"
    res_users = requests.get(users_url, auth=HTTPBasicAuth(username, password))
    users = res_users.json()["users"]

    data = []
    for user in users:
        org_units = [ou["name"] for ou in user.get("organisationUnits", [])]
        data.append({
            "Nom complet": user.get("name", ""),
            "Nom d'utilisateur": user.get("userCredentials", {}).get("username", ""),
            "Date de création": user.get("created", ""),
            "Unités d'organisation": ", ".join(org_units)
        })

    df = pd.DataFrame(data)
    df["Date de création"] = pd.to_datetime(df["Date de création"])

    # --- Détection des doublons
    st.subheader("🔍 Doublons (par nom)")
    dupes = df[df.duplicated("Nom complet", keep=False)]
    st.dataframe(dupes)

    # --- Dernière activité réelle
    st.subheader("📦 Dernière activité enregistrée (via audit)")
    last_activity_dict = get_last_activity_per_user(dhis2_url, username, password)
    df["Dernière activité"] = df["Nom d'utilisateur"].map(last_activity_dict)
    df["Jours depuis dernière activité"] = (pd.Timestamp.now() - df["Dernière activité"]).dt.days

    st.dataframe(df)

    # --- Export CSV
    st.download_button(
        label="⬇️ Télécharger CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="utilisateurs_dhis2.csv",
        mime="text/csv"
    )
