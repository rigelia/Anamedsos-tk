# Panduan Penulisan Bab 2: Metodologi (sampai BERTopic putaran 1)

Dokumen ini untuk anggota tim yang menulis bab setelah Pendahuluan. Isinya mencakup semua yang **sudah dikerjakan**:
- pemilihan kasus dan video;
- pengumpulan komentar;
- pemeriksaan kualitas data;
- prapemrosesan teks untuk BERTopic;
- BERTopic putaran 1 (pemisahan komentar relevan, hasil awal dengan label draft).

Analisis sentimen, BERTopic putaran 2, dan codebook **belum dikerjakan**, jadi cukup disiapkan kerangkanya (lihat bagian 2.7.2). Gambaran awal untuk Bab Hasil ada di bagian 2b.

Status per 1 Oktober 2026. Sumber angka:
- `data/20260930/collection_log.json`
- `data/interim/quality_report_v1.md`
- `data/processed/preprocess_report_v1.md`
- `experiments/runs.csv` dan `experiments/pass1_v1_nn15_mcs15_a/`

Detail teknis lengkap ada di `CLAUDE.md`.

> **Penting: angka hasil pemeriksaan kualitas masih versi 1 (v1).** Setelah tim meninjau `data/interim/review_quality_v1.csv` dan hasilnya dijalankan ulang sebagai v2, angka di 2.4 bisa berubah sedikit, terutama jumlah komentar berbahasa non-Indonesia. Tandai angka tersebut di draft (mis. dengan highlight) supaya mudah diperbarui.

---

## 0. Aturan umum penulisan bab ini

1. **Buka dengan desain penelitian.** Jangan langsung masuk ke tahapan. Paragraf pertama menyebut desain (deskriptif-komparatif dan eksploratif berbasis *digital trace*) beserta alasannya.
2. **Pakai kala lampau untuk yang sudah dikerjakan.** Proposal memakai "akan dikumpulkan"; di paper menjadi "dikumpulkan". Kala mendatang hanya untuk tahap yang belum dilakukan, kalau bab ini masih berstatus draft.
3. **Jangan mengulang teori.** Penjelasan konsep GenAI, autentisitas, dan sebagainya sudah ada di Pendahuluan. Bab ini hanya menyebut apa yang dipakai dan bagaimana memakainya.
4. **Setiap sub-bab diberi paragraf pengantar yang natural.** Hindari pola "Pembahasan dibagi menjadi dua bagian: pertama…".
5. **Sitasi mengikuti format proposal (angka dalam kurung siku, [1]–[11]).** Tidak ada sitasi di footnote.
6. **Angka harus bisa ditelusuri.** Setiap angka di bab ini berasal dari file log atau laporan kualitas, bukan hitungan manual.
7. **Istilah konsisten.** Lihat bagian 3.
8. Setelah draft selesai, jalankan pengecekan gaya bahasa (/humanizer) supaya tidak terasa ditulis AI.

---

## 1. Struktur sub-bab yang disarankan

| Sub-bab | Isi | Status |
|---|---|---|
| 2.1 Desain Penelitian | Jenis studi, unit analisis, batasan klaim | Siap ditulis |
| 2.2 Pemilihan Kasus dan Video | Kriteria, daftar kasus, status verifikasi | Siap ditulis; sebagian data verifikasi masih kosong |
| 2.3 Pengumpulan Data | API, tanggal pembekuan, data yang diambil, hasil | Siap ditulis |
| 2.4 Pemeriksaan Kualitas Data | Validasi, aturan penandaan, hasil eksklusi | Siap ditulis (angka v1) |
| 2.5 Etika dan Anonimisasi | Hash identitas, penyamaran *mention*, kutipan | Siap ditulis |
| 2.6 Prapemrosesan Teks | Dua versi teks untuk BERTopic, normalisasi slang, stopword | Siap ditulis (angka v1) |
| 2.7.1 BERTopic Putaran 1 | Konfigurasi, percobaan parameter, pemilihan, label relevansi | Siap ditulis; label masih draft |
| 2.7.2 Tahap Berikutnya | Sentimen, BERTopic putaran 2, codebook | Kerangka saja |

Nomor sub-bab menyesuaikan format paper. Proposal memakai format ACM dengan "1 PENDAHULUAN", sehingga bab ini menjadi "2 METODOLOGI" dengan sub-bab 2.1 dst.

---

## 2. Isi per sub-bab

### 2.1 Desain Penelitian

**Poin wajib:**
- Studi deskriptif-komparatif dan eksploratif berbasis *digital trace*: komentar publik YouTube yang terbentuk tanpa intervensi peneliti.
- Unit analisis utama: komentar (termasuk balasan) yang berkaitan dengan kasus penggunaan GenAI. Unit pengelompokan untuk perbandingan: kasus, tipe organisasi, dan jenis video.
- Perbandingan bersifat deskriptif: **tidak** menyimpulkan hubungan kausal, dan korpus **tidak** mewakili seluruh masyarakat Indonesia. Kalimat ini sudah ada di proposal; tulis ulang dengan kata-kata baru, jangan disalin.
- Alur umum dalam satu kalimat: pemilihan kasus dan video, pengumpulan komentar, pemeriksaan kualitas, prapemrosesan, identifikasi komentar relevan dan negatif, topic modeling, lalu pengodean manual dengan codebook.

**Contoh kalimat (sesuaikan, jangan disalin mentah):**
> Penelitian ini merupakan studi deskriptif-komparatif dan eksploratif yang memanfaatkan komentar publik YouTube sebagai *digital trace*. Komentar dipilih karena terbentuk secara spontan sebagai respons terhadap kasus yang sedang dibicarakan, tanpa diarahkan oleh instrumen survei.

**Opsional: diagram alur.** Satu gambar sederhana (kotak-panah) dari pemilihan kasus sampai codebook sangat membantu pembaca. Tandai tahap yang sudah selesai.

---

### 2.2 Pemilihan Kasus dan Video

**Poin wajib:**
- Pemilihan purposif pada dua tingkat: **kasus**, lalu **video** untuk tiap kasus.
- **Definisi kasus**: satu penggunaan GenAI tertentu dalam komunikasi visual oleh satu organisasi di Indonesia, misalnya satu iklan atau satu video kampanye.
- **Kriteria video**, sesuai proposal:
  - berkaitan langsung dengan kasus;
  - relevan bagi audiens Indonesia;
  - kolom komentar terbuka;
  - minimal 50 komentar pada tanggal pembekuan data.
