# Sistem Bahasa — Chatbot Lokal Offline Tanpa LLM

> **Status:** Pengembangan aktif — kamus berisi 3.013 lema dalam 60 batch; Tahap 2.5 (POS) dinyatakan selesai. Evaluasi development POS kontekstual mencapai coverage 98,0% dan selective accuracy 100,0%; lima abstention berupa nama orang ditunda ke tahap konteks. Parser kalimat v1.6 tersedia sebagai fondasi Tahap 2.6. GitHub Actions Run #114: 242/242 regression tests lulus.
> **Target utama:** sistem pengolahan bahasa untuk chatbot yang berjalan langsung di HP Android, tanpa layanan cloud, API berbayar, maupun LLM.

> **Checklist utama proyek:** lihat [Checklist Pengembangan](docs/CHECKLIST_PENGEMBANGAN.md) untuk daftar seluruh tahap dan pekerjaan yang sudah/belum selesai.

> **Status pekerjaan tahap pengolahan kata:** lihat [Dokumen Status Pengembangan](docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md) untuk progres, file yang sudah dibuat, pengujian, dan urutan pekerjaan berikutnya.

## 1. Gambaran proyek

**Sistem Bahasa** adalah proyek untuk membangun fondasi pengolahan Bahasa Indonesia agar sistem dapat mengenali kata, memahami hubungan makna, mengolah struktur kalimat, menggunakan konteks, dan pada tahap berikutnya menyusun jawaban.

Proyek ini **tidak menggunakan LLM**. Sistem dikembangkan dari komponen bahasa yang lebih terstruktur: kamus leksikal, aturan bahasa, hubungan antarkonsep, pengelolaan konteks, dan mesin pemrosesan.

Tujuan awal bukan mengumpulkan dialog siap pakai untuk dihafalkan chatbot. Fondasi pertama adalah **kamus kosakata sehari-hari dan bahasa gaul** yang berisi informasi linguistik setiap kata. Sistem nantinya diharapkan dapat mengolah kombinasi kata dan struktur kalimat, bukan hanya mencocokkan kalimat yang pernah disimpan.

Embedding **belum menjadi kebutuhan pada tahap awal**. Komponen ini akan dievaluasi kemudian jika pengujian menunjukkan bahwa pencarian berdasarkan aturan dan hubungan makna eksplisit belum cukup. Embedding, jika digunakan, hanya membantu pencarian kemiripan semantik; bukan mesin pembuat jawaban.

## 2. Prinsip dan batasan

- **On-device:** pemrosesan dilakukan di perangkat Android.
- **Offline-first:** setelah aplikasi dan seluruh aset yang diperlukan tersedia di HP, fitur inti dapat berjalan tanpa internet.
- **Tanpa LLM:** tidak menggunakan model bahasa generatif besar maupun pemanggilan LLM eksternal.
- **Tanpa cloud/API:** pesan pengguna tidak dikirim ke server untuk diproses.
- **Tanpa biaya layanan berjalan:** tidak membutuhkan biaya server atau token/API. Pengunduhan awal tetap dapat memakai kuota internet.
- **Ringan:** dirancang dengan sasaran perangkat Android sekitar RAM 6 GB; kebutuhan nyata harus diukur melalui prototipe.
- **Privasi lokal:** data percakapan disimpan di perangkat sesuai pengaturan aplikasi.
- **Bertahap dan terukur:** struktur data serta kemampuan sistem diuji sebelum diperluas.

## 3. Sasaran kamus tahap pertama

Target awal adalah **3.000 entri kosakata Bahasa Indonesia sehari-hari**, termasuk bahasa gaul, singkatan, dan variasi penulisan yang umum digunakan dalam percakapan.

Kamus ini **bukan kumpulan dialog**. Satu entri mewakili kata atau bentuk leksikal dan menyimpan informasi tentang kata tersebut.

Informasi yang direncanakan untuk setiap entri:

