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

- Normalisasi: 8 tes lulus, 0 gagal.
- Tokenizer: 12 tes lulus, 0 gagal.
- Loader kamus: 12 tes lulus, 0 gagal.
- Pencocokan kamus: 13 tes lulus, 0 gagal.
- Total fondasi: **45 tes lulus, 0 gagal**, dijalankan di lingkungan Python lokal terisolasi menggunakan salinan file dari GitHub. GitHub Actions tidak dijalankan.
- **Validasi langsung checkout penuh melalui Termux (27 November 2026):** `python -m tools.validasi_kamus_lengkap` menghasilkan `VALIDASI BERHASIL`; 60 batch dan 3.000 entri dimuat. Pemeriksaan JSONL, field wajib, format ID, array wajib, ID duplikat, dan lema duplikat lulus.
- Pencocokan token ke lemma, variants, dan derived_forms sudah dibuat.
- Integrasi normalisasi, tokenizer, dan pencocokan kamus tersedia di `tools/analisis_teks.py` melalui fungsi `analyze_text(text, lexicon)`. Indeks leksikal dibangun sekali dengan `build_lexicon(entries)` lalu dapat digunakan ulang untuk beberapa masukan.
- Analyzer mengembalikan teks ternormalisasi serta hasil per token: kata cocok/tidak dikenal atau tanda baca. Semua kandidat dipertahankan; POS dan sense tidak dipilih otomatis.
- 8 regression tests analyzer lulus pada lingkungan Python lokal terisolasi.
- Prototipe morfologi tersedia di `tools/morfologi.py` melalui `analyze_morphology(token, lexicon)`. Versi terbaru menambahkan kandidat konfiks ke-an, per-an, peN-an, bentuk menge-, serta perapian urutan prefiks. Kandidat hanya dikembalikan jika bentuk dasarnya ditemukan dalam indeks kamus.
- Versi morfologi terkini memiliki **47 regression tests yang telah dijalankan pada lingkungan Python lokal terisolasi: 47 lulus, 0 gagal**. Tes negatif mencakup bentuk leksikal `beranda`, `kemari`, `terong`, `selalu`, `melati`, `kelapa`, `perang`, `terapi`, dan `mereka` agar tidak salah dipotong sebagai imbuhan. Tes tambahan juga memastikan prefiks `penge-` tidak menghasilkan kandidat palsu melalui pemotongan `pen-`, mempertahankan seluruh POS dan sense ketika lema dasar ambigu, serta mencakup bentuk `memperindah`. Kasus `memperbaiki` dan `mempermainkan` telah dijalankan bersama suite. Tes baru `diperbaiki` memverifikasi imbuhan bertingkat `di- + per- + -i` dan menghasilkan kandidat `baik`.
- **Regression suite checkout penuh melalui Termux (27 November 2026):** `python -m unittest discover -s tests -v` dijalankan dari root repository dan menghasilkan `Ran 100 tests ... OK` — **100 lulus, 0 gagal**. Rinciannya: analyzer 8, loader 12, morfologi 47, normalisasi 8, pencocokan kamus 13, tokenizer 12. Ini merupakan satu kali eksekusi gabungan dari checkout penuh, berbeda dari pengujian komponen terisolasi sebelumnya.
- Belum ada integrasi Android.

## 4. Pekerjaan yang sedang dikerjakan

**Subtahap 2.1–2.4 telah memiliki fondasi dan regression suite yang lulus. Validasi seluruh kamus, implementasi POS awal, dan regression suite gabungan 110 tes telah diverifikasi pada checkout Termux pada 27 November 2026. Tahap 2.5 berlanjut pada disambiguasi POS berbasis konteks dan evaluasi dataset berlabel.**

Normalisasi lulus 8/8 tes, tokenizer 12/12, loader 12/12, pencocokan kamus 13/13, analyzer 8/8, morfologi 47/47, dan POS awal 10/10. Pada 27 November 2026, validator memuat seluruh 60 batch (3.000 entri). Regression suite gabungan dari checkout Termux setelah POS ditambahkan menjalankan **110 tes; seluruhnya lulus, 0 gagal**. Pencocokan token terhadap lema, variants, dan derived_forms sudah tersedia.

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

