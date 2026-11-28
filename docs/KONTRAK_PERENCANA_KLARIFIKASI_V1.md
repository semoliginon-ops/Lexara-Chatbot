# Kontrak Perencana Klarifikasi v1

**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.  
**Status:** kontrak desain; belum diimplementasikan dan belum terhubung ke dialog/runtime.  
**Masukan utama:** laporan `interpret_utterance(snapshot)` dari `tools/utterance_interpretation.py`.

## 1. Tujuan dan batas

Perencana v1 adalah modul read-only yang menentukan apakah ada satu ketidakpastian yang layak diajukan sebagai fokus klarifikasi. Modul ini **bukan** pembentuk kalimat, pengelola dialog, pemilih sense, atau pemanggil analyzer/parser.

Perencana tidak boleh menyimpulkan sendiri dampak terhadap jawaban berikutnya atau kemampuan pengguna membedakan kandidat. Kedua fakta tersebut harus diberikan secara eksplisit oleh pemanggil sebagai peluang klarifikasi yang telah dinilai. Jika bukti tersebut tidak ada, perencana tidak bertanya.

Tidak ada integrasi runtime, penyimpanan giliran, pengiriman pertanyaan, maupun pemrosesan jawaban pada v1.

## 2. Input

Fungsi publik yang direncanakan:

`plan_clarification(report, opportunities=None)`

- `report`: keluaran laporan interpretasi v1.
- `opportunities`: list opsional berisi penilaian eksternal untuk item ambiguity tertentu. Setiap item memiliki:
  - `ambiguity_item_index`: indeks item dalam `report["ambiguity"]["items"]`;
  - `candidate_refs`: sedikitnya dua referensi kandidat yang benar-benar terdapat pada `candidate_refs` item sumber;
  - `material_to_next_response`: boolean eksplisit;
  - `user_can_distinguish`: boolean eksplisit;
  - `priority`: integer non-negatif; angka lebih kecil berarti lebih diprioritaskan.

Tidak ada teks pertanyaan atau deskripsi kandidat yang dibuat/direka oleh perencana. Tidak ada kandidat baru yang boleh disuplai melalui `opportunities`.

## 3. Validasi dan keterlacakan

- Bentuk dasar `report` harus memiliki object `ambiguity`, list `ambiguity.items`, dan status sumber yang dikenali.
- Indeks item harus berada dalam rentang.
- Setiap referensi peluang harus cocok persis dengan salah satu referensi kandidat pada item sumber; referensi duplikat ditolak.
- Item sumber harus berstatus `ambiguous`; `resolved`, `unresolved`, dan `deferred` tidak dapat menjadi fokus pilihan kandidat.
- Dua atau lebih referensi harus tersedia. Kasus satu objek kandidat yang memuat beberapa `sense_ids` tetapi hanya satu `candidate_ref` belum cukup untuk pilihan aman pada v1.
- Input peluang yang rusak atau tidak dapat ditelusuri menghasilkan abstention aman, bukan pertanyaan.
- Modul tidak mengubah input.

## 4. Keputusan

Keputusan keluaran hanya salah satu dari:

| Keputusan | Kondisi |
|---|---|
| `ask` | Ada peluang valid dengan sedikitnya dua kandidat sumber, `material_to_next_response=true`, dan `user_can_distinguish=true`. |
| `defer` | Laporan ambiguity berstatus `deferred`, atau sumber item yang relevan ditandai deferred. |
| `abstain` | Ada ketidakpastian, tetapi kandidat tidak cukup/aman, atau data peluang tidak valid/tidak tersedia untuk menilai syarat wajib. |
| `proceed` | Tidak ada ketidakpastian yang relevan untuk diklarifikasi, atau seluruh peluang valid secara eksplisit tidak material/tidak dapat dibedakan pengguna. |

Prioritas dipakai hanya di antara peluang yang seluruh syarat `ask`-nya telah terpenuhi. Pilih priority terkecil; jika seri, pilih item yang muncul lebih dahulu dalam laporan. Keluaran memuat tepat satu fokus. Tidak ada penggabungan pertanyaan.

## 5. Maksud komunikatif

`communicative_intent` tidak diperlakukan sebagai sekumpulan pilihan sense. Beberapa penanda seperti tanda tanya dan `tolong` dapat hadir bersamaan. Status `communicative_intent.status == "ambiguous"` saja **tidak** membuat peluang klarifikasi dan tidak boleh memicu `ask`.

