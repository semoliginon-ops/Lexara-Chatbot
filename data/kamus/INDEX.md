# Indeks Utama Kamus — Sistem Bahasa

**Status:** Batch 001, Batch 002, Batch 003, dan Batch 004 disetujui dan terdaftar
**Target:** 3.000 lemma unik untuk Kamus v1.0
**Sumber aturan:** ../../docs/KAMUS.md

File ini adalah daftar induk untuk melacak semua lemma yang masuk ke kamus. Setiap kosakata baru harus diperiksa terhadap indeks ini sebelum ditambahkan ke data kamus. Tujuannya mencegah duplikasi, menjaga ID tetap unik, dan memastikan variasi ejaan diarahkan ke entri kanonis yang benar.

## 1. Aturan wajib sebelum menambah kata

1. Normalisasikan kandidat untuk pencarian duplikat: Unicode NFC, hapus spasi di awal/akhir, dan gunakan huruf kecil untuk pencocokan dasar.
2. Jangan menghapus tanda hubung atau apostrof secara otomatis.
3. Periksa kandidat terhadap lemma, variants, derived_forms, dan alias yang sudah ada.
4. Satu lemma dapat memiliki beberapa sense dan POS; jangan membuat lemma terpisah hanya karena maknanya berbeda.
5. Bentuk turunan tidak otomatis dihitung sebagai lemma baru.
6. ID harus unik dan stabil.
7. Kandidat yang belum jelas harus ditandai untuk tinjauan, bukan langsung disahkan.

## 2. Status entri

| Status | Arti |
|---|---|
| approved | Sudah diperiksa dan masuk hitungan target |
| review | Masih perlu verifikasi |
| rejected | Tidak digunakan |
| merged | Digabung atau diarahkan ke lemma kanonis lain |

Hanya status approved yang dihitung ke target 3.000 lemma.

## 3. Indeks lemma kanonis

