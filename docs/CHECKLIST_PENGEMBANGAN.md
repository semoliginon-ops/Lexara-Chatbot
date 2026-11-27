# Checklist Pengembangan — Sistem Bahasa

Dokumen ini adalah **peta tahapan dan status pekerjaan proyek**. Checklist menunjukkan urutan kerja, prasyarat, dan titik lanjut. Rincian teknis, riwayat versi, eksperimen, serta log pengujian disimpan di `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.

## Arti status

- [x] Selesai dan sudah diverifikasi.
- [~] Sedang dikerjakan atau sebagian fondasinya sudah tersedia.
- [ ] Belum dikerjakan.
- [!] Terhambat atau perlu keputusan.

## Snapshot proyek — 27 November 2026

- **Tahap aktif: 2.6 — Analisis struktur kalimat dasar.**
- Parser saat ini **v1.9**. Ini nomor versi parser, bukan tanda bahwa seluruh Tahap 2.6 sudah selesai.
- Kamus: **3.025 lema dalam 60 batch**; tidak ada rencana audit ulang batch secara rutin.
- Tahap 2.5 (POS) telah ditutup berdasarkan keputusan pengguna.
- Dataset POS: 100 kalimat / 543 token (60 development, 40 test); test split tetap tersegel.
- Evaluasi POS kontekstual pada development: 250/255 dikenali; coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%. Lima abstention berupa nama orang ditunda ke tahap pengenalan nama/konteks.
- GitHub Actions [Run #203](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46034097778) sukses: validasi kamus 3.025 lema, valensi, dataset POS, evaluasi development, dan **378/378 regression tests lulus**.

## Aturan kerja yang harus dijaga

- Penambahan lema baru ke kamus harus mendapat **persetujuan eksplisit pengguna** sebelum batch sumber maupun indeks diubah.
- Untuk memeriksa apakah lema sudah tersedia, periksa indeks kamus terlebih dahulu. Jangan melakukan audit ulang seluruh batch tanpa alasan yang jelas.
- Parser dan komponen bahasa harus bersikap konservatif: jika bukti belum cukup, tandai unresolved/abstain; jangan menebak fungsi kata.
- Setiap perubahan perilaku harus disertai regression test yang relevan dan pemeriksaan kompatibilitas.
- Kelulusan tes membuktikan perilaku yang diuji, bukan bahwa seluruh bahasa Indonesia sudah tercakup.

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

<badge color="info">Tahap aktif</badge>

**Posisi saat ini: parser v1.9, dengan inversi terbatas berbasis valensi tervalidasi pada Run #222.**

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
- [~] Inversi berbasis valensi mulai didukung secara konservatif. Jika satu token predikat memiliki tepat satu kandidat lema, satu sense, dan satu frame dengan hanya satu argumen `SUBJ` NP wajib, nomina pascaverbal dapat dianalisis sebagai subjek: `Muncul masalah.` → P-S dan `Di rumah muncul masalah.` → K-P-S. Kasus tanpa bukti valensi tunggal tetap unresolved: `Timbul masalah.` dan `Di rumah terdengar suara.`; pola serupa dengan objek dan subjek tersirat (`Di rumah membaca buku.`) juga tidak dipaksakan. Run #222 sukses, 395/395 tes regresi lulus. Run #223 menambahkan tujuh kondisi negatif untuk memastikan parser abstain pada kandidat/sense/frame ambigu, argumen tambahan, subjek opsional, realisasi non-NP, dan kecocokan bentuk turunan; Run #223 sukses, 396/396 tes regresi lulus. Run #224 menambahkan dua tes integrasi untuk frasa subjek pascaverbal dengan pewatas adjektival: `Muncul masalah besar.` → P-S dan `Di rumah muncul masalah besar.` → K-P-S; keduanya mempertahankan `masalah besar` sebagai satu frasa subjek. Run #224 sukses, 397/397 tes regresi lulus. Cakupan ini masih terbatas pada pola positif yang memenuhi syarat frame tersebut, bukan dukungan inversi K-P-S umum. Batas frasa preposisional awal sebelumnya diuji melalui pipeline nyata: Run #182, 359/359 tes.
- [~] Memperluas pengujian konstruksi melalui pipeline kamus/POS nyata; mencakup predikat adjektival `Dia sakit.` (PRON+ADJ → S-P), subjek nominal `Anak makan nasi.` (NOUN+VERB+NOUN → S-P-O), negasi verbal `Aku tidak makan nasi.` (PRON+ADV+VERB+NOUN → S-P-O), serta gabungan negasi dan modalitas `Aku tidak akan makan nasi.` (PRON+ADV+ADV+VERB+NOUN → S-P-O, dengan `tidak` sebagai negasi dan `akan` sebagai modal), serta modalitas verbal `Aku mau makan nasi.` dan `Aku ingin makan nasi.` (modal VERB + verba leksikal → satu rentang predikat, dengan kepala `makan`), dan `Aku bisa makan nasi.` (`bisa` memiliki kandidat POS VERB+NOUN; konteks sebelum verba `makan` memilih VERB, lalu parser membentuk S-P-O dengan kepala `makan`), serta `Aku tidak bisa makan nasi.` (negasi ADV + modal ambigu yang dipilih sebagai VERB berdasarkan verba berikutnya; parser membentuk predikat `tidak bisa makan` dengan kepala `makan`). Run #158: 345/345, Run #159: 346/346, Run #160: 347/347, Run #161: 348/348, Run #162: 349/349, Run #164: 350/350, Run #165: 351/351 tes regresi lulus. Pengujian juga mencakup `Aku mau makan nasi besok.` (modal verbal + objek + keterangan temporal pascapredikat menghasilkan S-P-O-K); Run #166 sukses dengan 352/352 tes regresi lulus. Kombinasi negasi + modal adverb + objek + keterangan temporal pascapredikat juga diuji lewat `Aku tidak akan makan nasi besok.`; Run #167 sukses dengan 353/353 tes regresi lulus. Pengujian juga mencakup modal ambigu `bisa` bersama keterangan temporal `nanti` pada `Aku bisa makan nasi nanti.`; konteks memilih VERB dari kandidat VERB+NOUN dan parser menghasilkan S-P-O-K. Run #169 sukses dengan 354/354 tes regresi lulus. Klausa konsesif setelah klausa utama juga diuji lewat `Aku pergi walaupun hujan turun.`; pipeline mengenali kedua klausa S-P dan relasi `konsesi`. Run #170 sukses dengan 355/355 tes regresi lulus. Variasi posisi klausa konsesif juga diuji: `Walaupun hujan turun, aku pergi.`; klausa subordinatif di depan dikenali sebagai S-P, klausa utama setelah koma sebagai S-P, dengan relasi `konsesi`. Run #171 sukses dengan 356/356 tes regresi lulus. Variasi elipsis konsesif dengan penanda alternatif `meskipun` juga diuji lewat `Meskipun lelah, aku pergi.`; pipeline memverifikasi POS kamus dan menghasilkan klausa awal `P-ELIPTIS` tanpa menebak subjek, sehingga status keseluruhan tetap `partial`. Run #172 sukses dengan 357/357 tes regresi lulus. Variasi konstruksi lain masih perlu ditambahkan. Run #227 menambahkan tes pipeline untuk klausa temporal pascaposisi `Aku pulang ketika hujan turun.`; parser mengidentifikasi klausa utama dan subordinatif sebagai S-P serta relasi `temporal`. Setelah satu asumsi tes POS yang tidak didukung kontrak parser dihapus, Run #227 sukses dengan 400/400 tes regresi lulus. Run #228 menambahkan tes pipeline untuk klausa sebab pascaposisi `Aku pulang sebab hujan turun.`; kedua klausa dianalisis sebagai S-P dan relasi dicatat sebagai `sebab`. Run #228 sukses dengan 401/401 tes regresi lulus. Run #229 menambahkan tes pipeline untuk klausa sebab di depan `Sebab hujan turun, aku pulang.`; klausa subordinatif dan klausa utama masing-masing dikenali sebagai S-P dengan relasi `sebab`. Run #229 sukses dengan 402/402 tes regresi lulus. Run #230 menambahkan tes pipeline untuk klausa utama bernegasi dengan subordinatif sebab pascaposisi: `Aku tidak pulang karena hujan turun.`; negasi `tidak` tetap menjadi modifier predikat, kedua klausa dikenali sebagai S-P, dan relasi subordinatif `sebab` dipertahankan. Run #230 sukses dengan 403/403 tes regresi lulus. Run #231 menambahkan tes pipeline untuk klausa utama bernegasi dengan subordinatif temporal pascaposisi: `Aku tidak pulang ketika hujan turun.`; `tidak` tetap menjadi modifier negasi, kedua klausa dikenali sebagai S-P, dan relasi subordinatif `temporal` dipertahankan. Run #231 sukses dengan 404/404 tes regresi lulus. Run #232 menambahkan tes pipeline untuk klausa utama bernegasi dengan subordinatif konsesif pascaposisi: `Aku tidak pergi meskipun hujan turun.`; `tidak` tetap menjadi modifier negasi pada predikat klausa utama, kedua klausa dikenali sebagai S-P, dan relasi subordinatif dicatat sebagai `konsesi`. Run #232 sukses dengan 405/405 tes regresi lulus. Run #233 menambahkan variasi posisi depan dengan klausa utama bernegasi: `Meskipun hujan turun, aku tidak pergi.`; klausa subordinatif tetap S-P dengan relasi `konsesi`, sedangkan klausa utama S-P mempertahankan `tidak` sebagai modifier negasi. Run #233 sukses dengan 406/406 tes regresi lulus. Run #234 menambahkan tes pipeline untuk klausa sebab di depan dengan klausa utama bernegasi: `Sebab hujan turun, aku tidak pulang.`; kedua klausa tetap S-P, relasi `sebab` dipertahankan, dan `tidak` tetap menjadi modifier negasi. Run #234 sukses, 407/407 tes regresi lulus. Run #225 menambahkan dua tes pipeline untuk klausa konsesif penuh dengan `meskipun`, baik setelah klausa utama (`Aku pergi meskipun hujan turun.`) maupun di depan dengan koma (`Meskipun hujan turun, aku pergi.`); kedua klausa dianalisis sebagai S-P dan relasi dicatat sebagai `konsesi`. Run #225 sukses, 399/399 tes regresi lulus.
- [x] Menguji pronomina persona melalui pipeline kamus → POS → parser: `aku`, `saya`, `kamu`, `engkau`, `dia`, `mereka`, `kita`, `kami`, `kalian`, `anda`, `beliau`, `ia`, dan `kau` lulus sebagai subjek maupun objek (Run #179, 358/358 tes regresi).
- [~] Melengkapi inventaris pronomina informal/regional lain serta menangani bentuk terikat seperti `-ku`, `-mu`, dan `-nya` melalui morfologi. Fondasi deteksi klitik sudah ditambahkan dan diuji pada `bukuku`, `rumahmu`, `bukunya`, `melihatku`, `melihatmu`, dan `melihatnya` melalui pipeline nyata. POS kini mengekspos komponen POS dasar + PRON untuk klitik, tanpa memaksakan satu POS gabungan atau memilih fungsi posesif/objek (Run #185, 368/368 tes). Parser kini dapat memakai host NOUN yang teridentifikasi untuk mempertahankan bentuk berklitik sebagai frasa nominal dan menetapkan fungsi klitik posesif secara terbatas; diuji end-to-end pada `Dia lihat bukuku.` (Run #190). Parser juga mengenali klitik objek pada host VERB yang POS-nya eksplisit, misalnya `Dia lihatku.`; token tetap satu token predikat, sementara metadata klitik mencatat fungsi objek terikat (Run #195). Untuk `-nya` pada host NOUN, parser mempertahankan ambiguitas antara posesif dan definit/anforis, alih-alih selalu menyebutnya posesif; diuji pada `Dia lihat bukunya.` (Run #198). Run #200 memperluas tes unit dan pipeline nyata untuk ketiga klitik objek verbal melalui `Dia lihatku.`, `Dia lihatmu.`, dan `Dia lihatnya.`; semuanya menghasilkan S-P-O dengan objek terikat dicatat terpisah dalam metadata, total 377/377 tes regresi lulus. Run #201 menambahkan uji pipeline penuh untuk pronomina informal `gue`, `gua`, `gw`, `lu`, `lo`, dan `elu` sebagai subjek maupun objek; keenam bentuk dikenali sebagai PRON dari kamus dan menghasilkan pola S-P-O, total 378/378 tes regresi lulus.  Run #205 menambahkan tes pipeline refleksif `diriku`, `dirimu`, dan `dirinya` sebagai bentuk `diri` + klitik pada posisi objek; host NOUN dikenali, sementara fungsi `-nya` tetap unresolved dan `-ku/-mu` masih dilaporkan sebagai possessive oleh aturan host nominal. Run #205 sukses, 382/382 tes regresi lulus. Ini menguji pengenalan bentuk dan batas perilaku parser saat itu, bukan penyelesaian interpretasi refleksif. Perubahan berikutnya menambahkan metadata kandidat hubungan referensi refleksif hanya ketika subjek pronominal eksplisit cocok dengan orang klitik (`aku/saya` + `-ku`, `kamu/engkau/kau` + `-mu`, `dia/ia/beliau` + `-nya`); relasi final tetap unresolved dan fungsi posesif klitik tetap terpisah. Tes integrasi untuk kecocokan dan ketidakcocokan orang ditambahkan; GitHub Actions Run #210 sukses. Perluasan berikutnya menguji frasa nominal berklitik sebagai subjek; Run #211 sukses dengan 384/384 tes regresi lulus. Run #212 sempat gagal karena contoh `Rumahmu besar.` mengandalkan predikat adjektival dengan subjek nominal berklitik, konstruksi yang memang belum didukung parser; kasus uji diperbaiki menjadi `Bukumu jatuh.` agar mengisolasi dukungan klitik subjek pada klausa verbal. Run #213 sukses dengan 386/386 tes regresi lulus, mencakup `Bukumu jatuh.` untuk `-mu` dan `Bukunya jatuh.` untuk `-nya` sambil mempertahankan ambiguitas fungsi `-nya`. Run #214 menambahkan tes morfologi/pipeline untuk `memilikinya`: bentuk turunan `memiliki` + klitik `-nya` dikenali sebagai satu kandidat dengan dasar `memiliki` dan kecocokan lema turunan `milik`. Run #215 menambahkan tes `perasaanmu`: bentuk turunan nominal `perasaan` + klitik `-mu` dikenali dengan dasar `perasaan` dan kecocokan lema turunan `rasa`. Run #216 menambahkan tes `perasaannya`: bentuk nominal turunan `perasaan` + klitik `-nya` dikenali dengan dasar `perasaan` dan kecocokan lema turunan `rasa`. Run #217 menambahkan tes `memilikiku`: bentuk turunan verbal `memiliki` + klitik `-ku` dikenali dengan dasar `memiliki` dan kecocokan lema turunan `milik`. Run #218 menambahkan tes `memilikimu`: bentuk turunan verbal `memiliki` + klitik `-mu` dikenali dengan dasar `memiliki` dan kecocokan lema turunan `milik`. Run #219 menambahkan tes `perasaanku`: bentuk turunan nominal `perasaan` + klitik `-ku` dikenali dengan dasar `perasaan` dan kecocokan lema turunan `rasa`. Keenam workflow Run #214–219 sukses; Run #219 menjalankan 392 tes regresi. Cakupan representatif untuk ketiga klitik (`-ku`, `-mu`, `-nya`) pada host turunan verbal (`memiliki`) dan nominal (`perasaan`) kini lengkap pada level pengenalan morfologi. Ini belum menyelesaikan seluruh cakupan klitik: inventaris regional, analisis internal frasa nominal, dan interpretasi semantis klitik tetap menjadi pekerjaan tersendiri. Inventaris regional, analisis internal frasa nominal, dan cakupan klitik lainnya tetap belum selesai. Inventaris regional yang belum terwakili, analisis internal frasa nominal, dan cakupan klitik lainnya masih belum selesai.
- [x] Menguji enam lema refleksif/demonstratif baru melalui pipeline kamus → POS → parser: `begini` dan `begitu` sebagai ADV; `diri` sebagai NOUN; `ini` dan `itu` sebagai PRON pada contoh demonstratif; serta `sendiri` mempertahankan kandidat ADJ+ADV tanpa pemilihan konteks yang belum didukung. Pengujian membedakan pemakaian adverbial `begini/begitu` dari demonstratif `ini/itu`, dan menjaga ambiguitas `sendiri`. Run #204 sukses, 381/381 tes regresi lulus.
- [ ] Menetapkan kriteria penutupan Tahap 2.6 berdasarkan cakupan pola, batasan yang terdokumentasi, dan hasil regresi.

**Batas saat ini:** inversi hanya dikenali jika kandidat predikat memiliki satu lema, satu sense, dan satu frame valensi dengan satu argumen SUBJ NP wajib. `Di rumah terdengar suara.` tetap menghasilkan subjek kosong dan `suara` unresolved karena bukti sense/frame yang tersedia belum memenuhi syarat; inversi K-P-S umum, subjek tersirat, serta pembedaan argumen dan adjung pada konstruksi yang lebih luas belum ditangani.

### 2.7 Dataset dan pengujian terpadu

<badge color="secondary">Berikutnya — fondasi sebagian tersedia</badge>

- [x] Memiliki dataset POS 100 kalimat / 543 token dengan development dan test split.
- [x] Memiliki validator dataset dan evaluasi POS development.
- [x] Memiliki regression suite lintas komponen yang dijalankan melalui GitHub Actions.
- [ ] Menyusun dataset khusus untuk menguji alur lengkap normalisasi → tokenisasi → kamus → morfologi → POS → parser.
- [ ] Memperluas variasi kalimat: baku, informal, slang, salah ketik, imbuhan, kata ulang, dan struktur kompleks.
- [ ] Menetapkan expected output untuk hasil parser, termasuk partial dan unresolved.
- [ ] Menjalankan evaluasi terpadu tanpa membuka test split untuk penyetelan.
- [ ] Menetapkan baseline dan kriteria kelulusan Tahap 2 secara keseluruhan.

**Gerbang menuju Tahap 3:** Tahap 2.6 dan 2.7 harus memiliki cakupan serta batas yang terdokumentasi dan lolos evaluasi terpadu. Tidak perlu menunggu parser memahami semua kemungkinan kalimat.

## Tahap 3 — Hubungan makna dan pemrosesan konteks

<badge color="info">Fondasi awal dikerjakan lebih awal — belum resmi dibuka</badge>

**Catatan urutan:** beberapa komponen awal Tahap 3 sudah dibuat lebih dahulu untuk mendukung pengembangan semantic role. Ini bukan berarti Tahap 2 selesai atau gerbang Tahap 3 sudah terpenuhi. Tahap 2.6 dan 2.7 tetap harus diselesaikan dan dievaluasi.

- [ ] Mengembangkan representasi makna kata dan relasi antarkonsep.
- [x] Membuat resolver kandidat semantic role berbasis bukti konteks eksplisit; pemilihan hanya terjadi jika satu frame didukung bukti kuat dan semua alternatif disingkirkan bukti kuat. Resolver tidak membuat bukti konteks sendiri; penghasil bukti kontekstual masih menjadi pekerjaan berikutnya. Run #149: 337/337 tes regresi lulus; Run #152: guard perbandingan argument slot yang sama tervalidasi, 339/339 tes lulus.
- [ ] Menentukan cara memilih sense berdasarkan konteks kalimat.
- [ ] Menggabungkan hasil leksikal, morfologi, POS, dan struktur kalimat.
- [ ] Menangani ambiguitas dan maksud ujaran secara bertahap.
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

Pekerjaan dilanjutkan dari **Tahap 2.6 — parser v1.9**. Tahap 2.5 tetap ditutup. Setelah cakupan parser cukup stabil, lanjutkan ke Tahap 2.7 untuk evaluasi pipeline terpadu; setelah gerbang Tahap 2 terpenuhi, barulah masuk ke Tahap 3.

- [x] Pemetaan semantic role pasif konservatif tervalidasi CI: subjek permukaan → argumen OBJ valensi; agen pasif melalui objek pascaverbal atau frasa `oleh`; agen yang tidak disebutkan boleh omitted. Dukungan dibatasi pada frame valensi SUBJ+OBJ dan klausa sederhana. Run #144 sukses (323/323 tes); Run #145 menambahkan dua tes integrasi end-to-end untuk agen pascaverbal dan agen yang dilesapkan, sukses (325/325 tes); Run #147 menambahkan dua guard untuk menolak parser non-SVO atau kepala predikat yang hilang, sukses (327/327 tes); Run #148 menguji konsistensi alternatif AGENT/CAUSER pada kalimat aktif dan pasif melalui pipeline penuh, sukses (328/328 tes).
