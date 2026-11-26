# Rancangan Dataset Berlabel untuk Evaluasi POS

**Status:** Batch keempat telah ditambahkan: 40 kalimat (24 development, 16 test; 215 token berdasarkan anotasi). Dataset batch keempat belum divalidasi di Termux; hasil evaluasi sebelumnya hanya mencakup 18 kalimat development sebelum batch ini.
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

**Progres:** 40/100 kalimat telah dianotasi (24 development, 16 test; 215 token terverifikasi validator Termux). Batch keempat lolos validasi struktur/tokenizer dan regression suite penuh 137/137. Evaluasi POS terakhir pada 24 kalimat development: 102 token resolved, 55 prediksi benar, coverage 54,9%, accuracy 53,9%, selective accuracy 98,2%. Hasil terbatas pada development set.

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

### 5.1 Konvensi operasional untuk kasus khusus

Karena taksonomi proyek hanya menyediakan 10 kode POS dan tidak memiliki kelas determinator (DET) atau aspek tersendiri, gunakan konvensi berikut secara konsisten pada dataset versi 1:

| Fenomena | Konvensi proyek | Contoh dan batasan |
|---|---|---|
| Demonstrativa atributif | `PRON` | `itu` pada “rumah itu” dan `ini` pada “buku ini” diberi `PRON`. Ini penyederhanaan taksonomi proyek; jangan membuat label DET baru pada dataset v1. |
| Penanda aspek/modalitas yang ditetapkan v1 | `ADV` | `sedang`, `akan`, `telah`, `sudah`, dan `lagi` diberi `ADV` ketika berfungsi sebagai penanda aspek/modalitas sebelum verba. Daftar ini adalah konvensi terbatas, bukan aturan bahwa semua kata bermakna modalitas otomatis `ADV`. |
| Verba modal kehendak | `VERB` | `mau` pada “Gue mau makan dulu” diberi `VERB`: kata ini menyatakan kehendak dan berfungsi sebagai verba modal yang mengambil komplemen verba. Jangan samakan semua bentuk modalitas ke satu POS. |
| Penanda larangan | `PART` | `jangan` diberi `PART` ketika menandai larangan dalam konstruksi imperatif, misalnya “Jangan pergi!”. |
| Gelar atau sapaan nominal | `NOUN` | `Pak`, `Bu`, dan gelar sejenis diberi `NOUN` ketika dipakai sebagai sapaan/gelar yang mendahului nama atau nomina. |
| Kata sebab | `CONJ` | `karena` diberi `CONJ` ketika menghubungkan klausa sebab dengan klausa lain. |
| Penanda tanya | `PART` | `-kah` dan bentuk seperti `apakah` diberi `PART` sesuai struktur leksikal/proyek; jangan memecah token jika tokenizer tidak memecahnya. |

Konvensi ini adalah keputusan anotasi internal agar label konsisten, bukan klaim bahwa semua tata bahasa atau skema linguistik memakai pemetaan yang sama. Jika satu bentuk menjalankan fungsi berbeda dalam kalimat lain, anotasi tetap mengikuti fungsi kontekstualnya. Catat kasus yang tidak tercakup dalam `notes` dan ajukan untuk audit, jangan memperluas aturan secara otomatis.

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
- [x] Menambahkan batch ketiga 10 kalimat (6 development, 4 test); total 30 kalimat/156 token (27 November 2026).\n- [x] Memvalidasi batch ketiga di checkout Termux: 30 kalimat, 156 token, 18 development, 12 test; seluruh pemeriksaan lulus di Termux (27 November 2026).\n- [ ] Memperluas dataset secara bertahap hingga target 100 kalimat.
- [x] Membuat `tools/validasi_dataset_pos.py` untuk memeriksa struktur JSONL, label, status, ID, dan kecocokan token dengan tokenizer.
- [x] Membuat 9 regression tests pada `tests/test_validasi_dataset_pos.py`.
- [x] Menjalankan `python -m tools.validasi_dataset_pos` dari checkout Termux untuk batch pertama: 10 kalimat dan 43 token tervalidasi (6 development, 4 test).
- [x] Menjalankan ulang validator setelah batch kedua: 20 kalimat dan 91 token (12 development, 8 test), berhasil (27 November 2026).
- [x] Menjalankan 9 regression tests validator dari checkout Termux: 9 lulus, 0 gagal (27 November 2026).
- [ ] Mengevaluasi development set dan mencatat kesalahan.
- [ ] Mengunci test set dan mengukur metrik tanpa penyetelan khusus terhadap test.
- [x] Memperbarui dokumentasi status dan checklist berdasarkan hasil verifikasi Termux.

