# Checklist Pengembangan — Sistem Bahasa

Dokumen ini adalah pusat pelacakan pekerjaan proyek. Perbarui checklist hanya setelah pekerjaan benar-benar selesai dan diverifikasi.

## Arti status

- [x] Selesai dan sudah diverifikasi.
- [ ] Belum dikerjakan.
- [~] Sedang dikerjakan.
- [!] Perlu pemeriksaan ulang atau ada kendala.

---

## Tahap 0 — Spesifikasi dan desain data

- [x] Menetapkan cakupan dan prinsip kamus.
- [x] Menetapkan skema entri, kelas kata, ragam bahasa, dan metadata.
- [x] Menetapkan aturan ID, deduplikasi, validasi, dan struktur data.
- [x] Menyiapkan dokumentasi kamus dan format batch.

## Tahap 1 — Kamus 3.000 entri

- [x] Mengumpulkan 3.000 lema dalam 60 batch.
- [x] Melengkapi definisi seluruh entri.
- [x] Menyusun INDEX dan token shards.
- [x] Menyelesaikan pemeriksaan serta penyempurnaan metadata batch 006–060.
- [x] Menjaga data inti kamus selama penyempurnaan metadata.
- [x] Mendokumentasikan skema dan aturan kamus.

## Tahap 2 — Pengolahan kata dan tata bahasa dasar

### 2.1 Normalisasi teks

- [x] Membuat modul `tools/normalisasi.py`.
- [x] Membuat 8 regression tests di `tests/test_normalisasi.py`.
- [x] Menjalankan seluruh tes normalisasi pada lingkungan Python lokal terisolasi.
- [x] Memeriksa hasil: 8 tes lulus, 0 gagal; tidak ditemukan masalah.
- [x] Menetapkan normalisasi sebagai baseline awal yang tervalidasi.

### 2.2 Tokenisasi

- [x] Membuat `tools/tokenizer.py`.
- [x] Memisahkan kata dan tanda baca menjadi token.
- [x] Mempertahankan tanda baca sebagai token tersendiri.
- [x] Menentukan dan menguji perilaku kata bertanda hubung dan apostrof.
- [x] Membuat 12 regression tests tokenizer; seluruhnya lulus.

### 2.3 Pencocokan token ke kamus

- [x] Memeriksa format JSONL batch kamus aktual pada sampel Batch 001 dan Batch 006.
- [x] Membuat loader kamus baca-saja di `tools/kamus_loader.py`.
- [x] Membuat pencocokan token terhadap lema, variants, dan derived_forms di `tools/pencocokan_kamus.py`.
- [x] Membedakan hasil lema, variasi, bentuk turunan, dan token tak dikenal.
- [x] Mempertahankan seluruh kandidat, POS, dan sense tanpa memilih makna secara otomatis.
- [x] Membuat 13 regression tests pencocokan leksikal; seluruhnya lulus.
- [x] Memeriksa struktur dasar seluruh 60 batch (3.000 entri): JSON, field wajib, ID, lema, dan sense.
- [ ] Menjalankan `python -m tools.validasi_kamus_lengkap` pada checkout repository untuk memuat 60 batch (3.000 entri) melalui loader Python; skrip validasi sudah tersedia.
- [x] Mengintegrasikan normalisasi, tokenizer, dan pencocokan kamus dalam `tools/analisis_teks.py`.
- [x] Membuat 8 regression tests analyzer; seluruhnya lulus pada lingkungan Python lokal terisolasi.

### 2.4 Analisis morfologi

- [x] Membuat prototipe awal `tools/morfologi.py` dengan pendekatan kandidat yang harus divalidasi kamus.
- [x] Membuat prototipe dan menjalankan 12 regression tests morfologi awal; 12 lulus, 0 gagal.
- [x] Memperbaiki urutan percobaan prefiks dan menghapus aturan prefiks duplikat yang tidak tepat.
- [x] Menambahkan kandidat konfiks ke-an, per-an, dan peN-an dengan validasi terhadap lema kamus.
- [x] Menambahkan kandidat bentuk menge- untuk pola seperti mengecat; cakupan tetap terbatas.
- [x] Menjalankan 18 regression tests morfologi versi terbaru pada lingkungan Python lokal terisolasi; 18 lulus, 0 gagal.
- [ ] Memperluas inventaris imbuhan, reduplikasi, dan perubahan morfofonemik berdasarkan pengujian.
- [x] Mempertahankan validasi kamus untuk setiap kandidat lema dan tidak melakukan stemming pada kecocokan persis.

### 2.5 Pengenalan kelas kata (POS)

