# Catatan Teknis — Sistem Bahasa

Dokumen ini menyimpan **keputusan teknis, perilaku komponen, batasan, dan hasil eksperimen penting** agar alasan di balik implementasi tidak hilang.

- **Peta kemajuan dan status tahapan:** [CHECKLIST_PENGEMBANGAN.md](CHECKLIST_PENGEMBANGAN.md)
- **Gambaran proyek:** [README.md](../README.md)
- **Skema dan aturan kamus:** [KAMUS.md](KAMUS.md)
- **Dataset POS:** [DATASET_POS.md](DATASET_POS.md)

Dokumen ini bukan checklist kedua dan bukan sumber utama status tahapan. Perubahan kecil pada checklist tidak mengharuskan dokumen ini ikut diperbarui. Tambahkan catatan di sini jika ada keputusan desain, perubahan perilaku, hasil pengujian penting, atau batasan baru yang perlu dipertahankan.

---

## 1. Ruang lingkup dan prinsip teknis

Sistem Bahasa adalah fondasi pemrosesan Bahasa Indonesia yang dirancang berjalan lokal/offline. Komponen mengolah teks melalui normalisasi, tokenisasi, pencocokan leksikal, morfologi, POS, dan analisis struktur kalimat.

Batas tujuan:
- Bukan LLM dan tidak memuat model GGUF.
- Tidak mengandalkan layanan cloud atau API berbayar untuk pemrosesan inti.
- Belum dapat diklaim memiliki pemahaman atau generasi bahasa bebas setara LLM.
- Kemampuan harus dinilai per komponen, pola, dan data uji yang benar-benar tersedia.

Prinsip implementasi:
- Pertahankan ambiguitas jika bukti belum cukup; abstention lebih baik daripada menebak.
- Jangan mengubah lemma, POS, sense, atau definisi kamus hanya untuk menyesuaikan satu aturan.
- Normalisasi tidak boleh menghapus informasi yang berpotensi mengubah makna.
- Bentuk informal/slang dan tanda baca dipertahankan kecuali ada aturan teruji.
- Perubahan parser harus disertai tes unit dan tes integrasi yang relevan.
- Jaga kompatibilitas antarmuka yang sudah dipakai komponen lain.
- Jangan menggunakan test split untuk menyetel aturan.

## 2. Baseline komponen

| Komponen | Implementasi | Perilaku / batas penting |
|---|---|---|
| Normalisasi | `tools/normalisasi.py` | Unicode NFC, casefold, merapikan whitespace. Tidak membakukan slang, menghapus tanda baca, atau melakukan stemming. |
| Tokenisasi | `tools/tokenizer.py` | Memisahkan kata dan tanda baca; bentuk bertanda hubung/apostrof internal dipertahankan. |
| Loader kamus | `tools/kamus_loader.py` | Membaca batch JSONL dan memvalidasi struktur; data sumber tidak dimodifikasi oleh loader. |
| Pencocokan leksikal | `tools/pencocokan_kamus.py` | Mencocokkan lemma, variants, dan derived_forms; mempertahankan seluruh kandidat/sense/POS. |
| Pipeline teks | `tools/analisis_teks.py` | Menghubungkan normalisasi, tokenizer, dan pencocokan kamus. Indeks leksikal dapat digunakan ulang. |
| Morfologi | `tools/morfologi.py` | Menghasilkan kandidat analisis imbuhan yang divalidasi melalui kamus; bukan stemming bebas. |
| POS | `tools/pos_tagger.py`, `tools/pos_context.py` | POS leksikal dan disambiguasi kontekstual konservatif. Ambiguitas dan abstention dipertahankan. |
| Parser | `tools/parser_kalimat.py` | Analisis struktur kalimat berbasis aturan eksplisit; fitur yang belum didukung tetap unresolved/partial. |

### Kamus dan indeks

- Kondisi yang tercatat pada validasi terbaru: **60 batch, 3.014 lema**.
- Indeks kamus terdiri dari delapan shard alfabet di `data/kamus/index/`.
- Pemeriksaan keberadaan kata baru dilakukan melalui indeks terlebih dahulu.
- Setiap penambahan lema baru wajib mendapat persetujuan eksplisit pengguna. Setelah disetujui, sumber batch dan indeks harus diperbarui bersama.
- Jangan melakukan audit ulang seluruh batch tanpa alasan teknis yang jelas atau permintaan pengguna.

### Morfologi

Morfologi adalah analisis kandidat, bukan pemotongan imbuhan secara membabi buta. Bentuk dasar harus ditemukan di indeks kamus sebelum kandidat dilaporkan. Kata yang sudah cocok persis dengan kamus tidak boleh di-stem.

Cakupan prototipe yang pernah ditambahkan mencakup sejumlah pola prefiks dan konfiks, antara lain bentuk ber-, di-, meN-, peN-, ke-an, per-an, dan bentuk bertingkat tertentu. Cakupan ini **belum merupakan inventaris lengkap morfologi Bahasa Indonesia**.

Tes negatif penting mencegah kata leksikal seperti `beranda`, `kemari`, `terong`, `selalu`, `melati`, `kelapa`, `perang`, `terapi`, dan `mereka` salah dipotong sebagai bentuk berimbuhan. Kasus prefiks bertumpuk `penge-`/`pen-`, lema ambigu, `memperindah`, `memperbaiki`, `mempermainkan`, dan `diperbaiki` juga pernah dimasukkan ke pengujian.

## 3. POS dan dataset

Dataset POS yang tercatat: **100 kalimat / 543 token**, terdiri dari 60 kalimat development dan 40 kalimat test.

Hasil evaluasi development kontekstual pada snapshot Run #126:
- 250 dari 255 token yang dievaluasi dikenali.
- Coverage: 98,0%.
- Accuracy: 98,0%.
- Selective accuracy: 100,0% pada prediksi yang dikeluarkan.
- Lima abstention berkaitan dengan nama orang.

Angka tersebut hanya menggambarkan dataset development yang tersedia, bukan akurasi umum untuk seluruh Bahasa Indonesia. Test split 40 kalimat dipertahankan sebagai data tersegel dan tidak digunakan untuk penyetelan.

Keputusan POS:
- Nama orang ditunda ke tahap pengenalan entitas/konteks; jangan memaksanya menjadi lema kamus atau label POS pada tahap ini.
- POS spesifik-sense dipertahankan.
- POS lema tidak otomatis diwariskan ke bentuk turunan; anotasi POS turunan harus eksplisit jika diperlukan.
- Kata dengan lebih dari satu fungsi POS tidak boleh dipaksa ke satu label tanpa bukti konteks yang memadai.

## 4. Parser kalimat — riwayat kemampuan

Parser dikembangkan bertahap. Nomor versi menunjukkan versi implementasi, **bukan** klaim bahwa seluruh tata bahasa telah tercakup.

| Versi | Penambahan utama |
|---|---|
| v0.1 | Pola klausa dasar S-P, S-P-O, dan S-P-K. |
| v0.2 | Rentang frasa nominal sederhana. |
| v0.3 | Penanganan negasi `tidak` dan `belum`. |
| v0.4 | Pola modal terbatas seperti `mau`, `ingin`, dan `hendak`. |
| v0.5 | Dukungan konservatif untuk predikat nonverbal. |
| v0.6 | Predikat penghubung tertentu, termasuk `menjadi` dan `tampak`, dengan pola S-P-Pel. |
| v0.7–v0.8 | Keterangan preposisional di depan klausa, termasuk beberapa keterangan berurutan. |
| v0.9 | Koordinasi subjek/objek nominal. |
| v1.0–v1.1 | Pemisahan dua atau lebih klausa koordinatif dengan konjungsi eksplisit. |
| v1.2 | Label relasi penghubung yang dikenal, misalnya penambahan, alternatif, pertentangan, sebab, konsesi, urutan, dan temporal. |
| v1.3–v1.5 | Klausa subordinatif di depan dan setelah klausa utama; satu pola konsesif eliptis ditandai `partial`. |
| v1.6 | `predicate_structure` memisahkan kepala predikat dan pewatas; `roles.predicate` dipertahankan demi kompatibilitas. |
| v1.7 | `akan` (ADV) dan `bisa` (VERB) dikenali sebagai modal hanya sebelum verba inti. `bisa` tunggal tetap dapat menjadi predikat. |
| v1.8 | Empat ADV temporal eksplisit (`besok`, `nanti`, `sekarang`, `tadi`) dapat dicatat sebagai keterangan awal. ADV lain tidak otomatis dianggap temporal. |
| v1.9 | Memperketat batas keterangan preposisional awal dan kandidat subjek. Inversi K-P-S penuh belum didukung. |

### Perilaku baseline v1.9 yang harus dipertahankan

1. `Di rumah aku bekerja.`
   - `di rumah` dicatat sebagai keterangan.
   - `aku` tetap menjadi kandidat subjek.
2. `Di rumah terdengar suara.`
   - `di rumah` dicatat sebagai keterangan.
   - `terdengar` dikenali sebagai predikat.
   - Subjek dibiarkan kosong dan `suara` tetap unresolved; jangan dipaksakan menjadi objek atau subjek.
3. Parser tidak mengklaim mendukung inversi K-P-S secara umum.
4. Jika struktur tidak cukup didukung aturan eksplisit, pertahankan status unresolved/partial.
5. Perubahan v1.9 tidak mengubah kamus atau menambah lema.

### Eksplorasi inversi setelah v1.9 — 27 November 2026

- Pipeline leksikal mengidentifikasi `muncul` dan `timbul` sebagai VERB, serta `masalah` sebagai NOUN.
- Entri `muncul` dan `timbul` memiliki definisi/catatan pemakaian yang mendukung makna intransitif seperti mulai hadir, terlihat, atau terjadi.
- Kalimat `Muncul masalah.` dan `Timbul masalah.` berpotensi memperlihatkan pola predikat-verba diikuti subjek nominal (K-P-S), tetapi parser belum memiliki metadata valensi verba atau aturan inversi yang cukup umum.
- Tes integrasi ditambahkan untuk memastikan nomina setelah verba tersebut **tidak otomatis dipaksa menjadi objek atau subjek**. Hasil yang aman saat ini tetap unresolved sampai ada aturan yang dapat membedakan pola intransitif dari pola verba-transitif + objek.
- Tes baru tersebut sudah tersimpan di repository, tetapi belum ada hasil CI yang mengonfirmasi kelulusannya. Jangan menyebutnya tervalidasi sebelum workflow benar-benar dijalankan.

Keputusan sementara: jangan menambahkan daftar verba intransitif hard-coded hanya untuk meloloskan dua contoh. Evaluasi dahulu apakah parser memerlukan fitur valensi/kerangka argumen leksikal yang terstruktur, dan bagaimana fitur itu dapat ditambahkan tanpa mengubah makna atau isi kamus secara spekulatif.

### Rancangan awal metadata valensi verba — catatan historis desain

Bagian ini merekam rancangan sebelum implementasi. Status terkini berada pada bagian **Rancangan skema valensi per-sense — disetujui dan diverifikasi** serta **Anotasi pilot pertama** di bagian akhir dokumen.

1. **Valensi melekat pada sense**, bukan hanya pada lemma. Satu lemma dapat memiliki beberapa sense dan setiap sense dapat memiliki satu atau lebih kerangka argumen.
2. **POS perlu tersedia pada tingkat sense** dalam skema generasi berikutnya. Field `pos` tingkat lemma dapat dipertahankan sebagai gabungan label untuk kompatibilitas; data lama tidak otomatis diberi POS sense baru tanpa peninjauan.
3. Setiap kerangka memisahkan **fungsi sintaksis** (misalnya subjek, objek, pelengkap, atau argumen berpreposisi) dari **peran semantis** (misalnya pelaku, tema, penerima, atau lokasi). Keterangan opsional tidak disamakan dengan argumen inti.
4. Kerangka mencatat apakah argumen wajib atau opsional dan bentuk realisasi yang didukung (misalnya frasa nominal atau frasa preposisional). Urutan permukaan kata tidak dikunci dalam metadata valensi; urutan ditangani parser.
5. Satu sense dapat memiliki beberapa kerangka yang sah. Contohnya, verba tertentu dapat dipakai tanpa objek yang dinyatakan atau dengan objek. Parser tidak boleh memilih salah satu kerangka hanya berdasarkan daftar kata.
6. Metadata valensi hanya menjadi bukti tambahan. Pemilihan sense dan kerangka tetap mempertimbangkan POS, konteks, morfologi/voice, serta struktur kalimat. Jika beberapa analisis masih cocok, hasil harus tetap ambigu/partial/unresolved.

Contoh konseptual (bukan entri kamus baru): sense intransitif `muncul` dapat memiliki argumen inti subjek dengan peran semantis tema; tidak ada objek langsung pada kerangka tersebut. Karena itu, pada `Muncul masalah.`, `masalah` dapat diuji sebagai kandidat subjek pascaverbal, tetapi belum boleh dipastikan sebelum aturan inversi dan tes pembeda tersedia.

**Batas kompatibilitas:** jangan mengubah field `pos`, bentuk entri JSONL, loader, POS tagger, atau parser saat tahap desain ini. Sebelum implementasi, siapkan spesifikasi skema, strategi pembacaan data lama, validasi, contoh positif/negatif, dan tes regresi. Tidak ada lema, POS, definisi, atau metadata kamus yang ditambahkan pada tahap ini.

#### Katalog awal semantic role — disepakati sebagai baseline desain

Pengguna telah menyetujui inventaris awal ini sebagai baseline desain pada 27 November 2026. Daftar berikut sengaja dibatasi; persetujuan ini belum berarti seluruh sense kamus sudah dianotasi atau skema sudah diimplementasikan. Peran semantis menjelaskan kontribusi makna suatu argumen terhadap sense predikat; peran ini **tidak ditentukan hanya dari posisi kata atau fungsi sintaksisnya**. Satu peran dapat muncul pada fungsi sintaksis berbeda, dan satu fungsi sintaksis dapat diisi peran semantis berbeda.

| Kode | Makna ringkas | Contoh ilustratif |
|---|---|---|
| `AGENT` | Pelaku yang secara sengaja/aktif melakukan tindakan. | `Rina` membuka pintu. |
| `EXPERIENCER` | Entitas yang mengalami keadaan psikologis atau persepsi. | `Rina` menyukai musik. |
| `THEME` | Entitas yang bergerak, muncul, berada, berubah, atau menjadi pokok keadaan tanpa penekanan pada dampak langsung. | Masalah muncul; `masalah` = THEME. |
| `PATIENT` | Entitas yang secara langsung dikenai tindakan atau mengalami perubahan/efek yang kuat. | Rina memecahkan `gelas`. |
| `RECIPIENT` | Entitas yang menerima sesuatu atau menjadi tujuan pemindahan kepemilikan/penerimaan. | Rina memberi buku kepada `Doni`. |
| `BENEFICIARY` | Entitas yang memperoleh manfaat atau untuk kepentingannya tindakan dilakukan. | Rina memasak untuk `ibunya`. |
| `INSTRUMENT` | Alat atau sarana yang digunakan untuk melakukan tindakan. | Rina memotong roti dengan `pisau`. |
| `LOCATION` | Tempat berlangsungnya keadaan atau peristiwa. | Rina tinggal di `Bandung`. |
| `SOURCE` | Titik asal atau sumber perpindahan/perolehan. | Rina datang dari `Bogor`. |
| `GOAL` | Tujuan atau titik akhir perpindahan/arah. | Rina pergi ke `pasar`. |
| `RESULT` | Hasil atau keadaan baru yang dihasilkan tindakan/perubahan. | Rina mengubah air menjadi `es`. |
| `CONTENT` | Isi proposisi, pikiran, ucapan, atau informasi yang dinyatakan/dipikirkan. | Rina mengatakan `bahwa ia siap`. |
| `STIMULUS` | Hal yang memicu respons emosi, persepsi, atau pengalaman. | Suara itu mengejutkan `Rina`; suara = STIMULUS. |

**Batas pembedaan yang wajib dijaga**

