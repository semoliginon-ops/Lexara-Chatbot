# Kontrak Integrasi Contextual Sense v1

**Status:** Disetujui pengguna pada 28 November 2026. Dokumen ini menetapkan batas integrasi; implementasi runtime belum dimulai.

## 1. Tujuan

Menetapkan orkestrasi terkontrol antara kandidat sense leksikal per kemunculan token, parser, Concept Sense Adapter, Context Evidence Generator, dan Contextual Sense Selector.

Integrasi ini memakai komponen yang sudah ada sebagai komponen terpisah. Kontrak ini tidak mengubah kontrak/API internal komponen tersebut.

## 2. Prinsip wajib

1. Satu pemanggilan selector hanya menangani kandidat sense untuk **satu kemunculan satu token**.
2. Evidence tidak boleh dipindahkan, digabung, atau digunakan lintas kemunculan token.
3. Tidak ada pemilihan berdasarkan frekuensi, urutan kandidat, POS, kedekatan token, kemiripan label konsep, atau relasi Concept Layer.
4. Hanya evidence kuat (strong) yang dapat memengaruhi keputusan selector. Evidence lemah tetap disimpan untuk audit.
5. Jika bukti tidak cukup atau pemetaan token/klausa tidak aman, sistem mempertahankan kandidat dan menunda keputusan; tidak menebak sense.
6. Komponen Tahap 1 dan Tahap 2 tetap menjadi sumber masukan baca-saja. Integrasi v1 tidak mengubah kamus, batch, indeks, morfologi, POS, parser, atau resolver semantic-role.

## 3. Posisi pipeline

Urutan konseptual:

1. Teks masuk ke pipeline analisis yang sudah ada.
2. Analyzer menghasilkan token dan kandidat leksikal masing-masing.
3. Parser menghasilkan struktur kalimat/klausa sesuai kemampuan saat ini.
4. Orchestrator baru membentuk kelompok kandidat berdasarkan kemunculan token.
5. Concept Sense Adapter melampirkan pemetaan konsep reviewed untuk kandidat sense pada kelompok token tersebut.
6. Context Evidence Generator menghasilkan observasi/evidence dari parser dan aturan konteks reviewed.
7. Contextual Sense Selector memutuskan hanya untuk kelompok kandidat token tersebut.
8. Orchestrator mengembalikan hasil per token beserta audit evidence dan alasan penundaan jika ada.

Adapter, generator, selector, parser, dan analyzer tetap modul terpisah.

## 4. Identitas kemunculan token

Setiap token diberi identitas sementara dalam satu hasil analisis, minimal:

- token_index: indeks token pada urutan token keluaran analyzer;
- token: bentuk token sebagaimana dikeluarkan analyzer.

Identitas ini hanya berlaku untuk satu pemanggilan analisis. Bukan ID kamus, bukan ID sense, dan bukan identitas permanen lintas percakapan.

Kandidat sense yang berasal dari token berbeda wajib berada di kelompok berbeda, termasuk ketika bentuk token dan daftar kandidatnya sama.

## 5. Batas pemetaan parser ke token

Parser saat ini mengekspos teks token dalam role/klausa dan belum menyediakan rentang indeks token yang stabil untuk seluruh struktur. Karena itu integrasi v1 menerapkan kebijakan konservatif:

- **Satu klausa, pemetaan tidak ambigu:** evidence boleh diproses jika observasi parser dapat dikaitkan dengan kemunculan token secara aman.
- **Kalimat majemuk / keluaran memiliki clauses:** pemilihan kontekstual ditunda pada v1. Jangan menerapkan evidence satu klausa ke kandidat token di klausa lain.
- **Token berulang dengan bentuk sama dan tidak tersedia identitas posisi pada observasi parser:** pemilihan ditunda. Jangan menganggap teks token yang sama menunjuk ke kemunculan yang sama.
- **Status parser partial:** hanya observasi yang benar-benar tersedia boleh digunakan; ketiadaan observasi tidak dianggap bukti negatif.
- **Status parser unresolved atau status yang tidak didukung:** jangan membuat kecocokan berbasis role. Token-level evidence hanya boleh digunakan jika sumber dan target token dapat dipastikan tanpa ambiguitas.
- Jika pemetaan tidak aman, hasil mencatat alasan penundaan dan mempertahankan seluruh kandidat sense.

Kebijakan ini sengaja membatasi cakupan v1. Perluasan pemetaan indeks token/klausa merupakan desain lanjutan tersendiri dan tidak boleh dilakukan dengan mengubah parser secara diam-diam.

## 6. Sumber aturan konteks

Lokasi dataset v1:

data/context_rules/context_rules.jsonl

Format setiap baris mengikuti kontrak docs/RANCANGAN_CONTEXT_EVIDENCE_GENERATOR.md:

- rule_id
- status
- target_sense_id
- conditions
- polarity
- strength
- source
- rationale

