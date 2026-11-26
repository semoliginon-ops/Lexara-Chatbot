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

## 5. Keputusan sementara

1. Jangan mengubah label dataset hanya berdasarkan perbedaan istilah antar-skema POS.
2. Tambahkan konvensi eksplisit untuk demonstrativa, aspek, larangan, dan gelar sapaan ke pedoman anotasi sebelum memperluas dataset terlalu jauh.
3. Setelah pedoman disepakati, audit ulang seluruh development set menggunakan pedoman yang sama.
4. Jangan membuka atau menggunakan split test untuk menyetel aturan.
5. Jalankan kembali validator dataset dan seluruh regression tests setelah ada perubahan data atau kode.

## 6. Titik lanjut

Langkah berikutnya adalah menyelaraskan aturan anotasi yang belum eksplisit dengan taksonomi resmi di `docs/KAMUS.md`, lalu memperbarui pedoman `docs/DATASET_POS.md`. Setelah itu, audit development set sekali lagi sebelum menambah batch dataset berikutnya.