### 5.2 Tokenizer — selesai
- [x] Buat `tools/tokenizer.py` dengan fungsi `tokenize(text: str) -> list[str]`.
- [x] Pecah teks menjadi token kata dan tanda baca; whitespace tidak menghasilkan token.
- [x] Tanda baca dikeluarkan sebagai token tersendiri, termasuk tanda baca berulang.
- [x] Bentuk bertanda hubung dan apostrof internal dipertahankan; apostrof di tepi menjadi token tanda baca.
- [x] Buat 12 regression tests; hasil pengujian lokal 12 lulus, 0 gagal.

Perilaku tambahan yang diuji: angka, underscore sebagai token tersendiri, teks kosong, kosakata informal, dan input non-string.

Contoh target awal:
- Masukan: `Aku mau makan nasi!`
- Token: `["aku", "mau", "makan", "nasi", "!"]`

Contoh ini adalah target perilaku tokenizer, bukan klaim bahwa tokenizer sudah dibuat.

### 5.3 Pencocokan token ke kamus
- [x] Periksa struktur JSONL aktual pada sampel Batch 001 dan Batch 006.
- [x] Buat `tools/kamus_loader.py` sebagai loader baca-saja; isi entri dipertahankan tanpa modifikasi.
- [x] Tambahkan 12 regression tests untuk pemuatan batch, urutan batch, validasi struktur, serta deteksi ID/lemma duplikat.
- [x] Hasil uji lokal loader: 12 lulus, 0 gagal.
- [x] Jalankan fungsi loader Python langsung terhadap seluruh 60 file batch aktual dari checkout Termux; 60 batch/3.000 entri berhasil dimuat.
- [x] Buat pencocokan token terhadap lemma, variants, dan derived_forms.
- [x] Pertahankan seluruh kandidat dan sense/POS; jangan putuskan makna tanpa konteks.
- [x] Integrasikan normalisasi, tokenizer, dan pencocokan leksikal dalam `tools/analisis_teks.py`.
- [x] Buat 8 regression tests analyzer; hasil pengujian lokal 8 lulus, 0 gagal.
- [x] Bedakan hasil: lemma ditemukan, varian ditemukan, bentuk turunan tercatat, atau tidak dikenal.
- [x] Tangani kandidat dengan beberapa sense atau POS dengan mempertahankan seluruh kandidat tanpa memilih makna otomatis.
- [x] Buat 13 regression tests pencocokan leksikal untuk perilaku inti dan validasi input.

### 5.4 Analisis morfologi — prototipe awal
- [x] Buat `tools/morfologi.py` dengan fungsi `analyze_morphology(token, lexicon)`.
- [x] Gunakan kamus sebagai pemeriksa kandidat bentuk dasar; kandidat yang tidak cocok dengan kamus tidak dilaporkan.
- [x] Hindari stemming kata yang sudah cocok persis dengan kamus.
- [x] Buat 12 regression tests awal; hasil lokal 12 lulus, 0 gagal.
- [x] Tambahkan pola kandidat konfiks ke-an, per-an, dan peN-an yang tetap divalidasi melalui kamus.
- [x] Rapikan urutan percobaan prefiks dan hilangkan prefiks duplikat yang tidak tepat.
- [x] Jalankan 20 regression tests morfologi versi terbaru; 20 lulus, 0 gagal.
- [x] Tambahkan perlindungan awal untuk bentuk leksikal beranda, kemari, kemarin, terima, terus, perlu, dan pernah.
- [x] Tambahkan tes negatif untuk bentuk beranda dan kemari agar tidak salah dianalisis sebagai bentuk berimbuhan.
- [x] Tambahkan lima tes negatif tambahan untuk terong, selalu, melati, kelapa, dan perang.
- [x] Jalankan 25 regression tests setelah penambahan lima kasus negatif; 25 lulus, 0 gagal.
- [x] Tambahkan dua tes negatif untuk `terapi` dan `mereka`.
- [x] Jalankan 27 regression tests morfologi; 27 lulus, 0 gagal.
- [x] Tambahkan tes konflik prefiks bertumpuk `penge-` dan `pen-`; pastikan hanya kandidat prefiks terpanjang yang diambil.
- [x] Jalankan 28 regression tests morfologi; 28 lulus, 0 gagal.
- [x] Uji bahwa lema ambigu mempertahankan seluruh POS dan sense melalui analisis morfologi.
- [ ] Perluas pengujian untuk kandidat palsu lainnya.
- [ ] Lengkapi inventaris imbuhan, reduplikasi, dan perubahan morfofonemik berdasarkan hasil uji.

