import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wärmeübertragung", layout="wide")

st.title("📊 Wärmeübertragung – Digitale Auswertung")

station = st.selectbox("Station auswählen", [
    "A – Wärmeleitung", "B – Konvektion", "C – Wärmestrahlung",
    "D – Thermosflasche", "E – Vergleich Thermos vs. Becher"
])

st.subheader("Messwerterfassung")
df = st.data_editor(
    pd.DataFrame({
        "Zeit [min]": [],
        "Temperatur [°C]": [],
        "Bemerkung": []
    }),
    num_rows="dynamic"
)

st.subheader("Diagramm")
diagrammtyp = st.radio("Diagrammtyp wählen", ["x-y-Diagramm", "Balkendiagramm"])

if diagrammtyp == "x-y-Diagramm":
    if "Zeit [min]" in df and "Temperatur [°C]" in df:
        fig, ax = plt.subplots()
        ax.plot(df["Zeit [min]"], df["Temperatur [°C]"], marker="o")
        ax.set_xlabel("Zeit [min]")
        ax.set_ylabel("Temperatur [°C]")
        ax.set_title(f"Temperaturverlauf – {station}")
        st.pyplot(fig)
elif diagrammtyp == "Balkendiagramm":
    if "Temperatur [°C]" in df:
        fig, ax = plt.subplots()
        ax.bar(df.index.astype(str), df["Temperatur [°C]"])
        ax.set_ylabel("Temperatur [°C]")
        ax.set_title(f"Vergleich – {station}")
        st.pyplot(fig)

st.subheader("🧠 Auswertung")
st.text_area("Was zeigt das Diagramm? Welche Wärmeübertragungsart ist dominant?", height=150)

st.download_button("📥 Arbeitsblatt herunterladen", data="Hier könnte ein PDF generiert werden", file_name="waermeuebertragung.pdf")

