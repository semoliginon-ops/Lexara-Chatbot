# Rancangan Penanganan Ambiguitas dan Maksud Ujaran v1

**Status:** rancangan tahap awal; belum diimplementasikan dan belum terhubung ke runtime.
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

## 9. Skema keluaran minimal v1 (rancangan)

Keluaran dirancang sebagai laporan baca-saja atas satu Context Snapshot. Bentuk ini belum menjadi kontrak implementasi final sampai modul dan tes khusus dibuat.

```json
{
  "schema_version": "1.0",
  "source": {
    "snapshot_status": "assembled | partial | deferred",
    "parser_status": "nilai asli parser atau null"
  },
  "ambiguity": {
    "status": "resolved | ambiguous | unresolved | deferred",
    "items": [
      {
        "dimension": "lexical_sense | pos | syntax | reference | intent",
        "token_index": 0,
        "candidate_refs": [
          {
            "source_field": "lexical_candidates",
            "candidate_id": "ID kandidat asli atau null"
          }
        ],
        "evidence_refs": [
          {
            "source_field": "field sumber asli",
            "token_index": 0
          }
        ],
        "status": "ambiguous",
        "reason": "multiple_supported_candidates"
      }
    ]
  },
  "communicative_intent": {
    "status": "resolved | ambiguous | unresolved | deferred",
    "label": "question | request | directive | assertion | expressive | fragment | unknown",
    "candidates": [],
    "evidence_refs": [],
    "reason": "explicit_marker | explicit_construction | insufficient_evidence"
  }
}
```

### Aturan skema

- `source.snapshot_status` dan `source.parser_status` menyalin status sumber; jangan menormalkan atau menghapus nilai aslinya.
- `ambiguity.items` hanya dibuat bila ada ketidakpastian yang dilaporkan sumber atau ditemukan oleh aturan v1 yang eksplisit. Jangan membuat catatan hanya karena sistem belum memiliki kemampuan menganalisis suatu dimensi.
- `dimension` menjelaskan jenis ketidakpastian; `token_index` boleh `null` bila ketidakpastian berada pada tingkat ujaran atau tidak dapat dipetakan aman ke satu token.
- `candidate_refs` menunjuk kandidat yang benar-benar tersedia pada snapshot atau komponen yang secara eksplisit dirujuk. Jangan menyalin lalu mengubah kandidat menjadi kandidat baru.
- `evidence_refs` adalah rujukan ke data sumber, bukan evidence baru. Setiap rujukan harus dapat ditelusuri kembali ke snapshot.
- `ambiguity.status` adalah ringkasan dimensi ambiguitas, bukan pengganti status per item. Jika item-item memiliki status berbeda, ringkasan mengikuti keadaan paling tidak pasti; urutan konservatif: deferred, unresolved, ambiguous, resolved.
- `communicative_intent.label` hanya diisi satu label jika tepat satu kandidat didukung bukti eksplisit. Jika beberapa kandidat masih mungkin, `label` harus `null`, status `ambiguous`, dan kandidat tetap tercatat. Jika bukti tidak cukup, gunakan `unknown` dengan status `unresolved`; jangan menganggap semua kalimat otomatis assertion.
- `reason` menjelaskan dasar status dan bukan skor keyakinan. Tidak ada probabilitas atau confidence score pada v1.
- Nilai contoh di atas adalah ilustrasi tipe data, bukan daftar aturan aktif. Nama field sumber harus diverifikasi terhadap snapshot sebelum implementasi.

### Batas keputusan untuk implementasi berikutnya

Implementasi pertama hanya boleh:
1. memvalidasi dan merujuk status/kandidat yang sudah ada pada snapshot;
2. membuat catatan ambiguitas untuk kasus yang benar-benar dapat ditunjuk sumbernya;
3. mengklasifikasikan bentuk komunikatif yang memiliki pola eksplisit dan telah disepakati sebagai aturan terbatas;
4. mengembalikan unresolved/deferred bila tidak ada bukti aman.

Implementasi pertama tidak boleh memilih sense baru, menafsirkan implikatur, menyimpulkan niat psikologis, mengeluarkan teks klarifikasi, atau mengubah komponen sumber.

