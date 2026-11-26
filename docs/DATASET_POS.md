# Rancangan Dataset Berlabel untuk Evaluasi POS

**Status:** Dataset 20 kalimat (12 development, 8 test) telah lolos validasi struktur dan tokenizer di Termux pada 27 November 2026; regression suite penuh terakhir terverifikasi 132/132; evaluasi akurasi POS belum dilakukan  
**Tahap:** 2.5 — Pengenalan kelas kata (POS)  
**Versi skema:** 1.0

Dokumen ini menetapkan format dan aturan anotasi dataset untuk menguji identifikasi serta disambiguasi kelas kata. Dokumen ini bukan klaim bahwa akurasi POS sudah diketahui.

## 1. Tujuan

Dataset dipakai untuk menjawab pertanyaan yang terukur:

1. Apakah label POS leksikal sesuai dengan fungsi kata pada kalimat?
2. Apakah aturan konteks lokal memilih POS yang tepat ketika sebuah kata memiliki beberapa kandidat?
3. Apakah sistem menahan keputusan ketika konteks tidak cukup atau petunjuk saling bertentangan?
4. Seberapa banyak token yang berhasil diberi keputusan dibanding yang tetap ambigu, tidak dikenal, atau memerlukan analisis morfologi?

Dataset bukan kumpulan dialog untuk dihafalkan dan bukan data pelatihan model LLM. Sistem tetap memakai aturan dan kamus yang dapat diperiksa.

## 2. Cakupan versi pertama

Target awal: **100 kalimat** yang dianotasi manual dan diperiksa.

Komposisi target (boleh disesuaikan setelah audit contoh, tetapi perubahan harus dicatat):

- 25 kalimat sederhana bahasa Indonesia netral/baku.
- 20 kalimat percakapan informal.
- 15 kalimat dengan kata yang memiliki lebih dari satu POS atau sense.
- 15 kalimat dengan imbuhan atau bentuk turunan.
- 10 kalimat dengan kata tugas, negasi, aspek, atau penanda waktu.
- 10 kalimat dengan susunan atau konteks yang berpotensi ambigu.
- 5 kalimat yang memuat tanda baca, angka, atau variasi penulisan.

Satu kalimat boleh memenuhi lebih dari satu karakteristik. Komposisi di atas adalah panduan cakupan, bukan kuota yang harus dipenuhi dengan kalimat buatan yang tidak alami.

## 3. Pembagian data

Pisahkan contoh menjadi:

- **development (60%)**: untuk memeriksa aturan dan memperbaiki kesalahan selama pengembangan.
- **test (40%)**: disimpan sebagai evaluasi tertahan; jangan dipakai untuk menyetel aturan satu per satu.

Pembagian dilakukan pada tingkat kalimat, bukan token. Kalimat duplikat atau parafrasa yang sangat dekat harus berada pada bagian yang sama agar tidak terjadi kebocoran evaluasi.

Untuk batch awal kecil, setiap record wajib memiliki field `split`. Jangan mengubah label test hanya agar hasil terlihat lebih baik. Jika aturan diubah setelah melihat hasil test, catat bahwa test set sudah menjadi data pengembangan dan buat test set baru untuk evaluasi berikutnya.

## 4. Format JSONL

Satu baris adalah satu kalimat berupa objek JSON. Simpan sebagai UTF-8 di:

`data/dataset_pos/kalimat_pos_v1.jsonl`

**Progres:** 20/100 kalimat telah dianotasi (12 development, 8 test; 91 token berdasarkan rancangan anotasi). Batch pertama 10 kalimat/43 token telah lolos validator di Termux. Batch kedua telah lolos validasi struktur/tokenizer di Termux pada 27 November 2026. Sampel ini belum cukup untuk menyimpulkan akurasi umum; kualitas label dan akurasi prediksi tetap perlu dievaluasi.

Skema record:

```json
{
  "id": "pos_0001",
  "split": "development",
  "text": "Aku sedang makan nasi.",
  "tokens": [
    {"token": "aku", "gold_pos": "PRON", "gold_status": "resolved"},
    {"token": "sedang", "gold_pos": "ADV", "gold_status": "resolved"},
    {"token": "makan", "gold_pos": "VERB", "gold_status": "resolved"},
    {"token": "nasi", "gold_pos": "NOUN", "gold_status": "resolved"},
    {"token": ".", "gold_pos": null, "gold_status": "not_applicable"}
  ],
  "phenomena": ["kalimat_sederhana", "aspek"],
  "notes": ""
}
```

### Field wajib

| Field | Aturan |
|---|---|
| `id` | ID unik dan stabil, format `pos_NNNN`. |
| `split` | Hanya `development` atau `test`. |
| `text` | Kalimat asli; jangan dinormalisasi atau diperbaiki diam-diam. |
| `tokens` | Daftar token sesuai urutan keluaran tokenizer proyek. |
| `token` | Bentuk token persis seperti keluaran `tokenize(text)`. Tokenizer melakukan casefold, sehingga token kata biasanya huruf kecil; tanda baca tetap dipertahankan. |
| `gold_pos` | Satu kode POS resmi atau `null` bila tidak ada label POS tunggal yang tepat. |
| `gold_status` | Salah satu status di bawah. |
| `phenomena` | Array tag cakupan fenomena; boleh kosong jika belum ditentukan. |
| `notes` | Catatan anotasi; string, boleh kosong. |

### Nilai `gold_status`

- `resolved`: fungsi token dalam kalimat cukup jelas; `gold_pos` wajib berisi satu kode resmi.
- `ambiguous`: konteks kalimat memang tidak cukup untuk menetapkan satu POS; `gold_pos` harus `null`.
- `unknown`: bentuk tidak dapat dianotasi dengan yakin berdasarkan pedoman dan sumber yang tersedia; `gold_pos` harus `null`. Jangan gunakan status ini hanya karena kata belum ada di kamus.
- `requires_morphology`: bentuk turunan perlu dianalisis lebih dahulu sebelum POS ditetapkan; `gold_pos` boleh `null` sampai analisis bentuk diselesaikan.
- `not_applicable`: tanda baca atau token non-kata; `gold_pos` harus `null`.

Gunakan hanya kode POS resmi dari `docs/KAMUS.md`: `NOUN`, `VERB`, `ADJ`, `ADV`, `PRON`, `NUM`, `PREP`, `CONJ`, `INTJ`, `PART`.

## 5. Aturan anotasi

1. Anotasi berdasarkan fungsi token di kalimat, bukan sekadar POS default lema.
2. Gunakan konteks kiri dan kanan yang cukup; jangan menetapkan POS hanya dari tebakan atau arti yang paling sering.
3. Pisahkan POS token dari sense/makna. Dataset versi pertama menguji POS; anotasi sense dapat menjadi tahap terpisah.
4. Jika dua analisis tetap sama-sama masuk akal dalam kalimat yang diberikan, gunakan `ambiguous`, bukan memaksakan label.
5. Untuk kata turunan, jangan menyalin POS lema secara otomatis. Periksa fungsi bentuk permukaan.
6. Pertahankan teks asli, slang, salah ketik, dan tanda baca. Catat fenomenanya; jangan membetulkan tanpa jejak.
7. Jika anotator ragu, isi `notes` dan tandai `unknown` atau `ambiguous` sesuai penyebabnya. Jangan mengarang kepastian.
8. Idealnya setiap label diperiksa ulang dengan pedoman dan entri kamus. Kasus yang diperselisihkan harus ditinjau sebelum dipakai untuk menghitung skor.

## 6. Validasi struktur dan konsistensi

Sebelum evaluasi, validator dataset harus memeriksa:

- Setiap baris adalah JSON valid dan objek.
- ID unik serta mengikuti pola yang ditetapkan.
- `split` hanya memiliki nilai yang diizinkan.
- `text` berupa string tidak kosong.
- Token dataset sama urutan dan ejaannya dengan keluaran `tokenize(text)`.
- Jumlah token anotasi sama dengan jumlah token tokenizer.
- Semua kode POS termasuk taksonomi resmi.
- Kombinasi `gold_status` dan `gold_pos` konsisten dengan aturan di atas.
- Tidak ada record identik atau ID ganda.

