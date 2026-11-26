# Audit Awal Kualitas Anotasi POS — Development

**Status:** Audit awal selesai; belum ada perubahan pada label dataset.  
**Dataset yang diperiksa:** `data/dataset_pos/kalimat_pos_v1.jsonl`  
**Cakupan:** 18 kalimat development. Split test tidak diperiksa dan tetap ditahan.

## 1. Tujuan dan batasan

Audit ini menilai kewajaran label berdasarkan fungsi kata dalam kalimat, bukan hanya validitas JSONL atau kecocokan tokenizer. Audit ini merupakan pemeriksaan awal oleh satu peninjau, bukan adjudikasi multi-anotator atau bukti akurasi model.

Tidak ada label yang diubah dalam audit awal ini. Kasus yang bergantung pada pedoman taksonomi proyek ditandai untuk klarifikasi sebelum dataset dipakai menghitung skor.

## 2. Hasil ringkas

- Seluruh 18 kalimat development ditinjau.
- Tidak ditemukan kesalahan label yang cukup pasti untuk langsung dikoreksi tanpa memperjelas pedoman.
- Beberapa kelas kata memerlukan aturan anotasi yang eksplisit agar konsisten: demonstrativa `ini/itu`, penanda aspek `sedang/akan/sudah`, larangan `jangan`, dan gelar sapaan `Pak`.
- Status `ambiguous` pada fragmen `Jalan.` dipertahankan karena konteks tidak cukup menentukan fungsi nomina atau verba.
- Split test tidak disentuh.

## 3. Kasus yang perlu pedoman eksplisit

| Kasus | Label sekarang | Catatan audit | Tindakan |
|---|---|---|---|
| `itu` pada “Rumah itu besar” dan “Burung kecil itu terbang” | `PRON` | Berfungsi sebagai demonstrativa/penentu nomina. Taksonomi proyek tidak memiliki kelas `DET`; perlu aturan konsisten apakah demonstrativa atributif dimasukkan ke `PRON`. | Pertahankan sementara; tetapkan konvensi di pedoman. |
| `sedang` pada “Aku sedang makan nasi” | `ADV` | Penanda aspek/progresif. Sebagian skema dapat memisahkannya sebagai partikel/aspek, tetapi taksonomi proyek tidak menyediakan kelas aspek tersendiri. | `ADV` dapat dipakai sebagai konvensi proyek; dokumentasikan. |
| `jangan` pada “Jangan letakkan tas di lantai!” | `ADV` | Penanda larangan/negasi imperatif. Klasifikasi dapat berbeda antar-pedoman (misalnya partikel atau adverbia). | Tinjau terhadap entri kamus dan tetapkan satu konvensi. |
| `Pak` pada “Pak guru sedang menjelaskan pelajaran” | `NOUN` | Gelar/sapaan yang mendahului nomina. Label `NOUN` masuk akal pada taksonomi ringkas, tetapi perlu konsistensi untuk gelar lain. | Pertahankan sementara; dokumentasikan aturan gelar. |
| `karena` pada “Karena hujan deras, pertandingan ditunda” | `CONJ` | Menghubungkan klausa sebab dengan klausa utama; label sesuai fungsi subordinatif dalam kalimat ini. | Tidak perlu perubahan. |

## 4. Pemeriksaan lain

- Pronomina seperti `aku`, `kamu`, `dia`, `mereka`, dan `kami` diberi `PRON` secara konsisten.
- Kata kerja berimbuhan seperti `bekerja`, `membaca`, `memasak`, `mengejar`, `ditunda`, dan `menjelaskan` diberi `VERB` sesuai fungsi kalimat.
- Numeralia `tiga` diberi `NUM`; nomina dan adjektiva pada frasa seperti “buku baru” dan “tikus kecil” konsisten dengan fungsi sintaksisnya.
- Tanda baca diberi `not_applicable` dan `gold_pos: null`.
- `Jalan.` tetap `ambiguous`; jangan dipaksa menjadi satu kelas kata tanpa konteks tambahan.

## 5. Keputusan dan tindak lanjut pedoman

