# Checklist Pengembangan — Sistem Bahasa

Dokumen ini adalah **peta tahapan dan status pekerjaan proyek**. Checklist menunjukkan urutan kerja, prasyarat, dan titik lanjut. Rincian teknis, riwayat versi, eksperimen, serta log pengujian disimpan di `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.

## Arti status

- [x] Selesai dan sudah diverifikasi.
- [~] Sedang dikerjakan atau sebagian fondasinya sudah tersedia.
- [ ] Belum dikerjakan.
- [!] Terhambat atau perlu keputusan.

## Snapshot proyek — 27 November 2026

- **Tahap aktif: 2.6 — Analisis struktur kalimat dasar.**
- Parser saat ini **v1.9**. Ini nomor versi parser, bukan tanda bahwa seluruh Tahap 2.6 sudah selesai.
- Kamus: **3.014 lema dalam 60 batch**; tidak ada rencana audit ulang batch secara rutin.
- Tahap 2.5 (POS) telah ditutup berdasarkan keputusan pengguna.
- Dataset POS: 100 kalimat / 543 token (60 development, 40 test); test split tetap tersegel.
- Evaluasi POS kontekstual pada development: 250/255 dikenali; coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%. Lima abstention berupa nama orang ditunda ke tahap pengenalan nama/konteks.
- GitHub Actions [Run #126](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45972629322) sukses: validasi kamus, dataset POS, evaluasi development, dan **255/255 regression tests lulus**.

## Aturan kerja yang harus dijaga

- Penambahan lema baru ke kamus harus mendapat **persetujuan eksplisit pengguna** sebelum batch sumber maupun indeks diubah.
- Untuk memeriksa apakah lema sudah tersedia, periksa indeks kamus terlebih dahulu. Jangan melakukan audit ulang seluruh batch tanpa alasan yang jelas.
- Parser dan komponen bahasa harus bersikap konservatif: jika bukti belum cukup, tandai unresolved/abstain; jangan menebak fungsi kata.
- Setiap perubahan perilaku harus disertai regression test yang relevan dan pemeriksaan kompatibilitas.
- Kelulusan tes membuktikan perilaku yang diuji, bukan bahwa seluruh bahasa Indonesia sudah tercakup.

---

# Peta tahapan utama

## Tahap 0 — Spesifikasi dan desain data

<badge color="success">Selesai</badge>

- [x] Menetapkan tujuan, ruang lingkup, dan prinsip sistem bahasa offline.
- [x] Menetapkan skema entri kamus, kelas kata, sense, ragam bahasa, dan metadata.
- [x] Menetapkan aturan ID, deduplikasi, validasi, dan struktur data.
- [x] Menyiapkan dokumentasi kamus dan format batch.

## Tahap 1 — Fondasi leksikal: kamus dan indeks

<badge color="success">Fondasi selesai</badge>

- [x] Menyusun kamus dasar dan mengembangkannya menjadi **3.014 lema / 60 batch**.
- [x] Melengkapi struktur definisi dan metadata entri sesuai skema proyek.
- [x] Menyusun indeks kamus dan 8 shard indeks.
- [x] Memvalidasi kesesuaian indeks dengan sumber kamus.
- [x] Menyelesaikan audit kualitas isi dan relasi leksikal yang telah direncanakan.
- [x] Menyediakan validator kamus lengkap dan regression tests.
- [ ] Pengembangan anotasi relasi leksikal per-sense secara lebih luas — pekerjaan lanjutan, bukan penghalang untuk melanjutkan parser.

**Catatan:** fondasi kamus selesai untuk cakupan saat ini. Ini bukan klaim bahwa seluruh kosakata atau seluruh definisi bahasa Indonesia sudah lengkap.

## Tahap 2 — Pemrosesan bahasa dasar

Tahap ini membangun alur dari teks mentah sampai struktur kalimat. Subtahap dikerjakan berurutan; parser tidak dianggap selesai hanya karena versinya bertambah.

### 2.1 Normalisasi teks

<badge color="success">Selesai</badge>

- [x] Membuat modul normalisasi.
- [x] Menetapkan dan menguji perilaku normalisasi dasar.
- [x] Menambahkan regression tests.

### 2.2 Tokenisasi

<badge color="success">Selesai</badge>

- [x] Membuat tokenizer.
- [x] Memisahkan kata dan tanda baca menjadi token.
- [x] Menetapkan perilaku kata bertanda hubung dan apostrof.
- [x] Menambahkan regression tests.

### 2.3 Pencocokan token ke kamus

<badge color="success">Selesai</badge>

- [x] Membuat loader kamus baca-saja.
- [x] Mencocokkan token dengan lema, variants, dan derived forms.
- [x] Membedakan kecocokan lema, variasi, bentuk turunan, dan token tak dikenal.
- [x] Mempertahankan kandidat POS dan sense tanpa memilih makna secara otomatis.
- [x] Mengaudit dan memvalidasi indeks kamus.
- [x] Mengintegrasikan normalisasi, tokenisasi, dan pencocokan dalam analyzer.
- [x] Menambahkan regression tests.

### 2.4 Analisis morfologi

<badge color="success">Fondasi implementasi tersedia</badge>

- [x] Membuat modul morfologi berbasis kandidat dan validasi lema kamus.
- [x] Menangani sejumlah pola prefiks, sufiks, konfiks, kombinasi imbuhan, reduplikasi, dan perubahan nasal yang telah diuji.
- [x] Mempertahankan seluruh POS/sense lema ambigu.
- [x] Menambahkan perlindungan dan tes negatif untuk mencegah pemotongan kata yang keliru.
- [ ] Memperluas inventaris imbuhan dan perubahan morfofonemik berdasarkan bukti pengujian.
- [ ] Mengukur cakupan morfologi pada variasi kata yang lebih luas.

**Batas:** morfologi sudah memiliki implementasi dasar, tetapi belum mencakup seluruh pola morfologi bahasa Indonesia.

### 2.5 Pengenalan kelas kata (POS)

<badge color="success">Selesai — ditutup 27 November 2026</badge>

- [x] Membuat POS tagger berbasis kandidat leksikal.
- [x] Menambahkan petunjuk konteks lokal secara konservatif.
- [x] Menyusun dataset berlabel 100 kalimat / 543 token.
- [x] Memisahkan development dan test; test split tetap tersegel.
- [x] Mengevaluasi POS kontekstual pada development: 250/255 dikenali, selective accuracy 100,0%.
- [x] Menetapkan abstention nama orang sebagai pekerjaan tahap pengenalan nama/konteks.
- [x] Menjalankan regression tests dan validasi terpadu.

**Status:** Tahap 2.5 ditutup. Jangan membuka kembali audit POS atau memaksa label untuk kasus yang sengaja di-abstain tanpa bukti masalah baru.

### 2.6 Analisis struktur kalimat dasar

<badge color="info">Tahap aktif</badge>

**Posisi saat ini: parser v1.9.**

- [x] Membuat parser dasar untuk pola S-P, S-P-O, dan keterangan.
- [x] Menambahkan dukungan bertahap untuk frasa nominal, negasi, modal, predikat nonverbal/linking, keterangan awal, koordinasi, dan klausa subordinatif yang telah diuji.
- [x] Memisahkan kepala predikat dari pewatas melalui `predicate_structure`, sambil mempertahankan `roles.predicate` untuk kompatibilitas.
- [x] Mengenali pola modal tertentu secara terbatas berdasarkan POS dan posisi terhadap verba inti.
- [x] Mengenali keterangan temporal awal yang sudah ditetapkan secara eksplisit.
- [x] Memperjelas batas keterangan preposisional awal dan subjek.
- [x] Mempertahankan abstention ketika fungsi sintaksis belum cukup jelas.
- [x] Memvalidasi parser v1.9 melalui GitHub Actions Run #126: **255/255 regression tests lulus**.
- [ ] Melanjutkan perluasan pola kalimat secara bertahap berdasarkan contoh yang terkontrol.
- [~] Menyepakati katalog awal 13 semantic role; menyusun kriteria kerja THEME/PATIENT dan contoh pembeda aktif/pasif, gerak, kemunculan, persepsi, serta perubahan keadaan. Masih perlu uji lintas sense sebelum skema final/validator. Belum ada anotasi atau perubahan data kamus.
- [ ] Menentukan dan menguji pola inversi, termasuk K-P-S, hanya setelah aturan dan bukti linguistiknya jelas.
- [ ] Menguji lebih banyak konstruksi melalui pipeline kamus dan POS nyata.
- [ ] Menetapkan kriteria penutupan Tahap 2.6 berdasarkan cakupan pola, batasan yang terdokumentasi, dan hasil regresi.

**Batas saat ini:** pada contoh `Di rumah terdengar suara.`, parser mengenali `di rumah` sebagai keterangan, tetapi membiarkan subjek kosong dan `suara` unresolved. Inversi K-P-S penuh belum diimplementasikan.

### 2.7 Dataset dan pengujian terpadu

<badge color="secondary">Berikutnya — fondasi sebagian tersedia</badge>

- [x] Memiliki dataset POS 100 kalimat / 543 token dengan development dan test split.
- [x] Memiliki validator dataset dan evaluasi POS development.
- [x] Memiliki regression suite lintas komponen yang dijalankan melalui GitHub Actions.
- [ ] Menyusun dataset khusus untuk menguji alur lengkap normalisasi → tokenisasi → kamus → morfologi → POS → parser.
- [ ] Memperluas variasi kalimat: baku, informal, slang, salah ketik, imbuhan, kata ulang, dan struktur kompleks.
- [ ] Menetapkan expected output untuk hasil parser, termasuk partial dan unresolved.
- [ ] Menjalankan evaluasi terpadu tanpa membuka test split untuk penyetelan.
- [ ] Menetapkan baseline dan kriteria kelulusan Tahap 2 secara keseluruhan.

**Gerbang menuju Tahap 3:** Tahap 2.6 dan 2.7 harus memiliki cakupan serta batas yang terdokumentasi dan lolos evaluasi terpadu. Tidak perlu menunggu parser memahami semua kemungkinan kalimat.

## Tahap 3 — Hubungan makna dan pemrosesan konteks

<badge color="secondary">Belum dimulai</badge>

- [ ] Mengembangkan representasi makna kata dan relasi antarkonsep.
- [ ] Menentukan cara memilih sense berdasarkan konteks kalimat.
- [ ] Menggabungkan hasil leksikal, morfologi, POS, dan struktur kalimat.
- [ ] Menangani ambiguitas dan maksud ujaran secara bertahap.
- [ ] Mengelola konteks percakapan beberapa giliran.
- [ ] Menangani nama orang/nama khusus yang sebelumnya di-abstain.
- [ ] Menyediakan mekanisme klarifikasi jika makna atau maksud belum cukup jelas.
- [ ] Menguji kemampuan pemahaman konteks dengan dataset tersendiri.

## Tahap 4 — Mesin aturan dan pembentukan respons

<badge color="secondary">Belum dimulai</badge>

- [ ] Merancang representasi keadaan/dialog dan aturan respons.
- [ ] Menghubungkan hasil pemahaman bahasa dengan pemilihan tindakan atau respons.
- [ ] Membentuk respons yang sesuai konteks menggunakan aturan dan komponen bahasa yang tersedia.
- [ ] Menangani respons ketika informasi tidak cukup, termasuk meminta klarifikasi.
- [ ] Menguji konsistensi, relevansi, dan batas kemampuan respons.

**Catatan:** tahap ini adalah mesin aturan dan pembentukan respons, bukan pelatihan atau pemasangan model LLM/GGUF.

## Tahap 5 — Integrasi Android offline

<badge color="secondary">Belum dimulai</badge>

- [ ] Menentukan arsitektur aplikasi dan antarmuka Android.
- [ ] Mengintegrasikan mesin bahasa dan penyimpanan lokal.
- [ ] Memastikan pemrosesan inti dapat berjalan tanpa koneksi internet.
- [ ] Menguji skenario inti dalam mode pesawat.
- [ ] Menguji instalasi, pemulihan data, dan penanganan kesalahan.

## Tahap 6 — Evaluasi perangkat dan optimasi

<badge color="secondary">Belum dimulai</badge>

- [ ] Mengukur RAM, CPU, baterai, latensi, dan ukuran penyimpanan.
- [ ] Mengidentifikasi bottleneck berdasarkan pengukuran nyata.
- [ ] Mengoptimalkan komponen tanpa merusak hasil regresi.
- [ ] Menguji kestabilan pada perangkat Android sasaran.
- [ ] Menetapkan batas kemampuan dan kebutuhan pengembangan lanjutan.

---

## Keputusan teknis opsional — embedding

Embedding **bukan tahap wajib dan bukan prasyarat** untuk menyelesaikan tahapan utama.

- [ ] Mengukur kekurangan sistem berbasis aturan dan relasi pada kasus nyata.
- [ ] Menyusun kasus uji pembanding.
- [ ] Mengukur manfaat embedding dibanding biaya RAM, penyimpanan, latensi, dan kompleksitas.
- [ ] Memutuskan berdasarkan hasil apakah embedding diperlukan.

## Titik lanjut resmi

Pekerjaan dilanjutkan dari **Tahap 2.6 — parser v1.9**. Tahap 2.5 tetap ditutup. Setelah cakupan parser cukup stabil, lanjutkan ke Tahap 2.7 untuk evaluasi pipeline terpadu; setelah gerbang Tahap 2 terpenuhi, barulah masuk ke Tahap 3.
