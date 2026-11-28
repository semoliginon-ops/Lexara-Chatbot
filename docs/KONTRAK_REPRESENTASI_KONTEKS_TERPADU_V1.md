# Kontrak Representasi Konteks Terpadu v1

**Status:** rancangan kerja Tahap 3.  
**Tujuan:** menyatukan keluaran analisis leksikal, morfologi, POS, dan parser dalam satu representasi baca-saja untuk dipakai oleh komponen pemahaman konteks berikutnya.

## 1. Posisi dan batas

Komponen ini menerima:
1. keluaran `analyze_text()` setelah `tag_pos()` dan `disambiguate_pos_context()`;
2. keluaran `parse_sentence()` dari analisis yang sama.

Komponen hanya mengemas dan menghubungkan hasil yang sudah tersedia. Komponen **tidak**:
- menjalankan ulang analyzer, morfologi, POS, atau parser;
- memilih sense atau POS;
- membuat evidence semantik baru;
- menyimpulkan semantic role dari POS atau urutan kata;
- mengubah kamus, Concept Layer, aturan konteks, atau komponen Tahap 1/2;
- mengubah atau menghapus status `partial` dan `unresolved`.

## 2. Identitas token

Setiap token keluaran analyzer dipertahankan dalam urutan aslinya dan diberi `token_index` yang hanya berlaku pada satu hasil analisis.

Bentuk token dan indeks tersebut menjadi identitas kemunculan token pada snapshot. Bentuk permukaan yang sama tidak boleh dianggap sebagai token yang sama.

## 3. Informasi per token

Untuk setiap token, snapshot mempertahankan:
- `token_index`, `token`, dan `kind`;
- status serta kandidat leksikal asli;
- kandidat morfologi dan bukti voice yang tersedia;
- kandidat POS, POS terpilih bila memang sudah tersedia, status POS, serta evidence POS kontekstual;
- relasi sintaksis yang dapat dipetakan secara aman dari hasil parser;
- status pemetaan dan alasan penundaan bila relasi sintaksis tidak dapat dipastikan.

Data sumber dipertahankan apa adanya; snapshot tidak mereduksi daftar kandidat menjadi satu pilihan.

## 4. Pemetaan struktur parser

Parser v1 mengekspos sebagian peran sebagai teks token, belum sebagai indeks token stabil. Karena itu pemetaan dilakukan dengan aturan konservatif:
- hanya pencocokan bentuk token yang sama persis setelah normalisasi `casefold`;
- token kata pada sumber harus muncul tepat satu kali;
- token harus muncul tepat satu kali pada observasi parser;
- token yang sama sekali tidak memiliki observasi parser tidak dianggap memiliki peran negatif;
- token dalam `unresolved_tokens` dicatat sebagai unresolved, bukan diberi peran;
- jika satu token cocok dengan lebih dari satu peran, pemetaan ditunda;
- jika bentuk token berulang, pemetaan token tersebut ditunda;
- jika parser menghasilkan `clauses`, pemetaan peran sintaksis v1 ditunda untuk seluruh kalimat; analisis klausa tetap dipertahankan sebagai data parser;
- parser dengan status yang tidak didukung tidak menghasilkan pemetaan peran.

Kategori peran yang boleh dilaporkan hanya `subject`, `predicate`, `object`, `adjunct`, dan `complement`, sesuai field parser yang tersedia. Tidak ada kategori atau peran baru yang diinferensikan.

## 5. Status keluaran

Status snapshot menjelaskan kelengkapan pengemasan, bukan keberhasilan memahami makna:
- `assembled`: semua token dapat direpresentasikan dan pemetaan parser yang tersedia tidak memerlukan penundaan;
- `partial`: parser memang `partial`, ada token unresolved, atau sebagian pemetaan tidak tersedia;
- `deferred`: struktur parser tidak aman untuk dipetakan, misalnya kalimat majemuk atau token berulang.

Status parser asli selalu dipertahankan terpisah. Status snapshot tidak menggantikan status parser, POS, selector, atau orchestrator.

## 6. Keluaran tingkat kalimat

Snapshot menyimpan metadata parser yang tersedia, termasuk `parser_method`, `status`, `pattern`, `roles`, `clauses` bila ada, `unresolved_tokens`, dan `notes`. Data ini disalin secara baca-saja; tidak ditafsirkan ulang menjadi relasi semantik.

## 7. Pengujian v1

Implementasi dibatasi pada satu modul baru dan tepat 10 tes khusus:
1. menggabungkan field leksikal, morfologi, voice, dan POS tanpa kehilangan kandidat;
2. mempertahankan urutan token dan identitas indeks;
3. memetakan subject/predicate/object/complement pada bentuk unik;
4. memetakan adjunct dari bentuk parser yang tersedia;
5. mempertahankan punctuation sebagai not_applicable;
6. menandai token parser-unresolved tanpa menebak peran;
7. menunda pemetaan bentuk token berulang;
8. menunda pemetaan peran pada hasil parser dengan `clauses`;
9. mempertahankan status partial dan token yang tidak teramati tanpa membuat bukti negatif;
10. memastikan input tidak berubah dan hasil deterministik.

Gunakan satu workflow GitHub Actions terfokus sesuai pola proyek. Jangan menjalankan ulang regression suite 450 tes atau tes lama komponen lain tanpa alasan teknis.

## 8. Kriteria penerimaan dan pekerjaan di luar cakupan

Implementasi diterima jika seluruh 10 tes khusus lulus dan seluruh batas di atas dipatuhi.

Pemilihan sense kontekstual, aturan `bangun`/ `jam`, integrasi entrypoint/runtime, pemahaman kalimat majemuk, konteks multi-giliran, inferensi maksud ujaran, serta perubahan parser/analyzer/POS/morfologi berada di luar cakupan v1 dan tetap menjadi pekerjaan terpisah.
