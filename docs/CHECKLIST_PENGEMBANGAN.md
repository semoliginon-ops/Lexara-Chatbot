# Checklist Pengembangan — Sistem Bahasa

Dokumen ini adalah **peta tahapan dan status pekerjaan proyek**. Checklist menunjukkan urutan kerja, prasyarat, dan titik lanjut. Rincian teknis, riwayat versi, eksperimen, serta log pengujian disimpan di `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.

## Arti status

- [x] Selesai dan sudah diverifikasi.
- [~] Sedang dikerjakan atau sebagian fondasinya sudah tersedia.
- [ ] Belum dikerjakan.
- [!] Terhambat atau perlu keputusan.

## Snapshot proyek — 28 November 2026

- **Tahap 2.6 ditutup:** 28 November 2026 atas keputusan pengguna. **Tahap 2.7 juga selesai** pada 28 November 2026 setelah inventarisasi bukti, audit celah integrasi, dan verifikasi empat skenario end-to-end; baseline terbaru adalah GitHub Actions Run #260 (**450/450 tes lulus**). **Tahap aktif sekarang: Tahap 3 — Hubungan makna dan pemrosesan konteks.**
- Parser saat ini **v1.9**. Ini nomor versi parser, bukan tanda bahwa seluruh Tahap 2.6 sudah selesai.
- Kamus: **3.025 lema dalam 60 batch**; tidak ada rencana audit ulang batch secara rutin.
- Tahap 2.5 (POS) telah ditutup berdasarkan keputusan pengguna.
- Dataset POS: 100 kalimat / 543 token (60 development, 40 test); test split tetap tersegel.
- Evaluasi POS kontekstual pada development: 250/255 dikenali; coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%. Lima abstention berupa nama orang ditunda ke tahap pengenalan nama/konteks.
- Baseline regresi terbaru: GitHub Actions [Run #260](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46090180853) sukses dengan **450/450 regression tests lulus**. Run #257 (446/446) tetap dicatat sebagai baseline sebelum empat tes integrasi end-to-end ditambahkan. Hasil run terdahulu tetap menjadi bukti untuk cakupan khusus masing-masing.

## Aturan kerja yang harus dijaga

- Penambahan lema baru ke kamus harus mendapat **persetujuan eksplisit pengguna** sebelum batch sumber maupun indeks diubah.
- Untuk memeriksa apakah lema sudah tersedia, periksa indeks kamus terlebih dahulu. Jangan melakukan audit ulang seluruh batch tanpa alasan yang jelas.
- Parser dan komponen bahasa harus bersikap konservatif: jika bukti belum cukup, tandai unresolved/abstain; jangan menebak fungsi kata.
- Setiap perubahan perilaku harus disertai regression test yang relevan dan pemeriksaan kompatibilitas.
- Kelulusan tes membuktikan perilaku yang diuji, bukan bahwa seluruh bahasa Indonesia sudah tercakup.


## Batas pekerjaan dan pencegahan tumpang tindih antar-tahap

Bagian ini menjadi aturan lintas-tahap untuk mencegah pekerjaan lama dibuka kembali atau dua tahap mengerjakan tujuan yang sama. Jika ada perbedaan penafsiran, gunakan batas dan pemilik pekerjaan berikut.

### Batas kepemilikan pekerjaan

| Area | Pemilik utama | Batas |
|---|---|---|
| Data leksikal, lema, POS dasar, sense yang tercatat, dan relasi leksikal per-sense | Tahap 1 | Menyediakan dan merawat data leksikal. Tidak mengerjakan pemilihan sense berdasarkan konteks kalimat atau membangun jaringan konsep untuk penalaran. Perluasan anotasi relasi per-sense tetap pekerjaan data leksikal Tahap 1 dan tidak menjadi prasyarat untuk memulai Tahap 3. |
| Bentuk kata, imbuhan, morfofonemik, klitik, tokenisasi, POS, dan struktur sintaksis dasar | Tahap 2 | Menyediakan analisis bentuk dan struktur. Kekurangan cakupan yang tidak menghalangi tugas aktif dicatat sebagai backlog; tidak otomatis memicu pembukaan ulang subtahap yang telah ditutup. |
| Representasi konsep, hubungan makna, pemilihan sense kontekstual, integrasi bukti, ambiguitas, dan konteks percakapan | Tahap 3 | Menggunakan keluaran Tahap 1 dan Tahap 2 sebagai masukan. Tahap ini tidak mengambil alih perluasan kamus atau morfologi secara umum. |
| Evaluasi lintas-sistem dan optimasi perangkat | Tahap 6 | Mengukur kualitas dan biaya sistem secara menyeluruh pada tahap evaluasi. Pengukuran lokal untuk menjawab keputusan teknis tertentu boleh dilakukan di tahap pemiliknya, tetapi tujuan dan metriknya harus berbeda serta dicatat agar tidak diduplikasi. |

### Aturan khusus untuk area yang berpotensi tumpang tindih

1. **Relasi leksikal per-sense vs relasi antarkonsep:** Tahap 1 mencatat relasi leksikal yang melekat pada entri/sense kamus, misalnya sinonimi atau antonimi leksikal. Tahap 3 merancang konsep sebagai unit representasi makna dan relasi konseptual yang dipakai untuk memahami atau menghubungkan makna dalam konteks. Tahap 3 boleh memakai data Tahap 1, tetapi tidak mengulang anotasi leksikal hanya dengan nama berbeda.
2. **Morfologi dan klitik:** Tahap 2 tetap menjadi pemilik analisis bentuk kata. Variasi imbuhan, morfofonemik, pronomina informal, dan klitik yang belum tercakup dicatat sebagai backlog dengan contoh konkret. Jangan memperluas inventaris atau mengubah aturan morfologi hanya karena satu variasi ditemukan selama Tahap 3, kecuali variasi tersebut terbukti langsung memblokir alur aktif.
3. **Resolver konteks yang sudah tersedia:** resolver kandidat semantic role berbasis bukti eksplisit adalah fondasi awal Tahap 3, bukan fitur pemahaman konteks yang lengkap. Resolver tidak menghasilkan bukti konteks sendiri. Pekerjaan baru harus berfokus pada representasi makna, penyediaan bukti kontekstual, dan pemilihan sense sesuai urutan desain; jangan membangun ulang resolver yang sudah ada tanpa temuan cacat yang terverifikasi.
4. **Embedding vs evaluasi Tahap 6:** pengukuran pada bagian keputusan embedding hanya untuk menjawab apakah embedding memberi manfaat pada kasus yang tidak tertangani aturan, dibanding biaya tambahannya. Tahap 6 mengevaluasi performa dan optimasi sistem/perangkat secara menyeluruh. Jangan menjalankan dua evaluasi dengan tujuan, dataset, dan metrik yang sama; hasil pengukuran yang relevan dapat dirujuk kembali.
5. **Pengujian yang sudah lulus:** hasil tes dan baseline yang tercatat tetap menjadi bukti. Tes lama tidak dijalankan ulang hanya untuk mengisi checklist atau mengulang audit. Pengujian ulang hanya diizinkan bila ada perubahan yang berisiko pada perilaku terkait, kegagalan baru yang dapat direproduksi, atau kebutuhan verifikasi yang dijelaskan secara spesifik.

### Mekanisme backlog dan gerbang perubahan lintas-tahap

Jika pekerjaan aktif menemukan kekurangan di tahap lain, catat terlebih dahulu:
- contoh input atau kondisi yang menunjukkan masalah;
- keluaran aktual dan keluaran yang diharapkan;
- komponen serta tahap pemilik masalah;
- apakah masalah benar-benar memblokir target aktif atau hanya perluasan cakupan;
- usulan perubahan dan pengujian minimum yang diperlukan.

Temuan yang tidak memblokir target aktif tetap menjadi backlog dan tidak dikerjakan spontan. Jika benar-benar memblokir, jelaskan bukti serta dampaknya dan minta keputusan pengguna sebelum mengubah komponen lintas-tahap. Setiap perubahan harus memiliki satu tahap pemilik, satu tujuan yang jelas, dan ruang lingkup pengujian yang disepakati sebelumnya. Penambahan lema tetap memerlukan persetujuan eksplisit pengguna.

**Pagar kerja Tahap 3 saat ini:** kontrak desain Concept Layer v1 telah disetujui dan didokumentasikan di [KONTRAK_REPRESENTASI_KONSEP.md](KONTRAK_REPRESENTASI_KONSEP.md). Validator read-only `tools/validasi_concept_layer.py`, 19 tes unit terfokus, dan fixture sintetis untuk tiga skema serta indeks sense telah ditambahkan. Validator membaca batch kamus hanya untuk menyelesaikan referensi `sense_id`; tidak mengubah data kamus. Pada 28 November 2026, 18 tes lulus pada eksekusi pertama; satu tes UTF-8 gagal karena fixture tes menulis escape sebagai teks literal, bukan byte rusak. Fixture diperbaiki menjadi byte `0xFF 0xFE 0xFA`, lalu tes yang gagal itu dijalankan ulang secara terisolasi dan lulus. Dengan demikian, seluruh 19 kasus telah terverifikasi lulus (18 pada eksekusi pertama + 1 tes terisolasi setelah perbaikan); suite 19 tes tidak dijalankan ulang sebagai satu batch. Tes digit ID non-ASCII juga lulus pada eksekusi pertama. Tidak ada workflow/CI yang dipicu dan regression suite 450 tes tidak dijalankan ulang. Hasil ini memverifikasi struktur yang diuji, bukan kebenaran linguistik konsep. Tinjauan batas kasus validator selesai; jangan menjalankan ulang 450 tes regresi tanpa alasan teknis.

**Context Evidence Generator:** kontrak disetujui pada 28 November 2026. Modul `tools/context_evidence_generator.py`, 10 tes terfokus, dan workflow khusus telah ditambahkan. Generator hanya mengekstrak observasi serta evidence dari aturan `reviewed`; tidak memilih sense atau menetapkan status akhir `ambiguous`/`unresolved`. Run #1 terverifikasi lulus 10/10. Pemilihan sense dan integrasi runtime belum dilakukan.

---

# Peta tahapan utama

## Tahap 0 — Spesifikasi dan desain data

<badge color="success">Selesai</badge>

- [x] Menetapkan tujuan, ruang lingkup, dan prinsip sistem bahasa offline.
- [x] Menetapkan skema entri kamus, kelas kata, sense, ragam bahasa, dan metadata.
- [x] Menetapkan aturan ID, deduplikasi, validasi, dan struktur data.
- [x] Menyiapkan dokumentasi kamus dan format batch.

## Tahap 1 — Fondasi leksikal: kamus dan indeks

<badge color="success">Fondasi selesai</badge>

- [x] Menyusun kamus dasar dan mengembangkannya menjadi **3.025 lema / 60 batch**.
- [x] Melengkapi struktur definisi dan metadata entri sesuai skema proyek.
- [x] Menyusun indeks kamus dan 8 shard indeks.
- [x] Memvalidasi kesesuaian indeks dengan sumber kamus.
- [x] Menyelesaikan audit kualitas isi dan relasi leksikal yang telah direncanakan.
- [x] Menyediakan validator kamus lengkap dan regression tests.
- [ ] Pengembangan anotasi relasi leksikal per-sense secara lebih luas — pekerjaan lanjutan, bukan penghalang untuk melanjutkan parser.

**Catatan:** fondasi kamus selesai untuk cakupan saat ini. Ini bukan klaim bahwa seluruh kosakata atau seluruh definisi bahasa Indonesia sudah lengkap.

## Tahap 2 — Pemrosesan bahasa dasar

Tahap ini membangun alur dari teks mentah sampai struktur kalimat. Subtahap dikerjakan berurutan; parser tidak dianggap selesai hanya karena versinya bertambah.

### 2.1 Normalisasi teks

<badge color="success">Selesai</badge>

- [x] Membuat modul normalisasi.
- [x] Menetapkan dan menguji perilaku normalisasi dasar.
- [x] Menambahkan regression tests.

### 2.2 Tokenisasi

<badge color="success">Selesai</badge>

- [x] Membuat tokenizer.
- [x] Memisahkan kata dan tanda baca menjadi token.
- [x] Menetapkan perilaku kata bertanda hubung dan apostrof.
- [x] Menambahkan regression tests.

### 2.3 Pencocokan token ke kamus

<badge color="success">Selesai</badge>

- [x] Membuat loader kamus baca-saja.
- [x] Mencocokkan token dengan lema, variants, dan derived forms.
- [x] Membedakan kecocokan lema, variasi, bentuk turunan, dan token tak dikenal.
- [x] Mempertahankan kandidat POS dan sense tanpa memilih makna secara otomatis.
- [x] Mengaudit dan memvalidasi indeks kamus.
- [x] Mengintegrasikan normalisasi, tokenisasi, dan pencocokan dalam analyzer.
- [x] Menambahkan regression tests.

### 2.4 Analisis morfologi

<badge color="success">Fondasi implementasi tersedia</badge>

- [x] Membuat modul morfologi berbasis kandidat dan validasi lema kamus.
- [x] Menangani sejumlah pola prefiks, sufiks, konfiks, kombinasi imbuhan, reduplikasi, dan perubahan nasal yang telah diuji.
- [x] Mempertahankan seluruh POS/sense lema ambigu.
- [x] Menambahkan perlindungan dan tes negatif untuk mencegah pemotongan kata yang keliru.
- [ ] Memperluas inventaris imbuhan dan perubahan morfofonemik berdasarkan bukti pengujian.
- [ ] Mengukur cakupan morfologi pada variasi kata yang lebih luas.

**Batas:** morfologi sudah memiliki implementasi dasar, tetapi belum mencakup seluruh pola morfologi bahasa Indonesia.

### 2.5 Pengenalan kelas kata (POS)

<badge color="success">Selesai — ditutup 27 November 2026</badge>

- [x] Membuat POS tagger berbasis kandidat leksikal.
- [x] Menambahkan petunjuk konteks lokal secara konservatif.
- [x] Menyusun dataset berlabel 100 kalimat / 543 token.
- [x] Memisahkan development dan test; test split tetap tersegel.
- [x] Mengevaluasi POS kontekstual pada development: 250/255 dikenali, selective accuracy 100,0%.
- [x] Menetapkan abstention nama orang sebagai pekerjaan tahap pengenalan nama/konteks.
- [x] Menjalankan regression tests dan validasi terpadu.

**Status:** Tahap 2.5 ditutup. Jangan membuka kembali audit POS atau memaksa label untuk kasus yang sengaja di-abstain tanpa bukti masalah baru.

### 2.6 Analisis struktur kalimat dasar

<badge color="success">Ditutup atas keputusan pengguna — 28 November 2026</badge>

**Status: Tahap 2.6 ditutup atas keputusan pengguna pada 28 November 2026.** Implementasi yang tersedia dibekukan sebagai baseline; penutupan ini bukan klaim bahwa seluruh konstruksi sintaksis Bahasa Indonesia telah didukung.

- [x] Membuat parser dasar untuk pola S-P, S-P-O, dan keterangan.
- [x] Menambahkan dukungan bertahap untuk frasa nominal, negasi, modal, predikat nonverbal/linking, keterangan awal, koordinasi, dan klausa subordinatif yang telah diuji.
- [x] Memisahkan kepala predikat dari pewatas melalui `predicate_structure`, sambil mempertahankan `roles.predicate` untuk kompatibilitas.
- [x] Mengenali pola modal tertentu secara terbatas berdasarkan POS dan posisi terhadap verba inti.
- [x] Mengenali keterangan temporal awal yang sudah ditetapkan secara eksplisit.
- [x] Memperjelas batas keterangan preposisional awal dan subjek.
- [x] Mempertahankan abstention ketika fungsi sintaksis belum cukup jelas.
- [x] Memvalidasi parser v1.9 melalui GitHub Actions Run #126: **255/255 regression tests lulus**.
- [x] Memperluas keterangan temporal eksplisit agar dapat muncul setelah predikat atau objek, selain di awal kalimat; hanya `besok`, `nanti`, `sekarang`, dan `tadi` yang dikenali, sedangkan ADV lain tetap unresolved. Diuji pada unit parser dan pipeline kamus/POS nyata; Run #154: 342/342 tes regresi lulus.
- [x] Menetapkan katalog desain 14 semantic role setelah persetujuan pengguna, termasuk CAUSER untuk penyebab non-agentif.
- [x] Menguji batas CAUSER lintas predikat: AGENT, INSTRUMENT, STIMULUS, THEME, serta argumen penyebab vs keterangan sebab; kasus ambigu ditandai untuk abstention.
- [x] Menyetujui spesifikasi skema valensi per-sense dan aturan anotasi awal.
- [x] Membuat validator struktural `tools/validasi_valensi.py` dan 15 tes khusus; Run #129 berhasil memvalidasi 60 batch / 3.014 entri dan seluruh 273 tes regresi.
- [x] Memasukkan anotasi pilot valensi pada 4 sense yang disetujui: muncul-S1, lihat-S1, buka-S1 (frame AGENT/CAUSER alternatif), dan makan-S1 (objek opsional).
- [x] Memvalidasi anotasi pilot melalui Run #130: 60 batch / 3.014 entri dan 273 tes regresi lulus.
- [x] Menambahkan lima tes integrasi pilot untuk `muncul`, `lihat`, `buka`, dan `makan`; Run #131 sukses dengan 278/278 tes regresi.
- [x] Membuat pemetaan semantic role konservatif untuk voice aktif berbasis frame valensi; frame alternatif dipertahankan sebagai ambiguous dan argumen opsional dapat dihilangkan. Run #132 menjadi baseline awal (289 tes).
- [x] Memperketat validasi kecocokan frame: argumen inti yang dikenali parser tidak boleh diabaikan, dan OBL tanpa batas preposisi eksplisit tidak dipetakan otomatis. Run #134: 291/291 tes regresi lulus.
- [x] Membuat detektor voice morfologis konservatif berbasis kandidat lema VERB yang tervalidasi: di- sebagai kandidat pasif; meN-/memper- sebagai kandidat aktif; ter-/ber- dan bentuk tanpa bukti eksplisit tetap unresolved. Run #136: 304/304 tes regresi lulus.
- [x] Mengintegrasikan hasil deteksi voice morfologis ke keluaran `analyze_text()` per token tanpa memilih kepala predikat atau mengubah parser. Run #137: 307/307 tes regresi lulus.
- [x] Membuat adapter `tools/hubungkan_voice_predikat.py` untuk menghubungkan bukti voice token ke `predicate_structure.head` pada klausa sederhana yang diparse penuh; adapter menolak kepala berulang, hasil partial, dan struktur klausa majemuk. Run #138 sukses (316/316 tes).
- [x] Menguji jalur morfologi nyata → `analyze_text()` → kepala predikat parser → adapter untuk contoh aktif, pasif, dan bentuk `ter-` yang tetap unresolved. Run #139 sukses (319/319 tes regresi).
- [x] Mengembangkan pemetaan semantic role untuk konstruksi pasif secara konservatif; mendukung agen pasif pascaverbal, frasa `oleh`, dan agen yang dilesapkan pada pola terbatas. Run #144–148, termasuk tes integrasi end-to-end, lulus hingga 328/328 tes.
- [x] Menambahkan tes konservatif CAUSER versus INSTRUMENT: `Palu memecahkan kaca` mempertahankan dua frame alternatif, sedangkan `dengan palu` tidak otomatis dipromosikan menjadi argumen inti. Run #135: 293/293 tes regresi lulus.
- [x] Menambahkan 10 tes integrasi pipeline nyata untuk frasa nominal dengan numeralia dan pewatas adjektival pada posisi subjek maupun objek. Lima kasus subjek memeriksa `dua/tiga + NOUN` dan `NUM + NOUN + ADJ`; lima kasus objek memeriksa `NOUN + ADJ` dan `NUM + NOUN`. Run #256 mengungkap tiga kasus numeralia objek yang sebelumnya tertinggal sebagai token unresolved; parser diperbaiki agar rentang objek dapat menyerap numeralia/adjektiva yang berada tepat sebelum kepala nominal. Run #257 sukses, 446/446 tes regresi lulus.
- [~] Inversi berbasis valensi mulai didukung secara konservatif. Jika satu token predikat memiliki tepat satu kandidat lema, satu sense, dan satu frame dengan hanya satu argumen `SUBJ` NP wajib, nomina pascaverbal dapat dianalisis sebagai subjek: `Muncul masalah.` → P-S dan `Di rumah muncul masalah.` → K-P-S. Kasus tanpa bukti valensi tunggal tetap unresolved: `Timbul masalah.` dan `Di rumah terdengar suara.`; pola serupa dengan objek dan subjek tersirat (`Di rumah membaca buku.`) juga tidak dipaksakan. Run #222 sukses, 395/395 tes regresi lulus. Run #223 menambahkan tujuh kondisi negatif untuk memastikan parser abstain pada kandidat/sense/frame ambigu, argumen tambahan, subjek opsional, realisasi non-NP, dan kecocokan bentuk turunan; Run #223 sukses, 396/396 tes regresi lulus. Run #224 menambahkan dua tes integrasi untuk frasa subjek pascaverbal dengan pewatas adjektival: `Muncul masalah besar.` → P-S dan `Di rumah muncul masalah besar.` → K-P-S; keduanya mempertahankan `masalah besar` sebagai satu frasa subjek. Run #224 sukses, 397/397 tes regresi lulus. Cakupan ini masih terbatas pada pola positif yang memenuhi syarat frame tersebut, bukan dukungan inversi K-P-S umum. Batas frasa preposisional awal sebelumnya diuji melalui pipeline nyata: Run #182, 359/359 tes.
- [~] Memperluas pengujian konstruksi melalui pipeline kamus/POS nyata; mencakup predikat adjektival `Dia sakit.` (PRON+ADJ → S-P), subjek nominal `Anak makan nasi.` (NOUN+VERB+NOUN → S-P-O), negasi verbal `Aku tidak makan nasi.` (PRON+ADV+VERB+NOUN → S-P-O), serta gabungan negasi dan modalitas `Aku tidak akan makan nasi.` (PRON+ADV+ADV+VERB+NOUN → S-P-O, dengan `tidak` sebagai negasi dan `akan` sebagai modal), serta modalitas verbal `Aku mau makan nasi.` dan `Aku ingin makan nasi.` (modal VERB + verba leksikal → satu rentang predikat, dengan kepala `makan`), dan `Aku bisa makan nasi.` (`bisa` memiliki kandidat POS VERB+NOUN; konteks sebelum verba `makan` memilih VERB, lalu parser membentuk S-P-O dengan kepala `makan`), serta `Aku tidak bisa makan nasi.` (negasi ADV + modal ambigu yang dipilih sebagai VERB berdasarkan verba berikutnya; parser membentuk predikat `tidak bisa makan` dengan kepala `makan`). Run #158: 345/345, Run #159: 346/346, Run #160: 347/347, Run #161: 348/348, Run #162: 349/349, Run #164: 350/350, Run #165: 351/351 tes regresi lulus. Pengujian juga mencakup `Aku mau makan nasi besok.` (modal verbal + objek + keterangan temporal pascapredikat menghasilkan S-P-O-K); Run #166 sukses dengan 352/352 tes regresi lulus. Kombinasi negasi + modal adverb + objek + keterangan temporal pascapredikat juga diuji lewat `Aku tidak akan makan nasi besok.`; Run #167 sukses dengan 353/353 tes regresi lulus. Pengujian juga mencakup modal ambigu `bisa` bersama keterangan temporal `nanti` pada `Aku bisa makan nasi nanti.`; konteks memilih VERB dari kandidat VERB+NOUN dan parser menghasilkan S-P-O-K. Run #169 sukses dengan 354/354 tes regresi lulus. Klausa konsesif setelah klausa utama juga diuji lewat `Aku pergi walaupun hujan turun.`; pipeline mengenali kedua klausa S-P dan relasi `konsesi`. Run #170 sukses dengan 355/355 tes regresi lulus. Variasi posisi klausa konsesif juga diuji: `Walaupun hujan turun, aku pergi.`; klausa subordinatif di depan dikenali sebagai S-P, klausa utama setelah koma sebagai S-P, dengan relasi `konsesi`. Run #171 sukses dengan 356/356 tes regresi lulus. Variasi elipsis konsesif dengan penanda alternatif `meskipun` juga diuji lewat `Meskipun lelah, aku pergi.`; pipeline memverifikasi POS kamus dan menghasilkan klausa awal `P-ELIPTIS` tanpa menebak subjek, sehingga status keseluruhan tetap `partial`. Run #172 sukses dengan 357/357 tes regresi lulus. Variasi konstruksi lain masih perlu ditambahkan. Run #227 menambahkan tes pipeline untuk klausa temporal pascaposisi `Aku pulang ketika hujan turun.`; parser mengidentifikasi klausa utama dan subordinatif sebagai S-P serta relasi `temporal`. Setelah satu asumsi tes POS yang tidak didukung kontrak parser dihapus, Run #227 sukses dengan 400/400 tes regresi lulus. Run #228 menambahkan tes pipeline untuk klausa sebab pascaposisi `Aku pulang sebab hujan turun.`; kedua klausa dianalisis sebagai S-P dan relasi dicatat sebagai `sebab`. Run #228 sukses dengan 401/401 tes regresi lulus. Run #229 menambahkan tes pipeline untuk klausa sebab di depan `Sebab hujan turun, aku pulang.`; klausa subordinatif dan klausa utama masing-masing dikenali sebagai S-P dengan relasi `sebab`. Run #229 sukses dengan 402/402 tes regresi lulus. Run #230 menambahkan tes pipeline untuk klausa utama bernegasi dengan subordinatif sebab pascaposisi: `Aku tidak pulang karena hujan turun.`; negasi `tidak` tetap menjadi modifier predikat, kedua klausa dikenali sebagai S-P, dan relasi subordinatif `sebab` dipertahankan. Run #230 sukses dengan 403/403 tes regresi lulus. Run #231 menambahkan tes pipeline untuk klausa utama bernegasi dengan subordinatif temporal pascaposisi: `Aku tidak pulang ketika hujan turun.`; `tidak` tetap menjadi modifier negasi, kedua klausa dikenali sebagai S-P, dan relasi subordinatif `temporal` dipertahankan. Run #231 sukses dengan 404/404 tes regresi lulus. Run #232 menambahkan tes pipeline untuk klausa utama bernegasi dengan subordinatif konsesif pascaposisi: `Aku tidak pergi meskipun hujan turun.`; `tidak` tetap menjadi modifier negasi pada predikat klausa utama, kedua klausa dikenali sebagai S-P, dan relasi subordinatif dicatat sebagai `konsesi`. Run #232 sukses dengan 405/405 tes regresi lulus. Run #233 menambahkan variasi posisi depan dengan klausa utama bernegasi: `Meskipun hujan turun, aku tidak pergi.`; klausa subordinatif tetap S-P dengan relasi `konsesi`, sedangkan klausa utama S-P mempertahankan `tidak` sebagai modifier negasi. Run #233 sukses dengan 406/406 tes regresi lulus. Run #234 menambahkan tes pipeline untuk klausa sebab di depan dengan klausa utama bernegasi: `Sebab hujan turun, aku tidak pulang.`; kedua klausa tetap S-P, relasi `sebab` dipertahankan, dan `tidak` tetap menjadi modifier negasi. Run #234 sukses, 407/407 tes regresi lulus. Run #235 menambahkan tes pipeline untuk klausa temporal di depan dengan klausa utama bernegasi: `Ketika hujan turun, aku tidak pulang.`; klausa subordinatif dan klausa utama dikenali sebagai S-P, relasi `temporal` dipertahankan, dan `tidak` tetap menjadi modifier negasi. Run #235 sukses, 408/408 tes regresi lulus. Run #236 menambahkan tes pipeline untuk variasi penanda sebab `karena` di depan: `Karena hujan turun, aku tidak pulang.`; klausa subordinatif dan klausa utama dikenali sebagai S-P, relasi semantis `sebab` dipertahankan, dan `tidak` tetap menjadi modifier negasi. Run #236 sukses, 409/409 tes regresi lulus. Run #237 menambahkan variasi klausa konsesif di depan dengan `walaupun`: `Walaupun hujan turun, aku tidak pulang.`; klausa subordinatif dan klausa utama tetap S-P, relasi `konsesi` dipertahankan, dan `tidak` tetap menjadi modifier negasi. Run #237 sukses, 410/410 tes regresi lulus. Run #238 menambahkan variasi klausa konsesif pascaposisi `Aku tidak pergi walaupun hujan turun.`; kedua klausa dikenali sebagai S-P, relasi `konsesi` dipertahankan, dan `tidak` tetap menjadi modifier negasi. Run #238 sukses, 411/411 tes regresi lulus. Run #239 memperbaiki dukungan relasi `tujuan` untuk subordinator `supaya` pada posisi depan dan belakang; Run #239 sukses, 412/412 tes regresi lulus. Run #240 menambahkan satu kelompok berisi 10 skenario klausa tujuan `supaya` melalui pipeline kamus/POS nyata, mencakup posisi depan/belakang, variasi pronomina, negasi, dan modalitas; Run #240 sukses, 413/413 tes regresi lulus. Run #225 menambahkan dua tes pipeline untuk klausa konsesif penuh dengan `meskipun`, baik setelah klausa utama (`Aku pergi meskipun hujan turun.`) maupun di depan dengan koma (`Meskipun hujan turun, aku pergi.`); kedua klausa dianalisis sebagai S-P dan relasi dicatat sebagai `konsesi`. Run #225 sukses, 399/399 tes regresi lulus.
- [x] Menambahkan 10 skenario integrasi koordinasi klausa melalui pipeline kamus/POS nyata untuk dua konjungsi yang belum memiliki cakupan tes khusus: `atau` sebagai relasi alternatif (lima variasi klausa) dan `tetapi` sebagai relasi pertentangan (lima variasi klausa). Setiap skenario memeriksa dua klausa terurai, subjek dan predikat tiap klausa, serta metadata relasi konjungsi. Run #252 sukses, 426/426 tes regresi lulus. Ini memperluas cakupan koordinasi, tetapi tidak menutup seluruh pekerjaan konstruksi Tahap 2.6.
- [x] Menambahkan 10 tes integrasi untuk koordinasi tiga klausa dengan dua konjungsi berbeda dalam satu rangkaian. Cakupan ini tidak mengulang Run #252 (koordinasi dua klausa `atau`/`tetapi`) maupun tes tiga klausa lama yang hanya memakai `dan` berulang. Sepuluh kombinasi menguji urutan relasi penambahan, alternatif, dan pertentangan; setiap kasus memeriksa sumber/POS konjungsi, tiga klausa, subjek-predikat tiap klausa, serta metadata relasi. Run #255 sukses, 436/436 tes regresi lulus.\n- [x] Menguji pronomina persona melalui pipeline kamus → POS → parser: `aku`, `saya`, `kamu`, `engkau`, `dia`, `mereka`, `kita`, `kami`, `kalian`, `anda`, `beliau`, `ia`, dan `kau` lulus sebagai subjek maupun objek (Run #179, 358/358 tes regresi).
- [~] Melengkapi inventaris pronomina informal/regional lain serta menangani bentuk terikat seperti `-ku`, `-mu`, dan `-nya` melalui morfologi. Fondasi deteksi klitik sudah ditambahkan dan diuji pada `bukuku`, `rumahmu`, `bukunya`, `melihatku`, `melihatmu`, dan `melihatnya` melalui pipeline nyata. POS kini mengekspos komponen POS dasar + PRON untuk klitik, tanpa memaksakan satu POS gabungan atau memilih fungsi posesif/objek (Run #185, 368/368 tes). Parser kini dapat memakai host NOUN yang teridentifikasi untuk mempertahankan bentuk berklitik sebagai frasa nominal dan menetapkan fungsi klitik posesif secara terbatas; diuji end-to-end pada `Dia lihat bukuku.` (Run #190). Parser juga mengenali klitik objek pada host VERB yang POS-nya eksplisit, misalnya `Dia lihatku.`; token tetap satu token predikat, sementara metadata klitik mencatat fungsi objek terikat (Run #195). Untuk `-nya` pada host NOUN, parser mempertahankan ambiguitas antara posesif dan definit/anforis, alih-alih selalu menyebutnya posesif; diuji pada `Dia lihat bukunya.` (Run #198). Run #200 memperluas tes unit dan pipeline nyata untuk ketiga klitik objek verbal melalui `Dia lihatku.`, `Dia lihatmu.`, dan `Dia lihatnya.`; semuanya menghasilkan S-P-O dengan objek terikat dicatat terpisah dalam metadata, total 377/377 tes regresi lulus. Run #201 menambahkan uji pipeline penuh untuk pronomina informal `gue`, `gua`, `gw`, `lu`, `lo`, dan `elu` sebagai subjek maupun objek; keenam bentuk dikenali sebagai PRON dari kamus dan menghasilkan pola S-P-O, total 378/378 tes regresi lulus.  Run #205 menambahkan tes pipeline refleksif `diriku`, `dirimu`, dan `dirinya` sebagai bentuk `diri` + klitik pada posisi objek; host NOUN dikenali, sementara fungsi `-nya` tetap unresolved dan `-ku/-mu` masih dilaporkan sebagai possessive oleh aturan host nominal. Run #205 sukses, 382/382 tes regresi lulus. Ini menguji pengenalan bentuk dan batas perilaku parser saat itu, bukan penyelesaian interpretasi refleksif. Perubahan berikutnya menambahkan metadata kandidat hubungan referensi refleksif hanya ketika subjek pronominal eksplisit cocok dengan orang klitik (`aku/saya` + `-ku`, `kamu/engkau/kau` + `-mu`, `dia/ia/beliau` + `-nya`); relasi final tetap unresolved dan fungsi posesif klitik tetap terpisah. Tes integrasi untuk kecocokan dan ketidakcocokan orang ditambahkan; GitHub Actions Run #210 sukses. Perluasan berikutnya menguji frasa nominal berklitik sebagai subjek; Run #211 sukses dengan 384/384 tes regresi lulus. Run #212 sempat gagal karena contoh `Rumahmu besar.` mengandalkan predikat adjektival dengan subjek nominal berklitik, konstruksi yang memang belum didukung parser; kasus uji diperbaiki menjadi `Bukumu jatuh.` agar mengisolasi dukungan klitik subjek pada klausa verbal. Run #213 sukses dengan 386/386 tes regresi lulus, mencakup `Bukumu jatuh.` untuk `-mu` dan `Bukunya jatuh.` untuk `-nya` sambil mempertahankan ambiguitas fungsi `-nya`. Run #214 menambahkan tes morfologi/pipeline untuk `memilikinya`: bentuk turunan `memiliki` + klitik `-nya` dikenali sebagai satu kandidat dengan dasar `memiliki` dan kecocokan lema turunan `milik`. Run #215 menambahkan tes `perasaanmu`: bentuk turunan nominal `perasaan` + klitik `-mu` dikenali dengan dasar `perasaan` dan kecocokan lema turunan `rasa`. Run #216 menambahkan tes `perasaannya`: bentuk nominal turunan `perasaan` + klitik `-nya` dikenali dengan dasar `perasaan` dan kecocokan lema turunan `rasa`. Run #217 menambahkan tes `memilikiku`: bentuk turunan verbal `memiliki` + klitik `-ku` dikenali dengan dasar `memiliki` dan kecocokan lema turunan `milik`. Run #218 menambahkan tes `memilikimu`: bentuk turunan verbal `memiliki` + klitik `-mu` dikenali dengan dasar `memiliki` dan kecocokan lema turunan `milik`. Run #219 menambahkan tes `perasaanku`: bentuk turunan nominal `perasaan` + klitik `-ku` dikenali dengan dasar `perasaan` dan kecocokan lema turunan `rasa`. Keenam workflow Run #214–219 sukses; Run #219 menjalankan 392 tes regresi. Cakupan representatif untuk ketiga klitik (`-ku`, `-mu`, `-nya`) pada host turunan verbal (`memiliki`) dan nominal (`perasaan`) kini lengkap pada level pengenalan morfologi. Ini belum menyelesaikan seluruh cakupan klitik: inventaris regional, analisis internal frasa nominal, dan interpretasi semantis klitik tetap menjadi pekerjaan tersendiri. Inventaris regional, analisis internal frasa nominal, dan cakupan klitik lainnya tetap belum selesai. Inventaris regional yang belum terwakili, analisis internal frasa nominal, dan cakupan klitik lainnya masih belum selesai. Run #241 menambahkan satu kelompok 10 skenario klitik pada frasa nominal multi-kata: `-ku`, `-mu`, dan `-nya` diuji pada posisi subjek maupun objek melalui pipeline kamus/POS/parser. Metadata peran frasa dipastikan; ambiguitas `-nya` tetap unresolved. Run #241 sukses, 414/414 tes regresi lulus. Analisis inti-pewatas frasa nominal tetap datar dan belum diselesaikan. Run #251 menambahkan lima skenario integrasi untuk bentuk turunan berklitik: `memilikiku`, `memilikimu`, `memilikinya`, `perasaanku`, dan `perasaanmu`. Ketiga bentuk turunan verbal (`memiliki` + klitik) dikenali morfologinya, tetapi host POS masih kosong sehingga parser secara benar mempertahankan status `unresolved`; dua bentuk turunan nominal (`perasaan` + `-ku/-mu`) dikenali sebagai frasa nominal subjek dengan fungsi posesif. Run #251 sukses, 416/416 tes regresi lulus. [Lihat Run #251](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46085818964).
- [x] Menguji enam lema refleksif/demonstratif baru melalui pipeline kamus → POS → parser: `begini` dan `begitu` sebagai ADV; `diri` sebagai NOUN; `ini` dan `itu` sebagai PRON pada contoh demonstratif; serta `sendiri` mempertahankan kandidat ADJ+ADV tanpa pemilihan konteks yang belum didukung. Pengujian membedakan pemakaian adverbial `begini/begitu` dari demonstratif `ini/itu`, dan menjaga ambiguitas `sendiri`. Run #204 sukses, 381/381 tes regresi lulus.
- [x] Mendokumentasikan cakupan baseline, batasan yang belum selesai, dan hasil regresi sebagai dasar penutupan Tahap 2.6. Tahap ditutup atas keputusan pengguna pada 28 November 2026; pekerjaan parsial tidak dianggap selesai secara teknis dan tidak dilanjutkan dengan perluasan pengujian tanpa arahan baru.

**Batas saat ini:** inversi hanya dikenali jika kandidat predikat memiliki satu lema, satu sense, dan satu frame valensi dengan satu argumen SUBJ NP wajib. `Di rumah terdengar suara.` tetap menghasilkan subjek kosong dan `suara` unresolved karena bukti sense/frame yang tersedia belum memenuhi syarat; inversi K-P-S umum, subjek tersirat, serta pembedaan argumen dan adjung pada konstruksi yang lebih luas belum ditangani.

### 2.7 Inventarisasi bukti dan evaluasi pipeline terpadu

<badge color="success">Selesai — baseline pipeline Tahap 2 tercatat</badge>

**Tujuan tahap ini bukan mengulang seluruh pengujian Tahap 2.1–2.6.** Hasil regression test, pengujian pipeline nyata, dataset, dan CI yang sudah tercatat harus diperlakukan sebagai bukti awal. Pengujian yang sudah memiliki bukti memadai tidak perlu dijalankan ulang hanya untuk mengisi checklist.

- [x] Memiliki dataset POS 100 kalimat / 543 token dengan development dan test split.
- [x] Memiliki validator dataset dan evaluasi POS development.
- [x] Memiliki regression suite lintas komponen yang dijalankan melalui GitHub Actions.
- [x] Menginventarisasi 21 berkas pengujian berdasarkan komponen dan jalur pipeline, dua workflow GitHub Actions, serta bukti CI terdahulu; Run #257 diverifikasi dari ringkasan dan log. Tidak ada skenario yang dijalankan ulang.
- [x] Memetakan cakupan yang telah diuji dan batas yang masih diketahui, termasuk perilaku `partial` dan `unresolved`; rinciannya dicatat di dokumen status.
- [x] Mengidentifikasi dan memverifikasi celah integrasi semantic role dengan empat skenario kalimat mentah → kamus aktual → POS/konteks → parser → voice → semantic role. Empat skenario baru lulus pada Run #260 (450/450 tes). Rincian dan batasannya dicatat di dokumen status.
- [x] Meninjau variasi yang relevan dengan celah integrasi: bentuk aktif berimbuhan meN- dan pasif di-, subjek pronominal, objek nominal, agen pascaverbal, serta pasif tanpa agen. Tidak menambah skenario informal/slang/salah ketik/kata ulang karena tidak terkait celah yang sedang diverifikasi.
- [x] Menetapkan expected output empat skenario baru berdasarkan kontrak parser, bukti voice morfologis, dan frame valensi pilot yang tersedia.
- [x] Menyusun dan menjalankan tepat empat skenario integrasi baru yang tidak mengulang tes lama secara identik; cakupan disepakati sebelum implementasi dan CI.
- [x] Mengevaluasi celah integrasi menggunakan empat skenario baru; Run #260 sukses dengan 450/450 tes regresi. Run #258–259 sempat gagal pada ekspektasi tes dan diperbaiki sebelum Run #260; tidak ada pengulangan massal di luar CI otomatis akibat dua commit koreksi.
- [x] Menetapkan baseline dan kriteria kelulusan Tahap 2: Run #260 lulus 450/450 regression tests; empat jalur end-to-end semantic role lulus; POS test split tetap tersegel; status `partial`/`unresolved` diterima hanya sesuai batas bukti dan kontrak yang terdokumentasi. Baseline ini berlaku untuk cakupan yang telah diuji, bukan klaim dukungan seluruh Bahasa Indonesia.

**Penggunaan GitHub Actions:** workflow GitHub Actions boleh dan dapat digunakan untuk menjalankan pengujian/validasi yang diperlukan selama pengembangan. Tidak ada pembatasan karena penghematan kuota. Cakupan tes tetap harus relevan dengan perubahan; hindari pengulangan yang tidak memiliki alasan teknis.

**Gerbang menuju Tahap 3:** bukti Tahap 2.1–2.6 telah diinventarisasi, celah pipeline yang relevan telah dinilai, dan baseline serta batas kemampuan Tahap 2 terdokumentasi. Tahap 2.6 tetap ditutup; keterbatasan teknisnya dicatat sebagai batas baseline, bukan alasan untuk membuka kembali tahap tersebut.

## Tahap 3 — Hubungan makna dan pemrosesan konteks

<badge color="success">Resmi dibuka — audit representasi makna dan relasi konsep</badge>

**Catatan urutan:** beberapa komponen awal Tahap 3 telah dibuat lebih dahulu untuk mendukung pengembangan semantic role. Tahap 3 kini resmi dibuka setelah gerbang Tahap 2.7 terpenuhi, tetapi Tahap 3 sendiri masih dalam tahap awal dan belum selesai. Tahap 2.6 tetap ditutup atas keputusan pengguna; Tahap 2.7 diselesaikan melalui inventarisasi bukti dan evaluasi celah, bukan pengulangan seluruh pengujian sebelumnya.

- [~] Mengembangkan representasi makna kata dan relasi antarkonsep: kontrak v1 disetujui; validator struktural read-only, 19 tes unit terfokus, dan fixture sintetis tersedia. Pilot awal terdiri dari 3 konsep, 3 pemetaan sense, dan 2 relasi; seluruh 8 record telah lolos validasi/review dan berstatus `reviewed`. Referensi `K0201-S1`, `K0399-S1`, dan `K0497-S1` diverifikasi pada batch kamus 004, 008, dan 010. Pembaca baca-saja `tools/concept_layer_loader.py` lulus di Termux (12/12), dan adapter `tools/concept_sense_adapter.py` juga lulus tes terfokus (10/10). Adapter mempertahankan setiap kandidat sense dan melampirkan konsep reviewed tanpa memilih makna atau memakai relasi untuk membuat pemetaan baru. Integrasi ke analyzer/runtime dan pemilihan sense kontekstual belum dilakukan.
- [x] Membuat resolver kandidat semantic role berbasis bukti konteks eksplisit; pemilihan hanya terjadi jika satu frame didukung bukti kuat dan semua alternatif disingkirkan bukti kuat. Resolver tidak membuat bukti konteks sendiri; penghasil bukti kontekstual masih menjadi pekerjaan berikutnya. Run #149: 337/337 tes regresi lulus; Run #152: guard perbandingan argument slot yang sama tervalidasi, 339/339 tes lulus.
- [~] Menentukan cara memilih sense berdasarkan konteks kalimat.
  - [x] Menyetujui kontrak dan membuat modul terpisah `tools/context_evidence_generator.py` untuk mengekstrak observasi serta menghasilkan evidence hanya dari aturan konteks `reviewed`; generator tidak memilih sense dan tidak menetapkan status akhir `ambiguous`/`unresolved`.
  - [x] Menambahkan tepat 10 tes unit khusus dan workflow GitHub Actions terfokus; Run #1 dan #2 terverifikasi lulus 10/10.
  - [x] Menyetujui rancangan `docs/RANCANGAN_CONTEXTUAL_SENSE_SELECTOR.md` dan mengimplementasikan `tools/contextual_sense_selector.py` sebagai modul terpisah. Selector hanya memilih jika satu sense mendapat strong support dan seluruh alternatif mendapat strong contradiction tanpa konflik.
  - [x] Menambahkan tepat 12 tes unit khusus `tests/test_contextual_sense_selector.py` dan workflow terfokus `.github/workflows/contextual-sense-selector-tests.yml`; GitHub Actions Run #3 [46107671664](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46107671664) lulus **12/12 tes**.
  - [x] Menyetujui dan mendokumentasikan batas integrasi Contextual Sense v1 di `docs/KONTRAK_INTEGRASI_CONTEXTUAL_SENSE_V1.md`.
  - [x] Membuat `tools/contextual_sense_integration.py` sebagai orchestrator per kemunculan token dan `tools/context_rules_loader.py` sebagai loader JSONL baca-saja. Orchestrator mempertahankan kandidat/evidence, mengisolasi kelompok token, serta menunda kasus kalimat majemuk, token berulang, dan pemetaan parser yang tidak aman.
  - [x] Menambahkan tepat 10 tes integrasi khusus dan workflow `.github/workflows/contextual-sense-integration-tests.yml`. Run #3 [46108556894](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46108556894) sukses, **10/10 tes lulus**, termasuk satu jalur nyata analyzer → POS → parser → orchestrator. Run #2 sempat gagal pada ekspektasi kapitalisasi token; ekspektasi disesuaikan dengan keluaran analyzer yang ternormalisasi, lalu Run #3 lulus.
  - [~] Inventarisasi 3.025 entri / 60 batch menemukan 9 lema multi-sense; dua kandidat same-POS (`bangun`, `jam`) telah ditinjau awal: tiga aturan tetap `proposed`/`weak`, sedangkan cue `alarm` untuk `jam` S1 ditolak karena tidak cukup spesifik. Tidak ada aturan `reviewed` atau `strong`; rincian tercatat di `docs/INVENTARIS_SENSE_AMBIGU_DAN_KANDIDAT_ATURAN_KONTEKS.md`.
  - [~] Bukti leksikografis/pedoman untuk `bangun` dan `jam` telah dicatat. Penelusuran terbatas ke contoh korpus Leipzig menambah satu contoh relevan untuk `bangun` S1, tetapi belum menemukan bukti pembanding yang jelas untuk `bangun` S2 atau kalimat korpus yang dapat menilai `jam`. Tiga aturan tetap `proposed`/`weak`, satu `rejected`; tidak ada aturan aktif. Rincian dan batas pencarian dicatat di inventaris.
  - [ ] Pemanggilan orchestrator dari entrypoint/runtime aplikasi belum dikerjakan.
- [x] Menggabungkan hasil leksikal, morfologi, POS, dan struktur kalimat melalui modul baca-saja `tools/context_snapshot.py` (`build_context_snapshot`). Snapshot mempertahankan kandidat/status sumber, memetakan peran parser hanya pada token unik, dan menunda token berulang serta kalimat majemuk.
  - [x] Menetapkan kontrak `docs/KONTRAK_REPRESENTASI_KONTEKS_TERPADU_V1.md`.
  - [x] Menambahkan tepat 10 tes khusus, termasuk satu pipeline nyata kamus → analyzer → POS → parser → snapshot; GitHub Actions Run #3 [46110525292](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46110525292) sukses **10/10**.
  - [x] Menambahkan workflow terfokus `.github/workflows/context-snapshot-tests.yml`; tidak menjalankan ulang regression suite 450 tes.
  - [ ] Integrasi snapshot ke entrypoint/runtime belum dikerjakan.
- [~] Menangani ambiguitas dan maksud ujaran secara bertahap. Modul read-only v1 `tools/utterance_interpretation.py` telah dibuat berdasarkan pemetaan Context Snapshot yang diverifikasi; dimensi ambiguity dibatasi pada lexical_sense, POS, dan syntax, sedangkan intent dicatat terpisah. Reference ditunda karena snapshot belum menyediakan struktur resolusinya. Tepat 11 tes khusus pada `tests/test_utterance_interpretation.py` lulus melalui GitHub Actions Run #1 [46114424670](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46114424670). Modul belum terhubung ke runtime; kebijakan klarifikasi dan perluasan pola intent tetap pekerjaan terpisah.
- [ ] Mengelola konteks percakapan beberapa giliran.
- [ ] Menangani nama orang/nama khusus yang sebelumnya di-abstain.
- [ ] Menyediakan mekanisme klarifikasi jika makna atau maksud belum cukup jelas.
- [ ] Menguji kemampuan pemahaman konteks dengan dataset tersendiri.

## Tahap 4 — Mesin aturan dan pembentukan respons

<badge color="secondary">Belum dimulai</badge>

- [ ] Merancang representasi keadaan/dialog dan aturan respons.
- [ ] Menghubungkan hasil pemahaman bahasa dengan pemilihan tindakan atau respons.
- [ ] Membentuk respons yang sesuai konteks menggunakan aturan dan komponen bahasa yang tersedia.
- [ ] Menangani respons ketika informasi tidak cukup, termasuk meminta klarifikasi.
- [ ] Menguji konsistensi, relevansi, dan batas kemampuan respons.

**Catatan:** tahap ini adalah mesin aturan dan pembentukan respons, bukan pelatihan atau pemasangan model LLM/GGUF.

## Tahap 5 — Integrasi Android offline

<badge color="secondary">Belum dimulai</badge>

- [ ] Menentukan arsitektur aplikasi dan antarmuka Android.
- [ ] Mengintegrasikan mesin bahasa dan penyimpanan lokal.
- [ ] Memastikan pemrosesan inti dapat berjalan tanpa koneksi internet.
- [ ] Menguji skenario inti dalam mode pesawat.
- [ ] Menguji instalasi, pemulihan data, dan penanganan kesalahan.

## Tahap 6 — Evaluasi perangkat dan optimasi

<badge color="secondary">Belum dimulai</badge>

- [ ] Mengukur RAM, CPU, baterai, latensi, dan ukuran penyimpanan.
- [ ] Mengidentifikasi bottleneck berdasarkan pengukuran nyata.
- [ ] Mengoptimalkan komponen tanpa merusak hasil regresi.
- [ ] Menguji kestabilan pada perangkat Android sasaran.
- [ ] Menetapkan batas kemampuan dan kebutuhan pengembangan lanjutan.

---

## Keputusan teknis opsional — embedding

Embedding **bukan tahap wajib dan bukan prasyarat** untuk menyelesaikan tahapan utama.

- [ ] Mengukur kekurangan sistem berbasis aturan dan relasi pada kasus nyata.
- [ ] Menyusun kasus uji pembanding.
- [ ] Mengukur manfaat embedding dibanding biaya RAM, penyimpanan, latensi, dan kompleksitas.
- [ ] Memutuskan berdasarkan hasil apakah embedding diperlukan.

## Titik lanjut resmi

Tahap 2.5 dan Tahap 2.6 tetap ditutup. **Tahap 2.7 selesai pada 28 November 2026** setelah inventarisasi 21 berkas tes dan dua workflow, pemetaan cakupan/batas baseline, audit celah pipeline, serta verifikasi tepat empat skenario integrasi end-to-end. Baseline terakhir yang diverifikasi adalah GitHub Actions Run #260 (**450/450 tes regresi lulus**). **Titik lanjut resmi: Tahap 3 — Hubungan makna dan pemrosesan konteks.** Kontrak Concept Layer v1 telah disetujui; validator, fixture, dan pembaca read-only tersedia. Validator 19 kasus telah terverifikasi lulus secara gabungan; pembaca Concept Layer lulus **12/12** dan adapter kandidat sense ke konsep lulus **10/10** di Termux. **Pemisahan pekerjaan:** aktivasi aturan konteks `bangun` dan `jam` diparkir sementara karena bukti belum memadai; ini bukan penghambat Tahap 3 secara keseluruhan. Pertahankan tiga aturan `proposed`/`weak` dan satu `rejected`, jangan mengaktifkannya, dan jangan menghubungkan orchestrator pemilihan sense ke entrypoint/runtime. **Pekerjaan aktif:** lanjutkan rancangan penanganan ambiguitas dan maksud ujaran v1 di [RANCANGAN_AMBIGUITAS_DAN_MAKSUD_UJARAN_V1.md](RANCANGAN_AMBIGUITAS_DAN_MAKSUD_UJARAN_V1.md). Rancangan memisahkan ambiguitas interpretasi dari bentuk komunikatif yang tampak, mempertahankan abstention, dan belum mengubah runtime. Skema keluaran minimal v1 telah diverifikasi terhadap field aktual Context Snapshot dan diperjelas: referensi kandidat memakai indeks sumber (bukan ID rekaan), dimensi reference ditunda karena tidak tersedia, dan intent dipisahkan dari ambiguity. Cakupan implementasi dibatasi tepat 11 tes unit khusus pada modul read-only terpisah; modul read-only v1 dan tepat 11 tes khusus kini telah diimplementasikan; GitHub Actions Run #1 [46114424670](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46114424670) memverifikasi 11/11 tes lulus. Titik lanjut berikutnya adalah merancang kebijakan klarifikasi secara terpisah, tanpa mengintegrasikan modul ini ke runtime atau memperluas pola intent sebelum ada rancangan dan cakupan tes yang dibatasi. Jangan mengubah aturan `bangun`/`jam` yang masih nonaktif. Integrasi snapshot ke entrypoint/runtime tetap menjadi pekerjaan terpisah dan tidak boleh mengaktifkan pemilihan sense tanpa evidence yang memenuhi kontrak. Jangan membuat aturan strong atau status reviewed otomatis; pertahankan batas per kemunculan token dan penundaan kalimat majemuk. Selector v1 telah diimplementasikan dan diverifikasi 12/12 tes pada GitHub Actions Run #3 [46107671664](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46107671664). Generator/selector belum terintegrasi ke runtime; jangan mencampur kandidat dari token berbeda atau mengubah komponen Tahap 1/2 tanpa blocker terverifikasi dan persetujuan. Gunakan tes terfokus dan GitHub Actions sesuai cakupan perubahan; jangan mengulang tes lama tanpa alasan teknis. Jangan mengubah kamus, batch, indeks, validator, parser, POS, morfologi, atau resolver kecuali ada blocker terbukti dan disetujui.