**Titik lanjut:** batch ketiga telah lolos validasi struktur/tokenizer di Termux: 30 kalimat/156 token (18 development, 12 test). Regression suite setelah batch ketiga: 132/132 lulus. Audit awal development telah dicatat; berikutnya terapkan konvensi operasional pada subbagian 5.1 dan audit ulang development set. Test split tetap ditahan.


## 10. Audit awal kualitas anotasi — 27 November 2026

- Audit awal telah dilakukan pada seluruh 18 kalimat development; split test tidak diperiksa.
- Hasil audit dan kasus yang memerlukan konvensi taksonomi eksplisit dicatat dalam [`AUDIT_ANOTASI_POS.md`](AUDIT_ANOTASI_POS.md).
- Belum ada label gold yang diubah. Kasus demonstrativa `itu`, penanda aspek `sedang`, larangan `jangan`, dan gelar `Pak` dipertahankan sementara sambil pedoman diperjelas.
- Validasi dataset: 30 kalimat, 156 token, 18 development, 12 test — lulus di Termux.
- Regression suite setelah batch ketiga: 132/132 lulus di Termux.

**Titik lanjut:** pertegas konvensi anotasi di pedoman, lalu audit ulang development set. Test split tetap ditahan.


**Pembaruan pedoman 27 November 2026:** subbagian 5.1 menetapkan konvensi operasional untuk demonstrativa atributif (`PRON`), penanda aspek/modalitas (`ADV`), penanda larangan (`PART`), gelar/sapaan nominal (`NOUN`), kata sebab (`CONJ`), dan penanda tanya (`PART`). Konvensi ini berlaku untuk konsistensi anotasi dataset v1 dan tidak menambah kode POS baru.


## 11. Evaluator development — 27 November 2026

File `tools/evaluasi_pos.py` membandingkan prediksi POS leksikal dan kontekstual terhadap gold label pada split development saja. Evaluator melaporkan coverage, accuracy terhadap seluruh token resolved, selective accuracy, confusion counts, dan penanganan token gold ambiguous. Record test tidak dimuat oleh CLI dan fungsi evaluasi menolak record yang bukan development.

Empat regression tests di `tests/test_evaluasi_pos.py` telah dijalankan dari Termux: **4/4 lulus**. Evaluasi pada 18 kalimat development menghasilkan 72 token resolved. POS leksikal dan POS kontekstual sama-sama mencatat 42 prediksi benar, coverage 58,3%, accuracy 58,3%, dan selective accuracy 100%. Hasil ini hanya berlaku untuk sampel development kecil, bukan akurasi umum.

Perintah:
```bash
python -m unittest discover -s tests -p "test_evaluasi_pos.py" -v
python -m tools.evaluasi_pos
python -m unittest discover -s tests -v
```

Hasil evaluasi hanya menggambarkan sampel development yang tersedia (saat ini 18 kalimat). Jangan gunakan test split untuk menyetel aturan.


### 11.1 Temuan audit pertama setelah evaluasi

Evaluator menemukan 1 token gold berstatus `ambiguous`, yaitu `jalan` pada record `pos_0006` (“Jalan.”), tetapi sistem memaksakan satu POS (`forced: 1`, `abstained: 0`). Karena fragmen tersebut memang tidak memberi konteks untuk memilih antara NOUN dan VERB, perilaku ini perlu diperiksa.

