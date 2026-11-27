# Audit Integritas Index Kamus

**Tanggal:** 27 November 2026  
**Cakupan:** Delapan token shard di `data/kamus/index/`  
**Status:** Audit struktur internal selesai; pencocokan menyeluruh terhadap 60 batch belum dilakukan.

## Ringkasan hasil

| Shard | Baris |
|---|---:|
| `a-c.tsv` | 645 |
| `d-f.tsv` | 413 |
| `g-i.tsv` | 329 |
| `j-l.tsv` | 594 |
| `m-o.tsv` | 469 |
| `p-r.tsv` | 458 |
| `s-u.tsv` | 597 |
| `v-z.tsv` | 92 |
| **Total** | **3.597** |

Jenis token yang tercatat:

- 3.000 lema
- 586 bentuk turunan
- 11 variasi

## Pemeriksaan yang lulus

- Semua baris memiliki lima kolom: token, ID, lema, jenis, dan nama batch.
- ID mengikuti format `K####`.
- Referensi batch mengikuti format `batch-NNN`.
- Seluruh 60 batch terwakili dalam baris bertipe lema.
- Urutan token alfabetis pada setiap shard.
- Penempatan huruf awal sesuai rentang nama shard.
- Tidak ditemukan token duplikat pada gabungan delapan shard.
- Jumlah baris dan distribusi jenis token konsisten dengan hasil pembacaan index.

## Perbaikan yang dilakukan

Audit awal menemukan lima token berada di shard yang tidak sesuai:

| Token | Shard sebelumnya | Shard yang benar |
|---|---|---|
| `cek` | `v-z.tsv` | `a-c.tsv` |
| `lulus` | `v-z.tsv` | `j-l.tsv` |
| `rapat` | `v-z.tsv` | `p-r.tsv` |
| `rekan` | `v-z.tsv` | `p-r.tsv` |
| `rencana` | `v-z.tsv` | `p-r.tsv` |

Setelah pemindahan, seluruh delapan shard diambil ulang dari GitHub dan diperiksa kembali. Hasil akhir: tidak ada token salah penempatan, semua shard terurut, dan tidak ada token duplikat.

## Batas audit

Audit ini hanya memeriksa konsistensi internal index. Index merupakan peta ringan, bukan pengganti batch JSONL.

Pemeriksaan berikut belum dilakukan:

1. Mencocokkan setiap lema index dengan entri sumber pada batch JSONL.
2. Memastikan setiap `derived_form` dan `variant` benar-benar tercatat pada entri sumber yang sesuai.
3. Memeriksa metadata lengkap seperti POS, senses, register, dan `derived_forms_pos`.

## Langkah audit berikutnya

Alat streaming `tools/audit_index_kamus.py` dan regression tests awal sudah ditambahkan. Alat ini membaca satu batch sumber pada satu waktu, lalu membandingkan seluruh baris lema, variasi, dan bentuk turunan dengan delapan shard index. Kode dan tes masih menunggu verifikasi lokal sebelum audit penuh dinyatakan selesai.

Jalankan setelah mengambil perubahan terbaru:

    python -m unittest discover -s tests -p "test_audit_index_kamus.py" -v && python -m tools.audit_index_kamus

Jangan memuat atau mengirim seluruh 60 batch sekaligus ke percakapan. Proses lokal membaca batch satu per satu dan menggunakan index ringan sebagai pembanding.
