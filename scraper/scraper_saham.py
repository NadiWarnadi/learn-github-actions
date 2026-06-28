import math
import time
import pandas as pd
import yfinance as yf
from fake_useragent import UserAgent

def ambil_daftar_saham_bei():
    """Mengambil daftar seluruh saham di BEI secara dinamis dari Wikipedia"""
    try:
        url = "https://id.wikipedia.org/wiki/Daftar_perusahaan_yang_terdaftar_di_Bursa_Efek_Indonesia"
        tables = pd.read_html(url)
        
        # Biasanya daftar saham ada di tabel pertama atau kedua di halaman tersebut
        # Kita gabungkan semua kolom yang mengandung kode saham
        ticker_list = []
        for table in tables:
            if 'Kode' in table.columns:
                # Yahoo Finance butuh akhiran .JK untuk saham Indonesia (contoh: BBCA.JK)
                tickers = table['Kode'].astype(str).str.strip() + ".JK"
                ticker_list.extend(tickers.tolist())
        
        # Hapus duplikat jika ada
        ticker_list = list(set(ticker_list))
        # Bersihkan dari kode yang aneh atau terlalu pendek/panjang
        ticker_list = [t for t in ticker_list if len(t) == 7] # Contoh: BBCA.JK panjangnya 7 karakter
        
        print(f"🔥 Berhasil mendapatkan {len(ticker_list)} saham secara dinamis dari bursa.")
        return sorted(ticker_list)
    except Exception as e:
        print(f"Gagal mengambil daftar dinamis, menggunakan backup. Error: {e}")
        # Jika wikipedia eror, ini sebagai cadangan darurat saja
        return ["BBCA.JK", "BMRl.JK", "TLKM.JK", "ASII.JK"]

def bagi_menjadi_kloter(daftar_saham, ukuran_kloter=230):
    """Membagi daftar saham menjadi beberapa kloter secara dinamis"""
    for i in range(0, len(daftar_saham), ukuran_kloter):
        yield daftar_saham[i:i + ukuran_kloter]

# --- MAIN PROCESS ---
if __name__ == "__main__":
    # 1. Ambil list saham terbaru secara otomatis
    semua_saham = ambil_daftar_saham_bei()
    
    # 2. Atur ukuran kloter sesuai keinginan Anda (misal 230 saham)
    UKURAN_KLOTER = 230
    total_kloter = math.ceil(len(semua_saham) / UKURAN_KLOTER)
    
    print(f"📦 Total saham akan dibagi menjadi {total_kloter} kloter.")
    
    ua = UserAgent()
    
    # 3. Mulai looping per kloter secara dinamis
    for nomor_kloter, kloter in enumerate(bagi_menjadi_kloter(semua_saham, UKURAN_KLOTER), 1):
        print(f"\n🚀 Memproses Kloter {nomor_kloter}/{total_kloter} (Berisi {len(kloter)} saham)...")
        
        # Gabungkan list menjadi string panjang dipisahkan spasi untuk yfinance batch download
        saham_string = " ".join(kloter)
        
        # Header palsu agar aman
        headers = {'User-Agent': ua.random}
        
        # Tarik data 1 hari ke belakang dengan interval 1 menit
        # yfinance otomatis memproses semua saham di dalam string tersebut sekaligus
        try:
            data = yf.download(saham_string, period="1d", interval="1m", group_by='ticker')
            
            # Di sini nanti kita masukkan logika untuk merapikan data dan menyimpannya ke Parquet
            print(f"✅ Kloter {nomor_kloter} berhasil diunduh.")
            
        except Exception as e:
            print(f"❌ Gagal mengunduh kloter {nomor_kloter}: {e}")
        
        # Beri jeda 15 detik antar kloter agar server Yahoo Finance tidak curiga
        if nomor_kloter < total_kloter:
            print("⏳ Istirahat 15 detik sebelum kloter berikutnya...")
            time.sleep(15)

    print("\n🎉 Semua kloter selesai diproses!")