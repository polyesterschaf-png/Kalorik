import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

st.set_page_config(page_title="Wärmeübertragung", layout="wide")
st.title("📊 Wärmeübertragung – Digitale Auswertung")

# Datenordner
DATENORDNER = "gruppen_daten"
os.makedirs(DATENORDNER, exist_ok=True)

# Lehrkraftmodus mit Passwortschutz
st.sidebar.header("🔐 Lehrkraftzugang")
lehrkraft_passwort = st.sidebar.text_input("Passwort eingeben", type="password")
lehrkraft_aktiv = False

if lehrkraft_passwort == "physik2025":
    lehrkraft_aktiv = True
    st.sidebar.success("Zugang gewährt")
elif lehrkraft_passwort != "":
    st.sidebar.error("Zugang verweigert")

# Umschalten zwischen Lehrkraft- und Schülermodus
if lehrkraft_aktiv:
    st.header("👩‍🏫 Lehrkraftmodus – Gruppenauswertung")

    files = glob.glob(f"{DATENORDNER}/*.csv")
    if not files:
        st.info("Noch keine Daten vorhanden.")
    else:
        selected_file = st.selectbox("Gruppe/Station auswählen", files)
        df = pd.read_csv(selected_file)
        st.write(df)

        if "Zeit [min]" in df.columns and "Temperatur Thermos [°C]" in df.columns:
            st.subheader("📊 Aggregiertes Diagramm (Station E)")
            all_e_files = [f for f in files if "Vergleich Thermos vs. Becher" in f]
            fig, ax = plt.subplots()
            for f in all_e_files:
                df_e = pd.read_csv(f)
                gruppe = os.path.basename(f).split("_")[0]
                ax.plot(df_e["Zeit [min]"], df_e["Temperatur Thermos [°C]"], label=f"{gruppe} – Thermos", linestyle="--")
                ax.plot(df_e["Zeit [min]"], df_e["Temperatur Becher [°C]"], label=f"{gruppe} – Becher", linestyle=":")
            ax.set_xlabel("Zeit [min]")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_title("Gesamtdiagramm Station E – alle Gruppen")
            ax.set_ylim(bottom=0)
            ax.legend()
            st.pyplot(fig)

else:
    st.header("👨‍🎓 Schülermodus – Datenerfassung & Auswertung")

    gruppen_id = st.text_input("🔢 Gruppen-ID eingeben (z. B. 'Gruppe 1')", max_chars=30)
    station = st.selectbox("Station auswählen", [
        "A – Wärmeleitung", "B – Konvektion", "C – Wärmestrahlung",
        "D – Thermosflasche", "E – Vergleich Thermos vs. Becher"
    ])

    stationsname = station.replace("–", "").replace(" ", "_")
    speicherpfad = f"{DATENORDNER}/{gruppen_id}_{stationsname}.csv"

    # Lade vorhandene Daten, falls vorhanden
    if os.path.exists(speicherpfad):
        df = pd.read_csv(speicherpfad)
        auswertung_vorlage = df["Auswertung"].iloc[0] if "Auswertung" in df.columns else ""
        df = df.drop(columns=["Auswertung"], errors="ignore")
        st.info("Vorherige Eingaben wurden geladen.")
    else:
        df = pd.DataFrame()
        auswertung_vorlage = ""

    # Station B: keine Messwerte
    if station == "B – Konvektion":
        st.subheader("📷 Beobachtung statt Messung")
        st.info("Diese Station benötigt keine Messwerte. Bitte fertige eine Skizze oder ein Foto an und beschreibe deine Beobachtung unten.")

    # Stationen A & C: Balkendiagramm
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
            fig, ax = plt.subplots()
            categories = df["Kategorie"].astype(str)
            temperatures = df["Temperatur [°C]"].astype(float)

            ax.bar(categories, temperatures, color="orange")
            ax.set_xlabel("Kategorie")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_title(f"{station} – {gruppen_id}")
            ax.set_ylim(bottom=0)

            for i, temp in enumerate(temperatures):
                ax.text(i, temp + 0.5, f"{temp:.1f}°C", ha='center')

            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

    # Station E: Temperaturverlauf
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
            fig, ax = plt.subplots()
            ax.plot(df["Zeit [min]"], df["Temperatur Thermos [°C]"], label="Thermos", marker="o")
            ax.plot(df["Zeit [min]"], df["Temperatur Becher [°C]"], label="Becher", marker="s")
            ax.set_xlabel("Zeit [min]")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_title(f"{station} – {gruppen_id}")
            ax.set_ylim(bottom=0)
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Fehler beim Zeichnen des Diagramms: {e}")

    # Station D: keine Messwerte
    elif station == "D – Thermosflasche":
        st.info("📌 Diese Station benötigt keine Messwerte. Bitte direkt zur Auswertung übergehen.")

    # Auswertung
    st.subheader("🧠 Auswertung")
    auswertung = st.text_area("Was zeigt das Diagramm oder deine Beobachtung? Welche Wärmeübertragungsart ist dominant?",
                              value=auswertung_vorlage, height=150)

    # Speichern
    if st.button("💾 Ergebnisse speichern"):
        if gruppen_id:
            df["Auswertung"] = auswertung
            df.to_csv(speicherpfad, index=False)
            st.success(f"Ergebnisse für {gruppen_id} gespeichert unter: {speicherpfad}")
        else:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
