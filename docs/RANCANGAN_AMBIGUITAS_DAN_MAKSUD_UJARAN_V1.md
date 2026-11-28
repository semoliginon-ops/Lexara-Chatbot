# Rancangan Penanganan Ambiguitas dan Maksud Ujaran v1

**Status:** modul read-only v1 telah diimplementasikan dan diverifikasi; belum terhubung ke runtime.
**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.
**Masukan utama:** Context Snapshot v1 (tools/context_snapshot.py).

## 1. Tujuan

Merancang dua keluaran yang saling berhubungan tetapi tidak dicampur:

1. **Ambiguitas interpretasi:** bagian ujaran yang memiliki lebih dari satu analisis yang masih didukung, atau belum dapat diputuskan.
2. **Maksud komunikatif ujaran:** jenis tindakan komunikasi yang tampak dari bentuk ujaran, misalnya bertanya, menyatakan, meminta, memerintah, atau mengekspresikan sesuatu.

Sistem harus dapat menyatakan bahwa maksud atau makna belum cukup jelas. Tidak boleh mengarang maksud tersembunyi, emosi, tujuan pribadi, atau informasi yang tidak diberikan oleh ujaran/konteks.

## 2. Prinsip pemisahan

- Ambiguitas leksikal/sense, POS, struktur sintaksis, referensi, dan maksud komunikatif adalah dimensi berbeda.
- Satu ujaran dapat memiliki lebih dari satu jenis ketidakpastian sekaligus.
- Ketidakpastian pada satu dimensi tidak otomatis membatalkan hasil dimensi lain yang sudah didukung.
- Hasil parser partial, unresolved, atau snapshot deferred harus tetap terlihat; jangan mengubahnya menjadi kepastian.
- Ketiadaan bukti bukan bukti negatif.
- Jangan memilih sense hanya dari frekuensi, urutan kata, kedekatan token, atau kemiripan konsep.
- Jangan mengaktifkan aturan bangun/jam yang masih nonaktif.

## 3. Lapisan keluaran yang direncanakan

### A. Status interpretasi

Status umum untuk satu aspek interpretasi:
- resolved: tepat satu analisis didukung bukti yang memenuhi kontraknya.
- ambiguous: dua atau lebih analisis masih didukung dan belum dapat dibedakan.
- unresolved: informasi/observasi yang diperlukan tidak tersedia atau tidak cukup.
- deferred: kasus berada di luar cakupan versi atau pemetaan input tidak aman.

Status ini tidak menggantikan status asli analyzer, POS, parser, snapshot, generator, atau selector. Status rinci sumber tetap disimpan.

### B. Maksud komunikatif yang tampak

Versi awal hanya boleh mengklasifikasikan bentuk komunikatif yang memiliki petunjuk eksplisit:
- question: bentuk pertanyaan yang dikenali secara eksplisit.
- request: permintaan yang memiliki penanda atau konstruksi permintaan yang dikenali.
- directive: perintah/larangan yang memiliki konstruksi eksplisit.
- assertion: pernyataan/informasi yang disampaikan sebagai klaim.
- expressive: ungkapan ekspresif yang memiliki penanda eksplisit.
- fragment: ujaran fragmen yang belum membentuk konstruksi lengkap tetapi masih dapat dicatat.
- unknown: bukti belum cukup atau konstruksi tidak tercakup.

Label ini menggambarkan bentuk komunikatif yang teramati, bukan niat psikologis atau tujuan tersembunyi pembicara. Satu ujaran dapat memiliki kandidat lebih dari satu; jika bukti tidak membedakan, hasil harus ambiguous atau unknown, bukan dipaksa menjadi satu label.

### C. Catatan ambiguitas

Setiap catatan ambiguitas kelak harus menunjuk ke sumber yang dapat dilacak, misalnya indeks token snapshot, kandidat sense, status POS, atau bagian parser. Catatan minimal memuat:
- dimensi ketidakpastian;
- referensi token/struktur yang tepat bila tersedia;
- daftar kandidat yang benar-benar berasal dari komponen sumber;
- evidence pendukung/penyangkal beserta asalnya;
- status dan alasan abstention.

Jangan membuat kandidat baru hanya untuk melengkapi daftar.

## 4. Urutan pemrosesan yang direncanakan

1. Terima snapshot dan validasi struktur masukan.
2. Catat status serta ketidakpastian yang sudah dilaporkan komponen sumber.
3. Bentuk kandidat interpretasi hanya dari kandidat/evidence yang tersedia dan sesuai kontrak masing-masing.
4. Klasifikasikan maksud komunikatif yang tampak hanya jika konstruksi/penanda eksplisit tersedia.
5. Pertahankan beberapa kandidat bila bukti belum membedakan.
6. Hasilkan resolved, ambiguous, unresolved, atau deferred untuk setiap dimensi secara terpisah.
7. Minta klarifikasi hanya pada tahap kebijakan dialog berikutnya; rancangan ini tidak menghasilkan teks pertanyaan klarifikasi.

