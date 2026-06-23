import streamlit as st
import plotly.express as px


def main():
    st.set_page_config(page_title="Spatial Curah Hujan", layout="wide")
    st.title("Peta Spasial Sebaran Curah Hujan")

    df = st.session_state.get("dataset")
    if df is None:
        st.warning("Dataset belum dimuat. Kembali ke Beranda untuk memuat data.")
        return

    if "CH" not in df.columns:
        st.error("Kolom CH tidak ditemukan dalam dataset.")
        return

    min_val = float(df["CH"].min())
    max_val = float(df["CH"].max())
    selected_range = st.slider(
        "Pilih rentang nilai curah hujan:", min_value=min_val,
        max_value=max_val, value=(min_val, max_val), step=max((max_val - min_val) / 100.0, 0.1)
    )

    filtered = df[(df["CH"] >= selected_range[0]) & (df["CH"] <= selected_range[1])]
    if filtered.empty:
        st.warning("Tidak ada titik data dalam rentang nilai yang dipilih.")
        return

    fig = px.scatter_mapbox(
        filtered,
        lat="LAT",
        lon="LON",
        color="CH",
        size="CH",
        size_max=12,
        zoom=4,
        mapbox_style="open-street-map",
        color_continuous_scale="Viridis",
        title="Sebaran Curah Hujan (CH)",
        hover_name="CH",
        hover_data={"LON": True, "LAT": True, "CH": True},
    )
    fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0}, coloraxis_colorbar_title="CH")

    st.plotly_chart(fig, use_container_width=True)
    st.write(
        "Visualisasi ini menunjukkan titik-titik pengamatan curah hujan pada peta. "
        "Gunakan filter untuk memfokuskan pada rentang curah hujan tertentu."
    )


if __name__ == "__main__":
    main()
