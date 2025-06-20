import pandas as pd
from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)

# Charger les données Excel
df = pd.read_excel("data/trajets_exemple.xlsx")

# Dictionnaire des facteurs d'émission (kg CO2 par km)
facteurs = {
    "Voiture thermique": 0.22,
    "Voiture électrique": 0.10,
}

# Ajouter une colonne avec le facteur correspondant à chaque mode de transport
df["Facteur_CO2"] = df["Véhicule"].map(facteurs)

# Calculer les émissions de CO2
df["Emissions_CO2 (kg)"] = df["Distance (km)"] * df["Facteur_CO2"]

# Afficher le tableau complet avec les calculs
print(df)

# Afficher le total des émissions de CO2
total = df["Emissions_CO2 (kg)"].sum()
print(Fore.CYAN + "\n=== Bilan carbone ===" + Style.RESET_ALL)
print(f"{Fore.GREEN}Total CO₂ produit : {round(total, 2)} kg{Style.RESET_ALL}")