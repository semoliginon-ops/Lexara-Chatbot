# Dokumentasi Kamus — Sistem Bahasa

**Status:** Rancangan awal  
**Versi:** 1.0-draft  
**Target awal:** 3.000 entri leksikal  
**Bahasa utama:** Bahasa Indonesia sehari-hari, termasuk ragam informal dan bahasa gaul

Dokumen ini khusus mengatur kamus leksikal Sistem Bahasa. Dokumen ini bukan kumpulan dialog, percakapan siap pakai, atau daftar jawaban chatbot.

## 1. Tujuan

Membangun basis kosakata terstruktur agar mesin bahasa dapat mengenali bentuk kata, makna, kelas kata, variasi pemakaian, dan hubungan antarkata. Kamus menjadi salah satu fondasi bagi pemrosesan kata, tata bahasa, pemahaman makna, dan pembentukan kalimat pada tahap berikutnya.

Kamus bukan mesin pemahaman lengkap. Kemampuan memahami kalimat tetap membutuhkan komponen lain seperti normalisasi, analisis morfologi, tata bahasa, representasi makna, konteks, dan aturan pemrosesan.

## 2. Ruang lingkup versi pertama

Target 3.000 entri adalah sasaran awal, bukan batas akhir bahasa yang dapat dipahami sistem.

Prioritas isi:
- Kosakata yang sering muncul dalam kehidupan sehari-hari.
- Kata benda, tindakan, sifat, keterangan, kata tugas, dan ekspresi.
- Bentuk baku dan bentuk informal.
- Bahasa gaul Indonesia yang umum digunakan.
- Singkatan, variasi ejaan, dan bentuk penulisan digital yang relevan.
- Bentuk turunan melalui imbuhan dan perubahan bentuk kata.
- Makna berbeda dari kata yang sama, jika memang ada.

Tidak termasuk sebagai entri utama:
- Dialog lengkap atau percakapan siap pakai.
- Kalimat jawaban chatbot.
- Paragraf contoh yang hanya mengulang dialog.
- Kata yang dibuat-buat tanpa penggunaan atau definisi yang dapat dipertanggungjawabkan.

Contoh kalimat boleh digunakan sebagai contoh pemakaian untuk menjelaskan makna, tetapi bukan sebagai entri kamus tersendiri.

## 3. Kelas kata (POS)

Untuk rancangan awal, kamus menggunakan 10 kelompok kelas kata kerja berikut. Klasifikasi ini merupakan taksonomi proyek dan dapat disempurnakan setelah diuji dengan data bahasa Indonesia nyata.

| Kode | Kelas kata | Keterangan | Contoh |
|---|---|---|---|
| NOUN | Nomina | Kata benda atau penamaan | rumah, meja, orang |
| VERB | Verba | Kata kerja atau tindakan | makan, tidur, berjalan |
| ADJ | Adjektiva | Kata sifat atau keadaan | besar, baik, malas |
| ADV | Adverbia | Kata yang menerangkan unsur lain | sangat, mungkin, selalu |
| PRON | Pronomina | Kata ganti | aku, kamu, mereka |
| NUM | Numeralia | Kata bilangan | satu, kedua, sepuluh |
| PREP | Preposisi | Kata depan/penanda relasi | di, ke, dari, untuk |
| CONJ | Konjungsi | Kata penghubung | dan, tetapi, karena |
| INTJ | Interjeksi | Kata seru atau ungkapan spontan | wah, aduh, eh |
| PART | Partikel/Artikula | Partikel penegas atau penanda tertentu | -lah, -kah, pun, si, sang |

Satu bentuk kata dapat memiliki lebih dari satu kelas kata atau makna. Setiap penggunaan yang berbeda harus dicatat sebagai sense/makna terpisah, bukan dipaksakan menjadi satu definisi.

## 4. Bahasa gaul dan ragam pemakaian

Bahasa gaul bukan kelas kata tersendiri. Bahasa gaul dicatat sebagai **ragam/register** atau penanda penggunaan, sementara kelas katanya tetap ditentukan berdasarkan fungsi kata tersebut.

