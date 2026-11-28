# Rancangan Context Evidence Generator v1 — Lexara

**Status:** Draf desain untuk ditinjau; belum disetujui dan belum diimplementasikan.
**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.
**Tujuan:** Menyediakan bukti yang dapat diaudit untuk pekerjaan pemilihan sense kontekstual berikutnya, tanpa mengubah parser, POS, morfologi, kamus, Concept Layer v1, atau semantic-role resolver.

## 1. Posisi dalam pipeline

Rancangan alur:

1. Analyzer menghasilkan kandidat leksikal beserta sense.
2. concept_sense_adapter melampirkan konsep yang sudah reviewed pada setiap sense kandidat.
3. Parser menghasilkan struktur klausa dan status parsed, partial, atau unresolved.
4. Context Evidence Generator mengekstrak observasi dari masukan tersebut dan mencocokkannya hanya dengan aturan konteks yang eksplisit serta berstatus reviewed.
5. Generator mengeluarkan bukti per-sense untuk calon komponen pemilih sense. Pemilih sense dan integrasi runtime merupakan pekerjaan terpisah.

Generator tidak memilih sense. Ia hanya menghasilkan bukti dan alasan yang dapat ditelusuri.

## 2. Pemisahan observasi dan evidence

Dua jenis keluaran harus dibedakan.

### 2.1 Observasi konteks

Observasi adalah fakta yang terlihat langsung pada masukan, bukan kesimpulan makna. Contoh:

- token/kandidat lema yang hadir;
- sense dan concept ID yang melekat pada kandidat;
- peran sintaksis yang secara eksplisit dihasilkan parser;
- kepala predikat dan modifier predikat yang memang disediakan parser;
- penanda negasi/modalitas yang dikenali;
- relasi penghubung klausa yang secara eksplisit dicatat parser;
- status dan metode parser.

Observasi harus mempertahankan sumber token/rentang token jika tersedia. Generator tidak boleh mengubah observasi menjadi klaim semantis hanya berdasarkan posisi kata.

### 2.2 Evidence untuk sense

Evidence hanya boleh dibuat ketika suatu aturan konteks eksplisit cocok dengan observasi. Setiap evidence memiliki:

- sense_id: sense yang didukung atau ditentang;
- concept_ids: konsep reviewed yang terkait dengan sense tersebut; boleh kosong;
- polarity: supports atau contradicts;
- strength: weak atau strong;
- source: asal bukti yang cocok;
- rule_id: ID aturan yang menghasilkan evidence;
- rationale: alasan yang menjelaskan kecocokan aturan;
- token_spans: rentang token yang menjadi dasar kecocokan, jika tersedia.

Evidence harus merujuk pada sense kandidat yang benar-benar diberikan. Generator tidak boleh menciptakan sense, konsep, atau pemetaan baru.

## 3. Aturan konteks

- Hanya aturan berstatus reviewed yang boleh menghasilkan evidence aktif.
- Setiap aturan memiliki ID stabil, target sense yang eksplisit, kondisi yang dapat diperiksa, polarity, strength, sumber, dan rationale.
- Aturan harus menyatakan kondisi positif maupun batas penerapannya secara eksplisit; kemiripan kata atau kedekatan token saja tidak cukup.
- Aturan yang belum ditinjau tidak menghasilkan evidence aktif.
- Versi pertama menggunakan katalog kondisi terbatas dan eksplisit. Tidak ada evaluasi ekspresi bebas, kode dinamis, atau inferensi tak terbatas.
- Bila belum ada aturan yang cocok, hasilnya adalah tanpa evidence; bukan bukti bahwa sense tersebut salah.

Sumber aturan dapat berupa anotasi kurasi atau pola konteks yang ditinjau. Setiap aturan harus dapat ditelusuri ke contoh/sumber dan rationale. Kumpulan aturan tidak boleh mengubah data kamus atau Concept Layer.

## 4. Kekuatan evidence

- weak: aturan yang ditinjau menemukan petunjuk relevan, tetapi petunjuk tersebut tidak cukup untuk membedakan sense secara meyakinkan.
- strong: aturan yang ditinjau secara khusus membedakan sense pada kondisi yang dinyatakan dan memiliki bukti yang cukup untuk mendukung atau menolak sense tersebut.
- Tidak ada evidence yang boleh diberi strength strong hanya dari urutan kata, posisi subjek/objek, POS, atau struktur parser.
- Strength ditetapkan oleh aturan yang ditinjau, bukan dihitung dari jumlah petunjuk atau skor kemiripan.
- Beberapa evidence yang lemah tidak otomatis menjadi satu evidence kuat.

## 5. Status parser dan abstention

