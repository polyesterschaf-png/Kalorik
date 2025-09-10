import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from constants import DATENORDNER

def clean_text(text):
    replacements = {
        "📊": "Messwerte:", "🧠": "Auswertung:", "📄": "PDF:",
        "–": "-", "°": " Grad", "ü": "ue", "ö": "oe", "ä": "ae", "ß": "ss"
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    return text.encode("latin1", "ignore").decode("latin1")

class SummaryPDF(FPDF):
    def header(self):
        logo_path = os.path.join("assets", "HPG-Header-Logo_v2.png")
        if os.path.exists(logo_path):
            self.image(logo_path, x=160, y=10, w=40)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Zusammenfassung aller Gruppen – Wärmeübertragung", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Seite {self.page_no()}", align="C")

def create_summary_pdf():
    pdf = SummaryPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.cell(0, 10, clean_text(f"Erstellt am: {timestamp}"), ln=True)
    pdf.ln(5)

    daten = []
    for file in os.listdir(DATENORDNER):
        if file.endswith(".csv"):
            pfad = os.path.join(DATENORDNER, file)
            try:
                df = pd.read_csv(pfad)
                if df.empty or "Auswertung" not in df.columns:
                    continue
                gruppe = file.split("_")[0]
                station = "_".join(file.split("_")[1:]).replace(".csv", "")
                auswertung = df["Auswertung"].iloc[0]
                daten.append({
                    "Gruppe": clean_text(gruppe),
                    "Station": clean_text(station),
                    "Auswertung": clean_text(auswertung)
                })
            except pd.errors.EmptyDataError:
                continue
            except Exception as e:
                print(f"Fehler beim Lesen von {file}: {e}")
                continue

    daten.sort(key=lambda x: x["Station"])

    aktuelle_station = ""
    for eintrag in daten:
        if eintrag["Station"] != aktuelle_station:
            aktuelle_station = eintrag["Station"]
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Station: {aktuelle_station}", ln=True)
            pdf.set_font("Arial", size=11)

        pdf.multi_cell(0, 8, f"Gruppe: {eintrag['Gruppe']}\nAuswertung: {eintrag['Auswertung']}")
        pdf.ln(3)

    return pdf.output(dest='S').encode('latin1')