- ID unik dan lema/kata utama.
- Bentuk kata atau variasi ejaan.
- Kelas kata, misalnya nomina, verba, adjektiva, adverbia, atau partikel.
- Definisi atau makna.
- Bentuk dasar dan bentuk turunan/imbuhan jika relevan.
- Sinonim, antonim, dan kata terkait jika tersedia.
- Ragam bahasa: baku, informal, slang, singkatan, atau bentuk regional bila kelak ditambahkan.
- Catatan konteks dan contoh penggunaan singkat bila diperlukan untuk menjelaskan makna.

Contoh konseptual:

| Kata | Kelas/ragam | Makna | Hubungan |
|---|---|---|---|
| makan | verba | memasukkan makanan ke dalam tubuh | makanan, memakan |
| lapar | adjektiva | merasa perlu makan | kenyang |
| mager | informal/slang | malas bergerak atau melakukan aktivitas | malas bergerak |
| banget | adverbia informal | sangat; menyatakan tingkat yang tinggi | sangat |

Contoh tersebut hanya ilustrasi format, bukan entri final.

### Prinsip penyusunan 3.000 entri

1. Utamakan kata yang benar-benar sering muncul dalam percakapan sehari-hari.
2. Masukkan bahasa gaul dan singkatan yang umum, dengan makna serta ragam bahasanya diberi label.
3. Bedakan kata yang bentuknya sama tetapi memiliki makna berbeda.
4. Catat hubungan kata secara eksplisit jika dapat dipastikan.
5. Hindari duplikasi lema; variasi ejaan dapat ditautkan ke entri utama.
6. Jangan mengejar jumlah dengan mengisi data yang tidak jelas atau tidak terverifikasi.

Target 3.000 adalah sasaran versi kamus pertama, bukan klaim bahwa jumlah tersebut cukup untuk mencakup seluruh Bahasa Indonesia.

## 4. Arsitektur sistem yang direncanakan

~~~text
Masukan pengguna
      |
      v
Normalisasi teks
      |
      v
Pengenalan dan analisis bentuk kata
      |
      v
Kamus leksikal + hubungan makna
      |
      v
Analisis struktur kalimat
      |
      v
Pemrosesan makna dan konteks
      |
      v
Mesin aturan dan penalaran terbatas
      |
      v
Pemilihan / pembentukan respons
      |
      v
Jawaban
~~~

Komponen pencarian semantik berbasis embedding dapat ditambahkan sebagai modul opsional setelah kebutuhan dan manfaatnya terbukti lewat pengujian.

### Komponen utama

1. **Kamus leksikal**
   - Menyimpan kosakata, lema, definisi, kelas kata, bentuk turunan, variasi, dan ragam bahasa.
   - Tahap awal berfokus pada 3.000 entri percakapan sehari-hari dan bahasa gaul.
   - Tidak menjadikan kumpulan dialog sebagai pengganti kamus.

2. **Pengolah bentuk kata**
   - Mengenali bentuk dasar, imbuhan, pengulangan, dan variasi penulisan.
   - Menormalisasi teks tanpa menghilangkan informasi yang dapat mengubah makna.

3. **Jaringan hubungan makna**
   - Menghubungkan sinonim, antonim, kategori, bagian-keseluruhan, pelaku, tindakan, objek, dan konsep terkait.
   - Hubungan harus disimpan dengan jenis relasi yang jelas, bukan sekadar daftar kata yang mirip.

4. **Mesin tata bahasa**
   - Menganalisis kelas dan fungsi kata dalam kalimat.
   - Mengembangkan pengenalan subjek, predikat, objek, pelengkap, keterangan, serta pola kalimat secara bertahap.

5. **Mesin pemrosesan makna dan konteks**
   - Menggabungkan informasi kata dan struktur kalimat untuk menafsirkan maksud.
   - Menggunakan konteks percakapan yang relevan dan terbatas.
   - Menangani ambiguitas dan meminta klarifikasi bila diperlukan.

6. **Rule Engine dan Response Engine**
   - Menjalankan aturan pemrosesan dan memilih atau menyusun respons berdasarkan hasil analisis.
   - Menggunakan pengetahuan dan pola respons yang dirancang, bukan mengklaim menghasilkan bahasa bebas setara LLM.