- **Jenis video.** Proposal menyebut tiga jenis, tetapi korpus akhir hanya memuat dua (lihat tabel). Tidak ada unggahan resmi organisasi yang memenuhi kriteria. Pada kasus Indomie, misalnya, kolom komentar di unggahan resmi dinonaktifkan [11].
- **Status verifikasi penggunaan GenAI** per kasus, memakai empat tingkat dari proposal: pernyataan resmi, pemberitaan media kredibel, label platform, indikasi visual.
- Kasus dengan verifikasi lebih rendah tetap dimasukkan dengan status tercatat, lalu dibandingkan hasilnya dengan dan tanpa kasus tersebut. Analisis sensitivitas ini **belum dilakukan**; cukup sebutkan sebagai rencana.

**Tabel kasus (siap pakai, isi kolom verifikasi yang masih [ISI]):**

| Kode | Kasus | Organisasi | Tipe organisasi | Tahun | Verifikasi |
|---|---|---|---|---|---|
| C01 | Iklan Indomie berbasis AI | Indomie (Indofood) | Merek komersial | 2023 | Media kredibel [11] |
| C02 | Video promosi Makan Bergizi Gratis (MBG) | Kementerian Komunikasi dan Digital | Institusi pemerintah | 2025 | Media kredibel [9], [10] |
| C03 | Video kampanye perlindungan anak di ruang digital | Kementerian Komunikasi dan Digital | Institusi pemerintah | 2025 | [ISI] |
| C04 | Iklan POLRI berbasis AI | Kepolisian Negara RI | Institusi pemerintah | 2025 | [ISI] |
| C05 | *Filler* Ramadan RTV | RTV | Merek komersial | 2025 | [ISI] |
| C06 | Video azan magrib Mentari TV | Mentari TV | Merek komersial | 2025 | [ISI] |
| C07 | Animasi AI Kementerian Komdigi (Maret 2025) | Kementerian Komunikasi dan Digital | Institusi pemerintah | 2025 | [ISI] |

**Tabel video:**

| Kode | Judul video | Kanal | Diunggah | Jenis video | Komentar |
|---|---|---|---|---|---|
| C01 | Iklan mie ini viral kena hujat! #viral #ai | Jaret Fajrianto (GHOSTY's COMIC) | 29-09-2023 | Pihak ketiga | 575 |
| C01 | Indomie Bikin Iklan Pakai AI Tapi Malah Dihujat Warganet, Kenapa? | Suaradotcom | 09-10-2023 | Pihak ketiga | 72 |
| C02 | Iklan BNI vs MBG: Anime vs AI Ampas?! | Pherfect | 22-02-2025 | Pihak ketiga | 172 |
| C03 | Mari Jaga Anak Kita dari Konten-konten Berbahaya | Kominfo Muara Enim | 18-02-2025 | Unggahan ulang/arsip | 730 |
| C04 | Kenapa POLRI Nekat Bikin Iklan AI?? | Mindplace | 03-07-2025 | Pihak ketiga | 553 |
| C05 | Filler Kemulian Cinta Ramadan RTV (2025) | ATCH | 16-03-2025 | Unggahan ulang/arsip | 127 |
| C06 | Adzan Maghrib Mentari TV 2025 | ATCH | 04-03-2025 | Unggahan ulang/arsip | 125 |
| C07 | KENAPA PEMERINTAH BIKIN IKLAN AI LAGI?? | Mindplace | 14-03-2025 | Pihak ketiga | 953 |

Kolom "Komentar" = jumlah komentar dan balasan yang terkumpul; sama dengan `commentCount` YouTube pada tanggal pembekuan.

**Keputusan yang perlu dijelaskan di teks (satu atau dua kalimat masing-masing):**
- **C03 memakai video unggahan kanal Dinas Kominfo daerah (Muara Enim)**, bukan kanal pusat. Video ini adalah materi kampanye itu sendiri, sehingga digolongkan sebagai unggahan ulang/arsip.
- **C07 dipisahkan dari C02.** Video C07 diunggah sebulan setelah kasus MBG, dan komentar teratasnya menyebut Komdigi, merujuk video sebelumnya dari kanal yang sama, serta menyinggung "lomba AI". Jadi yang dibahas adalah animasi AI Komdigi yang berbeda dari iklan MBG.
- **Video C02 membandingkan iklan anime BNI dengan iklan AI MBG.** Kasusnya tetap MBG; BNI tidak diperlakukan sebagai kasus karena iklannya tidak memakai GenAI.
- **RTV dan Mentari TV digolongkan sebagai merek komersial** karena keduanya stasiun televisi swasta yang memakai GenAI dalam konten siarannya sendiri. Kalimat ini penting karena reviewer bisa mempertanyakan apakah stasiun TV termasuk "merek".
- **Tiga dari empat kasus pemerintah melibatkan Komdigi.** Sebutkan secara terbuka, karena berpengaruh pada interpretasi RQ2.

**Yang masih kurang (screening log):** proposal menjanjikan dokumentasi kata kunci pencarian, tanggal penelusuran, dan alasan pengecualian kasus/video. `videos_manifest.csv` baru mencatat video yang masuk beserta alasannya. **Tim perlu mengisi:**
- kata kunci yang dipakai saat mencari video;
- kapan pencarian dilakukan;
- video/kasus yang dipertimbangkan tetapi tidak dipakai, beserta alasannya. Contoh: iklan Indomie resmi (komentar dinonaktifkan), kandidat dengan komentar di bawah 50.

Ringkasan screening cukup satu paragraf di teks. Log lengkapnya bisa masuk lampiran.

---

### 2.3 Pengumpulan Data

**Poin wajib:**
- **Sumber:** YouTube Data API v3. Endpoint yang dipakai:
  - `videos.list` untuk metadata dan statistik video;
  - `commentThreads.list` untuk komentar tingkat pertama;
  - `comments.list` untuk balasan pada thread yang tidak dikembalikan lengkap.
- Semua video diambil dalam **satu kali eksekusi** dari daftar video yang dikurasi manual, sehingga seluruh korpus punya satu tanggal pembekuan.
- **Tanggal pembekuan data: 30 September 2026, pukul 02.13–02.14 UTC (09.13 WIB).**
- **Data per komentar:**
  - ID komentar dan ID thread induk;
  - teks komentar;
  - tanggal publikasi dan tanggal penyuntingan;
  - jumlah *like*;
  - jumlah balasan;
  - penanda apakah komentar ditulis pemilik kanal;
  - hash identitas akun (lihat 2.5).
- **Data per video:** judul, kanal, tanggal unggah, jumlah tayangan, *like*, dan komentar pada saat pengambilan.
- Respons API mentah disimpan sebagai arsip JSON (sudah dianonimkan). Tabel komentar disimpan sebagai CSV UTF-8. Ini sesuai pembagian format di materi kuliah: JSON untuk respons API, CSV untuk data tabular kecil.