### 5.5 Pengenalan kelas kata (POS)
- [x] Gunakan kode POS resmi dalam `docs/KAMUS.md`.
- [x] Pertahankan kemungkinan lebih dari satu POS/sense untuk kata ambigu.
- [x] Buat identifikasi POS leksikal melalui `tools/pos_tagger.py`.
- [x] Tambahkan `tools/pos_context.py` dengan aturan konteks lokal konservatif: petunjuk aspek, preposisi, demonstrativa, dan pola sederhana `bisa`.
- [x] Pertahankan ambiguitas jika tidak ada petunjuk atau petunjuk bertentangan; jangan mengubah POS leksikal asli.
- [x] Buat 13 regression tests POS kontekstual; **13/13 lulus** pada checkout Termux (27 November 2026).
- [x] Jalankan regression suite gabungan pada checkout Termux: **123/123 tes lulus, 0 gagal** (27 November 2026).
- [ ] Susun dataset kalimat berlabel dan ukur akurasi POS.

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

**Titik lanjut (diperbarui 27 November 2026):** validasi loader seluruh 60 batch dan regression suite checkout penuh telah berhasil dijalankan melalui Termux. `python -m tools.validasi_kamus_lengkap` memuat 60 batch/3.000 entri. Setelah implementasi POS ditambahkan, 10 tes POS lulus dan `python -m unittest discover -s tests -v` menghasilkan **110 tes lulus, 0 gagal**. Lanjutkan Tahap 2.5 pada disambiguasi berbasis konteks dan evaluasi dataset berlabel. Catatan lama setelah bagian ini adalah riwayat perkembangan dan tidak mengesampingkan hasil validasi checkout penuh terbaru. Versi morfologi terbaru memperbaiki konflik prefiks bertumpuk agar prefiks terpanjang yang cocok dipakai dan kandidat palsu dari pemotongan prefiks pendek tidak ikut dihasilkan. Aturan prefiks `memper-` juga ditambahkan agar bentuk seperti `memperindah` dapat menghasilkan kandidat lema `indah`; tes negatif untuk bentuk tak dikenal menggunakan `memperxyz`. Sebanyak 38 tes morfologi lulus; total 91 tes komponen lulus secara terpisah. Tes imbuhan bertingkat `diperbaiki` ditambahkan dan dijalankan bersama seluruh suite: 33 lulus, 0 gagal. Aturan baru mengurai lapisan `di-`, lalu `per-`, lalu sufiks `-i`, dengan kandidat akhir tetap harus ditemukan di kamus. Pengujian dilakukan pada lingkungan Python lokal terisolasi menggunakan salinan sumber repository. 


**Pembaruan imbuhan bertingkat:** aturan `di- + per- + sufiks` dibatasi ke sufiks `-i` dan `-kan`; sufiks `-an` dikecualikan agar pola nominal tidak dianggap sebagai bentuk pasif. Tes negatif `diperkerjaan` telah ditambahkan untuk memastikan lema `kerja` tidak dihasilkan. Suite terbaru telah dijalankan setelah penambahan tes negatif: 34 lulus, 0 gagal. Pengujian menggunakan salinan terkini dari `tools/morfologi.py`, `tools/pencocokan_kamus.py`, dan `tests/test_morfologi.py` dalam lingkungan Python lokal terisolasi.

**Pembaruan reduplikasi berprefiks:** `tools/morfologi.py` kini mengenali pola terbatas `ber- + bentuk ulang` seperti `berjalan-jalan` dan `berlari-lari`, dengan syarat bagian setelah tanda hubung cocok persis dengan lema kamus. Dua tes baru dijalankan; suite morfologi terbaru: 36 lulus, 0 gagal. Total pengujian komponen terpisah: 89 lulus, 0 gagal (45 fondasi + 8 analyzer + 36 morfologi).