7. **Penyimpanan lokal**
   - Menyimpan kamus, relasi, aturan, konfigurasi, dan konteks percakapan yang diperlukan.
   - SQLite atau format lokal lain akan dievaluasi berdasarkan kebutuhan.

8. **Modul embedding opsional (belum diputuskan)**
   - Baru dipertimbangkan setelah kamus, aturan, dan mesin pemrosesan dasar diuji.
   - Jika diperlukan, digunakan untuk membantu pencarian kandidat berdasarkan kemiripan semantik.
   - Pemilihan model mempertimbangkan dukungan Bahasa Indonesia, lisensi, ukuran, latensi, RAM, dan kompatibilitas Android.
   - Embedding tidak dianggap sebagai pengganti kamus, tata bahasa, pemahaman konteks, atau mesin pembentuk jawaban.

## 5. Rencana pengembangan bertahap

### Tahap 0 — Spesifikasi dan desain data
- [ ] Menetapkan cakupan kosakata sehari-hari dan bahasa gaul.
- [ ] Menentukan skema entri kamus dan jenis relasi antarkata.
- [ ] Menetapkan aturan penamaan, ID, deduplikasi, dan validasi data.
- [ ] Menyiapkan contoh data kecil untuk menguji skema sebelum mengisi ribuan entri.

**Hasil tahap:** spesifikasi kamus dan format data yang konsisten, disertai sampel kecil untuk menguji struktur sejak awal.

**Catatan pengujian dini:** sampel kecil ini juga dipakai kembali pada tahap berikutnya sebagai uji regresi. Dengan begitu, perubahan skema, normalisasi, dan aturan bahasa dapat diketahui dampaknya sebelum diterapkan ke seluruh kamus.

### Tahap 1 — Kamus 3.000 entri
- [ ] Mengumpulkan lema/kata sehari-hari yang relevan.
- [ ] Menambahkan definisi, kelas kata, ragam bahasa, dan bentuk terkait.
- [ ] Memasukkan bahasa gaul serta singkatan umum dengan label yang sesuai.
- [ ] Menautkan sinonim, antonim, dan relasi makna yang dapat dipastikan.
- [ ] Memeriksa duplikasi, kelengkapan, dan konsistensi setiap entri.
- [ ] Membuat pencarian kata dan bentuk variasinya.

#### Penyempurnaan metadata kamus

Setelah 3.000 lema terkumpul, metadata kamus disempurnakan secara bertahap per batch. Pengayaan ini merupakan bagian dari penyelesaian kualitas kamus versi 1.0, bukan penambahan target jumlah lema.

Metadata yang diperiksa dan dilengkapi jika relevan:
- Variasi bentuk atau ejaan yang benar-benar digunakan.
- Bentuk turunan yang terbentuk secara morfologis.
- Sinonim yang benar-benar sepadan dalam konteks makna.
- Antonim yang merupakan lawan makna yang tepat.
- Kata atau istilah yang memiliki hubungan semantik atau konteks.
- Catatan penggunaan untuk menjelaskan ragam, konteks, ambiguitas, atau perbedaan makna.

Aturan penyempurnaan:
1. Akurasi linguistik lebih penting daripada banyaknya kolom yang terisi.
2. Kolom metadata boleh tetap kosong jika tidak ada informasi yang dapat dipastikan.
3. Jangan mengisi sinonim dengan kata yang hanya berhubungan, atau bentuk turunan dengan gabungan kata yang tidak terbentuk secara morfologis.
4. Penyempurnaan metadata tidak boleh mengubah ID, lema, kelas kata, ragam, maupun definisi yang sudah ada. Perubahan pada data inti harus melalui pemeriksaan dan revisi tersendiri.
5. Setiap batch diperiksa kembali setelah diperbarui untuk memastikan struktur dan data inti tetap konsisten.

**Kriteria selesai:** tersedia kamus versi 1.0 dengan target 3.000 entri yang terstruktur, dapat dicari, dan lolos pemeriksaan kualitas data, termasuk penyempurnaan metadata yang relevan dan akurat.