**Hasil:**
- **3.307 komentar** dari 8 video dan 7 kasus: 2.408 komentar tingkat pertama dan 899 balasan.
- Jumlah per video sama persis dengan `commentCount` yang dilaporkan YouTube.
- Rentang waktu komentar: 29 September 2023 sampai 23 September 2026.

**Satu catatan teknis yang layak disebut (satu kalimat):** pada dua video, API mengembalikan satu thread dua kali (diduga komentar yang disematkan), sehingga duplikat dihapus berdasarkan ID komentar. Materi kuliah menyebut *pagination error* sebagai salah satu sumber duplikasi, jadi ini contoh yang relevan.

**Jangan ditulis:** API key, detail kuota, atau nama file skrip. Nama file cukup di lampiran/repositori jika diminta.

---

### 2.4 Pemeriksaan Kualitas Data

Ini inti dari tahap yang baru selesai. Kerangkanya mengikuti materi kuliah Modul 5: kualitas data diperiksa **sebelum** analisis (*quality gate*), dengan validasi di tiga tingkat, lalu penandaan (*flagging*) alih-alih penghapusan langsung.

**Paragraf pengantar, poinnya:**
- Kualitas dinilai sesuai tujuan penelitian (*fit for purpose*).
- Setiap masalah ditandai di kolom tersendiri dan tidak langsung dihapus. Dengan begitu jumlah komentar yang dikeluarkan oleh tiap aturan bisa dilaporkan dan diperiksa ulang.
- Data mentah tidak diubah; hasil pemeriksaan disimpan sebagai versi data tersendiri.

**a. Validasi.** Semua aturan terpenuhi (tidak ada pelanggaran). Tulis dalam bentuk ringkas, tidak perlu mendaftar 17 aturan di teks. Tabel lengkap bisa ke lampiran.

| Tingkat | Contoh aturan | Hasil |
|---|---|---|
| Record | ID komentar tidak kosong dan unik; teks tidak null; *like* ≥ 0; tanggal valid; status balasan konsisten dengan ID induk | Semua terpenuhi |
| Dataset | Setiap balasan punya komentar induk; jumlah balasan per thread sesuai; jumlah komentar per video sesuai log dan statistik YouTube; tanggal komentar berada di antara tanggal unggah dan tanggal pengambilan | Semua terpenuhi |
| Riset | Keseimbangan korpus per kasus, tipe organisasi, dan jenis video; konsentrasi penulis | Dilaporkan sebagai keterbatasan (lihat bawah) |

**b. Aturan eksklusi**, diterapkan berurutan. Angka v1:

| Tahap | Keterangan | Dikeluarkan | Sisa |
|---|---|---|---|
| Korpus awal | | | 3.307 |
| Komentar pemilik kanal | Ditulis oleh kanal pengunggah video | 42 | 3.265 |
| Tanpa isi teks | Hanya emoji, simbol, timestamp video, atau *mention* | 38 | 3.227 |
| Spam | Promosi judi daring, promosi diri, atau tautan | 8 | 3.219 |
| Pengulangan oleh penulis sama | Teks identik dari akun yang sama; kemunculan pertama dipertahankan | 14 | 3.205 |
| Bukan bahasa Indonesia | Terutama bahasa Inggris; ditambah beberapa komentar beraksara Arab pada video azan | 60 | **3.145** |

Hasil akhir: **3.145 komentar (95,1%)** lolos pemeriksaan kualitas.

**c. Definisi yang harus dijelaskan (penting, karena ini keputusan metodologis):**
- **Duplikat vs konten berulang.** Mengikuti materi kuliah, keduanya dibedakan:
  - duplikat rekaman (ID sama) dihapus;
  - teks sama dari akun yang sama dianggap pengulangan dan hanya kemunculan pertama dipertahankan;
  - teks sama dari akun berbeda (mis. "sangat layak dihujat") **dipertahankan** karena merupakan respons sah dari orang yang berbeda. Ada 99 komentar seperti ini.
- **Spam.** Komentar ditandai jika memuat:
  - istilah kuat judi daring (mis. *gacor*, *maxwin*, *slot*);
  - minimal dua istilah lemah yang berbeda (mis. *wd*, *jp*, *hoki*);
  - angka dalam lingkaran yang dipakai menyamarkan nama situs;
  - tautan, atau frasa promosi diri.

  Semua komentar yang tertandai dibaca manual dan seluruhnya memang spam atau promosi. Aturan dibuat oleh tim karena bagian materi kuliah tentang bot dan spam tidak berisi konten; sebut ini secara jujur.
- **Bahasa.**
  - Deteksi per komentar memakai *lingua* (versi 2.2.0), dibatasi pada bahasa yang mungkin muncul: Indonesia, Melayu, Inggris, Arab, Jepang, Korea, Mandarin.
  - Melayu digabung dengan Indonesia karena keduanya sulit dibedakan pada teks pendek.
  - Komentar yang terdeteksi berbahasa asing tetapi memuat penanda bahasa Indonesia (kata fungsi atau slang seperti *yang*, *gak*, *aja*, akhiran *-nya*, tawa *wkwk*) dianggap campur kode dan tetap dipertahankan.
  - Komentar di bawah tiga kata tidak dideteksi bahasanya karena terlalu pendek untuk diklasifikasikan andal, kecuali jika aksaranya bukan Latin.
- **Komentar pendek tidak dikeluarkan.** Komentar di bawah tiga kata hanya ditandai (334 komentar di antara yang lolos). Keputusan memakainya diambil pada tahap topic modeling. Alasannya: komentar pendek seperti "lomba AI 🤣" tetap bisa bermakna.
- **Validasi manual.** Komentar yang tertandai spam, bukan bahasa Indonesia, campur kode, atau pengulangan (109 komentar) ditinjau manual. Keputusan peninjau dicatat terpisah, sehingga bisa diterapkan ulang secara konsisten.

  > Sebelum ditulis final: pastikan tinjauan manual sudah selesai dan angka diperbarui ke v2. Sebutkan juga berapa keputusan otomatis yang diubah oleh peninjau.

**d. Keseimbangan korpus setelah pemeriksaan (tingkat riset):**

| Kode | Tipe organisasi | Jenis video | Total | Lolos | % dari seluruh komentar yang lolos |
|---|---|---|---|---|---|
| C01 | Merek komersial | Pihak ketiga | 647 | 630 | 20,0 |
| C02 | Institusi pemerintah | Pihak ketiga | 172 | 135 | 4,3 |
| C03 | Institusi pemerintah | Unggahan ulang/arsip | 730 | 698 | 22,2 |
| C04 | Institusi pemerintah | Pihak ketiga | 553 | 538 | 17,1 |
| C05 | Merek komersial | Unggahan ulang/arsip | 127 | 111 | 3,5 |
| C06 | Merek komersial | Unggahan ulang/arsip | 125 | 115 | 3,7 |
| C07 | Institusi pemerintah | Pihak ketiga | 953 | 918 | 29,2 |

