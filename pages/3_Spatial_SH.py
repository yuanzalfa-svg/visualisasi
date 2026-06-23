import streamlit as st
import plotly.express as px
from dashboard_utils import SH_COLOR_MAP, add_sh_category


def main():
    st.set_page_config(page_title="Spatial Sifat Hujan", layout="wide")
    st.title("Peta Spasial Klasifikasi Sifat Hujan")

    df = st.session_state.get("dataset")
    if df is None:
        st.warning("Dataset belum dimuat. Kembali ke Beranda untuk memuat data.")
        return

    df = add_sh_category(df)
    if "SH_CATEGORY" not in df.columns:
        st.error("Kolom SH tidak ditemukan dalam dataset sehingga klasifikasi tidak dapat ditampilkan.")
        return

    filtered = df.dropna(subset=["SH_CATEGORY"])
    if filtered.empty:
        st.warning("Tidak ada data sifat hujan yang valid untuk divisualisasikan.")
        return

    fig = px.scatter_mapbox(
        filtered,
        lat="LAT",
        lon="LON",
        color="SH_CATEGORY",
        category_orders={"SH_CATEGORY": ["Bawah Normal", "Normal", "Atas Normal", "Tidak Tersedia"]},
        color_discrete_map=SH_COLOR_MAP,
        size_max=10,
        zoom=4,
        mapbox_style="open-street-map",
        title="Klasifikasi Sifat Hujan berdasarkan Standar BMKG",
        hover_data={"LON": True, "LAT": True, "SH": True, "SH_CATEGORY": True},
    )
    fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0})

    st.plotly_chart(fig, use_container_width=True)
    st.write(
        "Peta ini menampilkan zona pengamatan sifat hujan dengan klasifikasi diskret: Bawah Normal, Normal, dan Atas Normal. "
        "Warna kontras membantu membedakan kategori pada peta."
    )


if __name__ == "__main__":
    main()
