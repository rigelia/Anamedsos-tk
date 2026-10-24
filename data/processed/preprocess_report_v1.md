# Laporan prapemrosesan BERTopic (v1)

- Dibuat: 2026-09-30T04:45:36Z (preprocess_bertopic.py v1.0)
- Input: `data\interim\comments_quality_v1.csv` (3145 komentar eligible)
- Output: `data\processed\comments_bertopic_v1.csv`, stopword: `resources\stopwords_bertopic_v1.txt`

## Statistik

| ukuran | nilai |
|---|---|
| komentar | 3145 |
| kosakata_A_semua | 7079 |
| kosakata_B_semua | 6150 |
| kosakata_A_tanpa_stopword | 6476 |
| kosakata_B_tanpa_stopword | 5628 |
| token_diubah_B | {'override': 379, 'lexicon': 5669, 'nya': 924} |
| komentar_tanpa_kata_isi_setelah_stopword | 73 |
| rata2_token_repr | 14.4 |
| model_max_seq_length | 128 |
| komentar_terpotong_di_model | 45 |
| median_token_model | 15 |
| p95_token_model | 69 |

## Stopword (dipakai di CountVectorizer, tidak dihapus dari teks)

| komponen | jumlah |
|---|---|
| stopwords_iso_id | 758 |
| sklearn_english | 318 |
| custom_slang_filler | 129 |
| kept_meaningful | ['jelas', 'kurang', 'masalah', 'merasa', 'penting', 'rasa'] |
| total | 1171 |

## Normalisasi terbanyak (varian B)

| sebelum | sesudah | sumber | n |
|---|---|---|---|
| yg | yang | lexicon | 496 |
| aja | saja | lexicon | 450 |
| pake | pakai | lexicon | 441 |
| gak | enggak | lexicon | 364 |
| ga | enggak | lexicon | 254 |
| gw | gue | lexicon | 240 |
| kalo | kalau | override | 228 |
| udah | sudah | lexicon | 183 |
| gk | enggak | lexicon | 134 |
| gitu | begitu | lexicon | 114 |
| kek | kayak | lexicon | 95 |
| klo | kalau | override | 94 |
| emang | memang | lexicon | 88 |
| liat | lihat | lexicon | 76 |
| gini | begini | lexicon | 67 |
| ama | sama | lexicon | 64 |
| bener | benar | lexicon | 62 |
| dah | deh | lexicon | 53 |
| nonton | menonton | lexicon | 53 |
| udh | sudah | lexicon | 49 |
| gimana | bagaimana | lexicon | 48 |
| nggak | enggak | lexicon | 46 |
| kaya | kayak | lexicon | 45 |
| iklannya | iklan | nya | 41 |
| karna | karena | lexicon | 41 |
| make | pakai | override | 39 |
| sampe | sampai | lexicon | 38 |
| animasinya | animasi | nya | 33 |
| kyk | kayak | lexicon | 32 |
| bgt | banget | lexicon | 32 |
| tu | itu | lexicon | 31 |
| tetep | tetap | lexicon | 31 |
| kayaknya | kayak | nya | 31 |
| hasilnya | hasil | nya | 29 |
| bg | bang | lexicon | 29 |
| org | orang | lexicon | 27 |
| tp | tapi | lexicon | 27 |
| minta | meminta | lexicon | 27 |
| njir | anjir | lexicon | 26 |
| jg | juga | lexicon | 26 |

## Kata terbanyak setelah stopword

| # | A | B |
|---|---|---|
| 1 | ai (1553) | ai (1558) |
| 2 | iklan (454) | pakai (686) |
| 3 | pake (441) | iklan (498) |
| 4 | animator (297) | animator (308) |
| 5 | pemerintah (292) | pemerintah (297) |
| 6 | animasi (258) | animasi (292) |
| 7 | bikin (257) | orang (271) |
| 8 | orang (211) | bikin (264) |
| 9 | indonesia (190) | banget (193) |
| 10 | pakai (179) | indonesia (190) |
| 11 | bagus (141) | bagus (151) |
| 12 | banget (136) | video (143) |
| 13 | video (128) | lokal (125) |
| 14 | lokal (124) | gambar (124) |
| 15 | gambar (106) | lihat (113) |
| 16 | polisi (106) | anak (107) |
| 17 | anak (92) | polisi (107) |
| 18 | manusia (86) | anggaran (95) |
| 19 | indo (85) | kerja (93) |
| 20 | komdigi (85) | manusia (90) |
| 21 | kerja (84) | negara (90) |
| 22 | negara (84) | komdigi (87) |
| 23 | anggaran (79) | indo (85) |
| 24 | mie (78) | mie (83) |
| 25 | liat (76) | karya (78) |
| 26 | karya (71) | hasil (78) |
| 27 | mending (69) | jelek (72) |
| 28 | marjan (68) | suka (70) |
| 29 | suka (67) | mending (70) |
| 30 | indomie (66) | marjan (68) |

## Contoh sebelum/sesudah

