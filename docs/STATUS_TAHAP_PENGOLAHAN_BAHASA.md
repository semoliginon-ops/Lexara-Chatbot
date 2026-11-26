# Status Pengembangan — Tahap Pengolahan Kata dan Tata Bahasa Dasar

**Proyek:** Sistem Bahasa  
**Tahap roadmap:** Tahap 2 — Pengolahan kata dan tata bahasa dasar  
**Status keseluruhan:** Sedang dikerjakan  
**Dokumen induk:** [README.md](../README.md)  
**Checklist utama:** [CHECKLIST_PENGEMBANGAN.md](CHECKLIST_PENGEMBANGAN.md)  
**Dokumentasi kamus:** [KAMUS.md](KAMUS.md)

Dokumen ini adalah catatan kesinambungan kerja. Jika percakapan atau sesi pengembangan terputus, gunakan dokumen ini bersama README dan kondisi repository terbaru untuk melanjutkan pekerjaan tanpa mengulang langkah yang sudah selesai.

---

## 1. Tujuan tahap

Membangun prototipe pengolahan Bahasa Indonesia yang menerima teks, menormalkan masukan, memecah teks menjadi token, mengenali kata melalui kamus, lalu secara bertahap menganalisis bentuk kata, kelas kata, dan struktur kalimat.

Tahap ini menggunakan kamus 3.000 lema yang telah disusun. Fokusnya adalah membangun mesin pemrosesan, bukan menambah kumpulan dialog atau membuat LLM.

## 2. Batasan dan prinsip teknis

- Pemrosesan inti dirancang agar dapat berjalan lokal/offline.
- Tidak menggunakan LLM, GGUF, layanan cloud, atau API berbayar.
- Jangan mengubah data inti kamus (ID, lemma, POS, register, senses) hanya untuk mempermudah implementasi.
- Normalisasi tidak boleh menghapus informasi yang berpotensi mengubah makna.
- Pertahankan bentuk slang/informal; jangan otomatis membakukan kata.
- Tanda baca, tanda hubung, dan apostrof dipertahankan sampai ada aturan khusus yang teruji.
- Buat komponen kecil, terpisah, dan dapat diuji secara mandiri.
- Gunakan regression tests agar perbaikan berikutnya tidak merusak perilaku yang sudah benar.
- Jangan menjalankan GitHub Actions untuk pekerjaan rutin.

## 3. Kondisi repository saat dokumen ini dibuat

Branch kerja: `main`

### Pekerjaan selesai

1. Struktur repository diperiksa. Pada saat pemeriksaan, repository berisi:
   - `data/kamus/` untuk data kamus dan indeks token.
   - `docs/KAMUS.md` untuk skema dan aturan kamus.
   - `tools/audit_dictionary.py` untuk audit struktur kamus.
   - Belum ada modul pemrosesan bahasa sebelum pekerjaan tahap ini dimulai.
2. Modul normalisasi awal dibuat:
   - File: [`tools/normalisasi.py`](../tools/normalisasi.py)
   - Commit: `2fbb242b4c8682bb0ecb14c9e3094cbcbc405ccb`
   - Fungsi publik: `normalize_text(text: str) -> str`
   - Perilaku: Unicode NFC, casefold, merapikan whitespace berulang, menghapus spasi tepi.
   - Tidak menghapus tanda baca, tidak mengubah slang, tidak melakukan stemming, dan tidak mengubah tanda hubung/apostrof.
3. Regression tests awal dibuat:
   - File: [`tests/test_normalisasi.py`](../tests/test_normalisasi.py)
   - Commit: `576c42e845822a31c6e2548e09a06dd0af569d30`
   - Ada 8 kasus uji untuk kapitalisasi, whitespace, tanda baca, tanda hubung/apostrof, kosakata informal, Unicode NFC, string kosong, dan input non-string.

### Status verifikasi

