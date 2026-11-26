# Indeks Utama Kamus — Sistem Bahasa

**Status:** Batch 001 disetujui dan terdaftar
**Target:** 3.000 lemma unik untuk Kamus v1.0
**Sumber aturan:** ../../docs/KAMUS.md

File ini adalah daftar induk untuk melacak semua lemma yang masuk ke kamus. Setiap kosakata baru harus diperiksa terhadap indeks ini sebelum ditambahkan ke data kamus. Tujuannya mencegah duplikasi, menjaga ID tetap unik, dan memastikan variasi ejaan diarahkan ke entri kanonis yang benar.

## 1. Aturan wajib sebelum menambah kata

1. Normalisasikan kandidat untuk pencarian duplikat: Unicode NFC, hapus spasi di awal/akhir, dan gunakan huruf kecil untuk pencocokan dasar.
2. Jangan menghapus tanda hubung atau apostrof secara otomatis.
3. Periksa kandidat terhadap lemma, variants, derived_forms, dan alias yang sudah ada.
4. Satu lemma dapat memiliki beberapa sense dan POS; jangan membuat lemma terpisah hanya karena maknanya berbeda.
5. Bentuk turunan tidak otomatis dihitung sebagai lemma baru.
6. ID harus unik dan stabil.
7. Kandidat yang belum jelas harus ditandai untuk tinjauan, bukan langsung disahkan.

## 2. Status entri

| Status | Arti |
|---|---|
| approved | Sudah diperiksa dan masuk hitungan target |
| review | Masih perlu verifikasi |
| rejected | Tidak digunakan |
| merged | Digabung atau diarahkan ke lemma kanonis lain |

Hanya status approved yang dihitung ke target 3.000 lemma.

## 3. Indeks lemma kanonis

| ID | Lemma kanonis | POS | Register | Variasi/bentuk turunan | Status | Catatan |
|---|---|---|---|---|---|---|
| K0001 | aku | PRON | neutral, informal | — | approved | Batch 001 |
| K0041 | bagus | ADJ | neutral, informal | bagusan | approved | Batch 001 |
| K0048 | banget | ADV | informal, slang | — | approved | Batch 001 |
| K0016 | bangun | VERB | neutral | membangunkan, terbangun, bangunkan | approved | Batch 001 |
| K0033 | bantu | VERB | neutral | membantu, dibantu, bantuan, pembantu | approved | Batch 001 |
| K0043 | besar | ADJ | neutral | membesar, besaran, kebesaran | approved | Batch 001 |
| K0036 | bicara | VERB | neutral | berbicara, pembicaraan, membicarakan, pembicara | approved | Batch 001 |
| K0026 | bisa | VERB, NOUN | neutral, informal | kemampuan | approved | Batch 001 |
| K0047 | capek | ADJ | informal | cape | approved | Batch 001 |
| K0045 | cepat | ADJ | neutral | mempercepat, kecepatan, tercepat | approved | Batch 001 |
| K0018 | datang | VERB | neutral | kedatangan, mendatangi | approved | Batch 001 |
| K0035 | dengar | VERB | neutral | mendengar, terdengar, pendengaran, kedengaran | approved | Batch 001 |
| K0004 | dia | PRON | neutral | — | approved | Batch 001 |
| K0049 | dong | PART | informal, slang | — | approved | Batch 001 |
| K0023 | duit | NOUN | informal, slang | — | approved | Batch 001 |
| K0029 | enggak | ADV | informal, slang | nggak, gak, ga | approved | Batch 001 |
| K0008 | gue | PRON | slang, informal | gw, gua | approved | Batch 001 |
| K0025 | ingin | VERB | neutral | keinginan, menginginkan | approved | Batch 001 |
| K0030 | iya | INTJ | neutral, informal | ya | approved | Batch 001 |
| K0020 | jalan | NOUN | neutral | jalanan, perjalanan, berjalan | approved | Batch 001 |
| K0042 | jelek | ADJ | informal, neutral | kejelekan | approved | Batch 001 |
| K0006 | kami | PRON | neutral, formal | — | approved | Batch 001 |
| K0003 | kamu | PRON | neutral, informal | — | approved | Batch 001 |
| K0044 | kecil | ADJ | neutral | mengecil, kecil-kecilan | approved | Batch 001 |
| K0021 | kerja | NOUN | neutral | bekerja, pekerjaan, pekerja, mengerjakan | approved | Batch 001 |
| K0005 | kita | PRON | neutral | — | approved | Batch 001 |
| K0046 | lambat | ADJ | neutral | melambat, memperlambat, kelambatan | approved | Batch 001 |
| K0034 | lihat | VERB | neutral | melihat, terlihat, penglihatan, kelihatan | approved | Batch 001 |
| K0009 | lu | PRON | slang, informal | lo, elu | approved | Batch 001 |
| K0013 | makan | VERB | neutral | memakan, dimakan, makanan, pemakan | approved | Batch 001 |
| K0024 | mau | VERB | neutral, informal | kemauan, menghendaki | approved | Batch 001 |
| K0007 | mereka | PRON | neutral | — | approved | Batch 001 |
| K0014 | minum | VERB | neutral | meminum, diminum, minuman, peminum | approved | Batch 001 |
| K0038 | ngobrol | VERB | informal, slang | obrolan, mengobrol | approved | Batch 001 |
| K0031 | oke | INTJ | informal | ok, okay | approved | Batch 001 |
| K0037 | omong | NOUN | informal | mengomong, omongan | approved | Batch 001 |
| K0010 | orang | NOUN | neutral | perorangan | approved | Batch 001 |
| K0040 | paham | VERB | neutral | memahami, pemahaman, dipahami | approved | Batch 001 |
| K0017 | pergi | VERB | neutral | kepergian, bepergian | approved | Batch 001 |
| K0019 | pulang | VERB | neutral | kepulangan, memulangkan | approved | Batch 001 |
| K0012 | rumah | NOUN | neutral | perumahan, berumah | approved | Batch 001 |
| K0002 | saya | PRON | formal, neutral | — | approved | Batch 001 |
| K0050 | sih | PART | informal, slang | — | approved | Batch 001 |
| K0039 | tahu | VERB | neutral, informal | mengetahui, pengetahuan, ketahuan | approved | Batch 001 |
| K0011 | teman | NOUN | neutral | berteman, pertemanan | approved | Batch 001 |
| K0028 | tidak | ADV | neutral, formal | — | approved | Batch 001 |
| K0015 | tidur | VERB | neutral | tertidur, menidurkan, tiduran | approved | Batch 001 |
| K0032 | tolong | VERB | neutral | menolong, pertolongan, penolong | approved | Batch 001 |
| K0022 | uang | NOUN | neutral | keuangan, menguangkan | approved | Batch 001 |

