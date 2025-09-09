import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wärmeübertragung", layout="wide")
st.title("📊 Wärmeübertragung – Digitale Auswertung")

# Gruppen-ID
gruppen_id = st.text_input("🔢 Gruppen-ID eingeben (z. B. 'Gruppe 1')", max_chars=20)

# Stationenauswahl
station = st.selectbox("Station auswählen", [
    "A – Wärmeleitung", "B – Konvektion", "C – Wärmestrahlung",
    "D – Thermosflasche", "E – Vergleich Thermos vs. Becher"
])

# Dynamische Spalten je nach Station
if station == "E – Vergleich Thermos vs. Becher":
    columns = ["Zeit [min]", "Temperatur Thermos [°C]", "Temperatur Becher [°C]", "Bemerkung"]
    diagrammtyp = "x-y-Diagramm"
else:
    columns = ["Kategorie", "Temperatur [°C]", "Bemerkung"]
    diagrammtyp = "Balkendiagramm"

# Dateneditor
df = st.data_editor(
    pd.DataFrame({col: [] for col in columns}),
    num_rows="dynamic",
    use_container_width=True
)

# Diagramm
st.subheader("📈 Diagramm")

if diagrammtyp == "x-y-Diagramm":
    try:
        fig, ax = plt.subplots()
        ax.plot(df["Zeit [min]"], df["Temperatur Thermos [°C]"], label="Thermos", marker="o")
        ax.plot(df["Zeit [min]"], df["Temperatur Becher [°C]"], label="Becher", marker="s")
        ax.set_xlabel("Zeit [min]")
        ax.set_ylabel("Temperatur [°C]")
        ax.set_title(f"Temperaturverlauf – {gruppen_id}")
        ax.legend()
        st.pyplot(fig)
    except Exception as e:
        st.error("Bitte vollständige Daten für beide Temperaturreihen eingeben.")
elif diagrammtyp == "Balkendiagramm":
    try:
        fig, ax = plt.subplots()
        ax.bar(df["Kategorie"], df["Temperatur [°C]"], color="skyblue")
        ax.set_ylabel("Temperatur [°C]")
        ax.set_title(f"Vergleich – {station} ({gruppen_id})")
        st.pyplot(fig)
    except Exception as e:
        st.error("Bitte gültige Kategorien und Temperaturen eingeben.")

# Auswertung
st.subheader("🧠 Auswertung")
st.text_area("Was zeigt das Diagramm? Welche Wärmeübertragungsart ist dominant?", height=150)

# Downloadhinweis
st.info("📥 Du kannst dein Arbeitsblatt direkt in der App herunterladen oder die Ergebnisse hier sichern.")