**Pembaruan restorasi nasal `meng-`:** penambahan kandidat `k+akar` kini dilewati jika bagian setelah `meng-` sudah cocok dengan lema kamus. Ini mencegah kandidat spekulatif seperti `kambil` ketika `ambil` sudah tersedia, tanpa menghilangkan analisis `mengunci` → `kunci` ketika bentuk sisa `unci` tidak ditemukan. Regression suite morfologi terbaru: 38 lulus, 0 gagal; total komponen terpisah: 91 lulus, 0 gagal (45 fondasi + 8 analyzer + 38 morfologi). Pengujian memakai salinan terkini dari kode dan tes repository di lingkungan Python lokal terisolasi.


**Pembaruan restorasi nasal `peng-` (terbaru):** aturan restorasi `peng-` kini tidak menambahkan kandidat `k+akar` secara spekulatif apabila bagian setelah `peng-` sudah cocok dengan lema kamus. Regression tests memastikan `pengambil` menghasilkan `ambil`, bukan `kambil`, sementara `pengunci` tetap menghasilkan kandidat `kunci`. Suite morfologi terbaru dijalankan pada salinan sumber dan tes repository di lingkungan Python lokal terisolasi: **40 lulus, 0 gagal**. Total tes komponen yang dijalankan terpisah: **93 lulus, 0 gagal** (45 fondasi + 8 analyzer + 40 morfologi). GitHub Actions tidak dijalankan.

**Pembaruan prioritas restorasi nasal `men-/mem-/pen-/pem-` (terbaru):** analisis prefiks kini mengutamakan bentuk hasil restorasi konsonan awal `t` atau `p` jika bentuk tersebut ditemukan dalam kamus, sehingga kandidat kebetulan seperti `ari` tidak ikut dipilih untuk `menari`. Perlindungan yang sama diterapkan pada analisis gabungan prefiks+sufiks; `menarikan` juga menghasilkan `tari`, bukan `ari`. Regression suite morfologi dijalankan pada salinan sumber dan tes repository di lingkungan Python lokal terisolasi: **42 lulus, 0 gagal**. Total tes komponen terpisah: **95 lulus, 0 gagal** (45 fondasi + 8 analyzer + 42 morfologi). GitHub Actions tidak dijalankan.

**Audit alomorf `meny-/peny-` (selesai diverifikasi):** aturan retensi `ny` yang divalidasi kamus telah ditambahkan untuk prefiks tunggal dan kombinasi prefiks+sufiks. Regression tests `menyanyi` dan `menyanyikan` termasuk dalam suite terbaru. Suite morfologi 47/47 lulus pada lingkungan Python terisolasi; total komponen terpisah 100/100 lulus. Pengujian dari checkout repository penuh tetap belum dilakukan.

**Audit lanjutan restorasi nasal `meng-/peng-` pada akar vokal (sedang diverifikasi):** ditemukan dua jalur yang belum terlindungi oleh aturan sebelumnya. Pada pola gabungan prefiks+sufiks, `mengajarkan` berpotensi menghasilkan kandidat spekulatif `kajar` walaupun `ajar` sudah dikenal. Pada pola konfiks `peN-an`, `pengajaran` juga dapat menghasilkan `kajar`. Perbaikan kini menahan restorasi `k` apabila bentuk akar tanpa restorasi sudah ada di kamus, baik pada analisis gabungan maupun konfiks. Dua tes baru ditambahkan untuk `mengajarkan` dan `pengajaran`; fixture memuat `kajar` agar kandidat palsu benar-benar dapat terdeteksi. Bentuk dengan peluluhan konsonan tetap harus diuji, misalnya `mengunci` dan `pengunci` → `kunci`. File tes sekarang berisi 47 metode uji dan suite terbaru telah dijalankan: 47/47 lulus. Total komponen terpisah terverifikasi 100/100.