- **Per tipe organisasi:** pemerintah 2.289 (72,8%), komersial 856 (27,2%).
- **Per jenis video:** pihak ketiga 2.221 (70,6%), unggahan ulang/arsip 924 (29,4%).

**Hal yang perlu dibahas dari tabel ini (bisa di sini atau di bagian keterbatasan):**
- Korpus tidak seimbang: pemerintah jauh lebih banyak. Karena itu perbandingan RQ2 dan RQ3 memakai **proporsi**, bukan jumlah mentah, dan dilaporkan juga per kasus.
- Sisi komersial didominasi Indomie: 630 dari 856 komentar.
- C02 hanya tersisa 135 komentar karena pemilik kanal membalas 34 kali di kolom komentarnya.
- **Konsentrasi penulis rendah.** Ada 2.545 akun unik. 1% akun teratas menulis 7,7% komentar, dengan maksimum 43 komentar dari satu akun. Artinya korpus tidak didominasi segelintir akun.

---

### 2.5 Etika dan Anonimisasi

**Poin wajib:**
- Hanya komentar publik yang dipakai. Tidak ada interaksi dengan pengguna.
- **Identitas akun tidak disimpan dalam bentuk asli.**
  - ID kanal penulis diganti hash (HMAC-SHA256 dengan kunci rahasia) sejak tahap pengumpulan.
  - Nama tampilan, foto profil, dan URL kanal penulis dihapus, termasuk dari arsip JSON.
- ***Mention* di dalam teks** (mis. "@namaakun", terutama di balasan) diganti token netral "@user". Pada uji awal, 24 dari 72 komentar memuat nama akun di teksnya, sehingga tanpa langkah ini hash identitas tidak cukup.
- **Kutipan komentar di paper dipilih dengan hati-hati.** Pakai kutipan pendek. Pertimbangkan parafrase jika kalimatnya cukup unik untuk dilacak lewat pencarian. Jangan menyebut akun penulisnya.

Poin ini menjawab janji proposal: "authorId disimpan dalam bentuk hash", "kutipan komentar akan dipertimbangkan secara hati-hati".

---

### 2.6 Prapemrosesan Teks

Sumber angka:
- `data/processed/preprocess_report_v1.md`
- `data/processed/preprocess_config_v1.json`

Seperti 2.4, angka di sini dihitung dari data kualitas v1 dan bisa sedikit berubah setelah v2. **Tandai juga.**

**Paragraf pengantar, poinnya:**
- Tahap ini menyiapkan teks dari 3.145 komentar yang lolos pemeriksaan kualitas agar siap diproses BERTopic.
- Mengikuti materi kuliah Modul 6, tidak ada satu cara prapemrosesan yang benar untuk semua tugas. Perlakuan teks dipilih berdasarkan model yang akan memakainya.
- BERTopic punya dua komponen dengan kebutuhan berbeda:
  - model transformer yang mengelompokkan komentar berdasarkan makna;
  - penghitungan kata (c-TF-IDF) yang menentukan kata penciri setiap topik.
- Karena itu setiap komentar disiapkan dalam dua bentuk teks.

Jangan menjelaskan ulang cara kerja BERTopic atau transformer di sini; cukup sebut komponennya.

**a. Dua bentuk teks**

| Bentuk teks | Dipakai untuk | Prinsip |
|---|---|---|
| Teks embedding | Mengelompokkan komentar (model `paraphrase-multilingual-mpnet-base-v2`) | Pembersihan minimal. Konteks, kapitalisasi, negasi, slang, dan emoji dipertahankan karena model transformer memanfaatkannya |
| Teks representasi | Menentukan kata penciri topik | Pembersihan tradisional: huruf kecil, hanya kata, tanpa emoji, tanda baca, dan angka |

Dasar di materi kuliah (Modul 6, tabel *Task-Specific Preprocessing*):
- untuk klasifikasi berbasis transformer disarankan "*avoid unnecessary cleaning*" dan "*preserve contextual information*";
- untuk topic modeling, penghapusan stopword dan filter kosakata "*may help*".

**b. Rincian perlakuan** (bisa disajikan sebagai tabel di paper)

| Perlakuan | Teks embedding | Teks representasi A | Teks representasi B |
|---|---|---|---|
| Normalisasi Unicode, hapus karakter tak terlihat | Ya | Ya | Ya |
| Tautan → `[URL]`, *mention* → `[USER]` | Diganti token | Dihapus | Dihapus |
| Sapaan `[USER]` di awal balasan | Dihapus | Dihapus | Dihapus |
| Timestamp video (mis. "2:17") | Dihapus | Dihapus | Dihapus |
| Reduplikasi gaya medsos (*anak2*, *situs²* → *anak-anak*) | Ya | Ya | Ya |
| Huruf berulang (*bangettttt*) | Dipendekkan ke 2 (*bangett*) | Dipendekkan ke 1 (*banget*) | Dipendekkan ke 1 |
| Tawa (*wkwkwkwk*) | → *wkwk* | → *wkwk* | → *wkwk* |
| Emoji dan tanda baca | Dipertahankan (pengulangan dipendekkan) | Dihapus | Dihapus |
| Kapitalisasi | Dipertahankan | Huruf kecil | Huruf kecil |
| Normalisasi slang (*gak* → *enggak*, *yg* → *yang*) | Tidak | Tidak | Ya |
| Reduplikasi penuh (*orang-orang* → *orang*) | Tidak | Tidak | Ya |
| Akhiran *-nya* (*iklannya* → *iklan*) | Tidak | Tidak | Ya, jika kata dasarnya ada di korpus |
| Stopword | Tidak dihapus | Tidak dihapus dari teks | Tidak dihapus dari teks |
| Stemming | Tidak | Tidak | Tidak |

**c. Varian A dan B sebagai variabel eksperimen.** Materi kuliah (Modul 6, *Preprocessing as an Experiment Variable*) menyarankan membandingkan beberapa pipeline daripada menganggap satu pipeline paling baik. Karena itu teks representasi dibuat dua varian:
- **A:** tanpa normalisasi;
- **B:** dengan normalisasi slang.

Keduanya akan dibandingkan di tahap BERTopic berdasarkan:
- koherensi topik;
- keragaman topik;
- persentase outlier;
- keterbacaan topik bagi manusia.

Tulis bagian ini sebagai rancangan; hasil perbandingannya masuk bab hasil.

