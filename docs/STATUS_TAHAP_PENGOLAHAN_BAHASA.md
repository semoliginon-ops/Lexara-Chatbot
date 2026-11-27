# Catatan Teknis — Sistem Bahasa

Dokumen ini menyimpan **keputusan teknis, perilaku komponen, batasan, dan hasil eksperimen penting** agar alasan di balik implementasi tidak hilang.

- **Peta kemajuan dan status tahapan:** [CHECKLIST_PENGEMBANGAN.md](CHECKLIST_PENGEMBANGAN.md)
- **Gambaran proyek:** [README.md](../README.md)
- **Skema dan aturan kamus:** [KAMUS.md](KAMUS.md)
- **Dataset POS:** [DATASET_POS.md](DATASET_POS.md)

Dokumen ini bukan checklist kedua dan bukan sumber utama status tahapan. Perubahan kecil pada checklist tidak mengharuskan dokumen ini ikut diperbarui. Tambahkan catatan di sini jika ada keputusan desain, perubahan perilaku, hasil pengujian penting, atau batasan baru yang perlu dipertahankan.

---

## 1. Ruang lingkup dan prinsip teknis

Sistem Bahasa adalah fondasi pemrosesan Bahasa Indonesia yang dirancang berjalan lokal/offline. Komponen mengolah teks melalui normalisasi, tokenisasi, pencocokan leksikal, morfologi, POS, dan analisis struktur kalimat.

Batas tujuan:
- Bukan LLM dan tidak memuat model GGUF.
- Tidak mengandalkan layanan cloud atau API berbayar untuk pemrosesan inti.
- Belum dapat diklaim memiliki pemahaman atau generasi bahasa bebas setara LLM.
- Kemampuan harus dinilai per komponen, pola, dan data uji yang benar-benar tersedia.

Prinsip implementasi:
- Pertahankan ambiguitas jika bukti belum cukup; abstention lebih baik daripada menebak.
- Jangan mengubah lemma, POS, sense, atau definisi kamus hanya untuk menyesuaikan satu aturan.
- Normalisasi tidak boleh menghapus informasi yang berpotensi mengubah makna.
- Bentuk informal/slang dan tanda baca dipertahankan kecuali ada aturan teruji.
- Perubahan parser harus disertai tes unit dan tes integrasi yang relevan.
- Jaga kompatibilitas antarmuka yang sudah dipakai komponen lain.
- Jangan menggunakan test split untuk menyetel aturan.

## 2. Baseline komponen

| Komponen | Implementasi | Perilaku / batas penting |
|---|---|---|
| Normalisasi | `tools/normalisasi.py` | Unicode NFC, casefold, merapikan whitespace. Tidak membakukan slang, menghapus tanda baca, atau melakukan stemming. |
| Tokenisasi | `tools/tokenizer.py` | Memisahkan kata dan tanda baca; bentuk bertanda hubung/apostrof internal dipertahankan. |
| Loader kamus | `tools/kamus_loader.py` | Membaca batch JSONL dan memvalidasi struktur; data sumber tidak dimodifikasi oleh loader. |
| Pencocokan leksikal | `tools/pencocokan_kamus.py` | Mencocokkan lemma, variants, dan derived_forms; mempertahankan seluruh kandidat/sense/POS. |
| Pipeline teks | `tools/analisis_teks.py` | Menghubungkan normalisasi, tokenizer, dan pencocokan kamus. Indeks leksikal dapat digunakan ulang. |
| Morfologi | `tools/morfologi.py` | Menghasilkan kandidat analisis imbuhan yang divalidasi melalui kamus; bukan stemming bebas. |
| POS | `tools/pos_tagger.py`, `tools/pos_context.py` | POS leksikal dan disambiguasi kontekstual konservatif. Ambiguitas dan abstention dipertahankan. |
| Parser | `tools/parser_kalimat.py` | Analisis struktur kalimat berbasis aturan eksplisit; fitur yang belum didukung tetap unresolved/partial. |

### Kamus dan indeks

