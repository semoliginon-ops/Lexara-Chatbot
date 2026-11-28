# Kebijakan Klarifikasi v1

**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.  
**Status:** rancangan kebijakan; belum diimplementasikan dan belum terhubung ke dialog/runtime.  
**Masukan:** laporan `tools/utterance_interpretation.py` dan referensi sumber Context Snapshot.

## 1. Tujuan

Menentukan kapan Lexara perlu meminta informasi tambahan kepada pengguna, kapan harus menyatakan belum memahami, dan kapan tidak perlu mengganggu pengguna dengan pertanyaan. Kebijakan ini tidak memilih makna, tidak memperbaiki parser, dan tidak menghasilkan tindakan runtime.

Prinsip utama: **klarifikasi hanya diminta jika jawaban pengguna berpotensi menyelesaikan ketidakpastian yang berpengaruh pada respons berikutnya.**

## 2. Syarat wajib sebelum bertanya

Klarifikasi hanya boleh dipertimbangkan jika seluruh syarat berikut terpenuhi:

1. Ada ketidakpastian spesifik yang terdeteksi dan status/sumbernya dapat ditelusuri.
2. Ada sedikitnya dua interpretasi yang benar-benar didukung sumber, bukan kandidat rekaan.
3. Perbedaan interpretasi mengubah jawaban atau tindakan berikutnya secara material.
4. Ada pertanyaan singkat dan netral yang jawabannya dapat membedakan interpretasi tersebut.
5. Pertanyaan tidak meminta pengguna mengulang informasi yang sebenarnya sudah tersedia.

Jika satu syarat gagal, jangan mengajukan pertanyaan pilihan yang dibuat-buat.

## 3. Keputusan berdasarkan status

| Kondisi laporan | Keputusan v1 | Alasan |
|---|---|---|
| `resolved` | Jangan bertanya | Tidak ada ketidakpastian yang perlu diselesaikan pada aspek tersebut. |
| `ambiguous` dengan beberapa kandidat yang dapat dijelaskan | Pertimbangkan klarifikasi jika berdampak material dan dapat dibedakan oleh pengguna | Kandidat nyata tersedia, tetapi belum dipilih. |
| `ambiguous` tanpa kandidat yang dapat dijelaskan | Nyatakan bagian yang belum jelas; jangan membuat pilihan | Tidak ada dasar untuk menyusun pertanyaan pilihan. |
| `unresolved` karena informasi pengguna memang kurang | Minta satu informasi spesifik hanya jika kekurangannya dapat dijawab pengguna | Pengguna dapat melengkapi informasi yang hilang. |
| `unresolved` karena parser/analyzer tidak menghasilkan data | Jangan meminta pengguna menyelesaikan masalah internal sistem | Ini keterbatasan pemrosesan, bukan otomatis kekurangan informasi pengguna. |
| `deferred` atau pemetaan sumber tidak aman | Tunda; jangan bertanya berdasarkan hasil yang belum aman | Sistem belum memiliki landasan interpretasi yang dapat dipercaya. |
| Ketidakpastian tidak mengubah jawaban/tindakan | Lanjutkan dengan respons aman tanpa bertanya | Klarifikasi tidak memberi manfaat yang sebanding dengan gangguan. |

Status pada satu dimensi tidak otomatis membatalkan hasil dimensi lain. Contohnya, maksud bertanya dapat dikenali meskipun sense sebuah kata masih ambigu.

## 4. Pemilihan fokus pertanyaan

Jika beberapa ketidakpastian muncul bersamaan:

- Dahulukan ketidakpastian yang paling menentukan jawaban/tindakan berikutnya.
- Ajukan paling banyak **satu pertanyaan klarifikasi dalam satu giliran**.
- Jangan menggabungkan beberapa pertanyaan berbeda menjadi satu pertanyaan panjang.
- Jangan menanyakan kembali hal yang sudah dijawab pengguna.
- Setelah jawaban diterima, evaluasi ulang hanya ketidakpastian yang terkait; jangan mengulang seluruh pipeline atau meminta konfirmasi atas hal yang tidak berubah.
- Jika satu jawaban belum cukup, nyatakan bagian yang masih belum jelas sebelum mempertimbangkan pertanyaan lanjutan.

## 5. Bentuk pertanyaan

Pertanyaan harus:

- singkat, netral, dan tidak mengarahkan;
- menyebut bagian ujaran yang perlu diperjelas;
- menggunakan pilihan hanya jika setiap pilihan berasal dari kandidat sumber yang nyata dan dapat dipahami;
- tidak menyisipkan definisi, fakta, atau maksud yang tidak didukung sumber;
- tidak menganggap salah satu kandidat lebih benar hanya karena urutan, frekuensi, atau kebiasaan.

