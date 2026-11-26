# Indeks Utama Kamus — Sistem Bahasa

**Status:** Register awal; belum berisi entri kosakata yang disetujui  
**Target:** 3.000 lemma unik untuk Kamus v1.0  
**Sumber aturan:** ../../docs/KAMUS.md

File ini adalah daftar induk untuk melacak semua lemma yang masuk ke kamus. Setiap kosakata baru harus diperiksa terhadap indeks ini sebelum ditambahkan ke data kamus. Tujuannya mencegah duplikasi, menjaga ID tetap unik, dan memastikan variasi ejaan diarahkan ke entri kanonis yang benar.

## 1. Aturan wajib sebelum menambah kata

1. Normalisasikan kandidat untuk pencarian duplikat: Unicode NFC, hapus spasi di awal/akhir, dan gunakan huruf kecil untuk pencocokan dasar.
2. Jangan menghapus tanda hubung atau apostrof secara otomatis; tanda tersebut bisa membedakan bentuk kata.
3. Periksa apakah bentuk itu sudah tercatat sebagai lemma, variant, derived_form, atau redirect.
4. Jika hanya beda kapitalisasi atau salah ketik, jangan buat lemma baru. Catat sebagai variasi jika memang berguna.
5. Jika dua bentuk berbeda tetapi maknanya sama/berhubungan, jangan otomatis menggabungkannya. Tinjau sebagai kemungkinan sinonim atau kata terkait.
6. Satu lemma boleh mempunyai beberapa POS dan beberapa sense. Jangan membuat entri lemma baru hanya karena maknanya berbeda.
7. Homograf atau bentuk sama dengan asal/fungsi berbeda harus dicatat dengan sense terpisah dan catatan pembeda.
8. Jangan menganggap bentuk turunan berimbuhan sebagai lemma baru secara otomatis. Tambahkan sebagai lemma tersendiri hanya jika dibutuhkan sebagai bentuk leksikal mandiri; jika tidak, simpan di derived_forms.
9. Semua entri baru harus diberi ID stabil dan tidak boleh menggunakan ulang ID yang pernah dipakai.
10. Jika status kata masih meragukan, masukkan ke daftar tinjauan, bukan daftar lemma disetujui.

## 2. Status entri

| Status | Arti |
|---|---|
| approved | Sudah diperiksa dan masuk hitungan target 3.000 |
| review | Masih perlu verifikasi makna, POS, atau keunikan |
| rejected | Tidak digunakan; simpan alasan agar tidak diajukan ulang |
| merged | Digabung/diarahkan ke lemma kanonis lain |

Hanya status approved yang dihitung ke target 3.000 lemma.

## 3. Indeks lemma kanonis

Tambahkan satu baris untuk setiap lemma kanonis. Urutkan alfabetis berdasarkan lemma yang sudah dinormalisasi.

| ID | Lemma kanonis | POS | Register | Variasi/alias | Status | Catatan |
|---|---|---|---|---|---|---|
| — | Belum ada entri | — | — | — | — | Indeks akan diisi setelah kurasi kosakata dimulai. |

## 4. Daftar kandidat yang perlu ditinjau

Gunakan tabel ini untuk kata yang berpotensi duplikat, memiliki ejaan tidak baku, atau belum jelas kelas/maknanya.

| Kandidat | Kemungkinan lemma kanonis | Jenis pemeriksaan | Status | Catatan |
|---|---|---|---|---|
| — | — | — | — | Belum ada kandidat. |

## 5. Aturan pencatatan variasi

Contoh konseptual (bukan entri kamus yang sudah disahkan):

| Bentuk ditemukan | Perlakuan indeks |
|---|---|
| gak, nggak, enggak | Evaluasi sebagai variasi/alias atau lemma terpisah jika makna/fungsinya berbeda; jangan otomatis menghitung semuanya sebagai tiga lemma. |
| makan, memakan, dimakan | Umumnya satu lemma dasar dengan bentuk turunan, kecuali ada alasan leksikal untuk entri mandiri. |
| bisa (mampu), bisa (racun) | Satu bentuk lemma dengan sense berbeda; POS dapat berbeda. |
| gue, aku | Jangan digabung sebagai duplikat; keduanya bentuk leksikal berbeda dengan relasi makna/pronomina. |

## 6. Hitungan progres

- Lemma disetujui: **0 / 3.000**
- Kandidat dalam tinjauan: **0**
- Ditolak: **0**
- Digabung/alias: **0**

Hitungan harus diperbarui setiap batch kosakata selesai diperiksa. Jangan memperkirakan jumlah secara manual jika data sumber belum dihitung.

## 7. Alur kerja setiap batch

1. Kumpulkan batch kandidat.
2. Normalisasikan ejaan untuk pencocokan.
3. Cari kandidat terhadap lemma, variasi, bentuk turunan, dan alias yang sudah ada.
4. Periksa makna dan POS; tandai homograf atau polisemi.
5. Putuskan: lemma baru, variasi, bentuk turunan, relasi, atau ditolak.
6. Berikan ID stabil hanya setelah kandidat disetujui.
7. Tambahkan ke indeks ini dan data kamus dalam perubahan yang sama.
8. Jalankan pemeriksaan duplikat dan validasi skema sebelum commit.

**Prinsip:** indeks adalah sumber rujukan utama untuk pemeriksaan duplikat. Jangan menambahkan batch baru hanya berdasarkan ingatan atau percakapan; periksa file indeks dan data kamus terbaru di repository terlebih dahulu.
