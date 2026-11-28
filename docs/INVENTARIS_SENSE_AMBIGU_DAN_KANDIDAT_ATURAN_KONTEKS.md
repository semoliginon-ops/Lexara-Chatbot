# Inventaris Sense Ambigu dan Kandidat Aturan Konteks — v1

**Tanggal pemeriksaan:** 28 November 2026  
**Status:** inventaris awal; kandidat aturan berstatus `proposed`, belum disetujui untuk penggunaan runtime.

## 1. Metode dan cakupan

Indeks kamus diperiksa lebih dahulu untuk memahami pembagian token dan batch. Setelah itu seluruh **60 batch / 3.025 entri** dibaca secara baca-saja dan dihitung jumlah sense per entri. Tidak ada batch, indeks, atau entri kamus yang diubah.

Ditemukan **9 lema dengan lebih dari satu sense**. Jumlah ini adalah inventaris struktural, bukan berarti kesembilan lema membutuhkan aturan konteks. Kandidat dipilah berdasarkan apakah perbedaan sense masih berada dalam POS yang sama atau sudah dapat dibedakan oleh POS.

## 2. Hasil inventaris

| Lema | Sense | Perbedaan yang tercatat | Penilaian awal |
|---|---|---|---|
| bangun (K0016) | S1 / S2 | VERB: terjaga dari tidur / berdiri atau menjadi tegak | **Layak ditinjau untuk konteks**; kedua sense sama-sama VERB |
| jalan (K0020) | S1 / S2 | NOUN: jalur / VERB: bergerak dengan kaki | Beda POS; bukan prioritas aturan sense v1 |
| bisa (K0026) | S1 / S2 | VERB: mampu / NOUN: zat beracun | Beda POS; bukan prioritas aturan sense v1 |
| tolong (K0032) | S1 / S2 | VERB: membantu / ungkapan meminta bantuan | **Perlu kajian lanjutan**; definisi membedakan tindakan dan fungsi ujaran, tetapi belum tersedia contoh pemakaian yang cukup untuk merumuskan cue aman |
| cerita (K0191) | S1 / S2 | NOUN: kisah / VERB: menyampaikan kisah | Beda POS; bukan prioritas aturan sense v1 |
| pesan (K0194) | S1 / S2 | NOUN: amanat / VERB: meminta sesuatu disediakan | Beda POS; bukan prioritas aturan sense v1 |
| jam (K0293) | S1 / S2 | NOUN: alat penunjuk waktu / satuan enam puluh menit | **Layak ditinjau untuk konteks**; kedua sense sama-sama NOUN |
| disiplin (K0788) | S1 / S2 | NOUN: ketaatan / ADJ: taat aturan | Beda POS; bukan prioritas aturan sense v1 |
| tetap (K3007) | S1 / S2 | ADJ: tidak berubah / ADV: terus melakukan | Beda POS; usage notes sudah memberi contoh pembeda POS |

## 3. Kandidat aturan konteks

Dataset awal disimpan di `data/context_rules/context_rules.jsonl` dengan empat aturan untuk dua lema yang paling jelas memiliki dua sense dalam POS yang sama:

- `CE000001`: `bangun` S1, cue `tidur`.
- `CE000002`: `bangun` S2, cue `berdiri`.
- `CE000003`: `jam` S1, cue `alarm` — **rejected**, karena tidak cukup spesifik.
- `CE000004`: `jam` S2, cue `menit`.

CE000001, CE000002, dan CE000004 tetap `proposed` dengan strength `weak`. CE000003 (`jam` S1, cue `alarm`) telah diubah menjadi `rejected`: kata alarm juga dapat muncul dalam konteks pengaturan durasi, sehingga tidak cukup membedakan jam sebagai alat dari jam sebagai satuan waktu.

Cue yang tersisa berasal dari definisi atau istilah terkait pada entri kamus yang dirujuk di field `source`. Semuanya masih petunjuk awal. Karena kondisi `token_present` hanya memeriksa kemunculan kata dalam observasi kalimat, cue lemah ini tidak membuktikan hubungan makna dengan target secara pasti. Selector v1 tidak menggunakan weak evidence untuk memilih sense.

Aturan proposed/rejected tidak menghasilkan evidence aktif. Tidak ada aturan `reviewed` atau `strong`, dan tidak ada pemilihan sense otomatis yang diaktifkan.

## 4. Kasus yang belum diberi aturan

- `tolong`: perlu contoh kalimat yang membedakan tindakan membantu dari ungkapan permintaan. Cue seperti `minta` atau `bantuan` berisiko cocok pada kedua fungsi sehingga belum aman dipakai sebagai pembeda.
- `jalan`, `bisa`, `cerita`, `pesan`, `disiplin`, dan `tetap`: sense memiliki POS berbeda. POS kontekstual yang sudah tersedia dapat membantu menyaring kandidat; aturan sense khusus tidak ditambahkan hanya untuk mengulang pekerjaan POS.
- Tidak ada aturan yang dibuat untuk lema lain karena belum ada dasar cue yang cukup spesifik dalam data yang diperiksa.

## 5. Batas dan keputusan yang diperlukan

1. Inventaris ini belum merupakan validasi linguistik final.
2. Tiga aturan masih `proposed`; satu aturan ditolak karena cue tidak cukup spesifik. Tidak ada aturan yang diaktifkan.
3. Tidak boleh menaikkan strength menjadi `strong` hanya karena cue tampak relevan.
4. Belum ada integrasi entrypoint/runtime. Penentuan titik pemanggilan orchestrator merupakan pekerjaan berikutnya setelah kandidat aturan ditinjau.
5. Tidak ada perubahan pada kamus, indeks, Concept Layer, parser, POS, morfologi, analyzer, generator, selector, atau orchestrator.


