import streamlit as st
import pandas as pd
import datetime

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="FleetHub", layout="wide")

# ======================
# MENU PRINCIPAL
# ======================
def main_menu():
    st.title("🚗 FleetHub")
    st.subheader("Centre d’outils pour les gestionnaires de flottes")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Simulateur de TCO"):
            st.session_state.page = "tco"
    with col2:
        if st.button("🌱 Calculateur de carbone"):
            st.session_state.page = "carbone"
    with col3:
        if st.button("🏙️ Vérificateur ZFE"):
            st.session_state.page = "zfe"

# ======================
# MODULE 1 : TCO
# ======================
def simulateur_tco():
    st.markdown("### 📊 Simulateur de TCO")
    col1, col2 = st.columns(2)
    veh_data = []

    for i, col in enumerate([col1, col2], 1):
        col.subheader(f"Véhicule {i}")
        veh = {}
        veh["type"] = col.selectbox("Type de véhicule", ["Véhicule utilitaire", "Véhicule particulier"], key=f"type{i}")
        veh["energie"] = col.selectbox("Énergie", ["Essence", "Diesel", "Hybride", "Électrique"], key=f"energie{i}")
        leasing = col.checkbox("Leasing ?", key=f"leasing{i}")
        if leasing:
            veh["prix"] = col.number_input("Mensualité (€)", key=f"mensualite{i}")
        else:
            veh["prix"] = col.number_input("Prix d’achat HT (€)", key=f"prix{i}")

        veh["km"] = col.number_input("Kilométrage annuel (km)", value=15000, step=1000, key=f"km{i}")
        veh["duree"] = col.selectbox("Durée de détention (ans)", [3, 4, 5], key=f"duree{i}")
        veh["conso"] = col.number_input("Consommation (L/100km ou kWh/100km)", value=6.0, key=f"conso{i}")
        veh["carburant_prix"] = col.number_input("Prix carburant/électricité (€/L ou €/kWh)", value=1.9, key=f"carb{i}")
        veh["couts_fixes"] = col.number_input("Coûts fixes annuels (€)", value=1000, key=f"fixes{i}")
        veh_data.append(veh)

    if st.button("Calculer TCO"):
        col1, col2 = st.columns(2)
        for i, (col, veh) in enumerate(zip([col1, col2], veh_data), 1):
            duree = veh["duree"]
            km_total = veh["km"] * duree
            conso_total = veh["conso"] * km_total / 100
            carburant_total = conso_total * veh["carburant_prix"]
            couts_fixes_total = veh["couts_fixes"] * duree
            achat = veh["prix"] * 12 * duree if "mensualite" in veh else veh["prix"]
            tco_total = achat + carburant_total + couts_fixes_total
            tco_km = tco_total / km_total if km_total > 0 else 0

            col.metric(f"TCO total véhicule {i}", f"{tco_total:,.0f} €")
            col.metric(f"TCO par km", f"{tco_km:.2f} €/km")

            df = pd.DataFrame({
                "Catégorie": ["Achat", "Carburant", "Coûts fixes"],
                "Montant (€)": [achat, carburant_total, couts_fixes_total]
            })
            col.bar_chart(df.set_index("Catégorie"))

    if st.button("🔙 Revenir au menu principal"):
        st.session_state.page = "home"

# ======================
# MODULE 2 : CARBONE (ta version transformée en fonction)
# ======================
def calculateur_carbone():
    st.markdown("### 🌱 Calculateur de carbone")
    facteurs = {
        "Voiture thermique": 0.22,
        "Voiture électrique": 0.10,
    }

    if "mode" not in st.session_state:
        st.session_state.mode = None

    def reset_mode():
        st.session_state.mode = None

    if st.session_state.mode is None:
        st.write("### Choisis ton mode de calcul :")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Charger un fichier Excel", key="btn_excel"):
                st.session_state.mode = "excel"
        with col2:
            if st.button("📝 Saisir manuellement", key="btn_manual"):
                st.session_state.mode = "manuel"
    else:
        if st.button("🔙 Revenir au choix du mode"):
            reset_mode()

        if st.session_state.mode == "excel":
            st.markdown("""
            ### 📄 Format attendu :
            - 3 colonnes : `Date`, `Véhicule`, `Distance (km)`
            - Exemple : `2025-06-20 | Voiture thermique | 150.5`
            """)
            uploaded_file = st.file_uploader("Fichier Excel", type=["xlsx"])
            if uploaded_file:
                try:
                    df = pd.read_excel(uploaded_file)
                    colonnes = ["Date", "Véhicule", "Distance (km)"]
                    if list(df.columns) != colonnes:
                        st.error(f"Colonnes attendues : {colonnes}")
                    else:
                        df["Facteur_CO2"] = df["Véhicule"].map(facteurs)
                        if df["Facteur_CO2"].isnull().any():
                            st.error("Type de véhicule invalide.")
                        else:
                            df["Emissions_CO2 (kg)"] = df["Distance (km)"] * df["Facteur_CO2"]
                            st.subheader("📊 Données traitées")
                            st.dataframe(df)
                            total = df["Emissions_CO2 (kg)"].sum()
                            st.success(f"🌍 Total CO₂ : **{round(total, 2)} kg**")
                except Exception as e:
                    st.error(f"Erreur : {e}")
            else:
                st.info("💡 Uploade un fichier Excel pour commencer.")

        elif st.session_state.mode == "manuel":
            st.subheader("📝 Saisie manuelle")
            vehicule = st.selectbox("Type de véhicule", options=list(facteurs.keys()))
            distance = st.number_input("Distance parcourue (km)", min_value=0.0, step=0.1)
            if st.button("Calculer les émissions"):
                emission = distance * facteurs[vehicule]
                st.success(f"🌍 Ton {vehicule} a émis **{round(emission, 2)} kg** de CO₂")

    if st.button("🔙 Revenir au menu principal", key="back_from_carbone"):
        st.session_state.page = "home"
        reset_mode()

# ======================
# MODULE 3 : ZFE
# ======================
def verificateur_zfe():
    st.markdown("### 🏙️ Vérificateur compatibilité ZFE")
    date_immat = st.date_input("📅 Date d'immatriculation", value=datetime.date(2015, 1, 1))
    carburant = st.selectbox("⛽ Carburant", ["Essence", "Diesel", "Hybride", "Électrique"])
    norme = st.selectbox("🛡️ Norme Euro", ["Euro 2", "Euro 3", "Euro 4", "Euro 5", "Euro 6"])
    restrictions = {
        ("Diesel", "Euro 3"): "❌ Interdit",
        ("Diesel", "Euro 4"): "⚠️ Restreint",
        ("Essence", "Euro 2"): "❌ Interdit",
    }
    result = restrictions.get((carburant, norme), "✅ Autorisé")
    st.success(f"Résultat : {result}")

    if st.button("🔙 Revenir au menu principal"):
        st.session_state.page = "home"

# ======================
# ROUTEUR PRINCIPAL
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    main_menu()
elif st.session_state.page == "tco":
    simulateur_tco()
elif st.session_state.page == "carbone":
    calculateur_carbone()
elif st.session_state.page == "zfe":
    verificateur_zfe()
