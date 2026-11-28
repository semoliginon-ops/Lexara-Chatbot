# Kontrak Perencana Klarifikasi v1.1 — Referensi Sense-Level

**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.  
**Status:** kontrak desain; belum diimplementasikan.  
**Kompatibilitas:** mempertahankan jalur candidate_refs v1; menambahkan jalur sense_refs untuk beberapa sense di dalam satu kandidat entri.  
**Masukan:** laporan interpretasi v1, peluang klarifikasi eksplisit, dan Context Snapshot asli untuk validasi sense.

## 1. Alasan versi 1.1

Audit AUDIT_SUMBER_DESKRIPSI_KANDIDAT_KLARIFIKASI.md menemukan bahwa snapshot mempertahankan objek kandidat leksikal lengkap, termasuk entry.senses[]. Setiap sense memiliki sense_id dan definition.

Namun, laporan interpretasi v1 hanya menunjuk objek kandidat melalui candidate_refs. Satu kandidat entri dapat berisi beberapa sense. Contoh bangun mempunyai satu kandidat entri K0016 dengan K0016-S1 dan K0016-S2. Planner v1 tidak dapat meminta klarifikasi untuk dua sense tersebut karena hanya melihat satu referensi kandidat.

v1.1 menambahkan referensi sense-level tanpa mengubah kamus, Context Snapshot, atau laporan interpretasi v1.

## 2. Fungsi dan input

Fungsi publik versi berikutnya:

    plan_clarification(report, opportunities=None, snapshot=None)

- report: keluaran interpret_utterance(snapshot) yang sudah ada.
- opportunities: penilaian eksplisit materialitas, kemampuan pengguna membedakan opsi, dan prioritas.
- snapshot: Context Snapshot yang sama dengan sumber laporan; diperlukan untuk memvalidasi referensi sense-level.

Jalur lama candidate_refs tetap dapat digunakan tanpa snapshot jika semua syarat v1 terpenuhi. Jalur baru sense_refs wajib memiliki snapshot.

## 3. Bentuk referensi sense

Setiap sense_ref harus memuat semua field berikut:

~~~json
{
  "source_field": "lexical_candidates",
  "token_index": 0,
  "candidate_index": 0,
  "sense_index": 0,
  "sense_id": "K0016-S1"
}
~~~

Referensi harus cocok dengan seluruh rantai sumber:
1. token_index menunjuk token yang sama dengan ambiguity item.
2. candidate_index menunjuk kandidat yang ditunjuk oleh parent_candidate_ref.
3. sense_index menunjuk objek sense yang benar pada snapshot.tokens[token_index].lexical_candidates[candidate_index].entry.senses[].
4. sense_id harus sama persis dengan sense_id pada objek sense tersebut.
5. Objek sense harus memiliki definition berupa teks nonkosong. Definisi ini menjadi sumber uraian opsi pada kontrak interaksi, bukan teks buatan perencana.

Tidak cukup hanya mencocokkan sense_id; indeks sumber dan hubungan parent harus cocok juga.

## 4. Bentuk peluang klarifikasi sense-level

Peluang sense-level memiliki:
- ambiguity_item_index;
- parent_candidate_ref: satu referensi kandidat yang ada pada ambiguity item;
- sense_refs: sedikitnya dua referensi sense yang berbeda dan berasal dari parent tersebut;
- material_to_next_response: boolean eksplisit;
- user_can_distinguish: boolean eksplisit;
- priority: integer non-negatif; lebih kecil berarti lebih diprioritaskan.

Peluang tidak boleh mengirim definisi sendiri, membuat sense baru, atau mengubah teks definisi sumber. Deskripsi kandidat diambil dari snapshot setelah referensi tervalidasi.

Jalur candidate_refs lama dan sense_refs baru bersifat alternatif untuk satu peluang. Satu peluang tidak boleh mencampur kedua jenis referensi.

## 5. Syarat keputusan ask

Jalur sense-level hanya boleh menghasilkan ask jika seluruh kondisi berikut benar:
- ambiguity item berstatus ambiguous dan berdimensi lexical_sense;
- parent candidate ref cocok persis dengan salah satu candidate ref item;
- terdapat minimal dua sense ref unik;
- semua sense ref cocok ke snapshot pada token, kandidat, indeks sense, dan ID sense;
- semua sense memiliki definisi nonkosong;
- material_to_next_response == true;
- user_can_distinguish == true.

