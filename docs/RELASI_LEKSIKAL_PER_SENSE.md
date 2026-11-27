# Rancangan Relasi Leksikal per-Sense

**Status:** Rancangan kompatibilitas; belum diterapkan ke data batch.  
**Cakupan:** Sinonim, antonim, dan kata berkaitan pada entri kamus Sistem Bahasa.

## 1. Tujuan

Relasi leksikal harus terikat pada makna yang benar. Satu lemma dapat memiliki beberapa sense dan satu relasi tidak selalu berlaku untuk semua sense.

Contoh: `jalan` sebagai nomina dapat berhubungan sinonim dengan `jalur`, sedangkan penggunaan `jalan` sebagai verba tidak otomatis memiliki relasi yang sama.

## 2. Bentuk skema yang diusulkan

Field relasi boleh ditambahkan secara opsional di dalam objek sense:

```json
{
  "id": "K0020",
  "lemma": "jalan",
  "pos": ["NOUN", "VERB"],
  "senses": [
    {
      "sense_id": "K0020-S1",
      "definition": "Tempat atau jalur yang digunakan untuk dilalui orang atau kendaraan.",
      "pos": "NOUN",
      "synonyms": ["jalur", "lintasan"],
      "antonyms": [],
      "related_terms": ["trotoar", "kendaraan", "arah"]
    },
    {
      "sense_id": "K0020-S2",
      "definition": "Bergerak atau melangkah dengan menggunakan kaki; berjalan.",
      "pos": "VERB",
      "synonyms": [],
      "antonyms": [],
      "related_terms": ["berjalan", "melangkah"]
    }
  ]
}
```

Field yang diusulkan:
- `synonyms`: array string untuk padanan makna pada sense tersebut.
- `antonyms`: array string untuk lawan makna pada sense tersebut.
- `related_terms`: array string untuk hubungan konseptual pada sense tersebut.

Ketiga field bersifat opsional. Jika digunakan, nilainya harus berupa array string; array kosong diperbolehkan.

## 3. Kompatibilitas dengan data lama

1. Field relasi tingkat entri (`synonyms`, `antonyms`, `related_terms`) tetap diterima.
2. Data lama tidak perlu langsung dipindahkan atau dihapus.
3. Relasi tingkat entri yang belum diberi sense harus diperlakukan sebagai **relasi tanpa cakupan sense**, bukan otomatis disalin ke seluruh sense.
4. Jika sense tertentu tidak memiliki anotasi relasi, sistem tidak boleh mengarang atau mewarisi relasi dari sense lain.
5. Konsumen data harus mempertahankan informasi cakupan relasi: `sense_scoped` atau `entry_unscoped`.
6. Field baru tidak mengubah pencocokan token, normalisasi, morfologi, atau POS tagger.
7. Migrasi data dilakukan bertahap hanya setelah validator dan pembaca relasi diuji.

## 4. Aturan linguistik

- Sinonim dekat dan sinonim kontekstual boleh dicatat, tetapi perbedaan register dan batas pemakaiannya harus dijelaskan jika berpengaruh.
- Kata yang hanya berkaitan secara konsep tidak boleh dimasukkan sebagai sinonim.
- Bentuk turunan bukan otomatis sinonim.
- Relasi hanya boleh dimasukkan ke sense yang didukung bukti definisi dan pemakaiannya.
- Jangan memaksakan relasi timbal balik. Jika A mencatat B, sistem tidak boleh menganggap B pasti mencatat A.
- Jangan menyimpulkan antonim hanya karena dua kata sering muncul berlawanan dalam contoh.
- Relasi yang meragukan tetap menjadi temuan tinjauan, bukan data yang dipaksakan.

## 5. Validasi yang direncanakan

Validator relasi nantinya memeriksa:
- Setiap sense berupa objek dan memiliki `sense_id` yang valid.
- Field relasi, jika ada, berupa array string nonkosong per item.
- Tidak ada duplikasi relasi setelah normalisasi Unicode dan casefold dalam satu daftar.
- Tidak ada nilai relasi yang sama dengan lemma sendiri, kecuali ada alasan linguistik yang didokumentasikan.
- Field lama di tingkat entri tetap valid.
- Field baru tidak diwajibkan pada entri lama.
- Relasi tidak harus menunjuk ke lemma yang sudah ada; frasa atau istilah terkait boleh tetap dicatat sebagai string, tetapi status keterhubungannya tidak boleh dianggap sebagai entri kamus yang tervalidasi.

Validasi struktur tidak dapat membuktikan kebenaran linguistik. Tinjauan makna tetap diperlukan.


## 7. Validator struktural

Modul terpisah `tools/validasi_relasi_leksikal.py` memeriksa satu batch tanpa mengubah data. Jalankan dari root repository:

```bash
python -m unittest discover -s tests -p "test_validasi_relasi_leksikal.py" -v
python -m tools.validasi_relasi_leksikal data/kamus/batch-001.jsonl
```

Validator memeriksa tipe array, item teks nonkosong, duplikasi setelah normalisasi Unicode NFC dan casefold, relasi yang menunjuk ke lemma sendiri, serta keberadaan `sense_id` ketika sebuah sense menggunakan field relasi. Field relasi yang tidak digunakan tetap opsional; data lama tidak diwajibkan memiliki relasi per-sense.

Jalankan validator satu batch pada satu waktu. Hasil lulus hanya menyatakan struktur relasi lolos pemeriksaan, bukan bahwa relasinya benar secara linguistik. Implementasi dan tes masih harus diverifikasi di lingkungan lokal sebelum dinyatakan selesai.

## 8. Tahapan penerapan

1. Tinjau dan setujui rancangan skema.
2. Tambahkan validator terpisah beserta unit tests.
3. Uji data lama dan contoh baru tanpa mengubah batch.
4. Tambahkan pembaca relasi yang mempertahankan cakupan sense, jika memang dibutuhkan komponen berikutnya.
5. Perbarui data batch secara selektif setelah audit selesai dan setiap perubahan memiliki bukti.
6. Jalankan seluruh regression tests sebelum menyatakan kompatibel.

**Status saat ini:** rancangan dan validator struktural telah ditambahkan, beserta regression tests. Verifikasi lokal masih menunggu. Belum ada perubahan pada 3.000 entri, loader, pencocokan, morfologi, atau POS tagger.
