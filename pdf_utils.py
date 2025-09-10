from fpdf import FPDF

def create_pdf(gruppe, station, df, auswertung_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Gruppe: {gruppe}", ln=True)
    pdf.cell(200, 10, txt=f"Station: {station}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Auswertung:\n{auswertung_text}")
    pdf.ln(10)

    # Tabelle aus df
    pdf.set_font("Arial", size=10)
    for i, row in df.iterrows():
        zeile = ", ".join([f"{k}: {v}" for k, v in row.items()])
        pdf.multi_cell(0, 10, txt=zeile)

    return pdf.output(dest='S').encode('latin1')