| asli | text_embed | text_repr_a | text_repr_b |
|---|---|---|---|
| Aq klo liat polisi d pinggir jalan jengkel banget, cuman selfie aja lapor atasan trs plg....😢 | Aq klo liat polisi d pinggir jalan jengkel banget, cuman selfie aja lapor atasan trs plg...😢 | aq klo liat polisi pinggir jalan jengkel banget cuman selfie aja lapor atasan trs plg | aku kalau lihat polisi pinggir jalan jengkel banget cuman selfie saja lapor atasan terus pulang |
| Udah muak sama iklan AI, jadi jelek kualitas iklan sekarang kareana ada AI 🥲 | Udah muak sama iklan AI, jadi jelek kualitas iklan sekarang kareana ada AI 🥲 | udah muak sama iklan ai jadi jelek kualitas iklan sekarang kareana ada ai | sudah muak sama iklan ai jadi jelek kualitas iklan sekarang kareana ada ai |
| Katanya cintailah produk lokal  tapi pemerintah kok pakai AI | Katanya cintailah produk lokal tapi pemerintah kok pakai AI | katanya cintailah produk lokal tapi pemerintah kok pakai ai | katanya cintailah produk lokal tapi pemerintah kok pakai ai |
| Malu malu in pakai AI😂 | Malu malu in pakai AI😂 | malu malu in pakai ai | malu malu in pakai ai |
| Please udah stop ane udah muak 😡😡😡 | Please udah stop ane udah muak 😡😡😡 | please udah stop ane udah muak | please sudah stop ane sudah muak |
| Udah 7 hari, aman kah? | Udah 7 hari, aman kah? | udah hari aman kah | sudah hari aman kah |
| Coba tu si Youtuber Anjas Maradita yg dia main AI skrg, jgn2 dia yg bikin 😅 | Coba tu si Youtuber Anjas Maradita yg dia main AI skrg, jgn-jgn dia yg bikin 😅 | coba tu si youtuber anjas maradita yg dia main ai skrg jgn-jgn dia yg bikin | coba itu si youtuber anjas maradita yang dia main ai sekarang jangan dia yang bikin |
| Adzan   Tapi sudah ceria dan bahagia iku yak gan 1thn | Adzan Tapi sudah ceria dan bahagia iku yak gan 1thn | adzan tapi sudah ceria dan bahagia iku yak gan thn | adzan tapi sudah ceria dan bahagia iku ya gan tahun |
| Wajar, karena namanya juga pemerintah dan masyarakat IQ 78. Pemerintah itu organisasi yg pasti dilirik oleh seluruh individu dalam suatu negara, termasuk diliri | Wajar, karena namanya juga pemerintah dan masyarakat IQ 78. Pemerintah itu organisasi yg pasti dilirik oleh seluruh individu dalam suatu negara, termasuk diliri | wajar karena namanya juga pemerintah dan masyarakat iq pemerintah itu organisasi yg pasti dilirik oleh seluruh individu  | wajar karena nama juga pemerintah dan masyarakat iq pemerintah itu organisasi yang pasti dilirik oleh seluruh individu d |
| soalnya buat efisiensi. Kalo pake AI bisa gratis, kalo pake animator perlu bayar. "Mending duitnya dikorup". Pake AI bisa 1 hari jadi. Bayar animator? 2 tahun b | soalnya buat efisiensi. Kalo pake AI bisa gratis, kalo pake animator perlu bayar. "Mending duitnya dikorup". Pake AI bisa 1 hari jadi. Bayar animator? 2 tahun b | soalnya buat efisiensi kalo pake ai bisa gratis kalo pake animator perlu bayar mending duitnya dikorup pake ai bisa hari | soalnya buat efisiensi kalau pakai ai bisa gratis kalau pakai animator perlu bayar mending duit dikorup pakai ai bisa ha |
| Emang sih harus hemat anggaran | Emang sih harus hemat anggaran | emang sih harus hemat anggaran | memang sih harus hemat anggaran |
| 🗣️Boomers:"Gen Z ini kerja milih milih, dah gitu maunya yang Instan pula"  Sementara itu Boomers dengan Ai | 🗣️Boomers:"Gen Z ini kerja milih milih, dah gitu maunya yang Instan pula" Sementara itu Boomers dengan Ai | boomers gen ini kerja milih milih dah gitu maunya yang instan pula sementara itu boomers dengan ai | boomers gen ini kerja memilih memilih deh begitu mau yang instan pula sementara itu boomers dengan ai |
| ​@user Dan banyak detail yang jelek, kayak ada tangan nyambung sama rambut juga wkwkwk | Dan banyak detail yang jelek, kayak ada tangan nyambung sama rambut juga wkwk | dan banyak detail yang jelek kayak ada tangan nyambung sama rambut juga wkwk | dan banyak detail yang jelek kayak ada tangan menyambung sama rambut juga wkwk |
| budget 2M tiap bulan/project .... spil tipis aja ya dari awal pertama kali mau ember cuma ga berani lebih lagi, pernah dapat tawaran soalnya, nyesel ga nerima g | budget 2M tiap bulan/project ... spil tipis aja ya dari awal pertama kali mau ember cuma ga berani lebih lagi, pernah dapat tawaran soalnya, nyesel ga nerima ga | budget tiap bulan project spil tipis aja ya dari awal pertama kali mau ember cuma ga berani lebih lagi pernah dapat tawa | budget tiap bulan project spil tipis saja ya dari awal pertama kali mau ember cuma enggak berani lebih lagi pernah dapat |
| ​@@user kalo nulis itu ya dipikir dulu, sekarang bila sebuah hal baru yg km katakan trend itu dilakukan terus menerus akan menjadi sebuah kebiasaan dan hal yang | kalo nulis itu ya dipikir dulu, sekarang bila sebuah hal baru yg km katakan trend itu dilakukan terus menerus akan menjadi sebuah kebiasaan dan hal yang wajar d | kalo nulis itu ya dipikir dulu sekarang bila sebuah hal baru yg km katakan trend itu dilakukan terus menerus akan menjad | kalau menulis itu ya dipikir dulu sekarang bila sebuah hal baru yang kamu katakan trend itu dilakukan terus menerus akan |
| Droomp?? Maksudnya | Droomp?? Maksudnya | droomp maksudnya | droomp maksud |