Contoh:
- **gue**: PRON, register informal/gaul; padanan umum: saya atau aku sesuai konteks.
- **nongkrong**: VERB, register informal.
- **bokek**: ADJ, register informal/gaul.
- **mager**: bentuk leksikal informal yang bermakna malas bergerak atau enggan beraktivitas; kelas/fungsi dapat diberi catatan sesuai pemakaiannya.

Penanda register yang dapat digunakan:
- formal
- neutral
- informal
- slang
- regional
- technical
- archaic

Untuk bahasa daerah atau istilah regional, cantumkan wilayah jika diketahui. Jangan menganggap satu istilah berlaku di seluruh Indonesia.

## 5. Struktur data setiap entri

Setiap entri sebaiknya memiliki bidang berikut. Bidang wajib harus tersedia; bidang opsional boleh kosong jika informasinya belum diketahui.

| Field | Wajib | Fungsi |
|---|---|---|
| id | Ya | ID stabil dan unik |
| lemma | Ya | Bentuk dasar/kepala entri |
| pos | Ya | Satu atau lebih kode kelas kata |
| senses | Ya | Daftar makna; minimal satu |
| register | Ya | Ragam pemakaian |
| variants | Tidak | Ejaan atau bentuk variasi |
| derived_forms | Tidak | Bentuk berimbuhan/turunan |
| synonyms | Tidak | Sinonim yang sesuai makna |
| antonyms | Tidak | Antonim jika tersedia |
| related_terms | Tidak | Kata yang berkaitan secara konsep |
| usage_notes | Tidak | Catatan batasan dan konteks pemakaian |
| examples | Tidak | Contoh pemakaian singkat |
| source_notes | Tidak | Asal verifikasi atau catatan penyunting |

Contoh struktur JSON:

    {
      "id": "idn_verb_000001",
      "lemma": "makan",
      "pos": ["VERB"],
      "senses": [
        {
          "sense_id": "idn_verb_000001_s1",
          "definition": "Memasukkan makanan ke dalam mulut lalu menelannya.",
          "domain": ["aktivitas_sehari_hari"]
        }
      ],
      "register": ["neutral"],
      "variants": [],
      "derived_forms": ["memakan", "dimakan", "makanan"],
      "synonyms": ["menyantap"],
      "antonyms": [],
      "related_terms": ["makanan", "minum"],
      "usage_notes": [],
      "examples": ["Anak itu sedang makan."]
    }

Contoh di atas hanya ilustrasi skema, bukan keputusan bahwa semua relasi kata selalu saling dapat menggantikan. Sinonim, antonim, dan kata terkait harus diverifikasi berdasarkan makna tertentu.


### Metadata valensi per-sense

Skema metadata valensi per-sense telah disetujui sebagai bagian dari pengembangan tata bahasa. Field `valency_frames` bersifat **opsional** dan ditempatkan di dalam objek sense, bukan pada tingkat lemma.

- Sense yang belum memiliki `valency_frames` berarti belum dianotasi; bukan berarti tidak memiliki argumen.
- Satu sense dapat memiliki beberapa frame jika pola argumennya memang berbeda.
- Setiap frame memiliki `frame_id` dan daftar `arguments`.
- Setiap argumen memiliki `argument_id`, `syntactic_role`, `semantic_role`, `required`, dan `realizations`.
- Fungsi sintaksis awal: `SUBJ`, `OBJ`, `COMP`, `OBL`.
- Semantic role awal: `AGENT`, `CAUSER`, `EXPERIENCER`, `THEME`, `PATIENT`, `RECIPIENT`, `BENEFICIARY`, `INSTRUMENT`, `LOCATION`, `SOURCE`, `GOAL`, `RESULT`, `CONTENT`, `STIMULUS`.
- Tipe realisasi awal: `NP`, `PP`, `ADJP`, `CLAUSE`. Pembatas `prepositions` hanya berlaku pada realisasi `PP`.
- `semantic_role: null` hanya menyatakan bahwa role argumen belum diputuskan; bukan label role tambahan.
- `required` menyatakan status argumen dalam frame, bukan jaminan bahwa argumen selalu tampak pada permukaan kalimat. Voice dan pelesapan ditangani oleh lapisan terpisah.

