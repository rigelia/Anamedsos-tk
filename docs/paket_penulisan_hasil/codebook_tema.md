# Codebook Tema Keberatan v2

**Tujuan:** menjawab RQ1 (tema keberatan apa saja yang muncul) dan menjadi dasar RQ2/RQ3 (komposisi tema per jenis organisasi dan jenis video). Unit analisis: satu komentar berlabel sikap `tolak` (1.627 komentar, `experiments/stance_v1/sikap_final_v2.csv`).

**Asal tema:** tema diturunkan dari 25 topik BERTopic putaran 2 (`experiments/pass2_v1_nn30_mcs10_a/`, lihat `themes_draft.csv`) dan empat tema yang diharapkan proposal. Draf ini diuji Claude pada 50 komentar acak (`pilot_codebook_ids.csv`, seed 7): semua komentar bisa dikode, tidak ada yang jatuh ke `LT`. Status: **v1, direvisi setelah kalibrasi dengan Zillan** (lihat Riwayat).

Yang dikode adalah **alasan keberatan**, bukan nada atau sasaran. Komentar sarkas dibaca maksudnya (sama dengan panduan sikap aturan 1).

**Alasan tersirat tetap dikode.** Kalau alasannya bisa disimpulkan dengan jelas dari teks, komentar induk atau video, kode alasan itu: "0Rp" yang membalas "Tebak anggaran" → `AK`; "Mengerikan" di bawah video AI → `KV`; "kena tuntut Disney/Pixar karena tanpa izin" → `HC`. `EJ` hanya untuk komentar yang benar-benar tidak memberi alasan.

## Cara mengode

- Baca komentar bersama **kasus/video** dan **komentar induk** kalau komentar itu balasan.
- Isi **`tema_utama`** (wajib, satu kode): alasan keberatan yang paling ditekankan. Kolom ini yang dipakai untuk proporsi RQ2/RQ3, sehingga jumlahnya selalu 100%.
- Isi **`tema_kedua`** (opsional, satu kode): alasan lain yang juga jelas disebut. Dipakai untuk analisis tambahan (tema yang sering muncul bersama), tidak untuk proporsi utama. **Kosongkan** kalau komentar hanya punya satu alasan; jangan diisi kode yang sama dengan `tema_utama`.
- Topik BERTopic boleh dipakai sebagai petunjuk, tetapi **bukan** label. Komentar di topik "animator" tetap dikode `AK` kalau alasannya soal uang.

## Tujuh tema