Aturan hanya aktif bila status bernilai reviewed. Aturan proposed dan rejected tidak menghasilkan evidence. Dataset dimuat secara baca-saja; integrasi tidak mengubah status aturan otomatis.

Kondisi dan batas kekuatan evidence tetap tunduk pada kontrak Context Evidence Generator. Evidence kuat tidak boleh disimpulkan hanya dari struktur sintaksis, urutan kata, kedekatan token, atau kemiripan makna.

## 7. Bentuk hasil orkestrasi

Hasil integrasi menyediakan satu record per kemunculan token, sekurang-kurangnya memuat:

- identitas token sementara (token_index, token);
- kandidat sense asli;
- pemetaan konsep yang tersedia;
- observasi/evidence yang dihasilkan;
- hasil selector, jika selector aman dijalankan;
- status orkestrasi dan alasan jika ada penundaan.

Bentuk konseptual:

    {
        "token_index": 3,
        "token": "mobil",
        "candidate_senses": [],
        "concept_mappings": [],
        "evidence": [],
        "selection": null,
        "orchestration_status": "deferred",
        "defer_reason": "ambiguous_token_occurrence_mapping"
    }

Nilai di atas hanya ilustrasi skema, bukan keluaran runtime yang sudah tersedia. Status orkestrasi tidak menggantikan status selector (selected, ambiguous, unresolved, atau not_needed).

## 8. Batas tanggung jawab

| Komponen | Tanggung jawab dalam integrasi |
|---|---|
| Analyzer dan POS | Menyediakan token/kandidat; tidak diubah |
| Parser | Menyediakan struktur yang tersedia; tidak diubah |
| Concept Layer loader | Menyediakan konsep/pemetaan reviewed secara baca-saja |
| Concept Sense Adapter | Melampirkan konsep reviewed per kandidat sense |
| Context Evidence Generator | Menghasilkan observasi dan evidence sesuai kontraknya |
| Contextual Sense Selector | Memilih sense sesuai kontraknya |
| Orchestrator baru | Mengelompokkan per kemunculan token, mengatur urutan pemanggilan, menjaga batas klausa, dan mengemas hasil |
| Context rules loader baru | Memuat dataset aturan secara baca-saja dan menyerahkan record kepada generator |

Orchestrator tidak boleh menyalin atau mengimplementasikan ulang logika internal generator/selector.

## 9. Batas implementasi dan pengujian yang disetujui

Implementasi berikutnya dibatasi pada:

1. satu modul orchestrator baru;
2. satu loader aturan konteks baca-saja jika belum ada loader yang sesuai;
3. dataset awal aturan konteks hanya setelah isi aturan dan target sense ditinjau secara linguistik;
4. tepat 10 tes integrasi terfokus untuk kontrak orkestrasi, termasuk isolasi token berulang, pemisahan kandidat per token, pemetaan konsep reviewed, penggunaan evidence, penundaan pada klausa majemuk/pemetaan ambigu, parser partial/unresolved, serta pelestarian audit;
5. satu workflow GitHub Actions terfokus bila diperlukan oleh pola proyek.

Tes unit lama untuk generator, selector, adapter, dan parser tidak diulang tanpa perubahan atau alasan teknis yang spesifik. Regression suite 450 tes tidak otomatis dijalankan ulang hanya karena modul orkestrasi baru ditambahkan.

Tidak ada implementasi atau perubahan kode yang diotorisasi oleh persetujuan dokumen ini selain persiapan desain. Implementasi dimulai sebagai langkah berikutnya dengan batas di atas.

## 10. Di luar cakupan

- Pemilihan sense untuk kalimat majemuk pada v1.
- Pemetaan token berbasis posisi yang belum tersedia pada keluaran parser.
- Perubahan analyzer, tokenizer, POS, morfologi, parser, kamus, batch, indeks, Concept Layer v1, generator, selector, atau resolver semantic-role.
- Inferensi evidence otomatis dari kemiripan kata, frekuensi, urutan kandidat, atau relasi konsep.
- Integrasi konteks multi-giliran percakapan.
- Penetapan aturan konteks reviewed secara otomatis.
- Perubahan status kandidat/evidence atau penambahan confidence score.

## 11. Kriteria penerimaan desain

Desain dianggap terpenuhi apabila implementasi dapat membuktikan bahwa:

- setiap kelompok kandidat hanya berasal dari satu kemunculan token;
- evidence tidak bocor ke token lain;
- generator dan selector dipanggil tanpa mengubah kontrak masing-masing;
- aturan non-reviewed tidak aktif;
- struktur majemuk dan pemetaan ambigu ditunda secara eksplisit;
- partial/unresolved diperlakukan sesuai bukti yang tersedia;
- kandidat dan audit tetap dipertahankan saat keputusan ditunda;
- seluruh 10 tes integrasi khusus lulus.
