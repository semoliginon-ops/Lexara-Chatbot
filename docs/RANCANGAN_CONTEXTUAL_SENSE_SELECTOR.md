# Rancangan Contextual Sense Selector v1 — Lexara

**Status:** Disetujui pengguna pada 28 November 2026; implementasi v1 selesai dan terverifikasi.
**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.
**Prasyarat:** Context Evidence Generator v1 tersedia.
**Tujuan:** Memilih satu sense hanya jika evidence kontekstual benar-benar membedakan sense tersebut dari seluruh alternatif; selain itu mempertahankan ambiguitas atau abstention.

## 1. Tanggung jawab dan batas

Selector menerima satu kelompok kandidat sense untuk **satu kemunculan token/leksem** beserta evidence yang dihasilkan Context Evidence Generator.

Selector:
- tidak membuat atau mengubah evidence;
- tidak menambah, menghapus, atau menggabungkan kandidat dalam audit;
- tidak menebak berdasarkan frekuensi, urutan kata, POS, kedekatan token, atau kemiripan label konsep;
- tidak menggunakan relasi Concept Layer untuk menyimpulkan sense;
- tidak menggabungkan evidence dari token berbeda atau klausa berbeda;
- tidak mengubah resolver semantic-role yang sudah ada.

Satu pemanggilan selector hanya boleh membandingkan kandidat yang berasal dari kemunculan leksikal yang sama. Pemanggil bertanggung jawab memisahkan kelompok kandidat per kemunculan token. Selector tidak boleh menganggap semua sense dalam satu kalimat sebagai alternatif satu sama lain.

## 2. Input dan validasi

Antarmuka konseptual:

~~~python
select_contextual_sense(sense_candidates, evidence)
~~~

- `sense_candidates`: daftar kandidat per-sense dari adapter, untuk satu kemunculan token. Setiap kandidat minimal memiliki `sense_id`; metadata lain dipertahankan.
- `evidence`: daftar evidence dari Context Evidence Generator v1.

Validasi:
- `sense_id` kandidat harus berupa teks nonkosong dan unik dalam satu kelompok.
- Setiap evidence harus memiliki `sense_id` yang cocok dengan salah satu kandidat.
- Evidence dengan `polarity` selain `supports`/`contradicts` atau `strength` selain `weak`/`strong` ditolak sebagai input tidak valid.
- Evidence untuk sense yang tidak ada dalam kelompok kandidat tidak boleh memengaruhi keputusan; catat sebagai ignored dengan alasan `unknown_sense`.
- Evidence weak tetap disimpan dalam audit, tetapi tidak ikut menentukan kelayakan atau pemenang.
- Selector tidak membaca aturan konteks dan tidak memvalidasi ulang kebenaran linguistik aturan; itu tanggung jawab generator/kurasi.

## 3. Makna bukti untuk keputusan

Keputusan hanya memakai evidence `strong`.

Untuk setiap sense:
- **strong support**: ada minimal satu evidence strong dengan polarity `supports`.
- **strong contradiction**: ada minimal satu evidence strong dengan polarity `contradicts`.
- **conflicted**: sense memiliki strong support dan strong contradiction sekaligus.
- **excluded**: sense memiliki strong contradiction dan tidak memiliki strong support.
- **viable**: sense tidak excluded. Sense conflicted tetap tercatat viable untuk mencegah kontradiksi dipakai sebagai penghapusan otomatis, tetapi tidak boleh dipilih sebagai pemenang.

Satu evidence strong yang telah dikurasi dapat menjadi dasar keputusan; beberapa evidence weak tidak pernah dijumlahkan atau dinaikkan menjadi strong. Banyaknya evidence tidak menjadi skor.

## 4. Aturan pemilihan konservatif

Selector mengeluarkan `selected` hanya jika seluruh syarat ini terpenuhi:
1. Tepat satu sense viable.
2. Sense tersebut memiliki minimal satu strong support.
3. Sense tersebut tidak memiliki strong contradiction.
4. Setiap sense alternatif berstatus excluded, yaitu memiliki strong contradiction tanpa strong support.

Dengan demikian:
- Strong support pada satu sense **tidak cukup** jika alternatif masih tidak terbantahkan.
- Strong contradiction pada alternatif **tidak cukup** jika sense yang didukung juga memiliki kontradiksi kuat.
- Dua sense yang sama-sama mendapat strong support tidak dipaksa menjadi satu pemenang.
- Bukti lemah tidak mengubah keputusan meskipun jumlahnya banyak.

Aturan ini sengaja mengutamakan abstention daripada pilihan yang tidak memiliki pembeda kuat terhadap semua alternatif.

## 5. Status keluaran

Status selector dipisahkan dari status generator (`evidence_found`/`no_evidence`).