- Kedua file telah dibuat di GitHub dan dibaca ulang untuk memastikan isi tersimpan.
- **Tes otomatis belum dieksekusi.** Jangan menyebut seluruh tes lulus sebelum benar-benar dijalankan pada lingkungan Python.
- Belum ada tokenizer, pencocokan kamus, analyzer morfologi, POS tagger, atau parser kalimat.
- Belum ada integrasi Android.

## 4. Pekerjaan yang sedang dikerjakan

**Subtahap 2.1 selesai: normalisasi teks versi awal tervalidasi.**

Delapan regression tests telah dijalankan pada lingkungan Python lokal terisolasi menggunakan salinan isi file dari GitHub. Hasilnya 8 lulus dan 0 gagal. Tidak ditemukan masalah pada delapan kasus yang diuji. Ini memvalidasi perilaku dasar, bukan menjamin seluruh kemungkinan masukan Bahasa Indonesia. Langkah aktif berikutnya adalah membuat tokenizer.

Perhatian khusus:
- Uji Unicode dengan karakter gabungan dan karakter yang sudah terkomposisi.
- Pastikan spasi tab/baris baru ditangani konsisten.
- Pastikan tanda baca tidak hilang.
- Pastikan kata slang tetap sama selain normalisasi kapitalisasi.
- Jangan menganggap casefold selalu identik dengan lowercase untuk semua karakter; perilaku ini disengaja dan perlu dicatat.

## 5. Urutan pekerjaan berikutnya

Ikuti urutan ini. Jangan melompat ke parser kalimat sebelum komponen sebelumnya tersedia dan diuji.

### 5.1 Validasi normalisasi — selesai
- [x] Jalankan 8 regression tests pada lingkungan Python lokal terisolasi menggunakan salinan isi file dari GitHub.
- [x] Catat hasil: 8 tes lulus, 0 gagal.
- [x] Tidak ditemukan bug pada kasus yang diuji; tidak ada perubahan kode yang diperlukan.
- [x] Tetapkan normalisasi sebagai baseline awal. Pengujian ulang tetap dilakukan saat regression suite terpadu tersedia.

### 5.2 Tokenizer
- [ ] Buat `tools/tokenizer.py`.
- [ ] Pecah teks hasil normalisasi menjadi kata dan tanda baca.
- [ ] Pertahankan tanda baca sebagai token tersendiri.
- [ ] Pertahankan bentuk bertanda hubung sesuai kebijakan awal; jangan memecahnya tanpa aturan yang disengaja.
- [ ] Buat tes untuk spasi, tanda baca berulang, angka, kata berimbuhan, kata ulang, apostrof, dan teks kosong.

Contoh target awal:
- Masukan: `Aku mau makan nasi!`
- Token: `["aku", "mau", "makan", "nasi", "!"]`

Contoh ini adalah target perilaku tokenizer, bukan klaim bahwa tokenizer sudah dibuat.

### 5.3 Pencocokan token ke kamus
- [ ] Baca format JSONL batch kamus yang sebenarnya sebelum membuat loader.
- [ ] Buat loader yang dapat membaca batch tanpa mengubah sumber data.
- [ ] Buat pencarian token terhadap lemma dan token index yang relevan.
- [ ] Bedakan hasil: lemma ditemukan, varian ditemukan, bentuk turunan tercatat, atau tidak dikenal.
- [ ] Tangani satu kata dengan beberapa sense atau POS tanpa memilih makna secara gegabah.
- [ ] Buat tes menggunakan contoh nyata dari kamus.

### 5.4 Analisis morfologi
- [ ] Susun inventaris pola imbuhan Bahasa Indonesia berdasarkan dokumentasi dan data.
- [ ] Tangani prefiks, sufiks, konfiks, reduplikasi, dan perubahan bentuk yang relevan.
- [ ] Hindari stemming agresif yang mengubah kata atau memotong bentuk yang bukan imbuhan.
- [ ] Gunakan kamus sebagai pemeriksa kandidat bentuk dasar.
- [ ] Buat tes untuk bentuk valid, bentuk ambigu, dan kata yang tidak boleh dipotong.