1. Jangan mengubah label dataset hanya berdasarkan perbedaan istilah antar-skema POS.
2. Konvensi operasional untuk demonstrativa, aspek/modalitas, larangan, gelar/sapaan, kata sebab, dan penanda tanya telah ditetapkan dalam subbagian 5.1 `docs/DATASET_POS.md`.
3. Audit ulang seluruh development set menggunakan pedoman tersebut; koreksi label hanya jika fungsi token jelas tidak sesuai konvensi.
4. Jangan membuka atau menggunakan split test untuk menyetel aturan.
5. Jalankan kembali validator dataset dan seluruh regression tests setelah ada perubahan data atau kode.

## 6. Titik lanjut

Konvensi operasional telah ditambahkan ke `docs/DATASET_POS.md` tanpa menambah kode POS baru. Langkah berikutnya adalah menarik pembaruan, audit ulang development set menurut pedoman tersebut, lalu baru memutuskan apakah label perlu dikoreksi. Split test tetap ditahan.


## 7. Pembaruan pedoman — 27 November 2026

Pedoman operasional ditetapkan di `docs/DATASET_POS.md` subbagian 5.1: demonstrativa atributif `PRON`; penanda aspek/modalitas `ADV`; penanda larangan `PART`; gelar/sapaan nominal `NOUN`; kata sebab `CONJ`; penanda tanya `PART`. Pemetaan ini merupakan konvensi internal dataset v1. Belum ada label pada JSONL yang diubah. Audit ulang development masih harus dilakukan setelah pedoman ditarik ke checkout lokal.


## 8. Audit ulang development setelah pedoman ditetapkan — 27 November 2026

Seluruh 18 kalimat development diperiksa ulang terhadap konvensi operasional pada subbagian 5.1 `docs/DATASET_POS.md`. Split test tetap ditahan dan tidak digunakan dalam audit ini.

- Demonstrativa atributif `itu` pada contoh development tetap `PRON`, sesuai konvensi proyek.
- Penanda aspek/modalitas `sedang` dan `akan` tetap `ADV`.
- Gelar/sapaan `Pak` tetap `NOUN`.
- Penghubung sebab `karena` tetap `CONJ`.
- Penanda larangan `jangan` pada `Jangan letakkan tas di lantai!` dikoreksi dari `ADV` menjadi `PART`, sesuai konvensi yang telah dipilih. Catatan record juga menjelaskan alasan label.
- Fragmen `Jalan.` tetap `ambiguous` karena konteksnya tidak cukup.

**Hasil:** satu koreksi label gold pada record `pos_0024`; tidak ada perubahan pada record test. Audit ini adalah pemeriksaan konsistensi internal oleh satu peninjau, bukan adjudikasi multi-anotator atau bukti akurasi prediksi POS.

**Verifikasi berikutnya:** tarik perubahan ke Termux, jalankan validator dataset dan seluruh regression tests. Hasil eksekusi setelah perubahan ini masih menunggu pengguna.


## Audit metadata POS — lema "jalan" (27 November 2026)

**Temuan:** evaluator development sebelumnya menunjukkan token `jalan` pada `pos_0006` (fragmen "Jalan.") dipaksakan menjadi satu POS. Pemeriksaan entri `K0020` di `data/kamus/batch-001.jsonl` menemukan bahwa catatan penggunaan menyebut fungsi verba, tetapi metadata hanya mencantumkan `NOUN`.

**Koreksi metadata:**
- POS entri menjadi `["NOUN", "VERB"]`.
- Sense `K0020-S1` menyatakan makna jalur/tempat yang dilalui dan diberi POS `NOUN`.
- Sense `K0020-S2` menyatakan makna bergerak/melangkah dengan kaki dan diberi POS `VERB`.
- Catatan penggunaan menegaskan bahwa fungsi ditentukan oleh konteks dan fragmen tanpa konteks dapat ambigu.

**Pengamanan:** ditambahkan regression test integrasi yang memuat kamus dan development dataset sebenarnya, lalu memastikan satu token gold ambiguous `jalan` ditahan (abstained) dan tidak dipaksakan.

