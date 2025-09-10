import os
import pandas as pd
from constants import DATENORDNER

def lade_alle_auswertungen():
    zusammenfassung = []
    for file in os.listdir(DATENORDNER):
        if file.endswith(".csv"):
            pfad = os.path.join(DATENORDNER, file)
            df = pd.read_csv(pfad)
            gruppe = file.split("_")[0]
            station = "_".join(file.split("_")[1:]).replace(".csv", "")
            auswertung = df["Auswertung"].iloc[0] if "Auswertung" in df.columns else ""
            zusammenfassung.append({
                "Gruppe": gruppe,
                "Station": station,
                "Auswertung": auswertung
            })
    return pd.DataFrame(zusammenfassung)
