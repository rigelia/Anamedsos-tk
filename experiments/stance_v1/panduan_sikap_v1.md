# Panduan Label Sikap (stance) v1

**Tujuan:** dari 2.288 komentar relevan (`data/processed/comments_relevance_v1.csv`, `relevant == y`), pilih komentar yang berisi **keberatan terhadap penggunaan GenAI oleh organisasi**. Komentar `tolak` dibawa ke BERTopic pass 2 (RQ1).

Yang diukur adalah **sikap**, bukan nada. Komentar sarkas bernada "positif" bisa `tolak`; komentar bernada kesal bisa `dukung`.

## Unit dan konteks

- Satu baris = satu komentar. Baca bersama **kasus/video** (organisasi apa, iklan apa) dan **komentar induk** kalau komentar itu balasan.
- Semua komentar di sini sudah dinyatakan relevan. Jangan menilai ulang relevansinya; cukup tentukan sikapnya.

## Tiga label

| Label | Definisi | Contoh dari data |
|---|---|---|
| `tolak` | Mengkritik, menolak, mengejek, atau keberatan terhadap **penggunaan AI oleh organisasi ini** atau **hasil visualnya**. Termasuk sarkas, keberatan bersyarat ("boleh, tapi jangan untuk ini"), dan saran "seharusnya pakai animator". | "Sedih banget, seharusnya mereka harus hargain animator lokal:(" · "Tangannya nyambung wkwk ngeri" · "Beli robot POLISI ANJING mampu masak bayar animator gak mampu" · "Kreatif sekali" |
| `dukung` | Membela, menerima, atau memaklumi penggunaan AI oleh organisasi ini, **atau** membantah/menyerang para pengkritiknya. | "Berarti iklan nya sukses. Viral kan, ez" · "cepet dan murah" · "ini sudah cukup baguss menurutku,,berjaunglah" · "KEMANA ELU SAAT BURUH DIGANTI MESIN? KOK KAGAK KOAR-KOAR?" |
| `lain` | Relevan, tetapi sikap terhadap penggunaan AI **tidak jelas**: pertanyaan, info, koreksi teknis, candaan tanpa sasaran jelas, atau kritik yang sasarannya bukan penggunaan AI. | "Ai?" · "Ini namanya veo 3 ai bang" · "Di rtv juga ada iklan ramadhan pakai AI 😅" · "Gua sih gk peduli sama iklan nya yg penting produknya memuaskan" |

## Urutan memutuskan

1. **Apa sasaran komentarnya?** Penggunaan AI / hasil visual AI / keputusan organisasi memakai AI → lanjut ke 2. Sasaran lain (kinerja polisi, politik, pengkritik lain di kolom komentar, produk) → biasanya `lain`, kecuali aturan 4 berlaku.
2. **Arah sikapnya?** Menolak/mengkritik → `tolak`. Membela/menerima → `dukung`.
3. **Tidak bisa dipastikan** dari teks, komentar induk dan video → `lain`. (Sama dengan aturan relevansi: kalau tidak jelas, jangan dipaksakan.)

## Aturan kasus sulit

