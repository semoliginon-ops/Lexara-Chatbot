# Rancangan Context Evidence Generator v1 — Lexara

**Status:** Disetujui untuk implementasi terbatas.
**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.
**Tujuan:** Menyediakan evidence sense yang dapat diaudit untuk komponen pemilih sense berikutnya, tanpa mengubah parser, POS, morfologi, kamus, Concept Layer v1, atau semantic-role resolver.

## 1. Posisi dalam pipeline

1. Analyzer menghasilkan kandidat leksikal beserta sense.
2. concept_sense_adapter melampirkan konsep reviewed pada setiap sense kandidat.
3. Parser menghasilkan struktur klausa dengan status parsed, partial, atau unresolved.
4. Context Evidence Generator mengekstrak observasi dan mencocokkannya dengan aturan konteks eksplisit berstatus reviewed.
5. Komponen pemilih sense berikutnya menggunakan evidence untuk memutuskan apakah sense dapat dipilih atau harus tetap ambigu/tidak terselesaikan.

Generator **tidak memilih sense** dan **tidak menetapkan status akhir ambiguous/unresolved**. Generator hanya menghasilkan observasi, evidence, dan catatan batas pemrosesan. Status akhir merupakan tanggung jawab pemilih sense.

## 2. Pemisahan observasi dan evidence

### 2.1 Observasi

Observasi adalah fakta yang terlihat langsung pada masukan, bukan kesimpulan makna. Versi pertama mengambil:
- sense_id dan concept_id dari kandidat sense yang diberikan;
- status parser;
- token yang tercatat pada roles subject, predicate, object, adjuncts, dan complement;
- unresolved_tokens dari parser.

Observasi sintaksis hanya dicatat jika benar-benar disediakan parser. Generator tidak mengarang rentang token atau struktur yang tidak tersedia.

### 2.2 Evidence

Evidence hanya dibuat ketika aturan konteks eksplisit berstatus reviewed cocok. Setiap evidence memuat:
- sense_id;
- concept_ids (boleh kosong);
- polarity: supports atau contradicts;
- strength: weak atau strong;
- source;
- rule_id;
- rationale;
- matched_conditions sebagai jejak kondisi yang cocok;
- token_spans, berupa daftar kosong jika offset tidak tersedia dari sumber.

Evidence hanya boleh merujuk pada sense kandidat yang diberikan. Generator tidak menciptakan sense, konsep, atau pemetaan baru.

## 3. Kontrak aturan konteks v1

Setiap aturan memiliki field:
- rule_id: ID stabil, format CE diikuti minimal enam digit;
- status: proposed, reviewed, atau rejected;
- target_sense_id: sense yang menjadi sasaran aturan;
- conditions: daftar kondisi eksplisit yang semuanya wajib cocok (AND);
- polarity: supports atau contradicts;
- strength: weak atau strong;
- source: teks nonkosong yang menunjukkan sumber kurasi;
- rationale: teks nonkosong yang menjelaskan alasan linguistik.

Katalog kondisi v1 dibatasi pada:
- token_present: token tertentu harus hadir pada token yang teramati;
- role_contains: token tertentu harus hadir pada salah satu role parser yang didukung (subject, predicate, object, adjuncts, complement).

Kondisi role_contains hanya dapat cocok jika parser berstatus parsed atau partial dan role yang diminta benar-benar tersedia. Status unresolved atau status tak dikenal tidak boleh menghasilkan kecocokan struktural.

Aturan proposed/rejected tidak menghasilkan evidence. Aturan reviewed dengan target sense yang tidak terdapat pada kandidat diabaikan. Semua kondisi dalam satu aturan harus cocok. Tidak ada evaluasi kode/ekspresi bebas, kemiripan semantik otomatis, atau inferensi dari kedekatan kata.

## 4. Kekuatan evidence

