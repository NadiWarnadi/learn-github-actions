import os
from datetime import datetime
import pandas as pd
import yfinance as yf

ticker = "BBRI.JK"

# 1. Tarik data interval 1 menit untuk 1 hari terakhir
# auto_adjust=True memastikan kolom 'Close' bersih dari 'Adj Close'
data = yf.download(ticker, period="1d", interval="1m", auto_adjust=True)

# 2. Perbaikan MultiIndex Columns untuk versi yfinance terbaru
if isinstance(data.columns, pd.MultiIndex):
    # Mengambil level pertama (Open, High, Low, Close, Volume)
    data.columns = data.columns.get_level_values(0)

if not data.empty and len(data) > 0:
    # 3. Buat folder jika belum ada
    os.makedirs("data_saham", exist_ok=True)

    # 4. Format Datetime index agar mudah dibaca di CSV (menghilangkan timezone)
    data.index = data.index.tz_localize(None)

    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
    nama_file = f"data_saham/{ticker}_{tanggal_hari_ini}.csv"

    # 5. Simpan ke CSV
    data.to_csv(nama_file)
    print(f"Berhasil: Data disimpan di {nama_file} ({len(data)} baris data)")
else:
    print(
        "Peringatan: Data kosong. Membuat file log kosong agar Git tidak"
        " error."
    )
    os.makedirs("data_saham", exist_ok=True)
    with open("data_saham/.placeholder", "w") as f:
        f.write("")
