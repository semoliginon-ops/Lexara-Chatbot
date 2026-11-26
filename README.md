# Sistem Bahasa — Chatbot Lokal Offline Tanpa LLM

> **Status:** Perencanaan awal  
> **Target utama:** chatbot berbahasa alami yang berjalan langsung di HP Android, tanpa layanan cloud, tanpa API berbayar, dan tanpa LLM.

## 1. Gambaran proyek

**Sistem Bahasa** adalah proyek baru untuk membangun chatbot lokal berbasis kamus, aturan percakapan, pengelolaan konteks, dan pencarian kemiripan makna (*semantic search*).

Sistem ini **tidak menggunakan LLM**. Komponen embedding hanya membantu mengubah teks menjadi representasi numerik dan mencari kalimat atau pengetahuan yang paling mirip secara semantik. Embedding **tidak menulis jawaban baru dengan sendirinya**.

Jawaban chatbot dipilih dan dirangkai oleh mesin aturan, basis pengetahuan, serta template respons yang dibuat dalam proyek.

## 2. Prinsip dan batasan

- **On-device:** pemrosesan percakapan dilakukan di perangkat Android.
- **Offline-first:** setelah aplikasi, kamus, indeks, dan model lokal tersedia di HP, percakapan dasar tidak memerlukan internet.
- **Tanpa LLM:** tidak ada model bahasa generatif besar maupun pemanggilan LLM eksternal.
- **Tanpa cloud/API:** tidak mengirim pesan pengguna ke server untuk diproses.
- **Tanpa biaya layanan berjalan:** tidak memerlukan biaya server atau biaya token/API. Pengunduhan awal dan akses internet untuk memperoleh berkas tetap dapat memakai kuota pengguna.
- **Ringan:** dirancang agar dapat berjalan pada HP Android dengan RAM sekitar 6 GB; penggunaan RAM, CPU, baterai, dan penyimpanan akan diukur lewat pengujian nyata.
- **Privasi lokal:** riwayat dan data percakapan disimpan di perangkat sesuai pengaturan aplikasi.

Target ukuran embedding sekitar **80 MB** adalah sasaran awal, bukan ukuran yang sudah dipastikan. Ukuran akhir bergantung pada model, tokenizer, format runtime, dan kuantisasi yang dipilih.

## 3. Arsitektur sistem

```text
Pesan pengguna
      |
      v
Normalisasi teks
      |
      v
Pengenalan maksud + konteks percakapan
      |
      v
Pencarian kandidat
  |                 |
  v                 v
Kamus / aturan    Embedding lokal
  |                 |
  |           Pencarian semantik
  |                 |
  +--------+--------+
           |
           v
Pemeringkatan kandidat + pemeriksaan aturan
           |
           v
Pemilih / perangkai respons berbasis template
           |
           v
Jawaban chatbot
           |
           v
Pembaruan konteks dan memori lokal
```

### Komponen utama

1. **Kamus dan basis pengetahuan**
   - Kata, frasa, sinonim, variasi ejaan, dan makna.
   - Contoh kalimat dan kelompok maksud (*intent*).
   - Fakta atau pengetahuan yang boleh digunakan chatbot.
   - Respons dan template yang telah disiapkan.

2. **Text normalizer**
   - Menangani huruf besar-kecil, tanda baca, spasi, dan variasi penulisan.
   - Menangani bentuk percakapan sehari-hari secara bertahap tanpa menghapus makna penting.

3. **Rule Engine**
   - Aturan untuk salam, perkenalan, pertanyaan, perintah, penolakan, dan alur percakapan.
   - Mengelola prioritas aturan, kondisi, dan respons cadangan.
   - Mencegah hasil pencarian semantik dipakai jika bertentangan dengan aturan atau konteks.

4. **Embedding dan semantic search lokal**
   - Mengubah kalimat menjadi vektor.
   - Membandingkan kemiripan makna, bukan hanya kecocokan kata persis.
   - Mengambil beberapa kandidat terbaik dari contoh kalimat atau basis pengetahuan.
   - Memiliki ambang skor agar sistem dapat mengakui ketika tidak menemukan kecocokan yang cukup baik.

5. **Context dan conversation state**
   - Menyimpan konteks percakapan yang diperlukan, misalnya topik yang sedang dibahas dan referensi seperti “itu” atau “dia”.
   - Mengatur masa berlaku dan batas memori agar konteks lama tidak terus mengganggu percakapan baru.

