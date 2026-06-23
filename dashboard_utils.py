import os
from typing import List, Optional

import pandas as pd

DATA_SOURCE = os.path.join("data", "BlendGSMAP_POS.202606dec02.xls")
LON_CANDIDATES = ["LON", "LONG", "LONGITUDE", "Longitude", "Lon"]
LAT_CANDIDATES = ["LAT", "LATITUDE", "Latitude", "Lat"]
CH_CANDIDATES = ["CH", "Curah Hujan", "curah hujan", "Rainfall", "rainfall"]
SH_CANDIDATES = ["Sifat Hujan (%)", "SH%", "SH", "Sifat Hujan", "sifat hujan"]
DATE_CANDIDATES = ["DATE", "Tanggal", "tanggal", "TIME", "Waktu", "waktu", "Date", "date", "Tanggal_", "Datetime"]

CATEGORY_ORDER = ["Bawah Normal", "Normal", "Atas Normal", "Tidak Tersedia"]
SH_COLOR_MAP = {
    "Bawah Normal": "#d62728",
    "Normal": "#2ca02c",
    "Atas Normal": "#1f77b4",
    "Tidak Tersedia": "#7f7f7f",
}


def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lower_names = {col.strip().lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        candidate_key = candidate.strip().lower()
        if candidate_key in lower_names:
            return lower_names[candidate_key]
    for candidate in candidates:
        candidate_key = candidate.strip().lower()
        for name, original in lower_names.items():
            if candidate_key == name:
                return original
    return None


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Dataframe kosong atau tidak tersedia")

    lon_col = find_column(df, LON_CANDIDATES)
    lat_col = find_column(df, LAT_CANDIDATES)
    ch_col = find_column(df, CH_CANDIDATES)
    sh_col = find_column(df, SH_CANDIDATES)

    if lon_col is None or lat_col is None or ch_col is None:
        missing = [name for name, found in [("LON", lon_col), ("LAT", lat_col), ("CH", ch_col)] if found is None]
        raise KeyError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")

    selected_columns = [lon_col, lat_col, ch_col]
    if sh_col is not None:
        selected_columns.append(sh_col)

    cleaned = df[selected_columns].copy()
    cleaned = cleaned.rename(columns={lon_col: "LON", lat_col: "LAT", ch_col: "CH"})
    if sh_col is not None:
        cleaned = cleaned.rename(columns={sh_col: "SH"})

    cleaned["LON"] = pd.to_numeric(cleaned["LON"], errors="coerce")
    cleaned["LAT"] = pd.to_numeric(cleaned["LAT"], errors="coerce")
    cleaned["CH"] = pd.to_numeric(cleaned["CH"], errors="coerce")
    cleaned = cleaned.dropna(subset=["LON", "LAT", "CH"])  # Curah hujan, koordinat wajib

    if "SH" in cleaned.columns:
        cleaned["SH"] = pd.to_numeric(cleaned["SH"], errors="coerce")

    return cleaned.reset_index(drop=True)


def load_excel_data(source_path: Optional[str] = None) -> pd.DataFrame:
    path = source_path or DATA_SOURCE
    if not os.path.exists(path):
        raise FileNotFoundError(f"File data tidak ditemukan: {path}")
    try:
        data = pd.read_excel(path, engine="xlrd")
    except Exception as exc:
        raise RuntimeError(
            "Gagal membaca file Excel. Pastikan file .xls tersedia dan paket xlrd terpasang."
        ) from exc
    return normalize_dataframe(data)


def get_datetime_column(df: pd.DataFrame) -> Optional[str]:
    for candidate in DATE_CANDIDATES:
        if candidate in df.columns:
            return candidate
    for column in df.columns:
        normalized = column.strip().lower()
        for candidate in DATE_CANDIDATES:
            if normalized == candidate.strip().lower():
                return column
    return None


def parse_datetime_column(df: pd.DataFrame) -> Optional[str]:
    date_col = get_datetime_column(df)
    if date_col is None:
        return None

    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    except Exception:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if df[date_col].notna().sum() < max(1, len(df) // 20):
        return None

    df[date_col] = df[date_col].dropna()
    return date_col


def add_sh_category(df: pd.DataFrame) -> pd.DataFrame:
    if "SH" not in df.columns:
        return df

    def classify(value):
        if pd.isna(value):
            return "Tidak Tersedia"
        if value < 85:
            return "Bawah Normal"
        if value <= 115:
            return "Normal"
        return "Atas Normal"

    df = df.copy()
    df["SH_CATEGORY"] = df["SH"].apply(classify)
    return df


def build_time_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    if date_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    series = (
        df.dropna(subset=[date_col, value_col])
        .groupby(date_col)[value_col]
        .mean()
        .reset_index()
        .sort_values(date_col)
    )
    return series


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "SH_CATEGORY" not in df.columns:
        return pd.DataFrame({"Kategori": [], "Jumlah": []})

    summary = (
        df["SH_CATEGORY"]
        .value_counts()
        .reindex(CATEGORY_ORDER, fill_value=0)
        .reset_index()
    )
    summary.columns = ["Kategori", "Jumlah"]
    return summary
