import matplotlib.pyplot as plt

def plot_balken(df, station, gruppen_id):
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
    return fig
def plot_verlauf(df, station, gruppen_id):
    fig, ax = plt.subplots()
    ax.plot(df["Zeit [min]"], df["Temperatur Thermos [°C]"], label="Thermos", marker="o")
    ax.plot(df["Zeit [min]"], df["Temperatur Becher [°C]"], label="Becher", marker="s")
    ax.set_xlabel("Zeit [min]")
    ax.set_ylabel("Temperatur [°C]")
    ax.set_title(f"{station} – {gruppen_id}")
    ax.set_ylim(bottom=0)
    ax.legend()
    return fig