Langkah audit berikutnya:
1. Periksa seluruh kandidat POS lema `jalan` dalam kamus dan apakah metadata entri/sense mempertahankan NOUN serta VERB.
2. Telusuri mengapa `tools/pos_context.py` memberi keputusan tunggal pada token tersebut.
3. Tambahkan regression test agar contoh ambigu tanpa konteks tidak dipaksa menjadi satu POS ketika kandidat leksikal memang jamak.
4. Jangan mengubah split test atau memakai hasil test untuk menyetel aturan.

Catatan hasil eksekusi: regression suite penuh dari Termux menjalankan **136 tes dan seluruhnya lulus** pada 27 November 2026. Evaluasi development menunjukkan POS kontekstual belum meningkatkan metrik dibanding POS leksikal pada sampel yang tersedia.


### 11.2 Koreksi metadata lema "jalan"

Audit hasil evaluasi menemukan bahwa entri `K0020` mencatat `jalan` hanya sebagai `NOUN`, padahal catatan penggunaan sebelumnya sudah menyebut fungsi verba. Metadata diperbaiki menjadi `NOUN` dan `VERB` dengan dua sense terpisah dan label POS pada masing-masing sense. Fragmen "Jalan." pada development kini seharusnya tetap ambigu karena tidak menyediakan konteks pemilih.

Regression test integrasi ditambahkan untuk memastikan token gold ambiguous tersebut ditahan, bukan dipaksakan. Perubahan dan tes masih menunggu verifikasi Termux. Split test tidak disentuh.


## 12. Verifikasi batch keempat dan evaluasi development — 27 November 2026

Batch keempat (`pos_0031`–`pos_0040`) telah ditarik dan diverifikasi dari Termux. Validator melaporkan **40 kalimat, 215 token, 24 development, 16 test** dan berhasil memeriksa JSONL, ID, split, label/status POS, serta kecocokan token dengan tokenizer. Regression suite penuh: **137 tes lulus, 0 gagal, 0 error**.

Evaluasi hanya menggunakan 24 kalimat development (102 token `resolved`, 1 `ambiguous`, 29 `not_applicable`):
- POS leksikal: 56 diprediksi, 55 benar; coverage **54,9%**, accuracy **53,9%**, selective accuracy **98,2%**.
- POS dengan konteks lokal: hasil identik.
- Gold ambiguous: **1 ditahan, 0 dipaksakan**.
- Audit menetapkan `mau` pada `Gue mau makan dulu` sebagai `VERB` (verba modal kehendak), selaras dengan entri kamus `K0024`. Label dataset dikoreksi dari `ADV` menjadi `VERB`; tidak ada perubahan kamus atau aturan program. Setelah koreksi, metrik perlu dihitung ulang di Termux. `wah` berlabel `INTJ` belum mendapat prediksi; ini merupakan abstention, bukan prediksi salah.

Interpretasi: penambahan batch menurunkan metrik dibanding sampel sebelumnya, tetapi sampel development juga bertambah dan mencakup fenomena baru. Jangan membandingkan angka sebagai tren kualitas tanpa mempertimbangkan perubahan komposisi. POS kontekstual belum menunjukkan peningkatan dibanding leksikal. Test split 16 kalimat tetap tertahan dan tidak digunakan.


## 5.2 Cakupan interjeksi (INTJ)

Kata `aduh` pada `pos_0041` diberi `INTJ` dan memiliki entri kamus `K0602`. Kata `wah` pada `pos_0034` tetap diberi gold `INTJ`, tetapi belum ditemukan pada indeks kamus saat audit 27 November 2026; ini dicatat sebagai kekurangan cakupan leksikal, bukan alasan untuk mengubah label gold atau menambah aturan POS. Jangan mengubah `wah` menjadi kelas lain demi menyesuaikan prediksi. Penambahan kosakata interjeksi dapat dipertimbangkan dalam pengembangan kamus berikutnya setelah evaluasi cakupan.


## 12. Batch kelima — 27 November 2026