**Audit akar kata berawalan `ng-` (27 November 2026):** indeks token aktual diperiksa untuk lema `ngambek`, `ngarai`, `ngaret`, `ngaruh`, `ngebayangin`, `ngebut`, `ngecek`, `ngedumel`, `ngeh`, `ngemil`, `ngengat`, `ngeri`, dan `ngobrol`. Tidak ditemukan contoh bentuk permukaan `meng-/peng-` yang secara linguistik dan berdasarkan lema kamus membenarkan aturan restorasi baru untuk kelompok ini. Karena itu, tidak ada perubahan kode atau tes yang dibuat dari dugaan semata. Audit berlanjut dengan pendekatan berbasis contoh nyata; suite 47 tes morfologi telah dijalankan ulang dan lulus; hasil terbaru adalah 47 tes morfologi dan 100 tes komponen total.


**Audit cakupan bentuk turunan pada indeks token (27 November 2026):** indeks `m-o.tsv` dan `p-r.tsv` diperiksa untuk bentuk berimbuhan yang telah direkam sebagai `derived_form`. Contoh yang ditemukan mencakup `menulis`, `mengajar`, `mengambil`, `menyapu`, `menyampaikan`, `pengambilan`, `penyakit`, `penyampaian`, `pembacaan`, dan `penolakan`. Bentuk-bentuk ini sudah terhubung ke lema kanonis pada indeks, sehingga pencocokan leksikal dapat mengenalinya sebelum analisis morfologi fallback dipanggil. Tidak ada perubahan kode atau jumlah tes pada audit ini. Tes morfologi terkini berjumlah 47 metode; eksekusi terbaru yang terverifikasi adalah 47 lulus, dan total komponen terpisah adalah 100 lulus, 0 gagal. Langkah berikutnya: audit cakupan alomorf `peN-` dan interaksinya dengan lema yang memang berawalan `peng-/peny-`, tanpa mengubah aturan sebelum ada kasus regresi yang sah.


**Audit lema kanonis berawalan peN- (27 November 2026):** indeks token memuat lema kanonis seperti `pengacara`, `pengadilan`, `pengemudi`, `penggaris`, `penguin`, `penjara`, `peniti`, `penipuan`, `penasaran`, `penyanyi`, dan `penyu`. Kode `analyze_morphology` memeriksa kecocokan kata utuh melalui `_known(surface, lexicon)` sebelum mencoba aturan imbuhan, sehingga lema yang sudah dikenal tidak dipecah. Tidak ditemukan alasan untuk menambah guard atau mengubah aturan. Satu regression test baru ditambahkan untuk mengunci perilaku 11 lema tersebut dan variasi kapitalisasi `PENGUIN`. File tes kini memiliki 47 metode dan suite penuh pada lingkungan terisolasi telah dijalankan: 47/47 lulus; total komponen terpisah 100/100 lulus.


**Pembaruan hasil eksekusi suite morfologi (27 November 2026):** file tes terbaru yang berisi 47 metode berhasil dijalankan pada lingkungan Python terisolasi dengan salinan terbaru `tests/test_morfologi.py`, `tools/morfologi.py`, dan `tools/pencocokan_kamus.py` yang diambil dari GitHub. Hasil: **47/47 lulus, 0 gagal**. Dengan hasil komponen sebelumnya (45 tes fondasi + 8 tes analisis teks), total tes komponen terverifikasi secara terpisah kini **100/100 lulus**. Batasan: eksekusi ini bukan dari checkout repository penuh. Validasi seluruh 60 batch kamus dan pengujian integrasi dari checkout penuh tetap belum selesai.


## 9. Validasi checkout penuh melalui Termux — 27 November 2026

Repository `semoliginon-ops/Sistem_bahasa` berhasil di-clone ke perangkat Android dan seluruh perintah dijalankan dari direktori root checkout.

1. `python -m tools.validasi_kamus_lengkap` → **VALIDASI BERHASIL**; 60 batch, 3.000 entri. Pemeriksaan mencakup JSONL, field wajib, format ID, array wajib, ID duplikat, dan lema duplikat.
2. `python -m unittest discover -s tests -v` → **Ran 100 tests — OK**, 0 gagal.
3. Rincian tes: analyzer 8, loader 12, morfologi 47, normalisasi 8, pencocokan kamus 13, tokenizer 12.

Validasi ini dijalankan lokal pada Android melalui Termux; GitHub Actions tidak digunakan. Hasil ini menutup pekerjaan validasi loader seluruh kamus dan regression suite checkout penuh. Ini belum menyelesaikan POS, parser kalimat, atau dataset uji terpadu.