Perubahan ini hanya memperbaiki metadata entri dan tes. Tidak ada aturan konteks yang dilonggarkan, tidak ada data test yang dipakai, dan token index tidak berubah karena lemma serta token indeks tetap sama. Hasil akhir tetap menunggu verifikasi di Termux.


## Verifikasi setelah koreksi metadata lema "jalan" — 27 November 2026

Pengguna menjalankan perintah verifikasi dari checkout Termux setelah menarik pembaruan:

- 5 tes evaluator POS lulus, 0 gagal.
- Evaluator memuat 18 kalimat development; split test tidak digunakan.
- Gold ambiguous pada `pos_0006` (`Jalan.`) kini ditahan: **1 abstained, 0 forced**.
- Metrik token resolved tetap 42 prediksi benar dari 72; coverage 58,3%, accuracy 58,3%, selective accuracy 100% untuk token yang diprediksi.
- POS leksikal dan POS dengan konteks lokal menghasilkan metrik identik pada sampel ini.
- Regression suite penuh: **137 tes lulus, 0 gagal, 0 error**.

Koreksi metadata berhasil memperbaiki penanganan kasus ambigu yang ditemukan. Hasil ini tidak membuktikan akurasi umum; cakupan evaluasi masih 18 kalimat development. Test split tetap ditahan.


## Audit setelah batch keempat — 27 November 2026

Evaluasi development setelah batch keempat menemukan mismatch pada `pos_0031`: kalimat `Gue mau makan dulu.`. Kamus `K0024` menetapkan `mau` sebagai `VERB`, sedangkan gold awal memberi `ADV`. Audit fungsi kalimat menetapkan `mau` sebagai verba modal kehendak yang mengambil komplemen verba `makan`. Karena itu gold dikoreksi menjadi `VERB`. Konvensi `ADV` untuk `sedang`, `akan`, `telah`, `sudah`, dan `lagi` tetap terbatas pada daftar yang ditetapkan; tidak semua ungkapan modalitas otomatis `ADV`. Tidak ada perubahan kamus maupun aturan program.

Token `wah` pada kalimat development baru berlabel `INTJ` tetapi tidak mendapat prediksi tunggal. Ini menurunkan coverage, bukan selective accuracy. Evaluasi menunjukkan leksikal dan konteks lokal sama-sama 55/102 benar, coverage 54,9%, accuracy 53,9%, selective accuracy 98,2%. Gold ambiguous `Jalan.` tetap ditahan (1 abstained, 0 forced).

Validasi dataset 40 kalimat/215 token dan regression suite penuh 137/137 telah berhasil sebelum koreksi label `mau`. Koreksi hanya menyentuh satu token development; validasi, evaluasi, dan regression suite harus dijalankan ulang dari Termux sebelum dinyatakan terverifikasi. Split test tidak diubah dan tidak digunakan untuk penyetelan.


## Audit cakupan interjeksi — 27 November 2026

Kasus `wah` pada `pos_0034` tidak mendapat prediksi tunggal. Pemeriksaan indeks kamus tidak menemukan lemma `wah`, sehingga penyebab yang paling mungkin adalah kata tersebut belum tercakup dalam kamus. Sebaliknya, lemma `aduh` ditemukan sebagai entri `K0602` dengan POS `INTJ`. Batch kelima menambahkan `Aduh, anak itu jatuh!` (`pos_0041`) pada development untuk menguji interjeksi yang memang sudah tersedia. Tidak ada perubahan pada `pos_tagger.py`, `pos_context.py`, atau entri kamus. Split test tetap ditahan.


## Verifikasi batch kelima dan cakupan INTJ — 27 November 2026

