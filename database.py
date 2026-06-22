import sqlite3
import requests

def tarik_data_dan_buat_db():
    # 1. URL API Publik Single Cell Portal (Mengambil daftar studi sel manusia)
    # Endpoint ini mengembalikan data JSON berisi metadata sel, organ, dan spesies
    api_url = "https://broadinstitute.org"
    
    print("⏳ Menghubungi API Single Cell Portal...")
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status() # Cek jika koneksi eror
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
    
    # 3. Iterasi data dari API dan simpan ke database
    # Struktur JSON dari API Single Cell Portal membungkus data di dalam list
    count = 0
    for study in data_json:
        # Kita saring khusus untuk spesies manusia (Homo sapiens)
        spesies = study.get('species', [''])[0]
        if 'Homo sapiens' in spesies or 'human' in spesies.lower():
            accession = study.get('accession')
            judul = study.get('name')
            # Ambil organ tubuh (misal: otak, darah, paru) jika tersedia
            organ = ", ".join(study.get('organs', ['Tidak Diketahui']))
            cell_count = study.get('cell_count', 0)

            # Masukkan ke database
            cursor.execute('''
                INSERT OR IGNORE INTO studi_sel (accession, judul_studi, organ_tubuh, spesies, jumlah_sel)
                VALUES (?, ?, ?, ?, ?)
            ''', (accession, judul, organ, spesies, cell_count))
            count += 1

    conn.commit()
    conn.close()
    print(f"✅ Sukses! {count} data studi sel manusia berhasil disimpan ke 'sel_manusia.db'.")

if __name__ == "__main__":
    tarik_data_dan_buat_db()
