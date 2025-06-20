import streamlit as st
import pandas as pd

st.title("🌱 Calculateur de CO₂")

facteurs = {
    "Voiture thermique": 0.22,
    "Voiture électrique": 0.10,
}

# On utilise session_state pour garder la sélection entre pages
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
    # Affiche toujours un bouton pour revenir au choix initial
    if st.button("🔙 Revenir au choix du mode"):
        reset_mode()

    if st.session_state.mode == "excel":
        st.markdown("""
        ### 📄 Format du fichier Excel attendu :
        - Le fichier doit contenir **exactement 3 colonnes** dans cet ordre :
          1. `Date` — format date (exemple : `2025-06-20`)
          2. `Véhicule` — soit **`Voiture thermique`** ou **`Voiture électrique`**
          3. `Distance (km)` — distance parcourue en kilomètres (nombre)
        - Les noms des colonnes doivent être **exactement** ceux-ci, sans espace en trop ni fautes.
        - Exemple d’une ligne valide :  
          `2025-06-20 | Voiture thermique | 150.5`
        """)

        uploaded_file = st.file_uploader("Choisis ton fichier Excel", type=["xlsx"])

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)

                colonnes_attendues = ["Date", "Véhicule", "Distance (km)"]
                if list(df.columns) != colonnes_attendues:
                    st.error(f"Erreur : Les colonnes doivent être exactement : {colonnes_attendues}")
                else:
                    df["Facteur_CO2"] = df["Véhicule"].map(facteurs)
                    if df["Facteur_CO2"].isnull().any():
                        st.error("Erreur : La colonne 'Véhicule' doit contenir uniquement 'Voiture thermique' ou 'Voiture électrique'.")
                    else:
                        df["Emissions_CO2 (kg)"] = df["Distance (km)"] * df["Facteur_CO2"]

                        st.subheader("📊 Données traitées")
                        st.dataframe(df)

                        total = df["Emissions_CO2 (kg)"].sum()
                        st.markdown(f"### 🌍 Total CO₂ produit : **{round(total, 2)} kg**")
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")
        else:
            st.info("💡 Uploade un fichier Excel pour commencer.")

    else:  # mode manuel
        st.subheader("📝 Saisie manuelle des données")

        vehicule = st.selectbox("Type de véhicule", options=list(facteurs.keys()))
        distance = st.number_input("Distance parcourue (km)", min_value=0.0, step=0.1)

        if st.button("Calculer les émissions"):
            facteur = facteurs[vehicule]
            emission = distance * facteur
            st.success(f"🌍 Ton véhicule {vehicule} a émis environ **{round(emission, 2)} kg** de CO₂ pour {distance} km parcourus.")