1. `THEME` dan `PATIENT` tidak boleh digabung. THEME dipakai untuk entitas yang hadir, bergerak, berada, atau menjadi pokok keadaan; PATIENT dipakai jika entitas jelas terdampak tindakan/perubahan. Jika perbedaannya tidak didukung makna sense, jangan menebak.
2. `EXPERIENCER` adalah pihak yang mengalami perasaan/persepsi; `STIMULUS` adalah hal yang memicunya. Keduanya bukan sinonim AGENT.
3. `RECIPIENT` menerima sesuatu; `BENEFICIARY` mendapat manfaat. Seseorang dapat menjadi keduanya dalam konteks tertentu, tetapi labelnya tidak otomatis sama.
4. `SOURCE`, `GOAL`, dan `LOCATION` dibedakan berdasarkan relasi terhadap peristiwa, bukan semata-mata preposisi. Preposisi hanya petunjuk realisasi, bukan definisi peran.
5. `RESULT` adalah hasil yang muncul dari proses; jangan gunakan untuk semua pelengkap predikat.
6. `CONTENT` cocok untuk klausa/isi proposisional. Jangan memberi label ini hanya karena argumen berupa klausa; makna predikat harus mendukungnya.

#### Uji batas THEME vs PATIENT — aturan kerja sementara

Pembedaan ini diputuskan berdasarkan **jenis keterlibatan entitas dalam makna sense predikat**, bukan berdasarkan SUBJ/OBJ, urutan kata, atau bentuk aktif/pasif.

- **THEME**: entitas yang bergerak/berpindah, muncul/hadir, berada, atau menjadi sasaran persepsi/pembahasan, tanpa predikat yang secara jelas menyatakan bahwa entitas itu mengalami perubahan sifat/keadaan atau terkena dampak.
- **PATIENT**: entitas yang secara jelas dikenai tindakan atau mengalami perubahan keadaan/sifat yang dinyatakan oleh predikat. Pelaku boleh ada, tidak ada, atau tidak disebutkan.
- Jika predikat dan konteks tidak cukup membedakan keterlibatan tersebut, jangan memaksakan salah satu label. Tandai belum teranotasi atau pertahankan kandidat alternatif hanya jika dua pembacaan memang sah.

| Kalimat | Kandidat | Analisis sementara | Alasan |
|---|---|---|---|
| Rina memindahkan meja. | meja | THEME | Entitas berpindah lokasi; tindakan tidak dengan sendirinya menyatakan meja berubah sifat/keadaan. |
| Meja dipindahkan Rina. | meja | THEME | Bentuk pasif tidak mengubah peran semantis entitas yang dipindahkan. |
| Rina memecahkan gelas. | gelas | PATIENT | Gelas mengalami perubahan keadaan/keutuhan akibat tindakan. |
| Gelas dipecahkan Rina. | gelas | PATIENT | Peran tetap PATIENT meskipun menjadi subjek gramatikal pasif. |
| Masalah muncul. | masalah | THEME | Entitas mulai hadir/terjadi; bukan objek yang terkena tindakan oleh pelaku. |
| Bola menggelinding. | bola | THEME | Peristiwa menyatakan gerak/perpindahan. |
| Es mencair. | es | PATIENT | Es mengalami perubahan keadaan. |
| Daun menguning. | daun | PATIENT | Daun mengalami perubahan sifat/keadaan. |
| Rina melihat burung. | burung | THEME | Burung adalah entitas yang dipersepsi; tidak dinyatakan terdampak oleh tindakan melihat. |
| Burung itu terlihat oleh Rina. | burung itu | THEME | Perubahan konstruksi/voice tidak menjadikan burung PATIENT. |
| Pintu terbuka. | pintu | Belum diputuskan tanpa sense/konteks | Dapat dibaca sebagai peristiwa perubahan keadaan (PATIENT) atau keadaan/resultatif; label harus mengikuti sense yang tepat. |

**Temuan penting dari uji ini**

1. Batas yang paling berguna untuk baseline adalah **perpindahan/kehadiran/persepsi** (cenderung THEME) versus **perubahan keadaan/sifat atau dampak langsung** (cenderung PATIENT).
2. Jangan menjadikan “ada perubahan” sebagai aturan otomatis untuk PATIENT tanpa melihat jenis perubahan. Perubahan lokasi saja tetap dapat menjadi THEME; perubahan keadaan/sifat yang menjadi inti predikat cenderung PATIENT.
3. Aktif dan pasif tidak mengubah semantic role suatu entitas. Voice memengaruhi realisasi/fungsi sintaksis dan dapat mengubah apakah AGENT dinyatakan, bukan identitas peran entitas lain.
4. Kategori ini adalah pedoman anotasi proyek, bukan klaim bahwa semua teori linguistik memakai batas THEME/PATIENT yang sama. Kasus lintas makna dan resultatif tetap memerlukan peninjauan sense.

**Aturan anotasi konservatif**

- Katalog ini adalah daftar nilai awal yang diizinkan untuk proposal frame, bukan kewajiban mengisi semua peran pada semua sense.
- Satu argumen mendapat satu label utama dalam satu frame. Jika dua interpretasi sama-sama masuk akal, buat frame alternatif hanya bila keduanya benar-benar merupakan pola valensi yang sah; selain itu biarkan belum teranotasi.
- Jangan menyimpulkan semantic role dari `SUBJ`, `OBJ`, `COMP`, atau `OBL` saja. Contoh: subjek pada `Pintu terbuka` adalah THEME/PATIENT sesuai sense dan konstruksi, bukan AGENT.
- Peran tambahan dapat diusulkan kelak jika ditemukan kebutuhan berulang pada data nyata. Jangan memperluas daftar hanya untuk satu kalimat.
- Peran semantis tidak menggantikan anotasi keterangan bebas. Waktu, cara, sebab, frekuensi, dan derajat belum dimasukkan ke katalog argumen inti; penanganannya dapat dirancang sebagai lapisan adjunct terpisah.

Pada saat catatan desain ini pertama ditulis, belum ada sense kamus yang dianotasi dan belum ada validator. Perkembangan implementasi setelahnya dicatat pada bagian akhir dokumen: validator struktural telah dibuat, empat sense pilot telah dianotasi, dan tes integrasi awal telah dijalankan. Parser belum otomatis memilih semantic role atau menangani pemetaan voice pasif.

#### Uji AGENT vs EXPERIENCER vs STIMULUS — dan kandidat celah CAUSER

Pembedaan kerja:

- **AGENT**: pelaku yang mengendalikan atau secara sengaja melakukan tindakan. Jangan berikan AGENT hanya karena entitas menjadi subjek atau menjadi penyebab fisik.
- **EXPERIENCER**: entitas yang mengalami persepsi, emosi, sensasi, atau keadaan psikologis.
- **STIMULUS**: entitas/peristiwa yang menjadi isi sasaran atau pemicu pengalaman tersebut. Role ini hanya digunakan jika makna predikat memang menghubungkan argumen dengan pengalaman.
- **Ketiadaan AGENT** adalah hasil yang sah. Kalimat tidak wajib memiliki pelaku yang disebutkan.

| Kalimat uji | Argumen | Role sementara | Catatan |
|---|---|---|---|
| Rina membuka pintu. | Rina | AGENT | Pelaku tindakan terkendali. |
| Pintu dibuka Rina. | Rina | AGENT | Frasa pelaku pasif mempertahankan role semantis. |
| Pintu dibuka. | tidak ada argumen pelaku yang dinyatakan | AGENT tidak dinyatakan | Jangan menciptakan AGENT implisit sebagai argumen teramati. |
| Rina menyukai musik. | Rina | EXPERIENCER | Mengalami keadaan afektif. |
| Musik disukai Rina. | Rina | EXPERIENCER | Perubahan susunan/voice tidak mengubah role Rina. |
| Rina takut pada petir. | Rina | EXPERIENCER | Pihak yang mengalami rasa takut. |
| Petir menakuti Rina. | petir | STIMULUS | Pemicu pengalaman takut. |
| Petir menakuti Rina. | Rina | EXPERIENCER | Pihak yang mengalami rasa takut. |
| Rina dikejutkan suara keras. | Rina | EXPERIENCER | Pihak yang mengalami kejutan. |
| Suara keras mengejutkan Rina. | suara keras | STIMULUS | Pemicu pengalaman. |
| Rina mendengar musik. | Rina | EXPERIENCER | Pihak yang mengalami persepsi auditori. |
| Musik terdengar oleh Rina. | musik | THEME atau STIMULUS menurut sense | Jangan otomatis menganggap musik sebagai AGENT atau PATIENT. Rina adalah EXPERIENCER. |

**Celah yang ditemukan: penyebab non-agentif**

Bandingkan:

- Rina memecahkan kaca dengan palu. — Rina = AGENT; kaca = PATIENT; palu = INSTRUMENT.
- Angin memecahkan kaca. — kaca = PATIENT, tetapi angin tidak melakukan tindakan dengan kehendak. Memberi label AGENT pada angin akan mengaburkan perbedaan pelaku dan penyebab fisik.
- Hujan membanjiri jalan. — hujan merupakan penyebab non-agentif; jalan/area terdampak adalah PATIENT atau entitas terdampak sesuai sense.

Katalog baseline 13 role belum memiliki label umum yang jelas untuk **CAUSER** (penyebab non-agentif). STIMULUS tidak boleh dipakai sebagai label serba-guna untuk semua sebab: STIMULUS khusus relasi dengan pengalaman/persepsi/emosi, sedangkan CAUSER akan mencakup penyebab suatu peristiwa atau perubahan.

**Uji lanjutan kandidat CAUSER**

Contoh pembeda tambahan:

| Kalimat | Analisis kandidat | Hasil uji |
|---|---|---|
| Rina membuka pintu. | Rina = AGENT | Pelaku tindakan terkendali. |
| Angin membuka pintu. | angin = CAUSER | Penyebab fisik yang tidak bertindak dengan kehendak. |
| Rina membuka pintu dengan kunci. | Rina = AGENT; kunci = INSTRUMENT | Sarana tindakan tidak sama dengan penyebab mandiri. |
| Suara keras mengejutkan Rina. | suara = STIMULUS; Rina = EXPERIENCER | Sebab yang memicu pengalaman psikologis tetap STIMULUS. |
| Gempa meruntuhkan gedung. | gempa = CAUSER; gedung = PATIENT | Penyebab peristiwa fisik, bukan pelaku berkehendak. |
| Obat menurunkan demam. | obat = kandidat CAUSER; demam = entitas terdampak | Perlu sense predikat yang tepat; jangan menyamakan semua penyebab dengan INSTRUMENT. |
| Air mengalir dari gunung. | gunung = SOURCE | Asal gerak bukan penyebab gerak. |
| Pintu terbuka karena angin. | karena angin = keterangan sebab | Penyebab dapat hadir sebagai adjunct, bukan selalu argumen inti. |
| Angin membuka pintu. | angin = kandidat CAUSER sebagai argumen | Contoh yang lebih kuat untuk kebutuhan role pada frame predikat. |

**Pembedaan argumen dan adjunct**

Keberadaan frasa sebab seperti karena angin tidak otomatis membuktikan bahwa setiap predikat membutuhkan slot CAUSER. Pada kalimat Pintu terbuka karena angin, frasa sebab dapat dianalisis sebagai adjunct yang menerangkan alasan terjadinya peristiwa. Sebaliknya, pada Angin membuka pintu, angin menempati posisi argumen yang dipilih/dilisensikan oleh konstruksi predikat kausatif tersebut. Parser dan skema valensi harus membedakan keduanya.

**Evaluasi sementara**

1. CAUSER tidak dapat disamakan dengan AGENT: penyebab tidak harus memiliki kehendak atau kontrol.
2. CAUSER tidak dapat disamakan dengan INSTRUMENT: alat/sarana biasanya digunakan oleh pelaku, sedangkan penyebab fisik dapat menjadi sumber terjadinya peristiwa tanpa pelaku.
3. CAUSER tidak dapat disamakan dengan STIMULUS: STIMULUS dibatasi pada relasi dengan pengalaman/persepsi/emosi; CAUSER menjangkau peristiwa fisik dan perubahan keadaan.
4. CAUSER tidak dapat disamakan dengan SOURCE: SOURCE menandai asal perpindahan, bukan sebab terjadinya peristiwa.
5. CAUSER dapat menjadi argumen inti pada konstruksi tertentu atau muncul sebagai adjunct sebab pada konstruksi lain. Peran semantis dan status argumen/adjunct harus dicatat terpisah.

**Rekomendasi desain (belum menjadi keputusan resmi):** bukti contoh lintas predikat menunjukkan kebutuhan representasi CAUSER sebagai kandidat role tersendiri. Namun katalog resmi tetap 13 role sampai pengguna menyetujui ekstensi. Jika disetujui, definisi kerja yang disarankan: entitas atau peristiwa yang secara non-agentif menyebabkan terjadinya suatu peristiwa atau perubahan keadaan pada entitas lain. Label ini tidak digunakan untuk pelaku berkehendak (AGENT), sarana (INSTRUMENT), pemicu pengalaman psikologis (STIMULUS), atau asal perpindahan (SOURCE).

#### Matriks uji konseptual semantic role

Matriks ini dipakai untuk menguji konsistensi definisi role sebelum membuat validator. Label adalah target analisis konseptual, bukan keluaran parser yang sudah berjalan.

| Kalimat uji | Kandidat argumen | Role yang diuji | Tujuan / jebakan |
|---|---|---|---|
| Rina membuka pintu. | Rina | AGENT | Pelaku tindakan aktif. |
| Pintu dibuka Rina. | pintu | PATIENT | Subjek pasif tidak otomatis AGENT. |
| Pintu terbuka. | pintu | THEME atau PATIENT sesuai sense/konstruksi | Jangan memutuskan hanya dari posisi SUBJ. |
| Masalah muncul. | masalah | THEME | Kasus penting untuk valensi intransitif dan kandidat subjek pascaverbal. |
| Rina menyukai musik. | Rina | EXPERIENCER | Pengalami keadaan psikologis. |
| Suara keras mengejutkan Rina. | suara keras | STIMULUS | Pemicu pengalaman, bukan AGENT otomatis. |
| Rina memberi buku kepada Doni. | Doni | RECIPIENT | Penerima benda. |
| Rina memasak untuk ibunya. | ibunya | BENEFICIARY | Penerima manfaat, bukan otomatis RECIPIENT. |
| Rina memotong roti dengan pisau. | pisau | INSTRUMENT | Sarana tindakan. |
| Rina tinggal di Bandung. | Bandung | LOCATION | Lokasi keadaan. |
| Rina datang dari Bogor. | Bogor | SOURCE | Titik asal perpindahan. |
| Rina pergi ke pasar. | pasar | GOAL | Titik tujuan perpindahan. |
| Rina mengubah air menjadi es. | es | RESULT | Hasil perubahan. |
| Rina mengatakan bahwa ia siap. | bahwa ia siap | CONTENT | Isi proposisi/ucapan. |

**Kasus negatif / pembatas**

- Pada `Rina memecahkan gelas dengan palu`, `gelas` adalah PATIENT dan `palu` INSTRUMENT; jangan memberi keduanya AGENT hanya karena keduanya terkait tindakan.
- Pada `Doni menerima buku dari Rina`, `Doni` adalah RECIPIENT, sedangkan `Rina` adalah SOURCE dalam sense penerimaan yang sesuai; jangan mengandalkan preposisi saja tanpa memeriksa predikat.
- Pada `Rina berada di rumah`, `rumah` adalah LOCATION, bukan GOAL hanya karena muncul setelah preposisi `di`.
- Pada `Rina bekerja besok`, `besok` adalah keterangan waktu, bukan semantic role argumen inti dalam katalog ini.
- Pada `Rina berlari dengan cepat`, `dengan cepat` menyatakan cara/derajat, bukan INSTRUMENT.
- Pada `Rina melihat burung`, jangan otomatis menetapkan burung sebagai PATIENT; THEME lebih aman sebagai kandidat awal kecuali definisi sense dan skema anotasi menetapkan pembedaan lain.