| ID | Lemma kanonis | POS | Register | Variasi/bentuk turunan | Status | Catatan |
|---|---|---|---|---|---|---|
| K0109 | adik | NOUN | neutral, informal | adik-adik | approved | Batch 003 |
| K0152 | air | NOUN | neutral | berair, mengairi, pengairan | approved | Batch 004 |
| K0188 | ajar | VERB | neutral | mengajar, diajarkan, pengajaran, ajaran | approved | Batch 004 |
| K0001 | aku | PRON | neutral, informal | — | approved | Batch 001 |
| K0058 | ambil | VERB | neutral | mengambil, diambil, pengambilan, pengambil | approved | Batch 002 |
| K0102 | anak | NOUN | neutral | beranak, anak-anak, anakan | approved | Batch 003 |
| K0153 | api | NOUN | neutral | berapi, perapian | approved | Batch 004 |
| K0105 | ayah | NOUN | neutral | — | approved | Batch 003 |
| K0169 | ayam | NOUN | neutral | ayam-ayam | approved | Batch 004 |
| K0076 | baca | VERB | informal, neutral | membaca, dibaca, bacaan, pembaca, pembacaan | approved | Batch 002 |
| K0124 | badan | NOUN | neutral | berbadan | approved | Batch 003 |
| K0041 | bagus | ADJ | neutral, informal | bagusan | approved | Batch 001 |
| K0048 | banget | ADV | informal, slang | — | approved | Batch 001 |
| K0016 | bangun | VERB | neutral | membangunkan, terbangun, bangunkan | approved | Batch 001 |
| K0033 | bantu | VERB | neutral | membantu, dibantu, bantuan, pembantu | approved | Batch 001 |
| K0103 | bapak | NOUN | neutral, informal | kebapakan | approved | Batch 003 |
| K0093 | baper | ADJ | slang, informal | kebaperan | approved | Batch 002 |
| K0060 | bawa | VERB | neutral | membawa, dibawa, bawaan, pembawa | approved | Batch 002 |
| K0187 | belajar | VERB | neutral | mempelajari, dipelajari, pembelajaran, pelajar | approved | Batch 004 |
| K0055 | beli | VERB | neutral, informal | membeli, dibeli, pembelian, pembeli | approved | Batch 002 |
| K0147 | belum | ADV | neutral, informal | — | approved | Batch 003 |
| K0165 | beras | NOUN | neutral | — | approved | Batch 004 |
| K0072 | berdiri | VERB | neutral | mendirikan, didirikan, berdirinya, pendirian | approved | Batch 002 |
| K0192 | berita | NOUN | neutral | pemberitaan, memberitakan, diberitakan | approved | Batch 004 |
| K0043 | besar | ADJ | neutral | membesar, besaran, kebesaran | approved | Batch 001 |
| K0138 | besok | ADV | neutral, informal | — | approved | Batch 003 |
| K0036 | bicara | VERB | neutral | berbicara, pembicaraan, membicarakan, pembicara | approved | Batch 001 |
| K0026 | bisa | VERB, NOUN | neutral, informal | kemampuan | approved | Batch 001 |
| K0095 | bokek | ADJ | slang, informal | kebokekan | approved | Batch 002 |
| K0144 | boleh | ADV | neutral | membolehkan, diperbolehkan, kebolehan | approved | Batch 003 |
| K0086 | bosan | ADJ | neutral, informal | membosankan, kebosanan, dibosankan | approved | Batch 002 |
| K0162 | buah | NOUN | neutral | berbuah, buah-buahan | approved | Batch 004 |
| K0099 | bucin | NOUN | slang, informal | kebucinan | approved | Batch 002 |
| K0065 | buka | VERB | neutral | membuka, dibuka, terbuka, pembukaan, pembuka | approved | Batch 002 |
| K0160 | bunga | NOUN | neutral | berbunga, berbunga-bunga | approved | Batch 004 |
| K0047 | capek | ADJ | informal | cape | approved | Batch 001 |
| K0063 | cari | VERB | neutral | mencari, dicari, pencarian, pencari | approved | Batch 002 |
| K0045 | cepat | ADJ | neutral | mempercepat, kecepatan, tercepat | approved | Batch 001 |
| K0191 | cerita | NOUN, VERB | neutral, informal | bercerita, menceritakan, diceritakan, penceritaan | approved | Batch 004 |
| K0114 | cinta | NOUN | neutral | mencintai, dicintai, tercinta, percintaan | approved | Batch 003 |
| K0053 | cuci | VERB | neutral | mencuci, dicuci, cucian, pencucian | approved | Batch 002 |
| K0170 | daging | NOUN | neutral | berdaging | approved | Batch 004 |
| K0018 | datang | VERB | neutral | kedatangan, mendatangi | approved | Batch 001 |
| K0161 | daun | NOUN | neutral | berdaun, dedaunan | approved | Batch 004 |
| K0090 | dekat | ADJ | neutral | mendekat, mendekati, didekati, kedekatan | approved | Batch 002 |
| K0181 | demam | NOUN | neutral | berdemam | approved | Batch 004 |
| K0035 | dengar | VERB | neutral | mendengar, terdengar, pendengaran, kedengaran | approved | Batch 001 |
| K0004 | dia | PRON | neutral | — | approved | Batch 001 |
| K0183 | dokter | NOUN | neutral | kedokteran | approved | Batch 004 |
| K0049 | dong | PART | informal, slang | — | approved | Batch 001 |
| K0071 | duduk | VERB | neutral | menduduki, diduduki, duduk-duduk, kedudukan | approved | Batch 002 |
| K0023 | duit | NOUN | informal, slang | — | approved | Batch 001 |
| K0029 | enggak | ADV | informal, slang | nggak, gak, ga | approved | Batch 001 |
| K0092 | gabut | ADJ | slang, informal | kegabutan | approved | Batch 002 |
| K0171 | garam | NOUN | neutral | menggarami, penggaraman | approved | Batch 004 |
| K0100 | gercep | ADJ | slang, informal | — | approved | Batch 002 |
| K0008 | gue | PRON | slang, informal | gw, gua | approved | Batch 001 |
| K0172 | gula | NOUN | neutral | bergula | approved | Batch 004 |
| K0158 | gunung | NOUN | neutral | pegunungan, bergunung | approved | Batch 004 |
| K0185 | guru | NOUN | neutral | keguruan | approved | Batch 004 |
| K0149 | hanya | ADV | neutral | — | approved | Batch 003 |
| K0130 | hari | NOUN | neutral | harian, sehari-hari, berhari-hari | approved | Batch 003 |
| K0143 | harus | ADV | neutral | keharusan | approved | Batch 003 |
| K0116 | hati | NOUN | neutral | berhati | approved | Batch 003 |
| K0177 | haus | ADJ | neutral | kehausan | approved | Batch 004 |
| K0120 | hidung | NOUN | neutral | berhidung | approved | Batch 003 |
| K0104 | ibu | NOUN | neutral | keibuan | approved | Batch 003 |
| K0168 | ikan | NOUN | neutral | perikanan | approved | Batch 004 |
| K0078 | ingat | VERB | neutral | mengingat, diingat, ingatan, teringat, mengingatkan | approved | Batch 002 |
| K0025 | ingin | VERB | neutral | keinginan, menginginkan | approved | Batch 001 |
| K0197 | internet | NOUN | neutral | — | approved | Batch 004 |
| K0112 | istri | NOUN | neutral | beristri | approved | Batch 003 |
| K0030 | iya | INTJ | neutral, informal | ya | approved | Batch 001 |
| K0020 | jalan | NOUN | neutral | jalanan, perjalanan, berjalan | approved | Batch 001 |
| K0145 | jangan | PART | neutral, informal | — | approved | Batch 003 |
| K0190 | jawab | VERB | neutral | menjawab, dijawab, jawaban | approved | Batch 004 |
| K0042 | jelek | ADJ | informal, neutral | kejelekan | approved | Batch 001 |
| K0056 | jual | VERB | neutral | menjual, dijual, jualan, penjual, penjualan | approved | Batch 002 |
| K0150 | juga | ADV | neutral | — | approved | Batch 003 |
| K0096 | julid | ADJ | slang, informal | menjulid, kejulidan | approved | Batch 002 |
| K0193 | kabar | NOUN | neutral, informal | mengabari, dikabari, mengabarkan | approved | Batch 004 |
| K0141 | kadang | ADV | informal, neutral | kadang-kadang | approved | Batch 003 |
| K0108 | kakak | NOUN | neutral, informal | kakak-kakak | approved | Batch 003 |
| K0123 | kaki | NOUN | neutral | berkaki | approved | Batch 003 |
| K0006 | kami | PRON | neutral, formal | — | approved | Batch 001 |
| K0003 | kamu | PRON | neutral, informal | — | approved | Batch 001 |
| K0151 | karena | CONJ | neutral | — | approved | Batch 003 |
| K0044 | kecil | ADJ | neutral | mengecil, kecil-kecilan | approved | Batch 001 |
| K0068 | keluar | VERB | neutral | mengeluarkan, dikeluarkan, keluaran, pengeluaran | approved | Batch 002 |
| K0101 | keluarga | NOUN | neutral | kekeluargaan | approved | Batch 003 |
| K0137 | kemarin | ADV | neutral, informal | — | approved | Batch 003 |
| K0178 | kenyang | ADJ | neutral | mengenyangkan, kekenyangan | approved | Batch 004 |
| K0117 | kepala | NOUN | neutral | mengepalai, dikepalai | approved | Batch 003 |
| K0094 | kepo | ADJ | slang, informal | kepo-kepoan | approved | Batch 002 |
| K0021 | kerja | NOUN | neutral | bekerja, pekerjaan, pekerja, mengerjakan | approved | Batch 001 |
| K0061 | kirim | VERB | neutral | mengirim, dikirim, kiriman, pengiriman, pengirim | approved | Batch 002 |
| K0005 | kita | PRON | neutral | — | approved | Batch 001 |
| K0198 | komputer | NOUN | neutral | komputasi, mengomputasi | approved | Batch 004 |
| K0173 | kopi | NOUN | neutral | berkopi | approved | Batch 004 |
| K0046 | lambat | ADJ | neutral | melambat, memperlambat, kelambatan | approved | Batch 001 |
| K0155 | langit | NOUN | neutral | langit-langit | approved | Batch 004 |
| K0176 | lapar | ADJ | neutral, informal | kelaparan | approved | Batch 004 |
| K0073 | lari | VERB | neutral, informal | berlari, melarikan, pelari, larian | approved | Batch 002 |
| K0156 | laut | NOUN | neutral | lautan | approved | Batch 004 |
| K0097 | lebay | ADJ | slang, informal | berlebihan | approved | Batch 002 |
| K0034 | lihat | VERB | neutral | melihat, terlihat, penglihatan, kelihatan | approved | Batch 001 |
| K0009 | lu | PRON | slang, informal | lo, elu | approved | Batch 001 |
| K0079 | lupa | VERB | neutral, informal | melupakan, dilupakan, terlupa, kelupaan | approved | Batch 002 |
| K0091 | mager | ADJ | slang, informal | kemageran | approved | Batch 002 |
| K0074 | main | VERB | informal, neutral | bermain, memainkan, dimainkan, permainan, pemain | approved | Batch 002 |
| K0013 | makan | VERB | neutral | memakan, dimakan, makanan, pemakan | approved | Batch 001 |
| K0134 | malam | NOUN | neutral | bermalam, semalaman | approved | Batch 003 |
| K0106 | mama | NOUN | informal | — | approved | Batch 003 |
| K0051 | mandi | VERB | neutral | bermandi, memandikan, mandian | approved | Batch 002 |
| K0082 | marah | ADJ | neutral | memarahi, dimarahi, kemarahan, pemarah | approved | Batch 002 |
| K0052 | masak | VERB | neutral, informal | memasak, dimasak, masakan, pemasak | approved | Batch 002 |
| K0148 | masih | ADV | neutral | — | approved | Batch 003 |
| K0067 | masuk | VERB | neutral | memasuki, dimasuki, kemasukan, masukan | approved | Batch 002 |
| K0118 | mata | NOUN | neutral | bermata, memata-matai | approved | Batch 003 |
| K0024 | mau | VERB | neutral, informal | kemauan, menghendaki | approved | Batch 001 |
| K0007 | mereka | PRON | neutral | — | approved | Batch 001 |
| K0014 | minum | VERB | neutral | meminum, diminum, minuman, peminum | approved | Batch 001 |
| K0201 | mobil | NOUN | neutral | bermobil | approved | Batch 004 |
| K0200 | motor | NOUN | neutral, informal | bermotor, motoris | approved | Batch 004 |
| K0121 | mulut | NOUN | neutral | bermulut | approved | Batch 003 |
| K0142 | mungkin | ADV | neutral | kemungkinan | approved | Batch 003 |
| K0186 | murid | NOUN | neutral | — | approved | Batch 004 |
| K0069 | naik | VERB | neutral | menaiki, menaikkan, dinaikkan, kenaikan | approved | Batch 002 |
| K0128 | nama | NOUN | neutral | bernama, menamai, dinamai, penamaan | approved | Batch 003 |
| K0136 | nanti | ADV | neutral, informal | — | approved | Batch 003 |
| K0164 | nasi | NOUN | neutral | — | approved | Batch 004 |
| K0098 | ngaret | VERB | slang, informal | mengaret | approved | Batch 002 |
| K0038 | ngobrol | VERB | informal, slang | obrolan, mengobrol | approved | Batch 001 |
| K0075 | nonton | VERB | informal | menonton, ditonton, tontonan, penonton | approved | Batch 002 |
| K0182 | obat | NOUN | neutral | mengobati, diobati, pengobatan, obatan | approved | Batch 004 |
| K0031 | oke | INTJ | informal | ok, okay | approved | Batch 001 |
| K0037 | omong | NOUN | informal | mengomong, omongan | approved | Batch 001 |
| K0010 | orang | NOUN | neutral | perorangan | approved | Batch 001 |
| K0113 | pacar | NOUN | informal, neutral | berpacaran, memacari | approved | Batch 003 |
| K0131 | pagi | NOUN | neutral | kepagian | approved | Batch 003 |
| K0040 | paham | VERB | neutral | memahami, pemahaman, dipahami | approved | Batch 001 |
| K0057 | pakai | VERB | neutral, informal | memakai, dipakai, pemakaian, pakaian | approved | Batch 002 |
| K0107 | papa | NOUN | informal | — | approved | Batch 003 |
| K0017 | pergi | VERB | neutral | kepergian, bepergian | approved | Batch 001 |
| K0125 | perut | NOUN | neutral | berperut | approved | Batch 003 |
| K0194 | pesan | NOUN, VERB | neutral | berpesan, memesan, dipesan, pesanan, pemesanan | approved | Batch 004 |
| K0080 | pikir | VERB | neutral | berpikir, memikirkan, dipikirkan, pikiran, pemikiran | approved | Batch 002 |
| K0159 | pohon | NOUN | neutral | pepohonan | approved | Batch 004 |
| K0196 | ponsel | NOUN | neutral, informal | — | approved | Batch 004 |
| K0019 | pulang | VERB | neutral | kepulangan, memulangkan | approved | Batch 001 |
| K0126 | rambut | NOUN | neutral | berambut | approved | Batch 003 |
| K0166 | roti | NOUN | neutral | roti-roti | approved | Batch 004 |
| K0012 | rumah | NOUN | neutral | perumahan, berumah | approved | Batch 001 |
| K0180 | sakit | ADJ | neutral, informal | kesakitan, menyakiti, penyakit | approved | Batch 004 |
| K0054 | sapu | VERB | neutral | menyapu, disapu, sapuan | approved | Batch 002 |
| K0110 | saudara | NOUN | neutral | bersaudara, persaudaraan | approved | Batch 003 |
| K0002 | saya | PRON | formal, neutral | — | approved | Batch 001 |
| K0115 | sayang | ADJ | neutral, informal | menyayangi, disayangi, kesayangan | approved | Batch 003 |
| K0163 | sayur | NOUN | neutral | sayuran | approved | Batch 004 |
| K0085 | sedih | ADJ | neutral | menyedihkan, kesedihan, bersedih | approved | Batch 002 |
| K0179 | sehat | ADJ | neutral | kesehatan, menyehatkan | approved | Batch 004 |
| K0135 | sekarang | ADV | neutral, informal | — | approved | Batch 003 |
| K0184 | sekolah | NOUN | neutral | bersekolah, persekolahan | approved | Batch 004 |
| K0140 | selalu | ADV | neutral | — | approved | Batch 003 |
| K0084 | senang | ADJ | neutral | menyenangkan, disenangi, kesenangan, bersenang-senang | approved | Batch 002 |
| K0199 | sepeda | NOUN | neutral | bersepeda, pesepeda | approved | Batch 004 |
| K0089 | sering | ADV | neutral | keseringan | approved | Batch 002 |
| K0132 | siang | NOUN | neutral | — | approved | Batch 003 |
| K0087 | sibuk | ADJ | neutral | menyibukkan, disibukkan, kesibukan | approved | Batch 002 |
| K0050 | sih | PART | informal, slang | — | approved | Batch 001 |
| K0133 | sore | NOUN | neutral | sore-sore | approved | Batch 003 |
| K0111 | suami | NOUN | neutral | bersuami | approved | Batch 003 |
| K0146 | sudah | ADV | neutral, informal | — | approved | Batch 003 |
| K0081 | suka | VERB | neutral, informal | menyukai, disukai, kesukaan, penyuka | approved | Batch 002 |
| K0157 | sungai | NOUN | neutral | bersungai | approved | Batch 004 |
| K0088 | susah | ADJ | neutral, informal | menyusahkan, kesusahan, dipersusah | approved | Batch 002 |
| K0175 | susu | NOUN | neutral | menyusui, persusuan | approved | Batch 004 |
| K0139 | tadi | ADV | neutral, informal | — | approved | Batch 003 |
| K0039 | tahu | VERB | neutral, informal | mengetahui, pengetahuan, ketahuan | approved | Batch 001 |
| K0083 | takut | ADJ | neutral | menakuti, ditakuti, ketakutan, penakut | approved | Batch 002 |
| K0154 | tanah | NOUN | neutral | bertanah, tanah-tanah | approved | Batch 004 |
| K0122 | tangan | NOUN | neutral | menangani, ditangani, penanganan | approved | Batch 003 |
| K0189 | tanya | VERB | neutral, informal | bertanya, menanyakan, ditanya, pertanyaan | approved | Batch 004 |
| K0059 | taruh | VERB | informal, neutral | menaruh, ditaruh, taruhan | approved | Batch 002 |
| K0174 | teh | NOUN | neutral | — | approved | Batch 004 |
| K0195 | telepon | NOUN, VERB | neutral | menelepon, ditelepon, teleponan | approved | Batch 004 |
| K0119 | telinga | NOUN | neutral | bertelinga | approved | Batch 003 |
| K0167 | telur | NOUN | neutral | bertelur | approved | Batch 004 |
| K0011 | teman | NOUN | neutral | berteman, pertemanan | approved | Batch 001 |
| K0062 | terima | VERB | neutral | menerima, diterima, penerimaan, penerima | approved | Batch 002 |
| K0028 | tidak | ADV | neutral, formal | — | approved | Batch 001 |
| K0015 | tidur | VERB | neutral | tertidur, menidurkan, tiduran | approved | Batch 001 |
| K0032 | tolong | VERB | neutral | menolong, pertolongan, penolong | approved | Batch 001 |
| K0077 | tulis | VERB | neutral | menulis, ditulis, tulisan, penulis, penulisan | approved | Batch 002 |
| K0064 | tunggu | VERB | neutral | menunggu, ditunggu, penantian, penunggu | approved | Batch 002 |
| K0070 | turun | VERB | neutral | menuruni, menurunkan, diturunkan, penurunan | approved | Batch 002 |
| K0066 | tutup | VERB | neutral | menutup, ditutup, tertutup, penutupan, penutup | approved | Batch 002 |
| K0022 | uang | NOUN | neutral | keuangan, menguangkan | approved | Batch 001 |
| K0129 | umur | NOUN | neutral | berumur, seumur | approved | Batch 003 |
| K0127 | wajah | NOUN | neutral | berwajah | approved | Batch 003 |

