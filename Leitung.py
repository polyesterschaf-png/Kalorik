import streamlit as st
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt

# Eigene Module
from constants import STATIONEN, DATENORDNER
from data_utils import lade_daten, speichere_daten
from pdf_utils import create_pdf
from plot_utils import plot_balken, plot_verlauf

# Streamlit Setup
st.set_page_config(page_title="Wärmeübertragung", layout="wide")
st.title("📊 Wärmeübertragung – Digitale Auswertung")

# Lehrkraftmodus mit Passwortschutz
st.sidebar.header("🔐 Lehrkraftzugang")
lehrkraft_passwort = st.sidebar.text_input("Passwort eingeben", type="password")
lehrkraft_aktiv = lehrkraft_passwort == "physik2025"

if lehrkraft_aktiv:
    st.sidebar.success("Zugang gewährt")
else:
    if lehrkraft_passwort != "":
        st.sidebar.error("Zugang verweigert")

# Lehrkraftmodus
if lehrkraft_aktiv:
    st.header("👩‍🏫 Lehrkraftmodus – Gruppenauswertung")

    files = glob.glob(f"{DATENORDNER}/*.csv")
    if not files:
        st.info("Noch keine Daten vorhanden.")
    else:
        selected_file = st.selectbox("Gruppe/Station auswählen", files, key="lehrkraft_select")
        df, auswertung_text = lade_daten(selected_file)
        st.write("📊 Messwerte:")
        st.dataframe(df)
        st.write("🧠 Auswertung:")
        st.write(auswertung_text)

        pdf = create_pdf(
            os.path.basename(selected_file).split("_")[0],
            "_".join(os.path.basename(selected_file).split("_")[1:]).replace(".csv", ""),
            df,
            auswertung_text
        )
        st.download_button("📄 PDF herunterladen", data=pdf, file_name=os.path.basename(selected_file).replace(".csv", ".pdf"))

        # Aggregiertes Diagramm für Station E
        if "Vergleich Thermos vs. Becher" in selected_file:
            st.subheader("📈 Gesamtdiagramm Station E – alle Gruppen")
            fig, ax = plt.subplots()
            for f in files:
                if "Vergleich Thermos vs. Becher" in f:
                    df_e = pd.read_csv(f)
                    gruppe = os.path.basename(f).split("_")[0]
                    ax.plot(df_e["Zeit [min]"], df_e["Temperatur Thermos [°C]"], label=f"{gruppe} – Thermos", linestyle="--")
                    ax.plot(df_e["Zeit [min]"], df_e["Temperatur Becher [°C]"], label=f"{gruppe} – Becher", linestyle=":")
            ax.set_xlabel("Zeit [min]")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_ylim(bottom=0)
            ax.legend()
            pdf = create_pdf(gruppen_id, station, df, auswertung, fig)
            st.pyplot(fig)

# Schülermodus
else:
    st.header("👨‍🎓 Schülermodus – Datenerfassung & Auswertung")

    gruppen_id = st.text_input("🔢 Gruppen-ID eingeben", max_chars=30)
    station = st.selectbox("Station auswählen", STATIONEN, key="station_schueler")
    stationsname = station.replace("–", "").replace(" ", "_")
    speicherpfad = f"{DATENORDNER}/{gruppen_id}_{stationsname}.csv"

    df, auswertung_vorlage = lade_daten(speicherpfad)

    # Station B – Bild & Text
    if station == "B – Konvektion":
        st.subheader("📷 Beobachtung statt Messung")
        uploaded_file = st.file_uploader("Bild hochladen (JPG, PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, caption="Deine Beobachtung", use_column_width=True)
            with open(f"{DATENORDNER}/{gruppen_id}_{stationsname}_bild.png", "wb") as f:
                f.write(uploaded_file.getbuffer())

    # Stationen A & C – Balkendiagramm
    elif station in ["A – Wärmeleitung", "C – Wärmestrahlung"]:
        st.subheader("Messwerterfassung")
        if df.empty:
            df = pd.DataFrame({
                "Kategorie": ["Material 1", "Material 2"],
                "Temperatur [°C]": [None, None],
                "Bemerkung": ["", ""]
            })
        df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        st.subheader("📈 Balkendiagramm")
        try:
            fig = plot_balken(df, station, gruppen_id)
            pdf = create_pdf(gruppen_id, station, df, auswertung, fig)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

    # Station E – Temperaturverlauf
    elif station == "E – Vergleich Thermos vs. Becher":
        st.subheader("Messwerterfassung")
        if df.empty:
            df = pd.DataFrame({
                "Zeit [min]": [],
                "Temperatur Thermos [°C]": [],
                "Temperatur Becher [°C]": [],
                "Bemerkung": []
            })
        df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        st.subheader("📈 Temperaturverlauf")
        try:
            fig = plot_verlauf(df, station, gruppen_id)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

    # Station D – Nur Text
    elif station == "D – Thermosflasche":
        st.info("📌 Diese Station benötigt keine Messwerte.")

    # Auswertung
    st.subheader("🧠 Auswertung")
    auswertung = st.text_area("Was zeigt das Diagramm oder deine Beobachtung?", value=auswertung_vorlage, height=150, key="auswertung")

    # Speichern & PDF
    if st.button("💾 Ergebnisse speichern"):
        if gruppen_id:
            speichere_daten(speicherpfad, df, auswertung)
            st.success(f"Ergebnisse gespeichert unter: {speicherpfad}")
            pdf = create_pdf(gruppen_id, station, df, auswertung)
            st.download_button("📄 PDF herunterladen", data=pdf, file_name=f"{gruppen_id}_{stationsname}.pdf")
        else:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