- Kondisi yang tercatat pada validasi terbaru: **60 batch, 3.014 lema**.
- Indeks kamus terdiri dari delapan shard alfabet di `data/kamus/index/`.
- Pemeriksaan keberadaan kata baru dilakukan melalui indeks terlebih dahulu.
- Setiap penambahan lema baru wajib mendapat persetujuan eksplisit pengguna. Setelah disetujui, sumber batch dan indeks harus diperbarui bersama.
- Jangan melakukan audit ulang seluruh batch tanpa alasan teknis yang jelas atau permintaan pengguna.

### Morfologi

Morfologi adalah analisis kandidat, bukan pemotongan imbuhan secara membabi buta. Bentuk dasar harus ditemukan di indeks kamus sebelum kandidat dilaporkan. Kata yang sudah cocok persis dengan kamus tidak boleh di-stem.

Cakupan prototipe yang pernah ditambahkan mencakup sejumlah pola prefiks dan konfiks, antara lain bentuk ber-, di-, meN-, peN-, ke-an, per-an, dan bentuk bertingkat tertentu. Cakupan ini **belum merupakan inventaris lengkap morfologi Bahasa Indonesia**.

Tes negatif penting mencegah kata leksikal seperti `beranda`, `kemari`, `terong`, `selalu`, `melati`, `kelapa`, `perang`, `terapi`, dan `mereka` salah dipotong sebagai bentuk berimbuhan. Kasus prefiks bertumpuk `penge-`/`pen-`, lema ambigu, `memperindah`, `memperbaiki`, `mempermainkan`, dan `diperbaiki` juga pernah dimasukkan ke pengujian.

## 3. POS dan dataset

Dataset POS yang tercatat: **100 kalimat / 543 token**, terdiri dari 60 kalimat development dan 40 kalimat test.

Hasil evaluasi development kontekstual pada snapshot Run #126:
- 250 dari 255 token yang dievaluasi dikenali.
- Coverage: 98,0%.
- Accuracy: 98,0%.
- Selective accuracy: 100,0% pada prediksi yang dikeluarkan.
- Lima abstention berkaitan dengan nama orang.

Angka tersebut hanya menggambarkan dataset development yang tersedia, bukan akurasi umum untuk seluruh Bahasa Indonesia. Test split 40 kalimat dipertahankan sebagai data tersegel dan tidak digunakan untuk penyetelan.

Keputusan POS:
- Nama orang ditunda ke tahap pengenalan entitas/konteks; jangan memaksanya menjadi lema kamus atau label POS pada tahap ini.
- POS spesifik-sense dipertahankan.
- POS lema tidak otomatis diwariskan ke bentuk turunan; anotasi POS turunan harus eksplisit jika diperlukan.
- Kata dengan lebih dari satu fungsi POS tidak boleh dipaksa ke satu label tanpa bukti konteks yang memadai.

## 4. Parser kalimat — riwayat kemampuan

Parser dikembangkan bertahap. Nomor versi menunjukkan versi implementasi, **bukan** klaim bahwa seluruh tata bahasa telah tercakup.

| Versi | Penambahan utama |
|---|---|
| v0.1 | Pola klausa dasar S-P, S-P-O, dan S-P-K. |
| v0.2 | Rentang frasa nominal sederhana. |
| v0.3 | Penanganan negasi `tidak` dan `belum`. |
| v0.4 | Pola modal terbatas seperti `mau`, `ingin`, dan `hendak`. |
| v0.5 | Dukungan konservatif untuk predikat nonverbal. |
| v0.6 | Predikat penghubung tertentu, termasuk `menjadi` dan `tampak`, dengan pola S-P-Pel. |
| v0.7–v0.8 | Keterangan preposisional di depan klausa, termasuk beberapa keterangan berurutan. |
| v0.9 | Koordinasi subjek/objek nominal. |
| v1.0–v1.1 | Pemisahan dua atau lebih klausa koordinatif dengan konjungsi eksplisit. |
| v1.2 | Label relasi penghubung yang dikenal, misalnya penambahan, alternatif, pertentangan, sebab, konsesi, urutan, dan temporal. |
| v1.3–v1.5 | Klausa subordinatif di depan dan setelah klausa utama; satu pola konsesif eliptis ditandai `partial`. |
| v1.6 | `predicate_structure` memisahkan kepala predikat dan pewatas; `roles.predicate` dipertahankan demi kompatibilitas. |
| v1.7 | `akan` (ADV) dan `bisa` (VERB) dikenali sebagai modal hanya sebelum verba inti. `bisa` tunggal tetap dapat menjadi predikat. |
| v1.8 | Empat ADV temporal eksplisit (`besok`, `nanti`, `sekarang`, `tadi`) dapat dicatat sebagai keterangan awal. ADV lain tidak otomatis dianggap temporal. |
| v1.9 | Memperketat batas keterangan preposisional awal dan kandidat subjek. Inversi K-P-S penuh belum didukung. |

