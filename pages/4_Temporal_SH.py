import streamlit as st
import plotly.express as px
from dashboard_utils import add_sh_category, category_summary, build_time_series


def main():
    st.set_page_config(page_title="Temporal Sifat Hujan", layout="wide")
    st.title("Analisis Temporal dan Distribusi Sifat Hujan")

    df = st.session_state.get("dataset")
    if df is None:
        st.warning("Dataset belum dimuat. Kembali ke Beranda untuk memuat data.")
        return

    df = add_sh_category(df)
    if "SH_CATEGORY" not in df.columns:
        st.error("Kolom SH tidak ditemukan dalam dataset sehingga analisis sifat hujan tidak dapat dilakukan.")
        return

    st.subheader("Distribusi Frekuensi Kategori Sifat Hujan")
    summary = category_summary(df)
    if summary.empty or "Kategori" not in summary.columns or "Jumlah" not in summary.columns:
        st.warning("Tidak ada kategori sifat hujan yang tersedia untuk dianalisis.")
    else:
        st.bar_chart(summary.set_index("Kategori")["Jumlah"])
        st.dataframe(summary, use_container_width=True)

    st.markdown("---")
    st.subheader("Histogram Sifat Hujan")
    if "SH" in df.columns:
        fig_hist = px.histogram(df, x="SH", nbins=30, title="Histogram Nilai Sifat Hujan")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Kolom SH numerik tidak tersedia untuk histogram.")

    st.markdown("---")
    st.subheader("Tren Sifat Hujan dari Waktu ke Waktu")
    if "DATE" in df.columns:
        series = build_time_series(df, "DATE", "SH")
        if series.empty:
            st.warning("Tidak ada data temporal SH yang cukup untuk membuat grafik tren.")
        else:
            fig_line = px.line(series, x="DATE", y="SH", markers=True, title="Tren Rata-Rata Sifat Hujan")
            fig_line.update_layout(xaxis_title="Tanggal", yaxis_title="SH", margin={"r":0, "t":40, "l":0, "b":0})
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Kolom tanggal tidak tersedia sehingga tren temporal tidak dapat dihitung.")


if __name__ == "__main__":
    main()