- weak: aturan reviewed menemukan petunjuk relevan yang belum cukup membedakan sense secara meyakinkan.
- strong: aturan reviewed secara khusus membedakan sense pada kondisi yang dinyatakan.
- Strength ditetapkan oleh aturan yang dikurasi, bukan dihitung dari jumlah petunjuk.
- Beberapa evidence weak tidak dinaikkan menjadi strong.
- Aturan strong wajib memiliki setidaknya satu kondisi token_present. Aturan yang hanya bergantung pada role sintaksis tidak boleh menghasilkan strong.
- Posisi kata, urutan kata, POS, atau struktur parser saja tidak pernah otomatis menghasilkan strong.

## 5. Status parser dan konflik

- parsed: kondisi token dan role yang tersedia boleh diperiksa.
- partial: hanya kondisi yang dapat diverifikasi dari observasi yang tersedia boleh cocok; bagian unresolved tidak boleh diperlakukan sebagai struktur terkonfirmasi.
- unresolved atau status tidak dikenal: kondisi token masih dapat diperiksa dari token yang tersedia, tetapi role_contains tidak boleh cocok.
- Evidence supports dan contradicts untuk sense yang sama tetap dikeluarkan bersama.
- Generator tidak menggabungkan evidence lintas sense, tidak menentukan pemenang, tidak menghapus kandidat, dan tidak menetapkan status akhir ambiguous/unresolved.

## 6. Batas integrasi

Modul baru yang diusulkan: tools/context_evidence_generator.py.

Antarmuka:
~~~python
generate_context_evidence(sense_candidates, parse_result, context_rules)
~~~

Input sense_candidates mengikuti keluaran map_sense_candidates_to_concepts, yaitu daftar record per sense dengan sense_id dan concepts. parse_result adalah hasil parser yang sudah ada. context_rules adalah daftar aturan dengan kontrak pada bagian 3.

Hasil:
- observations: fakta hasil ekstraksi;
- evidence: evidence per sense dari aturan reviewed yang cocok;
- status: evidence_found atau no_evidence (status pemrosesan evidence, bukan status ambiguitas sense);
- notes: catatan batas parser atau alasan abstention.

Modul harus deterministik, read-only, dan tidak memutasi input. Tidak mengubah analyzer, kamus, batch, indeks, Concept Layer, loader, adapter, POS, morfologi, parser, atau semantic-role resolver. Format evidence ini berbeda dari evidence semantic-role resolver.

## 7. Tes terfokus yang disepakati

Tepat 10 tes unit khusus modul baru:
1. observasi sintaksis tanpa aturan tidak otomatis menjadi evidence;
2. aturan reviewed menghasilkan evidence pada sense sasaran;
3. aturan proposed/rejected tidak menghasilkan evidence;
4. beberapa evidence weak tetap weak dan tidak diagregasi;
5. aturan strong harus eksplisit dan tidak boleh hanya mengandalkan role sintaksis;
6. evidence supports dan contradicts dipertahankan sebagai konflik;
7. kandidat tanpa concept mapping tetap dapat menghasilkan evidence;
8. parser partial hanya memakai observasi yang tersedia;
9. parser unresolved tidak menghasilkan evidence dari kondisi role;
10. input tidak berubah dan hasil deterministik.

Tes Concept Layer v1 yang telah lulus tidak diulang. Tambahkan workflow GitHub Actions khusus untuk menjalankan 10 tes ini saja; jangan memicu regression suite penuh karena perubahan modul ini tidak mengubah komponen lama.

## 8. Batas hasil tahap ini

Penyelesaian modul dan tes tidak berarti pemilihan sense kontekstual atau integrasi runtime telah selesai. Itu merupakan langkah lanjutan tersendiri setelah generator tersedia dan aturan konteks mulai dikurasi. Dataset pilot Concept Layer tiga konsep tidak dianggap cukup untuk mendukung pemahaman konteks secara luas.

**Keputusan pengguna:** rancangan disetujui pada 28 November 2026. Implementasi dibatasi sesuai kontrak ini.
