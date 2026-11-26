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
- Total: **45 tes lulus, 0 gagal**, dijalankan di lingkungan Python lokal terisolasi menggunakan salinan file dari GitHub. GitHub Actions tidak dijalankan.
- Struktur dasar seluruh 60 file batch (3.000 entri) telah diperiksa melalui konten GitHub: format JSON, field wajib, ID, lema, dan struktur sense. Ini bukan pengganti eksekusi langsung loader Python terhadap seluruh file.
- Pencocokan token ke lemma, variants, dan derived_forms sudah dibuat.
- Integrasi normalisasi, tokenizer, dan pencocokan kamus tersedia di `tools/analisis_teks.py` melalui fungsi `analyze_text(text, lexicon)`. Indeks leksikal dibangun sekali dengan `build_lexicon(entries)` lalu dapat digunakan ulang untuk beberapa masukan.
- Analyzer mengembalikan teks ternormalisasi serta hasil per token: kata cocok/tidak dikenal atau tanda baca. Semua kandidat dipertahankan; POS dan sense tidak dipilih otomatis.
- 8 regression tests analyzer lulus pada lingkungan Python lokal terisolasi.
- Prototipe morfologi tersedia di `tools/morfologi.py` melalui `analyze_morphology(token, lexicon)`. Versi terbaru menambahkan kandidat konfiks ke-an, per-an, peN-an, bentuk menge-, serta perapian urutan prefiks. Kandidat hanya dikembalikan jika bentuk dasarnya ditemukan dalam indeks kamus.
- Versi morfologi terkini memiliki **40 regression tests yang telah dijalankan pada lingkungan Python lokal terisolasi: 40 lulus, 0 gagal**. Tes negatif mencakup bentuk leksikal `beranda`, `kemari`, `terong`, `selalu`, `melati`, `kelapa`, `perang`, `terapi`, dan `mereka` agar tidak salah dipotong sebagai imbuhan. Tes tambahan juga memastikan prefiks `penge-` tidak menghasilkan kandidat palsu melalui pemotongan `pen-`, mempertahankan seluruh POS dan sense ketika lema dasar ambigu, serta mencakup bentuk `memperindah`. Kasus `memperbaiki` dan `mempermainkan` telah dijalankan bersama suite. Tes baru `diperbaiki` memverifikasi imbuhan bertingkat `di- + per- + -i` dan menghasilkan kandidat `baik`.
- Total pengujian komponen yang telah dijalankan secara terpisah kini **93 tes lulus, 0 gagal** (45 fondasi + 8 analyzer + 40 morfologi). Ini bukan satu kali eksekusi gabungan seluruh tes. Pengujian morfologi memakai implementasi pencocokan leksikal repository dalam lingkungan Python lokal terisolasi.
- Belum ada integrasi Android.

## 4. Pekerjaan yang sedang dikerjakan

**Subtahap 2.1 dan 2.2 selesai; fondasi loader untuk 2.3 sudah tersedia.**

Normalisasi lulus 8/8 tes, tokenizer 12/12, loader 12/12, dan pencocokan kamus 13/13. Total 45/45 regression tests lulus pada lingkungan Python lokal terisolasi. Struktur dasar seluruh 60 batch (3.000 entri) juga telah diperiksa dari konten GitHub. Namun, eksekusi fungsi loader Python terhadap seluruh 60 file aktual belum dilakukan. Pencocokan token terhadap lema, variants, dan derived_forms sudah tersedia.

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
- [ ] Jalankan fungsi loader Python langsung terhadap seluruh 60 file batch aktual; audit struktur melalui konten GitHub saja belum mencukupi.
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

**Titik lanjut:** validasi loader terhadap seluruh 60 batch aktual masih perlu dijalankan dengan `python -m tools.validasi_kamus_lengkap` pada checkout repository. Struktur dasar 3.000 entri telah diperiksa melalui konten GitHub. Versi morfologi terbaru memperbaiki konflik prefiks bertumpuk agar prefiks terpanjang yang cocok dipakai dan kandidat palsu dari pemotongan prefiks pendek tidak ikut dihasilkan. Aturan prefiks `memper-` juga ditambahkan agar bentuk seperti `memperindah` dapat menghasilkan kandidat lema `indah`; tes negatif untuk bentuk tak dikenal menggunakan `memperxyz`. Sebanyak 38 tes morfologi lulus; total 91 tes komponen lulus secara terpisah. Tes imbuhan bertingkat `diperbaiki` ditambahkan dan dijalankan bersama seluruh suite: 33 lulus, 0 gagal. Aturan baru mengurai lapisan `di-`, lalu `per-`, lalu sufiks `-i`, dengan kandidat akhir tetap harus ditemukan di kamus. Pengujian dilakukan pada lingkungan Python lokal terisolasi menggunakan salinan sumber repository. 


**Pembaruan imbuhan bertingkat:** aturan `di- + per- + sufiks` dibatasi ke sufiks `-i` dan `-kan`; sufiks `-an` dikecualikan agar pola nominal tidak dianggap sebagai bentuk pasif. Tes negatif `diperkerjaan` telah ditambahkan untuk memastikan lema `kerja` tidak dihasilkan. Suite terbaru telah dijalankan setelah penambahan tes negatif: 34 lulus, 0 gagal. Pengujian menggunakan salinan terkini dari `tools/morfologi.py`, `tools/pencocokan_kamus.py`, dan `tests/test_morfologi.py` dalam lingkungan Python lokal terisolasi.

**Pembaruan reduplikasi berprefiks:** `tools/morfologi.py` kini mengenali pola terbatas `ber- + bentuk ulang` seperti `berjalan-jalan` dan `berlari-lari`, dengan syarat bagian setelah tanda hubung cocok persis dengan lema kamus. Dua tes baru dijalankan; suite morfologi terbaru: 36 lulus, 0 gagal. Total pengujian komponen terpisah: 89 lulus, 0 gagal (45 fondasi + 8 analyzer + 36 morfologi).


**Pembaruan restorasi nasal `meng-`:** penambahan kandidat `k+akar` kini dilewati jika bagian setelah `meng-` sudah cocok dengan lema kamus. Ini mencegah kandidat spekulatif seperti `kambil` ketika `ambil` sudah tersedia, tanpa menghilangkan analisis `mengunci` → `kunci` ketika bentuk sisa `unci` tidak ditemukan. Regression suite morfologi terbaru: 38 lulus, 0 gagal; total komponen terpisah: 91 lulus, 0 gagal (45 fondasi + 8 analyzer + 38 morfologi). Pengujian memakai salinan terkini dari kode dan tes repository di lingkungan Python lokal terisolasi.


**Pembaruan restorasi nasal `peng-` (terbaru):** aturan restorasi `peng-` kini tidak menambahkan kandidat `k+akar` secara spekulatif apabila bagian setelah `peng-` sudah cocok dengan lema kamus. Regression tests memastikan `pengambil` menghasilkan `ambil`, bukan `kambil`, sementara `pengunci` tetap menghasilkan kandidat `kunci`. Suite morfologi terbaru dijalankan pada salinan sumber dan tes repository di lingkungan Python lokal terisolasi: **40 lulus, 0 gagal**. Total tes komponen yang dijalankan terpisah: **93 lulus, 0 gagal** (45 fondasi + 8 analyzer + 40 morfologi). GitHub Actions tidak dijalankan.