| Kode | Tema | Definisi | Termasuk | Contoh dari data |
|---|---|---|---|---|
| `KV` | Kualitas visual | Keberatan pada **hasil visual**: cacat, jelek, aneh, menyeramkan, kaku, tidak dipoles. | Cacat anatomi/objek (tangan nyambung, jari 7, sayap polisi); reaksi saat melihat (jelek, jijik, muntah lihatnya); uncanny/takut/creepy; "minimal di-polish/di-retouch"; "manual lebih bagus"; **perbandingan dengan karya/alat buatan manusia yang lebih bagus** (Marjan, Pocari, BaLiTa, Minecraft, Blender/SFM); AI menghilangkan feel/integritas karya buatan tangan; penerimaan bersyarat "boleh AI kalau bagus". | "menit ke 🤣🤣 tangan nyatu kanan kiri" · "Mengerikan" · "Oke lah pake ai kalo bagus animasinya lah ini 🗿" · "Iklan terbagus yg pernah gua lihat sampai sampai gua muntah se liter" · "Masih bagusan animasi minecraft indo 💀💀" · "Mending iklan marjan anjir absolute cinema" |
| `PK` | Pekerja kreatif | Keberatan atas **dampak pada atau pengabaian terhadap kreator manusia**. | "Seharusnya sewa animator/ilustrator lokal"; talenta Indonesia diabaikan; tidak menghargai karya anak bangsa; kreator kehilangan pekerjaan/komisi; kekecewaan dari sesama kreator; "katanya cintai produk lokal" tapi pakai AI. | "Mengapa iklan pemerintah harus pakai ai padahal ada animator lokal😂" · "katanya suruh mencintai produk lokal, kok malah bikin animasi aja harus pakai AI sih???" · "Kami dari SKDK liat animasi kaya gini rada sakit hati😂" · "pemerintah itu kurang menghargai kerjaan animator di Indonesia" |
| `HC` | Hak cipta | Keberatan pada **cara AI menghasilkan karya**: memakai karya orang tanpa izin, tanpa royalti, atau meniru gaya. | Data latih dicomot; artstyle; risiko dituntut Disney/Pixar. (Feel/integritas karya buatan tangan → `KV`.) | "kena tuntut sama disney atau pixar karena bikin animasi visual AI kayak mereka tanpa izin" · "AI itu cuma nyomot hasil karya orang lain tanpa ngasih royalti ke kreator" |
| `AK` | Biaya, anggaran & korupsi | Keberatan yang **berkaitan dengan uang**: penghematan biaya, organisasi pelit, prioritas belanja, anggaran, dugaan mark-up atau korupsi. | Sindiran "efisiensi anggaran"; "dana dikorupsi makanya pakai AI"; "tebak anggarannya"; "robot 3M mampu, animator tidak"; perusahaan besar pelit/cari untung; uang pajak. | "pff anggaran tinggi hasilnya ai🖐️😂🖐️" · "Hemat anggaran / Korupsi anggaran?" · "Mengeluarkan biaya untuk byr artist ilustrator itu buang duit mereka" |
| `KO` | Kepantasan organisasi | Keberatan bahwa **organisasi ini tidak pantas atau tidak kompeten** memakai GenAI, tanpa alasan uang. | "AI bukan inovasi"; kebijakan AI pemerintah (lomba prompt, "Indonesia AI 2045"); pemakaian berulang oleh organisasi yang sama ("AI mulu", "lagi-lagi"); pencitraan/propaganda; "ga niat", "jangan pakai AI"; organisasi sebesar ini kok pakai AI. | "Damkar mah gak usah buat vidio ai segala udh terpercaya di masyarakat" · "inilah mimpi pemerintah... semuanya harus pake AI." · "Pke ai bukan inovasi tp kemunduran" |
| `AU` | Kekhawatiran umum tentang AI | Keberatan terhadap **AI secara umum**, bukan khusus pada organisasi atau kreator. | AI menggantikan manusia (umum); AI berbahaya; AI makin dipakai di mana-mana (merek/organisasi lain juga); ketergantungan pada AI. | "Kaya seolah olah ada entitas lain nya mengganti kan manusia serem" · "Bahaya nya sebuah ai bukan bahaya buat anak kont-🤡" · "Axe ID juga iklannya pake AI" |
| `EJ` | Ejekan tanpa alasan | Menolak, mengejek atau menghina **tanpa menyebut alasan** yang masuk tema lain. | "Layak dihujat"; "AI hama", "najis AI"; tawa/ejekan; makian ke organisasi; ironi tanpa alasan ("video ini konten berbahaya"); pertanyaan retoris "siapa yang tanggung jawab". | "sangat layak dihujat" · "Iklan gblk😂😂😂" · "Ai pula😂" |
| `LT` | Lainnya | Ada keberatan, tetapi alasannya tidak masuk tema mana pun. | Dicatat di kolom `catatan` supaya bisa menjadi tema baru kalau sering muncul. | (tidak muncul di pilot) |

## Aturan kasus sulit