6. **Response Engine**
   - Memilih respons berdasarkan maksud, konteks, hasil pencarian, dan aturan.
   - Menggunakan template serta variasi respons yang telah disediakan.
   - Tidak mengklaim dapat menghasilkan kalimat bebas seperti LLM.

7. **Penyimpanan lokal**
   - Menyimpan kamus, konfigurasi, indeks pencarian, dan preferensi.
   - Menyimpan riwayat percakapan secara lokal jika fitur tersebut diaktifkan.

## 4. Alur pemrosesan satu pesan

1. Pengguna mengirim pesan.
2. Teks dinormalisasi.
3. Sistem memeriksa aturan dan konteks percakapan.
4. Sistem mencari kecocokan langsung pada kamus dan basis pengetahuan.
5. Jika diperlukan, embedding lokal mencari kandidat dengan makna paling dekat.
6. Kandidat diberi skor dan diperiksa terhadap konteks serta aturan.
7. Response Engine memilih atau merangkai jawaban dari template yang tersedia.
8. Jika keyakinan rendah, chatbot bertanya klarifikasi atau memberi tahu bahwa ia belum memahami.
9. Konteks percakapan diperbarui dan jawaban ditampilkan.

## 5. Rencana pengembangan bertahap

### Tahap 0 — Fondasi dan spesifikasi
- [ ] Menetapkan tujuan, batasan, dan contoh percakapan.
- [ ] Menentukan struktur folder dan format data kamus.
- [ ] Menetapkan bahasa utama awal: Bahasa Indonesia.
- [ ] Menentukan cara menguji kualitas jawaban dan penggunaan sumber daya.

**Hasil tahap:** spesifikasi proyek dan struktur data awal.

### Tahap 1 — Kamus dan pencocokan dasar
- [ ] Membuat format entri kata, frasa, sinonim, maksud, dan respons.
- [ ] Membuat text normalizer.
- [ ] Membuat pencarian kata/frasa dan pencocokan aturan.
- [ ] Membuat respons fallback saat tidak ditemukan kecocokan.
- [ ] Menyiapkan kumpulan contoh percakapan untuk pengujian.

**Kriteria selesai:** variasi sederhana seperti “halo”, “hai”, dan “selamat pagi” dapat diarahkan ke fungsi salam yang tepat melalui data dan aturan.

### Tahap 2 — Rule Engine dan konteks
- [ ] Membuat sistem intent dan prioritas aturan.
- [ ] Membuat state percakapan.
- [ ] Menangani konteks sederhana lintas beberapa giliran.
- [ ] Menambahkan klarifikasi ketika maksud belum jelas.
- [ ] Membuat pengujian untuk konflik aturan dan konteks.

**Kriteria selesai:** sistem dapat mengikuti alur percakapan sederhana tanpa hanya bergantung pada kata persis.

### Tahap 3 — Semantic search dengan embedding lokal
- [ ] Mengevaluasi model embedding multibahasa yang cocok untuk Bahasa Indonesia.
- [ ] Memeriksa lisensi model dan izin distribusinya.
- [ ] Menguji tokenizer, format model, dan runtime Android.
- [ ] Mengubah data contoh menjadi embedding dan membuat indeks pencarian.
- [ ] Mengukur kualitas pencarian, latensi, RAM, ukuran berkas, dan baterai.
- [ ] Menentukan ambang skor serta perilaku ketika skor rendah.

**Kriteria selesai:** kalimat berbeda yang memiliki maksud serupa dapat menemukan kandidat yang relevan, dan sistem tidak memaksakan jawaban jika skor tidak meyakinkan.

### Tahap 4 — Integrasi Android offline
- [ ] Membuat antarmuka chat Android.
- [ ] Mengintegrasikan kamus, Rule Engine, penyimpanan, dan runtime embedding lokal.
- [ ] Memastikan seluruh inferensi dan pencarian berlangsung di perangkat.
- [ ] Memastikan aplikasi tetap dapat digunakan dalam mode pesawat setelah aset tersedia.
- [ ] Menguji instalasi, pemulihan data, dan penanganan kesalahan.

**Kriteria selesai:** percakapan uji berjalan tanpa koneksi internet dan tanpa permintaan jaringan untuk pemrosesan pesan.