| Status selector | Kondisi |
|---|---|
| `selected` | Satu sense memenuhi seluruh aturan pemilihan pada bagian 4. |
| `ambiguous` | Dua atau lebih sense tetap viable; termasuk tidak ada evidence pembeda, hanya evidence weak, atau beberapa kandidat mendapat dukungan kuat. |
| `unresolved` | Tidak ada kandidat, tidak ada sense yang dapat dipilih dan tersisa paling banyak satu sense viable tanpa strong support, atau konflik kuat membuat keputusan tidak aman. |
| `not_needed` | Hanya ada satu kandidat dan tidak ada strong contradiction; selector tidak mengklaim pemilihan kontekstual. Kandidat tunggal diteruskan apa adanya. |

Alasan keluaran yang disarankan:
- `one_sense_supported_all_alternatives_excluded`
- `multiple_viable_senses`
- `insufficient_strong_evidence`
- `strong_evidence_conflict`
- `no_candidates`
- `single_candidate_no_context_decision`

Tidak ada status probabilistik atau confidence score pada v1.

## 6. Konflik dan audit

- Evidence supports dan contradicts untuk sense yang sama tidak saling menghapus.
- Sense dengan kedua jenis strong evidence ditandai `conflicted` dan tidak boleh menang.
- Evidence weak tetap muncul dalam audit sebagai non-decisive.
- Evidence yang tidak cocok dengan kelompok kandidat dicatat sebagai ignored; tidak boleh diam-diam dipakai.
- Semua kandidat asli dipertahankan dalam keluaran audit, beserta ringkasan strong supports, strong contradictions, weak evidence, status kandidat, dan alasan keputusan.
- Jika lebih dari satu kandidat viable, status tetap `ambiguous`; jangan memilih berdasarkan urutan kandidat atau jumlah evidence.

## 7. Bentuk keluaran konseptual

~~~python
{
    "status": "selected | ambiguous | unresolved | not_needed",
    "reason": "reason_code",
    "selected_sense_id": None,  # terisi hanya saat status selected
    "candidate_audit": [
        {
            "sense_id": "...",
            "state": "viable | excluded | conflicted",
            "strong_supports": [],
            "strong_contradictions": [],
            "weak_evidence": []
        }
    ],
    "used_evidence": [],
    "ignored_evidence": []
}
~~~

Bentuk ini masih konseptual dan akan diselaraskan dengan struktur aktual adapter/generator sebelum implementasi. Selector tidak memodifikasi objek input.

## 8. Skenario uji terfokus yang diusulkan

Tepat 12 tes unit untuk modul selector baru:
1. satu kandidat tanpa strong contradiction menghasilkan `not_needed`, bukan klaim resolusi kontekstual;
2. nol kandidat menghasilkan `unresolved`;
3. strong support pada satu kandidat dan strong contradiction pada semua alternatif menghasilkan `selected`;
4. strong support tanpa bukti kuat untuk menyingkirkan alternatif tetap `ambiguous`;
5. dua kandidat dengan strong support tetap `ambiguous`;
6. strong support dan strong contradiction pada kandidat yang sama menghasilkan konflik dan tidak dipilih;
7. strong contradiction pada semua kandidat menghasilkan `unresolved`;
8. evidence weak saja tidak memilih dan tidak dieliminasi berdasarkan jumlah;
9. evidence untuk sense di luar kandidat diabaikan dan dicatat;
10. evidence dari kandidat lain tidak tercampur ke kelompok token ini;
11. seluruh kandidat dan evidence tetap tersedia pada audit;
12. input tidak berubah dan hasil deterministik.

Tes tidak menjalankan ulang tes generator atau Concept Layer yang telah lulus. Workflow GitHub Actions selector harus terpisah dan hanya dipicu oleh perubahan modul serta tes selector; perubahan file workflow saja tidak memicu tes.

## 9. Batas dan pekerjaan lanjutan

- Draf ini belum menetapkan integrasi ke analyzer/runtime.
- Draf ini belum membuat dataset aturan konteks linguistik; kualitas keputusan tetap dibatasi oleh aturan reviewed yang tersedia.
- Selector tidak menyelesaikan kekurangan cakupan parser atau kamus.
- Integrasi per kemunculan token memerlukan orkestrasi yang memastikan kandidat dan evidence berasal dari token yang sama; hal itu tidak boleh diasumsikan dari daftar kandidat satu kalimat.
- Selepas desain disetujui, implementasi dilakukan sebagai modul terpisah dengan 12 tes terfokus. Checklist dan dokumen status baru diperbarui setelah implementasi dan verifikasi benar-benar selesai.

**Keputusan pengguna:** disetujui pada 28 November 2026. Implementasi v1 tersedia pada `tools/contextual_sense_selector.py`; tepat 12 tes khusus lulus melalui GitHub Actions Run #3. Integrasi runtime tetap di luar cakupan.
