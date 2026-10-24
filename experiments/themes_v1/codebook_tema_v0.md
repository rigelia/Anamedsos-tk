# Codebook Tema Keberatan v0 (draf)

**Tujuan:** menjawab RQ1 (tema keberatan apa saja yang muncul) dan menjadi dasar RQ2/RQ3 (komposisi tema per jenis organisasi dan jenis video). Unit analisis: satu komentar berlabel sikap `tolak` (1.627 komentar, `experiments/stance_v1/sikap_final_v2.csv`).

**Asal tema:** tema diturunkan dari 25 topik BERTopic putaran 2 (`experiments/pass2_v1_nn30_mcs10_a/`, lihat `themes_draft.csv`) dan empat tema yang diharapkan proposal. Draf ini diuji Claude pada 50 komentar acak (`pilot_codebook_ids.csv`, seed 7): semua komentar bisa dikode, tidak ada yang jatuh ke `LT`. Status: **draf, perlu disetujui tim.**

Yang dikode adalah **alasan keberatan**, bukan nada atau sasaran. Komentar sarkas dibaca maksudnya (sama dengan panduan sikap aturan 1).

## Cara mengode

- Baca komentar bersama **kasus/video** dan **komentar induk** kalau komentar itu balasan.
- Isi **`tema_utama`** (wajib, satu kode): alasan keberatan yang paling ditekankan. Kolom ini yang dipakai untuk proporsi RQ2/RQ3, sehingga jumlahnya selalu 100%.
- Isi **`tema_kedua`** (opsional, satu kode): alasan lain yang juga jelas disebut. Dipakai untuk analisis tambahan (tema yang sering muncul bersama), tidak untuk proporsi utama. **Kosongkan** kalau komentar hanya punya satu alasan; jangan diisi kode yang sama dengan `tema_utama`.
- Topik BERTopic boleh dipakai sebagai petunjuk, tetapi **bukan** label. Komentar di topik "animator" tetap dikode `AK` kalau alasannya soal uang.

## Delapan tema

