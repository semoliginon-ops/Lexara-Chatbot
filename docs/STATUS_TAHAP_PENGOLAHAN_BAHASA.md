# Status Pengembangan — Tahap Pengolahan Kata dan Tata Bahasa Dasar

**Proyek:** Sistem Bahasa  
**Tahap roadmap:** Tahap 2 — Pengolahan kata dan tata bahasa dasar  
**Status keseluruhan:** Sedang dikerjakan  
**Dokumen induk:** [README.md](../README.md)  
**Checklist utama:** [CHECKLIST_PENGEMBANGAN.md](CHECKLIST_PENGEMBANGAN.md)  
**Dokumentasi kamus:** [KAMUS.md](KAMUS.md)

Dokumen ini adalah catatan kesinambungan kerja. Jika percakapan atau sesi pengembangan terputus, gunakan dokumen ini bersama README dan kondisi repository terbaru untuk melanjutkan pekerjaan tanpa mengulang langkah yang sudah selesai.


## Snapshot status terbaru — 27 November 2026

Bagian ini adalah acuan status terkini. Catatan historis di bawahnya dipertahankan sebagai riwayat dan tidak mengesampingkan snapshot ini.

- Kamus: **60 batch, 3.013 lema**; audit isi/relasi 60 batch dan audit index terdahulu selesai. Tidak ada audit ulang batch yang direncanakan.
- Dataset POS tervalidasi: **100 kalimat, 543 token** (60 development, 40 test).
- Evaluasi POS development kontekstual: **250/255 token dikenali**, coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%, tanpa kesalahan pada prediksi yang dikeluarkan.
- Lima abstention adalah kemunculan nama orang; sesuai keputusan pengguna, kasus ini ditunda ke tahap pengenalan nama/konteks dan tidak dipaksakan menjadi lema atau label POS.
- Test split 40 kalimat tetap tersegel dan tidak digunakan untuk penyetelan.
- Parser kalimat tersedia pada **v1.6**. Pengembangan parser sebelumnya dibekukan sementara untuk menyelesaikan POS; pembekuan kini dicabut.
- GitHub Actions **Run #114 SUCCESS**: validasi kamus 60 batch/3.013 lema, validasi dataset POS, evaluasi development, dan **242/242 regression tests lulus**.

**Titik lanjut aktif:** Tahap 2.5 (POS) dinyatakan selesai. Lanjutkan Tahap 2.6 dari baseline parser v1.5 dengan memperluas frasa verba/modal, memisahkan inti predikat dari pewatas, dan menguji variasi susunan kalimat sederhana. Lakukan perubahan kecil dengan regression tests; jangan mengulang audit batch atau membuka test split. Tahap 2.7 melengkapi variasi dataset; hubungan makna/konteks dan integrasi Android tetap mengikuti roadmap. Kelulusan tes bukan klaim pemahaman bahasa bebas setara LLM.

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

## 3. Riwayat kondisi repository awal (catatan historis)

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

## 4. Kondisi pekerjaan saat ini

Fondasi yang tersedia:
- Normalisasi, tokenisasi, loader kamus, pencocokan leksikal, dan analisis morfologi.
- POS leksikal dan POS kontekstual konservatif.
- Dataset POS 100 kalimat dengan development/test split dan validator/evaluator.
- Parser kalimat konservatif **v1.5**, mencakup pola klausa sederhana, frasa nominal datar, negasi/modal terbatas, koordinasi, label penghubung, serta klausa subordinatif tertentu.
- Regression suite dan workflow GitHub Actions untuk validasi kamus, dataset, evaluasi development, dan tes.