### Tahap 2 — Pengolahan kata dan tata bahasa dasar
- [ ] Membuat prototipe pemrosesan awal dengan sampel kamus yang representatif.
- [ ] Menguji sampel secara berulang untuk menemukan masalah struktur data dan aturan sedini mungkin.
- [ ] Membuat normalisasi teks.
- [ ] Mengenali bentuk dasar dan bentuk berimbuhan.
- [ ] Mengidentifikasi kelas kata.
- [ ] Membuat analisis pola dan fungsi kata dalam kalimat.
- [ ] Menguji kalimat dengan susunan serta variasi kata yang berbeda.

**Kriteria selesai:** sistem dapat memproses bentuk kata dan struktur kalimat sederhana menggunakan data serta aturan yang eksplisit.

### Tahap 3 — Hubungan makna dan pemrosesan konteks
- [ ] Memperluas jaringan relasi antarkata dan konsep.
- [ ] Menggabungkan analisis leksikal dengan struktur kalimat.
- [ ] Mengembangkan penafsiran maksud dan ambiguitas.
- [ ] Mengelola konteks percakapan lintas beberapa giliran.
- [ ] Membuat mekanisme klarifikasi saat informasi tidak cukup.

**Kriteria selesai:** sistem dapat mengolah sejumlah kalimat baru dari kombinasi kosakata dan aturan, serta menggunakan konteks sederhana secara konsisten.

### Tahap 4 — Evaluasi kebutuhan embedding
Tahap ini dilakukan setelah prototipe pengolahan kata, tata bahasa, relasi makna, dan konteks dapat dijalankan pada kasus uji nyata. Embedding tidak dievaluasi hanya berdasarkan perkiraan atau sebelum mesin dasar memiliki hasil pembanding.

- [ ] Menguji kemampuan pencarian dan pemrosesan tanpa embedding.
- [ ] Mengidentifikasi kasus nyata yang belum tertangani oleh prototipe dan aturan dasar.
- [ ] Menyusun kumpulan kasus uji pembanding agar manfaat embedding dapat diukur secara objektif.
- [ ] Membandingkan manfaat embedding dengan kompleksitas dan biaya sumber daya.
- [ ] Jika manfaatnya terbukti, mengevaluasi model embedding Bahasa Indonesia/multibahasa dan lisensinya.
- [ ] Mengukur kualitas, ukuran, latensi, RAM, dan kompatibilitas Android.

**Kriteria selesai:** ada keputusan berbasis hasil pengujian apakah embedding diperlukan. Proyek tetap dapat dilanjutkan tanpa embedding jika manfaatnya tidak sebanding.

### Tahap 5 — Integrasi Android offline
- [ ] Membuat antarmuka aplikasi Android.
- [ ] Mengintegrasikan kamus, pengolah kata, mesin tata bahasa, relasi makna, aturan, dan penyimpanan lokal.
- [ ] Memastikan pemrosesan inti berjalan di perangkat.
- [ ] Menguji penggunaan dalam mode pesawat setelah aset tersedia.
- [ ] Menguji instalasi, pemulihan data, dan penanganan kesalahan.

**Kriteria selesai:** prototipe dapat menjalankan skenario uji inti tanpa koneksi internet.

### Tahap 6 — Optimasi dan perluasan
- [ ] Mengukur dan mengoptimalkan RAM, CPU, baterai, serta penyimpanan.
- [ ] Memperbaiki kesalahan analisis berdasarkan hasil pengujian.
- [ ] Memperluas kosakata dan relasi secara terkontrol.
- [ ] Menguji salah ketik, bahasa informal, kalimat ambigu, dan percakapan panjang.
- [ ] Menyusun dokumentasi dan versi rilis.

### Pengembangan terpisah — Adaptive Lexicon (setelah sistem inti selesai)

Fitur ini merupakan **pengembangan lanjutan yang terpisah**, bukan bagian dari target penyelesaian sistem inti dan kamus versi pertama. Pengerjaannya baru dimulai setelah fondasi sistem, kamus 3.000 entri, pengolahan kata, tata bahasa, hubungan makna, pemrosesan konteks, dan integrasi offline selesai disempurnakan serta diuji.

**Tujuan:** memungkinkan sistem menemukan kosakata yang belum tercatat, mempelajari penggunaannya dari konteks, lalu memperbarui kamus lokal secara terkontrol.