GitHub Actions run [#1](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45906966948) menjalankan validator, evaluator development-only, dan regression suite dengan hasil sukses. Evaluator memuat 30 kalimat development: 125 token `resolved`, 1 `ambiguous`, dan 36 `not_applicable`. INTJ: `aduh` berhasil diprediksi benar (1), sedangkan `wah` tidak diprediksi (1), konsisten dengan temuan bahwa `wah` belum ada pada indeks kamus. POS leksikal dan kontekstual sama-sama menghasilkan 72 prediksi benar, coverage 57,6%, accuracy 57,6%, selective accuracy 100%. Gold ambiguous: 1 ditahan, 0 dipaksakan. Regression suite: 137/137 lulus. Angka ini khusus sampel development 30 kalimat; bukan akurasi umum. Test split 20 kalimat tetap tidak digunakan.


## Audit anotasi batch keenam — 27 November 2026

Record `pos_0051`–`pos_0060` dianotasi mengikuti konvensi POS v1 yang telah ditetapkan: `tidak` sebagai ADV, `untuk` dan `dari` sebagai PREP, `karena` sebagai CONJ, dan `jangan` sebagai PART. Bentuk `membeli`, `bekerja`, `membaca`, `memasak`, dan `membawa` diberi VERB. Kalimat test baru hanya ditambahkan sebagai data tertahan dan tidak digunakan untuk menyesuaikan aturan. Preflight struktur dilakukan sebelum commit; validasi Python dan evaluasi setelah commit menunggu workflow otomatis.


## Hasil evaluasi batch keenam — 27 November 2026

GitHub Actions run [#2](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45907643287) berhasil. Evaluasi development-only mencakup 36 kalimat: 148 token resolved, 90 diprediksi benar, coverage 60,8%, accuracy 60,8%, selective accuracy 100%. Per label, prediksi yang benar/abstain: ADJ 14/1; ADV 4/9; CONJ 3/3; INTJ 1/1; NOUN 36/11; NUM 0/2; PART 1/0; PREP 1/6; PRON 14/9; VERB 16/16. POS leksikal dan kontekstual menghasilkan angka identik. Gold ambiguous: 1 ditahan, 0 dipaksakan. Regression suite 137/137 lulus. Coverage NUM masih 0/2 dan PREP 1/7; ADV 4/13. Ini menunjukkan area cakupan untuk audit berikutnya, bukan alasan langsung mengubah aturan. Test split tidak digunakan.


## Audit cakupan indeks leksikal terhadap development — 27 November 2026

Pemeriksaan dilakukan pada token berstatus `resolved` dari 36 kalimat development dan dibandingkan dengan seluruh delapan shard indeks kamus. Daftar berikut adalah bentuk kata yang belum ditemukan pada indeks; ini mengidentifikasi kandidat gap cakupan, bukan otomatis membuktikan bahwa seluruhnya harus ditambahkan ke kamus.

| Gold POS | Bentuk yang belum ditemukan pada indeks |
|---|---|
| ADV | `akan`, `dulu`, `sangat`, `sedang`, `sekali`, `tetap` |
| PRON | `itu` |
| PREP | `di`, `ke`, `pada` |
| CONJ | `atau`, `kalau`, `tetapi` |
| ADJ | `baru` |
| NUM | `dua`, `tiga` |
| NOUN | `dodi`, `kilogram`, `padi`, `pagar`, `pak`, `pelajaran`, `pemandangan`, `pertandingan`, `rina`, `siswa`, `tikus` |
| VERB | `ditunda`, `hinggap`, `letakkan`, `menanam`, `mengejar`, `menjelaskan` |
| INTJ | `wah` |

Temuan paling relevan untuk cakupan kelas kata tertutup: dua contoh `NUM` (`dua`, `tiga`) tidak memiliki entri indeks; tiga preposisi (`di`, `ke`, `pada`) dan tiga konjungsi (`atau`, `kalau`, `tetapi`) juga belum terindeks. Entri `untuk` dan `dari` sudah ada dan POS kamusnya `PREP`. Kata `itu` belum terindeks tetapi dipertahankan sebagai `PRON` sesuai konvensi dataset v1. Jangan mengubah gold hanya agar cocok dengan prediksi. Langkah lanjutan adalah merancang suplementasi kosakata terfokus atau aturan closed-class yang dapat diuji; jangan mengubah 3.000 entri secara massal.


## Suplementasi POS terfokus dan evaluasi ulang — 27 November 2026

Audit gap indeks mendorong fallback kecil di luar kamus inti, bukan perubahan massal pada 3.000 lema. Implementasi berada di `tools/pos_supplement.py` dan dipanggil oleh `tools/pos_tagger.py` hanya ketika token tidak memiliki kandidat dari kamus. Kandidat kamus selalu menang; bentuk turunan yang memerlukan morfologi tetap tidak diberi POS otomatis.

Daftar awal berisi 12 bentuk:
- NUM: `dua`, `tiga`.
- PREP: `di`, `ke`, `pada`.
- CONJ: `atau`, `kalau`, `tetapi`.
- ADV sesuai konvensi anotasi proyek v1: `akan`, `sedang`, `sangat`, `sekali`.

Kata `dulu` dan `tetap` sengaja belum dimasukkan karena berpotensi memiliki fungsi berbeda. Tes memastikan keduanya tetap tidak dikenal oleh fallback. Tes juga memastikan lema `jalan` tetap membawa kandidat NOUN dan VERB dari kamus.

GitHub Actions run [#5](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908285217) sukses:
- Validator: 60 kalimat, 314 token, 36 development, 24 test.
- Evaluator development-only: 148 token resolved; 107 benar; coverage 72,3%; accuracy 72,3%; selective accuracy 100%.
- POS leksikal dan kontekstual menghasilkan metrik identik.
- Gold ambiguous: 1 ditahan, 0 dipaksakan.
- Regression suite: **141/141 lulus**.

Perubahan coverage dari 60,8% ke 72,3% berlaku pada development set yang sama (36 kalimat) setelah fallback ditambahkan. Ini menunjukkan gap yang diaudit berhasil ditangani pada contoh yang tercakup, tetapi bukan estimasi akurasi umum. Test split 24 kalimat tetap tidak digunakan.


## Batch ketujuh dan evaluasi development — 27 November 2026

Batch ketujuh menambahkan enam record development (`pos_0061`–`pos_0066`) dan empat record test (`pos_0067`–`pos_0070`). Fenomena development meliputi numeralia, preposisi tujuan, konjungsi pilihan/subordinatif, penanda aspek/modalitas, demonstrativa, dan adverbia derajat. Empat record test hanya ditambahkan sebagai data tertahan dan tidak digunakan untuk penyetelan.

GitHub Actions run [#6](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908531211) berhasil:
- Validator: 70 kalimat, 374 token, 42 development, 28 test.
- Evaluator development-only: 174 token resolved; 131 benar; coverage 75,3%; accuracy 75,3%; selective accuracy 100%.
- Gold ambiguous: 1 ditahan, 0 dipaksakan.
- Regression suite: **141/141 lulus**.

Hasil batch ketujuh mencakup development yang lebih besar; jangan membandingkan persentase dengan batch sebelumnya sebagai tren kualitas tanpa mempertimbangkan perubahan komposisi. Test split 28 kalimat tetap tidak digunakan.


## Batch kedelapan dan evaluasi development — 27 November 2026

Batch kedelapan menambahkan enam record development (`pos_0071`–`pos_0076`) dan empat record test (`pos_0077`–`pos_0080`). Fenomena development meliputi numeralia atributif, preposisi lokatif/tujuan, konjungsi pertentangan, penanda aspek, demonstrativa, nomina berimbuhan, dan adverbia derajat. Empat record test hanya ditambahkan sebagai data tertahan.

GitHub Actions run [#7](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45908957782) berhasil:
- Validator: 80 kalimat, 428 token, 48 development, 32 test.
- Evaluator development-only: 199 token resolved; 149 benar; coverage 74,9%; accuracy 74,9%; selective accuracy 100%.
- Gold ambiguous: 1 ditahan, 0 dipaksakan.
- Regression suite: **141/141 lulus**.

Metrik hanya menggambarkan development set yang kini berisi 48 kalimat. Penurunan persentase dibanding batch sebelumnya bukan bukti regresi atau peningkatan tanpa analisis komposisi dan contoh. Test split 32 kalimat tetap tidak digunakan.
