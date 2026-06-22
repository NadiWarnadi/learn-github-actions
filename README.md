# 🚀 learn-github-actions

Repositori ini dibuat khusus sebagai wadah eksperimen dan tempat belajar memahami alur kerja (**Workflow**) pada **GitHub Actions**. Di sini, saya mempraktikkan konsep otomatisasi *Continuous Integration* (CI) dan *Continuous Deployment* (CD).

---

## 🎯 Tujuan Belajar
* Memahami struktur file konfigurasi YAML untuk workflow.
* Mempelajari komponen utama: *Triggers (Events)*, *Jobs*, *Steps*, dan *Runners*.
* Mencoba integrasi otomatis seperti pengetesan kode (*testing*) dan *linting*.
* Mengeksplorasi penggunaan *Actions* siap pakai dari GitHub Marketplace.

## 📂 Struktur Folder
```text
learn-github-actions/
├── .github/
│   └── workflows/
│       └── ci.yml          # File konfigurasi utama GitHub Actions
├── README.md               # Dokumentasi proyek (file ini)
└── ...                     # File proyek/kode sumber lainnya
```

## 🛠️ Alur Kerja (Workflow) yang Dibuat

### 1. CI Workflow (`ci.yml`)
Workflow ini otomatis berjalan setiap kali ada aktivitas **`push`** atau **`pull_request`** ke *branch* utama (`main`).
* **Runner:** `ubuntu-latest`
* **Tugas:** Melakukan *checkout* kode, menyiapkan lingkungan (runtime), mengunduh dependensi, dan menjalankan pengujian (*automated testing*).

## 🚀 Cara Menggunakan Repositori Ini
1. **Fork atau Clone** repositori ini ke komputer lokal Anda.
2. Buat *branch* baru atau langsung lakukan perubahan kecil pada kode di *branch* `main`.
3. Lakukan `git commit` dan `git push` ke GitHub.
4. Buka tab **Actions** di halaman GitHub repositori ini untuk melihat proses otomatisasi berjalan secara *real-time*!

---
💡 *Proyek ini murni untuk jalur pembelajaran dan dokumentasi pribadi dalam menguasai DevOps tools.*
