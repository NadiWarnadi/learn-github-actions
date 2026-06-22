import sqlite3
import requests

def tarik_data_dan_buat_db():
    # 1. URL ENDPOINT API RESMI (Mengembalikan data list JSON berisi metadata studi sel)
    api_url = "https://broadinstitute.org"
    
    print("⏳ Menghubungi API Single Cell Portal...")
    try:
        # Menambahkan header User-Agent agar tidak diblokir oleh sistem keamanan server API
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status() 
        data_json = response.json()
    except Exception as e:
        print(f"❌ Gagal menarik data dari API: {e}")
        return

    # 2. Inisialisasi Database SQLite Lokal
    conn = sqlite3.connect('sel_manusia.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS studi_sel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accession TEXT UNIQUE,
            judul_studi TEXT,
            organ_tubuh TEXT,
            spesies TEXT,
            jumlah_sel INTEGER
        )
    ''')

    print("⚡ Memproses data JSON ke dalam SQLite...")
    
    count = 0
    # Memastikan data_json berwujud list sebelum di-looping
    if isinstance(data_json, list):
        for study in data_json:
            # Ambil daftar spesies (biasanya berbentuk list dari API)
            spesies_list = study.get('species', [])
            # Gabungkan list spesies menjadi string teks biasa agar mudah dicari
            spesies_text = ", ".join(spesies_list) if isinstance(spesies_list, list) else str(spesies_list)
            
            # Saring khusus data studi manusia (Homo sapiens)
            if 'Homo sapiens' in spesies_text or 'human' in spesies_text.lower():
                accession = study.get('accession')
                judul = study.get('name')
                
                # Ambil daftar organ tubuh dari API
                organ_list = study.get('organs', [])
                organ = ", ".join(organ_list) if isinstance(organ_list, list) else str(organ_list)
                
                cell_count = study.get('cell_count', 0)

                # Masukkan ke database SQLite
                cursor.execute('''
                    INSERT OR IGNORE INTO studi_sel (accession, judul_studi, organ_tubuh, spesies, jumlah_sel)
                    VALUES (?, ?, ?, ?, ?)
                ''', (accession, judul, organ, spesies_text, cell_count))
                count += 1

    conn.commit()
    conn.close()
    print(f"✅ Sukses! {count} data studi sel manusia berhasil disimpan ke 'sel_manusia.db'.")

if __name__ == "__main__":
    tarik_data_dan_buat_db()