**d. Normalisasi slang (varian B).**
- **Kamus:** normalisasi memakai *Colloquial Indonesian Lexicon* (Salsabila dkk., 2018). Kamus ini berisi sekitar 15.000 pasangan kata slang–baku yang disusun dari komentar Instagram.
- **Koreksi kamus:** kamus tidak dipakai mentah. Sebelum dipakai, setiap pemetaan yang muncul di korpus diperiksa, dan beberapa ternyata mengubah makna:

| Kata | Pemetaan kamus | Masalah | Keputusan |
|---|---|---|---|
| *mbg* | *mbak* | Nama kasus Makan Bergizi Gratis | Tidak diubah |
| *indo* | *indonesia* | Di korpus ini "mi indo" = Indomie | Tidak diubah |
| *x* | *kali* | Merujuk platform X (Twitter) | Tidak diubah |
| *it*, *in*, *to*, *so* | *itu*, *ini*, *tapi*, *sok* | Kata bahasa Inggris pada komentar campur kode | Kata stopword Inggris tidak dinormalisasi |
| *ngapain* | *mengapai* | Makna berubah | Tidak diubah |
| *make* | *memakai* | Tidak konsisten dengan *pake* → *pakai* | → *pakai* |

  Daftar lengkap koreksi (15 entri) beserta alasannya ada di `resources/slang_overrides.csv` dan cocok untuk lampiran.
- **Kata yang dilindungi:** selain koreksi di atas, kata tertentu tidak pernah diubah atau dihapus: *ai*, *mbg*, *komdigi*, *polri*, *indomie*, dsb. Kata berhuruf tunggal juga tidak dinormalisasi.
- **Akhiran -nya:** pelepasan *-nya* diperiksa manual. Hasilnya benar pada hampir semua kasus (*effortnya* → *effort*, *komdiginya* → *komdigi*); kurang dari 1% keliru. Kata yang maknanya berubah jika dilepas (*makanya*, *katanya*, *soalnya*) dikecualikan.

**e. Stopword.** Stopword **tidak dihapus dari teks**. Daftarnya hanya dipakai saat BERTopic menghitung kata penciri topik, sehingga teks embedding tetap utuh (materi kuliah: penghapusan stopword bisa menghilangkan negasi seperti "*tidak*").

| Komponen daftar stopword | Jumlah |
|---|---|
| *stopwords-iso* bahasa Indonesia (sumber yang dirujuk materi kuliah) | 758 |
| Stopword bahasa Inggris (scikit-learn), untuk komentar campur kode | 318 |
| Kata pengisi dan slang khas komentar (*sih*, *dong*, *wkwk*, *bang*, *gue*, *enggak*, …) | 129 |
| **Total setelah digabung dan dikurangi pengecualian** | **1.171** |

Pengecualian yang perlu disebut:
- *AI* dan nama kasus sengaja **tidak** dijadikan stopword.
- Enam kata dari *stopwords-iso* dikeluarkan dari daftar karena bermakna untuk tema keberatan: *masalah*, *penting*, *kurang*, *jelas*, *rasa*, *merasa*. Contohnya "kurang effort" dan "gak jelas".

**f. Hasil**

| Ukuran | Nilai |
|---|---|
| Komentar diproses | 3.145 |
| Rata-rata kata per komentar (teks representasi) | 14,4 |
| Jenis kata di luar stopword, varian A | 6.476 |
| Jenis kata di luar stopword, varian B | 5.628 (−13%) |
| Kata yang diubah pada varian B | 5.669 oleh kamus, 379 oleh koreksi manual, 924 oleh pelepasan *-nya* |
| Komentar yang hanya berisi stopword (mis. "iya sih") | 73 (ditandai, tidak dikeluarkan) |
| Median panjang komentar dalam token model | 15 |
| Komentar melebihi batas 128 token model | 45 (1,4%) |

