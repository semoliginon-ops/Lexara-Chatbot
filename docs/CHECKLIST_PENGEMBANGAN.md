# Checklist Pengembangan — Sistem Bahasa

Dokumen ini adalah pusat pelacakan pekerjaan proyek. Perbarui checklist hanya setelah pekerjaan benar-benar selesai dan diverifikasi.

## Arti status

- [x] Selesai dan sudah diverifikasi.
- [ ] Belum dikerjakan.
- [~] Sedang dikerjakan.
- [!] Perlu pemeriksaan ulang atau ada kendala.

## Snapshot status terkini — 27 November 2026

- Tahap 2.5 (POS) **selesai** berdasarkan keputusan pengguna.
- Kamus: **3.013 lema / 60 batch**; tidak ada audit ulang batch yang direncanakan.
- Dataset POS: 100 kalimat / 543 token (60 development, 40 test).
- Evaluasi POS kontekstual development: 250/255 dikenali; coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%; lima abstention nama orang ditunda ke tahap konteks.
- Test split tetap tersegel.
- GitHub Actions [Run #116](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45966546324): validasi kamus dan dataset berhasil, **246/246 regression tests lulus**.
- Parser kini berada pada v1.6; pembekuan parser dicabut setelah POS selesai. Fokus berikutnya adalah Tahap 2.6, bukan mengulang audit atau mengulang Tahap 2.5.

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
- [x] Menyelesaikan pemeriksaan serta penyempurnaan metadata dan relasi batch 001–060.
- [x] Menjaga data inti kamus selama penyempurnaan metadata.
- [x] Mendokumentasikan skema dan aturan kamus.

### Rancangan relasi leksikal per-sense

- [x] Membuat dokumen rancangan kompatibilitas relasi per-sense di `docs/RELASI_LEKSIKAL_PER_SENSE.md`; belum mengubah data kamus atau kode.
- [ ] Meninjau dan menetapkan rancangan field relasi opsional pada setiap sense.
- [x] Menambahkan modul validator struktur relasi per-sense dan 12 regression tests; verifikasi Termux: 12/12 tes khusus lulus, seluruh 60 batch (3.000 entri) lolos validasi struktur relasi secara bertahap, dan regression suite penuh 169/169 lulus pada 27 November 2026.
- [ ] Menguji kompatibilitas dengan seluruh bentuk data lama tanpa migrasi batch.
- [ ] Menentukan kebutuhan pembaca relasi per-sense pada komponen mesin makna sebelum implementasi runtime.
- [ ] Menerapkan anotasi per-sense hanya pada entri yang sudah diaudit dan memiliki bukti linguistik.

### Audit kualitas isi kamus — selesai, 60 batch

- [x] Audit seluruh `batch-001.jsonl` sampai `batch-060.jsonl` secara bertahap dalam 12 kelompok, masing-masing lima batch.
- [x] Pisahkan pemeriksaan baca-saja dari perbaikan; perubahan hanya dilakukan setelah kesalahan atau ketidakcocokan cukup jelas.
- [x] Tinjau temuan berdasarkan bukti dan dampak; pertahankan kandidat yang ambigu atau masih dapat dipertanggungjawabkan.
- [x] Jalankan validasi relasi leksikal dan regression tests melalui GitHub Actions untuk setiap kelompok lima batch.
- [x] Catat hasil audit dan koreksi per kelompok pada bagian laporan di bawah checklist ini.

#### Ringkasan audit makna dan relasi leksikal

- [x] Batch-001: audit selesai; empat penataan relasi/sense dicatat dan diperbaiki secara selektif. Perubahan data pada commit `b2b37d2`.
- [x] Batch-002: audit selesai; tujuh sinonim yang tidak setara atau merupakan bentuk turunan/perintah dihapus. Kandidat lain yang memerlukan konteks dipertahankan tanpa perubahan spekulatif.
- [x] Batch-003: audit selesai; empat relasi salah kategori/POS ditata ulang sebagai `related_terms` atau dihapus dari sinonim/antonim.
- [x] Batch-004: audit selesai; empat koreksi pada antonim, pemisahan sense, dan sinonim dilakukan.
- [x] Batch-005: audit selesai; delapan bentuk turunan/gramatikal dihapus dari daftar sinonim.
- [x] Batch-006–010: audit 250 entri; empat koreksi relasi dan pemisahan sense dilakukan.
- [x] Batch-011–015: audit 250 entri; sembilan koreksi relasi dilakukan.
- [x] Batch-016–020: audit 250 entri; enam koreksi/penataan relasi dan sense dilakukan.
- [x] Batch-021–025: audit 250 entri; enam koreksi relasi dilakukan.
- [x] Batch-026–030: audit 250 entri; delapan koreksi relasi dilakukan.
- [x] Batch-031–035: audit 250 entri; tujuh koreksi relasi dilakukan.
- [x] Batch-036–040: audit 250 entri; tiga koreksi relasi dilakukan.
- [x] Batch-041–045: audit 250 entri; tidak ditemukan relasi sinonim/antonim yang dapat dikoreksi; kekosongan anotasi dicatat sebagai coverage gap.
- [x] Batch-046–050: audit 250 entri; seluruh entri memiliki `related_terms`, tetapi tidak memiliki anotasi sinonim/antonim; tidak dibuat relasi tebakan.
- [x] Batch-051–055: audit 250 entri; satu typo `kabina` pada K2561 `pikap` diperbaiki menjadi `kabin`.
- [x] Batch-056–060: audit 250 entri; sepuluh koreksi geografis dan kategori administratif dilakukan pada Batch-056–057; Batch-058–060 dipertahankan.

**Hasil keseluruhan:** 60/60 batch dan 3.000 entri telah tercakup dalam audit bertahap. Validasi otomatis kelompok terakhir, GitHub Actions Run #73, selesai dengan status **SUCCESS** pada 27 November 2026.

**Batas audit:** audit ini berfokus pada isi dan relasi yang diperiksa dalam tiap kelompok, terutama kecocokan sinonim, antonim, related terms, serta koreksi faktual yang jelas. Kelulusan validator otomatis membuktikan struktur dan regression checks sesuai kontrak pengujian; bukan jaminan bahwa setiap definisi atau seluruh pengetahuan kamus telah sempurna secara linguistik.

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
- [x] Mengaudit struktur internal seluruh 8 shard index: 3.597 baris, urutan alfabetis, rentang shard, format kolom, ID, dan referensi batch.
- [x] Memperbaiki 5 token yang salah penempatan shard dan memverifikasi ulang seluruh index.
- [x] Mencocokkan seluruh baris index dengan sumber 60 batch JSONL secara streaming; 3.000 lema terindeks, tidak ada lema hilang atau baris index yang tidak cocok.
- [x] Menyelesaikan `tools/audit_index_kamus.py` dan regression tests; audit sumber 60 batch selesai tanpa kesalahan struktur atau ketidakcocokan index.
- [x] Mempertahankan seluruh kandidat, POS, dan sense tanpa memilih makna secara otomatis.
- [x] Membuat 13 regression tests pencocokan leksikal; seluruhnya lulus.
- [x] Memeriksa struktur dasar seluruh 60 batch (3.000 entri): JSON, field wajib, ID, lema, dan sense.
- [x] Menjalankan `python -m tools.validasi_kamus_lengkap` pada checkout repository melalui Termux; hasil aktual: 60 batch dan 3.000 entri berhasil dimuat dan seluruh pemeriksaan lulus.
- [x] Mengintegrasikan normalisasi, tokenizer, dan pencocokan kamus dalam `tools/analisis_teks.py`.
- [x] Membuat 8 regression tests analyzer; seluruhnya lulus pada lingkungan Python lokal terisolasi.

### 2.4 Analisis morfologi

- [x] Membuat prototipe awal `tools/morfologi.py` dengan pendekatan kandidat yang harus divalidasi kamus.
- [x] Membuat prototipe dan menjalankan 12 regression tests morfologi awal; 12 lulus, 0 gagal.
- [x] Memperbaiki urutan percobaan prefiks dan menghapus aturan prefiks duplikat yang tidak tepat.
- [x] Menambahkan kandidat konfiks ke-an, per-an, dan peN-an dengan validasi terhadap lema kamus.
- [x] Menambahkan kandidat bentuk menge- untuk pola seperti mengecat; cakupan tetap terbatas.
- [x] Menjalankan 20 regression tests morfologi versi terbaru pada lingkungan Python lokal terisolasi; 20 lulus, 0 gagal.
- [x] Menambahkan perlindungan untuk bentuk leksikal beranda, kemari, kemarin, terima, terus, perlu, dan pernah agar tidak dipotong sebagai prefiks secara keliru.
- [x] Menambahkan tes negatif untuk memastikan beranda dan kemari tidak salah dianalisis sebagai bentuk berimbuhan.
- [x] Menambahkan perlindungan tambahan untuk kata leksikal terong, selalu, melati, kelapa, dan perang.
- [x] Menjalankan 25 regression tests setelah penambahan lima kasus negatif baru; 25 lulus, 0 gagal.
- [x] Menambahkan tes untuk mencegah prefiks pendek `pen-` menghasilkan kandidat palsu ketika bentuk yang lebih panjang `penge-` cocok.
- [x] Mengubah pencocokan prefiks agar hanya memakai prefiks terpanjang yang cocok pada satu jalur analisis.
- [x] Menjalankan 29 regression tests morfologi pada lingkungan Python lokal terisolasi; 29 lulus, 0 gagal. Implementasi pencocokan leksikal repository digunakan dalam pengujian.
- [x] Memastikan analisis bentuk berimbuhan mempertahankan seluruh POS dan sense dari lema ambigu; tidak memilih satu makna secara otomatis.
- [x] Menambahkan aturan prefiks `memper-` agar bentuk seperti `memperindah` dapat menghasilkan kandidat lema `indah`.
- [x] Mengganti tes negatif yang keliru: `memperindah` bukan bentuk tak dikenal; memakai `memperxyz` untuk memastikan bentuk tanpa lema tetap ditolak.
- [x] Menjalankan 30 regression tests morfologi pada lingkungan Python lokal terisolasi; 30 lulus, 0 gagal.
- [x] Menambahkan dua kasus regresi kombinasi prefiks `memper-` dengan sufiks `-i` dan `-kan` (`memperbaiki`, `mempermainkan`).
- [x] Menjalankan ulang seluruh 32 regression tests setelah penambahan dua kasus tersebut; 32 lulus, 0 gagal pada lingkungan Python lokal terisolasi.
- [x] Tambahkan aturan imbuhan bertingkat `di- + per- + -i` dan regression test `diperbaiki`; 33/33 tes morfologi lulus.
- [x] Batasi aturan imbuhan bertingkat agar hanya menerima sufiks `-i` dan `-kan`, bukan `-an`.
- [x] Jalankan ulang suite morfologi setelah penambahan tes negatif `diperkerjaan`; 34 lulus, 0 gagal.
- [x] Tambahkan analisis konservatif reduplikasi berprefiks `ber-` (berjalan-jalan/berlari-lari) beserta regression tests.
- [ ] Perluas inventaris imbuhan dan perubahan morfofonemik berdasarkan pengujian.
- [x] Audit alomorf `meny-/peny-`: aturan retensi `ny` dan regression tests `menyanyi`/`menyanyikan` telah ditambahkan; suite morfologi terbaru 47/47 lulus pada lingkungan Python terisolasi.
- [x] Mempertahankan validasi kamus untuk setiap kandidat lema dan tidak melakukan stemming pada kecocokan persis.
- [x] Menambahkan perlindungan restorasi nasal `peng-`: jangan membuat kandidat `k+akar` jika sisa setelah prefiks sudah merupakan lema kamus.
- [x] Menambahkan tes positif `pengunci → kunci` dan tes negatif `pengambil → ambil`, bukan `kambil`.
- [x] Menjalankan ulang 40 regression tests morfologi; 40 lulus, 0 gagal pada lingkungan Python lokal terisolasi.
- [x] Memprioritaskan restorasi konsonan `t`/`p` pada prefiks nasal `men-`, `mem-`, `pen-`, dan `pem-` jika bentuk hasil restorasi cocok dengan lema kamus.
- [x] Menerapkan prioritas yang sama pada analisis gabungan prefiks+sufiks.
- [x] Menambahkan tes negatif `menari` dan `menarikan`: pilih `tari`, bukan kandidat kebetulan `ari`.
- [x] Menjalankan ulang suite morfologi terbaru yang berisi 47 regression tests; 47 lulus, 0 gagal pada lingkungan Python lokal terisolasi.

### 2.5 Pengenalan kelas kata (POS)

- [x] Menggunakan kode POS resmi dari `docs/KAMUS.md` (NOUN, VERB, ADJ, ADV, PRON, NUM, PREP, CONJ, INTJ, PART).
- [x] Membuat `tools/pos_tagger.py` untuk identifikasi POS berbasis kandidat leksikal.
- [x] Mempertahankan seluruh POS dan POS spesifik-sense tanpa memilih satu label secara otomatis.
- [x] Menahan pewarisan POS lema pada `derived_form` karena bentuk turunan dapat berubah kelas kata; tandai `requires_morphology`.
- [x] Membuat `tests/test_pos_tagger.py` dengan 10 regression tests.
- [x] Menjalankan 10 regression tests POS pada checkout Termux: 10 lulus, 0 gagal (27 November 2026).
- [x] Menjalankan ulang regression suite gabungan dari checkout Termux setelah POS ditambahkan: 110 tes lulus, 0 gagal (27 November 2026).
- [x] Membuat `tools/pos_context.py` untuk petunjuk konteks lokal yang konservatif dan disambiguasi POS.
- [x] Membuat 13 regression tests pada `tests/test_pos_context.py`; seluruhnya lulus pada checkout Termux (27 November 2026).
- [x] Menjalankan regression suite gabungan dari checkout Termux: **132 tes lulus, 0 gagal** (27 November 2026).
- [x] Menetapkan format JSONL, pembagian development/test, pedoman anotasi, dan metrik evaluasi pada [`docs/DATASET_POS.md`](DATASET_POS.md).
- [x] Menyusun batch pertama 10 kalimat berlabel (6 development, 4 test).
- [x] Menambahkan batch kedua 10 kalimat (6 development, 4 test); total 20 kalimat/91 token dalam file dataset.
- [x] Memvalidasi batch kedua di checkout Termux: 20 kalimat dan 91 token (12 development, 8 test), seluruh pemeriksaan lulus (27 November 2026).
- [x] Memperluas dataset hingga 100 kalimat (60 development, 40 test).
- [x] Membuat `tools/validasi_dataset_pos.py` untuk validasi struktur, label, status, ID, dan kecocokan token.
- [x] Membuat 9 regression tests pada `tests/test_validasi_dataset_pos.py`.
- [x] Menjalankan `python -m tools.validasi_dataset_pos` dari checkout Termux: **VALIDASI DATASET POS BERHASIL**, batch pertama: 10 kalimat, 43 token (6 development, 4 test), seluruh pemeriksaan struktur dan kesesuaian tokenizer lulus. Batch kedua (20 kalimat total) telah lolos validasi ulang di Termux: 20 kalimat, 91 token, 12 development, 8 test (27 November 2026).
- [x] Menjalankan 9 regression tests validator dari checkout Termux: 9 lulus, 0 gagal (27 November 2026).
- [x] Menjalankan ulang seluruh regression suite dari checkout Termux setelah validator POS ditambahkan: **132 tes lulus, 0 gagal** (27 November 2026).
- [x] Memvalidasi dataset POS terbaru dari checkout Termux: 30 kalimat, 156 token, 18 development, 12 test (27 November 2026).
- [x] Menyelesaikan dataset 100 kalimat dan evaluasi POS pada development set; 40 kalimat test tetap ditahan.

**Penutupan Tahap 2.5 — 27 November 2026**

- [x] Menyelesaikan penanganan kandidat POS development yang layak ditangani pada tahap ini; tidak memaksakan label untuk nama orang.
- [x] Memvalidasi POS kontekstual pada development: 250/255 dikenali, coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%, tanpa kesalahan prediksi.
- [x] Mempertahankan 40 kalimat test agar tetap tersegel.
- [x] Menjalankan validasi terpadu GitHub Actions Run #114: 60 batch/3.013 lema, dataset 100 kalimat/543 token, dan **242/242 regression tests lulus**.
- [x] Menetapkan lima kemunculan nama orang sebagai abstention yang disengaja untuk ditangani pada tahap pengenalan nama/konteks, bukan sebagai kekurangan Tahap 2.5.

**Status:** Tahap 2.5 selesai. Tidak perlu mengaudit ulang nama orang atau memaksa semua token memiliki POS.

### 2.6 Analisis struktur kalimat dasar

- [x] Menentukan masukan parser dari hasil POS leksikal dan POS kontekstual bila tersedia.
- [x] Membuat `tools/parser_kalimat.py` untuk kerangka sederhana S-P, S-P-O, dan keterangan berpreposisi.
- [x] Mengumpulkan frasa nominal sederhana yang berisi kepala nominal, pewatas adjektiva, atau numeralia sebagai rentang datar.
- [x] Membuat regression tests parser untuk frasa subjek dan objek; pola S-P-K juga diuji melalui kamus penuh pada `tests/test_integrasi_pipeline.py`.
- [x] Memasukkan negator verbal `tidak` dan `belum` (POS ADV/PART) ke rentang predikat secara terbatas.
- [x] Menguji negasi verbal dengan tes unit dan pipeline kamus penuh.
- [x] Memperluas parser secara bertahap hingga versi v1.5: modal, predikat nonverbal/linking, keterangan preposisional depan, koordinasi frasa nominal/klausa, label relasi penghubung, serta klausa subordinatif depan dan belakang.
- [x] Menetapkan parser v1.7 dengan `predicate_structure` dan modalitas `akan` (ADV) serta `bisa` (VERB) untuk memisahkan kepala predikat verbal dari pewatas modal, negasi, dan adverbial; `roles.predicate` tetap mempertahankan rentang lama demi kompatibilitas.
- [x] Menambahkan regression tests untuk perluasan parser tersebut; versi terakhir yang tercatat lulus pada Run #99 (232/232 tes) sebelum rangkaian penyelesaian POS.
- [x] Melanjutkan Tahap 2.6 dari baseline v1.6; parser kini v1.7 dan fitur lama tetap dipertahankan.
- [x] Mengenali `akan` (ADV) dan `bisa` (VERB) sebagai modal jika diikuti verba inti; penggunaan `bisa` tunggal tetap dipertahankan sebagai predikat.
- [ ] Memperluas frasa verba ke penanda modal/aspek lain hanya setelah POS dan konteksnya cukup kuat.
- [ ] Menguji variasi susunan kalimat sederhana.
- [x] Melaporkan token ambigu/tidak teranalisis dan pola yang belum didukung tanpa memaksakan struktur.
- [x] Menjalankan regression suite penuh melalui GitHub Actions Run #76: **187/187 lulus**; validasi kamus 60 batch/3.000 entri, dataset POS, dan evaluasi development juga berhasil.

### 2.7 Dataset dan pengujian terpadu

- [x] Menyusun dataset uji 100 kalimat dengan label POS dan pembagian development/test.
- [ ] Mencakup bahasa baku, informal, slang, salah ketik, imbuhan, dan kata ulang.
- [x] Menyimpan expected POS per token pada dataset JSONL.
- [x] Menjalankan regression suite seluruh komponen: 182/182 lulus pada GitHub Actions Run #75 (catatan historis).
- [x] Validasi terpadu terbaru Run #114: dataset 100 kalimat/543 token tervalidasi, evaluasi development POS berhasil, dan **242/242 regression tests lulus**.
- [ ] Memperluas variasi dataset untuk bahasa baku, informal, slang, salah ketik, imbuhan, dan kata ulang; test split yang ada tetap tersegel.

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

**Status terbaru (27 November 2026):** audit isi dan relasi kamus 60/60 batch selesai. Audit index terhadap sumber juga selesai: 3.000 lema terindeks, tidak ada lema hilang, baris index tidak cocok, atau kesalahan struktur. Dataset POS berisi 100 kalimat (60 development, 40 test). Evaluasi development menghasilkan 227/255 prediksi benar pada jalur leksikal (89,0%) dan 228/255 pada jalur kontekstual (89,4%); selective accuracy 100% dan tidak ada kesalahan pada prediksi yang dikeluarkan. Hasil ini hanya berlaku untuk development set; test set tetap ditahan.

Pengujian integrasi baru menggunakan kamus asli 3.000 lema telah ditambahkan pada `tests/test_integrasi_pipeline.py`. GitHub Actions Run #75 menjalankan validasi relasi lima batch terakhir, validasi penuh 60 batch/3.000 entri, validasi dataset, evaluasi development, dan **182 regression tests; seluruhnya lulus**.

**Titik lanjut aktif:** parser v0.3 mengenali negasi verbal terbatas (`tidak` dan `belum`) sebagai bagian predikat. Berikutnya perluas frasa verba/modal secara hati-hati, lalu pelengkap, negasi predikat adjektival/nominal, koordinasi, dan variasi susunan kalimat. Integrasi Android, pemrosesan makna lintas kalimat, dan pembentukan respons juga belum selesai. Jangan menyamakan kelulusan tes fondasi dengan kemampuan memahami bahasa bebas seperti LLM.

## Dokumen rujukan

- [README proyek](../README.md)
- [Status teknis tahap pengolahan bahasa](STATUS_TAHAP_PENGOLAHAN_BAHASA.md)
- [Dokumentasi kamus](KAMUS.md)

**Aturan pembaruan:** jangan mencentang pekerjaan hanya karena file sudah dibuat. Centang setelah isi dan hasilnya diperiksa; untuk pengujian, centang hanya setelah tes benar-benar dijalankan.


Pembaruan reduplikasi: analisis konservatif kini mengenali pola `ber-` pada unsur pertama dalam bentuk seperti `berjalan-jalan` dan `berlari-lari`, hanya jika unsur dasar kedua cocok dengan lema kamus. Dua regression tests baru dijalankan bersama suite morfologi: 36 lulus, 0 gagal.


Pembaruan morfofonemik nasal: aturan restorasi `meng-` kini tidak menambahkan kandidat berawalan `k` secara spekulatif apabila sisa bentuk setelah `meng-` sudah cocok dengan lema kamus. Contoh yang diuji: `mengambil` menghasilkan `ambil`, bukan `kambil`; `mengunci` tetap dapat menghasilkan `kunci`. Suite morfologi: 38 lulus, 0 gagal.


**Pembaruan restorasi nasal `peng-`:** aturan restorasi `peng-` kini mengikuti perlindungan konservatif yang sebelumnya diterapkan pada `meng-`. Jika sisa bentuk setelah prefiks sudah cocok dengan lema kamus, kandidat tambahan `k+akar` tidak dibuat. Tes memastikan `pengambil` menghasilkan `ambil`, bukan `kambil`, sedangkan `pengunci` tetap dapat menghasilkan `kunci`. Suite morfologi terbaru: 40 lulus, 0 gagal; total tes komponen terpisah: 93 lulus, 0 gagal (45 fondasi + 8 analyzer + 40 morfologi).

**Pembaruan prioritas restorasi nasal `men-/mem-/pen-/pem-`:** bila kandidat hasil pemulihan konsonan awal `t` atau `p` tersedia di kamus, kandidat mentah yang kebetulan cocok tidak lagi ikut ditambahkan. Perlindungan berlaku untuk analisis prefiks tunggal dan gabungan prefiks+sufiks. Kasus `menari` serta `menarikan` diuji: `tari` dipilih, bukan `ari`. Suite morfologi: 42 lulus, 0 gagal; total komponen terpisah: 95 lulus, 0 gagal (45 fondasi + 8 analyzer + 42 morfologi).

**Audit restorasi `meng-/peng-` pada akar vokal (sedang diverifikasi):** ditemukan celah pada analisis gabungan prefiks+sufiks dan konfiks `peN-an`: kandidat restorasi `k+akar` masih dapat muncul meskipun akar vokal sudah cocok dengan kamus. Aturan kini menahan kandidat tersebut untuk bentuk seperti `mengajarkan` dan `pengajaran`, sambil mempertahankan restorasi ketika akar tanpa `k` tidak ditemukan (misalnya `mengunci`/`pengunci`). Dua regression tests baru ditambahkan. Suite 46 tes belum dijalankan ulang; status tes terverifikasi tetap 42 morfologi dan 95 total komponen.


**Audit akar kata berawalan `ng-` (27 November 2026):** indeks token aktual diperiksa untuk lema `ngambek`, `ngarai`, `ngaret`, `ngaruh`, `ngebayangin`, `ngebut`, `ngecek`, `ngedumel`, `ngeh`, `ngemil`, `ngengat`, `ngeri`, dan `ngobrol`. Tidak ditemukan contoh bentuk permukaan `meng-/peng-` yang secara linguistik dan berdasarkan lema kamus membenarkan aturan restorasi baru untuk kelompok ini. Karena itu, tidak ada perubahan kode atau tes yang dibuat dari dugaan semata. Audit berlanjut dengan pendekatan berbasis contoh nyata; suite 47 tes morfologi telah dijalankan ulang dan lulus; hasil terbaru adalah 47 tes morfologi dan 100 tes komponen total.


**Audit cakupan bentuk turunan pada indeks token (27 November 2026):** indeks `m-o.tsv` dan `p-r.tsv` diperiksa untuk bentuk berimbuhan yang telah direkam sebagai `derived_form`. Contoh yang ditemukan mencakup `menulis`, `mengajar`, `mengambil`, `menyapu`, `menyampaikan`, `pengambilan`, `penyakit`, `penyampaian`, `pembacaan`, dan `penolakan`. Bentuk-bentuk ini sudah terhubung ke lema kanonis pada indeks, sehingga pencocokan leksikal dapat mengenalinya sebelum analisis morfologi fallback dipanggil. Tidak ada perubahan kode atau jumlah tes pada audit ini. Tes morfologi terkini berjumlah 47 metode; eksekusi terbaru yang terverifikasi adalah 47 lulus, dan total komponen terpisah adalah 100 lulus, 0 gagal. Langkah berikutnya: audit cakupan alomorf `peN-` dan interaksinya dengan lema yang memang berawalan `peng-/peny-`, tanpa mengubah aturan sebelum ada kasus regresi yang sah.


### Audit lema kanonis berawalan peN- (27 November 2026)
- [x] Periksa indeks token untuk lema yang diawali `peng-` dan `peny-/pen-`, termasuk `pengacara`, `pengadilan`, `pengemudi`, `penggaris`, `penguin`, `penjara`, `peniti`, `penipuan`, `penasaran`, `penyanyi`, dan `penyu`.
- [x] Verifikasi alur morfologi: token yang sudah cocok persis dengan lema/varian/bentuk turunan dikembalikan tanpa stemming.
- [x] Tambahkan regression test untuk memastikan 11 lema kanonis tersebut tidak dipecah sebagai imbuhan, termasuk pemeriksaan kapitalisasi `PENGUIN`.
- [x] Jalankan ulang seluruh suite morfologi terbaru (47 tes) pada salinan terisolasi yang direkonstruksi dari file GitHub; 47/47 lulus. Catatan: belum dijalankan dari checkout repository penuh.

Catatan: audit tidak menemukan bug pada alur kecocokan kata utuh. Perubahan hanya menambah cakupan regression test; aturan morfologi tidak diubah. File tes berisi 47 metode dan suite terbaru telah dijalankan: 47/47 lulus; total komponen terpisah 100/100 lulus.


### Hasil eksekusi suite morfologi terbaru (27 November 2026)
- [x] File `tests/test_morfologi.py` terbaru (47 metode) dijalankan bersama salinan `tools/morfologi.py` dan `tools/pencocokan_kamus.py` yang diambil dari GitHub.
- [x] Hasil: **47 passed, 0 failed**.
- [x] Total tes komponen terverifikasi secara terpisah menjadi **100 passed, 0 failed** (fondasi 45 + analisis teks 8 + morfologi 47).
- [x] Eksekusi regression suite dari checkout repository penuh dan validasi seluruh 60 batch kamus telah dilakukan pada 27 November 2026 melalui Termux.

Catatan historis: sebelum validasi Termux, 47 tes morfologi dijalankan pada lingkungan terisolasi. Hasil tersebut kini dilengkapi dan diperkuat oleh eksekusi gabungan 100 tes dari checkout repository penuh.


### Validasi checkout penuh melalui Termux (27 November 2026)
- [x] Clone repository `Sistem_bahasa` pada perangkat Android menggunakan Git.
- [x] Jalankan `python -m tools.validasi_kamus_lengkap`: **VALIDASI BERHASIL**, 60 batch, 3.000 entri; JSONL, field wajib, format ID, array wajib, ID duplikat, dan lema duplikat diperiksa.
- [x] Jalankan `python -m unittest discover -s tests -v` dari root checkout: **Ran 100 tests — OK**, 0 gagal.
- [x] Konfirmasi hasil gabungan komponen: analyzer 8, loader 12, morfologi 47, normalisasi 8, pencocokan kamus 13, tokenizer 12.
- [x] Tutup celah validasi loader seluruh kamus dan regression suite checkout penuh.

Catatan: validasi dilakukan lokal pada checkout repository di Termux, bukan melalui GitHub Actions. Hasil ini tidak berarti Tahap 2.5–2.7 sudah selesai.


### Progres awal Tahap 2.5 — POS (27 November 2026)
- [x] Taksonomi POS diambil dari dokumentasi kamus yang sudah ada; tidak membuat kode baru.
- [x] Implementasi awal `tools/pos_tagger.py` dan 10 tes regresi `tests/test_pos_tagger.py` telah ditambahkan ke branch `main`.
- [x] Implementasi mempertahankan beberapa POS dan POS per-sense, tidak melakukan disambiguasi konteks.
- [x] Bentuk turunan tercatat tidak mewarisi POS lema secara otomatis karena dapat berubah kelas kata (contoh: `makan` → `makanan`); statusnya `requires_morphology`.
- [x] `git pull` berhasil pada checkout Termux dan 10 regression tests POS lulus (27 November 2026).
- [x] Regression suite gabungan dijalankan ulang setelah POS ditambahkan: **110 tes lulus, 0 gagal** (`python -m unittest discover -s tests -v`).



### Verifikasi POS dan regression suite gabungan — 27 November 2026
- [x] Jalankan `python -m unittest discover -s tests -p "test_pos_tagger.py" -v`: **10 tes lulus, 0 gagal**.
- [x] Jalankan `python -m unittest discover -s tests -v` dari checkout Termux setelah POS ditambahkan: **Ran 110 tests — OK**, 0 gagal.
- [x] Konfirmasi seluruh 100 tes komponen sebelumnya tetap lulus bersama 10 tes POS baru.

**Titik lanjut aktif:** Tahap 2.5 belum selesai. Berikutnya adalah menambahkan petunjuk konteks kalimat untuk disambiguasi POS, kemudian membuat dataset kalimat berlabel dan mengukur akurasi. Disambiguasi belum boleh diklaim tersedia sebelum implementasi dan evaluasi dilakukan.


### Verifikasi dataset POS batch kedua dan regression suite penuh — 27 November 2026
- [x] Validasi dataset POS dari Termux: 20 kalimat, 91 token, 12 development, 8 test; seluruh pemeriksaan struktur dan kecocokan tokenizer lulus.
- [x] Jalankan `python -m unittest discover -s tests -v` setelah batch kedua ditarik: **Ran 132 tests — OK**, 0 gagal, waktu 0,087 detik.
- [x] Konfirmasi regression suite mencakup analyzer, loader kamus, morfologi, normalisasi, pencocokan kamus, POS kontekstual, POS leksikal, tokenizer, dan validator dataset POS.

**Titik lanjut:** audit mutu anotasi pada development set dan perluas dataset secara bertahap. Jangan gunakan test split untuk menyetel aturan POS.


### Penambahan batch ketiga dataset POS — 27 November 2026
- [x] Tambahkan 10 kalimat baru (`pos_0021`–`pos_0030`): 6 development dan 4 test.
- [x] Perbarui dataset menjadi **30 kalimat / 156 token**, dengan komposisi 18 development dan 12 test.
- [x] Tarik perubahan batch ketiga ke Termux dan jalankan `python -m tools.validasi_dataset_pos`: **VALIDASI DATASET POS BERHASIL**, 30 kalimat, 156 token, 18 development, 12 test (27 November 2026).
- [ ] Lanjutkan audit anotasi development set. Jangan gunakan test split untuk menyetel aturan.




### Regression suite setelah validasi batch ketiga
- [x] Jalankan `python -m unittest discover -s tests -v` dari Termux setelah batch ketiga: **Ran 132 tests in 0.105s — OK**, 0 gagal dan 0 error (27 November 2026).


**Status terbaru:** validasi dataset batch ketiga dan regression suite penuh telah berhasil pada checkout Termux. Berikutnya audit mutu anotasi pada development set; test split tetap ditahan.


## Pembaruan status POS — 27 November 2026

- [x] Batch ketiga dataset POS ditarik ke Termux dan lolos validasi: 30 kalimat, 156 token, 18 development, 12 test.
- [x] Regression suite penuh dijalankan ulang setelah batch ketiga: 132/132 lulus, 0 gagal, 0 error.
- [x] Audit awal seluruh 18 kalimat development dicatat di `docs/AUDIT_ANOTASI_POS.md`; split test tidak diperiksa.
- [x] Mencatat kasus yang perlu konvensi anotasi lebih eksplisit: demonstrativa `itu`, penanda aspek `sedang`, larangan `jangan`, dan gelar `Pak`.
- [ ] Menetapkan konvensi POS untuk kasus-kasus tersebut dalam `docs/DATASET_POS.md`.
- [ ] Audit ulang development set setelah pedoman diperjelas.
- [ ] Evaluasi prediksi POS pada development set; jangan gunakan test untuk penyetelan aturan.

**Titik lanjut:** perjelas pedoman anotasi berdasarkan audit awal. Belum ada label dataset yang diubah dan belum ada klaim akurasi POS.


### Pembaruan pedoman anotasi POS — 27 November 2026

- [x] Menetapkan konvensi operasional POS untuk demonstrativa, aspek/modalitas, larangan, gelar/sapaan, kata sebab, dan penanda tanya dalam `docs/DATASET_POS.md` subbagian 5.1.
- [x] Mencatat keputusan konvensi pada `docs/AUDIT_ANOTASI_POS.md`.
- [ ] Menarik pembaruan pedoman ke Termux.
- [ ] Audit ulang 18 kalimat development menggunakan konvensi baru.
- [ ] Koreksi label gold hanya jika ada ketidaksesuaian yang jelas; jangan mengubah split test.
- [ ] Jalankan validator dataset dan regression suite setelah koreksi data.

**Titik lanjut:** pengguna menjalankan `git pull`, lalu audit ulang development. Belum ada label JSONL yang diubah dan belum ada klaim akurasi POS.


### Audit ulang anotasi POS development — 27 November 2026
- [x] Konvensi anotasi POS v1 ditetapkan pada `docs/DATASET_POS.md` subbagian 5.1.
- [x] Audit ulang seluruh 18 kalimat development berdasarkan konvensi tersebut.
- [x] Koreksi label `jangan` pada record `pos_0024` dari `ADV` menjadi `PART`; split test tidak diubah.
- [x] Catat hasil dan batasan audit pada `docs/AUDIT_ANOTASI_POS.md`.
- [ ] Tarik perubahan ke Termux dan jalankan `python -m tools.validasi_dataset_pos`.
- [ ] Jalankan `python -m unittest discover -s tests -v` setelah validasi.

**Titik lanjut:** verifikasi perubahan dataset dari checkout Termux. Belum ada klaim akurasi POS.


## Verifikasi terbaru setelah koreksi anotasi — 27 November 2026

Bagian ini menjadi acuan status terkini apabila catatan historis di atas masih menyebut verifikasi menunggu atau jumlah tes yang lebih lama.

- [x] Audit ulang 18 record development dan koreksi gold label `jangan` pada `pos_0024` dari `ADV` menjadi `PART`; split test tidak diubah.
- [x] Jalankan `python -m tools.validasi_dataset_pos` dari Termux setelah koreksi: **30 kalimat, 156 token, 18 development, 12 test — VALIDASI DATASET POS BERHASIL**.
- [x] Jalankan `python -m unittest discover -s tests -v` dari Termux setelah koreksi: **132 tes lulus, 0 gagal, 0 error** (`Ran 132 tests in 0.093s — OK`).
- [ ] Perluas dataset secara bertahap menuju 100 kalimat; utamakan development set dan tetap tahan test split.
- [ ] Bangun evaluasi POS yang mengukur prediksi terhadap gold label pada development set. Validasi struktur dan regression suite bukan skor akurasi.

**Titik lanjut aktif:** perluasan development dataset dan persiapan evaluasi POS yang terukur. Jangan mulai parser kalimat atau menggunakan test split untuk menyetel aturan sebelum evaluasi development memadai.


## Evaluator POS development — 27 November 2026

- [x] Membuat `tools/evaluasi_pos.py` untuk membandingkan prediksi POS leksikal dan kontekstual dengan gold label.
- [x] Membatasi pemuatan data evaluator pada split `development`; evaluator menolak record split lain.
- [x] Menyertakan coverage, accuracy terhadap seluruh token resolved, selective accuracy, confusion counts, dan penanganan gold ambiguous.
- [x] Membuat 4 regression tests awal pada `tests/test_evaluasi_pos.py`.
- [x] Menjalankan 4 regression tests evaluator dari Termux: **4 lulus, 0 gagal** (27 November 2026).
- [x] Menjalankan evaluator pada 18 kalimat development: 72 token resolved; POS leksikal dan kontekstual sama-sama menghasilkan 42 prediksi benar, coverage 58,3%, accuracy 58,3%, selective accuracy 100%.
- [x] Menjalankan regression suite penuh dari Termux: **136 tes lulus, 0 gagal, 0 error** (`Ran 136 tests in 0.106s — OK`, 27 November 2026).
- [!] Audit satu token gold `ambiguous` (`jalan` pada `pos_0006`) yang justru dipaksakan menjadi satu POS oleh sistem; telusuri kandidat POS kamus dan perilaku konteks sebelum memperbaiki aturan.
- [ ] Perluas dataset secara bertahap; tambah contoh development yang mewakili kelas kata dan ambiguitas. Test split tetap ditahan.

**Catatan:** skor hanya berlaku untuk 18 kalimat development yang ada, bukan akurasi umum. POS kontekstual belum meningkatkan hasil dibanding POS leksikal pada sampel ini. Jangan memakai test split untuk menyetel aturan.


## Verifikasi koreksi metadata POS lema "jalan" — 27 November 2026

- [x] Menemukan penyebab: entri `K0020` hanya mencantumkan `NOUN` walau catatan penggunaan menyebut fungsi verba.
- [x] Memperbarui POS lema menjadi `NOUN` dan `VERB`, dengan dua sense yang masing-masing memiliki POS spesifik.
- [x] Menambahkan regression test integrasi agar token gold ambiguous `jalan` pada development tidak dipaksakan menjadi satu POS.
- [x] Menarik seluruh perubahan ke Termux melalui `git pull`.
- [x] Menjalankan 5 tes evaluator POS: **5 lulus, 0 gagal**.
- [x] Menjalankan evaluator pada 18 kalimat development: 72 token resolved; POS leksikal dan kontekstual sama-sama menghasilkan 42 prediksi benar, coverage 58,3%, accuracy 58,3%, selective accuracy 100%.
- [x] Memastikan penanganan token gold ambiguous: **1 ditahan, 0 dipaksakan**.
- [x] Menjalankan regression suite penuh dari Termux: **137 tes lulus, 0 gagal, 0 error**.

**Interpretasi:** koreksi metadata membuat fragmen `Jalan.` tetap ambigu sesuai gold label. Hasil POS kontekstual belum lebih baik daripada POS leksikal pada sampel ini. Selective accuracy 100% hanya berlaku pada prediksi yang dikeluarkan; coverage 58,3% dan accuracy keseluruhan 58,3%. Hasil hanya berlaku untuk development set kecil, bukan estimasi akurasi umum.

**Titik lanjut aktif:** perluas dataset POS dari 30 menuju 100 kalimat, dengan penambahan development set yang representatif. Pertahankan test split sebagai data tertahan dan jangan mulai parser kalimat sebelum evaluasi POS development memadai.


### Penambahan batch keempat dataset POS — 27 November 2026
- [x] Menambahkan 10 kalimat baru (`pos_0031`–`pos_0040`): 6 development dan 4 test.
- [x] Memperluas dataset dari 30 menjadi **40 kalimat**; komposisi menjadi 24 development dan 16 test.
- [x] Menambahkan variasi percakapan informal, modalitas, imbuhan, konjungsi, interjeksi, demonstrativa, adjektiva, numeralia, dan preposisi.
- [x] Tarik batch keempat ke Termux dan jalankan `python -m tools.validasi_dataset_pos`: **40 kalimat, 215 token, 24 development, 16 test — berhasil**.
- [x] Jalankan regression suite penuh setelah validasi: **137/137 lulus, 0 gagal, 0 error**.
- [x] Evaluasi development set setelah validasi; test split tetap ditahan dan tidak digunakan untuk penyetelan.

**Titik lanjut:** verifikasi batch keempat dari checkout Termux. Jumlah token 215 adalah hitungan anotasi sebelum validator dijalankan; jangan tandai batch ini terverifikasi sampai output Termux diterima.


### Verifikasi batch keempat dan evaluasi POS — 27 November 2026
- [x] Validasi dataset di Termux: **40 kalimat, 215 token, 24 development, 16 test**.
- [x] Regression suite penuh: **137 tes lulus, 0 gagal, 0 error**.
- [x] Evaluasi development: 102 token resolved; leksikal dan kontekstual sama-sama 55 benar, coverage 54,9%, accuracy 53,9%, selective accuracy 98,2%.
- [x] Gold ambiguous: 1 ditahan, 0 dipaksakan.
- [x] Audit `mau` pada `pos_0031`: ditetapkan sebagai `VERB` (verba modal kehendak), sesuai entri kamus `K0024`; label gold development dikoreksi dari `ADV` menjadi `VERB` tanpa mengubah kamus atau aturan program. Menunggu validasi ulang di Termux.
- [x] Audit awal kasus `INTJ`: `wah` belum ditemukan pada indeks kamus; `aduh` tersedia sebagai `K0602`/`INTJ`. Ditambahkan contoh development `aduh` untuk menguji interjeksi yang sudah tersedia; tidak perlu mengubah aturan POS hanya untuk `wah`.

**Titik lanjut aktif:** tarik koreksi anotasi `mau`, jalankan ulang validator, evaluator, dan regression suite; setelah itu audit cakupan prediksi kelas POS. Jangan gunakan 16 record test untuk penyetelan. Setelah verifikasi, lanjutkan batch kelima menuju 50 kalimat.


### Penambahan batch kelima dataset POS — 27 November 2026

- [x] Menambahkan 10 record baru (`pos_0041`–`pos_0050`): 6 development dan 4 test.
- [x] Memperluas dataset dari 40 menjadi **50 kalimat**; komposisi menjadi **30 development dan 20 test**.
- [x] Menambahkan contoh interjeksi `aduh` (INTJ) yang sudah tersedia pada kamus, serta variasi kalimat sederhana, demonstrativa, adjektiva, verba, dan preposisi.
- [x] Pemeriksaan struktural awal langsung pada file GitHub: 50 kalimat, 266 token, 30 development, 20 test; JSON, ID, label/status POS, dan kecocokan token diperiksa tanpa temuan.
- [x] GitHub Actions run [#1](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45906966948): validator dataset berhasil (50 kalimat, 266 token, 30 development, 20 test); evaluator development berhasil; regression suite **137/137 lulus**.

**Titik lanjut:** verifikasi batch kelima melalui pemeriksaan otomatis yang tersedia. Jangan gunakan 20 record test untuk penyetelan.


### Otomatisasi validasi POS di GitHub Actions

- [x] Menambahkan `.github/workflows/pos-validation.yml` untuk menjalankan validator dataset, evaluator development-only, dan seluruh regression suite pada perubahan `data/dataset_pos/`, `data/kamus/`, `tools/`, atau `tests/` di branch `main`/pull request.
- [x] Menambahkan pemicu manual `workflow_dispatch`.
- [ ] Menunggu eksekusi pertama pada perubahan dataset/kode berikutnya; workflow baru dibuat dan belum ada hasil run yang diklaim.

Catatan kuota: workflow hanya terpicu pada perubahan file dataset/kamus/kode/tes, bukan perubahan dokumentasi saja. Setiap run memakai kuota GitHub Actions.


### Hasil verifikasi otomatis batch kelima

- [x] Validator Python resmi: **50 kalimat, 266 token, 30 development, 20 test — berhasil**.
- [x] Evaluator development: 125 token resolved; 72 benar; coverage 57,6%; accuracy 57,6%; selective accuracy 100%.
- [x] INTJ: `aduh` terprediksi benar; `wah` abstain karena belum tercakup dalam indeks kamus.
- [x] Gold ambiguous: 1 ditahan, 0 dipaksakan.
- [x] Regression suite penuh: **137/137 lulus, 0 gagal, 0 error**.

Catatan: POS kontekstual dan leksikal masih menghasilkan metrik identik. Kenaikan angka terhadap batch sebelumnya tidak boleh dianggap bukti tren peningkatan karena komposisi dan jumlah sampel berubah. Test split 20 kalimat tetap ditahan.


### Penambahan batch keenam dataset POS — 27 November 2026

- [x] Menambahkan 10 record (`pos_0051`–`pos_0060`): 6 development dan 4 test.
- [x] Total dataset menjadi **60 kalimat, 314 token, 36 development, 24 test**.
- [x] Preflight struktural sebelum commit: JSON, ID, split, label/status POS, dan kecocokan token diperiksa tanpa temuan.
- [x] GitHub Actions run [#2](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45907643287): validator 60 kalimat/314 token berhasil; evaluator development berhasil; regression suite **137/137 lulus**.

**Titik lanjut:** periksa hasil workflow; jangan gunakan 24 record test untuk menyetel aturan.


### Hasil evaluasi batch keenam

- [x] Validator: 60 kalimat, 314 token, 36 development, 24 test.
- [x] Evaluator development: 148 token resolved; 90 benar; coverage 60,8%; accuracy 60,8%; selective accuracy 100%.
- [x] Gold ambiguous: 1 ditahan, 0 dipaksakan.
- [x] Regression suite: 137/137 lulus.
- [x] Audit cakupan kelas dengan abstention tinggi: NUM (0/2), PREP (1/7), ADV (4/13), dan CONJ (3/6); gap indeks dicatat tanpa mengubah label gold.

Catatan: metrik batch keenam tidak boleh disebut peningkatan kualitas yang terukur dibanding batch kelima karena ukuran dan komposisi development berubah. POS kontekstual masih identik dengan POS leksikal.


### Audit cakupan indeks leksikal POS

- [x] Bandingkan token resolved pada 36 kalimat development dengan delapan shard indeks kamus.
- [x] Catat gap untuk ADV, PRON, PREP, CONJ, ADJ, NUM, NOUN, VERB, dan INTJ pada `docs/AUDIT_ANOTASI_POS.md`.
- [x] Menentukan suplementasi POS terpisah untuk 12 kata tugas/numeralia terpilih; kamus 3.000 lema tidak diubah.
- [x] Menambahkan regression tests untuk suplementasi, prioritas kamus, dan pelestarian ambiguitas; workflow GitHub Actions berhasil.
- [x] Lanjutkan batch ketujuh setelah strategi cakupan diputuskan; test split tetap ditahan.


### Implementasi suplementasi POS terfokus — 27 November 2026

- [x] Membuat `tools/pos_supplement.py` sebagai daftar fallback terpisah dari kamus inti.
- [x] Menambahkan 12 bentuk terpilih: `dua`, `tiga` (NUM); `di`, `ke`, `pada` (PREP); `atau`, `kalau`, `tetapi` (CONJ); `akan`, `sedang`, `sangat`, `sekali` (ADV).
- [x] Mengintegrasikan fallback ke `tools/pos_tagger.py`; hanya digunakan ketika tidak ada kandidat kamus. Kandidat kamus tetap lebih utama dan bentuk turunan yang memerlukan morfologi tidak dipaksa.
- [x] Menambahkan tes untuk semua 12 kata, prioritas kandidat kamus, ambiguitas `jalan`, serta kata polifungsi yang sengaja belum disuplementasi (`dulu`, `tetap`).
- [x] GitHub Actions run [#5](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908285217): validator 60 kalimat/314 token berhasil; evaluator development berhasil; regression suite **141/141 lulus**.
- [x] Evaluasi development setelah suplementasi: 107/148 benar, coverage 72,3%, accuracy 72,3%, selective accuracy 100%. POS leksikal dan kontekstual sama. Satu gold ambiguous tetap ditahan, tidak dipaksakan.

**Catatan:** Batch 7 (`pos_0061`–`pos_0070`) sudah selesai dan diverifikasi; lihat bagian “Batch ketujuh dan verifikasi otomatis” di bawah. Test split tetap tertahan.


### Batch ketujuh dan verifikasi otomatis — 27 November 2026

- [x] Menambahkan `pos_0061`–`pos_0070`: enam kalimat development dan empat kalimat test.
- [x] Dataset menjadi **70 kalimat, 374 token, 42 development, 28 test**.
- [x] GitHub Actions run [#6](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908531211): validator berhasil; regression suite **141/141 lulus**.
- [x] Evaluator development-only: 174 token resolved, 131 benar, coverage 75,3%, accuracy 75,3%, selective accuracy 100%; satu gold ambiguous ditahan dan nol dipaksakan.

**Catatan:** Batch 8 (`pos_0071`–`pos_0080`) sudah selesai dan diverifikasi; lihat bagian “Batch kedelapan dan verifikasi otomatis” di bawah. Seluruh 32 kalimat test tetap tertahan.


### Batch kedelapan dan verifikasi otomatis — 27 November 2026

- [x] Menambahkan `pos_0071`–`pos_0080`: enam kalimat development dan empat kalimat test.
- [x] Dataset menjadi **80 kalimat, 428 token, 48 development, 32 test**.
- [x] GitHub Actions run [#7](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908957782): validator berhasil; regression suite **141/141 lulus**.
- [x] Evaluator development-only: 199 token resolved, 149 benar, coverage 74,9%, accuracy 74,9%, selective accuracy 100%; satu gold ambiguous ditahan dan nol dipaksakan.

**Catatan:** Batch 9 (`pos_0081`–`pos_0090`) sudah selesai dan diverifikasi; lihat bagian “Batch kesembilan dan verifikasi otomatis” di bawah. Seluruh 36 kalimat test tetap tertahan.


### Batch kesembilan dan verifikasi otomatis — 27 November 2026

- [x] Menambahkan `pos_0081`–`pos_0090`: enam kalimat development dan empat kalimat test.
- [x] Dataset menjadi **90 kalimat, 485 token, 54 development, 36 test**.
- [x] GitHub Actions run [#8](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909135531): validator berhasil; regression suite **141/141 lulus**.
- [x] Evaluator development-only: 227 token resolved, 167 benar, coverage 73,6%, accuracy 73,6%, selective accuracy 100%; satu gold ambiguous ditahan dan nol dipaksakan.

**Catatan:** Batch 10 (`pos_0091`–`pos_0100`) sudah selesai dan diverifikasi; lihat bagian “Batch kesepuluh dan verifikasi otomatis” di bawah. Seluruh 40 kalimat test tetap tertahan.


### Batch kesepuluh dan verifikasi otomatis — 27 November 2026

- [x] Menambahkan `pos_0091`–`pos_0100`: enam kalimat development dan empat kalimat test.
- [x] Dataset mencapai target v1: **100 kalimat, 543 token, 60 development, 40 test**.
- [x] GitHub Actions run [#9](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909322818): validator berhasil; regression suite **141/141 lulus**.
- [x] Evaluator development-only: 255 token resolved, 186 benar, coverage 73,3%, accuracy 72,9%, selective accuracy 99,5%; satu gold ambiguous ditahan dan nol dipaksakan.

**Catatan evaluasi:** terdapat setidaknya satu prediksi keliru pada token yang diputuskan sistem; selective accuracy 99,5% menandakan hasil yang diputuskan tidak sempurna. Jangan menyebut akurasi 100%. Seluruh 40 kalimat test tetap tertahan untuk evaluasi terpisah.

**Titik lanjut:** audit menyeluruh dataset v1, analisis kesalahan development, dan rencana evaluasi test yang terkontrol. Jangan menyetel aturan menggunakan test sebelum protokol evaluasi ditetapkan.


### Pelaporan kesalahan evaluator POS — 27 November 2026

- [x] Memperluas `tools/evaluasi_pos.py` agar menampilkan token development yang salah diprediksi beserta ID record, kalimat, gold, dan prediksi.
- [x] Menambahkan regression test untuk struktur dan ketepatan daftar kesalahan.
- [x] GitHub Actions [run #10](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909498360): validator 100 kalimat/543 token berhasil; regression suite **142/142 lulus**.
- [x] Menemukan kesalahan konkret: `pos_0093`, token `disiplin`, gold ADJ, prediksi NOUN pada evaluator leksikal dan kontekstual.

**Titik lanjut:** audit entri kamus `disiplin` dan konteks kalimat sebelum mengubah aturan atau anotasi. Jangan memakai split test.


### Perbaikan ambiguitas POS `disiplin` — 27 November 2026

- [x] Audit entri `K0788`: `disiplin` sebelumnya hanya berlabel NOUN.
- [x] Menambahkan sense ADJ terpisah tanpa menghapus sense NOUN.
- [x] Menambahkan aturan koordinasi POS yang konservatif untuk `dan`, `serta`, `maupun` ketika label POS konjung kiri dan kandidat kanan memiliki tepat satu irisan.
- [x] Menambahkan regression test untuk “Dia sangat rajin dan disiplin”.
- [x] GitHub Actions [run #11](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909687815): validator 100 kalimat/543 token berhasil; regression suite **143/143 lulus**.
- [x] Evaluasi development: POS konteks lokal 187/255 benar, coverage/accuracy 73,3%, selective accuracy 100%, dan 0 kesalahan prediksi yang diputuskan.

**Catatan:** POS leksikal masih abstain pada sebagian token ambigu; hasil kontekstual tidak boleh dianggap akurasi umum. Seluruh 40 kalimat test tetap tertahan.


### Diagnostik abstention POS dan suplementasi fungsi kata — 27 November 2026

- [x] Memperluas evaluator agar melaporkan abstention development menurut gold POS, sumber/status, kandidat, ID, dan kalimat.
- [x] Menambahkan regression test untuk konsistensi laporan abstention.
- [x] Menambahkan fallback terkurasi `itu` (PRON), `dan`/`ketika` (CONJ), dan `wah` (INTJ); kata polifungsi `baru`, `dulu`, dan `tetap` tetap tidak dipaksa.
- [x] GitHub Actions [run #13](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45910106880): validator 100 kalimat/543 token berhasil; regression suite **144/144 lulus**.
- [x] Evaluasi development: contextual POS 208/255 benar, coverage/accuracy 81,6%, selective accuracy 100%, tanpa salah prediksi pada token yang diputuskan.
- [x] Audit sisa abstention: ADJ 2, ADV 3, NOUN 19, VERB 23.

**Titik lanjut:** audit integrasi morfologi untuk verba berimbuhan dan cakupan lema NOUN. Jangan gunakan 40 record test untuk penyetelan.

### Integrasi morfologi ke POS tagger — 27 November 2026

- [x] Menghubungkan `analyze_morphology()` ke `analyze_text()`; setiap token kata kini membawa kandidat morfologi yang tervalidasi oleh kamus.
- [x] Mengizinkan bentuk turunan yang memang tercatat di kamus untuk dianalisis morfologinya, tanpa melakukan stemming pada lema utuh atau variasi ejaan.
- [x] Mengintegrasikan bukti morfologi ke POS tagger secara konservatif: label VERB hanya diberikan untuk pola verbal yang didukung dan seluruh kandidat lema dasarnya memiliki POS VERB.
- [x] Mempertahankan abstention untuk pola yang belum cukup kuat; tes khusus memastikan `bekerja` dari lema `kerja` (NOUN) tidak otomatis dipaksa menjadi VERB.
- [x] Menambahkan regression tests untuk analisis bentuk turunan tercatat dan penetapan POS berbasis morfologi.
- [x] GitHub Actions [run #26](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45910648622): validator 100 kalimat/543 token berhasil; regression suite **147/147 lulus**.
- [x] Evaluasi development-only: POS leksikal 215/255 benar (coverage/accuracy 84,3%); POS kontekstual 216/255 benar (coverage/accuracy 84,7%); selective accuracy 100%, tanpa salah prediksi pada token yang diputuskan.
- [x] Abstention VERB turun dari 23 menjadi 15; sisa total: ADJ 2, ADV 3, NOUN 19, VERB 15. Satu gold ambiguous tetap ditahan dan tidak dipaksakan.

**Titik lanjut:** audit pola morfologi yang belum tercakup (termasuk bentuk ber- dan bentuk dengan perubahan/penambahan konsonan), lalu audit lema NOUN yang belum ada di indeks. Jangan memakai 40 record test untuk menyetel aturan.


### Perbaikan prioritas bentuk turunan tercatat — 27 November 2026

- [x] Mengutamakan relasi `derived_form` yang sudah tercatat di kamus daripada segmentasi imbuhan spekulatif.
- [x] Memvalidasi bentuk turunan berawalan `meN-` dan `ber-` melalui lema dasar; bentuk `ber-` hanya diberi VERB jika relasi turunannya tercatat dan lema dasarnya ber-POS VERB.
- [x] Menambahkan dua regression tests untuk `memasak` dan `bermain`, serta mempertahankan tes negatif agar `bekerja` dari lema NOUN `kerja` tidak dipaksakan menjadi VERB.
- [x] Verifikasi Termux pada 27 November 2026: **149/149 regression tests lulus**.
- [x] Evaluasi development-only: POS leksikal **222/255 benar**, coverage/accuracy **87,1%**, selective accuracy **100%**; POS kontekstual **223/255 benar**, coverage/accuracy **87,5%**, selective accuracy **100%**.
- [x] Gold ambiguous: 1 ditahan, 0 dipaksakan; tidak ada kesalahan pada prediksi yang dikeluarkan.

**Titik lanjut:** audit 8 kemunculan token VERB yang masih abstain pada development: `bekerja` (3), `ditunda`, `letakkan`, `menjelaskan`, `hinggap`, dan `berteduh`. Pisahkan kebutuhan metadata turunan, pola morfologi pasif/imperatif, dan lema dasar yang belum ada. Jangan gunakan 40 kalimat test untuk penyetelan.


### Verifikasi anotasi POS bentuk turunan — 27 November 2026

- [x] Menambahkan anotasi POS eksplisit untuk bentuk turunan `bekerja`, `menjelaskan`, `dijelaskan`, dan `letakkan` tanpa mewarisi POS lemma secara otomatis.
- [x] Menambahkan validasi dan regression tests untuk `derived_forms_pos`.
- [x] Pengguna menarik pembaruan ke Termux dan menjalankan seluruh pemeriksaan lokal.
- [x] Regression suite: **152/152 tes lulus**.
- [x] Validator: **100 kalimat, 543 token, 60 development, 40 test — BERHASIL**.
- [x] Evaluasi development-only: POS leksikal **227/255 benar (89,0%)**; POS kontekstual **228/255 benar (89,4%)**.
- [x] Selective accuracy kedua jalur **100%**, tanpa kesalahan prediksi yang dikeluarkan; satu gold ambiguous ditahan dan nol dipaksakan.
- [x] Sisa abstention VERB pada development turun menjadi **3 token**: `ditunda`, `hinggap`, dan `berteduh`.

**Catatan:** hasil di atas berasal dari eksekusi lokal pengguna, bukan klaim hasil GitHub Actions. Evaluasi hanya menggunakan 60 kalimat development. Empat puluh kalimat test tetap ditahan.

**Titik lanjut:** audit apakah lema `tunda`, `hinggap`, dan `teduh` tersedia di kamus, lalu audit abstention NOUN/ADJ/ADV secara terpisah. Jangan menambah aturan hanya untuk mengejar skor development dan jangan menggunakan test split untuk penyetelan.


### Audit indeks lema untuk sisa VERB — 27 November 2026

- [x] Memeriksa seluruh delapan shard token index (a-c sampai v-z) untuk tunda, hinggap, teduh, ditunda, dan berteduh.
- [x] Tidak ditemukan token persis tersebut pada indeks kamus saat ini.
- [x] Memeriksa aturan penyusunan kamus: batch baru harus berisi tepat 50 lema ber-ID berurutan; tidak membuat batch parsial hanya untuk tiga kata.
- [ ] Masukkan ketiga lema ke daftar kandidat batch kamus berikutnya setelah audit duplikasi dan penetapan POS/sense: tunda (VERB), hinggap (VERB), teduh (ADJ; bentuk berteduh perlu anotasi VERB eksplisit jika disetujui).
- [ ] Lanjutkan audit 19 abstention NOUN development untuk menyusun prioritas lema yang benar-benar dibutuhkan.

Catatan: ketidakhadiran pada token index adalah bukti gap indeks/kamus yang perlu ditindaklanjuti, bukan alasan untuk menebak bentuk turunan atau mengubah aturan morfologi. Split test tetap tidak digunakan.

### Audit dan koreksi relasi leksikal Batch-002 — 27 November 2026

- [x] Audit semantik read-only pada relasi Batch-002; ditemukan tujuh sinonim yang tidak setara secara makna atau merupakan bentuk turunan/perintah.
- [x] Menghapus relasi sinonim yang tidak tepat pada K0059 `taruh`, K0067 `masuk`, K0071 `duduk`, K0072 `berdiri`, K0073 `lari`, K0090 `dekat`, dan K0095 `bokek`. Tidak mengubah definisi, sense, POS, bentuk turunan, atau relasi lain.
- [ ] Menunggu validasi lokal Batch-002 dan regression suite setelah perubahan.

**Batas audit:** koreksi ini hanya menangani tujuh relasi yang disetujui; relasi lain yang memerlukan pembatasan konteks tetap menunggu audit terpisah.

### Audit dan koreksi relasi leksikal Batch-003 — 27 November 2026

- [x] Audit semantik baca-saja pada 51 entri Batch-003.
- [x] Setelah persetujuan, menghapus relasi antonim `anak`–`orang tua` serta `suami`–`istri`; mempertahankan hubungan sebagai `related_terms`.
- [x] Menghapus `kasih` dari sinonim `sayang` karena perbedaan fungsi kelas kata; mempertahankan hubungan makna sebagai `related_terms`.
- [ ] Validasi Batch-003 dan regression suite menunggu validasi kelompok Batch-001–005 melalui GitHub Actions.

**Batas audit:** hanya empat relasi yang disetujui yang diubah; kandidat lain yang memerlukan pembatasan konteks belum diubah.

### Audit dan koreksi relasi leksikal Batch-004 — 27 November 2026

- [x] Audit semantik baca-saja pada 50 entri Batch-004.
- [x] Menghapus `puas` sebagai antonim `haus` (K0177).
- [x] Memisahkan sense nomina dan verba pada `cerita` (K0191), lalu membatasi sinonim `kisah` pada sense nomina.
- [x] Memisahkan sense nomina dan verba pada `pesan` (K0194), lalu membatasi sinonim `amanat` pada sense nomina.
- [x] Menghapus `panggilan` dari sinonim `telepon` (K0195) karena tidak menjadi padanan untuk makna perangkat.
- [ ] Validasi Batch-004 dan regression suite menunggu validasi kelompok Batch-001–005 melalui GitHub Actions.

**Batas audit:** definisi dipisah hanya untuk memperjelas dua makna yang sebelumnya tergabung; perubahan tidak mengubah lemma, POS entri, bentuk turunan, atau relasi lain.

### Audit dan koreksi relasi leksikal Batch-005 — 27 November 2026

- [x] Audit semantik baca-saja pada 50 entri Batch-005.
- [x] Menghapus delapan sinonim yang merupakan bentuk turunan, bukan sinonim dasar: K0211 `belok`, K0215 `kenal`, K0216 `ketemu`, K0221 `ganti`, K0227 `ulang`, K0228 `coba`, K0241 `percaya`, dan K0246 `izin`.
- [x] Mempertahankan seluruh field selain delapan relasi tersebut.
- [ ] Validasi kelompok Batch-001–005 dan regression suite menunggu pemicu GitHub Actions.

**Batas audit:** koreksi ini memperbaiki klasifikasi relasi; tidak mengubah lemma, definisi, POS, sense, atau bentuk turunan.

### Validasi otomatis kelompok Batch-001–005 — 27 November 2026

- [x] GitHub Actions berhasil pada run `45931208148` setelah perbaikan format nomor batch tiga digit.
- [x] Validasi relasi leksikal: 5 batch, 250 entri; seluruh batch berhasil secara struktural.
- [x] Validasi dataset POS: 100 kalimat, 543 token; 60 development dan 40 test.
- [x] Evaluasi POS development: leksikal coverage/accuracy 89,0%; kontekstual 89,4%; selective accuracy 100%; tidak ada kesalahan prediksi pada development.
- [x] Regression suite: 169 tes lulus.

**Batas hasil:** validasi relasi bersifat struktural, bukan penilaian kebenaran makna. Evaluasi POS hanya pada development split; test split tetap ditahan dan bukan dasar klaim akurasi umum.


### Audit dan koreksi semantik Batch-006–010 — 27 November 2026

- [x] Audit baca seluruh 250 entri pada Batch-006 sampai Batch-010, dengan fokus pada kecocokan relasi sinonim/antonim terhadap definisi dan cakupan makna.
- [x] Batch-006: memindahkan `kaca rias` dari sinonim `cermin` ke `related_terms` karena merupakan jenis cermin yang lebih khusus; memisahkan dua makna `jam` (alat penunjuk waktu dan satuan 60 menit), lalu membatasi `penunjuk waktu` pada sense alat.
- [x] Batch-007: memindahkan `higienis` dari sinonim `bersih` ke `related_terms` karena higienis berkaitan dengan kebersihan tetapi tidak selalu berarti bebas dari kotoran/noda.
- [x] Batch-009: menghapus `lulus` sebagai antonim umum `gagal` dan mempertahankannya sebagai `related_terms`; antonim umum yang tepat adalah `berhasil`.
- [x] Batch-008 dan Batch-010: tidak ditemukan relasi yang cukup kuat untuk dikoreksi pada audit ini; data dipertahankan.
- [ ] Validasi struktural kelompok Batch-006–010 dan regression suite menunggu GitHub Actions.

**Batas audit:** empat koreksi relasi/struktur makna di atas tidak mengubah lemma, ID entri, POS entri, atau bentuk turunan. Relasi lain yang hanya berbeda nuansa/register tidak diubah tanpa bukti yang lebih kuat. Validasi otomatis nantinya hanya menguji struktur dan regresi, bukan menggantikan penilaian linguistik.


### Audit dan koreksi semantik Batch-011–015 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-011 sampai Batch-015; fokus pada kesepadanan sinonim/antonim dengan definisi lema.
- [x] Batch-011: memindahkan `berlebihan` dari sinonim `boros` ke `related_terms` karena cakupannya lebih luas daripada perilaku boros.
- [x] Batch-012: memindahkan `langka` dari sinonim `jarang` ke `related_terms` (frekuensi kejadian vs kelangkaan); memindahkan `keren sekali` dari sinonim `keren` ke `related_terms` karena merupakan bentuk intensifikasi; memindahkan `enggan` dari sinonim `malas` ke `related_terms` karena ketidakmauan tidak identik dengan kurang motivasi.
- [x] Batch-013: menghapus `andaikan` dari sinonim `andai` karena merupakan bentuk turunan/varian gramatikal, bukan padanan leksikal yang perlu dicatat sebagai sinonim.
- [x] Batch-014: menghapus `sabar` dari antonim `kesel`; kesabaran bukan lawan makna langsung dari rasa kesal.
- [x] Batch-015: memindahkan `tekad` dari sinonim `ambisi` ke `related_terms`; menghapus `untung` dari antonim `bangkrut`; menghapus `membelot` dari sinonim `belot` sebagai bentuk turunan; memindahkan `cerdas` dari sinonim `bijak` ke `related_terms`; memindahkan `merembes` dari sinonim `bocor` ke `related_terms` karena hanya mencakup jenis kebocoran tertentu.
- [x] Entri lain dipertahankan jika relasinya masih dapat dipertanggungjawabkan atau perbedaannya memerlukan konteks lebih lanjut.
- [ ] Validasi struktural kelompok Batch-011–015 dan regression suite menunggu GitHub Actions.

**Batas audit:** koreksi ini menyasar relasi leksikal; tidak mengubah lema, ID entri, POS, atau bentuk turunan. Pemeriksaan otomatis tetap bersifat struktural dan regresi, bukan bukti bahwa seluruh makna kamus telah tervalidasi secara linguistik.


### Audit dan koreksi semantik Batch-016–020 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-016 sampai Batch-020 dengan pemeriksaan relasi sinonim/antonim terhadap definisi dan kelas makna.
- [x] Batch-016: menghapus `memaafkan` dari antonim `dendam` (tindakan memaafkan bukan antonim leksikal langsung); memindahkan `terkenal` dari sinonim `eksis` ke `related_terms` (keberadaan tidak sama dengan popularitas); membatasi sinonim `ketertiban` pada sense nomina `disiplin` dan memisahkan antonim sense adjektiva menjadi `tidak disiplin`.
- [x] Batch-017: memindahkan `tolak` dari sinonim `dorong` ke `related_terms`; `tolak` dapat berarti menolak atau mendorong menjauh, sehingga bukan sinonim umum untuk gerakan mendorong.
- [x] Batch-018: menghapus `tenangkan` dari antonim `ganggu`; bentuk perintah/aksi menenangkan bukan antonim leksikal langsung dari verba mengganggu.
- [x] Batch-019: memindahkan `jarang` dari sinonim `langka` ke `related_terms`; frekuensi rendah dan kelangkaan tidak selalu saling menggantikan.
- [x] Batch-020: memindahkan `korban` dari sinonim `mangsa` ke `related_terms`; korban lebih luas dan tidak selalu merupakan sasaran buruan.
- [ ] Validasi struktural Batch-016–020 dan regression suite menunggu GitHub Actions.

**Batas audit:** selain koreksi yang dicatat, entri dipertahankan. Perubahan tidak mengubah lemma atau ID; penataan sense pada `disiplin` hanya membatasi relasi ke makna yang tepat. Validasi otomatis menguji struktur dan regresi, bukan menjamin seluruh isi semantik kamus.


### Audit dan koreksi semantik Batch-021–025 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-021 sampai Batch-025.
- [x] Batch-021: memindahkan `lezat` dari sinonim `nikmat` ke `related_terms` karena maknanya lebih khusus pada rasa makanan; memindahkan `mekanis` dari sinonim `otomatis` ke `related_terms` karena cara kerja mekanis tidak selalu otomatis.
- [x] Batch-022: memindahkan `tersembunyi` dari sinonim `rahasia` ke `related_terms`; sesuatu yang rahasia tidak selalu tersembunyi secara fisik.
- [x] Batch-023: memindahkan `mantap` dari sinonim `tegas` ke `related_terms`; mantap dapat bermakna stabil/yakin, bukan selalu tegas dalam mengambil sikap.
- [x] Batch-024: memindahkan `kalah` dari antonim `unggul` ke `related_terms`; unggul (lebih baik/kuat) tidak selalu beroposisi langsung dengan hasil kalah.
- [x] Batch-025: memindahkan `menyerang` dari sinonim `agresif` ke `related_terms`; agresif adalah sifat/kecenderungan, sedangkan menyerang adalah tindakan.
- [ ] Validasi struktural Batch-021–025 dan regression suite menunggu GitHub Actions.

**Batas audit:** relasi lain dipertahankan jika masih dapat dibenarkan berdasarkan definisi yang tersedia. Perubahan hanya pada relasi leksikal; lemma dan ID tidak diubah. Validasi otomatis memeriksa struktur dan regresi, bukan membuktikan seluruh makna kamus.


### Audit dan koreksi semantik Batch-026–030 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-026 sampai Batch-030.
- [x] Batch-026: memindahkan `olok-olok` dari sinonim `ejek` ke `related_terms`; bentuk nomina tersebut bukan padanan langsung verba.
- [x] Batch-027: memindahkan `buas` dari sinonim `galak` ke `related_terms` karena buas menekankan sifat liar/ganas; memindahkan `ilustrasi` dari sinonim `gambaran` ke `related_terms` karena ilustrasi tidak selalu berupa uraian atau bayangan.
- [x] Batch-028: tidak ditemukan koreksi relasi yang cukup pasti; seluruh entri dipertahankan.
- [x] Batch-029: memindahkan `dilahirkan` dari sinonim `lahir` ke `related_terms` (bentuk pasif/kausatif); memindahkan `layani` dari sinonim `layan` ke `related_terms` (bentuk turunan/perintah); memindahkan `buang` dari sinonim `lempar` ke `related_terms` (membuang memiliki makna membuang sesuatu, tidak sekadar melontarkan); memperbaiki relasi `licin`: menghapus entri salah ketik `kesat?` dan sinonim terlalu luas `halus`, mengganti antonim `kasar` dengan `kesat`.
- [x] Batch-030: memindahkan `berisi` dari sinonim `muat` ke `related_terms`; kemampuan menampung tidak sama dengan keadaan sudah berisi.
- [ ] Validasi struktural Batch-026–030 dan regression suite menunggu GitHub Actions.

**Batas audit:** perubahan hanya menyentuh relasi leksikal; lemma dan ID tetap. Batch-028 lulus audit manual tanpa perubahan. Validasi otomatis menguji struktur dan regresi, bukan keseluruhan ketepatan semantik kamus.


### Audit dan koreksi semantik Batch-031–035 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-031 sampai Batch-035.
- [x] Batch-031: memindahkan `terkenal` dari sinonim `populer` ke `related_terms`; dikenal luas tidak selalu berarti disukai banyak orang.
- [x] Batch-032: tidak ditemukan koreksi relasi yang cukup pasti; seluruh entri dipertahankan.
- [x] Batch-033: memindahkan `mengisap` dari sinonim `serap` ke `related_terms` (mengisap adalah salah satu cara menarik cairan, tidak identik dengan penyerapan); memindahkan `mengusir` dari sinonim `singkir` ke `related_terms` (mengusir khususnya mengeluarkan pihak/orang, sedangkan menyingkir lebih luas).
- [x] Batch-034: memindahkan `genting` dari sinonim `tegang` ke `related_terms`; keadaan genting adalah keadaan kritis/darurat, bukan padanan umum dari tegang.
- [x] Batch-035: memindahkan `kurus` dari sinonim `tipis` ke `related_terms` (bentuk tubuh vs ukuran ketebalan); memindahkan `menyangka` dari sinonim `tuduh` ke `related_terms` (dugaan tidak selalu berupa tuduhan); memindahkan `menimbun` dari sinonim `tumpuk` ke `related_terms` (menimbun memiliki nuansa mengumpulkan/menyimpan banyak).
- [ ] Validasi struktural Batch-031–035 dan regression suite menunggu GitHub Actions.

**Batas audit:** relasi yang masih dapat dipertanggungjawabkan dipertahankan; batch yang tidak memiliki temuan pasti tidak diubah. Perubahan hanya pada relasi leksikal, tanpa mengganti lemma atau ID. Validasi otomatis tidak menggantikan penilaian semantik menyeluruh.


### Audit dan koreksi semantik Batch-036–040 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-036 sampai Batch-040.
- [x] Batch-036: tidak ditemukan koreksi relasi yang cukup pasti; seluruh entri dipertahankan.
- [x] Batch-037: memindahkan `permulaan` dari sinonim `awal` ke `related_terms`; lema `awal` dianotasi sebagai adjektiva, sedangkan `permulaan` merupakan nomina sehingga tidak tepat sebagai sinonim langsung tanpa penyesuaian POS.
- [x] Batch-038: memindahkan `rancangan` dari sinonim `denah` ke `related_terms`; rancangan lebih luas daripada gambar tata letak tempat. Memindahkan `peduli` dari antonim `egois` ke `related_terms`; antonim yang lebih langsung adalah `altruistis`, sedangkan peduli tidak selalu berlawanan dengan mementingkan diri sendiri.
- [x] Batch-039: tidak ditemukan relasi sinonim/antonim yang perlu dikoreksi; seluruh entri dipertahankan.
- [x] Batch-040: tidak ditemukan relasi sinonim/antonim yang perlu dikoreksi; seluruh entri dipertahankan.
- [ ] Validasi struktural Batch-036–040 dan regression suite menunggu GitHub Actions.

**Batas audit:** hanya tiga relasi yang diubah berdasarkan perbedaan kelas kata atau cakupan makna yang jelas. Entri lain dipertahankan. Validasi otomatis menguji struktur dan regresi, bukan menjamin seluruh makna kamus telah sempurna.


### Audit Batch-041–045 — 27 November 2026

- [x] Memeriksa seluruh 250 entri Batch-041 sampai Batch-045 beserta lemma, POS, dan definisi sense.
- [x] Batch-041–045: tidak ada field relasi `synonyms` atau `antonyms` pada entri yang diperiksa. Karena itu tidak ada relasi salah yang dapat dikoreksi pada kelompok ini; tidak dibuat sinonim/antonim tebakan hanya untuk mengisi kekosongan.
- [x] Tidak mengubah isi batch. Catat bahwa hasil ini adalah audit cakupan anotasi relasi, bukan bukti bahwa definisi setiap entri sudah tervalidasi secara leksikografis.
- [ ] Validasi struktural Batch-041–045 dan regression suite menunggu GitHub Actions.

**Catatan kualitas:** kelompok ini memuat 250 lema dengan definisi sense, tetapi belum memiliki anotasi sinonim/antonim. Kekosongan anotasi harus diperlakukan sebagai coverage gap, bukan kesalahan validasi atau relasi yang sudah benar.


### Audit Batch-046–050 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-046 sampai Batch-050, termasuk pemeriksaan anotasi relasi dan cakupan related_terms.
- [x] Batch-046: 50 entri; seluruhnya memiliki related_terms; tidak ada synonyms/antonyms pada tingkat entri maupun sense.
- [x] Batch-047: 50 entri; seluruhnya memiliki related_terms; tidak ada synonyms/antonyms pada tingkat entri maupun sense.
- [x] Batch-048: 50 entri; seluruhnya memiliki related_terms; tidak ada synonyms/antonyms pada tingkat entri maupun sense.
- [x] Batch-049: 50 entri; seluruhnya memiliki related_terms; tidak ada synonyms/antonyms pada tingkat entri maupun sense.
- [x] Batch-050: 50 entri; seluruhnya memiliki related_terms; tidak ada synonyms/antonyms pada tingkat entri maupun sense.
- [x] Tidak ditemukan koreksi related_terms yang cukup pasti dalam pemeriksaan kelompok ini; tidak menambahkan sinonim/antonim tebakan.
- [ ] Validasi struktural Batch-046–050 dan regression suite menunggu GitHub Actions.

**Catatan kualitas:** kelompok ini memiliki cakupan related_terms pada seluruh 250 entri, tetapi belum memiliki anotasi sinonim/antonim. Ini dicatat sebagai coverage gap untuk relasi sinonim/antonim, bukan kegagalan struktur atau bukti bahwa relasi tersebut tidak ada dalam bahasa.


### Audit Batch-051–055 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-051 sampai Batch-055, termasuk definisi sense dan related_terms.
- [x] Batch-051: 50 entri diperiksa; tidak ditemukan salah relasi yang cukup pasti untuk diubah.
- [x] Batch-052: 50 entri diperiksa; koreksi satu salah ketik pada K2561 `pikap`: `kabina` menjadi `kabin`.
- [x] Batch-053: 50 entri diperiksa; tidak ditemukan salah relasi yang cukup pasti untuk diubah.
- [x] Batch-054: 50 entri diperiksa; tidak ditemukan salah relasi yang cukup pasti untuk diubah.
- [x] Batch-055: 50 entri diperiksa; tidak ditemukan salah relasi yang cukup pasti untuk diubah.
- [ ] Validasi struktural Batch-051–055 dan regression suite menunggu GitHub Actions.

**Catatan kualitas:** koreksi pada kelompok ini terbatas pada typo yang jelas. Related terms lain dipertahankan ketika masih masuk akal sebagai keterkaitan topik atau konsep; tidak dipaksakan menjadi sinonim/antonim.


### Audit penutup Batch-056–060 — 27 November 2026

- [x] Audit seluruh 250 entri Batch-056 sampai Batch-060, termasuk definisi dan kecocokan related_terms.
- [x] Batch-056: koreksi 4 entri geografis yang jelas salah lokasi: K2781 Gunung Tambora (Pulau Lombok → Pulau Sumbawa); K2791 Gunung Mutis (Pulau Flores → Pulau Timor); K2798 Gunung Salak (Pegunungan Bukit Barisan diganti Jawa Barat dan Taman Nasional Gunung Halimun Salak); K2800 Gunung Tangkuban Parahu (Pulau Bali → Jawa Barat).
- [x] Batch-057: koreksi relasi administratif yang salah kategori: K2802–K2806 (kota administrasi Jakarta, hapus bupati); K2807 (Kabupaten Administrasi Kepulauan Seribu, hapus wali kota).
- [x] Batch-058: 50 entri diperiksa; tidak ditemukan koreksi relasi yang cukup pasti.
- [x] Batch-059: 50 entri diperiksa; tidak ditemukan koreksi relasi yang cukup pasti.
- [x] Batch-060: 50 entri diperiksa; tidak ditemukan koreksi relasi yang cukup pasti.
- [ ] Validasi struktural Batch-056–060 dan regression suite menunggu GitHub Actions.

**Catatan kualitas:** 10 entri pada Batch-056–057 diperbaiki berdasarkan ketidakcocokan geografis atau kategori pemerintahan yang eksplisit. Batch-058–060 dipertahankan. Audit ini tidak menggantikan validasi faktual menyeluruh atas seluruh definisi dan relasi.


### Parser kalimat v0.4 — frasa verba modal

- [x] Membedakan verba kehendak `mau`, `ingin`, dan `hendak` dari verba leksikal ketika keduanya hadir berurutan.
- [x] Menggabungkan verba kehendak dan verba leksikal ke dalam rentang predikat.
- [x] Mempertahankan penggunaan verba kehendak tunggal sebagai predikat jika tidak diikuti verba lain.
- [x] Menambahkan tiga regression tests untuk konstruksi modal dan penggunaan tunggal.
- [x] GitHub Actions Run #78: **190/190 tes lulus**; validasi 5 batch, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.
- [ ] Memperluas modalitas lain hanya setelah kelas kata dan perilakunya diverifikasi melalui kamus/pipeline.


### Parser kalimat v0.5 — predikat nonverbal sederhana

- [x] Mengenali predikat adjektival pada pola berpenanda subjek yang cukup jelas, misalnya pronomina atau demonstrativa.
- [x] Mengenali pola predikat nominal sederhana dengan penanda numeralia, misalnya `Ayah seorang guru`.
- [x] Menahan pola nomina-adjektiva yang ambigu, misalnya `rumah besar`, sebagai unresolved.
- [x] Menambahkan empat regression tests untuk predikat adjektival, nominal, dan abstention.
- [x] Memverifikasi predikat adjektival `Dia sakit` dan `Rumah itu besar` melalui kamus, POS tagger, disambiguasi konteks, dan parser end-to-end.
- [x] Menambahkan dua tes integrasi pipeline nyata; total suite menjadi **196 tes**.
- [x] GitHub Actions Run #81: **196/196 tes lulus**; validasi lima batch, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.
- [ ] Mengembangkan dan menguji konstruksi pelengkap predikat setelah desain peran sintaksisnya ditetapkan.


### Parser kalimat v0.6 — pelengkap predikat terbatas

- [x] Membedakan pelengkap nominal setelah verba penghubung `menjadi` dari objek.
- [x] Membedakan pelengkap adjektival setelah verba penghubung `tampak` dari objek.
- [x] Menggunakan label pola `S-P-Pel` dan mengisi field `roles.complement`.
- [x] Mempertahankan objek pada verba transitif biasa; diuji dengan `Dia membeli baju`.
- [x] Menambahkan tiga regression tests; GitHub Actions Run #82: **199/199 tes lulus**.
- [ ] Menguji `menjadi` dan `tampak` melalui pipeline kamus/POS nyata setelah dukungan leksikal dan kelas katanya diverifikasi.
- [ ] Memperluas pelengkap ke verba/konstruksi lain hanya setelah bukti linguistik dan tes tersedia.

**Batas implementasi:** aturan ini sengaja hanya mencakup dua verba dan pelengkap nominal/adjektival sederhana. Frasa adverbial, klausa pelengkap, dan konstruksi lain belum dimodelkan.


### Verifikasi cakupan leksikal pelengkap — 27 November 2026

- [x] Memastikan `tampak` dikenali sebagai VERB melalui varian kamus dari lema `nampak`.
- [x] Memastikan `menjadi` belum tersedia sebagai lema/varian/bentuk turunan yang cocok dalam cakupan kamus saat ini; pipeline tidak menebak POS-nya.
- [x] Memastikan `bahagia` belum memiliki kecocokan leksikal langsung yang memberi POS; parser menandai token tersebut unresolved, bukan pelengkap hasil tebakan.
- [x] Menambahkan dua tes integrasi: abstention untuk `Dia menjadi dokter` dan parsing parsial aman untuk `Mereka tampak bahagia`.
- [x] GitHub Actions Run #84: **201/201 tes lulus**, validasi kamus 3.000 lema dan evaluasi POS tetap lulus.
- [ ] Pertimbangkan perluasan kosakata sebagai perubahan cakupan dataset terpisah; jangan menyisipkan lema tambahan tanpa keputusan target dataset dan definisi/POS yang tervalidasi.

**Catatan:** ketiadaan kecocokan untuk `menjadi` dan `bahagia` adalah celah cakupan leksikal, bukan kerusakan parser. Bentuk `tampak` dapat dipetakan ke lema `nampak` melalui varian kamus.


### Parser kalimat v0.7 — keterangan preposisional di depan subjek

- [x] Mengenali keterangan berpreposisi sederhana yang ditempatkan sebelum subjek, misalnya `Di rumah aku bekerja.`.
- [x] Memisahkan frasa preposisional awal dari frasa subjek agar `rumah` tidak keliru dimasukkan ke subjek `aku`.
- [x] Mempertahankan keterangan preposisional setelah predikat seperti pada `Aku bekerja di rumah.`.
- [x] Menambahkan dua tes unit dan satu tes integrasi melalui kamus asli.
- [x] GitHub Actions Run #87: **204/204 regression tests lulus**; validasi 5 batch, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas implementasi:** hanya keterangan awal berbentuk PREP + frasa nominal sederhana yang selesai tepat sebelum subjek. Inversi, klausa majemuk, dan susunan kompleks tetap di luar cakupan.


### Parser kalimat v0.8 — beberapa keterangan preposisional di depan subjek

- [x] Mengenali rangkaian beberapa keterangan sederhana sebelum subjek, misalnya `Di rumah pada malam hari aku bekerja.`.
- [x] Mempertahankan urutan keterangan sesuai kemunculannya dalam kalimat.
- [x] Hanya menerima rangkaian awal jika seluruh bagian sebelum subjek dapat dipetakan sebagai PREP + frasa nominal; awalan yang tidak cocok tetap unresolved.
- [x] Menambahkan satu tes unit dan satu tes integrasi melalui kamus asli.
- [x] GitHub Actions Run #88: **206/206 regression tests lulus**; validasi 5 batch, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas implementasi:** keterangan depan yang dipisahkan tanda baca, klausa bertingkat, dan susunan campuran yang tidak cocok dengan pola konservatif belum diparse.


### Parser kalimat v0.9 — koordinasi frasa nominal sederhana

- [x] Mengenali subjek nominal yang dikoordinasikan dengan konjungsi eksplisit, misalnya `Aku dan dia bekerja.`.
- [x] Mengenali objek nominal yang dikoordinasikan, misalnya `Aku membeli nasi dan roti.`.
- [x] Tidak menganggap konjungsi sebagai bagian frasa jika unsur nominal di kedua sisinya tidak teridentifikasi.
- [x] Menambahkan dua tes unit dan satu tes integrasi melalui kamus asli.
- [x] GitHub Actions Run #89: **209/209 regression tests lulus**; validasi 5 batch, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas implementasi:** koordinasi hanya diperluas untuk frasa nominal sederhana dengan konjungsi yang dikenali POS sebagai CONJ. Koordinasi klausa penuh, elipsis, dan konstruksi bertingkat belum didukung.


### Parser kalimat v1.0 — dua klausa koordinatif sederhana

- [x] Memisahkan dua segmen klausa jika satu konjungsi teridentifikasi sebagai CONJ dan masing-masing sisi memiliki VERB teridentifikasi.
- [x] Menganalisis setiap klausa secara terpisah menggunakan parser konservatif yang sudah ada.
- [x] Mempertahankan koordinasi frasa nominal v0.9; tidak memecah `Aku dan dia bekerja` atau `Aku membeli nasi dan roti` menjadi dua klausa.
- [x] Menambahkan tiga tes unit dan satu tes integrasi melalui kamus asli.
- [x] GitHub Actions Run #90: **213/213 regression tests lulus**; validasi relasi lima batch terpilih, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas implementasi:** satu konjungsi dan dua klausa eksplisit. Koordinasi bertingkat, elipsis/subjek yang dihilangkan, relasi semantik antarklausa, dan pemisahan berbasis koma belum didukung.


### Parser kalimat v1.1 — koordinasi tiga klausa atau lebih

- [x] Memisahkan beberapa klausa secara berurutan jika setiap segmen di antara konjungsi eksplisit memiliki verba teridentifikasi.
- [x] Menyimpan konjungsi masing-masing sebagai penghubung klausa berikutnya.
- [x] Mempertahankan perilaku dua klausa v1.0 dan koordinasi frasa nominal v0.9.
- [x] Menolak pemisahan jika salah satu segmen tidak memiliki verba; parser kembali ke analisis satu klausa konservatif.
- [x] Menambahkan tiga tes unit dan satu tes integrasi tiga klausa melalui kamus asli.
- [x] GitHub Actions Run #91: **217/217 regression tests lulus**; validasi lima batch terpilih, kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas implementasi:** setiap klausa harus memiliki verba eksplisit yang dikenali. Elipsis, subjek/predikat yang dihilangkan, koordinasi bertingkat, dan relasi semantik antarklausa belum ditangani.

### Parser kalimat v1.2 — klasifikasi hubungan antarklausa

- [x] Menambahkan field `relation_to_previous` pada hasil setiap klausa setelah klausa pertama.
- [x] Mengklasifikasikan penghubung eksplisit untuk penambahan, alternatif, pertentangan, sebab, konsesi, urutan, dan hubungan temporal.
- [x] Menandai penghubung yang belum dipetakan sebagai `belum_diklasifikasikan`; tidak menebak relasi.
- [x] Menambahkan empat tes unit untuk sebab, pertentangan, konsesi, dan penghubung tak dikenal.
- [x] Menambahkan tes integrasi `Aku bekerja namun dia makan.` melalui kamus asli.
- [x] GitHub Actions Run #93: **222/222 regression tests lulus**; validasi kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas:** klasifikasi penghubung bukan pemahaman semantik lengkap. Sebab dan konsesi masih diuji dengan POS terkendali; arah hubungan, klausa awal bertanda `karena`, konstruksi bertanda koma, elipsis, dan klausa tanpa verba eksplisit belum didukung.

### Parser kalimat v1.3 — klausa subordinatif awal

- [x] Mengenali pola penghubung subordinatif + klausa awal berverba + koma + klausa utama.
- [x] Menyimpan analisis kedua klausa secara terpisah dan menandai relasi pada klausa subordinatif awal.
- [x] Menguji relasi sebab `Karena dia makan, aku pulang.` melalui kamus asli.
- [x] Menguji relasi temporal `Ketika dia makan, aku pulang.` melalui kamus asli.
- [x] Memastikan klausa eliptis `Walaupun lelah` tidak dipaksakan menjadi klausa lengkap.
- [x] GitHub Actions Run #96: **227/227 regression tests lulus**; validasi kamus 3.000 lema, dataset POS, dan evaluasi development berhasil.

**Batas:** hanya satu klausa subordinatif awal dengan predikat teridentifikasi dan satu koma pemisah. Klausa eliptis, subordinasi bertingkat, dan beberapa klausa awal belum didukung.


### Parser kalimat v1.4 — elipsis konsesif adjektival terbatas

- [x] Mengenali predikat adjektival eksplisit pada klausa konsesif awal seperti `Walaupun lelah, dia bekerja.`.
- [x] Membiarkan subjek klausa eliptis kosong; tidak menyalin atau menebak subjek dari klausa utama.
- [x] Menandai hasil sebagai `partial`, bukan `parsed`.
- [x] Menolak awalan yang tidak berakhir pada predikat adjektival teridentifikasi.
- [x] Menambahkan tes unit dan integrasi melalui kamus asli untuk `lelah` (ADJ).
- [ ] Menangani jenis elipsis lain hanya setelah pola dan bukti leksikalnya dapat dibatasi secara aman.

- [x] GitHub Actions Run #97: **229/229 regression tests lulus**; validasi kamus 60 batch/3.000 lema, dataset POS, evaluasi development, dan validasi relasi batch terpilih berhasil.


### Parser kalimat v1.5 — subordinasi setelah klausa utama

- [x] Mengenali pola klausa utama + penghubung subordinatif + klausa bawahan.
- [x] Memisahkan pola sebab dan temporal sebelum aturan koordinasi agar tidak salah diklasifikasikan sebagai klausa setara.
- [x] Menyimpan relasi pada batas kedua klausa dengan label eksplisit.
- [x] Menambahkan tes unit sebab/temporal dan tes integrasi sebab melalui kamus asli.
- [ ] Memperluas subordinasi bertingkat atau klausa eliptis akhir hanya jika analisis dapat dibatasi secara aman.

- [x] GitHub Actions Run #99: **232/232 regression tests lulus**; validasi kamus 60 batch/3.000 lema, dataset POS, evaluasi development, dan validasi relasi batch terpilih berhasil.


## Prioritas aktif — kembali ke Tahap 2.5 (27 November 2026)

Parser kalimat v1.5 dan seluruh tes yang sudah dibuat tetap dipertahankan, tetapi **pengembangan parser dihentikan sementara** sampai evaluasi POS development dinilai memadai. Jangan memulai fitur parser baru pada tahap ini.

### Urutan pekerjaan POS

- [ ] Audit token VERB abstain satu per satu: `bekerja` (3 kemunculan), `ditunda`, `letakkan`, `menjelaskan`, `hinggap`, dan `berteduh` (8 kemunculan total).
- [ ] Untuk setiap kasus, identifikasi apakah kebutuhan sebenarnya adalah lema baru, aturan morfologi, anotasi `derived_forms_pos`, atau perbaikan alur POS. Jangan menambah data/aturan sebelum penyebabnya terbukti.
- [ ] Setelah satu kasus diperiksa dan diperbaiki bila perlu, jalankan tes terkait sebelum melanjutkan ke kasus berikutnya.
- [ ] Setelah VERB, audit abstention ADJ (2), ADV (3), dan NOUN (19) secara bertahap.
- [ ] Perluas cakupan lema NOUN yang belum terindeks.
- [ ] Audit pola morfologi bentuk `ber-`, pasif `di-`, dan imperatif.
- [ ] Evaluasi ulang POS menggunakan development split dan regresi penuh; dokumentasikan hasil dan batasannya.
- [ ] Pertahankan test set sebagai data evaluasi akhir; jangan membukanya untuk penyetelan.

### Tahap berikutnya — belum dimulai

- [ ] Tahap 2.6 — analisis struktur kalimat dasar.
- [ ] Tahap 2.7 — dataset dan pengujian terpadu.
- [ ] Tahap 3 — hubungan makna dan konteks.
- [ ] Tahap 5 — integrasi Android.

**Catatan urutan:** parser v1.5 adalah pekerjaan terdahulu yang tetap tersimpan, bukan alasan untuk melompati prasyarat POS. Tidak ada audit ulang batch kamus secara rutin; fokus saat ini adalah diagnosis abstention dan kesiapan POS.


### Koreksi titik lanjut POS — hasil evaluasi GitHub Actions Run #99

Daftar delapan kemunculan pada catatan historis di atas sudah tidak seluruhnya merupakan abstention aktif. Evaluasi terbaru pada 60 kalimat development menunjukkan **tiga VERB abstain**, yaitu `ditunda`, `hinggap`, dan `berteduh`. Tiga kemunculan `bekerja` sudah teridentifikasi sebagai VERB; demikian juga `menjelaskan` dan `letakkan` pada data development yang diuji.

- [x] `bekerja` (3 kemunculan): sudah memiliki anotasi `derived_forms_pos` pada lema `kerja` dan tidak lagi muncul dalam daftar abstention Run #99.
- [x] `menjelaskan` dan `letakkan`: bentuk turunan berlabel VERB dan lulus tes pipeline kamus penuh.
- [x] `ditunda`: lema `tunda` dan anotasi bentuk turunan `ditunda` VERB sudah ditambahkan; tes integrasi lulus.
- [ ] `hinggap`.
- [ ] `berteduh`.

Bukti: Run #99 mencatat VERB development `NO_PREDICTION: 3` dan menampilkan hanya `ditunda`, `hinggap`, `berteduh` sebagai abstention. Tiga kemunculan `bekerja` berada pada `pos_0005`, `pos_0025`, dan `pos_0052` (semuanya development). Jangan mengaudit ulang atau mengubah kasus yang sudah selesai tanpa bukti masalah baru.


### POS Tahap 2.5 — kasus `ditunda` selesai

- [x] Verifikasi seluruh 60 batch sumber: lema `tunda` sebelumnya belum tersedia.
- [x] Tambahkan lema `tunda` (VERB) sebagai K3002 pada batch-060.
- [x] Catat `ditunda` sebagai `derived_forms` dengan anotasi eksplisit `derived_forms_pos: {"ditunda":["VERB"]}`; aturan pasif `di-` umum tidak diubah.
- [x] Perbarui indeks lema dan target validasi kamus menjadi 3.001 entri.
- [x] Tambahkan tes integrasi `Karena hujan deras, pertandingan ditunda.` untuk memastikan POS VERB berasal dari kamus.
- [x] GitHub Actions Run #101: validasi 60 batch/3.001 lema dan regresi 233/233 berhasil.


### Verifikasi `ditunda` — GitHub Actions Run #101

- [x] Validasi kamus lengkap: 60 batch, 3.001 lema.
- [x] Tes integrasi `ditunda` sebagai VERB melalui kamus.
- [x] Regresi penuh: 233/233 tes lulus.
- [x] Evaluasi development: abstention VERB tersisa dua, yaitu `hinggap` dan `berteduh`; test set tetap tidak digunakan.


### POS Tahap 2.5 — `hinggap` selesai (Run #102)

- [x] Pemeriksaan indeks: `hinggap` belum tercatat.
- [x] Tambahkan lema K3003 `hinggap` dengan POS VERB pada batch-060.
- [x] Tambahkan baris lema ke indeks `g-i.tsv`.
- [x] Tes integrasi melalui kalimat development `Burung hinggap pada pagar.`
- [x] Validasi penuh: 60 batch, 3.002 lema.
- [x] Regresi penuh: 234/234 tes lulus.
- [x] Abstention VERB development tersisa satu: `berteduh`.


### POS Tahap 2.5 — `berteduh` selesai (Run #103)

- [x] Pemeriksaan indeks: `berteduh` dan lema dasar `teduh` tidak tercatat.
- [x] Tambahkan lema K3004 `berteduh` dengan POS VERB pada batch-060.
- [x] Tambahkan baris lema ke indeks `a-c.tsv`.
- [x] Tes integrasi melalui kalimat development `Ketika hujan turun, mereka berteduh.`
- [x] Validasi penuh: 60 batch, 3.003 lema.
- [x] Regresi penuh: 235/235 tes lulus.
- [x] Abstention VERB development: 0.


### POS Tahap 2.5 — `baru` selesai (Run #104)

- [x] Pemeriksaan INDEX: `baru` belum tercatat; `barusan` merupakan lema berbeda.
- [x] Tambahkan K3005 `baru` sebagai ADJ berdasarkan dua konteks frasa nominal pada development.
- [x] Tambahkan ke INDEX `a-c.tsv`.
- [x] Tes dua konteks atributif: `buku baru`.
- [x] Validasi penuh: 60 batch, 3.004 lema; regresi 236/236 lulus.
- [x] Evaluasi development: tidak ada abstention ADJ secara kontekstual; tidak ada kesalahan prediksi.


### POS Tahap 2.5 — lema `dulu` disetujui dan ditambahkan (K3006)

- [x] Persetujuan pengguna diperoleh sebelum perubahan kamus.
- [x] Pemeriksaan INDEX: `dulu` belum tercatat; `duluan` adalah lema berbeda.
- [x] Tambahkan `dulu` sebagai ADV dengan definisi temporal dan urutan tindakan sesuai persetujuan.
- [x] Tambahkan baris lema pada INDEX `d-f.tsv`.
- [x] Tes integrasi untuk `Gue mau makan dulu.` dan `Dulu dia tinggal di sini.`.
- [x] GitHub Actions Run #105: validasi 60 batch/3.005 lema dan regresi 237/237 berhasil.
- [x] Evaluasi development: ADV tersisa dua abstention, keduanya `tetap`; `dulu` berhasil dikenali. NOUN masih 19 abstention.


### POS Tahap 2.5 — lema `tetap` disetujui dan ditambahkan (K3007)

- [x] Persetujuan pengguna diperoleh sebelum perubahan kamus.
- [x] Pemeriksaan INDEX: `tetap` belum tercatat.
- [x] Tambahkan satu lema dengan POS entri ADJ dan ADV; dua sense diberi POS masing-masing agar makna adjektival dan adverbial tidak tercampur.
- [x] Tambahkan baris lema pada INDEX `s-u.tsv`.
- [x] Konteks `tetap` sebelum VERB dapat memilih ADV; konteks yang belum cukup jelas tetap abstain.
- [x] Tes integrasi mencakup `pegawai tetap` (ambigu tetap dipertahankan) dan `mereka tetap bekerja` (ADV dipilih oleh konteks).
- [x] GitHub Actions Run #108: validasi 60 batch/3.006 lema, evaluasi development, dan regresi 239/239 tes berhasil.
