# Kontrak Interaksi Klarifikasi v1

**Tahap:** 3 — Hubungan makna dan pemrosesan konteks.  
**Status:** kontrak desain; belum diimplementasikan dan belum terhubung ke runtime.  
**Bergantung pada:** `tools/clarification_planner.py` dan sumber deskripsi kandidat yang tervalidasi.

## 1. Tujuan dan batas

Kontrak ini mengatur bagaimana satu fokus klarifikasi disajikan kepada pengguna dan bagaimana responsnya dicatat. Ia tidak memilih makna, tidak mengubah laporan interpretasi, tidak menjalankan analyzer/parser, dan tidak menentukan tindakan aplikasi.

Satu sesi klarifikasi hanya menangani satu fokus dari keluaran planner. Sesi tidak boleh mengubah kandidat, menambah opsi, atau mengubah keputusan planner menjadi kepastian semantik tanpa bukti.

Tidak ada integrasi runtime, penyimpanan permanen, pengiriman pesan otomatis, atau pemrosesan lanjutan atas jawaban pada v1.

## 2. Prasyarat penyajian kandidat

Masukan penyaji harus memuat:
- satu keluaran planner dengan `decision == "ask"` dan satu `focus`;
- referensi kandidat yang cocok persis dengan fokus;
- sedikitnya dua deskripsi kandidat yang dapat dipahami pengguna;
- asal deskripsi yang dapat ditelusuri ke data leksikal/gramatikal tepercaya.

Aturan keras:
1. Referensi internal seperti `candidate_index`, `sense_id`, dan `source_field` tidak ditampilkan kepada pengguna.
2. Label/uraian harus berasal dari definisi, glos, kategori, atau keterangan sumber yang benar-benar tersedia. Jangan membuat definisi hanya dari nama lemma, ID, urutan kandidat, atau tebakan model.
3. Teks contoh hanya boleh ditampilkan jika contoh itu memang tersimpan pada sumber kandidat dan aman ditampilkan.
4. Jika sumber tidak menyediakan uraian yang membedakan kandidat, jangan membuat pilihan. Kembalikan `cannot_present_safely` dan jangan membuka sesi tanya.
5. Satu objek kandidat yang berisi beberapa `sense_ids` tidak boleh dipecah menjadi pilihan pengguna kecuali setiap sense dapat diambil dan dipasangkan ke deskripsi otoritatifnya secara tepat.
6. Kandidat POS/sintaksis tidak boleh diterjemahkan menjadi istilah teknis yang membingungkan. Jika perbedaan tidak dapat dijelaskan secara sederhana dan setia pada sumber, jangan tampilkan.

**Kondisi sumber repo setelah audit:** definisi sense tepercaya sebenarnya tersedia di kamus proyek dan dapat ditelusuri melalui `snapshot.tokens[token_index].lexical_candidates[candidate_index].entry.senses[sense_index].definition`. Rincian jalur dan contoh entri dicatat dalam [AUDIT_SUMBER_DESKRIPSI_KANDIDAT_KLARIFIKASI.md](AUDIT_SUMBER_DESKRIPSI_KANDIDAT_KLARIFIKASI.md). Namun, laporan interpretasi dan planner v1 hanya menggunakan referensi tingkat objek kandidat. Satu kandidat entri dapat berisi dua sense, sehingga planner v1 tidak dapat memilih dua sense itu sebagai opsi terpisah. Prasyarat granularitas sense-level kini dipenuhi oleh planner v1.1 dan tes terfokusnya; lihat [KONTRAK_PERENCANA_KLARIFIKASI_V1_1.md](KONTRAK_PERENCANA_KLARIFIKASI_V1_1.md). Penyaji dapat dirancang untuk sense leksikal yang memiliki definition tervalidasi. Kasus POS/sintaksis tetap tidak boleh ditampilkan kecuali kelak tersedia deskripsi sumber yang aman.

## 3. Bentuk pertanyaan