Rancangan kemampuan:

1. **Deteksi kata tak dikenal** — menemukan token atau bentuk kata yang belum cocok dengan lema, variasi, maupun aturan morfologi yang tersedia.
2. **Pengumpulan konteks** — menyimpan contoh kalimat dan konteks lokal yang relevan, dengan perlindungan privasi serta kendali pengguna.
3. **Analisis kandidat** — memperkirakan kelas kata, makna, dan kemungkinan hubungan berdasarkan konteks serta pengetahuan bahasa yang sudah ada.
4. **Pemeriksaan duplikasi dan kualitas** — memastikan kandidat bukan salah ketik, variasi ejaan, bentuk turunan, atau lema yang sudah tercatat.
5. **Validasi bertahap** — mengumpulkan bukti dari beberapa penggunaan. Kandidat dengan keyakinan rendah tetap ditandai sebagai belum terverifikasi dan tidak langsung menjadi entri resmi.
6. **Pembaruan kamus lokal** — setelah memenuhi aturan validasi, kandidat dapat dipromosikan ke kamus perangkat. Perubahan harus memiliki jejak asal, versi, dan mekanisme koreksi/pembatalan.

**Prinsip teknis:**

- Dirancang **offline-first** dan tidak mewajibkan AI cloud, LLM, atau API berbayar.
- Deteksi kata baru, pencatatan konteks, pencocokan bentuk, dan pemeriksaan duplikasi dapat dilakukan dengan aturan serta data lokal.
- Penafsiran makna kata yang benar-benar baru atau sangat ambigu akan memiliki keterbatasan tanpa model/pengetahuan tambahan. Sistem harus boleh menunda keputusan, meminta konfirmasi, atau menandai kandidat untuk tinjauan—bukan mengarang definisi.
- Sinkronisasi atau bantuan layanan eksternal, jika kelak dipertimbangkan, bersifat opsional dan harus mendapat persetujuan pengguna; bukan syarat agar fitur inti bekerja.
- Kamus dasar yang sudah tervalidasi tidak boleh tertimpa otomatis oleh hasil pembelajaran yang belum pasti.

**Kriteria penerimaan fitur:** kata baru dapat dideteksi dan dikumpulkan, kandidat dapat diperiksa dari konteks, duplikasi dapat dicegah, dan hanya entri yang lolos validasi yang dapat memperbarui kamus lokal. Fitur ini baru dirancang dan dibangun setelah sistem inti serta kamus versi pertama selesai disempurnakan.

## 6. Strategi pengujian

Pengujian harus membedakan kemampuan mengenali kata, menganalisis struktur, dan menafsirkan makna. Contoh uji meliputi:

- Kata baku, kata informal, slang, dan singkatan.
- Bentuk dasar, imbuhan, dan pengulangan.
- Kata yang memiliki lebih dari satu makna.
- Sinonim dan antonim dalam konteks.
- Kalimat dengan susunan berbeda tetapi makna serupa.
- Kalimat dengan kata serupa tetapi maksud berbeda.
- Salah ketik dan variasi penulisan.
- Kalimat ambigu serta konteks lintas beberapa giliran.

Metrik yang dicatat:
- Ketepatan pencarian lema dan identifikasi kelas kata.
- Ketepatan analisis bentuk serta struktur kalimat.
- Ketepatan relasi makna dan interpretasi konteks.
- Tingkat kesalahan dan keberhasilan meminta klarifikasi.
- Latensi, RAM, CPU, baterai, dan ukuran penyimpanan.
- Keberhasilan berjalan tanpa jaringan.

## 7. Teknologi yang akan dievaluasi

Pilihan teknis belum dikunci sebelum prototipe:

- **Android:** Kotlin/Android sebagai kandidat aplikasi utama.
- **Penyimpanan data:** JSON atau format terstruktur untuk tahap awal; SQLite dapat dievaluasi untuk aplikasi.
- **Pemrosesan bahasa:** modul dan aturan lokal yang dapat diuji secara terpisah.
- **Embedding:** opsional; ONNX Runtime Mobile atau TensorFlow Lite hanya dievaluasi jika tahap evaluasi membuktikan kebutuhannya.

