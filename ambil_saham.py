import yfinance as yf
from datetime import datetime
import os

ticker = "BBRI.JK"

# Tarik data interval 1 menit untuk 1 hari terakhir
data = yf.download(ticker, period="1d", interval="1m")

# Perbaikan format jika yfinance mengembalikan MultiIndex Columns
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

if not data.empty and len(data) > 0:
    # Buat folder jika belum ada
    os.makedirs("data_saham", exist_ok=True)
    
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
    nama_file = f"data_saham/{ticker}_{tanggal_hari_ini}.csv"
    
    # Simpan ke CSV
    data.to_csv(nama_file)
    print(f"Berhasil: Data disimpan di {nama_file} ({len(data)} baris data)")
else:
    print("Peringatan: Data kosong. Membuat file log kosong agar Git tidak error.")
    os.makedirs("data_saham", exist_ok=True)
    with open("data_saham/.placeholder", "w") as f:
        f.write("")
