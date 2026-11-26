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
- [ ] Memvalidasi batch kedua (20 kalimat, target 91 token; 12 development, 8 test) dari checkout Termux.
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
- [ ] Setelah validasi, lanjutkan audit anotasi development set. Jangan gunakan test split untuk menyetel aturan.

Catatan: regression suite penuh terakhir yang dikonfirmasi pengguna adalah 132/132 lulus sebelum batch ketiga ditambahkan. Jangan menganggap hasil itu sebagai verifikasi setelah perubahan data batch ketiga.


### Regression suite setelah validasi batch ketiga
- [ ] Jalankan `python -m unittest discover -s tests -v` dari Termux setelah batch ketiga; hasil terakhir sebelum batch ketiga adalah 132/132 lulus.