Jika kandidat tidak bisa diterangkan dengan aman, gunakan pertanyaan terbuka yang meminta konteks spesifik, atau nyatakan bahwa sistem belum memahami bagian tersebut. Jangan menampilkan ID internal kandidat kepada pengguna.

## 6. Batas khusus untuk maksud komunikatif

Label bentuk komunikatif bukan selalu pilihan yang saling meniadakan. Satu ujaran dapat memiliki bentuk pertanyaan sekaligus penanda permintaan. Karena itu:

- Kehadiran beberapa penanda tidak otomatis berarti pengguna harus diminta memilih satu label.
- Bedakan ketidakpastian klasifikasi dari dua fungsi komunikatif yang memang dapat hadir bersamaan.
- Jangan menyimpulkan maksud pragmatis seperti sindiran, permintaan halus, atau tujuan pribadi tanpa bukti/konteks yang cukup.
- Pertanyaan klarifikasi tentang maksud hanya layak jika perbedaan itu benar-benar mengubah respons dan pengguna dapat menjelaskannya.

**Catatan kompatibilitas:** implementasi `_classify_intent` v1 saat ini menandai beberapa penanda eksplisit yang muncul bersamaan sebagai `ambiguous`. Itu belum membuktikan bahwa label-label tersebut saling eksklusif. Sebelum kebijakan ini dipakai pada dialog nyata, perilaku tersebut perlu ditinjau sebagai pekerjaan terpisah: apakah laporan perlu mendukung beberapa bentuk komunikatif sekaligus, atau hanya mencatat ketidakpastian yang benar-benar bersaing. Jangan mengatasi persoalan ini dengan meminta pengguna memilih label secara otomatis.

## 7. Contoh keputusan

| Situasi | Keputusan |
|---|---|
| Dua sense kata tersedia dan menghasilkan jawaban berbeda; keduanya dapat dijelaskan sederhana | Tanyakan makna yang dimaksud. |
| Dua sense tersedia tetapi jawaban berikutnya sama | Jangan bertanya; lanjutkan tanpa memilih sense secara permanen. |
| Token berstatus `unresolved` karena parser tidak mengenali perannya | Jangan meminta pengguna memperbaiki analisis sintaksis internal. |
| Snapshot berstatus `deferred` karena token berulang atau struktur di luar cakupan | Tunda interpretasi; jangan membuat pilihan kandidat. |
| Ujaran tidak memiliki penanda intent yang didukung | Catat belum cukup bukti; jangan menebak dan jangan otomatis bertanya tentang niat. |
| Bentuk pertanyaan dan penanda permintaan hadir bersamaan | Jangan paksa pengguna memilih salah satu label; evaluasi apakah keduanya dapat berlaku bersama. |
| Informasi tujuan belum disebutkan dan tujuan itu menentukan rekomendasi | Minta satu informasi tujuan yang spesifik. |

Contoh-contoh ini menjelaskan kebijakan, bukan aturan bahasa aktif atau data uji.

## 8. Privasi, kendali, dan batas dialog

- Minta hanya informasi yang diperlukan untuk menyelesaikan ketidakpastian saat itu.
- Jangan meminta data pribadi atau sensitif jika tidak diperlukan untuk menjawab.
- Pengguna boleh menjawab bebas, memilih kandidat, atau menolak menjawab.
- Jika pengguna tidak menjawab, jangan mengulang pertanyaan tanpa alasan baru; berikan respons aman berdasarkan informasi yang tersedia atau nyatakan keterbatasan.
- Jangan mengarang jawaban pengguna atau mengubah jawaban parsial menjadi kepastian.

## 9. Batas implementasi

Dokumen ini hanya menetapkan kebijakan keputusan. Tidak ada perubahan pada modul interpretasi, Context Snapshot, kamus, morfologi, POS, parser, resolver, Concept Layer, generator, selector, aturan konteks, maupun runtime.

Sebelum implementasi kebijakan dialog, pekerjaan terpisah harus menetapkan:
1. representasi status keputusan klarifikasi yang dapat ditelusuri ke laporan interpretasi;
2. cara membedakan kandidat yang sungguh bersaing dari beberapa fungsi yang dapat hadir bersamaan;
3. format pertanyaan netral tanpa menampilkan detail internal;
4. perilaku setelah jawaban, jawaban parsial, atau penolakan pengguna;
5. cakupan dan jumlah tes khusus yang tetap kecil dan tidak mengulang tes v1.

**Kriteria penerimaan rancangan:** setiap keputusan bertanya memiliki alasan dan sumber; tidak ada pertanyaan saat sistem hanya mengalami kegagalan internal atau status deferred; satu giliran memuat paling banyak satu fokus klarifikasi; dan beberapa penanda komunikatif tidak otomatis diperlakukan sebagai pilihan yang saling meniadakan.