Ukuran model atau target seperti 80 MB tidak ditetapkan sebagai kewajiban karena embedding belum diputuskan. Semua target performa harus didasarkan pada pengukuran nyata.

## 8. Peran GitHub

GitHub digunakan untuk:
- Menyimpan source code, dokumentasi, skema kamus, data uji, dan perubahan versi.
- Mencatat pekerjaan melalui commit dan issue.
- Mengelola konfigurasi build yang diperlukan.

GitHub **bukan tempat menjalankan chatbot**. Aplikasi berjalan di HP. GitHub Actions bersifat opsional dan proyek tidak boleh bergantung pada kuota Actions atau layanan cloud berbayar untuk menjalankan chatbot.

### Alur perubahan kamus dan penggunaan Actions

- Kamus disusun dalam batch yang umumnya berisi sekitar 50 lema; jumlah per batch boleh kurang atau lebih, dan keseimbangan dapat disesuaikan pada batch berikutnya. Jumlah 50 bukan syarat lulus/gagal.
- Sebelum menambahkan batch, periksa INDEX terbaru dan seluruh 8 token shard untuk mendeteksi duplikasi lema, variasi, serta bentuk turunan.
- Setelah setiap batch, periksa ID dan lema unik, konsistensi data, serta pembaruan INDEX dan shard sesuai. Jangan menambah atau menghapus entri hanya demi memaksakan jumlah 50.
- Pemeriksaan batch rutin dilakukan tanpa menjalankan GitHub Actions.
- Workflow **Dictionary Audit** hanya berjalan melalui pemicu manual (workflow_dispatch), bukan otomatis pada setiap push atau pull request.
- Jalankan audit besar melalui GitHub Actions setelah target 3.000 entri tercapai, atau jika memang diperlukan audit menyeluruh lebih awal.

Jangan memasukkan token, password, data pribadi, atau riwayat percakapan pengguna ke repository. Data kamus harus diperiksa sumber dan lisensinya sebelum dimasukkan atau didistribusikan.

## 9. Hal yang tidak menjadi target

- Tidak membuat atau memasang LLM/GGUF.
- Tidak menggunakan API ChatGPT atau API AI berbayar.
- Tidak mengirim pesan ke cloud untuk diproses.
- Tidak menjadikan kumpulan dialog sebagai inti kamus.
- Tidak menganggap embedding sebagai mesin pembuat kalimat.
- Tidak menjanjikan kemampuan setara ChatGPT.

## 10. Definisi keberhasilan proyek

Proyek mencapai target awal ketika:

1. Kamus versi 1.0 memiliki 3.000 entri kosakata percakapan sehari-hari dan bahasa gaul yang terstruktur.
2. Sistem dapat mencari kata, mengenali variasi bentuk, dan mengakses relasi maknanya.
3. Sistem dapat menganalisis struktur kalimat sederhana.
4. Sistem dapat menggabungkan informasi kata, struktur, dan konteks untuk memproses sejumlah maksud kalimat.
5. Sistem dapat mengakui ketidakpastian atau meminta klarifikasi.
6. Prototipe Android menjalankan pemrosesan inti secara lokal dan offline.
7. Sistem tidak memerlukan LLM, cloud, API, atau biaya layanan berjalan.

---

**Catatan:** dokumen ini adalah rencana pengembangan bertahap. Target 3.000 entri merupakan sasaran kamus versi pertama. Kebutuhan embedding, teknologi final, ukuran aplikasi, dan performa akan ditentukan berdasarkan hasil prototipe serta pengujian.

## Status parser bahasa