| Kode | Tema | Definisi | Termasuk | Contoh dari data |
|---|---|---|---|---|
| `KV` | Kualitas visual | Keberatan pada **hasil visual**: cacat, jelek, aneh, menyeramkan, kaku, tidak dipoles. | Cacat anatomi/objek (tangan nyambung, jari 7, sayap polisi); reaksi saat melihat (jelek, jijik, muntah lihatnya); uncanny/takut/creepy; "minimal di-polish/di-retouch"; "manual lebih bagus" tanpa menyebut karya tertentu; penerimaan bersyarat "boleh AI kalau bagus". | "menit ke 🤣🤣 tangan nyatu kanan kiri" · "Mengerikan" · "Oke lah pake ai kalo bagus animasinya lah ini 🗿" · "Iklan terbagus yg pernah gua lihat sampai sampai gua muntah se liter" |
| `PK` | Pekerja kreatif | Keberatan atas **dampak pada atau pengabaian terhadap kreator manusia**. | "Seharusnya sewa animator/ilustrator lokal"; talenta Indonesia diabaikan; tidak menghargai karya anak bangsa; kreator kehilangan pekerjaan/komisi; kekecewaan dari sesama kreator. | "Mengapa iklan pemerintah harus pakai ai padahal ada animator lokal😂" · "Kami dari SKDK liat animasi kaya gini rada sakit hati😂" · "pemerintah itu kurang menghargai kerjaan animator di Indonesia" |
| `HC` | Hak cipta & keaslian karya | Keberatan pada **cara AI menghasilkan karya**: memakai karya orang tanpa izin, tanpa royalti, meniru gaya, atau bukan karya seni yang sah. | Data latih dicomot; artstyle; risiko dituntut Disney/Pixar; AI art menghilangkan integritas/feel karya buatan tangan. | "kena tuntut sama disney atau pixar karena bikin animasi visual AI kayak mereka tanpa izin" · "AI itu cuma nyomot hasil karya orang lain tanpa ngasih royalti ke kreator" |
| `AK` | Biaya, anggaran & korupsi | Keberatan yang **berkaitan dengan uang**: penghematan biaya, organisasi pelit, prioritas belanja, anggaran, dugaan mark-up atau korupsi. | Sindiran "efisiensi anggaran"; "dana dikorupsi makanya pakai AI"; "tebak anggarannya"; "robot 3M mampu, animator tidak"; perusahaan besar pelit/cari untung; uang pajak. | "pff anggaran tinggi hasilnya ai🖐️😂🖐️" · "Hemat anggaran / Korupsi anggaran?" · "Mengeluarkan biaya untuk byr artist ilustrator itu buang duit mereka" |
| `PB` | Perbandingan dengan karya manusia | Menilai buruk penggunaan AI dengan **membandingkannya dengan karya atau alat buatan manusia yang disebut namanya**. | Iklan Marjan, BNI anime, Pocari, Sasa; animasi Tekotok, BaLiTa, Minecraft; saran memakai Blender/SFM/Unreal. | "Mending iklan marjan anjir absolute cinema" · "kerenan BaLiTa dari kominfo bjir" · "mending pakai source filmaker ( SFM ) atau blender aja" |
| `KO` | Kepantasan organisasi | Keberatan bahwa **organisasi ini tidak pantas atau tidak kompeten** memakai GenAI, tanpa alasan uang. | Tidak konsisten ("cintai produk lokal" tapi pakai AI); "AI bukan inovasi"; kebijakan AI pemerintah (lomba prompt, "Indonesia AI 2045"); pemakaian berulang oleh organisasi yang sama ("AI mulu", "lagi-lagi"); pencitraan/propaganda; "ga niat", "jangan pakai AI"; organisasi sebesar ini kok pakai AI. | "katanya suruh mencintai produk lokal, kok malah bikin animasi aja harus pakai AI sih???" · "inilah mimpi pemerintah... semuanya harus pake AI." · "Pke ai bukan inovasi tp kemunduran" |
| `AU` | Kekhawatiran umum tentang AI | Keberatan terhadap **AI secara umum**, bukan khusus pada organisasi atau kreator. | AI menggantikan manusia (umum); AI berbahaya; AI makin dipakai di mana-mana (merek/organisasi lain juga); ketergantungan pada AI. | "Kaya seolah olah ada entitas lain nya mengganti kan manusia serem" · "Bahaya nya sebuah ai bukan bahaya buat anak kont-🤡" · "Axe ID juga iklannya pake AI" |
| `EJ` | Ejekan tanpa alasan | Menolak, mengejek atau menghina **tanpa menyebut alasan** yang masuk tema lain. | "Layak dihujat"; "AI hama", "najis AI"; tawa/ejekan; makian ke organisasi; ironi tanpa alasan ("video ini konten berbahaya"); pertanyaan retoris "siapa yang tanggung jawab". | "sangat layak dihujat" · "Iklan gblk😂😂😂" · "Ai pula😂" |
| `LT` | Lainnya | Ada keberatan, tetapi alasannya tidak masuk tema mana pun. | Dicatat di kolom `catatan` supaya bisa menjadi tema baru kalau sering muncul. | (tidak muncul di pilot) |

## Aturan kasus sulit

