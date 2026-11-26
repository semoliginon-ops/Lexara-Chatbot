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

- [ ] Memeriksa format JSONL batch kamus aktual.
- [ ] Membuat loader kamus.
- [ ] Membuat pencocokan token terhadap lema dan indeks.
- [ ] Membedakan lema, variasi, bentuk turunan, dan kata tak dikenal.
- [ ] Menangani kata dengan beberapa POS atau sense.
- [ ] Membuat regression tests pencocokan leksikal.

### 2.4 Analisis morfologi

- [ ] Menyusun aturan imbuhan Bahasa Indonesia.
- [ ] Menangani prefiks, sufiks, konfiks, dan reduplikasi.
- [ ] Menggunakan kamus untuk memeriksa kandidat lema.
- [ ] Menghindari pemotongan kata yang bukan bentuk berimbuhan.
- [ ] Membuat regression tests morfologi.

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

**Tahap 2.3 — Pencocokan token ke kamus.**

Normalisasi: 8 tes lulus. Tokenizer: 12 tes lulus. Seluruh 20 tes dari kedua komponen lulus pada lingkungan Python lokal terisolasi menggunakan salinan file yang dibaca dari GitHub. GitHub Actions tidak dijalankan. Berikutnya periksa format JSONL batch kamus aktual sebelum merancang loader dan pencocokan leksikal.

## Dokumen rujukan

- [README proyek](../README.md)
- [Status teknis tahap pengolahan bahasa](STATUS_TAHAP_PENGOLAHAN_BAHASA.md)
- [Dokumentasi kamus](KAMUS.md)

**Aturan pembaruan:** jangan mencentang pekerjaan hanya karena file sudah dibuat. Centang setelah isi dan hasilnya diperiksa; untuk pengujian, centang hanya setelah tes benar-benar dijalankan.