Batch kelima menambahkan `pos_0041`–`pos_0050`: enam kalimat development dan empat test. Dataset menjadi 50 kalimat, 266 token, 30 development, dan 20 test. Pemeriksaan struktural berbasis salinan file GitHub memastikan seluruh baris JSON dapat dibaca, ID unik, label/status POS valid, dan urutan token sesuai pola tokenizer. Setelah workflow GitHub Actions ditambahkan, eksekusi resmi berhasil pada run [#1](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45906966948): validator Python lulus, evaluator development selesai, dan regression suite 137/137 lulus. Evaluasi memakai 30 kalimat development (125 token resolved); leksikal dan kontekstual sama-sama 72 benar, coverage 57,6%, accuracy 57,6%, selective accuracy 100%. Gold ambiguous: 1 ditahan, 0 dipaksakan. Split test tidak digunakan.


## 13. Batch keenam — 27 November 2026

Batch keenam menambahkan `pos_0051`–`pos_0060`: enam kalimat development dan empat test. Dataset menjadi 60 kalimat, 314 token, 36 development, dan 24 test. Cakupan tambahan meliputi negasi, verba berimbuhan, preposisi tujuan dan asal, konjungsi sebab, demonstrativa, serta adjektiva predikatif. Preflight struktural sebelum commit memeriksa JSON, ID, split, label/status POS, dan kecocokan token dengan pola tokenizer. Menunggu eksekusi workflow GitHub Actions untuk validasi Python, evaluasi development, dan regression suite. Test split tetap ditahan.


### Verifikasi otomatis batch keenam

GitHub Actions run [#2](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45907643287) berhasil menjalankan validator Python, evaluator development-only, dan regression suite. Validator: **60 kalimat, 314 token, 36 development, 24 test**. Evaluator memuat 36 kalimat development, 148 token resolved, 90 prediksi benar, coverage 60,8%, accuracy 60,8%, selective accuracy 100%; gold ambiguous 1 ditahan dan 0 dipaksakan. Regression suite: **137/137 lulus**. Angka ini hanya untuk development set dan tidak mewakili akurasi umum; test split 24 kalimat tetap tidak digunakan.


## 14. Suplementasi POS terfokus — 27 November 2026

Untuk menangani gap kosakata yang ditemukan pada development set, proyek menambahkan fallback terpisah dari kamus inti melalui `tools/pos_supplement.py`. Fallback ini bukan entri kamus dan tidak mengubah jumlah 3.000 lema. Daftar awal dibatasi pada 12 bentuk yang didukung contoh development dan konvensi POS v1: `dua`, `tiga` (NUM); `di`, `ke`, `pada` (PREP); `atau`, `kalau`, `tetapi` (CONJ); `akan`, `sedang`, `sangat`, `sekali` (ADV).

Aturan integrasi:
1. Kandidat dari kamus selalu diprioritaskan.
2. Fallback hanya digunakan jika token kata tidak memiliki kandidat kamus.
3. Bentuk turunan yang ditandai `requires_morphology` tidak diberi POS melalui fallback.
4. Kata yang berpotensi memiliki fungsi berbeda tidak dimasukkan hanya demi menaikkan coverage; `dulu` dan `tetap` tetap di luar daftar awal.
5. Sumber keputusan dicatat melalui `pos_source` (`dictionary`, `supplement`, `unknown`, atau status terkait).

Verifikasi GitHub Actions run [#5](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908285217): validator 60 kalimat/314 token; evaluasi development 148 token resolved, 107 benar, coverage 72,3%, accuracy 72,3%, selective accuracy 100%; regression suite 141/141 lulus. Satu gold ambiguous tetap ditahan dan tidak dipaksakan. Test split 24 kalimat tidak digunakan.

Angka coverage 72,3% adalah hasil pada 36 kalimat development yang tersedia, bukan akurasi umum. POS kontekstual belum menambah metrik di atas POS leksikal.


## 15. Batch ketujuh dan verifikasi — 27 November 2026

Batch ketujuh menambahkan 10 record (`pos_0061`–`pos_0070`), enam development dan empat test. Dataset menjadi 70 kalimat, 374 token, 42 development dan 28 test. Cakupan development meliputi numeralia, preposisi tujuan, konjungsi pilihan/subordinatif, penanda aspek/modalitas, demonstrativa, dan adverbia derajat.

GitHub Actions run [#6](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908531211) memvalidasi dataset: 70 kalimat, 374 token, 42 development, 28 test. Evaluator development-only memuat 174 token resolved, 131 benar, coverage 75,3%, accuracy 75,3%, selective accuracy 100%; satu gold ambiguous ditahan dan nol dipaksakan. Regression suite: 141/141 lulus. Test split tetap tertahan dan tidak digunakan.

Angka evaluasi hanya berlaku untuk development set yang berisi 42 kalimat; bukan estimasi akurasi umum. Jangan menganggap perubahan persentase antarbatch sebagai tren kualitas tanpa memperhatikan komposisi sampel.


## 16. Batch kedelapan dan verifikasi — 27 November 2026

Batch kedelapan menambahkan 10 record (`pos_0071`–`pos_0080`), enam development dan empat test. Dataset menjadi 80 kalimat, 428 token, 48 development dan 32 test. Cakupan development meliputi numeralia atributif, preposisi lokatif/tujuan, konjungsi pertentangan, penanda aspek, demonstrativa, nomina berimbuhan, dan adverbia derajat.

GitHub Actions run [#7](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908957782) memvalidasi dataset: 80 kalimat, 428 token, 48 development, 32 test. Evaluator development-only memuat 199 token resolved, 149 benar, coverage 74,9%, accuracy 74,9%, selective accuracy 100%; satu gold ambiguous ditahan dan nol dipaksakan. Regression suite: 141/141 lulus. Test split tetap tertahan dan tidak digunakan.

Angka evaluasi hanya berlaku untuk development set 48 kalimat. Perubahan persentase antarbatch tidak boleh langsung ditafsirkan sebagai tren kualitas tanpa memperhatikan komposisi sampel.


## 17. Batch kesembilan dan verifikasi — 27 November 2026

Batch kesembilan menambahkan 10 record (`pos_0081`–`pos_0090`), enam development dan empat test. Dataset menjadi 90 kalimat, 485 token, 54 development dan 36 test. Cakupan development meliputi negasi, verba transitif, nomina/verba berimbuhan, interjeksi, adjektiva atributif/predikatif, numeralia, preposisi lokatif/tujuan, dan konjungsi penambahan.

GitHub Actions run [#8](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909135531) memvalidasi dataset: 90 kalimat, 485 token, 54 development, 36 test. Evaluator development-only memuat 227 token resolved, 167 benar, coverage 73,6%, accuracy 73,6%, selective accuracy 100%; satu gold ambiguous ditahan dan nol dipaksakan. Regression suite: 141/141 lulus. Test split tetap tertahan dan tidak digunakan.

Angka evaluasi hanya berlaku untuk development set 54 kalimat; bukan estimasi akurasi umum. Perubahan persentase antarbatch tidak boleh langsung ditafsirkan sebagai tren kualitas tanpa memperhatikan komposisi sampel.


## 18. Batch kesepuluh dan pencapaian target dataset v1 — 27 November 2026

Batch kesepuluh menambahkan 10 record (`pos_0091`–`pos_0100`), enam development dan empat test. Dataset mencapai **100 kalimat, 543 token, 60 development, dan 40 test**. Fenomena development meliputi adverbia aspek/negasi, adjektiva atributif, adverbia derajat, konjungsi penambahan/subordinatif waktu, verba berimbuhan/transitif, serta preposisi lokatif/peruntukan.

GitHub Actions run [#9](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45909322818) memvalidasi dataset: 100 kalimat, 543 token, 60 development, 40 test. Evaluator development-only melaporkan 255 token resolved, 186 benar, coverage 73,3%, accuracy 72,9%, selective accuracy 99,5%; satu gold ambiguous ditahan dan nol dipaksakan. Regression suite: **141/141 lulus**.

Selective accuracy 99,5% menunjukkan masih ada prediksi keliru pada token yang diputuskan sistem. Pencapaian target 100 kalimat adalah pencapaian kuantitas dataset, bukan klaim bahwa POS sudah sempurna. Empat puluh kalimat test tetap tertahan dan tidak boleh digunakan untuk penyetelan aturan.
