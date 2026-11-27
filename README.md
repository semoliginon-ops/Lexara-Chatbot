# Sistem Bahasa — Fondasi Chatbot Lokal Offline

Sistem Bahasa adalah proyek untuk membangun sistem pengolahan Bahasa Indonesia yang berjalan secara lokal di perangkat Android. Sistem dikembangkan dari kamus, aturan linguistik, analisis struktur, hubungan makna, konteks, serta mesin aturan dan respons — **bukan dengan memasang atau melatih LLM/GGUF**.

> **Status proyek (27 November 2026):** Tahap 2.6 — analisis struktur kalimat dasar sedang dikerjakan. Parser berada pada versi **v1.9**. Kamus memuat **3.014 lema dalam 60 batch**. GitHub Actions [Run #126](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45972629322) berhasil dengan **255/255 regression tests lulus**.

## Tujuan

Membangun fondasi agar chatbot lokal dapat:
- mengenali kata, variasi penulisan, dan bentuk berimbuhan;
- menganalisis kelas kata serta fungsi kata dalam kalimat;
- menghubungkan kata dan konsep berdasarkan relasi yang eksplisit;
- menafsirkan maksud dengan mempertimbangkan konteks percakapan;
- memilih atau membentuk respons menggunakan aturan yang dapat diuji;
- berjalan secara lokal/offline setelah aplikasi dan asetnya tersedia di perangkat.

Sasaran ini dikembangkan bertahap. Kelulusan tes hanya membuktikan perilaku yang diuji, bukan bahwa sistem telah memahami seluruh Bahasa Indonesia atau memiliki kemampuan generatif setara LLM.

## Prinsip dan batasan

- **Lokal dan offline-first:** pemrosesan inti ditujukan berjalan di perangkat, tanpa ketergantungan layanan cloud.
- **Tanpa LLM/GGUF dan API AI berbayar:** kemampuan dibangun dari komponen bahasa dan aturan yang eksplisit.
- **Konservatif:** jika bukti linguistik belum cukup, sistem boleh menghasilkan status partial/unresolved atau meminta klarifikasi; jangan menebak.
- **Terukur:** perubahan perilaku harus disertai pengujian regresi dan pemeriksaan kompatibilitas.
- **Privasi:** data percakapan yang diperlukan dirancang untuk disimpan secara lokal.
- **Embedding opsional:** bukan prasyarat dan hanya akan dievaluasi jika pengujian menunjukkan manfaat yang sebanding dengan biaya RAM, penyimpanan, dan latensi.

## Arsitektur konseptual

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
Hubungan makna dan pemrosesan konteks
      |
      v
Mesin aturan dan pembentukan respons
      |
      v
Jawaban
```

Komponen tersebut dibangun dan diuji secara bertahap. Implementasi saat ini berfokus pada fondasi leksikal dan pemrosesan kata/struktur; pemahaman makna, konteks, mesin respons, dan aplikasi Android masih menjadi pekerjaan berikutnya.

## Status pengembangan saat ini

| Komponen | Status |
|---|---|
| Spesifikasi dan desain data | Selesai |
| Kamus dan indeks leksikal | Fondasi tersedia: 3.014 lema / 60 batch |
| Normalisasi teks | Selesai |
| Tokenisasi | Selesai |
| Pencocokan kamus | Selesai |
| Morfologi | Implementasi dasar tersedia; cakupan masih perlu diperluas |
| POS tagging | Tahap 2.5 ditutup |
| Analisis struktur kalimat | **Aktif — parser v1.9** |
| Dataset dan pengujian terpadu | Pekerjaan berikutnya dalam Tahap 2 |
| Hubungan makna dan konteks | Belum dimulai |
| Mesin aturan dan pembentukan respons | Belum dimulai |
| Integrasi Android offline | Belum dimulai |
| Optimasi perangkat | Belum dimulai |

### Catatan validasi terbaru

- Dataset POS berisi 100 kalimat / 543 token: 60 development dan 40 test. Test split tetap tersegel.
- Evaluasi POS kontekstual pada development: 250/255 token dikenali; coverage 98,0%, accuracy 98,0%, dan selective accuracy 100,0%. Lima abstention berupa nama orang ditunda ke tahap pengenalan nama/konteks.
- Parser v1.9 memisahkan keterangan preposisional awal dari kandidat subjek. Pada contoh `Di rumah aku bekerja.`, `aku` tetap menjadi kandidat subjek. Pada `Di rumah terdengar suara.`, subjek dibiarkan kosong dan `suara` unresolved.
- Inversi K-P-S penuh belum diimplementasikan. Perilaku parsial/unresolved dipertahankan jika fungsi sintaksis belum cukup jelas.
- [GitHub Actions Run #126](https://github.com/semoliginon-ops/Sistem_bahasa/actions/runs/45972629322) memvalidasi kamus, dataset POS, evaluasi development, dan 255/255 regression tests.

## Peta pengembangan

Urutan kerja dan status setiap butir dikelola di **[Checklist Pengembangan](docs/CHECKLIST_PENGEMBANGAN.md)**. Ringkasnya:

1. Spesifikasi dan desain data.
2. Kamus serta pemrosesan kata dan tata bahasa dasar.
3. Hubungan makna dan pemrosesan konteks.
4. Mesin aturan dan pembentukan respons.
5. Integrasi Android offline.
6. Evaluasi perangkat dan optimasi.

**Titik lanjut resmi:** lanjutkan Tahap 2.6 dari parser v1.9, kemudian lengkapi evaluasi pipeline pada Tahap 2.7 sebelum masuk Tahap 3. Tahap 2.5 (POS) tetap ditutup.

## Dokumentasi

- **[Checklist Pengembangan](docs/CHECKLIST_PENGEMBANGAN.md)** — peta tahapan, status pekerjaan, aturan kerja, dan titik lanjut resmi.
- **[Status Pengolahan Bahasa](docs/STATUS_TAHAP_PENGOLAHAN_BAHASA.md)** — catatan teknis, keputusan desain, versi komponen, batas implementasi, serta riwayat pengujian.
- **[Dokumentasi Kamus](docs/KAMUS.md)** — skema, struktur, dan aturan data kamus.

README ini hanya memuat gambaran umum, arsitektur, dan status ringkas. Rincian checklist maupun riwayat teknis dipelihara pada dokumen khusus agar informasi tidak tumpang tindih.

## Peran GitHub

GitHub digunakan untuk menyimpan source code, kamus, dataset, dokumentasi, dan riwayat perubahan. GitHub bukan tempat menjalankan chatbot. GitHub Actions digunakan untuk validasi ketika diperlukan; pekerjaan dokumentasi sederhana tidak perlu memicu workflow jika tidak ada kebutuhan pengujian.

### Aturan perubahan kamus

- Periksa indeks kamus terlebih dahulu untuk mengetahui apakah lema sudah tersedia.
- Penambahan lema baru harus mendapat **persetujuan eksplisit pengguna** sebelum batch sumber maupun indeks diubah.
- Setelah perubahan data, pastikan sumber, indeks, dan validator tetap konsisten.
- Jangan mengubah data hanya demi mencapai jumlah entri tertentu atau mengisi metadata yang tidak dapat dipastikan.

## Hal yang bukan target proyek

- Membuat atau memasang model LLM/GGUF.
- Menggunakan API ChatGPT atau API AI berbayar sebagai mesin pemrosesan.
- Mengirim pesan pengguna ke cloud untuk diproses.
- Menjanjikan kemampuan percakapan bebas setara ChatGPT.

Target proyek adalah sistem bahasa lokal yang terstruktur, dapat diuji, dan terus dikembangkan sesuai batas kemampuan yang terukur.