Contoh berikut ilustratif dan bukan anotasi yang boleh langsung disalin ke entri kamus:

```json
{
  "sense_id": "contoh-S1",
  "valency_frames": [
    {
      "frame_id": "F1",
      "arguments": [
        {
          "argument_id": "A1",
          "syntactic_role": "SUBJ",
          "semantic_role": "AGENT",
          "required": true,
          "realizations": [{ "type": "NP" }]
        }
      ]
    }
  ]
}
```

Validator struktural tersedia di `tools/validasi_valensi.py`. Data lama tanpa metadata valensi tetap harus dapat dimuat oleh loader yang ada. Validasi struktur tidak membuktikan bahwa anotasi role atau frame benar secara linguistik; setiap anotasi tetap memerlukan tinjauan dan contoh uji.


## 6. Pemisahan bentuk kata dan makna

Kamus harus membedakan:
1. **Lemma:** bentuk kepala entri, misalnya kata bisa.
2. **Bentuk turunan:** bentuk yang mengalami imbuhan atau proses morfologi, misalnya memakan dari makan.
3. **Sense:** satu makna tertentu dari sebuah lemma.
4. **POS:** fungsi gramatikal kata pada penggunaan tertentu.
5. **Register:** tingkat/formalitas atau ragam penggunaan.

Contoh kata bisa memiliki sekurangnya dua makna:
- bisa = mampu atau sanggup; fungsi umumnya verba/modalitas.
- bisa = racun; nomina.

Kedua makna harus disimpan sebagai sense terpisah agar mesin tidak mencampuradukkan makna.

### Anotasi POS khusus bentuk turunan

POS pada bentuk turunan tidak boleh otomatis diwariskan dari lemma. Jika bentuk permukaan mengubah kelas kata atau memiliki fungsi gramatikal yang berbeda, entri dapat menambahkan field opsional `derived_forms_pos`. Field ini berupa objek yang memetakan bentuk turunan persis ke satu atau lebih label POS yang telah ditinjau, misalnya:

    "derived_forms": ["bekerja", "pekerjaan"],
    "derived_forms_pos": {
      "bekerja": ["VERB"],
      "pekerjaan": ["NOUN"]
    }

Pemetaan hanya berlaku untuk bentuk yang disebutkan secara eksplisit. Bentuk turunan lain tetap berstatus belum diketahui sampai dianotasi. Jangan mengisi field ini berdasarkan tebakan dari imbuhan saja.

## 7. Prinsip kualitas data

- Satu entri harus memiliki definisi yang jelas dan tidak melingkar.
- Hindari duplikasi lemma yang hanya berbeda kapitalisasi, kecuali ada alasan linguistik.
- Jangan menyamakan sinonim dengan kata yang sekadar berkaitan.
- Catat kelas kata berdasarkan fungsi, bukan hanya bentuk permukaan.
- Pisahkan makna yang berbeda.
- Beri label ragam informal/gaul secara konsisten.
- Tandai informasi yang belum terverifikasi; jangan mengarang definisi atau asal kata.
- Gunakan ejaan Unicode yang konsisten dan simpan bentuk asli variasi penulisan.
- Setiap perubahan data harus dapat ditinjau melalui version control.

## 8. Strategi pengumpulan 3.000 entri

Pengisian dilakukan bertahap per kelompok dan diperiksa sebelum digabungkan. Angka pembagian kategori tidak ditetapkan secara kaku di awal karena distribusi kelas kata harus mengikuti kebutuhan percakapan nyata dan hasil inventarisasi.

### 8.1 Prosedur batch dan pemeriksaan rutin

