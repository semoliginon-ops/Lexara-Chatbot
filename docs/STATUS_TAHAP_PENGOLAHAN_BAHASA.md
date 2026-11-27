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

### Rancangan awal metadata valensi verba — belum diterapkan

Rancangan berikut adalah arah desain untuk diuji, bukan perubahan skema kamus yang sudah disahkan atau data yang sudah dimigrasikan.

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

Contoh pemetaan di atas hanya ilustrasi desain. Belum ada sense kamus yang dianotasi, belum ada validator, dan belum ada perilaku parser yang berubah. Sebelum diterapkan, katalog harus diuji pada contoh positif dan negatif lintas jenis predikat, termasuk kalimat aktif, pasif, non-agentif, dan sense polisemi.

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

**Keputusan sementara:** jangan mengubah katalog 13 role yang telah disepakati. Catat CAUSER sebagai kandidat ekstensi yang perlu diuji lebih luas sebelum disetujui. Untuk sementara, kasus penyebab non-agentif yang tidak dapat direpresentasikan secara aman tetap belum dianotasi; jangan dipaksa menjadi AGENT atau STIMULUS.

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