## 5. Aturan klarifikasi — batas awal

Klarifikasi kelak layak diminta jika:
- terdapat beberapa interpretasi yang sama-sama didukung; dan
- perbedaan interpretasi tersebut mengubah jawaban/tindakan berikutnya secara material; dan
- pertanyaan singkat dapat membedakannya.

Jangan meminta klarifikasi jika:
- satu interpretasi sudah didukung secara memadai;
- ketidakpastian tidak berpengaruh pada respons;
- sistem belum memiliki kandidat yang dapat dijelaskan; atau
- masalah sebenarnya adalah komponen sumber tidak menyediakan data yang diperlukan.

Jika belum ada kandidat yang dapat dijelaskan, sistem cukup menyatakan belum memahami bagian tersebut, bukan menyusun pilihan jawaban palsu.

## 6. Contoh ilustratif, bukan aturan aktif

- “Kamu bisa datang?” — bentuk pertanyaan tampak eksplisit; apakah ini pertanyaan kemampuan atau permintaan halus tidak boleh diputuskan hanya dari tanda tanya. Maksud pragmatis dapat tetap ambigu.
- “Tolong buka pintu.” — penanda permintaan eksplisit mendukung request; jangan menebak alasan pembicara meminta.
- “Pintu terbuka.” — bentuk ujaran dapat berupa pernyataan, tetapi makna keadaan/peristiwa bergantung pada sense dan konteks. Klasifikasi komunikatif tidak menyelesaikan ambiguitas sense.
- “Jam berapa?” — pertanyaan eksplisit; referen atau makna jam tidak otomatis dipilih oleh bentuk pertanyaan.

Contoh ini hanya menjelaskan pemisahan dimensi; bukan data latih, evidence aturan konteks, atau perubahan kamus/parser.

## 7. Batas implementasi versi pertama

- Tidak mengubah analyzer, kamus, indeks, morfologi, POS, parser, resolver semantic role, Concept Layer, Context Evidence Generator, Contextual Sense Selector, atau Context Snapshot.
- Tidak mengintegrasikan modul ke entrypoint/runtime.
- Tidak mengaktifkan aturan konteks yang belum reviewed/strong.
- Tidak menangani konteks multi-giliran, resolusi nama khusus, inferensi emosi/tujuan tersembunyi, atau generasi respons.
- Tidak membuat dataset besar atau pencarian korpus baru pada tahap rancangan.
- Implementasi harus menjadi modul terpisah yang menerima snapshot, dengan tes terfokus yang jumlah dan cakupannya ditetapkan sebelum coding.

## 8. Tahapan kerja setelah rancangan

1. Tinjau kelayakan masukan snapshot dan tentukan skema keluaran minimal yang tidak menduplikasi status sumber.
2. Implementasikan satu modul read-only kecil untuk memisahkan catatan ambiguitas dari klasifikasi bentuk komunikatif.
3. Buat contoh positif, negatif, dan abstention yang terbatas serta tes khusus untuk kontrak tersebut.
4. Setelah keluaran stabil, rancang kebijakan klarifikasi sebagai pekerjaan terpisah.
5. Integrasi runtime dan konteks multi-giliran tetap menjadi pekerjaan berikutnya, bukan bagian dari v1.

**Kriteria penerimaan rancangan:** batas antara makna, struktur, dan maksud komunikatif jelas; setiap kandidat dapat ditelusuri ke sumber; ketidakpastian dipertahankan; dan tidak ada perubahan pada komponen Tahap 1/2 atau aturan konteks nonaktif.

## 9. Skema keluaran minimal v1 (hasil verifikasi pemetaan)

Keluaran adalah laporan baca-saja atas satu Context Snapshot. Pemetaan berikut telah diperiksa terhadap `tools/context_snapshot.py`; field yang tidak tersedia tidak boleh direka.

```json
{
  "schema_version": "1.0",
  "source": {
    "snapshot_status": "assembled",
    "parser_status": "parsed"
  },
  "ambiguity": {
    "status": "ambiguous",
    "items": [
      {
        "dimension": "lexical_sense",
        "token_index": 0,
        "candidate_refs": [
          {
            "source_field": "lexical_candidates",
            "candidate_index": 0
          }
        ],
        "evidence_refs": [
          {
            "source_field": "lexical_status",
            "token_index": 0
          }
        ],
        "status": "ambiguous",
        "reason": "multiple_candidates_preserved"
      }
    ]
  },
  "communicative_intent": {
    "status": "resolved",
    "label": "question",
    "candidates": ["question"],
    "evidence_refs": [
      {
        "source_field": "normalized_text"
      }
    ],
    "reason": "explicit_question_mark"
  }
}
```