- [ ] Menggunakan kode POS resmi dari dokumentasi kamus.
- [ ] Menangani kata yang memiliki lebih dari satu kemungkinan POS.
- [ ] Menambahkan petunjuk konteks kalimat.
- [ ] Membuat data berlabel dan regression tests POS.

### 2.6 Analisis struktur kalimat dasar

- [ ] Menentukan masukan parser dari token dan hasil POS.
- [ ] Mengenali subjek, predikat, objek, pelengkap, dan keterangan.
- [ ] Menguji variasi susunan kalimat sederhana.
- [ ] Mencatat kasus ambigu atau belum teranalisis.
- [ ] Membuat regression tests parser.

### 2.7 Dataset dan pengujian terpadu

- [ ] Menyusun kalimat uji representatif.
- [ ] Mencakup bahasa baku, informal, slang, salah ketik, imbuhan, dan kata ulang.
- [ ] Menyimpan hasil yang diharapkan (expected output).
- [ ] Menjalankan regression suite untuk seluruh komponen.

## Tahap 3 — Hubungan makna dan pemrosesan konteks

- [ ] Memperluas jaringan relasi kata dan konsep.
- [ ] Menggabungkan analisis leksikal dan struktur kalimat.
- [ ] Mengembangkan penafsiran maksud dan ambiguitas.
- [ ] Mengelola konteks percakapan beberapa giliran.
- [ ] Membuat mekanisme klarifikasi.

## Tahap 4 — Evaluasi kebutuhan embedding (opsional)

- [ ] Mengukur kemampuan prototipe tanpa embedding pada kasus nyata.
- [ ] Mengidentifikasi kekurangan yang terukur.
- [ ] Menyiapkan kasus uji pembanding.
- [ ] Mengevaluasi manfaat dibanding biaya sumber daya.
- [ ] Mengambil keputusan berbasis hasil: gunakan atau tidak gunakan embedding.

## Tahap 5 — Integrasi Android offline

- [ ] Menentukan rancangan aplikasi Android.
- [ ] Mengintegrasikan komponen bahasa dan penyimpanan lokal.
- [ ] Memastikan pemrosesan inti berjalan di perangkat.
- [ ] Menguji skenario inti dalam mode pesawat.
- [ ] Menguji instalasi, pemulihan data, dan penanganan kesalahan.

## Tahap 6 — Optimasi dan perluasan

- [ ] Mengukur RAM, CPU, baterai, latensi, dan ukuran penyimpanan.
- [ ] Mengoptimalkan performa berdasarkan hasil pengukuran.
- [ ] Memperluas kosakata dan relasi secara terkontrol.
- [ ] Menguji salah ketik, bahasa informal, ambiguitas, dan percakapan panjang.
- [ ] Menyelesaikan dokumentasi dan persiapan rilis.

## Pengembangan terpisah — Adaptive Lexicon

*Dimulai setelah sistem inti selesai dan diuji.*

- [ ] Mendeteksi kata yang belum dikenal.
- [ ] Mengumpulkan contoh penggunaan secara lokal.
- [ ] Menganalisis kandidat kelas kata dan makna.
- [ ] Memeriksa duplikasi, variasi, dan bentuk turunan.
- [ ] Menyediakan validasi bertahap untuk kandidat.
- [ ] Mempromosikan hanya entri yang lolos validasi.
- [ ] Menyediakan jejak perubahan dan mekanisme koreksi/pembatalan.

---

## Titik lanjut aktif

**Tahap 2.3 — Validasi loader seluruh kamus masih terbuka; Tahap 2.4 — perluasan morfologi sedang berjalan dan tes versi terbaru menunggu eksekusi.**

Normalisasi, tokenizer, loader, pencocokan kamus, analyzer teks, dan prototipe morfologi telah melewati total 65 tes komponen yang dijalankan terpisah pada lingkungan Python lokal terisolasi: 65 lulus, 0 gagal (45 fondasi + 8 analyzer + 12 morfologi). Struktur dasar 60 batch (3.000 entri) telah diperiksa melalui konten GitHub, tetapi eksekusi langsung loader Python terhadap seluruh 60 file aktual masih belum dilakukan. Prototipe morfologi hanya menghasilkan kandidat yang cocok dengan kamus; cakupan aturan belum lengkap. GitHub Actions tidak dijalankan.

## Dokumen rujukan

- [README proyek](../README.md)
- [Status teknis tahap pengolahan bahasa](STATUS_TAHAP_PENGOLAHAN_BAHASA.md)
- [Dokumentasi kamus](KAMUS.md)

**Aturan pembaruan:** jangan mencentang pekerjaan hanya karena file sudah dibuat. Centang setelah isi dan hasilnya diperiksa; untuk pengujian, centang hanya setelah tes benar-benar dijalankan.
