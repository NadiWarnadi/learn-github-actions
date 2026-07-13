import os
import time
import random
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Daftar User-Agent untuk rotasi agar tidak dicurigai sebagai bot kaku
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

def buat_sesi_aman():
    """Membuat session HTTP dengan fitur auto-retry dan backoff yang kuat"""
    session = requests.Session()
    
    # Konfigurasi Retry jika terkena error 429 (Too Many Requests) atau 500/502/503/504
    retries = Retry(
        total=5,                  # Coba ulang maksimal 5 kali
        backoff_factor=3,         # Jeda meningkat: 3 detik, 6 detik, 12 detik...
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def sinkronisasi_master_emiten():
    print("=== Memulai Sinkronisasi Master Emiten Cerdas ===")
    
    folder_output = "data_saham"
    path_file = f"{folder_output}/master_emiten.csv"
    
    if not os.path.exists(folder_output):
        os.makedirs(folder_output)

    # 1. Load data lama untuk fungsi Smart Cache
    dict_cache_lama = {}
    if os.path.exists(path_file):
        try:
            df_lama = pd.read_csv(path_file)
            # Buat mapping ticker -> tanggal update terakhir
            dict_cache_lama = pd.Series(df_lama.updated_at.values, index=df_lama.ticker).to_dict()
            print(f"Berhasil memuat cache lama. Menemukan {len(dict_cache_lama)} data terdaftar.")
        except Exception as e:
            print(f"Gagal membaca cache lama (mungkin file korup/kosong): {e}")

    # 2. Daftar 900+ emiten kamu (Contoh pemicu, silakan ganti dengan list lengkapmu)
    list_target_emiten = ["BBRI", "TLKM", "ASII", "BBCA", "BMRI", "GOTO", "UNVR", "BUKA"] 
    
    session = buat_sesi_aman()
    data_terupdate = []
    
    batasan_hari_cache = 30 # Data profil perusahaan dianggap valid jika diupdate dalam 30 hari terakhir
    Hari_ini = datetime.now()

    for kode in list_target_emiten:
        ticker_id = f"{kode}.JK"
        
        # --- FITUR SMART CACHE (HEMAT KUOTA) ---
        if ticker_id in dict_cache_lama:
            try:
                tgl_update_terakhir = datetime.strptime(str(dict_cache_lama[ticker_id]), "%Y-%m-%d %H:%M:%S")
                # Jika data belum kadaluarsa (masih di bawah 30 hari), SKIP request ke internet
                if hari_ini - tgl_update_terakhir < timedelta(days=batasan_hari_cache):
                    print(f" Skip {ticker_id}: Data masih segar (Diperbarui {dict_cache_lama[ticker_id]})")
                    continue
            except ValueError:
                pass # Jika format tanggal rusak, abaikan cache dan tarik ulang
        
        # --- PROSES REQUEST AMAN & DINAMIS ---
        print(f" Memproses {ticker_id} dari server Yahoo...")
        
        # Ubah Header Session secara dinamis sebelum menembak API
        session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        
        try:
            ticker = yf.Ticker(ticker_id, session=session)
            info = ticker.info
            
            if not info or info.get("regularMarketPrice") is None:
                # Jika tidak ada harga, mungkin emiten disuspensi atau salah kode
                status = "Suspended/Inactive"
            else:
                status = "Active"

            data_terupdate.append({
                "ticker": ticker_id,
                "nama_perusahaan": info.get("longName", "N/A"),
                "sektor": info.get("sector", "N/A"),
                "industri": info.get("industry", "N/A"),
                "status_perusahaan": status,
                "updated_at": hari_ini.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # --- JEDA DINAMIS (ANTI BOT) ---
            # Beri jeda acak antara 1.5 sampai 3.5 detik per request agar polanya natural
            jeda = random.uniform(1.5, 3.5)
            time.sleep(jeda)
            
        except Exception as e:
            print(f" Gagal memproses {ticker_id}: {str(e)}")
            time.sleep(5) # Jeda lebih lama jika terjadi error agar server reda
            
    # 3. Gabungkan Data Hasil Tarikan Baru dengan Data Lama di Cache
    if data_terupdate:
        df_baru = pd.DataFrame(data_terupdate)
        if os.path.exists(path_file):
            df_lama = pd.read_csv(path_file)
            # Tumpuk data baru di atas data lama, hapus duplikat ticker, pertahankan yang paling baru
            df_final = pd.concat([df_baru, df_lama]).drop_duplicates(subset=["ticker"], keep="first")
        else:
            df_final = df_baru
            
        df_final.to_csv(path_file, index=False)
        print(f"=== Selesai! Master emiten diperbarui. Total data di file: {len(df_final)} ===")
    else:
        print("=== Selesai! Tidak ada data baru yang perlu ditarik hari ini (Semua cache valid). ===")

if __name__ == "__main__":
    sinkronisasi_master_emiten()