Verifikasi terpadu terakhir adalah GitHub Actions [Run #114](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45965451485):
- Kamus: 60 batch / **3.013 lema** tervalidasi.
- Dataset POS: 100 kalimat / 543 token; 60 development dan 40 test.
- POS kontekstual development: 250/255 dikenali; coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%.
- Lima abstention berupa nama orang ditunda ke tahap pengenalan nama/konteks.
- Regression suite: **242 tes lulus, 0 gagal**.

Tahap 2.5 selesai. Tahap 2.6 dilanjutkan dari parser v1.5; pekerjaan pertama adalah memperluas frasa verba/modal dan pengujian variasi susunan kalimat. Tahap 2.7 melengkapi keragaman dataset. Jaringan makna runtime, konteks percakapan multi-giliran, response engine, dan aplikasi Android belum selesai.
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

### 5.5 Pengenalan kelas kata (POS) — Tahap 2.5 selesai

- POS leksikal berbasis kamus tersedia di `tools/pos_tagger.py`; disambiguasi konteks lokal konservatif tersedia di `tools/pos_context.py`.
- POS spesifik-sense dan ambiguitas dipertahankan; POS lema tidak diwariskan otomatis ke bentuk turunan.
- Dataset POS tervalidasi: **100 kalimat / 543 token**, terdiri dari 60 development dan 40 test.
- Evaluasi development terakhir pada GitHub Actions Run #113:
  - POS leksikal: 247/255 prediksi benar; coverage 96,9%, selective accuracy 100,0%.
  - POS kontekstual: **250/255 dikenali**; coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%.
  - Tidak ada kesalahan pada prediksi kontekstual yang dikeluarkan.
  - Lima abstention merupakan lima kemunculan dari tiga nama orang. Sesuai keputusan pengguna, nama orang ditunda ke tahap pengenalan nama/konteks dan tidak dipaksa masuk kamus atau diberi POS pada tahap ini.
- 40 kalimat test tetap tersegel dan tidak digunakan untuk penyetelan.
- **Status:** Tahap 2.5 selesai berdasarkan evaluasi development dan keputusan pengguna.

### 5.6 Analisis struktur kalimat — baseline v1.6; Tahap 2.6 dilanjutkan

Parser tersedia di `tools/parser_kalimat.py`. Baseline v1.5 mencakup fitur sintaksis sebelumnya; v1.6 menambahkan rincian struktur predikat verbal. Fitur baseline v1.5 meliputi:
- Pola klausa sederhana S-P, S-P-O, S-P-K dan rentang frasa nominal sederhana.
- Negasi verbal terbatas serta penanganan modal.
- Predikat nonverbal dan predikat penghubung tertentu.
- Keterangan preposisional di depan klausa.
- Koordinasi frasa nominal dan beberapa klausa koordinatif.
- Label relasi untuk penghubung yang dikenali secara eksplisit.
- Klausa subordinatif terbatas di depan dan setelah klausa utama, termasuk pola konsesif eliptis tertentu dengan status `partial`.

Parser sempat dibekukan pada v1.5 agar fondasi POS diselesaikan terlebih dahulu. Karena Tahap 2.5 kini selesai, pembekuan tersebut dicabut. Perubahan terbaru menambahkan `predicate_structure` dengan `head` dan daftar `modifiers` bertipe `negation`, `modal`, atau `adverbial`; rentang `roles.predicate` lama tidak berubah sehingga pemanggil lama tetap kompatibel.

**Pekerjaan aktif berikutnya:**
- Memperluas frasa verba/modal di luar penanda yang sudah didukung.
- Memisahkan inti predikat dari pewatasnya tanpa menghilangkan urutan token.
- Menguji variasi susunan kalimat sederhana.
- Menambah dukungan secara konservatif untuk pelengkap dan pola lain setelah bukti uji tersedia.
- Mempertahankan status ambigu/unsupported bila struktur belum cukup didukung.

Parser v1.5 terakhir divalidasi tersendiri pada Run #99 dengan 232/232 tes. Parser v1.6 menambahkan `predicate_structure`; Run #114 memvalidasi perubahan ini dan regression suite lulus **242/242**.

### 5.7 Dataset uji dan regression suite — integrasi awal tersedia

- Dataset POS berisi 100 kalimat berlabel dan 543 token; 60 development, 40 test.
- Expected POS per token tersimpan dalam JSONL dan divalidasi terhadap tokenizer.
- Tes integrasi pipeline menggunakan kamus nyata tersedia di `tests/test_integrasi_pipeline.py`.
- Workflow memvalidasi kamus lengkap, dataset POS, evaluasi development, dan regression suite.
- GitHub Actions [Run #114](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45965451485): **242/242 tes lulus**.
- Pekerjaan yang masih terbuka adalah memperluas variasi dataset untuk bahasa baku, informal, slang, salah ketik, imbuhan, dan kata ulang. Test split yang sudah ada tetap ditahan.


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
- Setelah batch ketiga ditarik dan divalidasi, pengguna menjalankan `python -m unittest discover -s tests -v`: **Ran 132 tests in 0.105s — OK**, 0 gagal dan 0 error (27 November 2026).

**Titik lanjut:** audit mutu anotasi pada development set. Test split tetap ditahan.


### Verifikasi validasi dataset POS batch ketiga — 27 November 2026

Dari Termux, pengguna menjalankan `python -m tools.validasi_dataset_pos` setelah menarik commit batch ketiga.

- Hasil: **VALIDASI DATASET POS BERHASIL**.
- Jumlah aktual: **30 kalimat, 156 token, 18 development, 12 test**.
- Seluruh pemeriksaan JSONL, ID, split, label POS, status anotasi, dan kecocokan token dengan tokenizer lulus.
- Jumlah token aktual 156; angka 155 sebelumnya merupakan perkiraan sebelum validator dijalankan.
- Regression suite penuh terakhir yang dikonfirmasi masih 132/132 sebelum batch ketiga ditambahkan. Jalankan ulang untuk verifikasi terbaru.



### Verifikasi regression suite setelah batch ketiga — 27 November 2026

Pengguna menjalankan `git pull && python -m unittest discover -s tests -v` dari Termux setelah dokumentasi validasi batch ketiga diperbarui.

- `git pull` berhasil fast-forward ke commit dokumentasi terbaru.
- Hasil: **Ran 132 tests in 0.105s — OK**.
- Jumlah kegagalan: 0; jumlah error: 0.
- Seluruh kelompok tes analisis teks, loader kamus, morfologi, normalisasi, pencocokan kamus, POS kontekstual, POS leksikal, tokenizer, dan validator dataset POS lulus.
- Dataset pada checkout ini telah lolos validasi: 30 kalimat, 156 token, 18 development, 12 test.
- Hasil ini membuktikan regresi tes yang tersedia tetap lulus; belum mengukur akurasi POS atau memvalidasi kebenaran semantik seluruh anotasi gold.

**Titik lanjut:** audit kualitas anotasi pada development set, pertahankan test split sebagai data tertahan.


## Koreksi status terbaru Tahap 2.5 — 27 November 2026

Catatan ini menjadi status verifikasi terbaru dan mengesampingkan catatan historis yang menyebut batch ketiga atau regression suite masih menunggu.

- Dataset POS: **30 kalimat, 156 token, 18 development, 12 test**.
- `python -m tools.validasi_dataset_pos` dijalankan pengguna dari Termux dan menghasilkan **VALIDASI DATASET POS BERHASIL**.
- `python -m unittest discover -s tests -v` dijalankan pengguna setelah `git pull` dan menghasilkan **132 tests — OK**, 0 gagal, 0 error (0,105 detik).
- Audit awal kualitas anotasi pada 18 kalimat development telah dicatat di `docs/AUDIT_ANOTASI_POS.md`. Split test tidak diperiksa.
- Belum ada label gold yang diubah. Demonstrativa `itu`, aspek `sedang`, larangan `jangan`, dan gelar `Pak` perlu konvensi anotasi eksplisit.
- Hasil validasi struktur dan regression tests tidak boleh ditafsirkan sebagai skor akurasi POS.

**Titik lanjut:** perjelas konvensi anotasi, audit ulang development set, lalu ukur kinerja POS pada development. Test split tetap ditahan.


## Pembaruan pedoman anotasi POS — 27 November 2026

Konvensi operasional telah ditetapkan dalam `docs/DATASET_POS.md` subbagian 5.1 agar taksonomi 10 label proyek diterapkan konsisten:
- Demonstrativa atributif: `PRON`.
- Penanda aspek/modalitas: `ADV`.
- Penanda larangan: `PART`.
- Gelar/sapaan nominal: `NOUN`.
- Penghubung sebab: `CONJ`.
- Penanda tanya: `PART`.

Keputusan ini merupakan penyederhanaan internal dataset v1, bukan klaim universal linguistik. Belum ada label gold dalam JSONL yang diubah. Audit ulang 18 kalimat development masih menunggu pembaruan pedoman ditarik ke Termux. Split test tetap ditahan.


## Audit ulang anotasi POS development — 27 November 2026

- Pedoman anotasi POS v1 sudah ditetapkan pada `docs/DATASET_POS.md` subbagian 5.1.
- Seluruh 18 kalimat development diperiksa ulang; split test tetap ditahan dan tidak disentuh.
- Satu koreksi gold label dilakukan: `jangan` pada record `pos_0024` berubah dari `ADV` menjadi `PART`, sesuai konvensi penanda larangan.
- Label demonstrativa `itu`, aspek/modalitas `sedang/akan`, gelar `Pak`, dan penghubung sebab `karena` dipertahankan sesuai pedoman.
- Fragmen `Jalan.` tetap berstatus ambigu.
- Audit adalah pemeriksaan konsistensi internal oleh satu peninjau; bukan bukti akurasi model.

**Status verifikasi:** perubahan dataset dan dokumentasi sudah masuk ke branch `main`. Validasi dataset dan regression suite setelah perubahan masih menunggu dijalankan dari Termux.

**Titik lanjut:** `git pull`, kemudian `python -m tools.validasi_dataset_pos` dan `python -m unittest discover -s tests -v`.


## Verifikasi terbaru setelah koreksi anotasi POS — 27 November 2026

Bagian ini merupakan acuan status terkini dan mengesampingkan catatan historis yang menyebut verifikasi setelah koreksi masih menunggu.

- Audit ulang mencakup seluruh **18 record development**. Test split yang berisi 12 kalimat tetap ditahan dan tidak diubah.
- Satu koreksi gold label diterapkan pada `pos_0024`: token `jangan` diubah dari `ADV` menjadi `PART`, sesuai konvensi operasional dataset v1.
- Pengguna menjalankan `python -m tools.validasi_dataset_pos` dari Termux: **VALIDASI DATASET POS BERHASIL**, 30 kalimat, 156 token, 18 development, 12 test.
- Pengguna menjalankan `python -m unittest discover -s tests -v` dari Termux setelah koreksi: **Ran 132 tests in 0.093s — OK**, 0 gagal dan 0 error.
- Hasil ini mengonfirmasi validitas struktur dataset dan kelulusan regression suite yang tersedia. Hasil tersebut **bukan pengukuran akurasi POS** dan bukan bukti bahwa seluruh anotasi gold sudah benar secara linguistik.

**Status:** audit anotasi development, validasi dataset, dan regression suite pascakoreksi telah diverifikasi. Dataset masih 30/100 kalimat. Evaluasi prediksi POS terhadap gold label belum dibuat.

**Titik lanjut:** perluas development set secara bertahap, kemudian buat evaluasi POS yang melaporkan hasil per label dan kasus ambigu. Jangan gunakan 12 record test untuk menyetel aturan; jangan mulai parser kalimat sebelum evaluasi POS development memadai.


## Pembuatan evaluator POS development — 27 November 2026

Dibuat `tools/evaluasi_pos.py` untuk membandingkan keluaran POS leksikal dan POS dengan konteks lokal terhadap gold label pada split development. Evaluator:
- hanya memuat record `development` dan mengabaikan record `test`;
- menolak record non-development jika diberikan langsung ke fungsi evaluasi;
- melaporkan jumlah token resolved, coverage, accuracy terhadap semua token resolved, selective accuracy, confusion counts, dan apakah gold ambiguous tetap ditahan atau dipaksakan;
- memisahkan prediksi yang abstain dari prediksi yang benar, sehingga token tanpa prediksi tidak dihitung benar.

Empat regression tests awal dibuat pada `tests/test_evaluasi_pos.py`. **Kode dan tes belum dijalankan di Termux**; status masih menunggu verifikasi pengguna. Evaluator belum menghasilkan skor aktual.

**Perintah verifikasi berikutnya:**
1. `python -m unittest discover -s tests -p "test_evaluasi_pos.py" -v`
2. `python -m tools.evaluasi_pos`
3. `python -m unittest discover -s tests -v`

Hasil evaluasi hanya berlaku untuk 18 kalimat development saat ini. Jangan menyetel aturan berdasarkan test split.


## Verifikasi evaluator POS di Termux — 27 November 2026

Pengguna menjalankan rangkaian perintah setelah menarik commit evaluator ke Termux. Seluruh langkah berhasil:

- 4 regression tests khusus evaluator: **4 lulus, 0 gagal**.
- Evaluasi hanya memuat **18 kalimat development**; split test tidak dipakai.
- Token berstatus: 72 resolved, 1 ambiguous, dan 21 not_applicable.
- POS leksikal: 42/72 prediksi benar; coverage 58,3%; accuracy 58,3%; selective accuracy 100%.
- POS dengan konteks lokal: hasil identik dengan POS leksikal (42/72; coverage 58,3%; accuracy 58,3%; selective accuracy 100%). Pada sampel kecil ini, konteks lokal belum memberi peningkatan terukur.
- Penanganan gold ambiguous: 1 total, 0 ditahan, 1 dipaksakan. Kasusnya adalah token `jalan` pada record development `pos_0006` (“Jalan.”). Gold menyatakan ambigu antara NOUN dan VERB, tetapi keluaran sistem menetapkan satu POS. Ini adalah temuan yang harus diaudit, bukan keberhasilan disambiguasi.
- Regression suite penuh: **136 tes lulus, 0 gagal, 0 error** (`Ran 136 tests in 0.106s — OK`).

**Interpretasi:** selective accuracy 100% hanya berarti seluruh 42 prediksi yang dikeluarkan pada token resolved cocok dengan gold label. Coverage 58,3% menunjukkan 30 dari 72 token resolved tidak diberi prediksi. Accuracy 58,3% menghitung abstain sebagai tidak benar. Hasil ini terbatas pada development set kecil dan bukan estimasi akurasi umum.

**Titik lanjut:** audit kandidat POS lema `jalan` di kamus dan alasan sistem menganggapnya tidak ambigu. Periksa apakah masalah berasal dari metadata kamus atau aturan POS. Tambahkan regression test yang memastikan fragmen tanpa konteks tidak dipaksakan menjadi satu POS jika kamus/pedoman mengakui beberapa fungsi. Setelah itu, perluas dataset development secara bertahap. Jangan gunakan split test untuk menyetel aturan.


## Audit dan koreksi lema "jalan" — 27 November 2026

Pemeriksaan entri `K0020` di batch 001 menemukan ketidaksesuaian: `usage_notes` mengakui fungsi verba, tetapi field `pos` hanya berisi `NOUN`. Hal ini menyebabkan fragmen development "Jalan." dianggap tidak ambigu.

Metadata diperbaiki dengan dua kelas kata (`NOUN`, `VERB`) dan dua sense ber-POS spesifik: jalur/tempat (`NOUN`) serta bergerak/melangkah dengan kaki (`VERB`). Catatan penggunaan kini menyatakan bahwa fragmen tanpa konteks dapat tetap ambigu.

Satu regression test integrasi baru memuat kamus dan dataset development sebenarnya, lalu memeriksa bahwa token gold ambiguous `jalan` ditahan dan tidak dipaksakan. Tidak ada perubahan pada split test atau aturan konteks.

**Status:** perubahan sudah masuk branch `main`, menunggu verifikasi Termux. Jalankan tes evaluator, evaluator development, lalu seluruh regression suite.


## Verifikasi koreksi metadata POS lema "jalan" — 27 November 2026

Pengguna menarik enam pembaruan terbaru ke checkout Termux dengan `git pull` (fast-forward ke `0ff5ddb`).

- 5 regression tests khusus evaluator: **5 lulus, 0 gagal**.
- Evaluator hanya menggunakan 18 kalimat development: 72 token resolved, 1 ambiguous, 21 not_applicable.
- POS leksikal: 42 prediksi benar dari 72 token resolved; coverage 58,3%; accuracy 58,3%; selective accuracy 100%.
- POS dengan konteks lokal: hasil identik; belum ada peningkatan terukur pada sampel ini.
- Gold ambiguous: **1 ditahan (abstained), 0 dipaksakan (forced)**. Fragmen `Jalan.` kini tidak dipaksa menjadi satu POS.
- Regression suite penuh: **137 tests in 0.325s — OK**, 0 gagal dan 0 error.

Interpretasi: selective accuracy 100% hanya berlaku untuk 42 token yang diprediksi. Coverage 58,3% dan accuracy 58,3% menunjukkan masih banyak token resolved yang belum diprediksi. Evaluasi ini terbatas pada development set kecil dan bukan estimasi akurasi umum. Split test tetap tidak digunakan.

**Titik lanjut:** perluas dataset POS secara bertahap dari 30 menuju target 100 kalimat, utamakan variasi kasus pada development set, dan pertahankan test split sebagai data tertahan.


## Penambahan batch keempat dataset POS — 27 November 2026

Dataset POS diperluas dengan 10 record baru (`pos_0031`–`pos_0040`): 6 development dan 4 test. Jumlah sementara menjadi **40 kalimat**, terdiri dari **24 development dan 16 test**, dengan **215 token berdasarkan jumlah token anotasi**. Cakupan tambahan meliputi percakapan informal, modalitas, imbuhan, konjungsi, interjeksi, demonstrativa, adjektiva, numeralia, dan preposisi.

**Status:** perubahan sudah masuk branch `main`, tetapi belum diverifikasi dari Termux. Angka token masih menunggu konfirmasi validator; regression suite 137/137 adalah hasil sebelum batch keempat.

**Perintah verifikasi:**
1. `git pull`
2. `python -m tools.validasi_dataset_pos`
3. `python -m unittest discover -s tests -v`
4. `python -m tools.evaluasi_pos`

Evaluator hanya memakai split development. Jangan gunakan 16 record test untuk menyetel aturan.


## Verifikasi batch keempat dataset POS — 27 November 2026

Pengguna menarik perubahan ke Termux dan menjalankan validator, regression suite, serta evaluator secara berurutan.

- Validator: **40 kalimat, 215 token, 24 development, 16 test — VALIDASI DATASET POS BERHASIL**.
- Regression suite penuh: **137 tes lulus, 0 gagal, 0 error** (`Ran 137 tests in 0.330s — OK`).
- Evaluator hanya memakai development: 24 kalimat; 102 resolved, 1 ambiguous, 29 not_applicable.
- POS leksikal: 56 diprediksi, 55 benar; coverage 54,9%, accuracy 53,9%, selective accuracy 98,2%.
- POS konteks lokal: hasil identik; belum ada peningkatan terukur.
- Gold ambiguous: 1 ditahan, 0 dipaksakan.
- Audit lanjutan menetapkan `mau` pada `pos_0031` sebagai `VERB` (verba modal kehendak), sesuai entri kamus `K0024`; gold dikoreksi dari `ADV` menjadi `VERB`. Tidak ada perubahan kamus atau aturan program. Koreksi ini menunggu validasi dan evaluasi ulang di Termux. Token `wah` (INTJ) belum diprediksi; ini abstention.

**Titik lanjut:** audit `mau` serta cakupan prediksi kelas POS. Hasil hanya berlaku pada development set 24 kalimat; 16 kalimat test tetap ditahan.


## Audit kata `mau` — 27 November 2026

Pada kalimat development `Gue mau makan dulu`, `mau` ditetapkan sebagai `VERB` karena menyatakan kehendak dan berfungsi sebagai verba modal yang mengambil komplemen verba. Keputusan ini selaras dengan POS entri kamus `K0024`. Label gold pada `pos_0031` dikoreksi dari `ADV` menjadi `VERB`; pedoman `ADV` untuk `sedang`, `akan`, `telah`, `sudah`, dan `lagi` tetap dibatasi pada daftar tersebut. Kamus dan kode POS tidak diubah. Perubahan dataset serta dokumentasi menunggu validasi, evaluasi, dan regression suite ulang dari Termux. Split test tidak disentuh.


## Penambahan batch kelima dan audit INTJ — 27 November 2026

Dataset POS diperluas dari 40 menjadi 50 kalimat (`pos_0041`–`pos_0050`), terdiri dari 30 development dan 20 test. Batch menambahkan enam kalimat development dan empat test. Contoh `aduh` diberi `INTJ`, sesuai entri kamus `K0602`. Audit indeks menemukan `wah` belum tercakup dalam kamus; ini merupakan gap kosakata, bukan alasan mengubah POS atau menambah heuristik. Tidak ada perubahan kode POS atau kamus. Validasi dataset, evaluasi development, dan regression suite setelah batch kelima belum dijalankan. Test split tetap ditahan.


## Pemeriksaan awal batch kelima — 27 November 2026

File dataset yang telah di-commit dibaca ulang dari GitHub dan diperiksa secara struktural: 50 kalimat, 266 token, 30 development, 20 test; tidak ditemukan JSON rusak, ID duplikat, label/status POS tidak valid, atau ketidakcocokan token terhadap pola tokenizer. Setelah workflow validasi otomatis ditambahkan, GitHub Actions run [#1](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45906966948) benar-benar menjalankan modul Python proyek dan seluruh langkah berhasil. Validator: 50 kalimat, 266 token, 30 development, 20 test. Evaluator: 30 kalimat development, 125 token resolved; 72 benar, coverage 57,6%, accuracy 57,6%, selective accuracy 100%; 1 token ambiguous ditahan dan 0 dipaksakan. Untuk INTJ, `aduh` diprediksi benar sedangkan `wah` abstain. Regression suite penuh: 137/137 lulus. Test split tidak digunakan.


## Otomatisasi verifikasi tanpa Termux — 27 November 2026

Workflow `.github/workflows/pos-validation.yml` ditambahkan. Pada perubahan dataset POS, kamus, tools, atau tests di branch utama maupun pull request, GitHub Actions akan menjalankan validator dataset, evaluator yang hanya memuat development split, dan seluruh regression suite menggunakan Python 3.12. Workflow juga menyediakan pemicu manual. Workflow baru dibuat dan belum menjalani run; hasil pertama baru dapat dinilai setelah ada pemicu yang sesuai. Perubahan dokumentasi saja tidak memicu workflow agar penggunaan kuota Actions lebih hemat.


## Penambahan batch keenam — 27 November 2026

Dataset POS bertambah dari 50 menjadi 60 kalimat (`pos_0051`–`pos_0060`), terdiri dari 36 development dan 24 test, dengan 314 token berdasarkan anotasi. Cakupan baru mencakup negasi, verba berimbuhan, preposisi tujuan/asal, konjungsi sebab, demonstrativa, dan adjektiva predikatif. Preflight struktural sebelum commit lulus. Validator Python, evaluator development, dan regression suite setelah perubahan masih menunggu hasil GitHub Actions. Test split tetap ditahan.


## Verifikasi batch keenam — 27 November 2026

GitHub Actions run [#2](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45907643287) selesai dengan status sukses. Validator Python: 60 kalimat, 314 token, 36 development, 24 test. Evaluator development-only: 148 token resolved, 90 benar, coverage 60,8%, accuracy 60,8%, selective accuracy 100%; satu gold ambiguous ditahan dan tidak dipaksakan. Coverage per label memperlihatkan NUM 0/2, PREP 1/7, ADV 4/13, CONJ 3/6 (format benar/prediksi atau abstain dijelaskan di audit). Regression suite: 137/137 lulus. Test split tetap ditahan.


## Audit cakupan indeks leksikal POS — 27 November 2026

Setelah batch keenam, token resolved pada 36 kalimat development dibandingkan dengan delapan shard indeks kamus. Gap unik yang tercatat antara lain numeralia `dua` dan `tiga`; preposisi `di`, `ke`, `pada`; konjungsi `atau`, `kalau`, `tetapi`; adverbia `akan`, `dulu`, `sangat`, `sedang`, `sekali`, `tetap`; serta beberapa lema nomina/verba/adjektiva dan interjeksi `wah`. Kata tugas `untuk` dan `dari` sudah tersedia di kamus. Temuan ini mendukung suplementasi terfokus atau evaluasi closed-class, bukan perubahan massal terhadap kamus 3.000 lema. Belum ada perubahan kamus atau kode pada audit ini.


## Suplementasi POS terfokus — 27 November 2026

Dibuat fallback leksikal terpisah di `tools/pos_supplement.py` untuk 12 kata yang teridentifikasi dari audit gap development: dua/tiga (NUM), di/ke/pada (PREP), atau/kalau/tetapi (CONJ), serta akan/sedang/sangat/sekali (ADV sesuai konvensi proyek v1). Fallback hanya berlaku jika tidak ada kandidat POS dari kamus. Kamus 3.000 lema tidak diubah. Kata yang berpotensi polifungsi seperti `dulu` dan `tetap` sengaja dibiarkan tanpa fallback.

Regression tests menguji 12 kata, prioritas kandidat kamus, dan pelestarian ambiguitas. GitHub Actions run [#5](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908285217) berhasil: validator 60 kalimat/314 token (36 development, 24 test); evaluator development 148 token resolved, 107 benar, coverage 72,3%, accuracy 72,3%, selective accuracy 100%; gold ambiguous 1 ditahan dan 0 dipaksakan; regression suite **141/141 lulus**.

Kenaikan coverage dari 60,8% menjadi 72,3% dihitung pada development set yang sama setelah fallback; ini bukan akurasi umum. POS kontekstual dan leksikal tetap menghasilkan angka identik. Test split tetap ditahan.

**Titik lanjut:** Batch 7 (`pos_0061`–`pos_0070`), enam development dan empat test. Setelah batch ditambahkan, validator, evaluator development-only, dan regression suite dijalankan kembali melalui GitHub Actions.


## Batch ketujuh — 27 November 2026

Dataset POS diperluas menjadi 70 kalimat (`pos_0001`–`pos_0070`), 374 token, 42 development dan 28 test. Batch ketujuh menambahkan enam development dan empat test dengan cakupan numeralia, preposisi tujuan, konjungsi, penanda aspek/modalitas, demonstrativa, dan adverbia derajat.

GitHub Actions run [#6](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908531211) sukses: validator 70 kalimat/374 token; evaluator development-only 174 token resolved, 131 benar, coverage 75,3%, accuracy 75,3%, selective accuracy 100%; gold ambiguous 1 ditahan dan 0 dipaksakan; regression suite **141/141 lulus**. Test split 28 kalimat tidak digunakan.

**Titik lanjut:** Batch 8 (`pos_0071`–`pos_0080`), enam development dan empat test. Jangan menggunakan split test untuk mengubah aturan.


## Batch kedelapan — 27 November 2026

Dataset POS diperluas menjadi 80 kalimat (`pos_0001`–`pos_0080`), 428 token, 48 development dan 32 test. Batch kedelapan menambahkan enam development dan empat test, dengan cakupan numeralia atributif, preposisi lokatif/tujuan, konjungsi pertentangan, penanda aspek, demonstrativa, nomina berimbuhan, dan adverbia derajat.

GitHub Actions run [#7](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908957782) sukses: validator 80 kalimat/428 token; evaluator development-only 199 token resolved, 149 benar, coverage 74,9%, accuracy 74,9%, selective accuracy 100%; gold ambiguous 1 ditahan dan 0 dipaksakan; regression suite **141/141 lulus**. Test split 32 kalimat tidak digunakan.

**Titik lanjut:** Batch 9 (`pos_0081`–`pos_0090`), enam development dan empat test. Jangan menggunakan split test untuk mengubah aturan.


## Batch kesembilan — 27 November 2026

Dataset POS diperluas menjadi 90 kalimat (`pos_0001`–`pos_0090`), 485 token, 54 development dan 36 test. Batch kesembilan menambahkan enam development dan empat test, dengan cakupan negasi, verba transitif, nomina/verba berimbuhan, interjeksi, adjektiva atributif/predikatif, numeralia, preposisi, dan konjungsi.

GitHub Actions run [#8](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909135531) sukses: validator 90 kalimat/485 token; evaluator development-only 227 token resolved, 167 benar, coverage 73,6%, accuracy 73,6%, selective accuracy 100%; gold ambiguous 1 ditahan dan 0 dipaksakan; regression suite **141/141 lulus**. Test split 36 kalimat tidak digunakan.

**Titik lanjut:** Batch 10 (`pos_0091`–`pos_0100`), enam development dan empat test. Jangan menggunakan split test untuk mengubah aturan.


## Target dataset POS v1 tercapai — 27 November 2026

Dataset POS mencapai 100 kalimat (`pos_0001`–`pos_0100`), 543 token, terdiri dari 60 development dan 40 test. Batch kesepuluh menambahkan enam development dan empat test.

GitHub Actions run [#9](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909322818) sukses: validator 100 kalimat/543 token; evaluator development-only 255 token resolved, 186 benar, coverage 73,3%, accuracy 72,9%, selective accuracy 99,5%; satu gold ambiguous ditahan dan nol dipaksakan; regression suite **141/141 lulus**.

**Penting:** selective accuracy bukan 100%; terdapat prediksi keliru di antara token yang diputuskan sistem. Dataset telah mencapai target kuantitas, bukan berarti kualitas POS sudah final. Tahap berikutnya adalah audit kesalahan development dan penetapan protokol evaluasi terpisah untuk 40 kalimat test. Test tidak boleh digunakan untuk menyetel aturan.


## Audit kesalahan development pertama — 27 November 2026

`tools/evaluasi_pos.py` kini melaporkan contoh salah prediksi secara eksplisit. Perubahan diverifikasi pada GitHub Actions [run #10](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909498360): dataset tetap valid (100 kalimat, 543 token; 60 development, 40 test) dan regression suite **142/142 lulus**.

Kesalahan yang ditemukan: `pos_0093`, kalimat “Dia sangat rajin dan disiplin.”, token `disiplin`; gold `ADJ`, prediksi `NOUN` pada POS leksikal maupun kontekstual. Jangan ubah anotasi gold sekadar mengikuti prediksi. Audit entri kamus dan konteks harus mendahului perubahan. Test split 40 kalimat tetap tertahan.


## Perbaikan POS koordinatif `disiplin` — 27 November 2026

Entri kamus `disiplin` diperluas dengan sense ADJ selain NOUN. Aturan konteks lokal kini dapat memakai kesesuaian POS konjung kiri dan token kanan pada koordinasi `dan`/`serta`/`maupun`, hanya bila irisan label tepat satu. Perubahan diuji dengan kalimat development “Dia sangat rajin dan disiplin.”

GitHub Actions [run #11](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909687815) sukses: validator 100 kalimat/543 token; POS kontekstual 187/255 benar, coverage 73,3%, accuracy 73,3%, selective accuracy 100%, nol kesalahan prediksi yang diputuskan; regression suite **143/143 lulus**. POS leksikal menghasilkan 186/255 benar dan lebih banyak abstention. Ini hanya evaluasi development, bukan skor test atau akurasi umum. Test split 40 kalimat tetap ditahan.


## Diagnostik abstention POS dan perluasan fungsi kata — 27 November 2026

Evaluator kini menampilkan semua token development yang belum diputuskan beserta alasan dan sumber leksikalnya. Suplementasi terkurasi menambahkan `itu` (PRON), `dan`/`ketika` (CONJ), serta `wah` (INTJ), tanpa memasukkan kata polifungsi `baru`, `dulu`, dan `tetap` sebagai fallback tunggal.

GitHub Actions [run #13](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45910106880) sukses: validator 100 kalimat/543 token; contextual POS development 208/255 benar, coverage/accuracy 81,6%, selective accuracy 100%, nol kesalahan prediksi yang diputuskan; regression suite **144/144 lulus**. Abstention tersisa: ADJ 2, ADV 3, NOUN 19, VERB 23. Sebagian besar VERB membutuhkan morfologi; sebagian nomina belum ada dalam indeks kamus.

Angka ini hanya dari development, bukan estimasi performa umum. Test split 40 kalimat tetap tertahan. Tahap berikutnya: audit integrasi morfologi verba dan kelengkapan lema nomina.

## Integrasi morfologi dan POS — 27 November 2026

Pipeline kini menghubungkan `analyze_morphology()` dengan `analyze_text()` dan `tag_pos()`. Token kata menyertakan kandidat morfologi yang hanya diterima jika bentuk dasarnya ditemukan pada indeks kamus. Bentuk turunan yang tercatat di kamus juga dapat dianalisis morfologinya; lema utuh dan variasi ejaan tetap dilindungi dari stemming.

POS tagger menggunakan aturan konservatif untuk pola verbal yang telah didukung. Label VERB hanya diberikan jika aturan imbuhan sesuai dan semua kandidat lema dasar yang ditemukan memiliki POS VERB. Pola yang belum cukup kuat tetap abstain; misalnya `bekerja` tidak dipaksakan menjadi VERB hanya karena berawalan `ber-`, sebab lema `kerja` tercatat sebagai NOUN dan pola itu belum memiliki bukti POS turunan eksplisit.

GitHub Actions [run #26](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45910648622) sukses:
- Validator: 100 kalimat, 543 token; 60 development dan 40 test.
- POS leksikal development: 215/255 benar, coverage/accuracy 84,3%, selective accuracy 100%.
- POS kontekstual development: 216/255 benar, coverage/accuracy 84,7%, selective accuracy 100%.
- Kesalahan prediksi pada token yang diputuskan: 0 untuk leksikal dan 0 untuk kontekstual.
- Abstention: ADJ 2, ADV 3, NOUN 19, VERB 15. Gold ambiguous: 1 ditahan, 0 dipaksakan.
- Regression suite: **147/147 lulus**.

Hasil ini khusus 60 kalimat development; bukan estimasi akurasi umum. Dibanding evaluasi sebelumnya, abstention VERB turun dari 23 menjadi 15. Empat puluh record test tetap ditahan dan tidak digunakan dalam perubahan ini.

**Titik lanjut:** audit residual VERB (terutama `bekerja`, `memasak`, `membeli`, `menjelaskan`, `bermain`, `ditunda`, `letakkan`, `berteduh`) dan lengkapi lema NOUN yang benar-benar dibutuhkan. Bedakan gap kamus, keterbatasan aturan morfologi, dan kasus POS yang memerlukan metadata bentuk turunan.


## Verifikasi bentuk turunan tercatat dan POS — 27 November 2026

Tiga pembaruan kode di branch `main` memprioritaskan relasi `derived_form` yang tercatat di kamus dibanding segmentasi morfologi spekulatif. POS tagger menerima bentuk turunan berawalan `meN-` atau `ber-` sebagai VERB hanya jika lema dasar tervalidasi memiliki POS VERB. Pengamanan untuk `bekerja` tetap dipertahankan: lema `kerja` berlabel NOUN, sehingga bentuk itu tidak dipaksakan menjadi VERB tanpa bukti morfologis yang sesuai.

Pengguna menarik commit hingga `0d37b01` dan menjalankan regression suite lokal di Termux:
- **149/149 tes lulus**, 0 gagal, 0 error.
- POS leksikal development: **222/255 benar**, coverage/accuracy **87,1%**, selective accuracy **100%**.
- POS kontekstual development: **223/255 benar**, coverage/accuracy **87,5%**, selective accuracy **100%**.
- Tidak ada kesalahan pada prediksi yang dikeluarkan; 1 token gold ambiguous ditahan dan 0 dipaksakan.
- Evaluasi hanya memakai 60 kalimat development. Empat puluh kalimat test tetap tertahan.

Dibanding hasil sebelumnya (215/255 leksikal dan 216/255 kontekstual), kedua jalur bertambah tujuh prediksi benar pada development. Ini peningkatan coverage/accuracy pada set yang sama, bukan klaim akurasi umum.

**Sisa audit VERB development:** delapan kemunculan token abstain terdiri dari `bekerja` (3), `ditunda`, `letakkan`, `menjelaskan`, `hinggap`, dan `berteduh`. Status diagnostik: `bekerja` dan `menjelaskan` memerlukan analisis morfologi; empat bentuk lainnya belum memiliki kandidat leksikal/morfologis yang dapat dipakai. Audit berikutnya harus memeriksa lema dasar, bentuk turunan yang tercatat, serta pola pasif dan imperatif secara terpisah. Jangan menggunakan split test untuk menyetel aturan.


## Verifikasi POS bentuk turunan eksplisit — 27 November 2026

Pengguna menarik pembaruan terbaru ke Termux dan menjalankan seluruh rangkaian pemeriksaan lokal:

- Regression suite: **152/152 lulus**.
- Validator dataset: **100 kalimat, 543 token; 60 development dan 40 test — berhasil**.
- POS leksikal development: **227/255 benar**, coverage/accuracy **89,0%**, selective accuracy **100%**.
- POS kontekstual development: **228/255 benar**, coverage/accuracy **89,4%**, selective accuracy **100%**.
- Kesalahan prediksi pada token yang diputuskan: **0** untuk kedua jalur.
- Gold ambiguous: **1 ditahan, 0 dipaksakan**.
- Abstention VERB tersisa: `ditunda`, `hinggap`, dan `berteduh`.

Perubahan metadata bentuk turunan menyelesaikan prediksi untuk `bekerja`, `menjelaskan`, dan `letakkan` pada contoh development yang diaudit. Hasil ini terbatas pada development set dan bukan estimasi akurasi umum. Seluruh 40 record test tetap tertahan.

**Titik lanjut:** audit keberadaan lema `tunda`, `hinggap`, dan `teduh` serta gap kosakata NOUN. Jangan menyetel aturan menggunakan test split.


## Audit indeks untuk sisa verba — 27 November 2026

Pemeriksaan seluruh delapan shard token index tidak menemukan entri token persis tunda, hinggap, teduh, ditunda, maupun berteduh. Karena index merupakan alat navigasi dan pemeriksaan duplikasi, ketiga lema dasar dicatat sebagai kandidat penambahan kamus yang perlu ditinjau, bukan langsung ditambahkan tanpa pemeriksaan skema.

Aturan kamus saat ini menetapkan setiap batch berisi tepat 50 lema baru dengan ID berurutan. Karena itu tidak dibuat batch parsial untuk tiga kata. Rencana berikutnya adalah mengumpulkan lema prioritas lain dari abstention NOUN, lalu memasukkannya ke batch lengkap setelah audit duplikasi dan penetapan POS/sense. Untuk teduh, POS dasar perlu ditinjau sebagai ADJ; bentuk berteduh memerlukan anotasi POS bentuk turunan VERB yang eksplisit jika relasinya disetujui.

Tidak ada perubahan kode atau data kamus pada audit ini. Evaluasi tetap hanya pada development set; 40 kalimat test tetap tertahan.


## Parser kalimat v0.4 — frasa verba modal

Parser kini memiliki aturan terbatas untuk verba kehendak `mau`, `ingin`, dan `hendak`. Jika salah satu token tersebut berlabel VERB dan diikuti verba leksikal, parser memilih verba leksikal sebagai inti predikat dan menggabungkan verba kehendak ke rentang predikat. Jika berdiri sendiri, token tersebut tetap dapat menjadi predikat.

Tiga regression tests baru mencakup `aku mau pergi`, `dia ingin makan nasi`, dan penggunaan tunggal `aku mau`. Aturan ini tidak otomatis diperluas ke `bisa`, `dapat`, atau kata lain yang ambigu. GitHub Actions [Run #78](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45936018029) sukses: **190/190 regression tests lulus**, validasi lima batch berhasil, seluruh 3.000 lema tervalidasi secara struktural, validasi dataset POS dan evaluasi development juga berhasil.


## Parser kalimat v0.5 — predikat nonverbal sederhana

Parser kini memiliki jalur konservatif untuk predikat nonverbal ketika tidak ditemukan token ber-POS VERB. Pola adjektival diterima jika subjek memiliki penanda yang cukup jelas (misalnya pronomina atau demonstrativa `ini/itu`). Pola nominal sederhana diterima jika pola memiliki subjek nominal diikuti numeralia dan kepala nominal predikat, misalnya `Ayah seorang guru`.

Parser sengaja menahan rangkaian seperti `rumah besar` karena dapat dibaca sebagai frasa nominal, bukan kalimat. Empat tes baru menguji predikat adjektival, nominal, dan keputusan abstain. Perubahan ini belum diklaim terverifikasi melalui pipeline kamus/POS nyata; pengujian integrasi tersebut menjadi pekerjaan berikutnya.


GitHub Actions [Run #80](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45936363554) memverifikasi parser v0.5: **194/194 regression tests lulus**. Validasi kelompok lima batch, validasi struktur kamus 3.000 lema, validasi dataset POS, dan evaluasi development juga berhasil. Empat tes baru untuk predikat nonverbal termasuk di dalam regression suite. Keterbatasan yang masih terbuka: POS konstruksi nonverbal belum diuji end-to-end dengan kalimat nyata melalui pipeline kamus.


## Integrasi predikat nonverbal melalui pipeline kamus — 27 November 2026

Dua konstruksi predikat adjektival kini diuji melalui alur penuh kamus 3.000 lema → analisis leksikal/morfologi → POS tagger → disambiguasi konteks → parser:

- `Dia sakit.`: `dia` dikenali sebagai PRON dan `sakit` sebagai ADJ; parser menghasilkan pola S-P.
- `Rumah itu besar.`: `rumah` dikenali sebagai NOUN, `itu` sebagai PRON dari supplement POS yang eksplisit, dan `besar` sebagai ADJ; parser menghasilkan pola S-P dengan subjek `rumah itu`.

Dua tes integrasi end-to-end ditambahkan. GitHub Actions [Run #81](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45936903373) sukses: **196/196 regression tests lulus**. Validasi Batch-056–060, struktur seluruh kamus 60 batch/3.000 lema, dataset POS, dan evaluasi development juga sukses.

**Batas yang sudah diverifikasi:** integrasi nonverbal adjektival pada dua pola tersebut. Predikat nominal `Ayah seorang guru` masih diuji pada tingkat parser dengan POS terkontrol, belum melalui pipeline kamus penuh. Belum ada dukungan yang diklaim untuk pelengkap predikat seperti `menjadi dokter` atau `tampak bahagia`; itu menjadi tahap desain dan implementasi berikutnya.


## Parser kalimat v0.6 — pelengkap predikat terbatas — 27 November 2026

Parser kini membedakan dua konstruksi pelengkap predikat sederhana dari objek:

- `Dia menjadi dokter.`: `menjadi` sebagai predikat dan `dokter` sebagai pelengkap nominal; pola `S-P-Pel`.
- `Mereka tampak bahagia.`: `tampak` sebagai predikat dan `bahagia` sebagai pelengkap adjektival; pola `S-P-Pel`.

Field `roles.complement` diisi dan objek tetap kosong untuk dua pola tersebut. Tes pembanding memastikan verba transitif biasa, misalnya `Dia membeli baju`, tetap menghasilkan objek (`S-P-O`).

GitHub Actions [Run #82](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45937493840) sukses: **199/199 regression tests lulus**; validasi Batch-056–060, kamus 60 batch/3.000 lema, dataset POS, dan evaluasi development juga berhasil.

**Batas penting:** tiga tes fitur baru menggunakan POS terkontrol di tingkat parser. Dukungan POS untuk `menjadi` dan `tampak` belum diklaim terverifikasi end-to-end melalui kamus. Frasa kompleks seperti `tampak sangat bahagia`, klausa pelengkap, dan verba penghubung lain belum ditangani.


## Verifikasi cakupan leksikal pelengkap — 27 November 2026

Pemeriksaan melalui data kamus dan pipeline menemukan batas cakupan yang penting:

- `tampak` bukan lema mandiri pada dataset saat ini, tetapi merupakan varian eksplisit dari lema `nampak` (VERB). Pipeline mengenalinya sebagai VERB dari kamus.
- `menjadi` belum memiliki kecocokan kamus langsung pada dataset saat ini. POS-nya tidak ditebak.
- `bahagia` muncul sebagai kata terkait pada entri lain, tetapi belum tersedia sebagai lema/varian/bentuk turunan langsung dengan POS-nya sendiri. Karena itu, parser tidak menganggapnya ADJ hanya dari kemunculan kata di relasi makna.

Dua tes integrasi mengunci perilaku konservatif tersebut:
- `Dia menjadi dokter.` tetap unresolved karena verba penghubung belum dikenali secara leksikal.
- `Mereka tampak bahagia.` dikenali parsial: `tampak` sebagai VERB dan `bahagia` ditandai unresolved; tidak ada pelengkap yang ditebak.

GitHub Actions [Run #84](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45937903217) sukses: **201/201 regression tests lulus**, validasi 3.000 lema, dataset POS, dan evaluasi development juga lulus.

**Keputusan teknis:** jangan menambahkan kata ke supplement POS hanya untuk membuat contoh parser lulus. Perluasan lema/POS harus menjadi perubahan dataset yang disengaja, dengan definisi, kelas kata, dan tesnya sendiri.


## Parser kalimat v0.7 — keterangan preposisional di depan subjek — 27 November 2026

Parser kini dapat mengenali keterangan preposisional sederhana yang diletakkan sebelum subjek, selain keterangan yang berada setelah predikat.

Contoh:
- `Aku bekerja di rumah.` → S-P-K (keterangan setelah predikat).
- `Di rumah aku bekerja.` → S-P-K (keterangan sebelum subjek).

Perbaikan batas frasa memastikan kata `rumah` pada contoh kedua tidak diserap ke dalam subjek `aku`. Pola yang diterima dibatasi pada PREP + frasa nominal sederhana yang berakhir tepat sebelum subjek. Token awal yang tidak cocok dengan pola tersebut tidak otomatis dianggap keterangan.

Dua tes unit dan satu tes integrasi melalui kamus 3.000 lema ditambahkan. GitHub Actions [Run #87](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45944311484) sukses: **204/204 regression tests lulus**. Validasi relasi lima batch terpilih, struktur kamus 60 batch/3.000 lema, dataset POS, dan evaluasi development juga berhasil.

**Batas:** dukungan ini belum mencakup inversi, klausa majemuk, atau seluruh variasi susunan kalimat. Tahap parser berikutnya tetap perlu memperluas variasi secara terukur tanpa menebak fungsi token yang belum jelas.


## Parser kalimat v0.8 — beberapa keterangan preposisional di depan subjek — 27 November 2026

Parser kini dapat mengenali lebih dari satu frasa keterangan preposisional sederhana yang muncul berurutan sebelum subjek.

Contoh: `Di rumah pada malam hari aku bekerja.`
- Keterangan 1: `di rumah`
- Keterangan 2: `pada malam hari`
- Subjek: `aku`
- Predikat: `bekerja`
- Pola: S-P-K

Urutan keterangan dipertahankan. Parser hanya menerima awalan jika seluruh token sebelum subjek dapat dibagi menjadi rangkaian PREP + frasa nominal; jika ada bagian yang tidak cocok, bagian tersebut tidak dipaksakan menjadi keterangan.

Satu tes unit dan satu tes integrasi melalui kamus 3.000 lema ditambahkan. GitHub Actions [Run #88](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45944536094) sukses: **206/206 regression tests lulus**. Validasi relasi lima batch terpilih, struktur kamus 60 batch/3.000 lema, dataset POS, dan evaluasi development juga berhasil.

**Batas:** keterangan depan yang dipisahkan tanda baca, klausa bertingkat, dan susunan campuran di luar pola PREP + frasa nominal sederhana belum didukung.


## Parser kalimat v0.9 — koordinasi frasa nominal sederhana — 27 November 2026

Parser dapat mengenali koordinasi sederhana pada subjek dan objek jika konjungsi diidentifikasi secara eksplisit sebagai CONJ.

Contoh:
- `Aku dan dia bekerja.` → subjek `aku dan dia`, predikat `bekerja`.
- `Aku membeli nasi dan roti.` → subjek `aku`, predikat `membeli`, objek `nasi dan roti`.

Perluasan hanya menggabungkan rentang nominal pada sisi kiri/kanan konjungsi. Parser tidak menyimpulkan unsur yang dihilangkan dan tidak menganggap setiap kata `dan` otomatis sebagai penghubung klausa.

Dua tes unit dan satu tes integrasi melalui kamus 3.000 lema ditambahkan. GitHub Actions [Run #89](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45944727020) sukses: **209/209 regression tests lulus**. Validasi relasi lima batch terpilih, struktur kamus 60 batch/3.000 lema, dataset POS, dan evaluasi development juga berhasil.

**Batas:** koordinasi klausa penuh, elipsis, dan konstruksi bertingkat belum didukung. Tahap berikutnya dapat memodelkan koordinasi klausa secara terpisah agar tidak merusak analisis satu klausa yang sudah stabil.


## Parser kalimat v1.0 — dua klausa koordinatif sederhana — 27 November 2026

Parser kini dapat mengenali pola dua klausa eksplisit yang dihubungkan satu konjungsi teridentifikasi sebagai CONJ, jika kedua segmen masing-masing memiliki verba teridentifikasi.

Contoh `Aku bekerja dan dia makan.` menghasilkan dua analisis klausa:
1. Subjek `aku`, predikat `bekerja`.
2. Penghubung `dan`; subjek `dia`, predikat `makan`.

Setiap segmen dianalisis ulang oleh parser klausa sederhana yang sudah ada. Hasil tingkat atas menggunakan pola `KLAUSA-KOORDINATIF` dan menyimpan hasil di `clauses`. Field `roles` tingkat atas tetap kosong karena hasilnya terdiri dari dua klausa, bukan satu kerangka S-P-O.

Pemisahan hanya dilakukan jika tepat satu konjungsi teridentifikasi dan kedua sisi memiliki VERB. Karena itu koordinasi frasa nominal seperti `Aku dan dia bekerja` dan `Aku membeli nasi dan roti` tetap diproses oleh aturan v0.9, bukan dipotong sebagai klausa.

Tes unit dan integrasi melalui kamus asli ditambahkan. GitHub Actions [Run #90](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45944957796) sukses: **213/213 regression tests lulus**. Validasi kamus 60 batch/3.000 lema, relasi leksikal lima batch terpilih, dataset POS, dan evaluasi development juga berhasil.

**Batas:** hanya dua klausa dengan satu konjungsi eksplisit; koordinasi bertingkat, elipsis, relasi semantik antarklausa, dan pemisahan berdasarkan koma belum didukung.


## Parser kalimat v1.1 — koordinasi tiga klausa atau lebih — 27 November 2026

Kemampuan koordinasi klausa diperluas dari dua menjadi beberapa klausa berurutan. Parser mengumpulkan posisi konjungsi yang teridentifikasi sebagai CONJ, membagi token menjadi segmen, lalu hanya menerima pemisahan jika setiap segmen memiliki setidaknya satu VERB teridentifikasi dan analisis tiap segmen menghasilkan status `parsed` atau `partial`.

Contoh `Aku bekerja dan dia makan dan mereka belajar.` menghasilkan tiga analisis klausa berurutan:
1. Subjek `aku`, predikat `bekerja`.
2. Penghubung `dan`; subjek `dia`, predikat `makan`.
3. Penghubung `dan`; subjek `mereka`, predikat `belajar`.

Konjungsi tetap disimpan per klausa agar urutan hubungan eksplisit tidak hilang. Jika satu segmen tidak memiliki verba, parser tidak memaksakan pemisahan dan kembali ke jalur analisis satu klausa; ini menjaga koordinasi frasa nominal seperti `Aku dan dia bekerja`.

Tes unit mencakup tiga klausa, kompatibilitas dua klausa, dan kasus yang harus ditolak; tes integrasi memakai pipeline kamus 3.000 lema. GitHub Actions [Run #91](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45954434150) sukses: **217/217 regression tests lulus**. Validasi kamus, dataset POS, dan evaluasi development juga berhasil.

**Batas:** semua klausa harus memiliki verba eksplisit yang dikenali. Elipsis, subjek/predikat yang dihilangkan, koordinasi bertingkat, serta pemahaman relasi sebab-akibat/pertentangan antarklausa belum didukung.

## Parser kalimat v1.2 — klasifikasi penghubung antarklausa — 27 November 2026

Hasil pemisahan klausa kini menyimpan field tambahan `relation_to_previous` pada setiap klausa setelah klausa pertama. Label diberikan hanya untuk penghubung yang tercantum eksplisit di parser:
- `dan` → penambahan; `atau` → alternatif.
- `tetapi` dan `namun` → pertentangan.
- `karena` dan `sebab` → sebab.
- `walaupun` dan `meskipun` → konsesi.
- `lalu` dan `kemudian` → urutan; `ketika` → temporal.
- Penghubung lain diberi `belum_diklasifikasikan`, bukan ditebak. Klausa pertama memakai `null` karena tidak memiliki penghubung sebelumnya.

Empat tes unit memeriksa sebab, pertentangan, konsesi, dan penghubung yang belum dikenal. Satu tes integrasi membuktikan `namun` dikenali sebagai CONJ melalui kamus 3.000 lema dan menghasilkan label pertentangan. GitHub Actions [Run #93](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45955025367) sukses: **222/222 regression tests lulus**; validasi kamus 60 batch/3.000 lema, dataset POS, evaluasi development, dan validasi relasi terpilih juga berhasil.

**Batas:** label ini mengklasifikasikan fungsi penghubung yang eksplisit, bukan memahami seluruh hubungan semantik. Tes `karena` dan `walaupun` saat ini memakai POS terkendali; arah sebab-akibat, klausa sebab yang didahulukan, konstruksi konsesif bertanda koma, klausa tanpa verba eksplisit, serta relasi bertingkat belum didukung.

## Parser kalimat v1.3 — klausa subordinatif di depan klausa utama — 27 November 2026

Parser kini mengenali pola terbatas `penghubung subordinatif + klausa berverba + koma + klausa utama`. Untuk pola yang diterima, hasil memakai `KLAUSA-SUBORDINATIF`, menyimpan analisis kedua klausa secara terpisah, dan mencatat `relation_to_next` pada klausa subordinatif awal.

Contoh integrasi melalui kamus 3.000 lema:
- `Karena dia makan, aku pulang.` → klausa awal berelasi sebab dengan klausa utama.
- `Ketika dia makan, aku pulang.` → klausa awal berelasi temporal dengan klausa utama.

Tes unit juga memastikan klausa eliptis `Walaupun lelah, dia bekerja.` tidak dipaksakan menjadi klausa subordinatif karena klausa awal belum memiliki verba/predikat yang dapat dipastikan. GitHub Actions [Run #96](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45955536612) sukses: **227/227 regression tests lulus**; validasi kamus 60 batch/3.000 lema, dataset POS, evaluasi development, dan validasi relasi terpilih berhasil.

**Batas:** pola ini hanya menerima satu klausa subordinatif di depan, satu koma pemisah, dan klausa awal dengan predikat yang dikenali. Klausa eliptis seperti `Walaupun lelah`, beberapa klausa subordinatif, tanda koma bertingkat, dan relasi semantik yang lebih dalam belum didukung. Contoh integrasi memakai kata-kata yang sudah tercakup dan teridentifikasi oleh pipeline.


## Parser kalimat v1.4 — klausa konsesif eliptis berpredikat adjektival — 27 November 2026

Parser kini dapat menangani satu bentuk elipsis yang dibatasi ketat pada klausa konsesif di depan kalimat, misalnya `Walaupun lelah, dia bekerja.`. Jika token klausa awal seluruhnya dikenali sebagai adverbia pewatas dan predikat adjektival, parser mencatat predikat adjektival itu tetapi membiarkan subjek kosong. Hasil tingkat atas tetap `partial`, bukan `parsed`, karena subjek yang dilesapkan tidak disimpulkan atau disalin dari klausa utama.

Tes integrasi menggunakan kamus 3.000 lema memastikan `lelah` dikenali sebagai ADJ dan `dia bekerja` dianalisis sebagai klausa utama. Tes unit juga memastikan awalan yang hanya berisi adverbia tanpa predikat adjektival tidak diterima.

**Batas:** hanya klausa konsesif awal dengan pola token ADV/ADJ yang berakhir pada ADJ. Parser tidak menebak subjek eliptis, tidak menangani elipsis verba, dan tidak menggeneralisasi aturan ini ke klausa sebab atau temporal.


Validasi GitHub Actions Run #97 berhasil: **229/229 regression tests lulus**. Validasi struktur kamus memuat 60 batch/3.000 lema, validasi dataset POS, evaluasi development, dan validasi relasi pada batch terpilih juga sukses. [Lihat Run #97](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45956239387).


## Parser kalimat v1.5 — klausa subordinatif setelah klausa utama — 27 November 2026

Parser kini mengenali pola klausa utama yang diikuti klausa subordinatif dengan penghubung eksplisit, misalnya `Aku pulang karena hujan turun.`. Pemeriksaan subordinasi dilakukan sebelum pemisahan koordinasi agar penghubung seperti `karena`, `ketika`, dan `walaupun` tidak keliru diperlakukan sebagai konjungsi setara.

Klausa utama dan klausa subordinatif disimpan terpisah. Hubungan sebab, temporal, atau konsesi dicatat hanya jika penghubungnya termasuk daftar eksplisit. Tes unit mencakup contoh sebab dan temporal; tes integrasi memakai kalimat sebab melalui kamus 3.000 lema.

**Batas:** setiap sisi harus dapat dianalisis sebagai klausa `parsed` atau `partial`; elipsis pada klausa subordinatif akhir, beberapa penghubung subordinatif dalam satu kalimat, dan relasi semantik yang tidak tercantum belum dipaksakan.


Validasi GitHub Actions Run #99 berhasil: **232/232 regression tests lulus**. Validasi kamus 60 batch/3.000 lema, dataset POS, evaluasi development, dan validasi relasi batch terpilih juga sukses. [Lihat Run #99](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45956517467).


## Keputusan urutan pengembangan — prioritas kembali ke Tahap 2.5 — 27 November 2026

Setelah meninjau urutan tahapan, pengembangan parser dihentikan sementara. Parser v1.5, implementasi, dan tesnya tetap berada di repository; tidak ada rollback atau penghapusan. Namun, fitur parser baru tidak dikerjakan sebelum fondasi POS development dinilai memadai.

### Prioritas pertama: abstention VERB

Daftar sasaran terdiri dari delapan kemunculan: `bekerja` (3), `ditunda`, `letakkan`, `menjelaskan`, `hinggap`, dan `berteduh`. Audit dilakukan satu per satu. Untuk setiap kasus, diagnosis harus membedakan kebutuhan lema baru, aturan morfologi, anotasi `derived_forms_pos`, atau masalah pada alur pencocokan/POS. Keberadaan anotasi turunan sebelumnya harus diperiksa sebelum menambahkan perubahan baru.

Setiap kasus diperiksa terlebih dahulu, lalu hanya diperbaiki jika penyebabnya terbukti. Tes terkait dijalankan sebelum beralih ke kasus berikutnya. Tidak boleh mengubah test set untuk menyetel aturan.

### Prioritas setelah VERB

1. Audit abstention ADJ (2), ADV (3), dan NOUN (19) secara bertahap.
2. Perluas cakupan lema NOUN yang belum terindeks.
3. Audit cakupan morfologi `ber-`, pasif `di-`, dan imperatif.
4. Evaluasi ulang pada development split dan jalankan regresi. Test set tetap ditahan untuk evaluasi akhir.

### Gerbang sebelum Tahap 2.6

Tahap 2.6 (analisis struktur kalimat dasar) belum dinyatakan dimulai. Tahap 2.5 harus lebih dahulu memiliki hasil evaluasi POS development yang memadai dan terdokumentasi. Tahap 2.7, tahap hubungan makna/konteks, dan integrasi Android tetap menunggu urutan tersebut.

Daftar abstention adalah sasaran audit, bukan target untuk memaksa semua token memperoleh label. Abstention yang tepat untuk kasus ambigu tetap merupakan perilaku yang sah.


## Pemutakhiran titik lanjut POS berdasarkan Run #99 — 27 November 2026

Catatan historis yang menyebut delapan kemunculan VERB abstain telah diperbarui oleh hasil evaluasi berikutnya. GitHub Actions Run #99 pada 60 kalimat development mencatat **tiga** abstention VERB: `ditunda`, `hinggap`, dan `berteduh`. Token `bekerja` yang muncul tiga kali pada `pos_0005`, `pos_0025`, dan `pos_0052` sudah teridentifikasi; begitu pula `menjelaskan` dan `letakkan` pada pengujian development/pipeline terkait.

Karena itu `bekerja` dinyatakan selesai: anotasi `derived_forms_pos` pada lema `kerja` memberi VERB secara eksplisit tanpa mewarisi POS NOUN lema. Tidak perlu menambah aturan `ber-` umum atau mengubah kamus lagi untuk kasus ini. Langkah diagnosis berikutnya adalah `ditunda`, lalu `hinggap` dan `berteduh` satu per satu. Hasil Run #99: [GitHub Actions](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45956517467). Test set tetap tidak digunakan.


## Tahap 2.5 — penanganan `ditunda` — 27 November 2026

Pemeriksaan pada seluruh 60 batch memastikan lema `tunda` belum tersedia. Karena aturan morfologi pasif `di-` sudah ada, masalah ini bukan alasan untuk memperluas aturan prefiks secara umum. Ditambahkan lema `tunda` dengan POS VERB pada batch-060, beserta bentuk turunan `ditunda` dan anotasi POS eksplisit `derived_forms_pos` bernilai VERB. Indeks `s-u.tsv` diperbarui dan validator kamus penuh kini mengharapkan 3.001 lema. Tes integrasi baru memakai kalimat development `Karena hujan deras, pertandingan ditunda.` untuk memastikan token `ditunda` dikenali sebagai VERB dari kamus. Test set tidak digunakan. Hasil workflow masih menunggu.


## Hasil verifikasi penambahan `tunda` — GitHub Actions Run #101

Run #101 berhasil. Kamus memuat 60 batch dan 3.001 lema; tes integrasi mengonfirmasi `ditunda` dikenali sebagai VERB dari kamus. Regresi penuh **233/233 tes lulus**. Evaluasi POS development kini mencatat dua abstention VERB: `hinggap` dan `berteduh`; `ditunda` tidak lagi abstain. Abstention NOUN untuk `pertandingan` masih tercatat sebagai masalah morfologi terpisah dan tidak boleh disamakan dengan keberhasilan pengenalan `ditunda`. Test set tetap tidak digunakan. [GitHub Actions Run #101](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45958528991).


## Hasil penambahan `hinggap` — GitHub Actions Run #102

Pemeriksaan dilakukan melalui indeks kamus sesuai alur kerja: `hinggap` belum tercatat. Lema K3003 ditambahkan sebagai VERB pada batch-060 dan dicatat pada indeks `g-i.tsv`. Tes integrasi development `Burung hinggap pada pagar.` memastikan POS VERB berasal dari kamus. Run #102 berhasil: 60 batch, 3.002 lema, dan **234/234 tes regresi lulus**. Evaluasi development menunjukkan abstention VERB tersisa satu, yaitu `berteduh`. Test set tetap tidak digunakan untuk penyetelan. [GitHub Actions Run #102](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45958936060).


## Hasil penambahan `berteduh` — GitHub Actions Run #103

Indeks kamus tidak mencatat `berteduh` maupun lema dasar `teduh`. Karena itu `berteduh` ditambahkan sebagai lema VERB mandiri K3004 pada batch-060 dan indeks `a-c.tsv`. Tes integrasi development memastikan kalimat `Ketika hujan turun, mereka berteduh.` dikenali sebagai VERB dari kamus. Run #103 berhasil: 60 batch, 3.003 lema, **235/235 tes regresi lulus**. Evaluasi development kini menunjukkan **0 abstention VERB**; abstention ADJ tersisa 2 (`baru`), ADV 3 (`tetap` dua kali dan `dulu`), NOUN 19. Test set tetap tidak digunakan untuk penyetelan. [GitHub Actions Run #103](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45959093568).


## Hasil penambahan `baru` (ADJ) — GitHub Actions Run #104

INDEX belum mencatat `baru` (lema `barusan` yang sudah ada berbeda). Ditambahkan K3005 sebagai ADJ dengan definisi untuk makna adjektival dan catatan bahwa penggunaan adverbial akan dievaluasi pada tahap ADV. Tes integrasi mencakup dua konteks development `buku baru`. Run #104 berhasil: 60 batch, 3.004 lema, 236/236 tes regresi. Evaluasi development kontekstual: ADJ 23/23 dikenali, tidak ada abstention ADJ dan tidak ada kesalahan prediksi. Abstention ADV tersisa `tetap` (2 konteks) dan `dulu` (1 konteks). [GitHub Actions Run #104](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45959314201).


## Penambahan `dulu` (ADV) — menunggu validasi

Atas persetujuan pengguna, lema K3006 `dulu` ditambahkan sebagai ADV. Definisi mencakup penggunaan temporal masa lampau dan urutan tindakan. INDEX `d-f.tsv` diperbarui; tes integrasi mencakup dua kalimat development: `Gue mau makan dulu.` dan `Dulu dia tinggal di sini.`. GitHub Actions Run #105 berhasil: 60 batch, 3.005 lema, dan 237/237 tes regresi lulus. Evaluasi development kontekstual naik menjadi coverage 91,8% (234/255), selective accuracy 100%; abstention ADV tinggal dua kemunculan `tetap`, sedangkan NOUN masih 19. Test set tetap tidak digunakan.

Keputusan yang tetap berlaku: `tetap` ditunda sampai analisis dua fungsi POS (ADJ dan ADV); `adiknya`, `pelajaran`, `pertandingan`, dan `pemandangan` tidak ditambahkan sebagai lema baru tanpa evaluasi morfologi; nama orang tidak dimasukkan ke kamus inti. Penambahan lema lain tetap memerlukan persetujuan eksplisit pengguna.


Validasi penambahan `dulu` selesai: [GitHub Actions Run #105](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45961206191).


## Penambahan lema `tetap` (ADJ + ADV) — menunggu validasi

Atas persetujuan pengguna, K3007 `tetap` ditambahkan dengan dua sense terpisah: ADJ (tidak berubah/konstan/tidak goyah) dan ADV (melakukan hal yang sama seperti sebelumnya/tidak berhenti). POS entri memuat kedua label; masing-masing sense memiliki POS spesifik. Aturan konteks yang sangat terbatas memilih ADV ketika `tetap` langsung mendahului token yang telah dikenali sebagai VERB. Contoh `pegawai tetap` tetap ambigu dan tidak dipaksa. INDEX `s-u.tsv` diperbarui. Validasi GitHub Actions masih menunggu.


## Hasil validasi penambahan `tetap` — GitHub Actions Run #108

Run #108 berhasil: 60 batch, **3.006 lema**, dataset POS 100 kalimat/543 token, dan **239/239 tes regresi lulus**. Pada development split (255 token resolved), evaluasi kontekstual menghasilkan 236 prediksi benar, coverage 92,5%, accuracy 92,5%, dan selective accuracy 100%. Abstention ADV menjadi **0** (20/20 ADV dikenali); NOUN masih 19 abstention. Satu token ADJ tetap abstain secara konservatif. Test set tidak digunakan untuk penyetelan. Aturan konteks baru hanya memilih ADV untuk `tetap` yang langsung mendahului token VERB; kasus tanpa bukti yang cukup tetap dibiarkan ambigu. [GitHub Actions Run #108](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45961614138).
