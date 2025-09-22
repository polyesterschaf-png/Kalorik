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
    if s is None:
        return ""
    s = s.strip().replace("–", "-").replace("—", "-")
    # Leerzeichen zu Unterstrichen
    s = s.replace(" ", "_")
    # nur erlaubte Zeichen
    return re.sub(r'[^A-Za-z0-9_\-\.]', "_", s)

def make_zielname(gruppen_id: str, stationsname: str) -> str | None:
    """Gibt den Dateinamen für GitHub zurück oder None, wenn keine Gruppen-ID vorhanden ist."""
    if not gruppen_id:
        return None
    gid = safe_component(gruppen_id)
    stn = safe_component(stationsname)
    return f"{gid}_{stn}.csv"


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
            required_cols_E = ["Zeit [min]", "Temperatur Thermos [°C]", "Temperatur Becher [°C]"]
        if all(col in df.columns for col in required_cols_E):
            st.subheader("📈 Temperaturverlauf – Station E")
            try:
                # station_label = "E – Vergleich Thermos vs. Becher"  # falls du es im Plot brauchst
                fig = plot_verlauf(df, "E – Vergleich Thermos vs. Becher", os.path.basename(selected_file).split("_")[0])
                st.pyplot(fig)
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
   
    # Einheitliche, robuste Stationskomponente
    # Wir nehmen den sichtbaren Label-Text direkt als Komponente
    stationsname = safe_component(station)

    # Zielname festlegen (oder None, wenn noch keine ID vorhanden)
    zielname = make_zielname(gruppen_id, stationsname)


    # Daten laden NUR wenn eine Gruppen-ID vorhanden ist
    if zielname:
        df, auswertung_vorlage = lade_daten(zielname)
    else:
        # Ohne ID: Nichts von GitHub laden; sinnvolle Defaults bereitstellen
        df, auswertung_vorlage = pd.DataFrame(), ""

    # Station B – Bild & Text
if station == "B – Konvektion":
    st.subheader("📷 Beobachtung statt Messung")

    # Bild-Upload innerhalb des Blocks definieren
    uploaded_file = st.file_uploader(
        "Bild hochladen (JPG, PNG)", 
        type=["jpg", "jpeg", "png"], 
        key="b_bild"
    )

    if uploaded_file is not None:
        # Bild in der App anzeigen
        st.image(uploaded_file, caption="Deine Beobachtung", use_column_width=True)

        # Dateiendung/Bytes ermitteln
        import os
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            ext = ".png"
        file_bytes = uploaded_file.getvalue()  # bytes für Datei & GitHub

        # Dateiname konsistent & sicher
        bild_dateiname = f"{safe_component(gruppen_id)}_{stationsname}_bild{ext}"

        # Lokal speichern (optional – für direkte Wiederverwendung)
        try:
            os.makedirs(DATENORDNER, exist_ok=True)
            with open(os.path.join(DATENORDNER, bild_dateiname), "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            st.warning(f"Lokales Speichern des Bildes fehlgeschlagen: {e}")

        # Persistentes Speichern in GitHub (nur mit Gruppen-ID)
        if gruppen_id:
            try:
                gh_upload_bytes(
                    bild_dateiname,
                    file_bytes,
                    message=f"Bildupload Gruppe {gruppen_id} – {station}"
                )
                st.success("Bild wurde zusätzlich in GitHub gespeichert.")
            except Exception as e:
                st.warning(f"Bild konnte nicht in GitHub gespeichert werden: {e}")
        else:
            st.info("Tipp: Mit Gruppen-ID speichern wir das Bild auch in GitHub.")



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
                    st.stop()
            try:
                speichere_daten("IGNORIERT", df, auswertung, zielname=zielname)
            except Exception as e:
                st.error(f"GitHub-Fehler beim Speichern: {e}")  # z. B. „GitHub GET 401 ...: Bad credentials“
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
                    st.stop()
            try:
                speichere_daten("IGNORIERT", df, auswertung, zielname=zielname)
            except Exception as e:
                st.error(f"GitHub-Fehler beim Speichern: {e}")  # z. B. „GitHub GET 401 ...: Bad credentials“
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
                    st.stop()
            try:
                speichere_daten("IGNORIERT", df, auswertung, zielname=zielname)
            except Exception as e:
                st.error(f"GitHub-Fehler beim Speichern: {e}")  # z. B. „GitHub GET 401 ...: Bad credentials“
                st.stop()
            else:
                st.success(f"Ergebnisse gespeichert in GitHub: {zielname}")
