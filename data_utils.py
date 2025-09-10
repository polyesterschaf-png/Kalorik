import pandas as pd
import os

def lade_daten(pfad):
    if os.path.exists(pfad):
        try:
            df = pd.read_csv(pfad)
            auswertung = df["Auswertung"].iloc[0] if "Auswertung" in df.columns and not df["Auswertung"].empty else ""
            df = df.drop(columns=["Auswertung"], errors="ignore")
            return df, auswertung
        except pd.errors.EmptyDataError:
            return pd.DataFrame(), ""
        except Exception as e:
            print(f"Fehler beim Laden von {pfad}: {e}")
            return pd.DataFrame(), ""
    else:
        return pd.DataFrame(), ""


def speichere_daten(pfad, df, auswertung):
    df["Auswertung"] = auswertung
    df.to_csv(pfad, index=False)
