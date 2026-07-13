import os
import pandas as pd
from datetime import datetime

def proses_excel_bei():
    print("=== Memulai Pembersihan Data Excel BEI ===")
    
    folder_data = "data_saham"
    file_excel_bei = f"{folder_data}/daftar_saham_bei.xlsx"
    file_csv_output = f"{folder_data}/master_emiten.csv"
    
    # 1. Pastikan file Excel BEI sudah kamu upload ke folder data_saham/
    if not os.path.exists(file_excel_bei):
        print(f"Error: File '{file_excel_bei}' belum diupload!")
        return

    try:
        # 2. Baca file Excel
        df_bei = pd.read_excel(file_excel_bei, engine='openpyxl')
        
        # Mapping nama kolom asli dari BEI sesuai info kamu
        KOLOM_KODE = 'Kode'
        KOLOM_NAMA = 'Nama Perusahaan'
        KOLOM_TGL = 'Tanggal Pencatatan'
        KOLOM_SAHAM = 'Saham'
        KOLOM_PAPAN = 'Papan Pencatatan'
        
        # Validasi apakah kolom-kolom tersebut benar-benar ada di Excel
        kolom_wajib = [KOLOM_KODE, KOLOM_NAMA, KOLOM_TGL, KOLOM_SAHAM, KOLOM_PAPAN]
        for kol in kolom_wajib:
            if kol not in df_bei.columns:
                print(f"Error: Kolom '{kol}' tidak ditemukan di file Excel BEI!")
                print(f"Kolom yang ada saat ini: {df_bei.columns.tolist()}")
                return

        data_bersih = []
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Looping untuk membersihkan data per baris
        for index, row in df_bei.iterrows():
            kode_mentah = str(row[KOLOM_KODE]).strip()
            
            # Filter: Hanya ambil kode saham yang valid (4 karakter huruf, cth: BBRI)
            if not kode_mentah or len(kode_mentah) != 4 or not kode_mentah.isalpha():
                continue
            
            # Transformasi format ke Yahoo Finance (.JK)
            ticker_yf = f"{kode_mentah.upper()}.JK"
            nama = str(row[KOLOM_NAMA]).strip()
            papan = str(row[KOLOM_PAPAN]).strip()
            
            # Transformasi Tanggal Pencatatan menjadi YYYY-MM-DD standar database
            tgl_mentah = row[KOLOM_TGL]
            try:
                # Jika formatnya sudah datetime dari Excel
                tgl_formatted = pd.to_datetime(tgl_mentah).strftime("%Y-%m-%d")
            except:
                tgl_formatted = "N/A"
                
            # Transformasi Jumlah Saham Beredar menjadi angka murni (integer)
            try:
                saham_int = int(row[KOLOM_SAHAM])
            except:
                saham_int = 0

            # Masukkan ke dictionary struktur baru
            data_bersih.append({
                "ticker": ticker_yf,
                "nama_perusahaan": nama,
                "tanggal_pencatatan": tgl_formatted,
                "saham_beredar": saham_int,
                "papan_pencatatan": papan,
                "status_perusahaan": "Active",
                "updated_at": waktu_sekarang
            })
            
        # 4. Simpan hasil pembersihan ke CSV
        df_hasil = pd.DataFrame(data_bersih)
        df_hasil.to_csv(file_csv_output, index=False)
        
        print(f"\n=== SUKSES! ===")
        print(f"Berhasil merapikan {len(df_hasil)} emiten dari BEI.")
        print(f"File disimpan di: {file_csv_output}")
        print("\nContoh hasil data yang nyaman:")
        print(df_hasil.head(3).to_string())

    except Exception as e:
        print(f"Terjadi error saat memproses data: {str(e)}")

if __name__ == "__main__":
    proses_excel_bei()