- Untuk parser parsed, observasi sintaksis yang tersedia boleh dipakai oleh aturan yang secara eksplisit mengizinkannya.
- Untuk parser partial, hanya observasi pada bagian yang berhasil dianalisis yang boleh dipakai. Aturan yang memerlukan bagian yang tidak tersedia tidak cocok.
- Untuk parser unresolved atau status yang tidak dikenal, generator tidak boleh mengarang struktur. Observasi leksikal langsung masih dapat dicatat, tetapi aturan yang membutuhkan struktur klausa tidak boleh cocok.
- Evidence yang saling bertentangan harus dipertahankan bersama. Generator tidak menyelesaikan konflik.
- Tidak ada evidence atau evidence yang tidak cukup menghasilkan kondisi kandidat tetap ambigu/tidak terselesaikan pada tahap pemilihan sense berikutnya.

## 6. Batas konflik dan penggabungan

- Evidence disimpan per sense dan per aturan; jangan menggabungkan evidence dari sense berbeda.
- Evidence dari argument/slot atau klausa berbeda tidak boleh digabung untuk menciptakan dukungan kuat, kecuali satu aturan secara eksplisit mendefinisikan hubungan tersebut.
- Evidence duplikat dari aturan dan rentang token yang sama tidak boleh digandakan.
- Dukungan dan kontradiksi terhadap sense yang sama harus tetap terlihat sebagai konflik.
- Generator tidak menetapkan pemenang, tidak menghapus kandidat, dan tidak mengubah status sense.

## 7. Batas integrasi

Dalam cakupan modul ini:

- Membaca keluaran kandidat sense, hasil adapter, hasil parser, dan aturan konteks yang diberikan.
- Menghasilkan observasi dan evidence yang dapat diaudit.
- Bersifat deterministik dan tidak menulis ke sumber input.
- Tidak mengubah analyzer, kamus, batch, indeks, Concept Layer, loader, adapter, POS, morfologi, parser, atau semantic-role resolver.
- Tidak memanggil atau menggantikan resolver semantic role. Format evidence sense berbeda dari format evidence semantic-role resolver.
- Tidak memilih sense dan tidak mengubah keluaran runtime yang ada.

## 8. Antarmuka konseptual

Nama modul yang diusulkan: tools/context_evidence_generator.py.

Fungsi yang diusulkan:

~~~python
generate_context_evidence(
    sense_candidates,
    parse_result,
    context_rules,
)
~~~

Hasil konseptual memuat:

- observations: fakta yang diekstrak dari input;
- evidence: daftar evidence per-sense yang dihasilkan aturan reviewed;
- status: evidence_found atau no_evidence;
- notes: batas atau alasan abstention yang relevan.

Nama fungsi dan bentuk final objek masih dapat disesuaikan saat kontrak ini ditinjau. Tidak ada janji bahwa pilot tiga konsep saat ini sudah menyediakan aturan yang cukup untuk menghasilkan evidence kontekstual.

## 9. Rencana pengujian setelah desain disetujui

Tes terfokus hanya untuk modul baru:

1. observasi sintaksis tidak otomatis menjadi evidence;
2. aturan reviewed menghasilkan evidence sesuai target sense;
3. aturan proposed/rejected tidak menghasilkan evidence aktif;
4. evidence weak tetap weak dan tidak dinaikkan karena jumlah petunjuk;
5. evidence strong hanya muncul dari aturan yang secara eksplisit menetapkannya;
6. dukungan dan kontradiksi dipertahankan sebagai konflik;
7. kandidat tanpa concept mapping tetap diproses berdasarkan sense ID;
8. parser partial hanya menggunakan observasi yang tersedia;
9. parser unresolved tidak menghasilkan evidence yang memerlukan struktur klausa;
10. masukan tidak berubah dan keluaran deterministik.

Jumlah dan cakupan final tes dikunci sebelum implementasi. Tes Concept Layer v1 yang sudah ada tidak diulang kecuali ada alasan kompatibilitas yang terbukti. GitHub Actions boleh digunakan untuk tes yang relevan.

## 10. Keputusan yang masih memerlukan persetujuan

Sebelum implementasi, tinjau dan setujui:

1. pemisahan observasi dan evidence;
2. kewajiban evidence berasal dari aturan konteks eksplisit berstatus reviewed;
3. aturan strength weak/strong dan larangan menaikkan strength otomatis;
4. perilaku konservatif untuk parser partial/unresolved dan konflik;
5. batas modul, antarmuka konseptual, dan daftar tes terfokus.

**Status akhir:** dokumen ini hanya draf desain. Belum ada modul, dataset aturan, tes, atau integrasi runtime yang dibuat berdasarkan rancangan ini.