1. **Uang dan pekerja kreatif bersamaan** ("Beli robot 3M mampu, sewa animator ga mampu"): `tema_utama` mengikuti inti argumennya. Soal belanja, korupsi atau pelit → `AK`. Soal penghargaan atau lapangan kerja kreator → `PK`. Tema satunya masuk `tema_kedua`.
2. **`KV` vs `EJ`:** kata yang merujuk pada **tampilan** (jelek, jijik lihatnya, seram, aneh, cacat) → `KV`. Hinaan ke AI atau organisasi tanpa merujuk tampilan ("gblk", "AI hama", "layak dihujat") → `EJ`.
3. **Perbandingan dengan karya manusia** (Marjan, BNI anime, Pocari, BaLiTa, Blender) bukan tema sendiri; kode **isi** pembandingnya. Hasilnya lebih bagus → `KV`. Budget lebih kecil tapi hasil lebih bagus → `AK`. Seharusnya sewa kreator → `PK`. Murni candaan tanpa isi → `EJ`.
4. **`KO` vs `AK`:** kalau uang disebut sebagai alasan → `AK`. Kalau tidak → `KO`.
5. **"Organisasi lain juga pakai AI"**: penyebaran AI ke banyak merek/organisasi → `AU`. Pemakaian berulang oleh organisasi yang **sama** ("udah 2 kali", "AI mulu") → `KO`.
6. **Takut / seram**: takut melihat visualnya (creepy, "mama aku takut") → `KV`. Takut terhadap AI secara umum ("AI akan menggantikan manusia") → `AU`.
7. **Balasan pendek** ("fr🔥🔥🔥", "Hell nah", "bener") dikode mengikuti alasan pada **komentar induk** yang disetujuinya. Kalau induknya juga tanpa alasan → `EJ`.
8. **Sarkas** dibaca maksudnya. "Harus. Agar pemerintah bisa di anggap melek tekhnologi… 🗿" → `KO`.
9. **Kebijakan AI pemerintah** (lomba prompt AI, wapres juri lomba AI, infrastruktur digital belum siap tapi mau AI) → `KO`.
10. **Kritik polisi/pemerintah yang dikaitkan dengan iklan AI** (sudah `tolak` menurut panduan sikap): pencitraan/propaganda → `KO`. Duit rakyat/korupsi → `AK`.
11. **Debat AI art umum** di kolom komentar (panduan sikap aturan 14): argumen hak cipta/data latih → `HC`. Seniman kehilangan pekerjaan → `PK`. AI menggantikan manusia secara umum → `AU`.
12. **Tie-breaker** kalau dua tema sama kuat dan aturan di atas tidak memutuskan: pilih yang lebih spesifik, dengan urutan `HC` > `AK` > `PK` > `KV` > `KO` > `AU` > `EJ`. `EJ` hanya dipakai kalau tidak ada alasan sama sekali.

## Konvensi untuk komentar pendek (v1.1)

Ditambahkan saat Claude mengode 1.627 komentar, untuk pola pendek yang sering muncul dan belum diatur aturan di atas.

13. **Mempertanyakan atau menolak pemakaian itu sendiri** ("Kenapa pakai AI?", "Kok pake AI", "AI lagi/mulu/terus", "Jangan/stop pakai AI", "Ga niat") → `KO`.
14. **Penilaian kualitas produk** ("jelek", "burik", "sampah", "trash", "busuk", "cringe", "sakit mata lihatnya") → `KV`. **Makian atau tawa tanpa penilaian** ("Ai pula😂", "Cih ai", "AI hama", "Iklan gblk", "video tAI") → `EJ`.
15. **Ironi "konten berbahaya"** (video ini sendiri konten berbahaya) → `EJ`. Pernyataan bahwa **AI itu berbahaya** → `AU`.
16. **Pujian sarkas pada pilihan organisasi** ("Kreatif sekali", "Wow canggih", "Negeri kita sangat maju") → `KO`.
17. **"Tebak anggaran", "berapa biayanya", "ga modal"** → `AK`.
18. **Pejabat tua/gaptek/boomer/"puber AI"** → `KO`.
19. **Organisasi lain yang memakai AI** (Shopee, Axe, Mentari TV, kementerian lain) → `AU`. Pemakaian lain oleh **organisasi atau program yang sama** (iklan MBG Komdigi sebelumnya, kampanye pasangan yang sama) → `KO`.
20. **Mirip Disney/Pixar** sebagai tuduhan meniru atau risiko dituntut → `HC`.