- Setiap batch umumnya berisi sekitar **50 lema baru**, tetapi jumlah aktual boleh kurang atau lebih. Pembagian dapat diseimbangkan pada batch berikutnya; karena itu, jumlah baris per batch bukan syarat kelulusan dan tidak boleh dijadikan alasan untuk menambah, menghapus, atau mengubah ID entri.
- Setiap lema menggunakan satu POS utama sesuai keputusan penyusunan batch.
- Sebelum menyusun batch baru, ambil INDEX terbaru dan periksa seluruh 8 token shard (a-c.tsv, d-f.tsv, g-i.tsv, j-l.tsv, m-o.tsv, p-r.tsv, s-u.tsv, dan v-z.tsv).
- Pemeriksaan duplikasi mencakup lema yang sudah ada, variasi ejaan, serta bentuk turunan yang tercatat.
- Setelah batch ditambahkan, lakukan pemeriksaan manual terhadap jumlah entri, keunikan ID dan lema, rentang ID, pembaruan shard, urutan alfabetis shard, serta konsistensi jumlah pada INDEX.
- INDEX dijaga tetap ringan sebagai ringkasan dan navigasi; definisi serta rincian linguistik tetap disimpan pada berkas batch.
- Pemeriksaan rutin setiap batch tidak menjalankan GitHub Actions. Hasil pemeriksaan manual dicatat sebelum melanjutkan ke batch berikutnya.

### 8.2 Audit menyeluruh dengan GitHub Actions

Workflow **Dictionary Audit** dikonfigurasi hanya dengan pemicu manual (workflow_dispatch). Workflow tidak berjalan otomatis pada setiap push atau pull request, agar penambahan batch rutin tidak menghabiskan kuota Actions.

Audit menyeluruh dijalankan setelah target **3.000 entri** tercapai. Audit lebih awal hanya dilakukan jika ada kebutuhan khusus untuk memeriksa keseluruhan data. Pemeriksaan manual per batch tetap dilakukan dan tidak digantikan oleh audit akhir.

Urutan kerja yang disarankan:
1. Tetapkan skema data dan kode kelas kata.
2. Kumpulkan kosakata umum yang paling sering dipakai.
3. Tambahkan bentuk informal dan bahasa gaul yang terverifikasi.
4. Tambahkan variasi ejaan dan singkatan digital.
5. Lengkapi makna, kelas kata, bentuk turunan, dan relasi.
6. Deteksi duplikasi dan konflik makna.
7. Jalankan validasi otomatis dan tinjauan manual.
8. Bekukan rilis awal setelah target dan pemeriksaan kualitas terpenuhi.

Jangan mengejar jumlah 3.000 dengan mengorbankan ketepatan. Entri yang belum jelas lebih baik ditandai untuk ditinjau daripada dipaksakan masuk.

### 8.3 Audit kualitas isi per batch

Audit kualitas isi dilakukan bertahap, satu berkas batch pada satu waktu, dimulai dari `batch-001.jsonl` hingga `batch-060.jsonl`. Audit ini melengkapi validasi struktur otomatis; keduanya memiliki tujuan berbeda.

Aturan kerja:

1. Periksa satu batch sampai selesai sebelum berpindah ke batch berikutnya. Jangan memuat atau menyalin seluruh 60 batch sekaligus ke konteks kerja.
2. Perlakukan berkas batch sebagai sumber data utama. INDEX hanya alat navigasi dan pemeriksaan lema/duplikasi; jangan memperbesar INDEX menjadi salinan isi kamus.
3. Tahap audit bersifat baca-saja. Jangan mengubah entri ketika pemeriksaan masih berlangsung.
4. Periksa struktur dan tipe data, konsistensi ID/lema, POS, sense/definisi, register, variasi, bentuk turunan, relasi, serta catatan pemakaian sesuai skema yang berlaku.
5. Catat setiap temuan dengan nama batch, ID entri, field terkait, jenis temuan, bukti, dan tingkat kepastian. Bedakan kesalahan yang dapat dibuktikan dari saran atau kasus yang perlu tinjauan linguistik.
6. Jangan menganggap field opsional yang kosong atau bentuk turunan yang tidak tercantum pada INDEX sebagai kesalahan jika skema memang mengizinkannya.
7. Setelah audit batch selesai, rangkum hasilnya: temuan wajib diperbaiki, temuan untuk ditinjau, dan tidak ada masalah yang ditemukan. Batch yang lolos tidak perlu diubah.
8. Perbaikan dilakukan terpisah setelah temuan ditinjau. Ubah hanya entri yang memiliki bukti cukup, pertahankan ID stabil dan kompatibilitas skema, lalu jalankan validator serta regression tests yang relevan.
9. Jangan mengubah data hanya demi merapikan tampilan atau mengejar keseragaman yang tidak diwajibkan skema. Jangan mengarang definisi, POS, relasi, atau bentuk turunan.
10. Catat kemajuan batch dan hasil verifikasi pada checklist proyek. Jika perubahan berisiko memengaruhi POS, morfologi, atau komponen lain, tambahkan regression test sebelum menyatakan perbaikan selesai.

