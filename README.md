# LEXARA CHATBOT
### Rule-Based Language System

**Lexara Chatbot** adalah proyek pengembangan sistem pemrosesan Bahasa Indonesia berbasis aturan (*rule-based*), dengan sasaran penggunaan secara lokal/offline pada perangkat Android.

Lexara dibangun dari komponen linguistik yang eksplisit dan dapat diuji: kamus, normalisasi, tokenisasi, pencocokan leksikal, morfologi, pengenalan kelas kata (POS), analisis sintaksis, relasi makna, konteks percakapan, serta mesin aturan untuk pemilihan dan pembentukan respons.

> **Status proyek — 27 November 2026:** Tahap 2.6 (analisis struktur kalimat dasar) masih aktif. Parser berada pada versi **v1.9**. Kamus berisi **3.019 lema dalam 60 batch**. GitHub Actions [Run #182](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46023874794) berhasil dengan **359/359 regression tests lulus**.

## Identitas proyek

| Bagian | Identitas |
|---|---|
| Merek | **LEXARA** |
| Nama produk/proyek | **Lexara Chatbot** |
| Definisi teknologi | **Rule-Based Language System** |
| Fokus bahasa saat ini | Bahasa Indonesia |
| Target eksekusi | Lokal/offline, termasuk perangkat Android |
| Repository | [semoliginon-ops/Lexara-Chatbot](https://github.com/semoliginon-ops/Lexara-Chatbot) |

## Visi dan tujuan

Lexara bertujuan menyediakan fondasi bahasa lokal yang dapat:

- mengenali kata, variasi penulisan, dan bentuk berimbuhan;
- menganalisis kelas kata serta fungsi kata dalam kalimat;
- menghubungkan kata dan konsep melalui relasi yang didefinisikan secara eksplisit;
- menafsirkan maksud dengan mempertimbangkan struktur dan konteks percakapan;
- memilih atau membentuk respons menggunakan aturan yang dapat diperiksa dan diuji;
- berjalan secara lokal/offline setelah kode dan aset yang diperlukan tersedia di perangkat.

Kemampuan tersebut dikembangkan bertahap. Target chatbot merupakan arah pengembangan, bukan klaim bahwa seluruh kemampuan percakapan sudah tersedia saat ini.

## Prinsip dan batasan

- **Rule-based:** keputusan pemrosesan didasarkan pada data dan aturan linguistik eksplisit yang dapat ditelusuri.
- **Lokal dan offline-first:** pemrosesan inti ditujukan berjalan di perangkat tanpa ketergantungan layanan cloud.
- **Bukan LLM/GGUF:** proyek ini tidak membangun, memasang, atau menjalankan model LLM/GGUF sebagai mesin bahasa.
- **Konservatif:** jika bukti linguistik belum cukup, sistem dapat menghasilkan status `partial` atau `unresolved`, bukan menebak.
- **Terukur:** perubahan perilaku disertai pengujian regresi dan pemeriksaan kompatibilitas.
- **Privasi:** data percakapan yang diperlukan dirancang untuk diproses dan disimpan secara lokal.
- **Dapat dikembangkan:** komponen dipisahkan agar kamus, morfologi, sintaksis, semantik, konteks, dan mesin respons dapat ditingkatkan secara bertahap.

Kelulusan tes hanya membuktikan perilaku yang diuji. Itu bukan bukti bahwa seluruh Bahasa Indonesia telah tercakup atau bahwa Lexara sudah memiliki kemampuan generatif setara LLM maupun ChatGPT.

## Gambaran arsitektur

```text
Masukan pengguna
      |
      v
Normalisasi dan tokenisasi
      |
      v
Pencocokan kamus dan analisis morfologi
      |
      v
Pengenalan kelas kata (POS)
      |
      v
Analisis struktur kalimat
      |
      v
Relasi makna dan pemrosesan konteks
      |
      v
Mesin aturan dan pembentukan respons
      |
      v
Jawaban chatbot
```

Alur di atas adalah gambaran arsitektur sasaran. Implementasi dibangun dan divalidasi bertahap; tidak semua komponen sudah selesai atau terintegrasi sebagai chatbot yang siap digunakan.

## Status pengembangan

| Komponen | Status |
|---|---|
| Spesifikasi dan desain data | Selesai |
| Kamus dan indeks leksikal | Fondasi tersedia: **3.019 lema / 60 batch** |
| Normalisasi teks | Selesai |
| Tokenisasi | Selesai |
| Pencocokan kamus | Selesai |
| Morfologi | Implementasi dasar tersedia; cakupan masih perlu diperluas |
| POS tagging | Tahap 2.5 ditutup |
| Analisis struktur kalimat | **Aktif — parser v1.9 (Tahap 2.6)** |
| Dataset dan pengujian terpadu | Fondasi sebagian tersedia; Tahap 2.7 belum selesai |
| Relasi makna dan konteks | Fondasi awal tersedia; Tahap 3 belum resmi dibuka |
| Mesin aturan dan pembentukan respons | Pekerjaan berikutnya |
| Integrasi chatbot Android offline | Belum dimulai |
| Optimasi perangkat | Belum dimulai |

### Catatan validasi terbaru

- Dataset POS berisi **100 kalimat / 543 token**: 60 development dan 40 test. Test split tetap tersegel dan tidak digunakan untuk penyetelan.
- Evaluasi POS kontekstual pada development: **250/255 token dikenali**, coverage **98,0%**, accuracy **98,0%**, dan selective accuracy **100,0%**. Lima abstention berupa nama orang ditunda ke tahap pengenalan nama/konteks.
- Pipeline kamus → POS → parser telah menguji 13 pronomina persona: `aku`, `saya`, `kamu`, `engkau`, `dia`, `mereka`, `kita`, `kami`, `kalian`, `anda`, `beliau`, `ia`, dan `kau`, sebagai subjek maupun objek pada pola sederhana yang diuji.
- Parser v1.9 memisahkan keterangan preposisional awal dari kandidat subjek. Contoh `Dari rumah dia bekerja.` mempertahankan `dia` sebagai subjek dan `dari rumah` sebagai keterangan.
- Inversi K-P-S umum belum diimplementasikan. Pada contoh ambigu seperti `Di rumah terdengar suara.`, parser mempertahankan bagian yang belum pasti sebagai unresolved.
- [GitHub Actions Run #182](https://github.com/semoliginon-ops/Lexara-Chatbot/actions/runs/46023874794) berhasil memvalidasi kamus 60 batch / 3.019 lema, valensi, dataset POS, evaluasi development, dan **359/359 regression tests**.

Angka dan hasil tersebut adalah snapshot pengembangan pada tanggal di atas, bukan klaim akurasi umum untuk semua kalimat Bahasa Indonesia.

## Peta tahapan pengembangan

Urutan kerja dan status setiap butir dikelola pada **[Checklist Pengembangan](docs/CHECKLIST_PENGEMBANGAN.md)**.

1. Spesifikasi dan desain data.
2. Fondasi leksikal: kamus dan indeks.
3. Pemrosesan bahasa dasar: normalisasi, tokenisasi, pencocokan, morfologi, POS, dan sintaksis.
4. Dataset serta evaluasi pipeline terpadu.
5. Relasi makna dan pemrosesan konteks.
6. Mesin aturan dan pembentukan respons.
7. Integrasi chatbot Android offline.
8. Evaluasi perangkat dan optimasi.

**Titik lanjut resmi:** selesaikan butir yang masih terbuka pada Tahap 2.6, lalu lanjutkan Tahap 2.7 sesuai urutan checklist. Tahap 2.5 (POS) telah ditutup. Tahap 3 belum resmi dibuka karena gerbang evaluasi Tahap 2 belum terpenuhi.

## Dokumentasi

- **[Checklist Pengembangan](docs/CHECKLIST_PENGEMBANGAN.md)** — urutan tahapan, status pekerjaan, aturan kerja, dan titik lanjut resmi.
- **[Status Pengolahan Bahasa](docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md)** — keputusan teknis, perilaku komponen, batas implementasi, dan riwayat pengujian.
- **[Dokumentasi Kamus](docs/KAMUS.md)** — skema, struktur, dan aturan data kamus.

README ini berisi gambaran umum dan status ringkas. Rincian checklist dan riwayat teknis dipelihara pada dokumen khusus agar tidak tumpang tindih.

## Peran GitHub

GitHub digunakan untuk menyimpan source code, kamus, dataset, dokumentasi, dan riwayat perubahan. GitHub bukan tempat menjalankan chatbot. GitHub Actions digunakan untuk validasi ketika diperlukan; perubahan dokumentasi sederhana tidak perlu memicu workflow jika tidak ada kebutuhan pengujian.

### Aturan perubahan kamus

- Periksa indeks kamus terlebih dahulu untuk mengetahui apakah lema sudah tersedia.
- Penambahan lema baru harus mendapat **persetujuan eksplisit pengguna** sebelum batch sumber maupun indeks diubah.
- Setelah perubahan data, pastikan sumber, indeks, dan validator tetap konsisten.
- Jangan mengubah data hanya demi mencapai jumlah entri tertentu atau mengisi metadata yang tidak dapat dipastikan.

## Hal yang bukan target proyek

- Membuat atau memasang model LLM/GGUF.
- Menggunakan API ChatGPT atau API AI berbayar sebagai mesin pemrosesan inti.
- Mengirim teks percakapan ke cloud untuk dianalisis oleh layanan AI eksternal.
- Menjanjikan kemampuan percakapan bebas setara ChatGPT.

**Arah Lexara:** membangun sistem bahasa lokal yang terstruktur, dapat ditelusuri, dapat diuji, dan berkembang berdasarkan bukti serta evaluasi.