Jika seluruh prasyarat terpenuhi:
- tampilkan bagian ujaran yang perlu diperjelas;
- tampilkan paling sedikit dua pilihan yang masing-masing berasal dari deskripsi sumber;
- gunakan redaksi netral, singkat, dan tidak mengarahkan;
- jangan menyatakan salah satu pilihan lebih mungkin hanya karena urutan atau frekuensi;
- sediakan cara untuk menjawab dengan kata-kata sendiri atau menolak menjawab;
- tampilkan maksimal satu fokus dalam satu giliran.

Template hanya kerangka, bukan kalimat final otomatis:

`Pada bagian "<kutipan token>", maksud/makna yang kamu gunakan yang mana?`

Pilihan diisi dari deskripsi sumber yang sudah diverifikasi. Jika kutipan atau deskripsi tidak tersedia/aman, jangan gunakan template tersebut.

## 4. Identitas dan status sesi

Satu sesi memuat:
- `session_id` lokal/opaque yang tidak mengandung data pribadi;
- `planner_focus` persis seperti sumber;
- `prompt_choices` dengan kunci pilihan lokal dan referensi kandidat internal yang disimpan terpisah dari teks tampilan;
- `status`;
- respons mentah pengguna bila ada.

Status sesi:
- `presented`: pertanyaan aman sudah disajikan;
- `answered_choice`: pengguna memilih tepat satu pilihan yang tersedia;
- `answered_free_text`: pengguna memberi teks sendiri yang belum dapat dipetakan secara aman;
- `declined`: pengguna secara eksplisit menolak/menyatakan tidak ingin menjawab;
- `no_response`: tidak ada respons sampai sesi ditutup oleh pemanggil;
- `invalid_response`: respons pilihan tidak cocok dengan pilihan sesi;
- `cancelled`: sesi dibatalkan oleh pemanggil.

Status sesi bukan status interpretasi. Memilih opsi tidak otomatis membuktikan bahwa interpretasi sumber benar; ia hanya mencatat pilihan eksplisit pengguna untuk fokus tersebut.

## 5. Penanganan respons

| Respons pengguna | Pencatatan | Tindakan yang dilarang |
|---|---|---|
| Memilih satu kunci pilihan yang valid | `answered_choice`, simpan kunci dan ref yang terhubung | Jangan mengubah pilihan menjadi fakta di luar fokus sesi. |
| Memilih lebih dari satu pilihan padahal sesi meminta satu | `invalid_response` atau `answered_free_text` jika disampaikan sebagai teks | Jangan memilih salah satu secara otomatis. |
| Menjawab dengan kata-kata sendiri | `answered_free_text`, simpan teks apa adanya | Jangan memaksa teks ke kandidat terdekat atau mengklaim sudah terjawab. |
| Jawaban tampak parsial/tidak lengkap | Simpan sebagai `answered_free_text`; kelengkapan tetap `unknown` kecuali pengguna menyatakannya eksplisit | Jangan menganggap bagian yang tidak disebut sebagai persetujuan atau penolakan. |
| Menolak menjawab | `declined` | Jangan mengulang pertanyaan yang sama atau menghukum pengguna dengan menghentikan percakapan. |
| Tidak ada jawaban | `no_response` saat pemanggil menutup sesi | Jangan menganggap diam sebagai pilihan. |
| Kunci pilihan tidak dikenal | `invalid_response` | Jangan menebak pilihan yang dimaksud. |

Respons teks bebas atau parsial tidak otomatis menjadi bukti kandidat. Penafsiran respons bebas memerlukan proses interpretasi baru dan kontrak terpisah; itu bukan bagian v1 ini.

## 6. Setelah sesi

- Pilihan eksplisit hanya mengikat fokus sesi yang bersangkutan.
- Respons bebas, parsial, tidak valid, penolakan, dan tidak adanya jawaban tidak mengubah laporan awal.
- Jangan mengulang pertanyaan yang sama tanpa bukti/ketidakpastian baru.
- Jika klarifikasi belum menyelesaikan masalah, sistem harus tetap abstain atau menyatakan batas pemahamannya.
- Tidak ada pertanyaan kedua otomatis dalam satu sesi.
- Jangan menyimpan informasi pribadi tambahan yang tidak diperlukan.