Jika satu syarat gagal, hasilnya abstain aman, bukan pertanyaan.

Peluang sense-level tidak berlaku untuk POS, sintaksis, maksud komunikatif, atau dimensi lain. Jangan memecah daftar POS atau label maksud menjadi pilihan sense.

## 6. Bentuk fokus keluaran

Untuk peluang sense-level:

~~~json
{
  "schema_version": "1.1",
  "decision": "ask",
  "reason": "one_material_user_distinguishable_sense_ambiguity",
  "focus": {
    "ambiguity_item_index": 0,
    "parent_candidate_ref": {
      "source_field": "lexical_candidates",
      "token_index": 0,
      "candidate_index": 0
    },
    "sense_refs": [
      {
        "source_field": "lexical_candidates",
        "token_index": 0,
        "candidate_index": 0,
        "sense_index": 0,
        "sense_id": "K0016-S1"
      },
      {
        "source_field": "lexical_candidates",
        "token_index": 0,
        "candidate_index": 0,
        "sense_index": 1,
        "sense_id": "K0016-S2"
      }
    ]
  }
}
~~~

Untuk jalur kandidat v1, bentuk candidate_refs dipertahankan. Keputusan proceed, abstain, dan defer tetap memiliki focus: null. Hasil tidak mengandung teks pertanyaan atau mengubah snapshot/laporan.

## 7. Batas dan keamanan

- Tidak ada pemilihan sense otomatis. Planner hanya menentukan apakah pilihan dapat diajukan.
- Tidak menggunakan frekuensi, urutan sense, urutan kandidat, atau kemiripan kata sebagai alasan memilih.
- Tidak membuat deskripsi dari lemma, ID, konsep, atau pengetahuan model.
- Jika definisi hilang, kosong, atau referensi tidak cocok, abstain.
- Tidak mengubah tools/utterance_interpretation.py, tools/context_snapshot.py, loader, lookup, kamus, POS, parser, atau runtime.
- Tidak mengubah perilaku planner v1 untuk peluang yang sudah valid.
- Beberapa penanda maksud komunikatif tetap tidak menjadi alasan klarifikasi.

## 8. Cakupan tes khusus yang direncanakan

Tepat **12 tes unit baru** untuk jalur sense-level dan kompatibilitas:

1. menghasilkan satu fokus ask untuk dua sense valid dalam satu kandidat entri;
2. menolak sense refs jika snapshot tidak diberikan;
3. menolak parent candidate ref yang tidak terdapat pada ambiguity item;
4. menolak token index yang tidak cocok dengan ambiguity item;
5. menolak candidate index yang tidak cocok dengan parent ref;
6. menolak sense index di luar rentang;
7. menolak sense ID yang berbeda dari objek sense pada indeks sumber;
8. menolak sense tanpa definition nonkosong;
9. menolak sense refs duplikat;
10. menolak penggunaan sense refs untuk dimensi selain lexical_sense;
11. mempertahankan jalur candidate_refs v1 yang valid;
12. memilih satu peluang sense-level valid dengan prioritas tertinggi saat ada beberapa peluang.

Tes baru tidak mengulang 11 tes planner v1, 11 tes interpretasi, atau 10 tes Context Snapshot. Workflow kelak menjalankan hanya berkas tes v1.1 yang baru. Regression suite 450 tes tidak dijalankan ulang tanpa alasan teknis.

## 9. Batas pekerjaan berikutnya

Setelah kontrak diimplementasikan dengan 12 tes khusus, penyaji interaksi dapat mengambil definisi dari snapshot berdasarkan sense refs yang sudah tervalidasi. Kontrak interaksi tetap mengatur jawaban pilihan, teks bebas/parsial, penolakan, tidak ada respons, dan respons tidak valid.

Belum ada penyaji, sesi dialog, pemrosesan jawaban bebas, penyimpanan permanen, atau integrasi runtime pada kontrak ini.

**Kriteria penerimaan:** dua sense dalam satu entri dapat dirujuk secara terpisah dan diverifikasi terhadap snapshot; tidak ada ID/definisi rekaan; jalur v1 tetap kompatibel; dan tepat 12 tes baru lulus melalui workflow terfokus.
