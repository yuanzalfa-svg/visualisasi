import streamlit as st
from dashboard_utils import load_excel_data, add_sh_category


def load_data_to_session():
    if "dataset" not in st.session_state:
        st.session_state["dataset"] = None
        st.session_state["load_error"] = None

    if st.session_state["dataset"] is None and st.session_state["load_error"] is None:
        try:
            df = load_excel_data()
            st.session_state["dataset"] = add_sh_category(df)
        except Exception as exc:
            st.session_state["load_error"] = str(exc)


def main():
    st.set_page_config(page_title="Dashboard Curah Hujan", layout="wide")
    load_data_to_session()

    st.title("Beranda Dashboard Curah Hujan")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        try:
            st.image("image/LOGO BMKG.png", width=100, caption="BMKG")
        except Exception:
            st.write("Logo BMKG tidak tersedia")
    with col2:
        st.markdown("### Dashboard Curah Hujan Interaktif")
        st.markdown("**Dibuat oleh: Yuan Zalfa Tanggahma**")
        st.markdown("Dashboard ini menampilkan analisis spasial dan temporal curah hujan serta klasifikasi sifat hujan.")
    with col3:
        try:
            st.image("image/LOGO STMKG.PNG", width=100, caption="STMKG")
        except Exception:
            st.write("Logo STMKG tidak tersedia")

    st.write(
        "Selamat datang di dashboard interaktif curah hujan. "
        "Gunakan menu di sebelah kiri untuk berpindah antar halaman analisis spasial dan temporal."
    )

    if st.session_state.get("load_error"):
        st.error("Terjadi kesalahan saat memuat data: " + st.session_state["load_error"])
        st.write(
            "Periksa bahwa file `data/BlendGSMAP_POS.202606dec02.xls` tersedia dan formatnya mendukung pembacaan Excel."
        )
        return

    df = st.session_state["dataset"]
    if df is None or df.empty:
        st.warning("Data tidak tersedia atau hasil pembacaan kosong. Pastikan file Excel benar.")
        return

    st.subheader("Ringkasan Data")
    st.write("Dataset telah dimuat ke session state dan siap untuk analisis di halaman berikutnya.")
    st.write("Kolom kunci yang digunakan: `LON`, `LAT`, `CH`, `SH` (jika tersedia).")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown("---")
    st.write("Gunakan halaman:")
    st.write("- `1_Spatial_CH`: visualisasi peta sebaran curah hujan.")
    st.write("- `2_Temporal_CH`: analisis tren waktu curah hujan.")
    st.write("- `3_Spatial_SH`: visualisasi klasifikasi sifat hujan.")
    st.write("- `4_Temporal_SH`: analisis tren dan distribusi sifat hujan.")


if __name__ == "__main__":
    main()