### 5.5 Pengenalan kelas kata (POS)
- [ ] Gunakan kode POS resmi dalam `docs/KAMUS.md`.
- [ ] Pertahankan kemungkinan lebih dari satu POS/sense untuk kata ambigu.
- [ ] Mulai dari identifikasi leksikal, kemudian tambahkan petunjuk konteks kalimat.
- [ ] Ukur hasil pada kumpulan kalimat uji yang diberi label.

### 5.6 Analisis struktur kalimat dasar
- [ ] Tetapkan token dan hasil POS sebagai masukan parser.
- [ ] Kenali pola subjek, predikat, objek, pelengkap, dan keterangan secara bertahap.
- [ ] Uji variasi urutan kata dan kalimat sederhana.
- [ ] Catat kasus ambigu atau tidak teranalisis; jangan memaksakan hasil.

### 5.7 Dataset uji dan regression suite
- [ ] Buat kumpulan kalimat representatif dari percakapan sehari-hari.
- [ ] Sertakan bahasa baku, informal, slang, salah ketik, imbuhan, kata ulang, tanda baca, dan kalimat ambigu.
- [ ] Simpan expected output yang dapat diperiksa.
- [ ] Jalankan seluruh tes setiap kali aturan inti berubah.

## 6. Struktur file yang dituju

Struktur berikut adalah sasaran bertahap, bukan klaim bahwa seluruh file sudah tersedia:

```text
tools/
  audit_dictionary.py
  normalisasi.py
  tokenizer.py
  kamus_loader.py
  pencocokan_leksikal.py
  morfologi.py
  pos_tagger.py
  parser_kalimat.py

tests/
  test_normalisasi.py
  test_tokenizer.py
  test_kamus_loader.py
  test_pencocokan_leksikal.py
  test_morfologi.py
  test_pos_tagger.py
  test_parser_kalimat.py

docs/
  KAMUS.md
  STATUS_TAHAP_PENGOLAHAN_BAHASA.md
  DATASET_PENGUJIAN.md
```

Nama file dapat disesuaikan bila implementasi menunjukkan struktur yang lebih baik. Perubahan struktur harus dicatat di dokumen ini.

## 7. Aturan melanjutkan setelah sesi terputus

Saat melanjutkan proyek dari percakapan baru:

1. Baca README.md dan dokumen status ini terlebih dahulu.
2. Periksa branch dan isi repository terbaru; jangan mengandalkan ringkasan percakapan sebagai bukti kondisi GitHub saat ini.
3. Periksa file terakhir yang sedang dikerjakan dan commit terkait.
4. Cocokkan status aktual dengan checklist. Perbarui status ini bila ada pekerjaan baru.
5. Lanjutkan dari kotak checklist pertama yang belum selesai.
6. Jangan membuat ulang file atau commit yang sudah ada.
7. Jangan mengklaim tes lulus sebelum tes benar-benar dijalankan.
8. Kerjakan satu komponen kecil per giliran agar perubahan mudah diperiksa.
9. Jangan menjalankan GitHub Actions untuk pekerjaan rutin.

## 8. Kriteria selesai tahap

Tahap pengolahan kata dan tata bahasa dasar dinyatakan selesai jika:
- Normalisasi teks stabil dan memiliki regression tests.
- Tokenizer stabil dan memiliki regression tests.
- Token dapat dicocokkan ke kamus secara konsisten.
- Bentuk kata dasar/turunan dapat dianalisis dengan tingkat kesalahan yang terukur.
- POS dapat dikenali dengan mempertahankan ambiguitas yang relevan.
- Struktur kalimat sederhana dapat dianalisis dan diuji.
- Dataset uji serta regression suite tersedia.
- Keterbatasan dan kasus yang belum terpecahkan didokumentasikan.

Tahap ini tidak berarti sistem sudah memiliki pemahaman bahasa bebas seperti LLM. Tahap berikutnya pada roadmap adalah hubungan makna dan pemrosesan konteks.

---

**Titik lanjut:** buat `tools/tokenizer.py` dan `tests/test_tokenizer.py`. Normalisasi awal sudah diuji secara lokal: 8 lulus, 0 gagal.
