# data_utils.py
import io
import pandas as pd
from storage_github import gh_upload_bytes, gh_download_bytes

def speichere_daten(pfad_ignoriert: str, df: pd.DataFrame, auswertung: str, zielname: str = None):
    if zielname is None:
        import os
        zielname = os.path.basename(pfad_ignoriert) if pfad_ignoriert else "unbenannt.csv"

    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    gh_upload_bytes(zielname, csv_bytes, message=f"Save CSV: {zielname}")

    txt_name = zielname.replace(".csv", "_auswertung.txt")
    gh_upload_bytes(txt_name, (auswertung or "").encode("utf-8"), message=f"Save TXT: {txt_name}")

def lade_daten(zielname: str):
    df = pd.DataFrame()
    auswertung = ""
    try:
        csv_bytes = gh_download_bytes(zielname)
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception:
        df = pd.DataFrame()

    try:
        txt_bytes = gh_download_bytes(zielname.replace(".csv", "_auswertung.txt"))
        auswertung = txt_bytes.decode("utf-8", errors="ignore")
    except Exception:
        auswertung = ""

    return df, auswertung