Hasil matriks ini mendukung definisi awal, tetapi belum menyelesaikan seluruh batas THEME/PATIENT atau seluruh konstruksi. Khusus `Pintu terbuka`, label harus ditentukan berdasarkan sense verba dan interpretasi konstruksi; jika bukti leksikal belum cukup, anotasi tetap belum diputuskan. Sebelum implementasi, kasus-kasus tersebut perlu diperluas dengan variasi pasif, kausatif, verba persepsi, verba gerak, dan sense polisemi.

#### Usulan bentuk data konkret (proposal, belum menjadi skema aktif)

Metadata ditempatkan di dalam objek sense sebagai `valency_frames`. Satu sense boleh memiliki beberapa frame. Contoh berikut bersifat ilustratif dan tidak boleh disalin menjadi data kamus tanpa tinjauan entri yang bersangkutan.

```json
{
  "sense_id": "contoh-S1",
  "definition": "Contoh makna verba",
  "pos": ["VERB"],
  "valency_frames": [
    {
      "frame_id": "F1",
      "arguments": [
        {
          "syntactic_role": "SUBJ",
          "semantic_role": "THEME",
          "required": true,
          "realization": ["NP"]
        }
      ]
    }
  ]
}
```

Aturan field yang diusulkan:

- `sense_id`: ID stabil sense yang sudah ada.
- `pos`: POS untuk sense tersebut. Ini usulan bagi skema generasi berikutnya; bukan instruksi mengisi POS sense untuk seluruh data lama sekarang.
- `valency_frames`: array kerangka argumen yang didukung untuk sense itu. Jika belum ditinjau, field tidak ada atau statusnya belum diketahui; jangan mengartikan ketiadaan metadata sebagai verba tidak memiliki argumen.
- `frame_id`: ID unik di dalam sense.
- `arguments`: argumen inti pada kerangka tersebut.
- `syntactic_role`: fungsi sintaksis, dengan kode awal yang dibatasi seperti `SUBJ`, `OBJ`, `COMP`, dan `OBL`.
- `semantic_role`: peran makna seperti `AGENT`, `THEME`, `EXPERIENCER`, `RECIPIENT`, atau `RESULT`. Daftar ini perlu dikembangkan dan divalidasi, bukan diasumsikan lengkap.
- `required`: apakah argumen wajib untuk kerangka itu. Argumen opsional tetap berbeda dari keterangan bebas.
- `realization`: bentuk frasa yang dapat mengisi argumen, misalnya `NP`, `PP`, `ADJP`, atau `CLAUSE`.
- `prepositions`: opsional, untuk membatasi preposisi jika peran OBL direalisasikan sebagai PP. Tidak digunakan untuk mengunci urutan kata.

Contoh ilustratif beberapa jenis frame:

```json
{
  "sense_id": "contoh-muncul-S1",
  "pos": ["VERB"],
  "valency_frames": [
    {
      "frame_id": "F1",
      "arguments": [
        {
          "syntactic_role": "SUBJ",
          "semantic_role": "THEME",
          "required": true,
          "realization": ["NP"]
        }
      ]
    }
  ]
}
```

```json
{
  "sense_id": "contoh-makan-S1",
  "pos": ["VERB"],
  "valency_frames": [
    {
      "frame_id": "F1",
      "arguments": [
        {
          "syntactic_role": "SUBJ",
          "semantic_role": "AGENT",
          "required": true,
          "realization": ["NP"]
        },
        {
          "syntactic_role": "OBJ",
          "semantic_role": "THEME",
          "required": false,
          "realization": ["NP"]
        }
      ]
    }
  ]
}
```

```json
{
  "sense_id": "contoh-memberi-S1",
  "pos": ["VERB"],
  "valency_frames": [
    {
      "frame_id": "F1",
      "arguments": [
        {
          "syntactic_role": "SUBJ",
          "semantic_role": "AGENT",
          "required": true,
          "realization": ["NP"]
        },
        {
          "syntactic_role": "OBJ",
          "semantic_role": "THEME",
          "required": true,
          "realization": ["NP"]
        },
        {
          "syntactic_role": "OBL",
          "semantic_role": "RECIPIENT",
          "required": false,
          "realization": ["PP"],
          "prepositions": ["kepada", "ke"]
        }
      ]
    }
  ]
}
```

Catatan penting:
1. `Muncul masalah.` baru dapat menjadi kandidat pola verba + subjek pascaverbal jika frame sense `muncul` yang tepat mendukung SUBJ bertema THEME dan parser memiliki aturan urutan inversi yang diuji. Metadata valensi sendiri tidak mengesahkan urutan K-P-S.
2. Frame `makan` dengan OBJ opsional tidak berarti setiap nomina setelah `makan` otomatis objek. Kandidat harus cocok dengan struktur, konteks, dan sense.
3. Keterangan seperti waktu/tempat tidak dimasukkan sebagai argumen inti kecuali ada alasan leksikal yang kuat.
4. Voice aktif/pasif, kontrol/pelesapan subjek, dan urutan permukaan ditunda sebagai lapisan terpisah. Jangan menyimpulkan semuanya dari frame dasar.
5. Data lama tanpa `valency_frames` harus dibaca sebagai **belum dianotasi**, bukan sebagai frame kosong atau bukti bahwa verba tidak memiliki valensi.
6. Implementasi nantinya harus tetap bisa memuat entri lama, mempertahankan `pos` tingkat lema, dan tidak mengubah hasil parser lama ketika metadata belum tersedia.

Sebelum skema disahkan, validasi perlu memastikan peran sintaksis dan realisasi termasuk nilai yang diizinkan, `required` berupa boolean, `frame_id` unik di dalam sense, dan preposisi hanya dipakai untuk realisasi PP.

### Kontrak kompatibilitas

- Field lama `roles.predicate` harus tetap tersedia meskipun struktur predikat terperinci ditambahkan.
- `predicate_structure` menyediakan kepala predikat dan modifier yang dikenali tanpa menghilangkan urutan token.
- Jangan mengubah hasil yang sudah dipakai komponen lain tanpa tes regresi yang memeriksa kompatibilitas.

## 5. Hasil validasi terpadu yang menjadi bukti baseline