if not lehrkraft_aktiv:
    # Schülermodus
    st.header("👨‍🎓 Schülermodus – Datenerfassung & Auswertung")

    gruppen_id = st.text_input("🔢 Gruppen-ID eingeben", max_chars=30)
    station = st.selectbox("Station auswählen", [
        "A – Wärmeleitung", "B – Konvektion", "C – Wärmestrahlung",
        "D – Thermosflasche", "E – Vergleich Thermos vs. Becher"
    ])

    stationsname = station.replace("–", "").replace(" ", "_")
    speicherpfad = f"{DATENORDNER}/{gruppen_id}_{stationsname}.csv"

    # Daten laden
    if os.path.exists(speicherpfad):
        df = pd.read_csv(speicherpfad)
        auswertung_vorlage = df["Auswertung"].iloc[0] if "Auswertung" in df.columns else ""
        df = df.drop(columns=["Auswertung"], errors="ignore")
        st.info("Vorherige Eingaben wurden geladen.")
    else:
        df = pd.DataFrame()
        auswertung_vorlage = ""

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
            fig, ax = plt.subplots()
            categories = df["Kategorie"].astype(str)
            temperatures = df["Temperatur [°C]"].astype(float)
            ax.bar(categories, temperatures, color="orange")
            ax.set_xlabel("Kategorie")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_title(f"{station} – {gruppen_id}")
            ax.set_ylim(bottom=0)
            for i, temp in enumerate(temperatures):
                ax.text(i, temp + 0.5, f"{temp:.1f}°C", ha='center')
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
            fig, ax = plt.subplots()
            ax.plot(df["Zeit [min]"], df["Temperatur Thermos [°C]"], label="Thermos", marker="o")
            ax.plot(df["Zeit [min]"], df["Temperatur Becher [°C]"], label="Becher", marker="s")
            ax.set_xlabel("Zeit [min]")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_title(f"{station} – {gruppen_id}")
            ax.set_ylim(bottom=0)
            ax.legend()
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
            df["Auswertung"] = auswertung
            df.to_csv(speicherpfad, index=False)
            st.success(f"Ergebnisse gespeichert unter: {speicherpfad}")
            pdf = create_pdf(gruppen_id, station, df, auswertung)
            st.download_button("📄 PDF herunterladen", data=pdf, file_name=f"{gruppen_id}_{stationsname}.pdf")
        else:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
            
st.subheader("📂 Gruppenauswahl")
gruppen = sorted(set([os.path.basename(f).split("_")[0] for f in files]))
stationen = sorted(set(["_".join(os.path.basename(f).split("_")[1:]).replace(".csv", "") for f in files]))
gruppe = st.selectbox("Gruppe auswählen", gruppen)
station_wahl = st.selectbox("Station auswählen", stationen)

pfad = f"{DATENORDNER}/{gruppe}_{station_wahl}.csv"
if os.path.exists(pfad):
    df = pd.read_csv(pfad)
    auswertung_text = df["Auswertung"].iloc[0] if "Auswertung" in df.columns else ""
    df = df.drop(columns=["Auswertung"], errors="ignore")
    st.write("📊 Messwerte:")
    st.dataframe(df)
    st.write("🧠 Auswertung:")
    st.write(auswertung_text)
    pdf = create_pdf(gruppe, station_wahl, df, auswertung_text)
    st.download_button("📄 PDF herunterladen", data=pdf, file_name=f"{gruppe}_{station_wahl}.pdf")
else:
    st.warning("Keine Daten für diese Auswahl gefunden.")