## 6. Bukti contoh kalimat yang ditemukan

Penelusuran dibatasi pada dua lema same-POS yang sudah dipilih; tidak menambah lema atau aturan baru.

### bangun

Arsip entri KBBI daring memuat dua contoh yang relevan:
- “anak itu berkali-kali terjatuh, namun ia selalu dapat bangun kembali” — mendukung pembacaan bangun sebagai kembali berdiri setelah jatuh.
- “setiap pagi ia bangun pukul 04.00” — mendukung pembacaan bangun sebagai terjaga dari tidur.

Sumber: https://kbbi.web.id/bangun (arsip KBBI daring; halaman menyatakan basis data utamanya mengacu pada KBBI Edisi III dan bukan laman resmi KBBI Daring terbaru).

Penilaian: contoh tersebut berguna sebagai bukti leksikografis untuk memeriksa perbedaan dua makna dalam kamus proyek. Namun, ini belum merupakan sampel korpus percakapan alami dan cue `pagi`, `pukul`, `terjatuh`, atau `kembali` belum boleh otomatis dijadikan aturan aktif. Aturan `tidur` dan `berdiri` tetap proposed/weak sampai ada bukti yang cocok dengan kondisi generator dan target token secara lebih aman.

### jam

Buku resmi Badan Pengembangan Bahasa dan Perbukuan, *Bentuk dan Pilihan Kata* (2019), menyatakan bahwa `jam` dapat bermakna durasi/jangka waktu maupun arloji/alat penunjuk waktu. Contoh durasi yang diberikan: “Para pekerja di Indonesia rata-rata bekerja selama delapan jam sehari.” Buku tersebut juga menjelaskan makna benda penunjuk waktu/arloji. Rujukan: https://badanbahasa.kemendikdasmen.go.id/resource/doc/files/Buku_Seri_Penyuluhan_2019_Bentuk_dan_Pilihan_Kata.pdf, bagian “Pemakaian Kata Jam dan Pukul”.

Penilaian: sumber resmi menguatkan bahwa kedua makna dalam entri proyek memang perlu dibedakan. Contoh yang tersedia secara eksplisit lebih kuat untuk sense durasi daripada sense alat. Namun, contoh pedoman kebahasaan bukan kumpulan korpus alami, dan kata `jam` tetap dapat digunakan secara bervariasi dalam ragam percakapan. Aturan `menit` tetap proposed/weak; cue `alarm` tetap rejected. Belum ada dasar untuk status reviewed/strong.

### Kesimpulan bukti

Bukti rujukan kamus dan pedoman resmi sudah ditemukan untuk mengonfirmasi perbedaan makna dasar. Bukti ini belum memenuhi standar korpus autentik dan belum cukup untuk mengaktifkan aturan. Tidak ada aturan baru, perubahan kode, atau perubahan runtime pada langkah ini.


## 7. Penelusuran korpus terbatas — 28 November 2026

Penelusuran lanjutan tetap dibatasi pada `bangun` dan `jam`. Sumber yang diperiksa adalah halaman Tutur yang menampilkan contoh dari korpus Leipzig `ind_mixed_2013`; Tutur menyatakan halaman `bangun` memuat 2.467 kalimat korpus dari satu juta kalimat.

### bangun

Halaman [Tutur — bangun](https://tutur.taratsa.id/kata/bangun/) menampilkan contoh korpus:
- “00 ini pria tak usah bangun tidur agar produksi hormon testosteronnya tak terganggu.” — konteksnya mendukung makna bangkit/terjaga dari tidur (S1).
- “Hakikat tauhid adalah membaca Al Qur’an dengan merenungi artinya dan bangun malam.” — konteks malam tidak cukup untuk memastikan apakah yang dimaksud terjaga atau tetap tidak tidur; tidak dipakai sebagai bukti pembeda.
- Contoh korpus lain yang ditampilkan tidak memberikan contoh jelas untuk makna berdiri setelah jatuh (S2).

Penilaian: ada satu contoh korpus yang relevan untuk S1, tetapi contoh yang tersedia belum memberi pasangan bukti yang seimbang untuk S1 dan S2. Cue `tidur` tetap hanya `proposed`/`weak`; cue `berdiri` belum didukung contoh korpus yang cukup. Jangan mengaktifkan salah satu aturan.

### jam

Halaman [Tutur — jam](https://tutur.taratsa.id/kata/jam/) memuat definisi dan contoh leksikografis, tetapi tidak menampilkan bagian “Contoh dari korpus” atau kalimat korpus yang dapat diperiksa. Angka frekuensi korpus pada halaman itu bukan bukti konteks per kalimat. Karena itu penelusuran ini belum menemukan contoh korpus yang dapat membedakan `jam` sebagai alat penunjuk waktu (S1) dari `jam` sebagai durasi (S2).

Penilaian: cue `menit` tetap `proposed`/`weak`, tanpa bukti korpus spesifik yang mengaitkannya dengan token target. Cue `alarm` tetap `rejected`.

### Kesimpulan dan batas berhenti

Penelusuran terbatas ini menambah satu contoh korpus yang relevan untuk `bangun` S1, tetapi belum menemukan bukti pasangan yang memadai untuk `bangun` S2 maupun contoh korpus kontekstual untuk `jam`. Bukti belum memenuhi syarat untuk mengubah status atau strength aturan. Tiga aturan tetap `proposed`/`weak`, satu tetap `rejected`; tidak ada aturan `reviewed` atau `strong`.

Pencarian dihentikan pada batas sumber yang diperiksa. Tidak dilakukan perluasan ke lema lain, tidak dibuat contoh buatan, dan tidak dilakukan perubahan kode, dataset aturan, kamus, parser, POS, atau runtime.
