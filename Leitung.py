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

    if station in ["A – Wärmeleitung", "B – Konvektion", "C – Wärmestrahlung"]:
        st.subheader("Messwerterfassung")
        df = st.data_editor(
            pd.DataFrame({
                "Kategorie": ["Material 1", "Material 2"],
                "Temperatur [°C]": [None, None],
                "Bemerkung": ["", ""]
            }),
            num_rows="dynamic",
            use_container_width=True
        )

        st.subheader("📈 Balkendiagramm")
        try:
            fig, ax = plt.subplots()
            categories = df["Kategorie"]
            temperatures = df["Temperatur [°C]"]

            fig, ax = plt.subplots()
            ax.bar(x=categories, height=temperatures, color="orange")
            ax.set_xlabel("Kategorie")
            ax.set_ylabel("Temperatur [°C]")
            ax.set_title(f"{station} – {gruppen_id}")
            ax.set_ylim(bottom=0)  # y-Achse beginnt bei 0 °C
            st.pyplot(fig)
        except:
            st.warning("Bitte gültige Werte eingeben.")

    elif station == "E – Vergleich Thermos vs. Becher":
        st.subheader("Messwerterfassung")
        df = st.data_editor(
            pd.DataFrame({
                "Zeit [min]": [],
                "Temperatur Thermos [°C]": [],
                "Temperatur Becher [°C]": [],
                "Bemerkung": []
            }),
            num_rows="dynamic",
            use_container_width=True
        )

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
        except:
            st.warning("Bitte vollständige Daten eingeben.")

    elif station == "D – Thermosflasche":
        st.info("📌 Diese Station benötigt keine Messwerte. Bitte direkt zur Auswertung übergehen.")
        df = pd.DataFrame()  # leere Tabelle für Speicherung

    # Auswertung
    st.subheader("🧠 Auswertung")
    auswertung = st.text_area("Was zeigt das Diagramm? Welche Wärmeübertragungsart ist dominant?", height=150)

    # Speichern
    if st.button("💾 Ergebnisse speichern"):
        if gruppen_id:
            speicherpfad = f"{DATENORDNER}/{gruppen_id}_{station}.csv"
            df.to_csv(speicherpfad, index=False)
            st.success(f"Ergebnisse für {gruppen_id} gespeichert unter: {speicherpfad}")
        else:
            st.error("Bitte zuerst eine Gruppen-ID eingeben.")