## 7. Batas data dan privasi

- Simpan hanya data minimum untuk mencatat fokus, pilihan, status, dan respons.
- Jangan meminta nama, lokasi, kontak, atau data sensitif kecuali benar-benar diperlukan oleh tugas lain yang terpisah.
- `session_id` tidak boleh memuat teks ujaran atau identitas pengguna.
- Redaksi yang tampil kepada pengguna tidak boleh memuat ID internal, nama field, indeks array, status parser, atau detail implementasi.

## 8. Keluaran kontrak

Hasil penyajian:
- `presented`: satu prompt dan pilihan yang telah tervalidasi;
- `cannot_present_safely`: sumber kandidat tidak cukup untuk menjelaskan pilihan; tidak ada prompt.

Hasil pencatatan respons:
- `answered_choice`;
- `answered_free_text`;
- `declined`;
- `no_response`;
- `invalid_response`;
- `cancelled`.

Setiap hasil harus tetap menyertakan referensi fokus internal untuk audit, tetapi referensi itu tidak ditampilkan kepada pengguna. Teks mentah pengguna dipisahkan dari teks pilihan yang dibuat dari sumber.

## 9. Cakupan tes khusus yang direncanakan

Jika dan hanya jika sumber deskripsi kandidat sudah tersedia dan tervalidasi, implementasi v1 dibatasi tepat **10 tes unit khusus**:

1. tidak menyajikan prompt jika planner bukan `ask`;
2. tidak menyajikan prompt jika focus tidak ada atau tidak valid;
3. menolak kandidat yang tidak cocok dengan referensi fokus;
4. menolak presentasi jika kurang dari dua deskripsi kandidat tepercaya;
5. tidak memecah satu kandidat multi-sense tanpa deskripsi sense yang cocok satu per satu;
6. menghasilkan satu prompt dengan pilihan netral dari deskripsi sumber yang tervalidasi;
7. mencatat pilihan tunggal yang valid beserta referensi fokus;
8. menyimpan jawaban bebas/parsial tanpa memetakannya otomatis ke kandidat;
9. mencatat penolakan dan tidak ada respons tanpa memilih kandidat;
10. menolak pilihan tidak valid atau multi-pilihan tanpa memilih otomatis.

Tes tidak mengulang 11 tes planner atau 11 tes interpretasi. Tidak menjalankan regression suite 450 tes. Tidak ada workflow atau implementasi sebelum prasyarat sumber deskripsi terpenuhi.

## 10. Pekerjaan yang tetap ditunda

- Menemukan dan memverifikasi lookup definisi/glos per sense dan per kandidat POS.
- Menafsirkan jawaban bebas pengguna.
- Menggunakan jawaban klarifikasi untuk mengubah sense pilihan atau konteks multi-giliran.
- Menyimpan sesi secara permanen.
- Menghasilkan redaksi bebas berbasis LLM.
- Mengintegrasikan klarifikasi ke entrypoint/runtime.

**Kriteria penerimaan desain:** tidak ada kandidat/definisi rekaan; pilihan tampil hanya jika setiap opsi punya sumber tepercaya; jawaban bebas/parsial tidak dipaksa menjadi pilihan; penolakan/diam tidak dianggap jawaban; dan satu sesi hanya memiliki satu fokus.

## 11. Status prasyarat perencana

Planner v1.1 telah mendukung referensi sense-level dan memverifikasi definisi sumber terhadap snapshot. Implementasi serta 12 tes khusus lulus melalui GitHub Actions Run #2 [46118895383](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46118895383); kompatibilitas planner v1 diverifikasi kembali 11/11 pada Run [46118895363](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46118895363). Kontrak penyaji dan pencatatan respons tetap belum diimplementasikan atau dihubungkan ke runtime.
