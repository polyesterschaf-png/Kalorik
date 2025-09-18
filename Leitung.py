
import re
from storage_github import gh_list_csv
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
from summary_utils import create_summary_pdf


def safe_component(s: str) -> str:
    if s is None: return ""
    s = s.strip().replace("–", "-").replace(" ", "_")
    return re.sub(r'[^A-Za-z0-9_\-\.]', "_", s)

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
# Lehrkraftmodus
if lehrkraft_aktiv:
    st.header("👩‍🏫 Lehrkraftmodus – Gruppenauswertung")
    try:
        files = gh_list_csv()  # CSVs aus GitHub
    except Exception as e:
        st.error("Konnte die Dateiliste aus GitHub nicht laden.")
        st.caption(str(e))  # zeigt z. B. "GitHub list error 403: Resource not accessible by integration"
        files = []
    if not files:
        st.info("Noch keine Daten vorhanden.")
    else:
        selected_file = st.selectbox("Gruppe/Station auswählen", files, key="lehrkraft_select")
        df, auswertung_text = lade_daten(selected_file)
        # ... (Rest unverändert)

        st.write("📊 Messwerte:")
        st.dataframe(df)
        st.write("🧠 Auswertung:")
        st.write(auswertung_text)

        fig = None
        # Diagramm für Station E im Lehrkraftmodus
        if "Vergleich Thermos vs. Becher" in selected_file:
            st.subheader("📈 Temperaturverlauf – Station E")
            try:
                # Prüfen, ob alle nötigen Spalten vorhanden sind
                required_cols = ["Zeit [min]", "Temperatur Thermos [°C]", "Temperatur Becher [°C]"]
                if all(col in df.columns for col in required_cols):
                    fig = plot_verlauf(df, "Station E", os.path.basename(selected_file).split("_")[0])
                    st.pyplot(fig)
                else:
                    st.warning("Die Datei enthält nicht alle nötigen Spalten für das Diagramm.")
            except Exception as e:
                st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

        pdf = create_pdf(
            os.path.basename(selected_file).split("_")[0],
            "_".join(os.path.basename(selected_file).split("_")[1:]).replace(".csv", ""),
            df,
            auswertung_text,
            fig
        )
        st.download_button("📄 PDF herunterladen", data=pdf, file_name=os.path.basename(selected_file).replace(".csv", ".pdf"))

    # Zusammenfassungs-PDF
    st.subheader("📋 Zusammenfassung aller Gruppen")
    if st.button("📄 Zusammenfassungs-PDF erstellen"):
        pdf = create_summary_pdf()
        st.download_button("📥 PDF herunterladen", data=pdf, file_name="Zusammenfassung_Waermeuebertragung.pdf")

# Schülermodus
else:
    st.header("👨‍🎓 Schülermodus – Datenerfassung & Auswertung")

    gruppen_id = st.text_input("🔢 Gruppen-ID eingeben", max_chars=30)
    station = st.selectbox("Station auswählen", STATIONEN, key="station_schueler")
    stationsname = station.replace("–", "").replace(" ", "_")
    speicherpfad = f"{gruppen_id}_{stationsname}.csv" if gruppen_id else "unbenannt.csv"

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
        st.subheader("📋 Messwerterfassung")
        if df.empty:
            df = pd.DataFrame({
                "Kategorie": ["Material 1", "Material 2"],
                "Temperatur [°C]": [None, None],
                "Bemerkung": ["", ""]
            })
        df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        fig = None
        st.subheader("📈 Balkendiagramm")
        try:
            fig = plot_balken(df, station, gruppen_id)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

        st.subheader("🧠 Auswertung")
        auswertung = st.text_area(
            "Was zeigt das Diagramm oder deine Beobachtung? Welche Wärmeübertragungsart ist dominant?",
            value=auswertung_vorlage,
            height=150,
            key="auswertung"
        )

       
        if st.button("💾 Ergebnisse speichern"):
            if not gruppen_id:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
        else:
            try:
                # ACHTUNG: zielname sicher befüllen (siehe unten)
                speichere_daten("IGNORIERT", df, auswertung, zielname=zielname)
            except Exception as e:
                st.error(f"GitHub-Fehler beim Speichern: {e}")  # zeigt z. B. „GitHub GET 401 ...: Bad credentials“
                st.stop()
            else:
                st.success(f"Ergebnisse gespeichert in GitHub: {zielname}")


    # Station E – Temperaturverlauf
    elif station == "E – Vergleich Thermos vs. Becher":
        st.subheader("📋 Messwerterfassung")
        if df.empty:
            df = pd.DataFrame({
                "Zeit [min]": [],
                "Temperatur Thermos [°C]": [],
                "Temperatur Becher [°C]": [],
                "Bemerkung": []
            })
        df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        fig = None
        st.subheader("📈 Temperaturverlauf")
        try:
            fig = plot_verlauf(df, station, gruppen_id)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

        st.subheader("🧠 Auswertung")
        auswertung = st.text_area(
            "Was zeigt das Diagramm oder deine Beobachtung?",
            value=auswertung_vorlage,
            height=150,
            key="auswertung"
        )

        if st.button("💾 Ergebnisse speichern"):
            if not gruppen_id:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
        else:
            try:
                # ACHTUNG: zielname sicher befüllen (siehe unten)
                speichere_daten("IGNORIERT", df, auswertung, zielname=zielname)
            except Exception as e:
                st.error(f"GitHub-Fehler beim Speichern: {e}")  # zeigt z. B. „GitHub GET 401 ...: Bad credentials“
                st.stop()
            else:
                st.success(f"Ergebnisse gespeichert in GitHub: {zielname}")

    # Station D – Nur Text
    elif station == "D – Thermosflasche":
        st.info("📌 Diese Station benötigt keine Messwerte.")
        st.subheader("🧠 Auswertung")
        auswertung = st.text_area(
            "Was zeigt deine Beobachtung?",
            value=auswertung_vorlage,
            height=150,
            key="auswertung"
        )

        if st.button("💾 Ergebnisse speichern"):
            if not gruppen_id:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
        else:
            try:
                # ACHTUNG: zielname sicher befüllen (siehe unten)
                speichere_daten("IGNORIERT", df, auswertung, zielname=zielname)
            except Exception as e:
                st.error(f"GitHub-Fehler beim Speichern: {e}")  # zeigt z. B. „GitHub GET 401 ...: Bad credentials“
                st.stop()
            else:
                st.success(f"Ergebnisse gespeichert in GitHub: {zielname}")
