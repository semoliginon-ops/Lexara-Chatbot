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

**Status keputusan dan implementasi:** skema disetujui pengguna. Validator struktural dan 15 tes khusus telah dibuat. Run #129 berhasil menguji seluruh 60 batch / 3.014 entri dan menjalankan 273 tes regresi; semua lulus. Kompatibilitas data lama terbukti pada pemuatan kamus dan pemeriksaan valensi. Validator ini memeriksa struktur, bukan kebenaran linguistik anotasi. Langkah berikutnya adalah menyusun anotasi terbatas pada beberapa sense terpilih, meninjau setiap frame berdasarkan makna sense, lalu menambahkan pengujian integrasi parser. Tidak ada penambahan lema kamus yang diperlukan.

**Anotasi pilot pertama — 4 sense (27 November 2026):** setelah persetujuan pengguna, metadata valensi dimasukkan pada empat sense yang sudah ada:
- `muncul` / `K1475-S1`: satu frame, SUBJ/THEME.
- `lihat` / `K0034-S1`: SUBJ/EXPERIENCER dan OBJ/THEME.
- `buka` / `K0065-S1`: dua frame alternatif dengan struktur sintaktis sama, masing-masing SUBJ/AGENT atau SUBJ/CAUSER; OBJ/PATIENT.
- `makan` / `K0013-S1`: SUBJ/AGENT; OBJ/PATIENT dengan `required: false`.

Anotasi ini terbatas pada empat sense tersebut. Dua frame `buka` memodelkan alternatif peran semantis pada posisi SUBJ; objek pada `makan` dinyatakan opsional. Belum ada klaim bahwa seluruh variasi valensi atau semua konstruksi aktif/pasif telah tercakup. Tahap berikutnya adalah validasi CI atas perubahan data dan tes integrasi terarah pada kalimat contoh serta kasus negatif/ambigu.