### Tahap 5 — Optimasi dan perluasan
- [ ] Mengoptimalkan indeks dan pencarian.
- [ ] Menguji kuantisasi atau model yang lebih kecil jika diperlukan.
- [ ] Memperluas kamus, contoh, dan variasi respons secara terukur.
- [ ] Menguji percakapan panjang, salah ketik, bahasa informal, dan pertanyaan ambigu.
- [ ] Membuat dokumentasi, versi rilis, dan prosedur backup.

**Kriteria selesai:** performa dan kualitas memenuhi target perangkat yang ditentukan berdasarkan hasil pengujian, bukan perkiraan.

## 6. Strategi pengujian

Setiap perubahan harus diuji dengan kumpulan kalimat yang mencakup:

- Salam dan perkenalan dengan variasi kata.
- Pertanyaan dengan maksud sama tetapi susunan berbeda.
- Salah ketik dan bahasa percakapan.
- Percakapan beberapa giliran yang membutuhkan konteks.
- Kalimat ambigu atau di luar pengetahuan.
- Kalimat yang mirip secara kata tetapi berbeda maksud.

Metrik yang dicatat:

- Ketepatan intent dan relevansi kandidat.
- Tingkat jawaban keliru dan fallback yang tepat.
- Latensi respons.
- Penggunaan RAM, CPU, baterai, dan penyimpanan.
- Keberhasilan berjalan tanpa jaringan.

## 7. Teknologi yang akan dievaluasi

Pilihan teknis belum dikunci sebelum prototipe dan pengukuran:

- **Android:** Kotlin/Android sebagai kandidat aplikasi utama.
- **Runtime embedding:** ONNX Runtime Mobile atau TensorFlow Lite, dipilih setelah format model dan dukungan perangkat diperiksa.
- **Penyimpanan:** format lokal sederhana untuk kamus dan metadata; SQLite dapat dievaluasi untuk data terstruktur.
- **Semantic index:** mulai dari pencarian vektor sederhana; optimasi dilakukan jika jumlah data sudah membutuhkannya.

Pemilihan model harus mempertimbangkan dukungan Bahasa Indonesia, lisensi, ukuran, kualitas, kompatibilitas Android, dan kebutuhan RAM. Angka 80 MB bukan janji sebelum pengujian.

## 8. Peran GitHub

GitHub digunakan untuk:
- Menyimpan source code, dokumentasi, skema data, dan pengujian.
- Mencatat perubahan melalui commit dan riwayat versi.
- Mengelola issue serta daftar pekerjaan.
- Menyimpan konfigurasi build yang diperlukan.

GitHub **bukan tempat menjalankan chatbot**. Aplikasi berjalan di HP. GitHub Actions bersifat opsional; proyek tidak boleh bergantung pada kuota Actions atau layanan cloud berbayar untuk menjalankan fitur chatbot.

Jangan memasukkan token, password, data pribadi, atau riwayat percakapan pengguna ke repository. Model dan dataset berukuran besar hanya disimpan di repository jika ukuran, lisensi, dan kebijakan GitHub mengizinkan; alternatif distribusinya akan diputuskan kemudian.

## 9. Hal yang tidak menjadi target

- Tidak membuat atau memasang LLM/GGUF.
- Tidak menggunakan API ChatGPT atau API AI berbayar.
- Tidak mengirim pesan ke cloud untuk mendapatkan jawaban.
- Tidak menjanjikan kemampuan bahasa setara ChatGPT.
- Tidak menganggap embedding sebagai mesin pembuat kalimat.

## 10. Definisi keberhasilan proyek

Proyek dianggap mencapai target utama ketika aplikasi Android dapat:

1. Memahami sejumlah variasi kalimat Bahasa Indonesia melalui aturan dan pencarian semantik.
2. Menggunakan konteks percakapan sederhana secara konsisten.
3. Memberikan jawaban relevan dari pengetahuan dan template lokal.
4. Meminta klarifikasi atau mengakui keterbatasan saat tidak yakin.
5. Berjalan tanpa internet setelah seluruh aset tersedia di perangkat.
6. Tidak memerlukan LLM, cloud, API, atau biaya layanan berjalan.

---

**Catatan:** dokumen ini adalah rencana awal. Ukuran model, runtime, target performa, dan jadwal pengerjaan akan ditetapkan setelah prototipe diuji pada perangkat Android sasaran.
