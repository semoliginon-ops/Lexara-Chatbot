# Kontrak Representasi Konsep dan Relasi — Lexara Concept Layer v1

**Status:** Disetujui pengguna pada 28 November 2026; spesifikasi desain v1. Belum menjadi implementasi.
**Pemilik:** Tahap 3 — Hubungan makna dan pemrosesan konteks.

## 1. Tujuan dan batas

Concept Layer menyediakan identitas konsep yang stabil, pemetaan dari sense kamus ke konsep, dan relasi eksplisit antarkonsep. Lapisan ini menjadi sumber pengetahuan konseptual untuk pekerjaan Tahap 3 berikutnya.

Lapisan konsep **terpisah dari data kamus**. Kamus, batch, indeks, definisi sense, anotasi relasi leksikal per-sense, morfologi, klitik, POS, parser, dan resolver yang sudah tersedia tidak diubah sebagai bagian dari kontrak ini.

Tiga berkas JSONL disiapkan di `data/concepts/`:

- `concepts.jsonl`
- `sense_concept_map.jsonl`
- `concept_relations.jsonl`

Satu baris berisi satu objek JSON mandiri. Berkas kosong atau belum tersedia tidak boleh ditafsirkan sebagai bukti bahwa suatu konsep atau relasi tidak ada; konsumen harus membedakan data kosong, data belum dimuat, dan data tidak valid.

## 2. Skema data

### 2.1 `concepts.jsonl`

Satu record mendefinisikan satu konsep, bukan satu kata atau satu lema.

```json
{
  "concept_id": "C000001",
  "label": "jalur",
  "definition": "Lintasan yang dapat dilalui orang atau kendaraan.",
  "status": "reviewed",
  "evidence": {
    "source_type": "lexical_definition",
    "source_ref": "K0020-S1",
    "rationale": "Definisi konsep dirumuskan dari makna sense yang dirujuk."
  }
}
```

Ketentuan:
- `concept_id` wajib, unik, stabil, berformat `C` diikuti enam digit atau lebih, dan tidak boleh digunakan ulang.
- `label` dan `definition` wajib berupa string nonkosong.
- `status` wajib salah satu dari `proposed`, `reviewed`, atau `rejected`.
- `evidence` wajib mengikuti struktur pada bagian 2.4.
- Konsep yang belum memiliki pemetaan sense atau relasi boleh disimpan.
- Label bukan identitas konsep; dua konsep dapat memiliki label mirip jika definisi dan cakupan maknanya berbeda.

### 2.2 `sense_concept_map.jsonl`

Satu record menghubungkan satu sense kamus dengan satu konsep.

```json
{
  "sense_id": "K0020-S1",
  "concept_id": "C000001",
  "status": "reviewed",
  "evidence": {
    "source_type": "lexical_definition",
    "source_ref": "K0020-S1",
    "rationale": "Sense ini merujuk pada lintasan yang dapat dilalui."
  }
}
```

Ketentuan:
- `sense_id` harus merujuk ke sense yang benar-benar ada pada kamus; format ID mengikuti ID sense kamus, bukan ID baru buatan Concept Layer.
- `concept_id` harus merujuk ke record konsep yang ada.
- Satu sense boleh memiliki nol, satu, atau beberapa pemetaan konsep jika setiap pemetaan memiliki alasan yang dapat dipertanggungjawabkan.
- Beberapa sense boleh dipetakan ke konsep yang sama jika cakupan maknanya memang setara.
- Pasangan `sense_id` + `concept_id` harus unik. Perubahan status atau bukti memperbarui record pasangan yang sama, bukan membuat duplikat.
- Sense yang belum dipetakan adalah kondisi sah dan tidak boleh dipaksa masuk ke konsep terdekat.

### 2.3 `concept_relations.jsonl`

Satu record menyatakan relasi berarah dari satu konsep ke konsep lain.

```json
{
  "relation_id": "R000001",
  "source": "C000001",
  "type": "PART_OF",
  "target": "C000005",
  "status": "reviewed",
  "evidence": {
    "source_type": "curated_knowledge",
    "source_ref": null,
    "rationale": "Konsep sumber merupakan bagian dari konsep target."
  }
}
```

Ketentuan:
- `relation_id` wajib, unik, stabil, berformat `R` diikuti enam digit atau lebih, dan tidak boleh digunakan ulang.
- `source` dan `target` wajib merujuk ke konsep yang ada.
- `source` dan `target` tidak boleh sama kecuali kelak ada tipe relasi refleksif yang secara eksplisit disetujui; v1 tidak mendefinisikan tipe seperti itu.
- Identitas relasi adalah kombinasi `source` + `type` + `target`; kombinasi identik tidak boleh muncul dua kali.
- Relasi bersifat berarah. Relasi kebalikan tidak dibuat otomatis dan, bila diperlukan, harus dicatat sebagai record terpisah.
- Relasi yang belum pasti tetap dapat disimpan dengan status `proposed`; relasi yang ditolak dapat dipertahankan sebagai `rejected` untuk jejak audit.

### 2.4 Struktur bukti

Semua record wajib memiliki objek `evidence`:

- `source_type`: string nonkosong yang menjelaskan jenis dasar bukti, misalnya `lexical_definition`, `usage_example`, `curated_knowledge`, atau `corpus_observation`.
- `source_ref`: string atau `null`; bila ada, menunjuk sumber yang dapat ditelusuri, misalnya `K0020-S1` atau ID contoh/dokumen.
- `rationale`: string nonkosong yang menjelaskan mengapa record dibuat.

Bukti harus cukup untuk ditinjau ulang. Label atau kemiripan kata saja bukan bukti relasi.

