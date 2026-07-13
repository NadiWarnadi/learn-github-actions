"""
Pengumpulan data harga menit murni curl_cffi (tanpa yfinance).
Impersonate Chrome penuh + dummy visit + shuffle + batch + random sleep.
"""

import os
import json
import random
import time
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from curl_cffi import requests

# Konfigurasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MASTER_CSV = "data_saham/master_emiten.csv"
DATA_DIR = Path("data_saham")
YEAR = datetime.now().year
DATA_DIR_YEAR = DATA_DIR / f"tahun={YEAR}"
DATA_DIR_YEAR.mkdir(parents=True, exist_ok=True)

# Headers standar seperti browser Chrome
BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

def create_session():
    """Buat session dengan impersonate Chrome."""
    return requests.Session(impersonate="chrome")

def dummy_visit(session):
    """Lakukan kunjungan tiruan ke homepage dan saham acak untuk mendapatkan cookies."""
    logger.info("🌐 Melakukan dummy visit ke Yahoo Finance...")
    
    # 1. Kunjungi halaman utama
    session.get("https://finance.yahoo.com/", headers=BASE_HEADERS)
    time.sleep(random.uniform(2.0, 4.0))
    
    # 2. Kunjungi halaman saham populer (seolah-olah browsing)
    sample_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"]
    chosen = random.choice(sample_tickers)
    headers_ticker = BASE_HEADERS.copy()
    headers_ticker["Referer"] = "https://finance.yahoo.com/"
    session.get(f"https://finance.yahoo.com/quote/{chosen}", headers=headers_ticker)
    time.sleep(random.uniform(2.0, 5.0))
    
    logger.info(f"✅ Dummy visit selesai (mengunjungi {chosen})")

def fetch_ticker_data(session, ticker, max_retries=3):
    """
    Ambil data 1 menit dari API Yahoo Finance menggunakan curl_cffi.
    Endpoint: chart/v8
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://finance.yahoo.com",
        "Referer": f"https://finance.yahoo.com/quote/{ticker}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ])
    }
    
    for attempt in range(max_retries):
        try:
            resp = session.get(url, headers=headers, timeout=30)
            if resp.status_code == 404:
                logger.warning(f"⛔ {ticker} tidak ditemukan (404).")
                return None
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}")
            
            data = resp.json()
            chart = data.get('chart', {})
            result = chart.get('result', [])
            if not result:
                return None
            
            meta = result[0]['meta']
            timestamps = result[0]['timestamp']
            indicators = result[0]['indicators']['quote'][0]
            
            # Cek apakah data kosong
            if not timestamps or not indicators.get('open'):
                return None
            
            # Buat DataFrame
            df = pd.DataFrame({
                'waktu': pd.to_datetime(timestamps, unit='s'),
                'open': indicators['open'],
                'high': indicators['high'],
                'low': indicators['low'],
                'close': indicators['close'],
                'volume': indicators['volume']
            })
            
            # Hapus baris NaN
            df.dropna(inplace=True)
            if df.empty:
                return None
            
            # Tambahkan kode emiten
            df['emiten_code'] = ticker
            return df
            
        except Exception as e:
            wait_time = (2 ** attempt) + random.uniform(1, 3)
            logger.warning(f"⚠️ Gagal ambil {ticker} (attempt {attempt+1}): {e}. Retry dalam {wait_time:.1f}s")
            time.sleep(wait_time)
    
    return None

def main():
    # 1. Baca master emiten
    if not os.path.exists(MASTER_CSV):
        logger.error(f"❌ {MASTER_CSV} tidak ditemukan. Jalankan tarik_emiten dulu.")
        return
    
    df_master = pd.read_csv(MASTER_CSV)
    tickers = df_master['Kode'].tolist()
    logger.info(f"📊 Total emiten: {len(tickers)}")
    
    # 2. Buat session dan lakukan dummy visit (ini yang membuat kita tembus Cloudflare!)
    session = create_session()
    dummy_visit(session)
    
    # 3. Shuffle urutan emiten
    random.shuffle(tickers)
    logger.info("🔀 Urutan emiten diacak.")
    
    # 4. Batch ukuran 25
    BATCH_SIZE = 25
    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    logger.info(f"📦 Total batch: {len(batches)} (masing-masing {BATCH_SIZE} emiten)")
    
    all_dfs = []
    
    for batch_idx, batch in enumerate(batches):
        logger.info(f"🔄 Memproses batch {batch_idx+1}/{len(batches)}")
        
        # Proses setiap ticker dalam batch
        for ticker in batch:
            df = fetch_ticker_data(session, ticker)
            if df is not None:
                all_dfs.append(df)
                logger.info(f"✅ {ticker} berhasil")
            else:
                logger.info(f"⏭️ {ticker} dilewati (data kosong/suspended)")
            
            # Jeda kecil antar ticker (0.5 - 1.5 detik) agar tidak terlalu cepat
            time.sleep(random.uniform(0.5, 1.5))
        
        # Jeda antar batch: 3 - 6 detik (lebih slow untuk aman)
        if batch_idx < len(batches) - 1:
            sleep_batch = random.uniform(3.0, 6.0)
            logger.info(f"⏳ Jeda antar batch {sleep_batch:.1f}s")
            time.sleep(sleep_batch)
        
        # Coffee break setiap 5 batch (8-15 detik)
        if (batch_idx + 1) % 5 == 0:
            coffee = random.uniform(8.0, 15.0)
            logger.info(f"☕ Coffee break! Istirahat {coffee:.1f}s")
            time.sleep(coffee)
    
    # 5. Gabungkan semua data
    if not all_dfs:
        logger.warning("⚠️ Tidak ada data yang berhasil diambil hari ini.")
        return
    
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.sort_values(['waktu', 'emiten_code'], inplace=True)
    
    # 6. Simpan ke Parquet
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_file = DATA_DIR_YEAR / f"harga_{today_str}.parquet"
    final_df.to_parquet(out_file, index=False, compression='snappy')
    
    logger.info(f"🎉 SUKSES! Data tersimpan di {out_file}")
    logger.info(f"📈 Total baris: {len(final_df)} | Total emiten unik: {final_df['emiten_code'].nunique()}")

if __name__ == "__main__":
    main()