## 10. Tahap 2.5 — Pengenalan kelas kata (POS), progres awal — 27 November 2026

### Taksonomi yang digunakan
Kode POS resmi sudah ditetapkan pada `docs/KAMUS.md`: `NOUN`, `VERB`, `ADJ`, `ADV`, `PRON`, `NUM`, `PREP`, `CONJ`, `INTJ`, dan `PART`. Implementasi menggunakan kode yang sudah ada; tidak membuat label alternatif.

### Implementasi awal
- `tools/pos_tagger.py` menambahkan identifikasi POS berbasis kandidat leksikal dari hasil `analyze_text`.
- Hasil menyimpan seluruh kandidat POS per entri dan POS per sense. Kata dengan lebih dari satu POS tidak dipaksa menjadi satu label.
- Belum ada disambiguasi berbasis konteks kalimat. Metadata hasil secara eksplisit menyatakan `pos_contextual_disambiguation: false`.
- Bentuk `derived_form` tidak otomatis mewarisi POS lema karena kelas kata dapat berubah, misalnya `makan` (VERB) menjadi `makanan` (NOUN). Bentuk turunan ditandai `requires_morphology` untuk diproses setelah analisis morfologi.
- `tests/test_pos_tagger.py` berisi 10 regression tests untuk POS entri, POS ganda, POS per-sense, ambiguitas, bentuk turunan, token tak dikenal, tanda baca, pelestarian hasil analisis, dan validasi input.

### Status verifikasi
- [x] Kode POS diselaraskan dengan dokumentasi kamus.
- [x] Modul POS awal dan 10 regression tests telah ditambahkan ke branch `main`.
- [x] `git pull` berhasil pada checkout Termux; `python -m unittest discover -s tests -p "test_pos_tagger.py" -v` menghasilkan **10 tes lulus, 0 gagal**.
- [x] Regression suite gabungan setelah POS ditambahkan: `python -m unittest discover -s tests -v` menghasilkan **110 tes lulus, 0 gagal** pada checkout Termux (27 November 2026).
- [x] Petunjuk konteks lokal konservatif dan disambiguasi POS awal tersedia melalui `tools/pos_context.py`.
- [x] `tests/test_pos_context.py` berisi 13 regression tests; **13/13 lulus** pada checkout Termux.
- [x] Regression suite gabungan terbaru: **123 tes lulus, 0 gagal**.
- [x] Menetapkan spesifikasi dataset POS versi 1.0 pada [`DATASET_POS.md`](DATASET_POS.md): skema JSONL, pedoman anotasi, pembagian development/test, validasi, dan metrik.
- [x] Menyusun 10 kalimat sampel berlabel (6 development, 4 test) di `data/dataset_pos/kalimat_pos_v1.jsonl`.
- [x] Membuat `tools/validasi_dataset_pos.py` untuk validasi JSONL, ID, split, label POS, status anotasi, dan kecocokan token dengan tokenizer.
- [x] Membuat `tests/test_validasi_dataset_pos.py` berisi 8 regression tests.
- [x] Menjalankan `python -m tools.validasi_dataset_pos` dari checkout Termux: **VALIDASI DATASET POS BERHASIL**; 10 kalimat, 43 token, 6 development, 4 test.
- [~] Menjalankan 8 tes khusus validator dari checkout Termux; hasil masih menunggu.
- [ ] Memperluas dataset menuju target 100 kalimat dan mengukur akurasi POS.

**Batas klaim:** POS leksikal dan prototipe disambiguasi konteks lokal konservatif sudah tersedia; 13 tes khusus konteks dan seluruh 123 tes gabungan lulus pada checkout Termux. Aturan ini masih terbatas dan belum mewakili tata bahasa Indonesia secara menyeluruh. Dataset awal 10 kalimat sudah tersedia; validator sudah dijalankan dan berhasil memvalidasi 10 kalimat/43 token di Termux; 8 regression tests masih menunggu dijalankan. Evaluasi akurasi belum dilakukan.


### Verifikasi POS pada checkout Termux — 27 November 2026