GitHub Actions [Run #126](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45972629322) berstatus **completed / success**.

Cakupan yang divalidasi pada run tersebut:
- Validasi kamus: 60 batch / 3.014 lema.
- Validasi dataset POS.
- Evaluasi POS development.
- Regression suite: **255/255 tes lulus**.

Run #125 sebelumnya gagal setelah perubahan batas keterangan awal karena pronomina ikut tertelan ke dalam frasa preposisional. Perbaikannya mempertahankan pronomina orang sebagai kandidat subjek; Run #126 kemudian berhasil. Catatan ini penting sebagai alasan mengapa perilaku v1.9 diuji secara khusus.

Kelulusan Run #126 membuktikan tes yang tercakup dalam workflow tersebut lulus pada commit yang diuji. Itu bukan bukti bahwa semua kata, semua konstruksi sintaksis, atau seluruh tata bahasa telah tervalidasi.

## 6. Batasan yang diketahui

- Morfologi masih berupa prototipe berbasis pola dan kamus, belum mencakup seluruh variasi morfofonemik, reduplikasi, dan imbuhan.
- POS kontekstual diuji pada dataset terbatas; nama orang masih ditunda.
- Parser merupakan parser aturan terbatas, bukan parser tata bahasa lengkap.
- Inversi K-P-S penuh belum didukung.
- Relasi penghubung hanya diklasifikasikan jika termasuk daftar eksplisit; relasi semantik yang lebih dalam belum dipahami.
- Klausa eliptis, koordinasi bertingkat, dan struktur ambigu tertentu tetap dapat menghasilkan unresolved/partial.
- Tahap hubungan makna/konteks, mesin pembentukan respons, integrasi Android offline, dan evaluasi perangkat merupakan pekerjaan roadmap terpisah.

## 7. Cara memperbarui dokumen ini

Perbarui dokumen ini hanya jika ada hal teknis yang layak menjadi catatan kesinambungan, misalnya:
- keputusan desain atau perubahan kontrak antarmodul;
- penambahan kemampuan parser/morfologi/POS beserta batasnya;
- hasil regresi penting atau kegagalan yang menghasilkan pelajaran teknis;
- perubahan arsitektur atau keterbatasan yang perlu diketahui saat melanjutkan proyek.

Untuk perubahan status tahap, centang dan perbarui **CHECKLIST_PENGEMBANGAN.md**. Jangan menyalin seluruh checklist ke dokumen ini.

#### Keputusan resmi: CAUSER sebagai semantic role ke-14 — 27 November 2026

Pengguna menyetujui penambahan `CAUSER` sebagai role ke-14 dalam katalog semantic role. Katalog baseline kini berisi 14 role: `AGENT`, `CAUSER`, `EXPERIENCER`, `THEME`, `PATIENT`, `RECIPIENT`, `BENEFICIARY`, `INSTRUMENT`, `LOCATION`, `SOURCE`, `GOAL`, `RESULT`, `CONTENT`, dan `STIMULUS`.

**Definisi CAUSER:** entitas atau faktor yang menyebabkan suatu kejadian/perubahan tanpa bertindak sebagai pelaku yang berkehendak. Gunakan hanya ketika argumen itu memang berfungsi sebagai penyebab non-agentif dalam makna sense predikat.

Contoh pembeda:
- `Rina membuka pintu.` → Rina = `AGENT` (pelaku berkehendak).
- `Angin membuka pintu.` → angin = `CAUSER` (penyebab non-agentif).

**Batas yang wajib dijaga:**
1. `CAUSER` tidak menggantikan `AGENT`, `INSTRUMENT`, `STIMULUS`, atau `SOURCE`. Alat/sarana tetap `INSTRUMENT`; pemicu pengalaman psikologis/persepsi tetap `STIMULUS`; titik asal perpindahan tetap `SOURCE`.
2. Jangan memberi `AGENT` hanya karena entitas berada pada posisi SUBJ atau menjadi sebab fisik. Kehendak/kontrol tindakan harus didukung oleh makna sense.
3. Argumen inti berbeda dari keterangan sebab tambahan: `Angin membuka pintu.` menempatkan angin sebagai argumen penyebab pada predikat; `Pintu terbuka karena angin.` menyatakan sebab melalui frasa/klausa sebab tambahan. Keduanya tidak boleh disamakan secara otomatis dalam analisis struktur.
4. Jangan memberi `CAUSER` pada setiap frasa yang menyatakan sebab. Penetapan role hanya berlaku bila penyebab merupakan argumen dalam kerangka sense predikat yang sedang dianalisis.
5. Jika perbedaan AGENT/CAUSER atau argumen/adjunct tidak didukung oleh sense dan konstruksi, pertahankan ambiguitas atau status belum teranotasi.

Persetujuan ini mengesahkan nilai role pada tingkat desain. Belum ada sense kamus yang dianotasi, belum ada metadata valensi yang ditambahkan ke data, dan belum ada validator atau perilaku parser yang diubah. Implementasi tetap menunggu spesifikasi skema dan pengujian lanjutan.

#### Uji batas CAUSER lintas jenis predikat — 27 November 2026

Setelah CAUSER disahkan sebagai role ke-14, dilakukan uji konseptual untuk mencegah pemakaian terlalu luas. Hasil berikut adalah pedoman anotasi desain; bukan anotasi sense kamus atau hasil evaluasi parser.

| Kalimat uji | Argumen/keterangan | Analisis kerja | Alasan/batas |
|---|---|---|---|
| Rina membuka pintu. | Rina | AGENT | Pelaku mengendalikan tindakan. |
| Angin membuka pintu. | Angin | CAUSER | Penyebab fisik non-agentif dalam pembacaan biasa. |
| Gempa meruntuhkan gedung. | Gempa | CAUSER | Peristiwa alam menjadi penyebab kejadian fisik. |
| Batu memecahkan kaca. | Batu | CAUSER | Penyebab fisik; bukan pelaku berkehendak. |
| Rina memecahkan kaca dengan palu. | Rina; palu | AGENT; INSTRUMENT | Rina melakukan tindakan; palu adalah sarana yang dipakai. |
| Palu memecahkan kaca. | Palu | Belum diputuskan tanpa konteks/frame | Dapat dipahami sebagai alat dengan pelaku tersirat atau sebagai penyebab mekanis yang diperlakukan sebagai CAUSER. Jangan otomatis memilih. |
| Angin bertiup. | Angin | THEME/kandidat argumen sesuai frame, bukan otomatis CAUSER | Predikat menyatakan gerak/keadaan angin; tidak ada akibat lain yang disebabkan dalam klausa. |
| Air mengalir. | Air | THEME/kandidat argumen sesuai frame, bukan otomatis CAUSER | Entitas bergerak; tidak otomatis menjadi penyebab. |
| Air mengikis batu. | Air | CAUSER | Air menjadi daya penyebab perubahan pada batu dalam pembacaan ini. |
| Suara keras mengejutkan Rina. | Suara keras; Rina | STIMULUS; EXPERIENCER | Suara memicu pengalaman psikologis, bukan CAUSER untuk kejadian fisik. |
| Bau itu membuat Rina mual. | Bau itu; Rina | STIMULUS; EXPERIENCER sebagai analisis awal | Respons yang dipicu berupa pengalaman/sensasi; periksa sense dan kerangka predikat sebelum anotasi final. |
| Panas melelehkan es. | Panas | CAUSER | Faktor fisik menyebabkan perubahan keadaan. |
| Hujan membuat jalan licin. | Hujan | CAUSER | Hujan menjadi argumen penyebab pada konstruksi kausatif. |
| Jalan menjadi licin karena hujan. | karena hujan | Keterangan sebab (adjunct), bukan otomatis CAUSER | Sebab dinyatakan sebagai keterangan tambahan, bukan argumen inti predikat utama. |
| Pintu terbuka karena angin. | karena angin | Keterangan sebab (adjunct), bukan otomatis CAUSER | Sama-sama menyatakan sebab, tetapi realisasi sintaksisnya berbeda dari argumen CAUSER pada contoh kausatif. |

**Aturan hasil uji:**

1. CAUSER ditentukan oleh fungsi semantisnya terhadap sense predikat, bukan oleh ciri benda mati, posisi subjek, atau fakta bahwa sesuatu mendahului akibat.
2. Entitas non-manusia tidak otomatis CAUSER. Pada predikat gerak/keadaan seperti “angin bertiup” dan “air mengalir”, entitas dapat menjadi THEME sesuai frame sense.
3. Bedakan argumen penyebab yang dipilih/dilisensikan predikat dari keterangan sebab bebas. Kehadiran kata “karena” merupakan petunjuk konstruksi keterangan sebab, bukan bukti CAUSER.
4. INSTRUMENT adalah sarana yang dipakai dalam tindakan; CAUSER adalah faktor penyebab kejadian. Jika konteks tidak membedakan alat dengan penyebab mekanis (misalnya “Palu memecahkan kaca”), jangan memaksakan label.
5. STIMULUS dibatasi pada pemicu pengalaman psikologis/perseptual/sensasional. Penyebab perubahan fisik seperti panas yang melelehkan es lebih tepat diuji sebagai CAUSER.
6. AGENT memerlukan bukti kontrol/kehendak yang didukung sense dan konteks. Jangan menyimpulkan AGENT hanya dari subjek atau verba aktif.
7. Jika predikat, sense, atau konstruksi belum cukup untuk membedakan role, anotasi boleh ditunda/abstain.

**Kesimpulan:** contoh lintas predikat mendukung CAUSER sebagai role tersendiri dan menunjukkan batas penggunaannya. Namun, kasus alat/penyebab mekanis serta konstruksi kausatif tertentu tetap memerlukan pemeriksaan sense dan kerangka argumen. Katalog 14 role tetap menjadi baseline yang disetujui; belum ada sense kamus yang dianotasi dan belum ada implementasi kode.



#### Rancangan skema valensi per-sense — disetujui dan diverifikasi

Rancangan ini telah disetujui pengguna pada 27 November 2026 sebagai dasar implementasi skema valensi per-sense. Validator struktural tersedia di `tools/validasi_valensi.py` dengan 15 tes khusus di `tests/test_validasi_valensi.py`. GitHub Actions Run #129 berhasil: validasi valensi pada 60 batch / 3.014 entri lulus dan seluruh 273 tes regresi lulus. Data kamus, loader, dan parser tidak diubah.

**Lokasi metadata**

- Metadata ditempatkan di dalam objek sense, melalui field opsional `valency_frames`.
- Field yang tidak ada pada entri lama berarti **belum dianotasi**, bukan berarti sense tersebut tidak memiliki argumen.
- Satu sense dapat memiliki nol, satu, atau beberapa frame yang sudah dianotasi. Beberapa frame diperlukan jika satu sense memiliki pola argumen yang berbeda.
- Valensi hanya mencatat argumen yang dilisensikan oleh sense predikat. Keterangan bebas seperti waktu, cara, dan sebab tambahan tidak dimasukkan sebagai argumen valensi.

**Bentuk data yang diusulkan**

```json
{
  "sense_id": "memberi-S1",
  "pos": ["VERB"],
  "valency_frames": [
    {
      "frame_id": "F1",
      "arguments": [
        {
          "argument_id": "A1",
          "syntactic_role": "SUBJ",
          "semantic_role": "AGENT",
          "required": true,
          "realizations": [
            { "type": "NP" }
          ]
        },
        {
          "argument_id": "A2",
          "syntactic_role": "OBJ",
          "semantic_role": "THEME",
          "required": true,
          "realizations": [
            { "type": "NP" }
          ]
        },
        {
          "argument_id": "A3",
          "syntactic_role": "OBL",
          "semantic_role": "RECIPIENT",
          "required": true,
          "realizations": [
            { "type": "PP", "prepositions": ["kepada", "ke"] }
          ]
        }
      ]
    }
  ]
}
```

**Arti field**

| Field | Aturan proposal |
|---|---|
| `valency_frames` | Daftar frame untuk satu sense. Field boleh tidak ada pada data lama yang belum dianotasi. |
| `frame_id` | ID unik di dalam satu sense; tidak harus unik global. |
| `arguments` | Daftar argumen inti yang dilisensikan frame. |
| `argument_id` | ID unik di dalam satu frame agar argumen dapat dirujuk dalam pengembangan berikutnya. |
| `syntactic_role` | Salah satu dari `SUBJ`, `OBJ`, `COMP`, `OBL`. Ini fungsi sintaksis, bukan semantic role. |
| `semantic_role` | Salah satu dari 14 role yang disetujui. Nilai `null` hanya boleh dipakai jika fungsi semantis argumen memang belum dapat diputuskan; artinya belum teranotasi, bukan role baru. |
| `required` | Boolean: apakah argumen merupakan bagian wajib dari frame secara leksikal/semantis. Ini tidak berarti argumen harus selalu tampak di permukaan; pelesapan, voice, dan kontrol ditangani oleh lapisan terpisah. |
| `realizations` | Satu atau lebih bentuk sintaksis yang dapat merealisasikan argumen pada frame tersebut. |
| `realizations[].type` | Salah satu dari `NP`, `PP`, `ADJP`, `CLAUSE`. |
| `realizations[].prepositions` | Opsional dan hanya sah untuk `PP`; membatasi preposisi jika sense memang mensyaratkannya. Tidak adanya daftar berarti belum ada pembatasan preposisi yang dicatat, bukan bahwa semua preposisi pasti cocok. |

**Katalog nilai sintaksis dan semantis**

- Fungsi sintaksis awal: `SUBJ`, `OBJ`, `COMP`, `OBL`.
- Realisasi awal: `NP`, `PP`, `ADJP`, `CLAUSE`.
- Semantic role: tepat 14 nilai baseline yang sudah disetujui: `AGENT`, `CAUSER`, `EXPERIENCER`, `THEME`, `PATIENT`, `RECIPIENT`, `BENEFICIARY`, `INSTRUMENT`, `LOCATION`, `SOURCE`, `GOAL`, `RESULT`, `CONTENT`, `STIMULUS`.

**Aturan interpretasi yang diusulkan**

1. Satu sense boleh memiliki beberapa frame. Frame alternatif tidak boleh dibuat hanya untuk menampung ketidakpastian analisis satu kalimat.
2. Argumen opsional tetap dapat dicatat dalam frame dengan `required: false`. Jika perbedaan pola lebih tepat direpresentasikan sebagai dua frame, gunakan dua frame; jangan menduplikasi keduanya tanpa alasan.
3. Urutan permukaan tidak disimpan di frame. Parser menentukan urutan dan realisasi aktual berdasarkan struktur kalimat.
4. Role semantis tidak diturunkan otomatis dari fungsi sintaksis. SUBJ dapat berperan sebagai AGENT, CAUSER, THEME, PATIENT, atau EXPERIENCER sesuai sense; OBJ tidak otomatis PATIENT.
5. `prepositions` membatasi realisasi PP yang memang disyaratkan oleh sense. Preposisi sendiri tidak menentukan semantic role.
6. Frame hanya berisi argumen inti. Frasa seperti `karena hujan` tidak otomatis menjadi argumen CAUSER; harus dibuktikan bahwa sense predikat melisensikan argumen tersebut.
7. Metadata yang belum tersedia tidak boleh ditafsirkan sebagai frame kosong atau bukti bahwa suatu argumen tidak mungkin ada.

**Contoh konseptual untuk pengujian (bukan anotasi kamus)**

- Sense intransitif `muncul`:  satu frame dengan `SUBJ / THEME / required=true / NP`. Ini memberi dasar untuk menguji `Muncul masalah.` sebagai kandidat subjek pascaverbal, tetapi belum mengesahkan inversi secara otomatis.
- Sense `memberi`: frame dengan `SUBJ / AGENT`, `OBJ / THEME`, dan `OBL / RECIPIENT` yang direalisasikan sebagai PP dengan preposisi yang sesuai.
- Sense `makan`:  dapat diuji dengan argumen OBJ / THEME opsional atau frame alternatif tanpa OBJ, bergantung pada analisis leksikal yang diputuskan. Jangan menganggap semua verba transitif memiliki pola opsional yang sama.

**Validasi yang harus dibuat sebelum skema diaktifkan**

- Tipe `valency_frames`, `arguments`, dan `realizations` harus berupa array; objek wajib memiliki field yang disyaratkan.
- `frame_id` unik dalam satu sense; `argument_id` unik dalam satu frame.
- `syntactic_role`, `semantic_role`, dan tipe realisasi harus berasal dari katalog yang diizinkan; `semantic_role` boleh `null` hanya untuk anotasi yang belum diputuskan.
- `required` harus boolean.
- `prepositions` hanya boleh muncul pada realisasi `PP`, dan jika hadir harus berupa daftar string nonkosong yang tidak duplikat.
- Satu argumen dapat memiliki beberapa tipe realisasi, tetapi setiap objek realisasi harus valid dan tidak duplikat.
- Field tambahan yang tidak dikenal harus ditolak atau ditangani secara eksplisit; jangan diam-diam mengubah data.
- Data lama tanpa `valency_frames` harus tetap lolos validasi dan tetap dapat dimuat tanpa perubahan perilaku.

**Cakupan yang sengaja ditunda**

Voice aktif/pasif, pelesapan argumen di permukaan, kontrol, raising, urutan kata, konstruksi inversi, argumen implisit, serta penanda klausa yang lebih rinci belum dimasukkan ke skema awal. Semua itu perlu lapisan aturan dan pengujian tersendiri agar metadata valensi tidak menjadi terlalu rumit atau menyatakan hal yang belum didukung bukti.

**Status implementasi pada tahap validator:** skema disetujui pengguna; validator struktural dan 15 tes khusus tersedia. Run #129 menguji 60 batch / 3.014 entri dan 273 tes regresi. Validasi ini memeriksa struktur, bukan kebenaran linguistik anotasi. Anotasi pilot dan tes integrasi berikutnya telah diselesaikan secara bertahap; lihat catatan Run #130 dan #131 di bawah.

**Anotasi pilot pertama — 4 sense (27 November 2026):** setelah persetujuan pengguna, metadata valensi dimasukkan pada empat sense yang sudah ada:
- `muncul` / `K1475-S1`: satu frame, SUBJ/THEME.
- `lihat` / `K0034-S1`: SUBJ/EXPERIENCER dan OBJ/THEME.
- `buka` / `K0065-S1`: dua frame alternatif dengan struktur sintaktis sama, masing-masing SUBJ/AGENT atau SUBJ/CAUSER; OBJ/PATIENT.
- `makan` / `K0013-S1`: SUBJ/AGENT; OBJ/PATIENT dengan `required: false`.

Anotasi ini terbatas pada empat sense tersebut. Dua frame `buka` memodelkan alternatif peran semantis pada posisi SUBJ; objek pada `makan` dinyatakan opsional. Run #130 berhasil: validasi valensi 60 batch / 3.014 entri lulus dan 273 tes regresi lulus.

**Tes integrasi pilot — Run #131 (27 November 2026):** lima tes baru ditambahkan di `tests/test_valency_pilot_integration.py`. Cakupan: (1) anotasi THEME pada `muncul` tidak membuat parser memaksakan analisis `Muncul masalah.` yang masih unresolved; (2) struktur S-P-O `lihat` sesuai dengan anotasi EXPERIENCER/THEME; (3) dua frame `buka` (AGENT dan CAUSER) tetap dipertahankan karena pola sintaksisnya sama dan parser belum boleh memilih role semantis dari posisi SUBJ; (4) `makan` menerima pola S-P tanpa objek dan S-P-O dengan objek; (5) parser membedakan susunan permukaan aktif dan pasif tanpa mengklaim pemetaan semantic role pasif. Run #131 sukses dengan **278/278 tes regresi lulus**.

**Batas yang masih berlaku:** tes aktif/pasif baru memeriksa struktur permukaan; pemetaan PATIENT ke subjek pasif dan AGENT ke frasa pelaku belum diimplementasikan. Pembedaan CAUSER versus INSTRUMENT pada kasus ambigu juga belum menjadi keputusan otomatis. Parser tidak diubah pada pekerjaan ini; yang ditambahkan adalah tes integrasi. Tidak ada penambahan lema atau perubahan anotasi kamus setelah persetujuan empat sense.

**Lapisan pemetaan semantic role aktif — Run #132 (27 November 2026):** dibuat modul terpisah `tools/pemetaan_peran_semantis.py`. Modul menerima hasil parser, satu sense yang sudah dipilih, dan konfirmasi voice dari pemanggil. Pemetaan hanya berjalan bila voice secara eksplisit dikonfirmasi sebagai aktif dan parser berstatus `parsed`. Frame yang cocok dipetakan dari SUBJ/OBJ/COMP/OBL ke semantic role; argumen opsional yang tidak muncul dicatat sebagai `omitted`; batas preposisi pada OBL dihormati. Jika beberapa frame cocok (seperti `buka` AGENT/CAUSER), semua kandidat dikembalikan dengan status `ambiguous`, bukan dipilih otomatis. Jika voice belum diketahui, voice pasif, parser unresolved/partial, atau tidak ada frame yang cocok, modul abstain atau mengembalikan status incompatible.

Run #132 sukses dengan **289/289 tes regresi lulus**. Sebelas tes baru mencakup pemetaan `lihat`, ambiguitas `buka`, objek opsional `makan`, penahanan pemetaan saat voice tidak diketahui/pasif, inversi unresolved, argumen wajib yang hilang, dan pencocokan OBL berdasarkan preposisi.

**Batas implementasi:** modul ini tidak memilih sense; sense harus dipasok oleh lapisan sebelumnya. Konfirmasi voice aktif juga harus datang dari pemanggil, bukan ditebak dari parser v1.9. Pemetaan voice pasif, pemilihan otomatis AGENT vs CAUSER, dan pembedaan CAUSER vs INSTRUMENT masih belum diterapkan. Parser inti tidak diubah.


**Penguatan batas pemetaan semantic role — Run #134 (27 November 2026):** dua celah konservatisme pada mapper diperbaiki tanpa mengubah parser atau data kamus.

1. Sebuah frame tidak lagi dianggap cocok jika parser sudah mengenali SUBJ/OBJ/COMP pada permukaan, tetapi frame tersebut sama sekali tidak memodelkan salah satu fungsi sintaksis yang hadir. Ini mencegah frame intransitif yang hanya memiliki SUBJ mengabaikan OBJ yang sudah dikenali parser.
2. Argumen OBL tidak dipetakan jika realisasi PP tidak memiliki daftar preposisi pembatas yang eksplisit. Parser saat ini masih menggabungkan PP argumen dan PP keterangan dalam daftar adjuncts; karena itu, PP tanpa batas leksikal yang jelas tidak cukup aman untuk dipromosikan menjadi argumen inti.

Dua regression test baru ditambahkan pada `tests/test_pemetaan_peran_semantis.py`: (a) frame tanpa OBJ ditolak ketika parser mengenali objek; (b) OBL dengan PP tanpa batas preposisi tidak dipetakan otomatis. Implementasi berada di `tools/pemetaan_peran_semantis.py`, tetap terpisah dari parser.

GitHub Actions **Run #134** sukses: validasi kamus 60 batch / 3.014 entri, validasi metadata valensi, dataset POS, evaluasi development, dan **291/291 tes regresi lulus**. [Lihat Run #134](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46003126203).

**Batas yang tetap berlaku:** pemeriksaan ini meningkatkan keamanan pencocokan frame, tetapi belum membuat parser mampu membedakan semua argumen PP dari adjunct. OBL hanya dipetakan bila preposisinya dibatasi secara eksplisit; ini adalah kebijakan konservatif sementara. Pemilihan sense, konfirmasi voice, pemetaan pasif, dan pembedaan otomatis AGENT/CAUSER atau CAUSER/INSTRUMENT tetap belum tersedia. Tidak ada batch kamus, indeks, lema, anotasi sense, atau parser inti yang diubah.


**Uji batas CAUSER versus INSTRUMENT — Run #135 (27 November 2026):** dua tes tambahan dibuat tanpa menambah anotasi kamus.

1. Kalimat ilustratif `Palu memecahkan kaca` diuji dengan dua frame sintetis yang memiliki struktur sintaksis sama tetapi role SUBJ berbeda (CAUSER atau INSTRUMENT). Mapper harus mengembalikan `ambiguous` dan mempertahankan kedua kandidat. Fixture ini hanya menguji perilaku mapper; bukan anotasi baru untuk sense `memecahkan`.
2. Pada `Rina memecahkan kaca dengan palu`, frasa `dengan palu` diperlakukan sebagai keterangan yang belum dilisensikan sebagai argumen inti dalam frame uji. Mapper tidak boleh menambahkan role INSTRUMENT hanya berdasarkan keberadaan PP tersebut.

Run #135 sukses dengan **293/293 tes regresi lulus**; validasi 60 batch / 3.014 entri dan langkah CI lainnya juga sukses. [Lihat Run #135](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46003321891).

**Interpretasi batas:** tes ini memastikan sistem mempertahankan ambiguitas bila dua frame memang disediakan dan tidak mengubah semua PP `dengan` menjadi INSTRUMENT. Tes ini tidak menyelesaikan pemilihan CAUSER/INSTRUMENT di konteks nyata, tidak menambah sense kamus, dan tidak mengklaim parser sudah mengenali semua keterangan alat.


#### Deteksi voice morfologis konservatif — Run #136 (27 November 2026)

Modul baru `tools/deteksi_voice.py` menyediakan fungsi `detect_voice(morphology_candidates)`. Modul ini sengaja terpisah dari parser dan semantic-role mapper; tidak mengubah hasil parser atau memanggil mapper secara otomatis.

**Aturan awal yang diimplementasikan:**

- Kandidat dengan rule `prefix_di` (termasuk kombinasi `prefix_di+...`) ditandai sebagai bukti voice pasif, hanya jika kandidat lema yang cocok memiliki POS VERB.
- Kandidat dengan rule `prefix_meN`, `prefix_memper`, atau restorasi nasal aktif `meng-/meny-/men-/mem-` ditandai sebagai bukti voice aktif, hanya jika kandidat lema yang cocok memiliki POS VERB.
- `ter-`, `ber-`, bentuk tanpa penanda yang dikenali, dan kandidat non-VERB tidak dipaksa menjadi voice aktif/pasif.
- Jika kandidat morfologi verbal memberi bukti aktif dan pasif sekaligus, hasilnya `ambiguous`, bukan dipilih otomatis.
- Hasil `identified` berarti ada bukti pola morfologis pada kandidat lema VERB; bukan jaminan bahwa seluruh konstruksi sintaksis, makna, atau voice kalimat sudah dipahami.

**Tes khusus** di `tests/test_deteksi_voice.py` mencakup di- pasif, kombinasi di- bertingkat, meN-/memper-/nasal-restoration aktif, penahanan ter-/ber-, bentuk tidak dikenal, kandidat non-VERB, bukti yang bertentangan, dan validasi tipe input.

GitHub Actions **Run #136** sukses: validasi kamus 60 batch / 3.014 entri dan **304/304 tes regresi lulus**. [Lihat Run #136](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46007374655).

**Batas penting:** detektor ini baru menerima keluaran morfologi per token. Ia belum memilih token yang benar-benar menjadi kepala predikat, belum memeriksa konstruksi kalimat, belum terhubung ke `analyze_text`/parser, dan belum mengubah pemetaan semantic role pasif. Awalan `di-` dan `meN-` adalah bukti morfologis untuk kandidat voice, bukan pengganti analisis sintaksis dan konteks.


#### Integrasi bukti voice pada analisis token — Run #137 (27 November 2026)

Detektor dari Run #136 kini dipanggil oleh `tools/analisis_teks.py` untuk setiap token kata. Keluaran token mempertahankan field lama dan menambahkan `voice_analysis`, yang berisi status, label voice bila teridentifikasi, alasan, bukti rule morfologi, dan catatan batas. Token tanda baca tidak berubah.

Tes integrasi di `tests/test_analisis_teks.py` memastikan:
- `ditulis` menghasilkan bukti voice pasif;
- `menulis` menghasilkan bukti voice aktif;
- `terbuka` tetap unresolved, bukan dipaksa pasif;
- struktur keluaran lama (normalisasi, tokenisasi, pencocokan, dan kandidat morfologi) tetap tersedia.

GitHub Actions **Run #137** sukses: validasi kamus 60 batch / 3.014 entri dan **307/307 tes regresi lulus**. [Lihat Run #137](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46007550098).

**Batas integrasi:** `voice_analysis` adalah bukti morfologis per token, bukan voice kalimat. Modul belum memilih kepala predikat; kata berimbuhan yang bukan predikat juga dapat memiliki bukti morfologisnya sendiri. Parser dan semantic-role mapper belum mengonsumsi field ini. Integrasi berikutnya perlu mengaitkan bukti pada kepala predikat yang sudah dikenali, lalu menahan hasil bila ada lebih dari satu kandidat atau struktur belum jelas.


### Penghubung bukti voice token dengan kepala predikat

Modul `tools/hubungkan_voice_predikat.py` menghubungkan hasil `voice_analysis` per token dari `analyze_text()` dengan `predicate_structure.head` dari parser. Adapter ini sengaja tidak mengubah parser v1.9 maupun bentuk keluaran lama.

Batas implementasi awal:
- Hanya menerima hasil parser `conservative_svo_v4` dengan status `parsed`.
- Kepala predikat harus ditemukan tepat satu kali sebagai token kata pada hasil analisis teks.
- Bukti voice token harus berstatus `identified` dan berisi label `active` atau `passive`.
- Hasil parser `partial`, struktur koordinasi/subordinasi, kepala predikat yang berulang/tidak ditemukan, dan bukti voice yang belum pasti menghasilkan `unresolved`.
- Adapter belum mengubah atau memetakan semantic role. Integrasi pemetaan pasif merupakan pekerjaan berikutnya setelah penghubung ini tervalidasi.

Sembilan tes khusus mencakup voice aktif/pasif, token kepala berulang, parser partial, struktur klausa majemuk, bukti voice unresolved, kepala tidak ditemukan, serta validasi input. GitHub Actions Run #138 mengonfirmasi seluruh 316/316 tes regresi lulus dan validasi kamus 60 batch / 3.014 entri berhasil. Hasil ini memvalidasi adapter dan regresi proyek, bukan akurasi voice untuk seluruh bahasa Indonesia.


Uji integrasi lintas modul kemudian ditambahkan pada `tests/test_voice_pipeline_integration.py`. Tiga skenario memakai keluaran morfologi nyata dari `analyze_text()`, parser klausa sederhana, dan adapter: `Rina menulis surat` terhubung sebagai aktif; `Surat ditulis Rina` terhubung sebagai pasif; dan `Pintu terbuka` tetap unresolved karena bukti `ter-` tidak menetapkan voice. GitHub Actions Run #139 sukses dengan **319/319 tes regresi**. Ini membuktikan koneksi antarmodul pada contoh terkontrol, belum membuktikan cakupan voice umum.


### Pemetaan semantic role pasif — implementasi awal menunggu validasi CI

`tools/pemetaan_peran_semantis.py` kini memiliki jalur pasif konservatif yang terpisah dari pemetaan aktif. Jalur ini hanya berjalan jika pemanggil memasok `voice="passive"` yang sudah dikonfirmasi oleh penghubung bukti voice dan parser berstatus `parsed`.

Aturan terbatas:
- Subjek permukaan pasif dipetakan ke argumen OBJ pada frame valensi (misalnya PATIENT).
- Agen dapat direalisasikan sebagai objek pascaverbal pada pola `Pintu dibuka Rina`, atau sebagai frasa PP dengan preposisi `oleh` pada `Pintu dibuka oleh Rina`.
- Jika agen tidak disebutkan (`Pintu dibuka`), argumen SUBJ valensi ditandai `omitted`; kewajiban argumen aktif tidak otomatis memaksa agen muncul dalam konstruksi pasif.
- Bila agen muncul sekaligus dalam dua bentuk, atau ada lebih dari satu realisasi agen yang tidak dapat diselaraskan, hasil `unresolved`.
- Semua frame yang cocok tetap dipertahankan. Untuk pilot `buka-S1`, AGENT dan CAUSER tetap ambigu; sistem tidak memilih salah satunya hanya dari posisi.
- Hanya frame dengan satu argumen SUBJ dan satu OBJ yang didukung. Konstruksi pasif lain, klausa majemuk, dan pola yang belum dipahami tetap di luar cakupan.

Tes unit ditambahkan untuk agen pascaverbal, frasa `oleh`, agen yang dilesapkan, dan konflik realisasi. Tes integrasi juga mengalirkan bukti morfologi pasif nyata dari `analyze_text()` melalui parser dan adapter ke mapper. GitHub Actions Run #144 sukses dengan **323/323 tes regresi**. Tes integrasi memastikan voice pasif hasil morfologi nyata mengalir ke mapper; hasil untuk `buka-S1` tetap ambigu antara AGENT dan CAUSER.


Validasi CI Run #144: **323/323 tes lulus**. Tes mencakup pemetaan pasif dengan agen pascaverbal, agen berfrasa `oleh`, agen yang dilesapkan, konflik dua realisasi agen, dan integrasi voice pasif dari analisis morfologi sampai semantic-role mapper. Validasi kamus penuh tetap mencakup 60 batch / 3.014 lema. Keberhasilan ini hanya memvalidasi pola terbatas yang diuji; belum berarti semua konstruksi pasif bahasa Indonesia sudah tertangani.


Uji integrasi diperluas pada Run #145 untuk dua pola tambahan: `Pintu dibuka Rina` (agen pascaverbal) dan `Pintu dibuka` (agen tidak disebutkan). Keduanya menggunakan voice pasif yang dideteksi dari analisis morfologi nyata, dihubungkan ke kepala predikat parser, lalu dipetakan melalui frame valensi. Run #145 sukses dengan **325/325 tes regresi**. Pola ini tetap dibatasi pada klausa sederhana dan frame pilot yang tersedia.


Pengamanan tambahan pada Run #147: jalur pemetaan pasif kini hanya menerima parser klausa sederhana `conservative_svo_v4` dan wajib memiliki `predicate_structure.head`. Parser non-SVO atau hasil tanpa kepala predikat ditolak sebagai `unresolved`, sekalipun pemanggil memasok `voice="passive"`. Dua tes guard ditambahkan. Run #147 sukses dengan **327/327 tes regresi**.


Uji konsistensi lintas voice pada Run #148 memakai pasangan `Angin membuka pintu` dan `Pintu dibuka angin`. Keduanya melewati analisis morfologi, parser, penghubung voice, dan mapper. Kedua konstruksi tetap mempertahankan kandidat AGENT dan CAUSER tanpa pemilihan otomatis. Run #148 sukses dengan **328/328 tes regresi**.


### Resolver kandidat semantic role berbasis bukti konteks

Dibuat `tools/resolusi_peran_semantis.py` sebagai lapisan terpisah setelah pemetaan valensi. Fungsi `resolve_semantic_role_candidates()` menerima hasil mapper dan daftar bukti konteks terstruktur.

Kontrak bukti:
- Mengikat bukti ke `frame_id`, `argument_id`, dan `semantic_role` yang benar-benar ada pada kandidat.
- Bukti memiliki `polarity` (`supports` atau `contradicts`), `strength` (`strong` atau `weak`), dan `source`.
- Bukti lemah, tidak cocok, atau tidak lengkap tidak dapat memilih frame.
- Frame dipilih hanya jika tepat satu kandidat mendapat bukti kuat yang mendukung dan semua kandidat alternatif mendapat bukti kuat yang menentang **untuk argument slot yang sama**. Bukti pada argumen berbeda tidak boleh digabung untuk memilih frame.
- Dukungan tanpa penyingkiran alternatif, bukti yang saling bertentangan, atau tidak adanya bukti mempertahankan status `ambiguous`.
- Modul tidak menebak tipe entitas dari ejaan kata. Ia juga tidak menghasilkan bukti konteks sendiri; lapisan pengenal entitas/peristiwa dan interpretasi konteks masih perlu dibangun.

Sembilan tes menguji tanpa bukti, dukungan sepihak, bukti pembeda lengkap, bukti lemah, konflik, bukti tidak cocok, format bukti invalid, hasil yang sejak awal tidak ambigu, dan jaminan input tidak dimutasi. GitHub Actions Run #149 sukses dengan **337/337 tes regresi**.


Pengamanan resolver diperketat: dukungan dan penolakan terhadap alternatif harus membandingkan `argument_id` yang sama. Bukti untuk argumen berbeda tidak boleh digabung untuk membuat keputusan frame. Dua tes tambahan memastikan bukti lintas-slot tidak menghasilkan pilihan palsu dan keputusan kuat yang saling bertentangan tetap ambiguous. GitHub Actions Run #152 sukses dengan **339/339 tes regresi**.


### Klarifikasi urutan tahap — 27 November 2026

Tahap 2.6 dan 2.7 **belum selesai** dan gerbang Tahap 2 menuju Tahap 3 belum terpenuhi. Beberapa pekerjaan semantic role dan konteks dikerjakan lebih awal sebagai fondasi teknis, sehingga secara urutan ada pekerjaan Tahap 3 yang mendahului penutupan Tahap 2. Ini tidak boleh ditafsirkan sebagai Tahap 2 telah selesai.

Koreksi checklist: pemetaan semantic role pasif sebenarnya telah selesai dan tervalidasi melalui Run #144–148 (hingga 328/328 tes), sehingga item tersebut sekarang dicentang. Pekerjaan Tahap 2.6 yang masih terbuka mencakup perluasan pola parser terkontrol, pola inversi K-P-S, uji konstruksi lebih luas dengan pipeline nyata, dan kriteria penutupan. Tahap 2.7 masih membutuhkan dataset pipeline lengkap, variasi kalimat, expected output termasuk partial/unresolved, evaluasi terpadu dengan test split tetap tersegel, serta baseline dan kriteria kelulusan.

Resolver konteks semantic role yang dibuat pada Run #149 dan diperketat pada Run #152 adalah **fondasi awal**. Resolver menerima bukti konteks terstruktur; penghasil bukti otomatisnya belum ada. Karena itu Tahap 3 belum dinyatakan resmi dimulai.


### Perluasan keterangan temporal pascapredikat — Run #154 (27 November 2026)

Parser kini dapat mengenali empat adverbia temporal eksplisit (`besok`, `nanti`, `sekarang`, `tadi`) bukan hanya sebelum subjek, tetapi juga setelah predikat atau objek. Pola yang diuji mencakup klausa intransitif (`Aku bekerja besok.`) dan transitif (`Aku makan nasi nanti.`). Adverbia lain tidak otomatis dianggap temporal; token ADV yang tidak termasuk daftar tetap unresolved/partial. Perubahan dilakukan pada `tools/parser_kalimat.py`, dengan tes unit pada `tests/test_parser_kalimat.py` dan tes pipeline kamus lengkap pada `tests/test_integrasi_pipeline.py`.

Workflow regresi sebelumnya belum terpicu oleh perubahan parser karena path parser dan tes integrasi belum tercantum pada filter workflow. Path tersebut ditambahkan ke `.github/workflows/pos-validation.yml` agar perubahan parser berikutnya menjalankan suite penuh. Run #153 sempat gagal pada dua tes baru karena pemindaian kandidat objek melewati ADV temporal; pemindaian diperbaiki agar ADV dapat diperiksa oleh tahap keterangan. Run #154 kemudian sukses: validasi kamus 60 batch / 3.014 entri, validasi valensi, dataset POS, evaluasi development, dan **342/342 tes regresi lulus**. [Lihat Run #154](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46014585155).

**Batas:** perluasan ini hanya mencakup empat adverbia temporal yang sudah dikenali secara eksplisit. Ini tidak menyelesaikan seluruh keterangan adverbial atau inversi K-P-S. Tahap aktif tetap 2.6.


### Investigasi awal inversi K-P-S — Run #156 (27 November 2026)

Checklist Tahap 2.6 meminta pola inversi diuji hanya jika aturan linguistik dan bukti pendukungnya jelas. Investigasi ini belum menambahkan parser K-P-S positif, karena posisi nomina setelah verba saja tidak cukup untuk menentukan apakah nomina itu subjek inversi atau objek dengan subjek yang dilesapkan.

Dua konstruksi dibandingkan melalui unit test dan pipeline kamus/POS nyata:
- `Di rumah terdengar suara.`: kandidat K-P-S; `suara` mungkin subjek pascaverbal.
- `Di rumah membaca buku.`: pola permukaan serupa, tetapi `buku` dapat menjadi objek sementara subjek tidak disebutkan.

Parser mempertahankan kedua kalimat sebagai `unresolved`, mencatat `di rumah` sebagai keterangan awal, dan tidak memaksakan nomina akhir menjadi SUBJ maupun OBJ. Tes baru ditambahkan pada `tests/test_parser_kalimat.py` dan `tests/test_integrasi_pipeline.py`. Run #156 sukses: validasi kamus penuh 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, serta **344/344 tes regresi lulus**. [Lihat Run #156](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46015428982).

**Keputusan sementara:** investigasi batas dan uji abstention selesai sebagian; inversi K-P-S belum diimplementasikan dan item checklist tetap `[~]`. Aturan positif perlu menunggu pemilihan sense predikat dan bukti valensi yang cukup untuk membedakan predikat intransitif dari predikat transitif/objek. Jangan membuat daftar kata kerja khusus hanya untuk meloloskan contoh tertentu. Tahap aktif tetap 2.6.


### Perluasan uji konstruksi melalui pipeline kamus/POS — Run #157–158 (27 November 2026)

Untuk melanjutkan item pengujian konstruksi nyata pada Tahap 2.6, ditambahkan tes predikat adjektival `Dia sakit.` melalui `analyze_text()`, POS tagger, disambiguasi konteks, dan parser. Indeks kamus diperiksa lebih dahulu untuk memastikan lema `dia` dan `sakit` tersedia; tidak ada perubahan kamus. Hasil yang diharapkan: `dia` = PRON, `sakit` = ADJ, struktur S-P, tanpa objek.

Run #157 gagal hanya karena tes awal mencari token dengan kapitalisasi `Dia`, sedangkan normalisasi menghasilkan token `dia`. Ekspektasi tes disesuaikan dengan keluaran normalisasi (bukan mengubah perilaku parser). Run #158 sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **345/345 tes regresi lulus**. [Lihat Run #158](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46015686211).

Item pengujian pipeline pada checklist sekarang berstatus `[~]`, bukan selesai: kasus predikat adjektival ini menambah satu konstruksi nyata, tetapi variasi lain masih harus diuji. Tahap aktif tetap 2.6.


### Tambahan uji subjek nominal melalui pipeline nyata — Run #159 (27 November 2026)

Ditambahkan kasus `Anak makan nasi.` untuk memastikan subjek berupa nomina umum, bukan hanya pronomina, diproses melalui kamus, POS, dan parser. Indeks kamus sebelumnya telah mengonfirmasi `anak`, `makan`, dan `nasi` tersedia; tidak ada perubahan data kamus. POS yang diharapkan: NOUN + VERB + NOUN; hasil parser: S-P-O dengan `anak` sebagai subjek dan `nasi` sebagai objek. Run #159 sukses dengan **346/346 tes regresi**, termasuk validasi kamus 60 batch / 3.014 lema dan evaluasi development POS. [Lihat Run #159](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46015818026).

Pengujian konstruksi nyata Tahap 2.6 kini juga mencakup predikat adjektival `Dia sakit.` (Run #158) dan subjek nominal `Anak makan nasi.` (Run #159). Cakupan ini masih parsial; item checklist tetap `[~]` sampai variasi konstruksi lain yang relevan diuji.


### Uji negasi verbal melalui pipeline kamus/POS nyata — Run #160 (27 November 2026)

Ditambahkan tes integrasi untuk kalimat `Aku tidak makan nasi.` Indeks kamus diperiksa terlebih dahulu dan mengonfirmasi lema `aku`, `tidak`, `makan`, dan `nasi` tersedia; tidak ada batch atau indeks kamus yang diubah. Tes memeriksa POS hasil pipeline: PRON + ADV + VERB + NOUN, lalu memastikan parser menghasilkan pola S-P-O, menempatkan `tidak` bersama `makan` dalam rentang predikat, mengidentifikasi kepala predikat `makan`, dan mempertahankan `nasi` sebagai objek. Run #160 sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **347/347 tes regresi lulus**. [Lihat Run #160](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46016150202).

Cakupan pengujian konstruksi nyata Tahap 2.6 kini mencakup kalimat adjektival, kalimat dengan subjek nominal dan objek, serta negasi verbal. Item perluasan pengujian tetap berstatus sebagian karena variasi pola dan batas parser lain belum seluruhnya diuji.


### Uji gabungan negasi dan modalitas melalui pipeline nyata — Run #161 (27 November 2026)

Ditambahkan tes integrasi untuk kalimat `Aku tidak akan makan nasi.` Indeks kamus diperiksa terlebih dahulu dan memastikan `aku`, `tidak`, `akan`, `makan`, dan `nasi` tersedia; tidak ada perubahan pada batch atau indeks kamus. Tes memeriksa hasil POS nyata (PRON + ADV + ADV + VERB + NOUN), lalu memastikan parser mempertahankan pola S-P-O, rentang predikat `tidak akan makan`, kepala predikat leksikal `makan`, pewatas `tidak` sebagai negasi dan `akan` sebagai modal, serta `nasi` sebagai objek.

GitHub Actions **Run #161** sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **348/348 tes regresi lulus**. [Lihat Run #161](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46016960249).

**Batas:** pengujian ini memvalidasi satu susunan terkontrol untuk gabungan negasi dan modalitas. Ini belum membuktikan semua kombinasi modal, negasi, atau urutan pewatas predikat telah didukung.

### Uji modalitas verbal melalui pipeline nyata — Run #162 (27 November 2026)

Ditambahkan tes integrasi untuk dua kalimat: `Aku mau makan nasi.` dan `Aku ingin makan nasi.` Indeks kamus memastikan lema `aku`, `mau`, `ingin`, `makan`, dan `nasi` tersedia; tidak ada perubahan pada batch atau indeks kamus. Pipeline memvalidasi modal `mau` dan `ingin` sebagai VERB, lalu parser menggabungkan modal dengan verba leksikal ke rentang predikat, mempertahankan `makan` sebagai kepala predikat, dan `nasi` sebagai objek.

GitHub Actions **Run #162** sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **349/349 tes regresi lulus**. [Lihat Run #162](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46017378600).

**Batas:** pengujian mencakup dua modal verbal yang sudah didaftarkan eksplisit pada parser; ini tidak berarti seluruh kata yang dapat menyatakan keinginan, kemampuan, atau keharusan otomatis dikenali sebagai modal.


### Uji modal ambigu `bisa` melalui pipeline nyata — Run #164 (27 November 2026)

Ditambahkan tes integrasi untuk kalimat `Aku bisa makan nasi.` Pemeriksaan indeks memastikan lema `aku`, `bisa`, `makan`, dan `nasi` tersedia; tidak ada perubahan pada batch maupun indeks kamus. Tes awal Run #163 menemukan bahwa kandidat POS kamus untuk `bisa` memang `VERB` dan `NOUN`, sehingga ekspektasi tes diperbaiki agar tidak memaksa satu POS leksikal. Pada pipeline konteks, verba sesudahnya (`makan`) menjadi bukti yang memilih `VERB` melalui aturan `bisa_before_verb`. Parser kemudian menghasilkan pola S-P-O, predikat `bisa makan`, kepala `makan`, dan objek `nasi`.

GitHub Actions **Run #164** sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **350/350 tes regresi lulus**. [Lihat Run #164](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46017770296).

**Batas:** ini membuktikan satu konteks modal `bisa` yang diikuti verba. Penggunaan `bisa` sebagai nomina atau pada konteks lain tetap bergantung pada bukti konteks; tidak semua konstruksi modal otomatis tercakup. Lema `hendak` tidak ditemukan pada shard indeks yang diperiksa dan tidak ditambahkan.


### Uji negasi + modal ambigu `bisa` melalui pipeline nyata — Run #165 (27 November 2026)

Ditambahkan tes integrasi untuk kalimat `Aku tidak bisa makan nasi.` Indeks kamus memastikan lema `aku`, `tidak`, `bisa`, `makan`, dan `nasi` tersedia; tidak ada perubahan pada batch maupun indeks kamus. Kandidat POS `bisa` tetap VERB+NOUN dan dipilih sebagai VERB berdasarkan konteks verba berikutnya (`makan`), sedangkan `tidak` tetap ADV. Parser menghasilkan pola S-P-O, rentang predikat `tidak bisa makan`, kepala predikat `makan`, modifier `tidak` sebagai negasi dan `bisa` sebagai modal, serta objek `nasi`.

GitHub Actions **Run #165** sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **351/351 tes regresi lulus**. [Lihat Run #165](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46018126303).

**Batas:** pengujian ini mencakup kombinasi satu negasi (`tidak`) dan satu modal ambigu (`bisa`) dalam susunan terkontrol. Ini belum memvalidasi seluruh urutan negasi/modal atau seluruh penggunaan leksikal `bisa`.

### Uji modal verbal dengan keterangan temporal pascapredikat — Run #166 (27 November 2026)

Ditambahkan tes integrasi untuk `Aku mau makan nasi besok.` Indeks kamus diperiksa lebih dahulu dan memastikan lema `aku`, `mau`, `makan`, `nasi`, dan `besok` tersedia; tidak ada batch atau indeks kamus yang diubah. Tes melewati analisis teks, POS tagger, disambiguasi POS kontekstual, dan parser. Hasilnya: `aku` PRON, `mau` VERB, `makan` VERB, `nasi` NOUN, dan `besok` ADV; parser menghasilkan pola S-P-O-K, rentang predikat `mau makan` dengan kepala `makan`, objek `nasi`, serta keterangan temporal `besok`.

GitHub Actions **Run #166** sukses: validasi kamus 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **352/352 tes regresi lulus**. [Lihat Run #166](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46018848688).

**Batas:** pengujian ini memvalidasi satu kombinasi modal verbal dengan keterangan temporal setelah objek. Ini belum membuktikan semua susunan keterangan atau kombinasi modalitas telah didukung.

### Uji negasi + modal adverb + keterangan temporal pascapredikat — Run #167 (27 November 2026)

Ditambahkan tes integrasi untuk `Aku tidak akan makan nasi besok.` Indeks kamus diperiksa terlebih dahulu: `aku`, `akan`, `besok`, `makan`, `nasi`, dan `tidak` tersedia. Tidak ada penambahan lema atau perubahan batch/index. Melalui pipeline nyata, POS dikenali sebagai PRON, ADV, ADV, VERB, NOUN, ADV. Parser menghasilkan S-P-O-K; predikat `tidak akan makan` berkepala `makan`, dengan modifier `tidak` sebagai negasi dan `akan` sebagai modal, objek `nasi`, serta keterangan temporal `besok`.

GitHub Actions **Run #167** sukses: validasi 60 batch / 3.014 lema, validasi valensi, dataset POS, evaluasi development, dan **353/353 tes regresi lulus**. Coverage/accuracy POS kontekstual development tetap 98,0% / 98,0%, selective accuracy 100,0%. [Lihat Run #167](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46019265619).

**Batas:** ini membuktikan satu kombinasi negasi + modal adverb + objek + keterangan temporal pascapredikat. Tidak menggeneralisasi ke seluruh pola urutan kata atau seluruh jenis keterangan.

### Uji modal ambigu `bisa` + keterangan temporal `nanti` — Run #169 (27 November 2026)

Ditambahkan tes integrasi untuk `Aku bisa makan nasi nanti.` Indeks kamus memastikan `aku`, `bisa`, `makan`, `nasi`, dan `nanti` tersedia. Tidak ada perubahan batch maupun indeks. Kandidat leksikal `bisa` tetap VERB+NOUN; bukti konteks `bisa_before_verb` dengan cue `makan` memilih VERB, dan tes memeriksa bukti melalui field `pos_context_evidence` sesuai skema pipeline. Parser menghasilkan S-P-O-K, predikat `bisa makan` berkepala `makan`, objek `nasi`, dan adjunct temporal `nanti`.

Run #168 sempat gagal karena tes baru membaca nama field bukti konteks yang keliru (`context_evidence`); log mengidentifikasi KeyError tersebut. Tes diperbaiki agar memakai `pos_context_evidence`, lalu **Run #169 sukses** dengan validasi 60 batch / 3.014 lema, valensi, dataset POS, evaluasi development, dan **354/354 tes regresi lulus**. POS kontekstual development tetap coverage/accuracy 98,0% dan selective accuracy 100,0%. [Lihat Run #169](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46019606633).

**Batas:** pengujian memvalidasi satu konstruksi `bisa` modal yang diikuti verba dan keterangan temporal pascapredikat. Penggunaan `bisa` dalam konteks lain tetap memerlukan bukti konteks yang memadai.

### Uji klausa konsesif pascaposisi — Run #170 (27 November 2026)

Ditambahkan tes integrasi pipeline nyata untuk `Aku pergi walaupun hujan turun.` Indeks kamus memastikan `aku`, `pergi`, `walaupun`, `hujan`, dan `turun` tersedia. Tidak ada perubahan batch atau indeks kamus. Tes memverifikasi POS dari kamus (`PRON`, `VERB`, `CONJ`, `NOUN`, `VERB`), pemisahan klausa utama `Aku pergi` dan klausa subordinatif `hujan turun`, serta relasi `konsesi` yang ditandai oleh `walaupun`.

GitHub Actions **Run #170 selesai dengan conclusion success**. Validasi 60 batch / 3.014 lema, valensi, dataset POS, dan evaluasi development berhasil; **355/355 tes regresi lulus**. POS kontekstual development tetap coverage/accuracy 98,0% dan selective accuracy 100,0%. [Lihat Run #170](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46019852916).

**Batas:** pengujian ini mencakup klausa konsesif pascaposisi dengan dua klausa S-P eksplisit. Ini belum membuktikan semua bentuk konsesi, elipsis, atau susunan klausa konsesif sudah ditangani.

### Uji klausa konsesif di awal kalimat — Run #171 (27 November 2026)

Ditambahkan tes integrasi pipeline nyata untuk `Walaupun hujan turun, aku pergi.` Indeks kamus memastikan `walaupun`, `hujan`, `turun`, `aku`, dan `pergi` tersedia; tidak ada penambahan lema maupun perubahan batch/index. Tes memverifikasi POS dari kamus, klausa subordinatif awal `hujan turun` dengan pola S-P, klausa utama `aku pergi` dengan pola S-P, dan relasi konsesi `walaupun` yang dihubungkan melalui koma.

GitHub Actions **Run #171 selesai dengan conclusion success**. Validasi 60 batch / 3.014 lema, valensi, dataset POS, dan evaluasi development berhasil. **356/356 tes regresi lulus.** POS kontekstual development tetap coverage/accuracy 98,0% dan selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #171](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46020096831).

**Batas:** pengujian mencakup satu pola konsesif eksplisit di awal kalimat dengan koma dan dua klausa S-P. Ini tidak membuktikan seluruh variasi konsesi atau elipsis telah ditangani.

### Variasi elipsis konsesif dengan penanda `meskipun` — Run #172 (27 November 2026)

Ditambahkan tes pipeline kamus/POS/parser untuk `Meskipun lelah, aku pergi.` Indeks kamus mengonfirmasi semua lema tersedia (`meskipun`, `lelah`, `aku`, `pergi`); tidak ada perubahan batch atau indeks kamus. POS masing-masing diverifikasi berasal dari kamus. Parser mengenali klausa subordinatif konsesif awal dengan pola `P-ELIPTIS` dan klausa utama `aku pergi` dengan pola S-P. Subjek klausa eliptis tetap kosong dan hasil keseluruhan `partial`; parser tidak menyalin atau menebak subjek dari klausa utama.

GitHub Actions **Run #172 selesai dengan conclusion success**. Validasi 60 batch / 3.014 lema, valensi, dataset POS, dan evaluasi development berhasil; **357/357 tes regresi lulus**. POS kontekstual development tetap coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%. Test split tidak dibuka. [Lihat Run #172](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46020456944).

**Batas:** tes ini memverifikasi satu bentuk elipsis adjektival konsesif dengan penanda `meskipun`; tidak menggeneralisasi semua elipsis atau semua konjungsi.

### Uji pronomina persona sebagai subjek dan objek — Run #173 (27 November 2026)

Ditambahkan tes integrasi pipeline kamus → POS → parser untuk pronomina persona `saya`, `kamu`, `dia`, dan `mereka`. Keempatnya ditemukan pada indeks kamus sebagai lema PRON, lalu diuji pada posisi subjek (contoh pola S-P-O) dan objek (contoh pola S-P-O). Seluruh token mendapat POS PRON dari kamus dan seluruh hasil parser sesuai peran yang diharapkan. Tidak ada perubahan pada batch maupun indeks kamus.

Pemeriksaan indeks juga menunjukkan `kalian` belum tersedia sebagai lema atau entri indeks. Sesuai aturan proyek, lema baru tidak ditambahkan tanpa persetujuan eksplisit pengguna; pengujian untuk kata ini masih tertunda.

GitHub Actions **Run #173 selesai dengan conclusion success**. Validasi kamus 60 batch / 3.014 lema, valensi, dataset POS, dan evaluasi development berhasil; **358/358 tes regresi lulus**. POS kontekstual development tetap coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #173](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46021616127).

**Batas:** pengujian membuktikan empat pronomina pada posisi subjek dan objek dalam pola kalimat sederhana yang diuji. Ini belum membuktikan seluruh penggunaan pronomina, ragam tutur, atau konstruksi sintaksis yang lebih kompleks.


### Perluasan inventaris dan uji pronomina persona — Run #176 (27 November 2026)

Atas persetujuan pengguna, lema `kalian` ditambahkan ke `data/kamus/batch-060.jsonl` sebagai PRON (ID K3016) dan dimasukkan ke indeks `j-l.tsv`. Jumlah kamus menjadi 3.015 lema pada 60 batch. Validator ukuran kamus dan asersi jumlah entri pada tes integrasi diperbarui dari 3.014 menjadi 3.015.

Tes pipeline kamus → POS → parser diperluas untuk sembilan pronomina: `aku`, `saya`, `kamu`, `engkau`, `dia`, `mereka`, `kita`, `kami`, dan `kalian`. Setiap bentuk diuji pada posisi subjek dan objek dalam pola S-P-O; seluruhnya dikenali sebagai PRON dan hasil parser sesuai harapan.

Pemeriksaan indeks menemukan kandidat tambahan `Anda`, `beliau`, `ia`, dan `kau` belum tersedia sebagai lema. Kandidat ini belum ditambahkan; perlu persetujuan pengguna sebelum ada perubahan kamus. Bentuk seperti `-ku`, `-mu`, dan `-nya` juga perlu ditangani sebagai bentuk terikat/morfologi, bukan otomatis dianggap lema pronomina mandiri.

GitHub Actions **Run #176 selesai dengan conclusion success**. Validasi kamus lengkap berhasil memuat 60 batch / 3.015 lema; validasi valensi dan dataset POS berhasil; **358/358 tes regresi lulus**. POS kontekstual development tetap coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #176](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46022179021).

**Batas:** uji sembilan pronomina ini mencakup pola kalimat sederhana S-P-O pada posisi subjek dan objek. Ini belum membuktikan seluruh konstruksi, ragam hormat, bentuk terikat, atau pronomina nonpersona.


### Perluasan pronomina persona — Run #179 (27 November 2026)

Atas persetujuan pengguna, empat lema tambahan dimasukkan ke `data/kamus/batch-060.jsonl`: `anda` (K3017, PRON, formal), `beliau` (K3018, PRON, formal/hormat), `ia` (K3019, PRON), dan `kau` (K3020, PRON, informal/akrab atau puitis). Ketiganya ditempatkan pada shard indeks sesuai huruf awal; jumlah kamus menjadi **3.019 lema dalam 60 batch** dan indeks memuat **3.601 token**.

Tes pipeline kamus → POS → parser kini mencakup 13 pronomina: `aku`, `saya`, `kamu`, `engkau`, `dia`, `mereka`, `kita`, `kami`, `kalian`, `anda`, `beliau`, `ia`, dan `kau`. Seluruhnya diuji pada posisi subjek dan objek dalam pola S-P-O; uji memverifikasi kecocokan kamus, POS PRON, dan peran parser. Run #177–178 gagal pada pemeriksaan jumlah karena validator masih mengharapkan 3.015 lema; nilai validator dan label workflow diselaraskan menjadi 3.019. **Run #179 selesai dengan conclusion success: 358/358 tes regresi lulus**, validasi kamus 60 batch / 3.019 lema, validasi valensi dan dataset POS berhasil, serta evaluasi POS development tetap coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%. Test split tidak dibuka. [Lihat Run #179](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46023172229).

**Batas:** pengujian 13 pronomina ini mencakup pola sederhana S-P-O sebagai subjek dan objek. Inventaris pronomina informal/regional lain serta bentuk terikat seperti `-ku`, `-mu`, dan `-nya` belum selesai; bentuk terikat tetap menjadi pekerjaan morfologi.


### Batas frasa preposisional awal dengan subjek pronomina eksplisit — Run #182 (27 November 2026)

Ditambahkan satu tes integrasi pipeline kamus → POS → parser untuk kalimat `Dari rumah dia bekerja.`. Indeks kamus diperiksa terlebih dahulu: `dari` tersedia sebagai PREP, `rumah` sebagai NOUN, `dia` sebagai PRON, dan `bekerja` sebagai bentuk turunan VERB. Tes memverifikasi seluruh POS berasal dari kamus, parser mempertahankan `dia` sebagai subjek, `bekerja` sebagai predikat, dan `dari rumah` sebagai keterangan awal. Tidak ada perubahan kamus maupun perilaku parser; ini memperkuat uji regresi batas PP awal melalui pipeline nyata.

Selama pengujian awal, kandidat kalimat dengan `di` tidak dapat dipakai untuk memverifikasi POS kamus karena token `di` tidak ditemukan pada indeks. Tidak ada lema yang ditambahkan; contoh uji diganti dengan `dari` yang memang tersedia pada indeks. Perbaikan ekspektasi tes juga menjaga tes lama tetap utuh.

GitHub Actions **Run #180 dan #181** gagal pada percobaan tes/ekspektasi awal; setelah menggunakan lema yang terindeks dan memperbaiki ekspektasi hanya pada tes baru, **Run #182 selesai dengan conclusion success**. Validasi kamus 60 batch / 3.019 lema, valensi, dataset POS, dan evaluasi development berhasil; **359/359 tes regresi lulus**. POS development tetap coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #182](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/46023874794).

**Batas:** hasil ini hanya membuktikan PP awal `dari rumah` tidak menelan subjek pronomina eksplisit `dia` pada contoh yang diuji. Inversi K-P-S seperti `Di rumah terdengar suara.` dan kemungkinan subjek tersirat pada `Di rumah membaca buku.` tetap unresolved; belum ada aturan positif K-P-S yang aman.

### Fondasi analisis klitik pronominal terikat — Run #183 (27 November 2026)

Modul morfologi kini mengenali tiga klitik pronominal terikat (-ku, -mu, -nya) setelah bentuk dasar yang cocok dengan kamus. Analisis mengembalikan bentuk permukaan, bentuk dasar, kandidat leksikal, identitas klitik, serta dua interpretasi yang masih mungkin: posesif atau objek. Tahap morfologi tidak memilih fungsi sintaksisnya secara otomatis.

Pengujian unit mencakup bentuk nominal bukuku, rumahmu, bukunya, bentuk verbal turunan melihatku, serta perlindungan terhadap pronomina utuh kamu agar tidak dipecah sebagai klitik. Bentuk dengan dasar yang tidak dikenal, seperti xyzku, tidak dipaksakan. Tes integrasi juga memverifikasi enam bentuk: bukuku, rumahmu, bukunya, melihatku, melihatmu, dan melihatnya melalui analyze_text() dengan kamus lengkap. Indeks diperiksa untuk lema dasar yang dipakai; tidak ada penambahan atau perubahan data kamus.

GitHub Actions Run #183 selesai dengan conclusion success. Validasi kamus 60 batch / 3.019 lema, valensi, dataset POS, dan evaluasi POS development berhasil; 366/366 tes regresi lulus. POS development tetap coverage 98,0%, accuracy 98,0%, selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #183](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46026858196).

Batas: ini baru fondasi segmentasi klitik pada tahap morfologi. Hasil token berklitik masih berstatus unknown pada pencocokan permukaan; POS tagger dan parser belum mengonsumsi informasi klitik untuk menetapkan PRON terikat atau membedakan fungsi posesif dari objek. Bentuk lain, variasi ejaan informal, dan konteks sintaksisnya masih perlu diuji.
### Integrasi komponen klitik pada POS secara konservatif — Run #185 (27 November 2026)

POS tagger kini membaca hasil analisis klitik dari morfologi dan mengekspos struktur komponen: POS host (hanya dari lema/varian atau anotasi POS bentuk turunan yang eksplisit), komponen klitik PRON, kombinasi POS yang mungkin, serta kandidat fungsi posesif/objek dengan status unresolved. POS permukaan utama tetap kosong/unknown karena satu token gabungan seperti bukuku (NOUN+PRON) atau melihatnya (VERB+PRON) tidak boleh dipaksa menjadi satu kelas kata tunggal. POS lema tidak diwariskan ke bentuk turunan tanpa anotasi POS permukaan yang tervalidasi.

Tes POS mencakup host nominal `buku` dan `rumah`, serta host verbal turunan `melihat` dengan anotasi VERB eksplisit. Tes negatif memastikan bentuk turunan tanpa anotasi POS tidak mewarisi POS lema. Tes integrasi memeriksa enam bentuk klitik melalui alur analyze_text → tag_pos → disambiguate_pos_context. Percobaan Run #184 gagal karena tes integrasi memanggil analyzer leksikal saja sebelum mengharapkan metadata POS; tes diperbaiki agar menggunakan pipeline POS lengkap, tanpa mengubah perilaku produksi.

GitHub Actions **Run #185 selesai dengan conclusion success**; **368/368 tes regresi lulus**. Validasi kamus 60 batch / 3.019 lema, valensi, dataset POS, dan evaluasi POS development berhasil. Test split tetap tersegel. [Lihat Run #185](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46027412483).

**Batas:** metadata POS komponen belum menentukan fungsi sintaksis klitik. Parser belum memisahkan host dan klitik menjadi argumen/pewatas, dan belum membedakan `-nya` posesif dari objek melalui konteks. Bentuk host turunan hanya memperoleh POS jika anotasi POS bentuk permukaan tersedia; selain itu tetap unresolved.
### Parser mengonsumsi klitik pada host nominal — Run #190 (27 November 2026)

Parser kini dapat memakai komponen POS klitik hanya jika host nominal memiliki satu POS eksplisit NOUN. Token gabungan seperti `bukuku` tetap menjadi satu token permukaan dan dapat mengisi slot frasa nominal subjek/objek; parser tidak memaksakan POS permukaan tunggal pada token leksikal tersebut. Jika host POS kosong/ambigu atau bukan NOUN, jalur ini tidak diaktifkan dan token tetap unresolved.

Untuk host NOUN yang sudah teridentifikasi, parser menambahkan `clitic_analysis` yang mencatat bentuk permukaan, lema dasar, klitik, fungsi `possessive`, dan peran frasa nominal dalam klausa. Tes unit menguji `bukuku` sebagai objek nominal dan memastikan `melihatku` dengan host POS kosong tidak dipaksakan. Tes integrasi melalui kamus lengkap menguji `Dia lihat bukuku.` menjadi S-P-O, dengan `bukuku` sebagai objek dan `-ku` sebagai posesif.

GitHub Actions **Run #190 selesai dengan conclusion success**; **371/371 tes regresi lulus**. Validasi kamus 60 batch / 3.019 lema, valensi, dataset POS, dan evaluasi POS development berhasil. Test split tetap tersegel. [Lihat Run #190](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46028108871).

**Batas:** dukungan ini hanya untuk klitik yang melekat pada host NOUN dengan POS tunggal yang diketahui. Klitik pada host VERB (fungsi objek terikat), struktur internal NP posesif yang lebih rinci, dan variasi ragam/informal belum ditangani. Token permukaan tidak dipecah menjadi dua token; `clitic_analysis` menyimpan metadata relasi internal secara terpisah.
### Klitik objek pada host verbal — Run #195 (27 November 2026)

Parser kini mengonsumsi metadata klitik ketika host memiliki satu POS eksplisit `VERB`. Untuk bentuk seperti `lihatku`, host `lihat` dikenali sebagai verba melalui lema kamus, sehingga token permukaan tetap menjadi kepala predikat dan `-ku` dianalisis sebagai objek terikat. Keluaran `clitic_analysis` mencatat `function: object`, `function_status: selected_by_verbal_host`, dan `host_role: predicate`; pola klausa dapat mencerminkan slot objek melalui `S-P-O`, tanpa menduplikasi token ke `roles.object`.

Tes unit memverifikasi `lihatku` sebagai predikat dengan objek klitik, dan tes pipeline kamus/POS nyata memverifikasi `Dia lihatku.`. Host turunan yang tidak memiliki anotasi POS eksplisit tidak boleh mewarisi POS lema secara otomatis; percobaan awal dengan `melihatku` menunjukkan host `melihat` belum memiliki anotasi turunan eksplisit, sehingga contoh uji diganti ke host lema `lihat` yang POS-nya jelas. Ini mempertahankan aturan konservatif, bukan melonggarkannya.

GitHub Actions **Run #195 selesai dengan conclusion success**; **373/373 tes regresi lulus**. [Lihat Run #195](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46029121093). Tidak ada lema baru ditambahkan dan tidak ada batch kamus yang diubah.

**Batas:** fungsi objek terikat hanya dipilih untuk host dengan POS tunggal `VERB` yang eksplisit. Host turunan tanpa anotasi POS, host ambigu, konstruksi lain, dan variasi informal/regional tetap unresolved sampai ada bukti/aturan yang memadai. `roles.object` tidak diisi ulang dengan token predikat yang sama; relasi objek terikat direpresentasikan terpisah melalui `clitic_analysis`.
### Menjaga ambiguitas fungsi nominal `-nya` — Run #198 (27 November 2026)

Penanganan klitik nominal diperhalus agar tidak menganggap setiap `-nya` sebagai posesif. Pada host NOUN, `-ku` dan `-mu` dapat ditandai posesif secara terbatas. Sementara itu, `-nya` pada nomina dapat menyatakan kepemilikan atau fungsi definit/anforis; tanpa konteks yang cukup, parser menyimpan `function: null`, kandidat `possessive` dan `definite_anaphoric`, serta status `unresolved`, sambil tetap melaporkan peran frasa nominalnya dalam klausa.

Tes unit dan integrasi pipeline kamus/POS nyata menggunakan `Dia lihat bukunya.` memastikan `bukunya` tetap teridentifikasi sebagai objek, tetapi fungsi `-nya` tidak diputuskan secara paksa. GitHub Actions **Run #198 sukses; 375/375 tes regresi lulus**. [Lihat Run #198](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46029341871).

**Batas:** kandidat fungsi yang diuji saat ini dibatasi pada posesif vs definit/anforis untuk `-nya` nominal. Pemakaian `-nya` lain, misalnya nominalisasi atau fungsi wacana pada konstruksi tertentu, belum dimodelkan. Tidak ada perubahan kamus atau penambahan lema.
### Konsistensi klitik objek verbal untuk -ku, -mu, dan -nya — Run #200 (27 November 2026)

Pengujian parser diperluas agar tiga bentuk klitik pada host VERB diuji dengan aturan yang sama. Tes unit menggunakan host lema `lihat` dengan POS VERB eksplisit untuk bentuk `lihatku`, `lihatmu`, dan `lihatnya`. Setiap bentuk menghasilkan kerangka S-P-O; token gabungan tetap berada pada rentang predikat, sedangkan klitik dicatat sebagai objek terikat dalam `clitic_analysis` dengan `function_status: selected_by_verbal_host`. Slot `roles.object` tidak diisi dengan salinan token predikat.

Pipeline lengkap kamus → morfologi → POS → konteks → parser juga menguji kalimat `Dia lihatku.`, `Dia lihatmu.`, dan `Dia lihatnya.`. Ketiganya dikenali dengan host POS `VERB` eksplisit dan menghasilkan keluaran yang konsisten. Bentuk kalimat tersebut digunakan sebagai uji struktural untuk klitik objek pada host verbal; pengujian ini tidak menyatakan bahwa seluruh ragam atau konteks pemakaian ketiga bentuk sudah tercakup.

GitHub Actions **Run #200 selesai dengan conclusion success**; **377/377 tes regresi lulus**. Validasi kamus 60 batch / 3.019 lema, valensi, dataset POS, dan evaluasi POS development juga berhasil; test split tetap tersegel. [Lihat Run #200](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46031404877).

**Batas:** dukungan masih terbatas pada host VERB dengan satu POS eksplisit yang berasal dari lema/metadata yang tervalidasi. Bentuk turunan seperti `melihat` tanpa anotasi POS turunan eksplisit tetap tidak mewarisi POS lema secara otomatis. Fungsi klitik pada host selain pola yang telah diuji, variasi informal/regional, dan analisis internal frasa nominal masih memerlukan pengujian lanjutan. Tidak ada lema baru ditambahkan dan tidak ada batch/index kamus yang diubah.

### Uji pronomina persona informal melalui pipeline penuh — Run #201 (27 November 2026)

Inventaris indeks menunjukkan lema pronomina informal `gue` dan `lu` telah tersedia pada batch 001. Variasi `gua`, `gw`, `lo`, dan `elu` tercatat sebagai variants dari kedua lema tersebut. Entri `awak` dan `abdi` juga ada di indeks, tetapi keduanya ber-POS NOUN dalam data kamus saat ini sehingga tidak diperlakukan sebagai pronomina persona. Tidak ada perubahan batch atau indeks kamus.

Tes integrasi pipeline kamus → POS → parser ditambahkan untuk enam bentuk `gue`, `gua`, `gw`, `lu`, `lo`, dan `elu`. Setiap bentuk diuji sebagai subjek pada kalimat pola S-P-O dan sebagai objek pada kalimat pola S-P-O. Seluruhnya dikenali sebagai PRON dengan sumber POS dari kamus dan menempati peran sintaksis yang diharapkan.

GitHub Actions **Run #201 selesai dengan conclusion success**; **378/378 tes regresi lulus**. Validasi kamus 60 batch / 3.019 lema, valensi, dataset POS, dan evaluasi POS development berhasil. Coverage dan accuracy POS kontekstual development tetap 98,0%, selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #201](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46032249459).

**Batas:** pengujian baru mencakup enam bentuk informal perkotaan yang merupakan lema/varian dari dua entri PRON. Ini belum membuktikan seluruh pemakaian regional, ragam hormat, pronomina refleksif, demonstratif, interogatif, atau indefinit. Kandidat yang tidak ditemukan di indeks belum ditambahkan; perlu persetujuan eksplisit pengguna sebelum perubahan kamus.

### Penambahan lema refleksif dan demonstratif — Run #203 (27 November 2026)

Atas persetujuan pengguna, enam lema ditambahkan ke `data/kamus/batch-060.jsonl: `begini` (K3021, ADV), `begitu` (K3022, ADV), `diri` (K3023, NOUN), `ini` (K3024, PRON), `itu` (K3025, PRON), dan `sendiri` (K3026, ADJ+ADV). Sumber kamus, empat shard indeks terkait, dan `data/kamus/INDEX.md` diperbarui dalam satu commit. Jumlah menjadi **3.025 lema dalam 60 batch** dan **3.607 token terindeks**.

POS demonstratif `ini` dan `itu` dipakai sebagai kategori PRON dalam taksonomi proyek, dengan catatan bahwa keduanya juga dapat mendampingi nomina. `begini` dan `begitu` dicatat sebagai ADV; `diri` sebagai NOUN; `sendiri` sebagai ADJ+ADV. Bentuk `diriku`, `dirimu`, dan `dirinya` belum ditambahkan sebagai lema terpisah karena perlu ditangani bersama analisis morfologi/klitik.

Run #202 sempat gagal karena validator kamus lengkap dan satu assertion integrasi masih mengharapkan 3.019 entri. Ekspektasi keduanya diperbarui menjadi 3.025. **Run #203 selesai dengan conclusion success**: validasi relasi untuk batch 058–060, validasi kamus lengkap 3.025 lema, validasi valensi, validasi dataset POS, evaluasi development, dan **378/378 tes regresi lulus**. Coverage dan accuracy POS development tetap 98,0%, selective accuracy 100,0%; test split tidak dibuka. [Lihat Run #203](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46034097778).

**Batas:** Run #203 memvalidasi struktur kamus dan regresi yang sudah ada, tetapi belum menambahkan tes pipeline khusus untuk enam lema baru. Fungsi demonstratif sebagai penentu nomina vs pengganti frasa nominal, fungsi refleksif `diri/sendiri`, dan konstruksi adverbial `begini/begitu` masih perlu diuji sebelum cakupan sintaksisnya dinyatakan tersedia.


### Pengujian pipeline enam lema refleksif dan demonstratif — Run #204 (27 November 2026)

Setelah keenam lema ditambahkan pada Run #203, tes integrasi khusus ditambahkan untuk memeriksa bahwa lema tersebut benar-benar melewati pipeline kamus → POS → parser, bukan hanya lolos validasi struktur kamus. Tes mencakup pengenalan lema dan sumber POS dari kamus; pemakaian adverbial `begini` dan `begitu`; demonstratif `ini` dan `itu` pada frasa nominal; serta `diri` sebagai NOUN dan `sendiri` yang tetap memiliki kandidat ADJ+ADV ketika konteks belum cukup untuk memilih salah satunya.

GitHub Actions **Run #204 selesai dengan conclusion success**; **381/381 tes regresi lulus**. Log juga mengonfirmasi validasi kamus lengkap memuat **3.025 lema** dalam 60 batch, validasi relasi leksikal batch terpilih, valensi, dataset POS, dan evaluasi development berhasil. [Lihat Run #204](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46041318079).

**Batas:** tes ini memvalidasi pengenalan POS dan sejumlah contoh pipeline terpilih, bukan seluruh fungsi sintaksis demonstratif atau refleksif. Fungsi `ini/itu` sebagai penentu nomina vs pengganti frasa nominal belum dibedakan sebagai kategori sintaksis tersendiri; konstruksi refleksif lengkap seperti `diriku/dirimu/dirinya` belum diuji sebagai analisis klitik-refleksif; dan pemilihan ADJ vs ADV untuk `sendiri` masih dibiarkan ambigu bila bukti konteks tidak memadai. Tidak ada perubahan kamus pada Run #204.


### Pengujian bentuk refleksif diri + klitik — Run #205 (27 November 2026)

Tes integrasi pipeline penuh ditambahkan untuk kalimat `Aku melihat diriku.`, `Kamu melihat dirimu.`, dan `Dia melihat dirinya.`. Ketiganya dikenali melalui morfologi sebagai host `diri` (NOUN) + klitik pronominal `-ku`, `-mu`, atau `-nya`; tidak ada lema terpisah untuk bentuk gabungan tersebut dan tidak ada perubahan batch/index kamus.

GitHub Actions **Run #205 selesai dengan conclusion success**; **382/382 tes regresi lulus**. Log mengonfirmasi validasi kamus lengkap memuat **3.025 lema** dan validasi valensi serta tahapan validasi lain pada workflow berhasil. [Lihat Run #205](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46042081787).

**Batas penting:** parser saat ini masih memperlakukan `-ku/-mu` pada host NOUN sebagai posesif berdasarkan POS host; ia belum memberi label fungsi refleksif pada keseluruhan frasa `diriku/dirimu`. Untuk `dirinya`, fungsi `-nya` tetap unresolved antara posesif dan definit/anforis. Tes ini memastikan pengenalan morfologi dan mendokumentasikan batas tersebut, bukan menyatakan analisis refleksif sudah selesai. Pembedaan fungsi refleksif harus ditangani pada lapisan sintaksis/konteks dengan bukti yang memadai.

### Kandidat hubungan referensi refleksif untuk diri + klitik — validasi tertunda (28 November 2026)

Parser diperluas untuk mengekspos kandidat hubungan referensi refleksif pada frasa objek dengan host lema `diri`. Pemeriksaan dibatasi pada kecocokan orang antara satu subjek pronominal eksplisit dan klitik:
- `aku/saya` + `diriku`
- `kamu/engkau/kau` + `dirimu`
- `dia/ia/beliau` + `dirinya`

Keluaran baru mempertahankan `reference_relation: null`, mengisi `reference_relation_candidate: "reflexive"` dengan status `candidate_by_person_agreement`, dan mencatat `antecedent_candidate`. Kandidat alternatif `reflexive/non_reflexive` tetap dipertahankan karena kecocokan orang saja belum membuktikan koreferensi secara semantik. Jika orang subjek tidak cocok atau subjek pronominal eksplisit tidak tunggal, hubungan tetap `unresolved`. Fungsi klitik yang sudah ada tidak diubah: `-ku/-mu` tetap dianalisis sebagai penanda posesif pada host NOUN, sedangkan fungsi `-nya` tetap unresolved antara posesif dan definit/anforis.

Tes integrasi diperluas untuk tiga pasangan yang cocok dan satu pasangan tidak cocok (`Aku melihat dirimu.`) agar sistem tidak mengklaim refleksif hanya berdasarkan bentuk `diri` + klitik. GitHub Actions Run #210 selesai dengan conclusion success. Pekerjaan tetap berstatus parsial karena metadata tersebut hanya kandidat koreferensi, bukan resolusi refleksif final. [Lihat Run #210](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46042754768).

**Batas:** ini hanya menghasilkan kandidat koreferensi berdasarkan kesesuaian orang pada pola objek sederhana. Sistem belum melakukan resolusi anafora lintas kalimat, belum menangani frasa subjek majemuk atau pronomina plural, dan belum memutuskan semua pemakaian refleksif/nonrefleksif. Tidak ada perubahan kamus atau indeks.

### Pengujian klitik posesif pada frasa nominal subjek — Run #211 (27 November 2026)

Tes integrasi pipeline penuh ditambahkan untuk kalimat `Bukuku jatuh.`. Bentuk `bukuku` dikenali melalui host NOUN + klitik `-ku`, dapat mengisi peran subjek dalam pola S-P, dan metadata parser mempertahankan fungsi `possessive` serta `nominal_phrase_role: subject`. Ini melengkapi pengujian klitik nominal yang sebelumnya terutama memakai posisi objek (`Dia lihat bukuku.`).

GitHub Actions **Run #211 selesai dengan conclusion success**; **384/384 tes regresi lulus**. Log mengonfirmasi validasi kamus lengkap memuat **3.025 lema** dalam 60 batch, evaluasi POS development, dan tahapan validasi workflow berhasil. [Lihat Run #211](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46043106171).

**Batas:** pengujian ini memastikan posisi frasa nominal subjek untuk satu contoh `-ku); belum membuktikan semua klitik dapat digunakan pada semua jenis frasa nominal atau semua posisi sintaksis. Fungsi `-nya` tetap ambigu antara posesif dan definit/anforis; relasi refleksif tetap kandidat yang belum diputuskan. Tidak ada perubahan kamus atau indeks.


### Pengujian klitik nominal -mu dan -nya pada frasa subjek — Run #213 (28 November 2026)

Tes integrasi pipeline penuh diperluas untuk dua bentuk subjek nominal: `Bukumu jatuh.` dan `Bukunya jatuh.`. Pada `Bukumu`, host `buku` dikenali sebagai NOUN dengan klitik `-mu`, fungsi posesif dipertahankan, dan frasa mengisi peran subjek pada pola S-P. Pada `Bukunya`, host NOUN dengan klitik `-nya` juga dapat mengisi peran subjek pada pola S-P, tetapi fungsi klitik tetap `unresolved` dengan kandidat `possessive` dan `definite_anaphoric`.

Percobaan awal memakai kalimat `Rumahmu besar.` gagal karena parser belum mendukung predikat adjektival sederhana dengan subjek nominal yang tidak memiliki penanda pronominal eksplisit. Contoh uji `-mu` kemudian diganti menjadi `Bukumu jatuh.` agar pengujian mengisolasi dukungan klitik pada posisi subjek tanpa memperluas cakupan predikat nonverbal. Kegagalan percobaan awal dicatat sebagai batas parser, bukan disembunyikan.

GitHub Actions **Run #213 selesai dengan conclusion success**; **386/386 tes regresi lulus**. Log juga mengonfirmasi validasi kamus lengkap memuat **3.025 lema** dalam 60 batch serta validasi valensi, dataset POS, dan evaluasi development berhasil. [Lihat Run #213](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46078924646).

**Batas:** hasil ini menguji masing-masing satu contoh `-mu` dan `-nya` pada posisi subjek dengan predikat verbal. Ini belum membuktikan cakupan semua klitik pada seluruh posisi atau seluruh struktur frasa nominal. `-nya` tetap ambigu antara posesif dan definit/anforis. Predikat adjektival dengan subjek nominal biasa maupun berklitik belum menjadi cakupan parser yang tervalidasi. Tidak ada perubahan kamus atau indeks.

### Pengujian tambahan bentuk turunan + klitik — Run #214 dan #215 (28 November 2026)

Dua tes integrasi morfologi tambahan memperluas cakupan bentuk berklitik tanpa menambah lema atau mengubah batch/index kamus:

- **Run #214 — `memilikinya`:** menguji bentuk verbal turunan `memiliki` yang diikuti klitik `-nya`. Analisis menghasilkan satu kandidat klitik dengan `base_form: memiliki`, aturan `clitic_nya`, dan kecocokan lema `milik` sebagai `derived_form`. GitHub Actions sukses. [Lihat Run #214](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46079795753).
- **Run #215 — `perasaanmu`:** menguji bentuk nominal turunan `perasaan` yang diikuti klitik `-mu`. Analisis menghasilkan satu kandidat dengan `base_form: perasaan`, aturan `clitic_mu`, dan kecocokan lema `rasa` sebagai `derived_form`. GitHub Actions sukses. [Lihat Run #215](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46080089810).

**Batas:** kedua tes memvalidasi pengenalan kandidat morfologi dan kecocokan bentuk turunan pada contoh terpilih. Tes ini tidak menyatakan fungsi sintaksis/semantis klitik telah diselesaikan untuk semua konteks. Khusus `-nya`, ambiguitas fungsi pada host nominal tetap dipertahankan; tidak ada perubahan kamus atau indeks.

### Pengujian tambahan bentuk turunan + klitik -nya — Run #216 (28 November 2026)

Tes integrasi morfologi menambahkan bentuk nominal turunan `perasaan` + klitik `-nya` melalui token `perasaannya`. Analisis menghasilkan satu kandidat klitik dengan `base_form: perasaan`, aturan `clitic_nya`, dan kecocokan lema `rasa` sebagai `derived_form`.

GitHub Actions **Run #216 selesai dengan conclusion success**; **389/389 tes regresi lulus**. [Lihat Run #216](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46080236697).

**Batas:** tes ini memvalidasi pengenalan morfologi bentuk turunan + klitik pada satu contoh tambahan. Tes ini tidak menyelesaikan fungsi sintaksis/semantis `-nya` pada semua konteks; ambiguitas nominal posesif vs definit/anforis tetap dipertahankan. Tidak ada lema, batch, atau indeks kamus yang diubah.

### Pengujian tambahan bentuk turunan verbal + klitik -ku — Run #217 (28 November 2026)

Tes integrasi menambahkan bentuk `memilikiku`, dengan dasar turunan `memiliki` dan klitik `-ku`. Analisis menghasilkan satu kandidat dengan aturan `clitic_ku`, `base_form: memiliki`, serta kecocokan lema `milik` sebagai `derived_form`.

GitHub Actions **Run #217 selesai dengan conclusion success**; **390 tes regresi dijalankan**. [Lihat Run #217](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46080373836).

**Batas:** ini memvalidasi pengenalan morfologi untuk satu bentuk turunan verbal berklitik `-ku`, bukan seluruh variasi sintaksis atau semantisnya. Tidak ada lema, batch, atau indeks kamus yang diubah.

### Pengujian tambahan bentuk turunan verbal + klitik -mu — Run #218 (28 November 2026)

Tes integrasi menambahkan bentuk `memilikimu`, dengan dasar turunan `memiliki` dan klitik `-mu`. Analisis menghasilkan satu kandidat dengan aturan `clitic_mu`, `base_form: memiliki`, serta kecocokan lema `milik` sebagai `derived_form`.

GitHub Actions **Run #218 selesai dengan conclusion success**; **391 tes regresi dijalankan**. [Lihat Run #218](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46080502303).

**Batas:** tes ini memvalidasi pengenalan morfologi untuk satu bentuk turunan verbal berklitik `-mu`, bukan seluruh variasi sintaksis atau semantisnya. Tidak ada lema, batch, atau indeks kamus yang diubah.

### Pengujian tambahan bentuk turunan nominal + klitik -ku — Run #219 (28 November 2026)

Tes integrasi menambahkan bentuk `perasaanku`, dengan dasar turunan `perasaan` dan klitik `-ku`. Analisis menghasilkan satu kandidat dengan aturan `clitic_ku`, `base_form: perasaan`, serta kecocokan lema `rasa` sebagai `derived_form`.

GitHub Actions **Run #219 selesai dengan conclusion success**; **392 tes regresi dijalankan**. [Lihat Run #219](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46080600275).

Dengan ini, seri enam tes representatif Run #214–219 mencakup ketiga klitik (`-ku`, `-mu`, `-nya`) pada host turunan verbal (`memiliki`) dan nominal (`perasaan`). Cakupan ini menilai pengenalan morfologi melalui pipeline nyata; bukan bukti bahwa fungsi sintaksis atau semantik semua bentuk sudah terselesaikan. Tidak ada lema, batch, atau indeks kamus yang diubah.
