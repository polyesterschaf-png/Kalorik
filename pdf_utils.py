from fpdf import FPDF
import os
from datetime import datetime
import tempfile
class PDF(FPDF):
    def header(self):
        logo_path = os.path.join("assets", "HPG-Header-Logo_v2.png")
        if os.path.exists(logo_path):
            self.image(logo_path, x=160, y=10, w=40)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Digitale Auswertung – Wärmeübertragung", ln=True, align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Seite {self.page_no()}", align="C")

def create_pdf(gruppe, station, df, auswertung_text, fig=None):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Kopfbereich
    pdf.cell(0, 10, f"Gruppe: {gruppe}", ln=True)
    pdf.cell(0, 10, f"Station: {station}", ln=True)
    pdf.cell(0, 10, f"Zeitpunkt: {timestamp}", ln=True)
    pdf.ln(5)

    # Auswertung
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "🧠 Auswertung:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, auswertung_text)
    pdf.ln(5)

    # Diagramm einfügen (falls vorhanden)
    if fig:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, dpi=150)
            pdf.image(tmpfile.name, x=10, w=180)
        os.unlink(tmpfile.name)
        pdf.ln(5)

    # Messwerte als Tabelle
    if not df.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "📊 Messwerte:", ln=True)
        pdf.set_font("Arial", size=10)

        col_widths = [40] * len(df.columns)
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], 8, col, border=1)
        pdf.ln()

        for _, row in df.iterrows():
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 8, str(item), border=1)
            pdf.ln()

    return pdf.output(dest='S').encode('latin1')