- `git pull` berhasil mengambil implementasi POS dan dokumentasi terbaru dari `main`.
- `python -m unittest discover -s tests -p "test_pos_tagger.py" -v` → **Ran 10 tests — OK**, 0 gagal.
- `python -m unittest discover -s tests -p "test_pos_context.py" -v` → **Ran 13 tests — OK**, 0 gagal.
- `python -m unittest discover -s tests -v` → **Ran 123 tests — OK**, 0 gagal.
- Seluruh 110 tes sebelumnya tetap lulus setelah penambahan 13 tes POS kontekstual.

**Status terbaru:** POS leksikal dan prototipe disambiguasi konteks lokal konservatif terverifikasi pada checkout repository penuh. Aturan konteks masih terbatas. Spesifikasi dataset POS, batch sampel 10 kalimat, validator, dan 8 regression tests sudah dibuat. Verifikasi validator dataset berhasil pada checkout Termux; verifikasi 8 regression tests masih menunggu. Berikutnya perluasan data dan evaluasi akurasi. Parser kalimat belum dimulai.


### Pembaruan verifikasi validator dataset POS — 27 November 2026

- `python -m tools.validasi_dataset_pos` pada checkout Termux → **VALIDASI DATASET POS BERHASIL**; 10 kalimat, 43 token, 6 development, 4 test. Pemeriksaan JSONL, ID, split, label POS, status anotasi, dan kecocokan token dengan tokenizer lulus.
- `python -m unittest discover -s tests -p "test_validasi_dataset_pos.py" -v` → **Ran 9 tests — OK**, 0 gagal.
- Jumlah tes pada file validator adalah 9 metode uji (bukan 8); checklist dan spesifikasi diperbaiki agar konsisten.
- Status validator dan tes khususnya kini terverifikasi dari checkout Termux. Evaluasi akurasi POS belum dilakukan; dataset masih 10/100 kalimat.

**Titik lanjut:** perluas dataset POS secara bertahap menuju 100 kalimat. Setelah cakupan development memadai, evaluasi kesalahan pada development set sebelum mengunci dan mengukur test set. Jangan mengklaim akurasi umum dari sampel 10 kalimat.


### Regression suite penuh setelah validator dataset POS — 27 November 2026

Dari checkout repository `~/Sistem_bahasa` di Termux, perintah `python -m unittest discover -s tests -v` berhasil dijalankan setelah validator dataset POS ditambahkan.

- Hasil: **Ran 132 tests — OK**, 0 gagal.
- Waktu eksekusi yang dilaporkan: 0,087 detik.
- Cakupan suite mencakup analisis teks, loader kamus, morfologi, normalisasi, pencocokan kamus, POS kontekstual, POS leksikal, tokenizer, dan validator dataset POS.
- Verifikasi khusus validator sebelumnya: 9/9 tes lulus; validasi dataset: 10 kalimat dan 43 token berhasil.

**Status:** regression suite checkout penuh terbaru terverifikasi 132/132 lulus. Evaluasi akurasi POS belum dilakukan; dataset masih 10 dari target 100 kalimat. Titik lanjut adalah memperluas dataset secara bertahap dan mengevaluasi development set.


### Pembaruan dataset POS — batch kedua (27 November 2026)

- Batch kedua menambahkan 10 kalimat baru dengan ID `pos_0011`–`pos_0020` ke `data/dataset_pos/kalimat_pos_v1.jsonl`.
- Komposisi total saat ini: **20/100 kalimat**, 12 development dan 8 test; rancangan anotasi berjumlah 91 token.
- Cakupan tambahan meliputi adjektiva, adverbia derajat/cara, numeralia, imbuhan, partikel tanya, interjeksi, demonstrativa, dan nama diri.
- File dataset sudah diperbarui di branch `main`. Validasi batch kedua dan regression suite setelah penarikan perubahan masih menunggu dijalankan dari Termux. Hasil 132/132 tes sebelumnya tetap merupakan hasil terakhir yang benar-benar dijalankan, bukan klaim verifikasi untuk perubahan data terbaru.
- **Titik lanjut:** `git pull`, lalu `python -m tools.validasi_dataset_pos`; pastikan hasil menunjukkan 20 kalimat, 91 token, 12 development, dan 8 test.


