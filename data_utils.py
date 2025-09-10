import pandas as pd
import os

def lade_daten(pfad):
    if os.path.exists(pfad):
        df = pd.read_csv(pfad)
        auswertung = df["Auswertung"].iloc[0] if "Auswertung" in df.columns else ""
        df = df.drop(columns=["Auswertung"], errors="ignore")
        return df, auswertung
    else:
        return pd.DataFrame(), ""

def speichere_daten(pfad, df, auswertung):
    df["Auswertung"] = auswertung
    df.to_csv(pfad, index=False)
