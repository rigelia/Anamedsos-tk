# Laporan kualitas data (v1)

- Dibuat: 2026-09-30T04:11:54Z (quality_check.py v1.0)
- Input: `data\20260930\comments.csv` (koleksi 2026-09-30T02:13:43Z)
- Output: `data\interim\comments_quality_v1.csv`
- Parameter: MIN_WORDS=3, INDONESIAN_THRESHOLD=0.5, FOREIGN_THRESHOLD=0.5, detektor bahasa lingua 2.2.0
- Override manual diterapkan: 0

## 1. Validasi

FAIL pada level record menghentikan proses; WARN dilaporkan dan perlu dijelaskan.

| level | rule | n_fail | total | status |
|---|---|---|---|---|
| record | commentId tidak kosong | 0 | 3307 | PASS |
| record | commentId unik | 0 | 3307 | PASS |
| record | videoId ada di manifest | 0 | 3307 | PASS |
| record | textOriginal tidak null | 0 | 3307 | PASS |
| record | likeCount >= 0 dan numerik | 0 | 3307 | PASS |
| record | publishedAt timestamp valid | 0 | 3307 | PASS |
| record | updatedAt timestamp valid | 0 | 3307 | PASS |
| record | authorHash tidak kosong | 0 | 3307 | PASS |
| record | isReply konsisten dengan parentId | 0 | 3307 | PASS |
| dataset | setiap reply punya parent di data | 0 | 899 | PASS |
| dataset | jumlah reply per thread = totalReplyCount | 0 | 2408 | PASS |
| dataset | jumlah baris per video = collection_log | 0 | 8 | PASS |
| dataset | jumlah baris per video = commentCount YouTube | 0 | 8 | PASS |
| dataset | komentar tidak lebih awal dari upload video | 0 | 3307 | PASS |
| dataset | komentar tidak lebih baru dari waktu pengambilan | 0 | 3307 | PASS |
| dataset | updatedAt >= publishedAt | 0 | 3307 | PASS |
| dataset | kolom kasus sama dengan manifest | 0 | 3307 | PASS |

## 2. Funnel eksklusi

Flag diterapkan berurutan; `removed` = komentar yang baru tereksklusi pada langkah itu.

| step | removed | remaining |
|---|---|---|
| Total komentar | 0 | 3307 |
| Komentar pemilik channel | 42 | 3265 |
| Tanpa isi teks (kosong / emoji / simbol / timestamp saja) | 38 | 3227 |
| Spam (judi online / promosi / link) | 8 | 3219 |
| Teks sama berulang dari penulis yang sama (setelah yang pertama) | 14 | 3205 |
| Bukan bahasa Indonesia | 60 | 3145 |

## 3. Jumlah per flag (tidak berurutan, satu komentar bisa punya beberapa flag)

| flag | n |
|---|---|
| flag_owner | 42 |
| flag_no_content | 42 |
| flag_short | 398 |
| flag_edited | 302 |
| flag_spam | 10 |
| flag_same_author_repeat | 17 |
| flag_non_indonesian | 61 |
| flag_lang_uncertain | 0 |

## 4. Keseimbangan korpus (level riset)

### Per tipe organisasi

| org_type | total | eligible | pct_eligible | share_of_eligible |
|---|---|---|---|---|
| commercial | 899 | 856 | 95.2 | 27.2 |
| government | 2408 | 2289 | 95.1 | 72.8 |

### Per tipe video

| video_type | total | eligible | pct_eligible | share_of_eligible |
|---|---|---|---|---|
| reupload_archive | 982 | 924 | 94.1 | 29.4 |
| third_party | 2325 | 2221 | 95.5 | 70.6 |

### Per kasus

| case_id | org_type | video_type | verification_status | total | eligible | pct_eligible | share_of_eligible |
|---|---|---|---|---|---|---|---|
| C01 | commercial | third_party | credible_media | 647 | 630 | 97.4 | 20.0 |
| C02 | government | third_party | credible_media | 172 | 135 | 78.5 | 4.3 |
| C03 | government | reupload_archive | to_verify | 730 | 698 | 95.6 | 22.2 |
| C04 | government | third_party | to_verify | 553 | 538 | 97.3 | 17.1 |
| C05 | commercial | reupload_archive | to_verify | 127 | 111 | 87.4 | 3.5 |
| C06 | commercial | reupload_archive | to_verify | 125 | 115 | 92.0 | 3.7 |
| C07 | government | third_party | to_verify | 953 | 918 | 96.3 | 29.2 |

## 5. Catatan level riset

- Komentar eligible: 3145 dari 3307 (95.1%)
- Penulis unik (eligible): 2545
- Konsentrasi penulis: 1% penulis teratas (25) menulis 7.7% komentar eligible; maksimum 43 komentar per penulis
- Label bahasa (semua komentar): {'id': 2827, 'too_short': 397, 'non_id': 61, 'id_mixed': 22}
- Komentar pendek (< MIN_WORDS) di antara eligible: 334
- Teks sama dari >1 penulis (konten berulang sah, dipertahankan): 99
- Rentang waktu komentar: 2023-09-29 s.d. 2026-09-23
- Catatan: Melayu digabung dengan Indonesia; bahasa daerah (Jawa, Sunda) tidak dideteksi terpisah. Spam dan label bahasa perlu dicek manual lewat review file.