## 3. Status dan penggunaan aktif

Nilai status untuk konsep, pemetaan, dan relasi:

- `proposed`: usulan, belum diterima.
- `reviewed`: sudah ditinjau dan diterima.
- `rejected`: sudah ditinjau dan ditolak.

Hanya record berstatus `reviewed` yang boleh dipakai sebagai pengetahuan aktif oleh komponen runtime. Record `proposed` dan `rejected` tetap tersedia untuk proses kurasi/audit, tetapi tidak boleh memengaruhi hasil pemahaman atau inferensi.

Pemetaan hanya aktif jika record pemetaan berstatus `reviewed` **dan** record konsep tujuannya berstatus `reviewed`. Relasi hanya aktif jika record relasi serta kedua konsep ujungnya berstatus `reviewed`.

## 4. Katalog tipe relasi v1

| Tipe | Makna arah |
|---|---|
| `IS_A` | source merupakan jenis/subtipe dari target |
| `PART_OF` | source merupakan bagian dari target |
| `HAS_PART` | source memiliki target sebagai bagian |
| `CAUSES` | source menyebabkan target |
| `USED_FOR` | source digunakan untuk tujuan/fungsi target |
| `HAS_PROPERTY` | source memiliki sifat yang dinyatakan target |
| `LOCATED_IN` | source berada di lokasi/ruang target |
| `ASSOCIATED_WITH` | source memiliki hubungan konseptual yang relevan dengan target, tanpa klaim relasi lebih spesifik |

Tipe relasi harus berasal dari katalog ini. Penambahan tipe baru memerlukan revisi kontrak dan persetujuan, bukan penggunaan string bebas.

Arah tidak boleh dibalik secara otomatis. Contohnya, `A PART_OF B` tidak otomatis menghasilkan `B HAS_PART A`; record kebalikan hanya ditambahkan jika memang diinginkan dan didukung bukti. `ASSOCIATED_WITH` bukan pengganti untuk relasi yang lebih spesifik jika bukti jenis relasinya tersedia.

## 5. Aturan identitas, konsistensi, dan konservatisme

1. ID konsep dan relasi stabil serta tidak pernah digunakan ulang.
2. Tidak ada pemetaan atau relasi berdasarkan kemiripan bentuk kata semata.
3. Satu lema dengan beberapa sense tidak boleh dipetakan sekaligus tanpa mengacu pada `sense_id` yang tepat.
4. Satu sense boleh memiliki beberapa konsep, tetapi setiap record pemetaan harus punya bukti mandiri.
5. Konsep tanpa relasi dan sense tanpa pemetaan diperbolehkan.
6. Relasi konseptual tidak disalin dari `synonyms`, `antonyms`, atau `related_terms` pada kamus.
7. Tidak ada pewarisan relasi entri lama ke semua sense.
8. Tidak ada asumsi simetri atau invers otomatis.
9. Ketidakpastian dipertahankan melalui status `proposed` atau ketiadaan record; jangan memaksakan hubungan.
10. Data kamus lama tetap menjadi sumber sense dan tidak perlu dimigrasikan ke format Concept Layer.

## 6. Validasi struktural yang direncanakan

Validator terpisah nantinya memeriksa:
- Setiap baris merupakan JSON object yang valid.
- Field wajib ada dan memiliki tipe yang benar; field tambahan yang tidak dikenal ditolak agar kontrak tidak berkembang diam-diam.
- ID sesuai pola, unik dalam ruang ID-nya, dan stabil dalam pembaruan data.
- Nilai status dan tipe relasi termasuk katalog yang diizinkan.
- Semua referensi `sense_id` dan `concept_id` dapat diresolusikan.
- Pasangan pemetaan dan kombinasi relasi tidak duplikat.
- Bukti memiliki `source_type`, `source_ref`, dan `rationale` sesuai tipe yang ditentukan.
- Referensi diri pada relasi ditolak pada v1.
- Hanya record `reviewed` yang memenuhi syarat untuk membangun graf aktif; status konsep juga diperhitungkan.

Validasi struktural tidak membuktikan kebenaran linguistik. Ketepatan konsep, pemetaan, dan relasi tetap membutuhkan kurasi berbasis bukti.

## 7. Batas implementasi dan urutan kerja

Urutan pekerjaan setelah kontrak disetujui:

1. Menulis dan meninjau spesifikasi ini.
2. Membuat validator struktural terpisah dan tes unit dengan data fixture sintetis.
3. Memvalidasi fixture positif/negatif tanpa menyentuh kamus utama.
4. Membuat pembaca data konsep baca-saja setelah validator stabil.
5. Menyusun integrasi pemilihan sense kontekstual pada pekerjaan Tahap 3 berikutnya.

Di luar cakupan dokumen ini:
- mengubah batch kamus atau indeks;
- menambah/mengubah lema atau anotasi relasi leksikal;
- mengubah morfologi, klitik, POS, parser, atau resolver yang sudah ada;
- menjalankan ulang regression suite 450 tes tanpa perubahan yang memberi alasan teknis;
- membuat klaim bahwa pemahaman konteks sudah aktif sebelum pembaca dan integrasi runtime tersedia.

## 8. Status

Kontrak desain v1 disetujui pengguna pada 28 November 2026. Dokumen ini menetapkan format dan batas desain, bukan bukti bahwa data, validator, pembaca, atau integrasi runtime sudah dibuat. Baseline regresi yang berlaku tetap GitHub Actions Run #260 (450/450); tidak ada tes atau workflow yang dijalankan untuk menyetujui kontrak ini.