### Verifikasi batch kedua dataset POS — 27 November 2026

Dari checkout `~/Sistem_bahasa` di Termux, pengguna menjalankan `python -m tools.validasi_dataset_pos` setelah menarik commit batch kedua.

- Hasil: **VALIDASI DATASET POS BERHASIL**.
- Jumlah: **20 kalimat, 91 token, 12 development, 8 test**.
- Pemeriksaan JSONL, ID, split, label POS, status anotasi, dan kecocokan token dengan tokenizer semuanya lulus.
- Status dataset: **20/100 kalimat** telah lolos validasi struktur. Evaluasi kualitas anotasi dan akurasi prediksi POS belum dilakukan.
- Regression suite penuh terakhir yang terverifikasi tetap **132/132 lulus** sebelum batch data kedua ditambahkan; jalankan ulang untuk konfirmasi setelah sinkronisasi terbaru.

**Titik lanjut:** jalankan regression suite penuh, lalu audit dan perluas data development secara bertahap. Test split tetap ditahan dan tidak dipakai untuk menyetel aturan.


### Verifikasi regression suite setelah batch kedua dataset POS — 27 November 2026

Pengguna menjalankan `python -m unittest discover -s tests -v` dari checkout `~/Sistem_bahasa` di Termux setelah batch kedua dataset ditarik dan divalidasi.

- Hasil: **Ran 132 tests in 0.087s — OK**.
- Jumlah kegagalan dan error: **0**.
- Cakupan: analisis teks, loader kamus, morfologi, normalisasi, pencocokan kamus, POS kontekstual, POS leksikal, tokenizer, dan validator dataset POS.
- Bersama validasi dataset yang baru saja berhasil, status dataset adalah **20 kalimat/91 token**, terdiri dari 12 development dan 8 test.
- Ini memverifikasi regresi kode dan struktur dataset pada checkout saat ini; hasil ini **belum mengukur akurasi POS** atau membuktikan kualitas semua anotasi gold.

**Titik lanjut:** audit anotasi dan perluas dataset, utamakan variasi kasus pada development set. Pertahankan test split sebagai data evaluasi tertahan.


### Penambahan batch ketiga dataset POS — 27 November 2026

- Commit dataset: `9bba4ee49ecb4e071126c2e7d33c0e3fac87e9f5`.
- Ditambahkan 10 record dengan ID `pos_0021`–`pos_0030`: 6 development dan 4 test.
- Total rancangan dataset menjadi **30 kalimat, 156 token, 18 development, 12 test**.
- Fenomena tambahan mencakup kalimat perintah, konjungsi subordinatif, negasi, numeralia, kata ulang, bentuk berimbuhan, dan pronomina interogatif.
- Pengguna menjalankan `python -m tools.validasi_dataset_pos` di Termux setelah `git pull`; hasil **VALIDASI DATASET POS BERHASIL**: 30 kalimat, 156 token, 18 development, 12 test. Pemeriksaan JSONL, ID, split, label POS, status anotasi, dan kecocokan token dengan tokenizer lulus (27 November 2026).
- Regression suite penuh 132/132 lulus pada verifikasi sebelumnya, sebelum batch ketiga ditambahkan. Belum ada klaim regression test setelah perubahan data ini.

**Titik lanjut:** jalankan ulang regression suite penuh setelah batch ketiga, lalu audit mutu anotasi pada development set. Test split tetap ditahan.


### Verifikasi validasi dataset POS batch ketiga — 27 November 2026

Dari Termux, pengguna menjalankan `python -m tools.validasi_dataset_pos` setelah menarik commit batch ketiga.

- Hasil: **VALIDASI DATASET POS BERHASIL**.
- Jumlah aktual: **30 kalimat, 156 token, 18 development, 12 test**.
- Seluruh pemeriksaan JSONL, ID, split, label POS, status anotasi, dan kecocokan token dengan tokenizer lulus.
- Jumlah token aktual 156; angka 155 sebelumnya merupakan perkiraan sebelum validator dijalankan.
- Regression suite penuh terakhir yang dikonfirmasi masih 132/132 sebelum batch ketiga ditambahkan. Jalankan ulang untuk verifikasi terbaru.

