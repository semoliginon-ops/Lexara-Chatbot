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
- `CE000003`: `jam` S1, cue `alarm`.
- `CE000004`: `jam` S2, cue `menit`.

Semua aturan sengaja berstatus `proposed` dan berkekuatan `weak`. Cue berasal dari definisi, istilah terkait, atau catatan penggunaan pada entri kamus yang dirujuk di field `source`. Cue tersebut hanya petunjuk awal; kehadirannya tidak membuktikan sense secara mutlak. Secara khusus, `alarm` juga dapat muncul dalam konteks pengaturan durasi, sehingga aturan untuk jam S1 perlu ditinjau hati-hati.

Aturan proposed tidak menghasilkan evidence aktif dan tidak dapat memengaruhi selector. Tidak ada aturan `reviewed`, `strong`, atau pemilihan sense otomatis yang dibuat.

## 4. Kasus yang belum diberi aturan

- `tolong`: perlu contoh kalimat yang membedakan tindakan membantu dari ungkapan permintaan. Cue seperti `minta` atau `bantuan` berisiko cocok pada kedua fungsi sehingga belum aman dipakai sebagai pembeda.
- `jalan`, `bisa`, `cerita`, `pesan`, `disiplin`, dan `tetap`: sense memiliki POS berbeda. POS kontekstual yang sudah tersedia dapat membantu menyaring kandidat; aturan sense khusus tidak ditambahkan hanya untuk mengulang pekerjaan POS.
- Tidak ada aturan yang dibuat untuk lema lain karena belum ada dasar cue yang cukup spesifik dalam data yang diperiksa.

## 5. Batas dan keputusan yang diperlukan

1. Inventaris ini belum merupakan validasi linguistik final.
2. Semua aturan tetap `proposed` sampai pengguna meninjau ketepatan cue, polarity, dan alasan linguistiknya.
3. Tidak boleh menaikkan strength menjadi `strong` hanya karena cue tampak relevan.
4. Belum ada integrasi entrypoint/runtime. Penentuan titik pemanggilan orchestrator merupakan pekerjaan berikutnya setelah kandidat aturan ditinjau.
5. Tidak ada perubahan pada kamus, indeks, Concept Layer, parser, POS, morfologi, analyzer, generator, selector, atau orchestrator.