Perencana v1 hanya mengatur ambiguity items yang memiliki kandidat sumber. Ia tidak menanyakan pengguna apakah ujarannya merupakan `question`, `request`, atau `directive`.

## 6. Bentuk keluaran

Keluaran minimal:

```json
{
  "schema_version": "1.0",
  "decision": "ask",
  "reason": "one_material_user_distinguishable_ambiguity",
  "focus": {
    "ambiguity_item_index": 0,
    "candidate_refs": [
      {"source_field": "pos_candidates", "token_index": 1, "candidate_index": 0},
      {"source_field": "pos_candidates", "token_index": 1, "candidate_index": 1}
    ]
  }
}
```

Untuk `proceed`, `abstain`, dan `defer`, `focus` bernilai null. Keluaran tidak berisi teks pertanyaan, jawaban yang diasumsikan, confidence score, ataupun perubahan pada laporan sumber.

## 7. Batas yang sengaja ditunda

- Memperbaiki representasi beberapa sense dalam satu kandidat leksikal.
- Menentukan materialitas secara otomatis dari semantik respons.
- Menyusun redaksi pertanyaan dan label kandidat yang ramah pengguna.
- Mengelola jawaban, jawaban parsial, penolakan, dan riwayat beberapa giliran.
- Menggabungkan perencana dengan dialog/runtime.

Batas ini disengaja: laporan v1 belum menyediakan seluruh informasi yang dibutuhkan untuk menilai materialitas dan menyusun pertanyaan yang aman. Perencana tidak boleh menutupi kekurangan itu dengan inferensi.

## 8. Cakupan tes khusus yang disepakati

Tepat **11 tes unit khusus** pada `tests/test_clarification_planner.py`:

1. menolak bentuk dasar laporan yang tidak valid;
2. menghasilkan `proceed` jika tidak ada ambiguity item;
3. menghasilkan `defer` untuk status ambiguity deferred;
4. tidak bertanya pada item syntax `unresolved` tanpa kandidat;
5. abstain jika item ambiguous hanya memiliki kurang dari dua candidate refs;
6. tidak bertanya jika peluang tidak menyatakan dampak material;
7. tidak bertanya jika pengguna tidak dapat membedakan kandidat;
8. menghasilkan satu fokus `ask` untuk peluang valid dengan dua atau lebih referensi sumber;
9. memilih peluang valid berprioritas tertinggi dan hanya satu fokus;
10. tidak menjadikan beberapa penanda communicative intent sebagai alasan bertanya;
11. abstain jika indeks item atau candidate refs peluang tidak cocok dengan laporan.

Tes memakai fixture laporan kecil; tidak mengulang 11 tes utterance interpretation, 10 tes Context Snapshot, atau regression suite 450 tes. Implementasi kelak hanya boleh menambah modul perencana, berkas tes tersebut, workflow khusus, dan pembaruan dokumentasi terkait. Tidak mengubah modul interpretasi, snapshot, kamus, morfologi, POS, parser, resolver, generator, selector, aturan konteks, atau runtime.

**Kriteria penerimaan:** keputusan `ask` hanya muncul jika semua syarat kebijakan terbukti eksplisit dan kandidat dapat ditelusuri; satu keputusan memiliki paling banyak satu fokus; tidak ada inferensi maksud atau pertanyaan atas kegagalan internal; tepat 11 tes khusus lulus melalui workflow terfokus.

## 9. Hasil implementasi v1

- Modul read-only: `tools/clarification_planner.py`, fungsi publik `plan_clarification(report, opportunities=None)`.
- Tes khusus: `tests/test_clarification_planner.py`, tepat 11 kasus sesuai cakupan kontrak.
- Workflow: `.github/workflows/clarification-planner-tests.yml`.
- GitHub Actions Run #3 [46117392802](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46117392802) sukses; log memverifikasi **11/11 tes lulus**.
- Modul hanya mengembalikan keputusan dan satu referensi fokus; tidak membuat kalimat pertanyaan, tidak memproses jawaban, dan tidak terhubung ke runtime.
- Tidak ada regression suite 450 tes, tes Context Snapshot, atau tes utterance interpretation yang dijalankan ulang.