Parser konservatif saat ini telah mencapai v1.2: selain memisahkan beberapa klausa berverba eksplisit, hasilnya menyimpan label hubungan untuk penghubung yang dikenali (`dan`, `atau`, `tetapi`, `namun`, `karena`, `sebab`, `walaupun`, `meskipun`, `lalu`, `kemudian`, dan `ketika`). Label yang belum didukung tidak ditebak. GitHub Actions [Run #93](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45955025367) lulus dengan **222/222 tes**. Ini masih kerangka sintaksis sederhana, bukan pemahaman semantik lengkap; batasan dan cakupan uji rinci dicatat di `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.

## Status parser bahasa

Parser konservatif telah mencapai v1.3. Selain koordinasi beberapa klausa dan label penghubung, parser kini mengenali pola terbatas klausa subordinatif di depan klausa utama, misalnya `Karena dia makan, aku pulang.` dan `Ketika dia makan, aku pulang.`. Klausa awal tanpa predikat teridentifikasi tidak dipaksakan. GitHub Actions [Run #96](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45955536612) lulus dengan **227/227 tes**. Batas implementasi dicatat dalam `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.


## Status parser bahasa

Parser konservatif mencapai v1.4. Perluasan terbaru menangani bentuk terbatas klausa konsesif eliptis berpredikat adjektival, seperti `Walaupun lelah, dia bekerja.`. Subjek yang dilesapkan tetap kosong dan hasil ditandai `partial`; sistem tidak menebak atau menyalin subjek dari klausa utama. Cakupan serta hasil validasi terbaru dicatat di `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.

Validasi parser v1.4 melalui GitHub Actions [Run #97](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45956239387) berhasil dengan **229/229 regression tests lulus**. Validasi kamus lengkap 3.000 lema, dataset POS, dan evaluasi development juga berhasil.


Parser v1.5 menambahkan pola subordinatif setelah klausa utama, misalnya `Aku pulang karena hujan turun.`. Penghubung sebab/temporal/konsesi yang dikenali tidak lagi diperlakukan sebagai koordinasi setara pada pola tersebut. Hasil validasi dicatat di `docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md`.

Validasi parser v1.5 melalui GitHub Actions [Run #99](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45956517467) berhasil dengan **232/232 regression tests lulus**. Validasi kamus lengkap 3.000 lema, dataset POS, dan evaluasi development juga berhasil.


## Status tahap dan fokus pengembangan terkini — 27 November 2026

### Tahap 2.5 — Pengenalan kelas kata (POS): selesai

- Kamus tervalidasi: 60 batch, **3.013 lema**.
- Dataset POS: 100 kalimat / 543 token; 60 development dan 40 test.
- POS kontekstual pada development: 250/255 token dikenali; **coverage 98,0%**, accuracy 98,0%, selective accuracy 100,0%.
- Tidak ada kesalahan pada prediksi POS kontekstual yang dikeluarkan.
- Lima abstention yang tersisa adalah lima kemunculan dari tiga nama orang. Nama orang tidak dipaksakan menjadi lema kamus atau label POS pada tahap ini; pengenalannya ditunda ke tahap konteks/memory.
- Test split 40 kalimat tetap ditahan dan tidak digunakan untuk penyetelan.
- GitHub Actions [Run #114](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45965451485) berhasil: validasi kamus, dataset POS, evaluasi development, dan **242/242 regression tests lulus**.

### Tahap 2.6 — Analisis struktur kalimat: dilanjutkan

Parser kini berada pada versi **v1.6**. Tahap 2.6 kini dilanjutkan dengan tambahan struktur keluaran yang memisahkan kepala predikat dari pewatas modal, negasi, dan adverbial; rentang `roles.predicate` lama tetap dipertahankan agar kompatibel.

Langkah berikutnya adalah memperluas analisis frasa verba/modal dan memisahkan inti predikat dari pewatasnya, kemudian menguji variasi susunan kalimat sederhana. Perluasan dilakukan bertahap dengan regression tests dan tetap mempertahankan perilaku konservatif: struktur yang belum didukung dilaporkan, bukan ditebak.

Tahap 2.7 (dataset dan pengujian terpadu) tetap berjalan sebagai pekerjaan pelengkap: perluas cakupan contoh bahasa baku, informal, slang, salah ketik, imbuhan, dan kata ulang. Test split tetap tersegel.

Tahap 3 (hubungan makna dan konteks), evaluasi embedding opsional, dan integrasi Android mengikuti urutan roadmap. Tidak ada audit ulang 60 batch yang dijadwalkan, dan perubahan lema baru tetap memerlukan persetujuan eksplisit pengguna.