Cara membaca:
- Penurunan kosakata 13% menunjukkan bahwa variasi ejaan (*gak*/*ga*/*gk*/*nggak*, *pake*/*pakai*/*make*) sebelumnya terpecah menjadi kata-kata berbeda.
- Komentar yang melebihi 128 token hanya terbaca bagian awalnya oleh model embedding. Jumlahnya kecil, jadi cukup disebut sebagai keterbatasan.

**g. Contoh sebelum/sesudah** (siap pakai; ketiganya tidak memuat informasi identitas)

| Asli | Teks embedding | Teks representasi A | Teks representasi B |
|---|---|---|---|
| @user Dan banyak detail yang jelek, kayak ada tangan nyambung sama rambut juga wkwkwk | Dan banyak detail yang jelek, kayak ada tangan nyambung sama rambut juga wkwk | dan banyak detail yang jelek kayak ada tangan nyambung sama rambut juga wkwk | dan banyak detail yang jelek kayak ada tangan menyambung sama rambut juga wkwk |
| Memang layak dihujat, merek besar yang gak mau modal banyak 😂 | Memang layak dihujat, merek besar yang gak mau modal banyak 😂 | memang layak dihujat merek besar yang gak mau modal banyak | memang layak dihujat merek besar yang enggak mau modal banyak |
| Saya tidak tahu menahu dengan urusan ini yang jelas rasanya enak tapi iklannya harusnya sih aku aja yang buat | (tidak berubah) | saya tidak tahu menahu dengan urusan ini yang jelas rasanya enak tapi iklannya harusnya sih aku aja yang buat | saya tidak tahu menahu dengan urusan ini yang jelas rasanya enak tapi iklan harusnya sih aku saja yang buat |

Yang ditunjukkan tiap contoh:
- Contoh 1: sapaan balasan dihapus dan tawa dipendekkan.
- Contoh 2: emoji tetap ada di teks embedding, dan slang *gak* dinormalisasi di B.
- Contoh 3: *-nya* dilepas (*iklannya* → *iklan*) tetapi *rasanya* dan *harusnya* dipertahankan, serta *aja* → *saja*.

Ini sejalan dengan latihan "tiga versi prapemrosesan" di materi kuliah.

**h. Yang sengaja tidak dilakukan** (layak ditulis satu kalimat masing-masing):
- **Tidak ada stemming:** kata penciri topik harus tetap terbaca, dan model embedding tidak membutuhkannya.
- **Emoji tidak dikonversi ke teks** (*😂* → *face_with_tears_of_joy*): model multilingual bisa membaca emoji langsung, sementara untuk kata penciri topik emoji tidak informatif.
- **Tidak ada penerjemahan** komentar campur kode; model embedding bersifat multilingual.

**Sitasi baru untuk daftar pustaka:**
- Salsabila, N. A., Winatmoko, Y. A., Septiandri, A. A., & Jamal, A. (2018). *Colloquial Indonesian Lexicon*. International Conference on Asian Language Processing (IALP) 2018. Sesuaikan dengan format ACM seperti referensi lain; cek DOI di IEEE Xplore.
- *stopwords-iso* (https://github.com/stopwords-iso/stopwords-id): sebut sebagai rujukan perangkat lunak/sumber data.
- Model embedding `paraphrase-multilingual-mpnet-base-v2` (Sentence-Transformers). Bisa dirujuk ke Reimers & Gurevych (2019, 2020) jika tim ingin sitasi formal; cukup satu kalimat, penjelasan modelnya tidak perlu diulang.

---

### 2.7 Analisis

Analisis terdiri atas beberapa tahap. Yang sudah dijalankan baru **BERTopic putaran 1** (2.7.1). Tahap lainnya masih rencana (2.7.2).

Sumber angka:
- `experiments/runs.csv`
- `experiments/pass1_v1_nn15_mcs15_a/` (`topic_review.md`, `topic_info.csv`, `labels_draft.csv`)

#### 2.7.1 BERTopic putaran 1: memisahkan komentar relevan (sudah dijalankan, hasil awal)

**Tujuan.** Putaran pertama **bukan** untuk menemukan tema keberatan, tetapi untuk memisahkan komentar yang merespons penggunaan GenAI dari komentar yang tidak berkaitan (rasa mie, nostalgia TV, komentar tentang kanal, dsb.). Relevansi dinilai berdasarkan konteks, bukan kata kunci. Contoh: "Bagaimana mau maju jika kelakuan KOMDIGI ini aja tidak mau hargai karya anak bangsa" tetap relevan walaupun tidak menyebut "AI". Karena BERTopic mengelompokkan berdasarkan makna, komentar seperti ini bisa terkumpul bersama komentar lain yang searti.

**Paragraf pengantar, poinnya:**
- BERTopic [sitasi Grootendorst 2022] dipakai pada seluruh 3.145 komentar yang lolos pemeriksaan kualitas.
- Alurnya:
  1. teks embedding diubah menjadi vektor makna;
  2. dimensinya direduksi dengan UMAP;
  3. dikelompokkan dengan HDBSCAN;
  4. kata penciri tiap kelompok ditentukan dengan c-TF-IDF dari teks representasi.
- Cukup satu kalimat per komponen. **Jangan** menjelaskan matematika UMAP/HDBSCAN di bab ini.

**a. Konfigurasi** (tabel siap pakai)

| Komponen | Pengaturan |
|---|---|
| Model embedding | `paraphrase-multilingual-mpnet-base-v2` (768 dimensi, maks. 128 token) |
| Reduksi dimensi (UMAP) | 5 dimensi, metrik kosinus, `min_dist` 0, `random_state` 42 |
| Pengelompokan (HDBSCAN) | `min_samples` 5, pemilihan klaster *excess of mass* |
| Kata penciri (c-TF-IDF) | unigram dan bigram, `min_df` 2, daftar stopword 1.171 kata, `reduce_frequent_words` |
| Yang divariasikan | UMAP `n_neighbors` {15, 30} × HDBSCAN `min_cluster_size` {10, 15, 25} × teks representasi {A, B} = 12 run |
| Ukuran evaluasi | jumlah topik, persentase outlier, ukuran topik terbesar, koherensi c_v dan NPMI [sitasi Röder dkk. 2015], keragaman topik [sitasi Dieng dkk. 2020] |

Setiap run dicatat parameternya di `experiments/runs.csv`, mengikuti prinsip *experiment tracking* di materi kuliah Modul 4. Seed acak dikunci, dan run ulang menghasilkan angka yang identik.

**b. Hasil percobaan parameter** (tabel siap pakai; nilai varian A, kecuali disebut lain)

| `n_neighbors` | `min_cluster_size` | Topik | Outlier | Topik terbesar | c_v | NPMI | Keragaman |
|---|---|---|---|---|---|---|---|
| 15 | 10 | 57 | 32,6% | 10,2% | 0,402 | −0,247 | 0,939 |
| **15** | **15** | **44** | **32,2%** | **10,2%** | **0,416** | **−0,230** | **0,961** |
| 15 | 25 | 22 | 21,1% | 24,9% | 0,427 | −0,191 | 0,955 |
| 30 | 10 | 43 | 29,2% | 16,3% | 0,413 | −0,251 | 0,942 |
| 30 | 15 | 22 | 13,7% | 31,5% | 0,449 | −0,181 | 0,955 |
| 30 | 25 | 16 | 12,6% | 33,4% | 0,458 | −0,184 | 0,963 |

**Alasan pemilihan** (tulis 2–3 kalimat):
- Konfigurasi dengan koherensi tertinggi (nn30) menghasilkan satu klaster raksasa berisi 31–33% komentar, dan konfigurasi nn15/mcs25 juga punya klaster 25%. Klaster sebesar itu hampir pasti campuran, sehingga tidak berguna untuk memisahkan komentar relevan.
- Sebaliknya, `min_cluster_size` 10 menghasilkan 57 topik kecil yang berat untuk dilabeli manual.
- **Dipilih: `n_neighbors` 15, `min_cluster_size` 15.** Topik terbesarnya hanya 10%, keragamannya tertinggi, dan jumlah topiknya masih bisa dibaca satu per satu.
- Tekankan bahwa pemilihan **tidak semata-mata berdasarkan koherensi**; pembacaan manusia tetap menjadi kriteria penentu (Modul 6).

**c. Varian A vs B.** Pengelompokan ditentukan oleh teks embedding, sehingga varian A dan B menghasilkan klaster yang identik dan hanya berbeda pada kata penciri. Perbedaan koherensinya kecil dan arahnya tidak konsisten (A sedikit lebih tinggi pada `min_cluster_size` 10–15, B pada 25). Konfigurasi akhir memakai kata penciri varian A, sedangkan kata varian B tetap ditampilkan sebagai pembanding. Kalimat untuk paper: normalisasi slang tidak memberi perbaikan yang berarti pada putaran ini.

Cara membaca angka (boleh satu kalimat di paper):
- c_v sekitar 0,4 lazim untuk teks media sosial yang pendek;
- NPMI negatif umum terjadi karena kata penciri jarang muncul bersama dalam satu komentar pendek. Karena itu NPMI dipakai untuk membandingkan run, bukan sebagai ukuran mutlak.

**d. Hasil konfigurasi terpilih**
- 44 topik.
- 1.014 komentar (32,2%) tidak masuk topik mana pun (outlier, topik −1).
- Topik terbesar: "animator/kreator lokal tidak dipakai", 321 komentar (10,2%).

**e. Pelabelan relevansi**, saat ini masih **draft dan harus divalidasi tim** sebelum ditulis final:
- Setiap topik dilabeli *relevan*, *tidak relevan*, atau *campuran*.
- Pelabelan berdasarkan kata penciri, sebaran kasus, dan contoh komentar per topik: 8 komentar dengan keanggotaan tertinggi dan 4 komentar acak.

| Label (draft) | Topik | Komentar | % |
|---|---|---|---|
| Relevan | 19 | 1.221 | 38,8 |
| Tidak relevan | 11 | 278 | 8,8 |
| Campuran (termasuk 1.014 outlier) | 15 | 1.646 | 52,3 |

Contoh nama topik untuk dicantumkan di paper atau lampiran:
- **Relevan:**
  - animator/kreator lokal tidak dipakai;
  - perbandingan dengan iklan buatan manusia (Marjan, BNI, iklan anime);
  - AI sebagai alat vs pengganti manusia;
  - penghematan anggaran sebagai motif;
  - dugaan korupsi anggaran;
  - hak cipta dan AI art;
  - cacat visual (anatomi, objek);
  - AI tidak dipoles;
  - pemerintah tidak kompeten teknologi;
  - sindiran bahwa iklan itu sendiri "konten berbahaya";
  - harus beradaptasi dengan teknologi (sisi pro-AI).
- **Tidak relevan:**
  - rasa produk dan loyalitas merek Indomie;
  - koreksi nama "mi indo";
  - komentar tentang video/kanal;
  - nostalgia televisi;
  - azan dan doa;
  - persetujuan tanpa isi;
  - tawa.
- **Campuran:**
  - kritik umum terhadap polisi/pemerintah;
  - politik (menteri, presiden);
  - reaksi sangat pendek ("ga niat", "Ai 🤣👎").

**Hal yang perlu ditulis jujur:**
- **Outlier besar (32%) dan tidak bisa langsung dibuang.** Sebagian berisi keberatan jelas. Contoh: *"Please komdigi, ada baiknya buat animasi lokal di banding AI…"* masuk outlier. Tulis cara penanganannya setelah tim memutuskan (lihat 2.7.2).
- **Beberapa topik berasal dari satu kasus saja**, misalnya topik polisi 99% dari C04, atau topik rasa mie dari C01. Ini wajar untuk pemisahan relevansi, tetapi di putaran 2 tema seharusnya bisa melintasi kasus.
- **Relevan ≠ negatif.** Topik relevan masih memuat komentar pro-AI (mis. "harus beradaptasi"), yang akan disaring pada tahap sentimen.

#### 2.7.2 Tahap berikutnya (belum dijalankan; tulis sebagai rencana singkat)

1. **Validasi label relevansi** oleh tim, lalu tentukan penanganan:
   - **topik campuran:** dibaca per komentar;
   - **outlier:** ditinjau lewat sampel, atau dialokasikan ulang ke topik terdekat dengan fungsi `reduce_outliers` BERTopic, lalu diperiksa.
2. **Penyaringan komentar negatif.** Analisis sentimen hanya sebagai alat bantu; setiap hasil divalidasi dengan pembacaan manual karena sarkasme dan campur kode.
3. **BERTopic putaran 2** pada komentar yang relevan dan negatif, untuk memunculkan kandidat tema keberatan. Nama kasus (*indomie*, *komdigi*, *polri*) bisa perlu dikeluarkan dari kata penciri agar tema tidak terpecah per kasus.
4. **Codebook.** Tema dari BERTopic divalidasi, digabung atau dipecah, dan dinamai melalui pengodean manual pada sampel.
5. **Perbandingan RQ2/RQ3** memakai **proporsi** tema per tipe organisasi, per jenis video, dan per kasus.

**Sitasi baru untuk daftar pustaka** (format ACM, sesuaikan dengan referensi lain):
- Maarten Grootendorst. 2022. BERTopic: Neural topic modeling with a class-based TF-IDF procedure. arXiv:2203.05794.
- Leland McInnes, John Healy, and James Melville. 2018. UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. arXiv:1802.03426.
- Ricardo J. G. B. Campello, Davoud Moulavi, and Jörg Sander. 2013. Density-Based Clustering Based on Hierarchical Density Estimates. PAKDD 2013.
- Michael Röder, Andreas Both, and Alexander Hinneburg. 2015. Exploring the Space of Topic Coherence Measures. WSDM 2015.
- Adji B. Dieng, Francisco J. R. Ruiz, and David M. Blei. 2020. Topic Modeling in Embedding Spaces. TACL 8.
- Nils Reimers and Iryna Gurevych. 2020. Making Monolingual Sentence Embeddings Multilingual using Knowledge Distillation. EMNLP 2020. Ini untuk model embedding multilingual.

Periksa detail bibliografis (halaman, DOI) sebelum dimasukkan; daftar di atas belum dicek satu per satu.

---

## 2b. Catatan temuan awal untuk Bab Hasil (jangan ditulis di Bab 2)

Bagian ini **bukan isi Bab Metodologi**. Ini gambaran awal agar penulis Bab Hasil tahu arah datanya.

Angka berasal dari label **draft** putaran 1 dan masih mencakup komentar pro-AI, jadi **belum boleh ditulis sebagai temuan**.

**Sebaran komentar relevan:**
- Per tipe organisasi: pemerintah 868 (71%), komersial 353 (29%).
- Per jenis video: pihak ketiga 825, unggahan ulang/arsip 396.

**Pola awal yang menarik untuk RQ2.** Bandingkan setiap tema dengan baseline 71% pemerintah:

| Tema (draft) | % dari komentar pemerintah | Kecenderungan |
|---|---|---|
| Hak cipta dan AI art | 17% | Komersial |
| Seniman dan seni | 28% | Komersial |
| Perbandingan dengan iklan buatan manusia | 58–61% | Seimbang |
| Animator/kreator lokal tidak dipakai | 88% | Pemerintah |
| Penghematan anggaran / dugaan korupsi | 86–89% | Pemerintah |
| Pemerintah tidak kompeten teknologi | 94% | Pemerintah (sesuai dugaan) |

Gambaran kasarnya:
- keberatan terhadap merek komersial condong ke **seni dan hak cipta**;
- keberatan terhadap institusi pemerintah condong ke **uang publik, talenta lokal, dan kompetensi**.

**Peringatan saat menulis nanti:**
- **Sisi komersial praktis = Indomie:** 264 dari 353 komentar komersial yang relevan. Pola seni/hak cipta bisa jadi pola "Indomie 2023", ketika debat AI art sedang ramai, bukan pola komersial secara umum.
- **C04 (POLRI) hanya menyumbang 90 komentar relevan dari 538.** Sebagian besar sisanya kritik umum terhadap polisi (topik campuran).
- **Tema yang muncul di luar dugaan proposal:** "penghematan anggaran sebagai motif" dan "dugaan korupsi". Ini bisa menjadi temuan tersendiri tentang keberatan yang khas institusi pemerintah.

---

## 3. Istilah baku (pakai konsisten di seluruh bab)

| Pakai | Jangan campur dengan |
|---|---|
| GenAI | AI generatif, AI generator, AI (tanpa konteks) |
| komentar (mencakup balasan); "komentar tingkat pertama" dan "balasan" jika perlu dibedakan | reply, comment, tanggapan |
| kasus | case, insiden |
| institusi pemerintah / merek komersial (sesuai RQ2) | instansi, brand, perusahaan (bergantian) |
| jenis video: **unggahan ulang/arsip** dan **video pihak ketiga** | re-upload, commentary, video reaksi |
| tanggal pembekuan data | tanggal crawling, tanggal scraping |
| pemeriksaan kualitas data | cleaning, pembersihan (pilih satu dan konsisten) |
| komentar yang lolos pemeriksaan kualitas | eligible, data bersih |
| keberatan / tema keberatan | kritik, penolakan, komplain (bergantian) |
| prapemrosesan teks | preprocessing, text cleaning (bedakan dari "pemeriksaan kualitas data") |
| teks embedding / teks representasi | input model, teks bersih, teks mentah |
| varian A / varian B (teks representasi) | pipeline 1/2, versi normal/versi slang |
| normalisasi slang | normalisasi alay, koreksi ejaan |
| kata penciri topik | keyword, label topik (label topik = nama yang diberi tim nanti) |
| topik (hasil BERTopic) | klaster, cluster, kelompok (pilih "topik" di teks; "klaster" hanya saat menjelaskan HDBSCAN) |
| outlier (topik −1) | noise, sampah, tidak terklasifikasi |
| putaran 1 / putaran 2 | pass 1/2, tahap 1/2 BERTopic |
| relevan / tidak relevan / campuran | related, off-topic, mixed |
| tema keberatan (hasil akhir setelah codebook) | topik (topik = keluaran BERTopic, tema = hasil interpretasi tim) |

Catatan:
- Data diambil lewat API resmi, jadi jangan sebut "scraping".
- Istilah Inggris yang dipakai (*digital trace*, *topic modeling*, *flagging*) ditulis miring.

---

## 4. Keterbatasan yang wajib disebut (di bab ini atau bab penutup)

1. **Hanya dua dari tiga jenis video** yang ada di korpus; tidak ada unggahan resmi organisasi.
2. **Jenis video berimpit dengan kasus.** Setiap kasus hanya diwakili satu jenis video, sehingga perbedaan antarjenis video (RQ3) tidak bisa dipisahkan dari perbedaan antarkasus.
3. **Ketimpangan korpus:**
   - pemerintah 72,8% vs komersial 27,2%;
   - sisi komersial didominasi Indomie;
   - tiga dari empat kasus pemerintah melibatkan Komdigi.
4. **Perbedaan waktu:** Indomie terjadi 2023, kasus lain 2025. Sikap publik terhadap GenAI bisa berubah dalam rentang itu.
5. **Verifikasi:** hanya C01 dan C02 yang terverifikasi lewat media kredibel (update jika sumber untuk kasus lain sudah ditemukan).
6. **Bahasa:**
   - komentar berbahasa Inggris dari pengguna Indonesia ikut dikeluarkan (±55 komentar) karena kriteria bahasa Indonesia sebagai bahasa utama;
   - bahasa daerah tidak dideteksi terpisah;
   - Melayu digabung dengan Indonesia.
7. **Aturan spam** disusun tim dan divalidasi dengan pembacaan manual, bukan alat deteksi bot yang tervalidasi.
8. **Keterbatasan platform:** komentar yang dihapus, disembunyikan, atau tersaring otomatis oleh YouTube sebelum tanggal pembekuan tidak terjangkau.
9. **Prapemrosesan:**
   - 45 komentar (1,4%) melebihi batas 128 token model embedding, sehingga hanya bagian awalnya yang terbaca;
   - kamus slang disusun dari komentar Instagram tahun 2018, jadi slang yang lebih baru atau khas YouTube mungkin tidak tercakup; sebagian pemetaannya dikoreksi manual;
   - pelepasan akhiran *-nya* berbasis aturan dan keliru pada sebagian kecil kata (<1%).
10. **Topic modeling:**
    - 32% komentar menjadi outlier pada putaran 1 dan butuh penanganan tambahan;
    - hasil BERTopic bergantung pada parameter, sehingga konfigurasi dipilih dari percobaan yang tercatat, bukan satu-satunya kemungkinan;
    - pelabelan relevansi dilakukan per topik berdasarkan sampel komentar, sehingga komentar di dalam topik bisa tidak seragam;
    - sisi komersial didominasi komentar kasus Indomie.

---

## 5. Checklist sebelum draft dikirim ke tim

- [ ] Paragraf pertama menyebut desain penelitian dan alasannya
- [ ] Setiap sub-bab punya pengantar yang tidak kaku
- [ ] Tidak ada penjelasan teori yang mengulang Pendahuluan
- [ ] Kala lampau untuk tahap yang sudah selesai
- [ ] Kolom verifikasi [ISI] di tabel kasus sudah diisi (atau ditandai sebagai keterbatasan)
- [ ] Ringkasan screening log (kata kunci, tanggal, pengecualian) sudah ada
- [ ] Angka pemeriksaan kualitas dan prapemrosesan sudah versi final (v2 setelah tinjauan manual)
- [ ] Sitasi *Colloquial Indonesian Lexicon* dan *stopwords-iso* sudah masuk daftar pustaka
- [ ] Sitasi BERTopic, UMAP, HDBSCAN, koherensi (Röder dkk.), keragaman (Dieng dkk.), dan model embedding sudah masuk dan detailnya dicek
- [ ] Label relevansi putaran 1 sudah divalidasi tim (bukan lagi draft) sebelum angkanya ditulis final
- [ ] Penanganan outlier dan topik campuran sudah diputuskan dan ditulis
- [ ] Isi bagian 2b (temuan awal) **tidak** ikut masuk Bab 2
- [ ] Semua angka cocok dengan `quality_report` dan `collection_log.json`
- [ ] Alasan RTV/Mentari TV sebagai merek komersial sudah dijelaskan
- [ ] Istilah sesuai tabel di bagian 3
- [ ] Tidak ada API key, nama akun, atau kutipan dengan nama pengguna
- [ ] Sitasi memakai format angka [n] seperti proposal
- [ ] Sudah dicek dengan /humanizer
