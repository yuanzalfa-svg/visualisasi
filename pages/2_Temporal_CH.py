import streamlit as st
import plotly.express as px
from dashboard_utils import build_time_series


def main():
    st.set_page_config(page_title="Temporal Curah Hujan", layout="wide")
    st.title("Analisis Temporal Curah Hujan")

    df = st.session_state.get("dataset")
    if df is None:
        st.warning("Dataset belum dimuat. Kembali ke Beranda untuk memuat data.")
        return

    if "CH" not in df.columns:
        st.error("Kolom CH tidak ditemukan dalam dataset.")
        return

    has_date = "DATE" in df.columns
    if not has_date:
        st.info("Tidak ditemukan kolom tanggal yang jelas; menampilkan distribusi CH tanpa sumbu waktu.")
        fig = px.histogram(df, x="CH", nbins=30, title="Distribusi Curah Hujan")
        st.plotly_chart(fig, use_container_width=True)
        return

    series = build_time_series(df, "DATE", "CH")
    if series.empty:
        st.warning("Tidak ada data temporal yang cukup untuk membangun grafik tren.")
        return

    fig = px.line(series, x="DATE", y="CH", markers=True, title="Tren Curah Hujan Rata-rata per Periode")
    fig.update_layout(xaxis_title="Tanggal", yaxis_title="Curah Hujan (CH)", margin={"r":0, "t":40, "l":0, "b":0})

    st.plotly_chart(fig, use_container_width=True)
    st.write(
        "Grafik garis ini menunjukkan perubahan rata-rata curah hujan sepanjang waktu dengan periode berdasarkan nilai tanggal di dataset."
    )


if __name__ == "__main__":
    main()