Audit per batch tidak menggantikan validasi struktur seluruh kamus, dan lolosnya validator struktur tidak otomatis membuktikan bahwa seluruh definisi atau relasi linguistik sudah benar. Audit isi juga tidak boleh mengklaim kualitas semantik sempurna hanya berdasarkan pemeriksaan otomatis.

---

## 9. Validasi dan pengujian

Pemeriksaan minimum:
- Semua ID unik.
- Semua entri memiliki lemma, POS, dan minimal satu sense.
- Semua kode POS termasuk daftar yang diizinkan.
- Semua label register termasuk daftar yang diizinkan.
- Tidak ada referensi sinonim/antonim yang menunjuk ke ID yang tidak ada (jika relasi memakai ID).
- Bentuk turunan tidak otomatis dianggap sinonim dari lemma.
- Makna ganda tercatat sebagai sense berbeda.
- Variasi gaul memiliki label register dan, bila relevan, padanan atau catatan pemakaian.
- Data dapat dibaca dan dimuat secara offline di perangkat Android.

## 10. Format penyimpanan dan integrasi

Format sumber yang disarankan adalah JSON atau JSONL UTF-8 agar mudah diperiksa, divalidasi, dan diproses. Format final belum dikunci; pemilihan antara satu berkas JSON, beberapa berkas JSONL, atau SQLite dilakukan setelah ukuran dan pola akses data diuji.

Kamus harus dapat digunakan tanpa koneksi internet saat runtime. Pengembangan dan penyimpanan kode/data dilakukan di repository; aplikasi tidak boleh bergantung pada GitHub untuk menjalankan pencarian kamus.

## 11. Hubungan dengan komponen Sistem Bahasa

Kamus menyediakan data leksikal bagi komponen lain:
- Normalisasi teks: menghubungkan variasi ejaan dengan bentuk yang dikenali.
- Analisis morfologi: mengenali imbuhan dan bentuk turunan.
- Analisis POS: memperkirakan fungsi kata dalam kalimat.
- Mesin tata bahasa: memakai informasi kelas kata dan relasi sintaksis.
- Mesin makna: memakai sense dan hubungan konsep.
- Mesin konteks: membantu memilih makna yang tepat berdasarkan kalimat sekitar.

Embedding tidak menjadi prasyarat untuk menyusun kamus. Kebutuhannya akan dievaluasi setelah pencarian berbasis kamus dan aturan dasar diuji. Jika kelak dipakai, embedding hanya komponen pencarian kemiripan semantik dan bukan pengganti kamus atau mesin pembentukan jawaban.

## 12. Kriteria selesai untuk Kamus v1.0

Kamus v1.0 dapat dinyatakan siap ketika:
- Target 3.000 entri telah dicapai.
- Struktur data konsisten dan tervalidasi.
- Duplikasi utama telah diperiksa.
- Makna ganda dan kelas kata telah ditangani.
- Bahasa informal/gaul diberi label yang sesuai.
- Data dapat dimuat dan dicari secara offline.
- Tersedia catatan versi dan daftar isu data yang masih perlu diperbaiki.

---

**Catatan:** Kamus v1.0 adalah fondasi leksikal, bukan klaim bahwa Sistem Bahasa sudah mampu memahami seluruh bahasa Indonesia atau percakapan manusia.
