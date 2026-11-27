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

### Rancangan relasi leksikal per-sense

- [x] Membuat dokumen rancangan kompatibilitas relasi per-sense di `docs/RELASI_LEKSIKAL_PER_SENSE.md`; belum mengubah data kamus atau kode.
- [ ] Meninjau dan menetapkan rancangan field relasi opsional pada setiap sense.
- [x] Menambahkan modul validator struktur relasi per-sense dan 11 regression tests; verifikasi Termux: 11/11 tes khusus lulus, `batch-001.jsonl` (49 entri) lolos validasi struktur, dan regression suite penuh 168/168 lulus pada 27 November 2026.
- [ ] Menguji kompatibilitas dengan seluruh bentuk data lama tanpa migrasi batch.
- [ ] Menentukan kebutuhan pembaca relasi per-sense pada komponen mesin makna sebelum implementasi runtime.
- [ ] Menerapkan anotasi per-sense hanya pada entri yang sudah diaudit dan memiliki bukti linguistik.

### Audit kualitas isi kamus — bertahap per batch

- [ ] Audit isi `batch-001.jsonl` sampai `batch-060.jsonl` satu batch pada satu waktu; catat temuan sebelum berpindah batch.
- [ ] Pisahkan audit baca-saja dari tahap perbaikan; jangan mengubah data selama audit.
- [ ] Tinjau temuan berdasarkan bukti dan dampak; perbaiki hanya kesalahan yang terkonfirmasi.
- [ ] Jalankan validator dan regression tests yang relevan setelah setiap kelompok perbaikan.
- [ ] Catat hasil setiap batch dan tandai batch selesai hanya setelah pemeriksaan serta verifikasi benar-benar dilakukan.

#### Verifikasi struktur relasi leksikal

- [x] `batch-001.jsonl`: 49 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-002.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-003.jsonl`: 51 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-004.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-005.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-006.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-007.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-008.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-009.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-010.jsonl`: 50 entri; validator struktur relasi berhasil di Termux pada 27 November 2026.
- [x] `batch-011.jsonl`: 50 entri; dua referensi diri pada K0520 `awas` dan K0531 `bersin` diperbaiki; validator struktur relasi berhasil dijalankan ulang di Termux pada 27 November 2026.
- [x] `batch-012.jsonl`: 50 entri; dua referensi diri pada K0568 `jengkel` dan K0574 `keren` diperbaiki; validator struktur relasi berhasil dijalankan ulang di Termux pada 27 November 2026.
- [x] `batch-013.jsonl`: 50 entri; referensi diri pada K0608 `barangkali` dan K0645 `yuk` diperbaiki; validator struktur relasi berhasil dijalankan ulang di Termux pada 27 November 2026.
- [x] `batch-014.jsonl`: 50 entri; lima referensi diri pada K0656 `doang`, K0661 `kayaknya`, K0672 `percaya diri`, K0692 `sungkan`, dan K0693 `terpaksa` diperbaiki; validator struktur relasi berhasil dijalankan ulang di Termux pada 27 November 2026.
- [x] `batch-015.jsonl`: 50 entri; lima referensi diri pada K0720 `bandel`, K0735 `biadab`, K0741 `boncos`, K0748 `canggung`, dan K0750 `cerewet` diperbaiki; validator struktur relasi berhasil dijalankan ulang di Termux pada 27 November 2026.
- [x] `batch-016.jsonl`: 50 entri; tiga referensi diri pada K0755 `ceroboh`, K0762 `dahaga`, dan K0764 `dalih` diperbaiki; validator struktur relasi berhasil dijalankan ulang di Termux pada 27 November 2026.
- [x] `batch-017.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-018.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-019.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-020.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-021.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-022.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-023.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-024.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-025.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-026.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [x] `batch-027.jsonl`: 50 entri; pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; validator struktur relasi berhasil dijalankan di Termux pada 27 November 2026.
- [ ] `batch-028.jsonl`: pemeriksaan awal tidak menemukan ID/lemma ganda atau referensi diri; menunggu verifikasi validator struktur relasi di Termux.
- [ ] Lanjutkan validasi struktur batch berikutnya satu per satu; hasil validasi struktur tidak dianggap sebagai audit kebenaran makna.

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
- [ ] Mencocokkan seluruh baris index dengan sumber 60 batch JSONL secara bertahap; audit internal index saja belum membuktikan kesesuaian dengan batch.
- [~] Menyiapkan `tools/audit_index_kamus.py` untuk mencocokkan index dengan sumber secara streaming satu batch per giliran; regression tests telah ditambahkan dan menunggu verifikasi lokal.
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
- [ ] Memperluas dataset secara bertahap hingga target 100 kalimat.
- [x] Membuat `tools/validasi_dataset_pos.py` untuk validasi struktur, label, status, ID, dan kecocokan token.
- [x] Membuat 9 regression tests pada `tests/test_validasi_dataset_pos.py`.
- [x] Menjalankan `python -m tools.validasi_dataset_pos` dari checkout Termux: **VALIDASI DATASET POS BERHASIL**, batch pertama: 10 kalimat, 43 token (6 development, 4 test), seluruh pemeriksaan struktur dan kesesuaian tokenizer lulus. Batch kedua (20 kalimat total) telah lolos validasi ulang di Termux: 20 kalimat, 91 token, 12 development, 8 test (27 November 2026).
- [x] Menjalankan 9 regression tests validator dari checkout Termux: 9 lulus, 0 gagal (27 November 2026).
- [x] Menjalankan ulang seluruh regression suite dari checkout Termux setelah validator POS ditambahkan: **132 tes lulus, 0 gagal** (27 November 2026).
- [x] Memvalidasi dataset POS terbaru dari checkout Termux: 30 kalimat, 156 token, 18 development, 12 test (27 November 2026).
- [ ] Memperluas dataset hingga target 100 kalimat dan mengevaluasi akurasi POS.

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

**Validasi checkout penuh dan verifikasi POS hingga konteks lokal selesai pada 27 November 2026 melalui Termux.** Validator memuat 60 batch/3.000 entri. Regression suite gabungan terbaru menjalankan **123 tes dan seluruhnya lulus**. Tahap 2.5 berlanjut ke penyusunan dataset kalimat berlabel dan evaluasi akurasi POS.

Hasil tes komponen yang tercatat dan dijalankan terpisah:
- Fondasi (normalisasi, tokenizer, loader, pencocokan kamus): 45 lulus.
- Analyzer teks: 8 lulus.
- Morfologi: 47 lulus.
- **Baseline awal: 100 lulus, setelah POS dasar: 110 lulus, dan setelah POS kontekstual: 123 lulus; seluruhnya 0 gagal.**

Catatan historis: sebelum 27 November 2026, tes komponen dijalankan terpisah pada salinan terisolasi. Pada 27 November 2026, validasi diulang langsung dari checkout repository penuh di Termux: validator 60 batch/3.000 entri berhasil dan `python -m unittest discover -s tests -v` menjalankan 100 tes dengan hasil OK, 0 gagal.

Langkah berikutnya: lanjutkan Tahap 2.5 dengan dataset kalimat berlabel dan evaluasi akurasi POS. Jangan mulai parser sebelum fondasi POS dan pengujiannya memadai.

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
