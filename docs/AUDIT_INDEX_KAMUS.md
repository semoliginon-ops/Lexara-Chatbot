# Audit Integritas Index Kamus

**Tanggal:** 27 November 2026  
**Cakupan:** Delapan shard index dibandingkan dengan 60 batch sumber.

## Prinsip desain

Index adalah peta ringan, bukan salinan lengkap seluruh metadata dan bentuk turunan dari batch. Karena itu:
- Semua 3.000 lema wajib tercantum di index.
- Setiap baris yang tercantum (lema, variasi, atau bentuk turunan) wajib cocok dengan sumber batch: token, ID, lema induk, tipe, dan nama batch.
- Variasi dan bentuk turunan boleh tidak dicantumkan seluruhnya. Ketidakadaan bentuk opsional di index bukan kesalahan.
- Baris index yang tidak punya pasangan tepat di batch sumber adalah kesalahan.
- Audit membaca satu batch pada satu waktu.

## Hasil pemeriksaan index internal sebelumnya

Index memiliki 3.597 baris: 3.000 lema, 586 bentuk turunan, dan 11 variasi. Pemeriksaan internal sebelumnya menemukan urutan shard benar, tidak ada duplikasi token, dan tidak ada salah penempatan huruf.

## Koreksi atas audit pertama

Eksekusi pertama alat audit menghasilkan 6.065 baris yang diharapkan dan melaporkan 2.468 baris hilang. Angka tersebut menghitung seluruh variasi dan bentuk turunan dari batch seolah-olah semuanya wajib dimasukkan ke index. **Asumsi itu keliru untuk desain index ringan.** Hasil tersebut bukan bukti 2.468 data kamus hilang; itu menunjukkan bentuk opsional yang tidak dimasukkan ke index.

Audit diperbaiki agar membedakan:
1. **Lema wajib:** seluruh lema harus ada.
2. **Baris opsional:** variasi dan bentuk turunan boleh tidak ada di index.
3. **Baris tak cocok:** setiap baris yang ada di index tetap harus cocok persis dengan sumber batch.

## Verifikasi

Jalankan:

    python -m unittest discover -s tests -p "test_audit_index_kamus.py" -v
    python -m tools.audit_index_kamus

Audit dinyatakan lulus hanya jika seluruh batch dan 3.000 lema valid, tidak ada baris index tambahan/tidak cocok, dan tidak ada kesalahan struktur. Jumlah bentuk opsional yang tidak diindeks dilaporkan sebagai informasi, bukan kegagalan.