## Aturan tambahan dari adjudikasi validasi buta (v2)

Diturunkan dari 45 komentar yang diadjudikasi Zillan (`adjudikasi_tema.xlsx`). Aturan ini mengalahkan konvensi 13–20 kalau bertentangan.

21. **Konvensi 13–20 dikonfirmasi** dalam adjudikasi (#4, #29, #33, #50, #59, #84, #99), kecuali yang diubah di bawah.
22. **"Cringe" / "norak" tanpa merujuk tampilan** → `EJ` (#12). Kalau disertai rujukan pada hasil ("norak banget hasilnya") tetap `KV`.
23. **Kreator manusia sebagai pembanding** ("animator Minecraft menangis melihat ini", "kalah saing sama animator lokal", "animasi kerja keras vs tulis prompt", "coba kayak Good Day pakai ilustrator") → `PK` (#13, #58, #79). Pembanding berupa **karya** yang lebih bagus (Marjan, BNI, Adit Sopo Jarwo) tetap `KV` (aturan 3).
24. **Debat AI art umum soal seni, jiwa atau status "artist"** ("Artist AI bukan artist", "seni itu jiwa", "gambar AI tidak ada seninya") → `AU` (#20, #73). Ini mengubah perubahan v1 nomor 4: feel karya buatan tangan → `KV` hanya kalau dikaitkan dengan **tampilan iklan ini**. Alasan "AI meniru gambar yang sudah jadi" → `HC` (#60).
25. **Orang atau budaya pengguna AI secara umum** (anak muda/staf yang cuma pakai generator, AI dikaitkan dengan konten cabul, ketergantungan manusia pada AI) → `AU` (#68, #70, #77).
26. **Sindiran pendek yang menyebut pemakaian AI** ("Singkat padat pake ai 😑", "Mantap pake ai", "Absolute cinema bagi kominjomok") → `KO` (#23, #56, #85). Seruan tanpa sasaran ("WUIHH CANGGIH NYOO") dan ejekan organisasi yang gagal ("niru biar viral eh malah dihujat😂") → `EJ` (#11, #62). Hinaan ke AI secara umum tanpa alasan ("AI hanya untuk orang lemah") → `EJ` (#22).
27. **Penekanan:** kalau komentar memuat dua alasan yang dirangkai ("tua bangka gak tau teknologi sampai parahnya tidak mendukung studio film anak bangsa"), `tema_utama` adalah alasan yang menjadi puncak kalimat (#72 → `PK`).

**Pengecualian, bukan aturan:** #54 "Apa bende nih wee gk niat bikin" → `AU` (keputusan adjudikasi; menurut aturan di atas komentar serupa tetap `KO`).

## Hubungan dengan proposal dan topik BERTopic

| Tema proposal | Kode | Topik BERTopic utama (pass 2) |
|---|---|---|
| Kualitas visual | `KV` | 1 (perbandingan), 2 (sebagian), 11, 12, 13, 17, 18 |
| Dampak pada pekerja kreatif | `PK` | 3, 4, 19 |
| Hak cipta | `HC` | 9 |
| Kepantasan organisasi memakai GenAI | `KO` | 5, 7, 8, 14, 24 |
| *(baru)* Biaya, anggaran & korupsi | `AK` | 6, 16, 21, 22, 23 |
| *(baru)* Kekhawatiran umum tentang AI | `AU` | 0 (sebagian) |
| *(baru)* Ejekan tanpa alasan | `EJ` | 2 (sebagian), 10, 20 |

`EJ` bukan alasan, tetapi tetap dicatat karena menunjukkan berapa banyak keberatan yang diungkapkan tanpa argumen. Topik BERTopic 1 (perbandingan dengan iklan Marjan/BNI/Pocari) tidak menjadi tema sendiri; perbandingan adalah cara berargumen, jadi dikode menurut isinya (aturan 3).

## Prosedur dan validasi (usulan)

1. **Kalibrasi (sudah, v0 → v1):** anggota tim mengode 50 komentar pilot (`pilot_codebook_ids.csv`) **tanpa melihat** `pilot_claude.csv`. Bandingkan, lalu perbaiki definisi yang sering berbeda sebelum pengodean penuh. Pelajaran dari tahap sikap: κ rendah (0,235) terutama karena ambang batas yang berbeda, dan baru ketahuan setelah semua komentar dilabeli.
2. **Pengodean penuh:** Claude mengode 1.627 komentar `tolak` dengan codebook yang sudah disetujui.
3. **Validasi buta:** 100 komentar acak (seed 42, di luar pilot) dikode manusia tanpa melihat kode Claude. κ dihitung pada `tema_utama`, dengan target ≥ 0,6. Ketidaksepakatan diadjudikasi dengan cara yang sama seperti tahap sikap.
4. **Analisis:** proporsi `tema_utama` per `org_type` (RQ2), per `video_type` (RQ3) dan **per kasus**, karena beberapa sel hanya berisi satu kasus (lihat CLAUDE.md, "Balance"). Robustness check: hitung ulang tanpa kasus `to_verify`.

## Riwayat

- v0 (2026-10-24): draf oleh Claude dari 25 topik pass 2, `themes_draft.csv` dan pilot 50 komentar. Dibanding `themes_draft.csv`: `anggaran_korupsi` diperluas menjadi `AK` (termasuk "perusahaan pelit", topik 22 dipindah dari kepantasan organisasi), dan `AU` ditambahkan dari topik 0.
- v1 (2026-10-24): setelah kalibrasi. Zillan mengode 49 dari 50 komentar pilot tanpa melihat kode Claude (`kalibrasi_tema.xlsx`; kode "KP" dibaca `PK`, salah ketik yang dikonfirmasi Zillan). `tema_utama` cocok 28/49, κ = 0,484 (`kalibrasi_hasil.json`). Perubahan: (1) `PB` dihapus karena tidak cocok satu pun (Claude 6 PB, Zillan memberi EJ 3, KV 2, AK 1); perbandingan dikode menurut isinya (aturan 3). (2) Alasan tersirat tetap dikode; `EJ` hanya untuk komentar tanpa alasan (Zillan memakai EJ 16 kali, Claude 6). (3) "Cintai produk lokal tapi pakai AI" dipindah dari `KO` ke `PK`. (4) Feel/integritas karya buatan tangan dipindah dari `HC` ke `KV`; `HC` dibatasi pada hak cipta/izin/data latih. (5) `tema_kedua` dikosongkan kalau hanya ada satu alasan. Codebook v0 disimpan di `codebook_tema_v0.md`.
- v1.1 (2026-10-24): konvensi 13–20 ditambahkan selama Claude mengode semua 1.627 komentar `tolak` (`kode_claude_v1.txt`), **sebelum** validasi buta dibuat, sehingga validator memakai versi yang sama dengan Claude. Konvensi ini merangkum keputusan Claude dan belum dikonfirmasi tim.
- v2 (2026-10-24): setelah validasi buta. Seorang anggota tim mengode 100 komentar (`filled/validasi_tema_anmed.xlsx`) tanpa melihat kode Claude: cocok 55/100, **κ = 0,452** (`validasi_tema_hasil.json`). Validator memakai `AU` 22 kali (Claude 3). Zillan mengadjudikasi 45 ketidaksepakatan: 25 sesuai Claude, 16 sesuai validator, 4 kode lain (`adjudikasi_tema_hasil.json`); Claude v1 vs final 80/100, κ = 0,753; validator vs final 71/100, κ = 0,65. Aturan 21–27 ditambahkan. Claude membaca ulang kandidat komentar di luar sampel untuk tiap pola dan mengubah 14 kode (`perubahan_tema_v2_claude.csv`); hasil di `tema_final_v2.csv` (`relabel_tema_v2.py`). Codebook v1.1 disimpan di `codebook_tema_v1.md`.