## 4. Kandidat yang digabung atau diperlakukan sebagai variasi

| Bentuk kandidat | Perlakuan | Catatan |
|---|---|---|
| bisa (mampu), bisa (racun) | Satu lemma: K0026 | Dua sense dengan POS VERB dan NOUN |
| gw, gua | Variasi lemma gue | Tidak dihitung sebagai lemma terpisah |
| lo, elu | Variasi lemma lu | Tidak dihitung sebagai lemma terpisah |
| nggak, gak, ga | Variasi lemma enggak | Tidak dihitung sebagai lemma terpisah |
| ok, okay | Variasi lemma oke | Tidak dihitung sebagai lemma terpisah |
| ya | Variasi lemma iya | Tidak dihitung sebagai lemma terpisah |
| cape | Variasi lemma capek | Tidak dihitung sebagai lemma terpisah |
| memakan, dimakan, makanan, dan bentuk turunan lain | Bentuk turunan lemma masing-masing | Tidak dihitung sebagai lemma terpisah |

## 5. Hitungan progres

- Lemma disetujui: **49 / 3.000**
- Kandidat dalam tinjauan: **0**
- Ditolak: **0**
- Digabung/alias: **7 kelompok variasi/polisemi tercatat**

Catatan: 50 kandidat yang direview menghasilkan 49 lemma kanonis karena dua kandidat "bisa" digabung menjadi satu lemma dengan dua sense dan dua POS.

## 6. Alur kerja setiap batch

1. Ambil indeks dan data kamus terbaru dari repository.
2. Normalisasikan ejaan dan cari duplikasi terhadap lemma, variasi, dan bentuk turunan.
3. Periksa makna dan POS; pisahkan sense untuk polisemi/homograf.
4. Tetapkan ID setelah disetujui.
5. Tambahkan data batch dan perbarui indeks.
6. Jalankan validasi JSONL, ID unik, lemma kanonis unik, dan kode POS/register.
7. Catat perubahan dalam commit.

**Prinsip:** indeks dan data kamus di repository adalah sumber rujukan utama. Jangan mengandalkan ingatan percakapan untuk pemeriksaan duplikat.