Jangan menghitung akurasi bila validasi struktur gagal.

## 7. Metrik evaluasi

Laporkan metrik secara terpisah; satu angka akurasi saja dapat menutupi kecenderungan sistem menebak atau terlalu sering menahan keputusan.

- **Accuracy pada token resolved:** prediksi POS tepat dibagi seluruh token gold berstatus `resolved` yang dapat dinilai.
- **Coverage:** token gold `resolved` yang diberi satu prediksi POS oleh sistem dibagi seluruh token gold `resolved`.
- **Selective accuracy:** prediksi benar dibagi token gold `resolved` yang benar-benar diputuskan sistem.
- **Ambiguity handling:** jumlah token gold `ambiguous` yang tetap tidak diputuskan, dan jumlah yang keliru dipaksa menjadi satu POS.
- **Unknown/morphology counts:** jumlah token yang tidak dikenal atau memerlukan analisis morfologi; laporkan terpisah, jangan diam-diam dikeluarkan dari ringkasan.
- **Confusion matrix:** untuk token resolved yang memiliki prediksi tunggal, rincikan label gold versus prediksi.

Sertakan jumlah token dan kalimat yang menjadi dasar setiap metrik. Jangan menyamakan token yang tidak diprediksi dengan prediksi benar.

## 8. Batasan prototipe saat ini

Aturan di `tools/pos_context.py` adalah heuristik lokal yang sangat terbatas: petunjuk aspek/modal, preposisi, demonstrativa, dan pola sederhana untuk kata `bisa`. Lulusnya regression tests membuktikan perilaku pada kasus uji tersebut, bukan akurasi umum pada Bahasa Indonesia.

Dataset harus membantu menemukan kasus yang belum ditangani. Jangan menambah aturan baru hanya untuk membuat satu contoh test lolos; cari pola yang dapat dijelaskan dan tambahkan kasus positif serta negatif.

## 9. Urutan kerja

- [x] Menetapkan rancangan format dan pedoman anotasi versi 1.0.
- [x] Menyusun batch pertama 10 kalimat berlabel (6 development, 4 test).
- [x] Menambahkan batch kedua 10 kalimat (6 development, 4 test); total rancangan 20 kalimat/91 token.
- [x] Memvalidasi batch kedua di checkout Termux: 20 kalimat dan 91 token (12 development, 8 test), seluruh pemeriksaan lulus (27 November 2026).
- [ ] Memperluas dataset secara bertahap hingga target 100 kalimat.
- [x] Membuat `tools/validasi_dataset_pos.py` untuk memeriksa struktur JSONL, label, status, ID, dan kecocokan token dengan tokenizer.
- [x] Membuat 9 regression tests pada `tests/test_validasi_dataset_pos.py`.
- [x] Menjalankan `python -m tools.validasi_dataset_pos` dari checkout Termux untuk batch pertama: 10 kalimat dan 43 token tervalidasi (6 development, 4 test).
- [x] Menjalankan ulang validator setelah batch kedua: 20 kalimat dan 91 token (12 development, 8 test), berhasil (27 November 2026).
- [x] Menjalankan 9 regression tests validator dari checkout Termux: 9 lulus, 0 gagal (27 November 2026).
- [ ] Mengevaluasi development set dan mencatat kesalahan.
- [ ] Mengunci test set dan mengukur metrik tanpa penyetelan khusus terhadap test.
- [x] Memperbarui dokumentasi status dan checklist berdasarkan hasil verifikasi Termux.

**Titik lanjut:** dataset 20/100 kalimat telah lolos validasi struktur/tokenizer dan regression suite penuh terbaru 132/132 lulus di Termux (27 November 2026). Berikutnya audit kualitas anotasi dan perluas dataset menuju 100 kalimat. Evaluasi development set dilakukan setelah audit; test split tetap ditahan.