### Perilaku baseline v1.9 yang harus dipertahankan

1. `Di rumah aku bekerja.`
   - `di rumah` dicatat sebagai keterangan.
   - `aku` tetap menjadi kandidat subjek.
2. `Di rumah terdengar suara.`
   - `di rumah` dicatat sebagai keterangan.
   - `terdengar` dikenali sebagai predikat.
   - Subjek dibiarkan kosong dan `suara` tetap unresolved; jangan dipaksakan menjadi objek atau subjek.
3. Parser tidak mengklaim mendukung inversi K-P-S secara umum.
4. Jika struktur tidak cukup didukung aturan eksplisit, pertahankan status unresolved/partial.
5. Perubahan v1.9 tidak mengubah kamus atau menambah lema.

### Kontrak kompatibilitas

- Field lama `roles.predicate` harus tetap tersedia meskipun struktur predikat terperinci ditambahkan.
- `predicate_structure` menyediakan kepala predikat dan modifier yang dikenali tanpa menghilangkan urutan token.
- Jangan mengubah hasil yang sudah dipakai komponen lain tanpa tes regresi yang memeriksa kompatibilitas.

## 5. Hasil validasi terpadu yang menjadi bukti baseline

GitHub Actions [Run #126](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45972629322) berstatus **completed / success**.

Cakupan yang divalidasi pada run tersebut:
- Validasi kamus: 60 batch / 3.014 lema.
- Validasi dataset POS.
- Evaluasi POS development.
- Regression suite: **255/255 tes lulus**.

Run #125 sebelumnya gagal setelah perubahan batas keterangan awal karena pronomina ikut tertelan ke dalam frasa preposisional. Perbaikannya mempertahankan pronomina orang sebagai kandidat subjek; Run #126 kemudian berhasil. Catatan ini penting sebagai alasan mengapa perilaku v1.9 diuji secara khusus.

Kelulusan Run #126 membuktikan tes yang tercakup dalam workflow tersebut lulus pada commit yang diuji. Itu bukan bukti bahwa semua kata, semua konstruksi sintaksis, atau seluruh tata bahasa telah tervalidasi.

## 6. Batasan yang diketahui

- Morfologi masih berupa prototipe berbasis pola dan kamus, belum mencakup seluruh variasi morfofonemik, reduplikasi, dan imbuhan.
- POS kontekstual diuji pada dataset terbatas; nama orang masih ditunda.
- Parser merupakan parser aturan terbatas, bukan parser tata bahasa lengkap.
- Inversi K-P-S penuh belum didukung.
- Relasi penghubung hanya diklasifikasikan jika termasuk daftar eksplisit; relasi semantik yang lebih dalam belum dipahami.
- Klausa eliptis, koordinasi bertingkat, dan struktur ambigu tertentu tetap dapat menghasilkan unresolved/partial.
- Tahap hubungan makna/konteks, mesin pembentukan respons, integrasi Android offline, dan evaluasi perangkat merupakan pekerjaan roadmap terpisah.

## 7. Cara memperbarui dokumen ini

Perbarui dokumen ini hanya jika ada hal teknis yang layak menjadi catatan kesinambungan, misalnya:
- keputusan desain atau perubahan kontrak antarmodul;
- penambahan kemampuan parser/morfologi/POS beserta batasnya;
- hasil regresi penting atau kegagalan yang menghasilkan pelajaran teknis;
- perubahan arsitektur atau keterbatasan yang perlu diketahui saat melanjutkan proyek.

Untuk perubahan status tahap, centang dan perbarui **CHECKLIST_PENGEMBANGAN.md**. Jangan menyalin seluruh checklist ke dokumen ini.