1. **Sarkas dibaca maksudnya, bukan kata-katanya.** "Kreatif sekali", "Salut! Pemerintah berhasil membuktikan…", "Komdigi telah sukses mengebom 2 kali industri Animasi Indonesia" → `tolak`.
2. **Ejekan pada hasil AI** (tertawa, "jelek banget anj😂", "Creepyy", "Absolute ass") → `tolak`, walaupun tanpa alasan. Ejekan ini nanti dikelompokkan di pass 2, misalnya sebagai "ejekan tanpa alasan".
3. **Mengutip atau memparodikan kalimat narasi iklan** ("Ini jahat sekali 🗿", "InI jAhAt SeKaLi🤓👆") tanpa menyinggung AI atau visualnya → `lain`. Yang diejek pesannya, bukan penggunaan AI. *(Perlu dikonfirmasi tim.)*
4. **Kritik umum ke pemerintah/organisasi**: `tolak` hanya kalau dikaitkan dengan penggunaan AI ini, misalnya lewat anggaran ("Pakai AI biar uang sisanya untuk jajan"), korupsi ("tinggal bayar pake duit hasil korupsi" sebagai jawaban kenapa pakai AI), atau ketidakmampuan ("pemerintah iklan aja gk bisa"). Tanpa kaitan itu → `lain` ("pemerente mah dari awal gak pernah peduli dgn rakyat").
5. **Sindiran "ganti pejabat dengan AI"** ("Itu para pejabat pemerintah ganti aja sama ai") → `lain`. Sasarannya pejabat, bukan penggunaan AI dalam iklan.
6. **Keberatan bersyarat** ("AI itu buat draft awal, bukan hasil akhir", "boleh tapi … mereka membuatnya 100% AI", "minimal di-polish") → `tolak`, karena yang dikritik adalah penggunaan kali ini.
7. **Penerimaan bersyarat yang membela** ("mau dibuat pakai AI atau engga, kalau maknanya jelas respons masyarakat ga akan…") → `dukung`.
8. **Membandingkan dengan karya manusia** ("kalah sama Marjan", "liatin iklan marjan, film jumbo bagus tanpa AI") → `tolak`.
9. **Info bahwa organisasi lain juga memakai AI** ("shopee juga iklannya pakai AI 😂") → `lain`, kecuali jelas dipakai untuk membela (`dukung`) atau mengejek (`tolak`).
10. **Menyerang pengkritik / "AI itu masa depan"** sebagai bantahan ke penolak → `dukung`. Prediksi netral ("AI akan menggantikan manusia") tanpa membela atau menolak → `lain`.
11. **Ketakutan tanpa sasaran** ("ngeri", "Please udah stop ane udah muak 😡") → `tolak` hanya kalau jelas tertuju pada visual atau penggunaan AI dari konteks video. Kalau tidak jelas → `lain`.
12. **Keberatan dan pembelaan dalam satu komentar** → ambil sikap terhadap **penggunaan kali ini**. "AI bagus, tapi untuk iklan publik jangan" → `tolak`.
13. **Ketidakpedulian** ("gk peduli sama iklannya, yang penting produknya") → `lain`.
14. **Debat AI secara umum di kolom komentar** (hak cipta AI art, nasib seniman, "AI itu masa depan") dihitung sebagai sikap terhadap kasus ini, karena terjadi dalam konteks videonya. Argumen menolak AI art → `tolak`; argumen membela → `dukung`. Saling hina antarkomentator tanpa argumen → `lain`.
15. **Isi iklan vs kenyataan (C04)**: kritik bahwa iklan tidak sesuai kinerja polisi tanpa menyinggung AI atau visualnya ("kerja aja yang bener, gak usah pencitraan") → `lain`. Kalau menyinggung AI, sayap/visual aneh, atau "pencitraan pakai AI" → `tolak`.
16. **Kebijakan AI pemerintah yang dikaitkan dengan iklan** (lomba prompt AI, wapres juri lomba AI, "pakai AI bukan inovasi") → `tolak`.
17. **Alasan netral kenapa organisasi memakai AI** ("ya murah & cepet", "kena efisiensi anggaran") → `lain`; kalau jelas sindiran ("efisiensi katanya 😅", "biar sisa anggaran bisa ditilep") → `tolak`; kalau membenarkan ("emang sih harus hemat anggaran") → `dukung`.

## Validasi

- 100 komentar acak (seed tetap), dilabeli manusia **tanpa melihat label model**.
- Target κ ≥ 0,6. Kalau di bawahnya, cari pola ketidaksepakatan, perbaiki panduan ini (v2), lalu putuskan ketidaksepakatan.
- Perubahan aturan setelah validasi dicatat di bagian "Riwayat" di bawah.

## Riwayat

- v1 (2026-10-23): draf awal oleh Claude dari pembacaan 120 komentar acak. Aturan 3 menunggu konfirmasi tim.
- v1.1 (2026-10-23): aturan 14–17 ditambahkan selama Claude memberi label 2.288 komentar, untuk kasus yang sering muncul. Ditambahkan **sebelum** validasi manusia dimulai, jadi validator memakai versi ini.