### 9.1 Pemetaan field yang benar-benar tersedia

| Kebutuhan | Field snapshot yang tersedia | Batas |
|---|---|---|
| Status snapshot | `status` | Nilai asli: `assembled`, `partial`, atau `deferred`. |
| Status parser | `parser_status` | Nilai asli parser, dapat `null`. |
| Kandidat sense/leksikal | `tokens[].lexical_candidates[]` | Objek kandidat memiliki bentuk sumbernya sendiri; tidak ada ID kandidat universal. Rujuk dengan `source_field` dan `candidate_index`. |
| Status leksikal | `tokens[].lexical_status` | Status asli dari analyzer. |
| Kandidat POS | `tokens[].pos_candidates[]` | Rujuk dengan indeks kandidat; jangan mengarang ID. |
| Status/konteks POS | `pos`, `pos_status`, `context_pos`, `pos_context_status`, `pos_context_evidence` | Pertahankan kandidat dan evidence yang ada; jangan membuat keputusan POS baru. |
| Status sintaksis per token | `syntactic_role`, `syntax_status`, `syntax_reason` | `mapped`, `unresolved`, `not_observed`, `deferred`, atau `not_applicable` sesuai sumber. |
| Struktur parser lengkap | `parser_result` | Salinan hasil parser; tidak boleh dianggap sebagai struktur referensi/anaphora. |
| Teks ujaran | `normalized_text` dan `tokens[].token` | Dapat dipakai untuk pemeriksaan bentuk komunikatif eksplisit yang dibatasi. |

Snapshot **tidak** menyediakan kandidat resolusi referensi/pronomina yang terstruktur. Karena itu, `reference` dikeluarkan dari dimensi yang dapat menghasilkan catatan v1; bukan diberi status seolah-olah sudah dianalisis. `intent` juga tidak menjadi `ambiguity.items[].dimension`, sebab hasil maksud komunikatif sudah memiliki bagian tersendiri.

### 9.2 Aturan referensi dan status

- `candidate_refs` memakai `source_field`, `token_index`, dan `candidate_index` bila relevan. Referensi harus menunjuk item yang benar-benar ada. Tidak ada `candidate_id` sintetis.
- `evidence_refs` hanya menunjuk field snapshot yang benar-benar ada. Referensi tingkat ujaran boleh tidak memiliki `token_index`.
- Dimensi v1 yang boleh menghasilkan catatan: `lexical_sense`, `pos`, dan `syntax`. Catatan hanya dibuat saat snapshot memiliki kandidat/status eksplisit yang menunjukkan ketidakpastian. `not_observed` tidak otomatis menjadi ambiguitas.
- `ambiguity.status` merangkum item; urutan konservatif dari paling tidak pasti: `deferred`, `unresolved`, `ambiguous`, `resolved`. Jika tidak ada item, gunakan `resolved` hanya bila snapshot tidak melaporkan ketidakpastian pada dimensi yang diperiksa; selain itu gunakan status yang sesuai.
- Status sumber tidak ditimpa. Status laporan v1 tidak menggantikan status analyzer, POS, parser, maupun snapshot.
- Jika pemetaan token atau sumber tidak aman, hasil ditunda atau unresolved; jangan menebak.

### 9.3 Batas klasifikasi maksud komunikatif v1

Klasifikasi awal hanya mengenali bentuk yang memiliki penanda eksplisit dan dapat diuji tanpa inferensi pragmatis:
- `question`: tanda tanya eksplisit pada `normalized_text`.
- `request`: penanda permintaan eksplisit `tolong` pada token ujaran.
- `directive`: penanda larangan eksplisit `jangan` pada token ujaran.
- Selain pola tersebut, hasil `unknown` / `unresolved`.

Label `assertion`, `expressive`, dan `fragment` tetap bagian dari kosakata skema, tetapi v1 tidak mengklasifikasikannya otomatis. Tanda tanya hanya membuktikan bentuk pertanyaan, bukan apakah pertanyaan itu secara pragmatis merupakan permintaan. Jika lebih dari satu pola eksplisit bertabrakan, jangan memaksakan satu label.

### 9.4 Batas implementasi dan tes yang disepakati

Implementasi akan menjadi modul read-only terpisah yang menerima satu snapshot dan tidak memanggil ulang analyzer/parser. Cakupan tepat **11 tes unit khusus** dalam satu berkas `tests/test_utterance_interpretation.py`:

