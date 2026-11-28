# Audit Sumber Deskripsi Kandidat Klarifikasi

**Tanggal:** 28 November 2026  
**Status:** audit baca-saja selesai; tidak ada kode atau data kamus diubah.

## 1. Pertanyaan audit

Apakah repo sudah memiliki sumber definisi/glos per sense yang dapat ditampilkan kepada pengguna, dan apakah data tersebut dapat dipetakan kembali ke kandidat pada Context Snapshot tanpa menebak?

## 2. Sumber yang ditemukan

### A. Data kamus kanonis

- Entri kamus berada pada `data/kamus/batch-001.jsonl` sampai `batch-060.jsonl`.
- Skema `docs/KAMUS.md` menetapkan `senses[]` dengan `sense_id` dan `definition`.
- `tools/kamus_loader.py` memuat entri lengkap tanpa mengubah field.
- `tools/pencocokan_kamus.py` menyimpan entri asli secara utuh pada `candidate["entry"]`, bersama `entry_id`, `lemma`, `matched_form`, dan `match_type`.
- `tools/analisis_teks.py` mengembalikan seluruh kandidat dari lookup; tidak memilih sense.
- `tools/context_snapshot.py` menyalin kandidat analisis ke `tokens[].lexical_candidates[]` tanpa membuang objek kandidat.

Maka jalur data yang tersedia adalah:

`snapshot.tokens[token_index].lexical_candidates[candidate_index].entry.senses[sense_index]`

Field `sense_id` dan `definition` pada objek sense dapat menjadi sumber label/uraian pilihan, dengan syarat struktur dan pemetaan diverifikasi pada saat penggunaan. ID internal tetap tidak ditampilkan.

### B. Pemeriksaan contoh entri

| Entri | ID | Sense dan definisi pada kamus |
|---|---|---|
| bangun | K0016 | K0016-S1: “Beralih dari keadaan tidur ke keadaan sadar.”; K0016-S2: “Berdiri atau menjadi tegak dari posisi duduk atau berbaring.” |
| bisa | K0026 | K0026-S1: “Mampu atau sanggup melakukan sesuatu.”; K0026-S2: “Zat beracun yang dapat membahayakan tubuh dan dihasilkan oleh hewan atau organisme tertentu.” |
| tolong | K0032 | K0032-S1: “Membantu atau memberikan bantuan kepada seseorang.”; K0032-S2: “Kata yang digunakan untuk meminta bantuan secara sopan.” |
| jam | K0293 | K0293-S1: “Alat atau penunjuk untuk mengetahui waktu.”; K0293-S2: “Satuan waktu yang terdiri atas enam puluh menit.” |

Pemeriksaan dilakukan pada batch-001 dan batch-006. Definisi di atas berasal langsung dari data kamus proyek, bukan hasil generasi.

## 3. Temuan integrasi penting

1. Snapshot mempertahankan objek kandidat lengkap di `lexical_candidates`, sehingga definisi sense memang dapat dijangkau tanpa menambah data baru atau mengubah kamus.
2. Laporan `interpret_utterance` hanya menyimpan referensi tingkat objek kandidat: `source_field`, `token_index`, dan `candidate_index`.
3. Satu objek kandidat kamus dapat memuat beberapa `senses[]`. Contoh `bangun` mempunyai satu kandidat entri dengan dua sense. Karena itu, ambiguity report v1 menghasilkan satu `candidate_ref`, bukan dua.
4. Planner v1 mensyaratkan sedikitnya dua `candidate_refs`. Jadi planner v1 **tidak dapat** mengeluarkan `ask` untuk ambiguitas dua sense di dalam satu kandidat entri, walaupun definisi kedua sense tersedia.
5. Ini bukan kekurangan definisi kamus. Ini ketidakcocokan granularitas referensi antara laporan interpretasi/planner dan unit pilihan yang diperlukan untuk klarifikasi.

## 4. Keputusan teknis

- Sumber definisi sense tersedia dan cukup untuk merancang presentasi pilihan leksikal berbasis data.
- Sebelum penyaji dapat dipakai, kontrak planner harus diperluas secara terbatas agar fokus dapat merujuk ke sense tertentu di dalam kandidat entri, bukan hanya ke objek kandidat entri.
- Bentuk referensi sense harus tetap dapat ditelusuri: `token_index`, `candidate_index`, dan `sense_index` serta `sense_id` yang harus cocok dengan sumber. Jangan menerima `sense_id` saja tanpa verifikasi indeks/sumber.
- Planner v1 yang ada tetap dipertahankan; perluasan dilakukan sebagai versi kontrak berikutnya dan tes tambahan yang terfokus. Jangan mengubah data kamus atau mengarang kandidat.
- Untuk POS/sintaksis, jangan menampilkan opsi dari kandidat yang tidak menyediakan label sederhana dan jelas. Audit ini hanya membuktikan sumber definisi sense leksikal.

## 5. Batas

Audit ini tidak:
- mengubah data kamus, loader, lookup, analyzer, snapshot, atau laporan interpretasi;
- mengubah planner v1;
- menyusun teks pertanyaan otomatis;
- mengaktifkan aturan konteks atau pemilihan sense;
- menghubungkan klarifikasi ke runtime.

**Titik lanjut yang disarankan:** tetapkan kontrak planner v1.1 untuk referensi sense-level yang bersarang di dalam kandidat leksikal. Setelah itu, kontrak penyaji interaksi dapat menggunakan definisi kamus yang terverifikasi. Cakupan tes harus ditetapkan sebelum implementasi.