1. **Uang dan pekerja kreatif bersamaan** ("Beli robot 3M mampu, sewa animator ga mampu"): `tema_utama` mengikuti inti argumennya. Soal belanja, korupsi atau pelit → `AK`. Soal penghargaan atau lapangan kerja kreator → `PK`. Tema satunya masuk `tema_kedua`.
2. **`KV` vs `EJ`:** kata yang merujuk pada **tampilan** (jelek, jijik lihatnya, seram, aneh, cacat) → `KV`. Hinaan ke AI atau organisasi tanpa merujuk tampilan ("gblk", "AI hama", "layak dihujat") → `EJ`.
3. **`KV` vs `PB`:** kalau pembandingnya disebut namanya (Marjan, Pocari, Blender) → `PB`. Kalau hanya "manual lebih bagus" atau "animator lebih bagus" tanpa nama → `KV`. Kalau intinya "sewa animator" → `PK`.
4. **`KO` vs `AK`:** kalau uang disebut sebagai alasan → `AK`. Kalau tidak → `KO`.
5. **"Organisasi lain juga pakai AI"**: penyebaran AI ke banyak merek/organisasi → `AU`. Pemakaian berulang oleh organisasi yang **sama** ("udah 2 kali", "AI mulu") → `KO`.
6. **Takut / seram**: takut melihat visualnya (creepy, "mama aku takut") → `KV`. Takut terhadap AI secara umum ("AI akan menggantikan manusia") → `AU`.
7. **Balasan pendek** ("fr🔥🔥🔥", "Hell nah", "bener") dikode mengikuti alasan pada **komentar induk** yang disetujuinya. Kalau induknya juga tanpa alasan → `EJ`.
8. **Sarkas** dibaca maksudnya. "Harus. Agar pemerintah bisa di anggap melek tekhnologi… 🗿" → `KO`.
9. **Kebijakan AI pemerintah** (lomba prompt AI, wapres juri lomba AI, infrastruktur digital belum siap tapi mau AI) → `KO`.
10. **Kritik polisi/pemerintah yang dikaitkan dengan iklan AI** (sudah `tolak` menurut panduan sikap): pencitraan/propaganda → `KO`. Duit rakyat/korupsi → `AK`.
11. **Debat AI art umum** di kolom komentar (panduan sikap aturan 14): argumen hak cipta/data latih → `HC`. Seniman kehilangan pekerjaan → `PK`. AI menggantikan manusia secara umum → `AU`.
12. **Tie-breaker** kalau dua tema sama kuat dan aturan di atas tidak memutuskan: pilih yang lebih spesifik, dengan urutan `HC` > `AK` > `PK` > `PB` > `KV` > `KO` > `AU` > `EJ`. `EJ` hanya dipakai kalau tidak ada alasan sama sekali.

## Hubungan dengan proposal dan topik BERTopic

| Tema proposal | Kode | Topik BERTopic utama (pass 2) |
|---|---|---|
| Kualitas visual | `KV` | 2 (sebagian), 11, 12, 13, 17, 18 |
| Dampak pada pekerja kreatif | `PK` | 3, 4, 19 |
| Hak cipta | `HC` | 9 |
| Kepantasan organisasi memakai GenAI | `KO` | 5, 7, 8, 14, 24 |
| *(baru)* Biaya, anggaran & korupsi | `AK` | 6, 16, 21, 22, 23 |
| *(baru)* Perbandingan dengan karya manusia | `PB` | 1 |
| *(baru)* Kekhawatiran umum tentang AI | `AU` | 0 (sebagian) |
| *(baru)* Ejekan tanpa alasan | `EJ` | 2 (sebagian), 10, 20 |

`PB` dan `EJ` bisa dipertanyakan sebagai "tema": `PB` adalah cara berargumen, dan `EJ` adalah keberatan tanpa alasan. Keduanya tetap dipisah karena jumlahnya besar. Kalau tim memilih menggabungkan (misalnya `PB` ke `KV`), keputusan itu dicatat di Riwayat dan kode lama tetap bisa dipetakan ulang.

## Prosedur dan validasi (usulan)

1. **Kalibrasi (opsional, disarankan):** anggota tim mengode 50 komentar pilot (`pilot_codebook_ids.csv`) **tanpa melihat** `pilot_claude.csv`. Bandingkan, lalu perbaiki definisi yang sering berbeda sebelum pengodean penuh. Pelajaran dari tahap sikap: κ rendah (0,235) terutama karena ambang batas yang berbeda, dan baru ketahuan setelah semua komentar dilabeli.
2. **Pengodean penuh:** Claude mengode 1.627 komentar `tolak` dengan codebook yang sudah disetujui.
3. **Validasi buta:** 100 komentar acak (seed 42, di luar pilot) dikode manusia tanpa melihat kode Claude. κ dihitung pada `tema_utama`, dengan target ≥ 0,6. Ketidaksepakatan diadjudikasi dengan cara yang sama seperti tahap sikap.
4. **Analisis:** proporsi `tema_utama` per `org_type` (RQ2), per `video_type` (RQ3) dan **per kasus**, karena beberapa sel hanya berisi satu kasus (lihat CLAUDE.md, "Balance"). Robustness check: hitung ulang tanpa kasus `to_verify`.

## Riwayat

- v0 (2026-10-24): draf oleh Claude dari 25 topik pass 2, `themes_draft.csv` dan pilot 50 komentar. Dibanding `themes_draft.csv`: `anggaran_korupsi` diperluas menjadi `AK` (termasuk "perusahaan pelit", topik 22 dipindah dari kepantasan organisasi), dan `AU` ditambahkan dari topik 0.