## 4. Kandidat yang digabung atau diperlakukan sebagai variasi

| Bentuk kandidat | Perlakuan | Catatan |
|---|---|---|
| bisa (mampu), bisa (racun) | Satu lemma: K0026 | Dua sense dengan POS VERB dan NOUN |
| gw, gua | Variasi lemma gue | Tidak dihitung sebagai lemma terpisah |
| lo, elu | Variasi lemma lu | Tidak dihitung sebagai lemma terpisah |
| nggak, gak, ga | Variasi lemma enggak | Tidak dihitung sebagai lemma terpisah |
| ok, okay | Variasi lemma oke | Tidak dihitung sebagai lemma terpisah |
| ya | Variasi lemma iya | Tidak dihitung sebagai lemma terpisah |
| cape | Variasi lemma capek | Tidak dihitung sebagai lemma terpisah |
| memakan, dimakan, makanan, dan bentuk turunan lain | Bentuk turunan lemma masing-masing | Tidak dihitung sebagai lemma terpisah |

## 5. Hitungan progres

- Lemma disetujui: **200 / 3.000**
- Kandidat dalam tinjauan: **0**
- Ditolak: **0**
- Digabung/alias: **7 kelompok variasi/polisemi tercatat**

Catatan: Batch 001 menghasilkan 49 lemma kanonis. Batch 002 menambahkan 50 lemma unik yang telah disetujui.

## 6. Alur kerja setiap batch

1. Ambil indeks dan data kamus terbaru dari repository.
2. Normalisasikan ejaan dan cari duplikasi terhadap lemma, variasi, dan bentuk turunan.
3. Periksa makna dan POS; pisahkan sense untuk polisemi/homograf.
4. Tetapkan ID setelah disetujui.
5. Tambahkan data batch dan perbarui indeks.
6. Jalankan validasi JSONL, ID unik, lemma kanonis unik, dan kode POS/register.
7. Catat perubahan dalam commit.

**Prinsip:** indeks dan data kamus di repository adalah sumber rujukan utama. Jangan mengandalkan ingatan percakapan untuk pemeriksaan duplikat.