1. menolak input snapshot yang bentuk dasarnya tidak valid;
2. mempertahankan status snapshot dan parser asli;
3. mencatat kandidat sense jamak dengan indeks kandidat yang benar;
4. mencatat kandidat POS jamak dengan indeks kandidat yang benar;
5. mempertahankan status sintaksis `unresolved` tanpa menetapkan peran;
6. mempertahankan kondisi sintaksis `deferred` tanpa menebak;
7. tidak membuat catatan ambiguitas dari `not_observed` saja;
8. mengenali bentuk pertanyaan dengan tanda tanya eksplisit;
9. mengenali penanda permintaan `tolong`;
10. mengenali penanda larangan `jangan`;
11. mengembalikan `unknown` / `unresolved` untuk bentuk tanpa penanda yang didukung.

Tes ini tidak menguji ulang Context Snapshot; ia memakai fixture snapshot kecil dan menguji kontrak modul baru. Tidak ada perubahan pada kamus, analyzer, morfologi, POS, parser, resolver, Concept Layer, generator, selector, integrasi sense, maupun runtime. Satu workflow GitHub Actions khusus hanya akan ditambahkan untuk 11 tes ini setelah implementasi. Regression suite 450 tes dan 10 tes Context Snapshot tidak dijalankan ulang tanpa alasan teknis.

**Kriteria penerimaan:** seluruh referensi dapat ditelusuri ke field snapshot; tidak ada ID/kandidat/evidence rekaan; ketidakpastian sumber dipertahankan; 11 tes khusus lulus; dan tidak ada perubahan pada komponen di luar modul baru serta dokumen terkait.


## 10. Hasil implementasi v1

- Modul terpisah: `tools/utterance_interpretation.py`, fungsi publik `interpret_utterance(snapshot)`.
- Tes khusus: `tests/test_utterance_interpretation.py`, tepat 11 kasus sesuai cakupan yang disepakati.
- Workflow: `.github/workflows/utterance-interpretation-tests.yml`.
- GitHub Actions Run #1 [46114424670](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46114424670) sukses; log memverifikasi **11/11 tes lulus**.
- Modul hanya membaca snapshot dan menghasilkan laporan. Tidak ada perubahan pada komponen sumber maupun integrasi runtime.
- Klasifikasi maksud dibatasi pada tanda tanya eksplisit, token `tolong`, dan token `jangan`; pola lain tetap `unknown` / `unresolved`. Penanda yang muncul bersamaan dicatat sebagai bentuk komunikatif yang sama-sama teramati, bukan sebagai kandidat yang saling bersaing. Perbaikan kompatibel untuk hal ini dicatat pada bagian 10.1.
- Kebijakan klarifikasi, pengenalan reference, perluasan pola intent, dan integrasi runtime tetap pekerjaan terpisah.


## 10.1 Perbaikan representasi penanda komunikatif yang berkoeksistensi

Audit implementasi menemukan bahwa tanda tanya bersama token `tolong`, atau token `tolong` bersama `jangan`, sebelumnya dilaporkan sebagai `ambiguous`. Itu tidak tepat: setiap penanda eksplisit adalah observasi bentuk komunikatif yang dapat hadir bersamaan, bukan alternatif label yang harus dipilih salah satu.

Perilaku diperbaiki secara kompatibel pada `tools/utterance_interpretation.py`:
- Field baru `labels` selalu berisi daftar label eksplisit yang teramati, mengikuti urutan tetap: `question`, `request`, `directive`.
- Jika hanya satu label teramati, `status`, `label`, dan `candidates` mempertahankan perilaku v1; `labels` berisi satu item.
- Jika lebih dari satu label teramati, `status` adalah `resolved`, `label` bernilai null, `labels` memuat semua penanda, dan `candidates` kosong karena tidak ada pilihan yang saling bersaing. Evidence tiap penanda tetap dirujuk ke sumber snapshot yang tepat.
- Jika tidak ada penanda yang didukung, hasil tetap `unknown` / `unresolved` dengan `labels` kosong.
- Ini hanya pencatatan bentuk eksplisit; tidak menyimpulkan hubungan pragmatis, tidak memilih maksud tersembunyi, dan tidak memicu klarifikasi.

Verifikasi terfokus:
- Tes baru `tests/test_utterance_intent_coexistence.py`: tepat 4 kasus (question+request, request+directive, kompatibilitas satu penanda, dan kondisi tanpa penanda).
- Workflow `.github/workflows/utterance-intent-coexistence-tests.yml`.
- GitHub Actions Run #1 [46120863024](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46120863024): log memverifikasi **4/4 tes lulus**.
- Suite lama `tests/test_utterance_interpretation.py` dijalankan otomatis sebagai kompatibilitas: Run [46120842200](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46120842200), **11/11 tes lulus**.
- Tidak ada perubahan pada snapshot, parser, POS, kamus, planner, penyaji klarifikasi, atau runtime.
