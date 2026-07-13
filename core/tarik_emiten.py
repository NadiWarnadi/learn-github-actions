"""
Script untuk membaca daftar saham BEI (Excel) dan menghasilkan master_emiten.csv
dengan format standar (kode + .JK, nama, tanggal pencatatan ISO, jumlah saham integer).
"""

import pandas as pd
import os
import re
from pathlib import Path

EXCEL_PATH = "data_saham/daftar_saham_bei.xlsx"
OUTPUT_CSV = "data_saham/master_emiten.csv"

def clean_number(s):
    """Hilangkan titik ribuan, ubah ke integer."""
    if isinstance(s, (int, float)):
        return int(s)
    s = str(s).strip()
    s = re.sub(r'[^\d]', '', s)
    return int(s) if s else 0

def main():
    if not os.path.exists(EXCEL_PATH):
        print(f"File {EXCEL_PATH} tidak ditemukan. Jalankan secara manual dengan mengunduh dari BEI.")
        return

    df = pd.read_excel(EXCEL_PATH, dtype=str)
    # Kolom yang diharapkan: No, Kode, Nama Perusahaan, Tanggal Pencatatan, Saham, Papan Pencatatan
    required_cols = ['Kode', 'Nama Perusahaan', 'Tanggal Pencatatan', 'Saham', 'Papan Pencatatan']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Kolom '{col}' tidak ditemukan di Excel. Periksa format file.")

    # Filter kode saham yang valid (hanya 4 huruf alfabet)
    df = df[df['Kode'].astype(str).str.match(r'^[A-Za-z]{4}$')].copy()

    # Transformasi
    df['Kode'] = df['Kode'].str.upper() + '.JK'
    df['Nama Perusahaan'] = df['Nama Perusahaan'].str.strip()
    df['Tanggal Pencatatan'] = pd.to_datetime(df['Tanggal Pencatatan'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['Saham'] = df['Saham'].apply(clean_number)

    df_out = df[['Kode', 'Nama Perusahaan', 'Tanggal Pencatatan', 'Saham', 'Papan Pencatatan']]
    df_out = df_out.sort_values('Kode').reset_index(drop=True)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df_out.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    print(f"✅ Master emiten berhasil disimpan ke {OUTPUT_CSV} dengan {len(df_out)} emiten.")

if __name__ == "__main__":
    main()