"""
Quality gate untuk korpus komentar (Modul 5: Social Media Data Quality).

Alur:
  1. Validasi record-level  -> jika gagal, proses berhenti (data tidak ditulis).
  2. Validasi dataset-level -> dilaporkan sebagai PERINGATAN.
  3. Flagging per komentar  -> masalah ditandai di kolom flag_*, tidak dihapus.
  4. Override manual        -> keputusan reviewer dari quality_overrides.csv.
  5. Kolom `eligible`       -> komentar yang lolos semua flag eksklusi.
  6. Laporan                -> ringkasan validasi, funnel eksklusi, keseimbangan korpus.

Input : data/<tanggal>/comments.csv, videos.csv, collection_log.json (tidak diubah)
Output (data/interim/):
  comments_quality_<versi>.csv   semua komentar + kolom flag + eligible
  review_quality_<versi>.csv     komentar yang perlu dicek manual
  quality_report_<versi>.md      laporan untuk tim / bagian metodologi
  quality_report_<versi>.json    laporan yang sama dalam bentuk terstruktur

Penggunaan:
  python src/quality_check.py
  python src/quality_check.py --raw-dir data/20260930 --version v1 --overwrite
"""

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import sys
import unicodedata

import pandas as pd
import regex as re

SCRIPT_VERSION = "1.0"

DEFAULT_RAW_DIR = "data/20260930"
INTERIM_DIR = Path("data/interim")
MANIFEST_CSV = "config/videos_manifest.csv"
OVERRIDES_CSV = "config/quality_overrides.csv"

# ---------------------------------------------------------------------------
# Aturan (semua parameter ada di sini agar mudah dilaporkan)
# ---------------------------------------------------------------------------

# Komentar dengan kata lebih sedikit dari ini ditandai flag_short (informasi saja,
# tidak mengeksklusi). Bahasa juga tidak dideteksi di bawah ambang ini.
MIN_WORDS = 3

# Deteksi bahasa: bahasa yang dipertimbangkan detektor. Melayu digabung dengan
# Indonesia karena keduanya tidak bisa dibedakan dengan andal pada teks pendek.
INDONESIAN_THRESHOLD = 0.5   # confidence(Indonesia + Melayu) minimal untuk label "id"
FOREIGN_THRESHOLD = 0.5      # confidence bahasa lain minimal untuk label non-Indonesia

# Kata fungsi / slang Indonesia: jika ada, komentar yang terdeteksi bahasa lain
# dianggap code-mixing dan tetap dipertahankan.
INDONESIAN_MARKERS = {
    "yang", "yg", "dan", "di", "ke", "dari", "ini", "itu", "tidak", "gak", "ga", "nggak",
    "enggak", "gk", "aja", "saja", "udah", "udh", "sudah", "banget", "bgt", "sih", "kok",
    "dong", "nya", "gw", "gue", "gua", "lu", "lo", "kalo", "kalau", "pake", "pakai",
    "bikin", "buat", "juga", "jg", "bang", "mah", "kan", "tapi", "tp", "karena", "krn",
    "iklan", "pemerintah", "anjir", "jir", "emang", "emg", "kayak", "kek",
    "iya", "makin", "deket", "bagi", "lagi", "mau", "apa", "ada", "jadi", "sama", "bisa",
    "harus", "dah", "deh", "lah", "nih", "tuh", "gimana", "kenapa", "knp", "banh", "bg",
    "lebih", "orang", "kita", "aku", "anjay", "cuy", "dgn", "mending", "mnding", "doang",
    "pas", "gitu", "gini",
}
LAUGHTER = re.compile(r"^(wk)+w?$")  # wkwk, wkwkwk, ...

# Spam judi online / promosi. STRONG: satu kata cukup. WEAK: butuh >= 2 kata.
SPAM_STRONG = re.compile(
    r"\b(gacor|maxwin|slot|togel|toto\w*|scatter|jackpot|rtp)\b|\bdepo(sit)?\s*\d",
    re.IGNORECASE,
)
SPAM_WEAK = re.compile(
    r"\b(wd|jp|hoki|pola|situs|cuan|bonus|rezeki|modal\s*\d+\w*)\b",
    re.IGNORECASE,
)
# Angka dalam lingkaran (❶❻❽, ①②) dipakai untuk menyamarkan nama situs judi
ENCLOSED_DIGITS = re.compile(r"[①-⓿❶-➓]")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
SELF_PROMO = re.compile(
    r"(upload video baru|mampir ke channel|cek channel|subscribe channel (aku|gw|gue|saya))",
    re.IGNORECASE,
)

MENTION_TOKEN = re.compile(r"@user\b")
VIDEO_TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(:\d{2})?\b")
ZERO_WIDTH = re.compile(r"[​-‏⁠﻿]")
# Kata harus diawali huruf; \p{M} saja (mis. variation selector U+FE0F pada emoji) bukan kata
WORD = re.compile(r"\p{L}[\p{L}\p{M}]*(?:[-'][\p{L}\p{M}]+)*")

# Flag yang mengeksklusi komentar dari analisis, dalam urutan funnel laporan
EXCLUSION_FLAGS = [
    ("flag_owner", "Komentar pemilik channel"),
    ("flag_no_content", "Tanpa isi teks (kosong / emoji / simbol / timestamp saja)"),
    ("flag_spam", "Spam (judi online / promosi / link)"),
    ("flag_same_author_repeat", "Teks sama berulang dari penulis yang sama (setelah yang pertama)"),
    ("flag_non_indonesian", "Bukan bahasa Indonesia"),
]
OVERRIDABLE_FIELDS = {flag for flag, _ in EXCLUSION_FLAGS} | {"lang"}

# ---------------------------------------------------------------------------
# Helpers teks
# ---------------------------------------------------------------------------


def normalize_text(text: str) -> str:
    """NFKC (huruf fancy 𝐁𝐓𝐕 -> BTV), hapus karakter zero-width, rapikan spasi."""
    text = unicodedata.normalize("NFKC", text)
    text = ZERO_WIDTH.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def content_text(text: str) -> str:
    """Teks tanpa @user, URL, dan timestamp video; dipakai untuk menghitung kata dan bahasa."""
    text = MENTION_TOKEN.sub(" ", text)
    text = URL_PATTERN.sub(" ", text)
    text = VIDEO_TIMESTAMP.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def duplicate_key(text: str) -> str:
    """Kunci pembanding untuk teks berulang: huruf kecil, hanya kata."""
    return " ".join(WORD.findall(content_text(text).casefold()))


def spam_reason(raw_text: str, text: str) -> str:
    reasons = []
    if SPAM_STRONG.search(text):
        reasons.append("judi_strong")
    # Hitung kata weak yang berbeda: "situs², situs-situs" tetap satu kata
    weak_terms = {m.group(1).casefold().split()[0] for m in SPAM_WEAK.finditer(text)}
    if len(weak_terms) >= 2:
        reasons.append("judi_weak_x2")
    if ENCLOSED_DIGITS.search(raw_text):
        reasons.append("angka_samaran")
    if URL_PATTERN.search(text):
        reasons.append("url")
    if SELF_PROMO.search(text):
        reasons.append("promosi_diri")
    return ";".join(reasons)


# ---------------------------------------------------------------------------
# Deteksi bahasa
# ---------------------------------------------------------------------------


def build_language_detector():
    try:
        from lingua import Language, LanguageDetectorBuilder
    except ImportError:
        print("ERROR: Library lingua belum terpasang. Jalankan: pip install lingua-language-detector")
        sys.exit(1)

    # Hanya bahasa yang masuk akal muncul di korpus. Dengan daftar yang lebih luas,
    # slang Indonesia sering tertebak Tagalog/Jerman/Belanda (dicek pada run v1 awal).
    languages = [
        Language.INDONESIAN, Language.MALAY, Language.ENGLISH, Language.ARABIC,
        Language.JAPANESE, Language.KOREAN, Language.CHINESE,
    ]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    return detector, Language


def has_indonesian_marker(words: list[str]) -> bool:
    """Kata fungsi/slang Indonesia, akhiran -nya, atau tawa 'wkwk'.

    Huruf berulang dipendekkan dulu ("Ituu" -> "itu", "aaku" -> "aku").
    """
    for word in words:
        w = word.casefold()
        squeezed = re.sub(r"(\p{L})\1+", r"\1", w)
        if w in INDONESIAN_MARKERS or squeezed in INDONESIAN_MARKERS:
            return True
        if len(w) > 4 and w.endswith("nya"):
            return True
        if LAUGHTER.match(w):
            return True
    return False


def detect_language(detector, Language, text: str, n_words: int, words: list[str]) -> tuple[str, float, str]:
    """Mengembalikan (label, confidence_indonesia, bahasa_teratas).

    Label: id, id_mixed (terdeteksi asing tetapi ada penanda Indonesia),
           non_id, uncertain, too_short.
    """
    if n_words < MIN_WORDS:
        # Terlalu pendek untuk detektor, tetapi aksara non-Latin pasti bukan Indonesia
        if n_words > 0 and not re.search(r"\p{Latin}", text):
            return "non_id", 0.0, "non_latin_script"
        return "too_short", float("nan"), ""

    confidences = {c.language: c.value for c in detector.compute_language_confidence_values(text)}
    p_indonesian = confidences.get(Language.INDONESIAN, 0.0) + confidences.get(Language.MALAY, 0.0)
    top_language, top_value = max(confidences.items(), key=lambda kv: kv[1])
    top_name = top_language.name.lower()

    if p_indonesian >= INDONESIAN_THRESHOLD:
        return "id", p_indonesian, top_name
    if has_indonesian_marker(words):
        return "id_mixed", p_indonesian, top_name
    if top_value >= FOREIGN_THRESHOLD:
        return "non_id", p_indonesian, top_name
    return "uncertain", p_indonesian, top_name


# ---------------------------------------------------------------------------
# Validasi
# ---------------------------------------------------------------------------


def check(results: list, level: str, rule: str, n_fail: int, total: int, hard: bool) -> None:
    status = "PASS" if n_fail == 0 else ("FAIL" if hard else "WARN")
    results.append({"level": level, "rule": rule, "n_fail": int(n_fail), "total": int(total), "status": status})


def validate_records(df: pd.DataFrame, manifest: pd.DataFrame) -> list[dict]:
    r = []
    n = len(df)
    check(r, "record", "commentId tidak kosong", df["commentId"].isna().sum(), n, True)
    check(r, "record", "commentId unik", df["commentId"].duplicated().sum(), n, True)
    check(r, "record", "videoId ada di manifest", (~df["videoId"].isin(manifest["video_id"])).sum(), n, True)
    check(r, "record", "textOriginal tidak null", df["textOriginal"].isna().sum(), n, True)
    check(r, "record", "likeCount >= 0 dan numerik", (pd.to_numeric(df["likeCount"], errors="coerce").fillna(-1) < 0).sum(), n, True)
    check(r, "record", "publishedAt timestamp valid", df["publishedAt_dt"].isna().sum(), n, True)
    check(r, "record", "updatedAt timestamp valid", df["updatedAt_dt"].isna().sum(), n, True)
    check(r, "record", "authorHash tidak kosong", df["authorHash"].isna().sum(), n, False)
    is_reply = df["isReply"]
    has_parent = df["parentId"].notna()
    check(r, "record", "isReply konsisten dengan parentId", (is_reply != has_parent).sum(), n, True)
    return r


def validate_dataset(df: pd.DataFrame, videos: pd.DataFrame, log: dict, manifest: pd.DataFrame) -> list[dict]:
    r = []
    n = len(df)
    replies = df[df["isReply"]]

    orphan = ~replies["parentId"].isin(df.loc[~df["isReply"], "commentId"])
    check(r, "dataset", "setiap reply punya parent di data", orphan.sum(), len(replies), False)

    # Jumlah reply per thread vs totalReplyCount milik parent
    reply_counts = replies.groupby("parentId").size()
    parents = df[~df["isReply"]].set_index("commentId")["totalReplyCount"]
    mismatch = (parents - reply_counts.reindex(parents.index).fillna(0)).ne(0).sum()
    check(r, "dataset", "jumlah reply per thread = totalReplyCount", mismatch, len(parents), False)

    # Jumlah baris per video vs log koleksi dan statistik video
    logged = {v["video_id"]: v.get("fetched_total") for v in log["videos"]}
    rows_per_video = df.groupby("videoId").size()
    n_bad_log = sum(rows_per_video.get(vid, 0) != cnt for vid, cnt in logged.items())
    check(r, "dataset", "jumlah baris per video = collection_log", n_bad_log, len(logged), False)
    stats = videos.set_index("video_id")["comment_count"]
    n_bad_stats = sum(rows_per_video.get(vid, 0) != cnt for vid, cnt in stats.items())
    check(r, "dataset", "jumlah baris per video = commentCount YouTube", n_bad_stats, len(stats), False)

    # Konsistensi waktu
    video_published = pd.to_datetime(df["videoId"].map(videos.set_index("video_id")["published_at"]), utc=True)
    retrieved = pd.to_datetime(df["retrievedAt"], utc=True)
    check(r, "dataset", "komentar tidak lebih awal dari upload video", (df["publishedAt_dt"] < video_published).sum(), n, False)
    check(r, "dataset", "komentar tidak lebih baru dari waktu pengambilan", (df["publishedAt_dt"] > retrieved).sum(), n, False)
    check(r, "dataset", "updatedAt >= publishedAt", (df["updatedAt_dt"] < df["publishedAt_dt"]).sum(), n, False)

    # Kolom kasus konsisten dengan manifest saat ini
    m = manifest.set_index("video_id")
    case_cols = ["case_id", "organization", "org_type", "video_type", "verification_status"]
    inconsistent = sum((df[c] != df["videoId"].map(m[c])).sum() for c in case_cols)
    check(r, "dataset", "kolom kasus sama dengan manifest", inconsistent, n, False)
    return r


# ---------------------------------------------------------------------------
# Flagging
# ---------------------------------------------------------------------------


def add_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["text_normalized"] = df["textOriginal"].fillna("").map(normalize_text)
    df["text_content"] = df["text_normalized"].map(content_text)
    words = df["text_content"].map(WORD.findall)
    df["n_words"] = words.map(len)

    df["flag_owner"] = df["isVideoOwner"].astype(bool)
    df["flag_no_content"] = df["n_words"] == 0
    df["flag_short"] = df["n_words"] < MIN_WORDS
    df["flag_edited"] = df["updatedAt_dt"] != df["publishedAt_dt"]

    df["spam_reason"] = [spam_reason(raw, norm) for raw, norm in zip(df["textOriginal"].fillna(""), df["text_normalized"])]
    df["flag_spam"] = df["spam_reason"] != ""

    # Duplikat: teks sama dari penulis yang sama -> tandai semua kecuali yang pertama.
    # Teks sama dari penulis berbeda = konten berulang yang sah, hanya dicatat.
    df["dup_key"] = df["text_normalized"].map(duplicate_key)
    has_key = df["dup_key"] != ""
    ordered = df.sort_values("publishedAt_dt")
    repeat = ordered[has_key.loc[ordered.index]].duplicated(subset=["authorHash", "dup_key"], keep="first")
    df["flag_same_author_repeat"] = False
    df.loc[repeat[repeat].index, "flag_same_author_repeat"] = True
    df["n_authors_same_text"] = df.groupby("dup_key")["authorHash"].transform("nunique").where(has_key, 0)

    df["author_n_comments"] = df.groupby("authorHash")["commentId"].transform("size")

    print("  Mendeteksi bahasa...")
    detector, Language = build_language_detector()
    detected = [detect_language(detector, Language, text, n, w)
                for text, n, w in zip(df["text_content"], df["n_words"], words)]
    df["lang"] = [d[0] for d in detected]
    df["lang_conf_id"] = [round(d[1], 3) for d in detected]
    df["lang_top"] = [d[2] for d in detected]
    df["flag_non_indonesian"] = df["lang"] == "non_id"
    df["flag_lang_uncertain"] = df["lang"] == "uncertain"

    return df.drop(columns=["dup_key"])


def apply_overrides(df: pd.DataFrame, path: Path) -> tuple[pd.DataFrame, list[dict]]:
    """Menerapkan keputusan reviewer: commentId, field, value, reviewer, reason."""
    if not path.exists():
        return df, []
    overrides = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
    applied = []
    for _, o in overrides.iterrows():
        if o["field"] not in OVERRIDABLE_FIELDS:
            print(f"  PERINGATAN: override field '{o['field']}' tidak dikenal, dilewati")
            continue
        mask = df["commentId"] == o["commentId"]
        if not mask.any():
            print(f"  PERINGATAN: override commentId {o['commentId']} tidak ditemukan, dilewati")
            continue
        if o["field"] == "lang":
            df.loc[mask, "lang"] = o["value"]
            df.loc[mask, "flag_non_indonesian"] = o["value"] == "non_id"
            df.loc[mask, "flag_lang_uncertain"] = o["value"] == "uncertain"
        else:
            df.loc[mask, o["field"]] = o["value"].strip().lower() in {"true", "1", "yes"}
        applied.append(o.to_dict())
    return df, applied


# ---------------------------------------------------------------------------
# Laporan
# ---------------------------------------------------------------------------


def build_funnel(df: pd.DataFrame) -> list[dict]:
    remaining = pd.Series(True, index=df.index)
    funnel = [{"step": "Total komentar", "removed": 0, "remaining": int(remaining.sum())}]
    for flag, label in EXCLUSION_FLAGS:
        removed = remaining & df[flag]
        remaining &= ~df[flag]
        funnel.append({"step": label, "flag": flag, "removed": int(removed.sum()), "remaining": int(remaining.sum())})
    return funnel


def balance_table(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    t = df.groupby(by).agg(total=("commentId", "size"), eligible=("eligible", "sum"))
    t["pct_eligible"] = (t["eligible"] / t["total"] * 100).round(1)
    t["share_of_eligible"] = (t["eligible"] / t["eligible"].sum() * 100).round(1)
    return t.reset_index()


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def build_review(df: pd.DataFrame) -> pd.DataFrame:
    """Komentar yang keputusannya perlu dicek manusia."""
    reasons = {
        "spam": df["flag_spam"],
        "non_indonesian": df["flag_non_indonesian"],
        "lang_uncertain": df["flag_lang_uncertain"],
        "id_mixed": df["lang"] == "id_mixed",
        "same_author_repeat": df["flag_same_author_repeat"],
    }
    parts = []
    for reason, mask in reasons.items():
        part = df[mask].copy()
        part.insert(0, "review_reason", reason)
        parts.append(part)
    review = pd.concat(parts)[[
        "review_reason", "commentId", "case_id", "videoId", "isReply", "textOriginal",
        "spam_reason", "lang", "lang_top", "lang_conf_id", "n_words",
    ]]
    review["reviewer_decision"] = ""
    review["reviewer_note"] = ""
    return review


def write_report_md(path: Path, meta: dict, validation: list, funnel: list, flags: dict,
                    balances: dict, research: dict, overrides: list) -> None:
    L = []
    L.append(f"# Laporan kualitas data ({meta['version']})\n")
    L.append(f"- Dibuat: {meta['created_at_utc']} (quality_check.py v{meta['script_version']})")
    L.append(f"- Input: `{meta['input']}` (koleksi {meta['collection_started_utc']})")
    L.append(f"- Output: `{meta['output']}`")
    L.append(f"- Parameter: MIN_WORDS={MIN_WORDS}, INDONESIAN_THRESHOLD={INDONESIAN_THRESHOLD}, "
             f"FOREIGN_THRESHOLD={FOREIGN_THRESHOLD}, detektor bahasa lingua {meta['lingua_version']}")
    L.append(f"- Override manual diterapkan: {len(overrides)}\n")

    L.append("## 1. Validasi\n")
    L.append("FAIL pada level record menghentikan proses; WARN dilaporkan dan perlu dijelaskan.\n")
    L.append(md_table(pd.DataFrame(validation)) + "\n")

    L.append("## 2. Funnel eksklusi\n")
    L.append("Flag diterapkan berurutan; `removed` = komentar yang baru tereksklusi pada langkah itu.\n")
    L.append(md_table(pd.DataFrame(funnel).drop(columns=["flag"], errors="ignore")) + "\n")

    L.append("## 3. Jumlah per flag (tidak berurutan, satu komentar bisa punya beberapa flag)\n")
    L.append(md_table(pd.DataFrame([{"flag": k, "n": v} for k, v in flags.items()])) + "\n")

    L.append("## 4. Keseimbangan korpus (level riset)\n")
    for title, table in balances.items():
        L.append(f"### {title}\n")
        L.append(md_table(table) + "\n")

    L.append("## 5. Catatan level riset\n")
    for k, v in research.items():
        L.append(f"- {k}: {v}")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quality gate untuk korpus komentar YouTube.")
    parser.add_argument("--raw-dir", default=DEFAULT_RAW_DIR)
    parser.add_argument("--version", default="v1", help="Label versi output, mis. v1, v2")
    parser.add_argument("--overrides", default=OVERRIDES_CSV, help="File keputusan review manual")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    out_csv = INTERIM_DIR / f"comments_quality_{args.version}.csv"
    if out_csv.exists() and not args.overwrite:
        print(f"ERROR: {out_csv} sudah ada. Gunakan --version baru atau --overwrite.")
        sys.exit(1)

    print("=== Quality gate ===")
    df = pd.read_csv(raw_dir / "comments.csv", encoding="utf-8-sig",
                     dtype={"commentId": str, "parentId": str, "authorHash": str})
    videos = pd.read_csv(raw_dir / "videos.csv", encoding="utf-8-sig")
    log = json.loads((raw_dir / "collection_log.json").read_text(encoding="utf-8"))
    manifest = pd.read_csv(MANIFEST_CSV, encoding="utf-8-sig", dtype=str)
    print(f"Input: {len(df)} komentar dari {df['videoId'].nunique()} video ({raw_dir})")

    for col in ["isReply", "isVideoOwner"]:
        df[col] = df[col].astype(str).str.lower().eq("true")
    df["publishedAt_dt"] = pd.to_datetime(df["publishedAt"], utc=True, errors="coerce")
    df["updatedAt_dt"] = pd.to_datetime(df["updatedAt"], utc=True, errors="coerce")

    # 1-2. Validasi
    print("\n[1/4] Validasi...")
    validation = validate_records(df, manifest)
    for v in validation:
        print(f"  {v['status']:<4}  {v['rule']} ({v['n_fail']})")
    if any(v["status"] == "FAIL" for v in validation):
        print("Validasi record-level GAGAL; tidak ada output yang ditulis. Perbaiki data koleksi dulu.")
        sys.exit(1)
    dataset_checks = validate_dataset(df, videos, log, manifest)
    for v in dataset_checks:
        print(f"  {v['status']:<4}  {v['rule']} ({v['n_fail']})")
    validation += dataset_checks

    # 3-4. Flag dan override
    print("\n[2/4] Flagging...")
    df = add_flags(df)
    df, overrides = apply_overrides(df, Path(args.overrides))
    if overrides:
        print(f"  {len(overrides)} override manual diterapkan dari {args.overrides}")

    # 5. Eligible
    df["eligible"] = ~df[[flag for flag, _ in EXCLUSION_FLAGS]].any(axis=1)

    # 6. Output
    print("\n[3/4] Menyimpan output...")
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    out = df.drop(columns=["publishedAt_dt", "updatedAt_dt"])
    out.to_csv(out_csv, index=False, encoding="utf-8-sig")
    review_csv = INTERIM_DIR / f"review_quality_{args.version}.csv"
    build_review(df).to_csv(review_csv, index=False, encoding="utf-8-sig")

    funnel = build_funnel(df)
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    flag_counts = {c: int(df[c].sum()) for c in flag_cols}
    lang_counts = df["lang"].value_counts().to_dict()
    balances = {
        "Per tipe organisasi": balance_table(df, ["org_type"]),
        "Per tipe video": balance_table(df, ["video_type"]),
        "Per kasus": balance_table(df, ["case_id", "org_type", "video_type", "verification_status"]),
    }
    eligible = df[df["eligible"]]
    author_counts = eligible["authorHash"].value_counts()
    top_n = max(1, int(len(author_counts) * 0.01))
    research = {
        "Komentar eligible": f"{len(eligible)} dari {len(df)} ({len(eligible) / len(df) * 100:.1f}%)",
        "Penulis unik (eligible)": len(author_counts),
        "Konsentrasi penulis": f"1% penulis teratas ({top_n}) menulis "
                               f"{author_counts.head(top_n).sum() / len(eligible) * 100:.1f}% komentar eligible; "
                               f"maksimum {author_counts.max()} komentar per penulis",
        "Label bahasa (semua komentar)": lang_counts,
        "Komentar pendek (< MIN_WORDS) di antara eligible": int(eligible["flag_short"].sum()),
        "Teks sama dari >1 penulis (konten berulang sah, dipertahankan)": int((eligible["n_authors_same_text"] > 1).sum()),
        "Rentang waktu komentar": f"{df['publishedAt_dt'].min():%Y-%m-%d} s.d. {df['publishedAt_dt'].max():%Y-%m-%d}",
        "Catatan": "Melayu digabung dengan Indonesia; bahasa daerah (Jawa, Sunda) tidak dideteksi terpisah. "
                   "Spam dan label bahasa perlu dicek manual lewat review file.",
    }

    from importlib.metadata import version
    meta = {
        "version": args.version,
        "script_version": SCRIPT_VERSION,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input": str(raw_dir / "comments.csv"),
        "collection_started_utc": log.get("started_at_utc"),
        "output": str(out_csv),
        "lingua_version": version("lingua-language-detector"),
    }
    write_report_md(INTERIM_DIR / f"quality_report_{args.version}.md", meta, validation, funnel,
                    flag_counts, balances, research, overrides)
    (INTERIM_DIR / f"quality_report_{args.version}.json").write_text(json.dumps({
        "meta": meta,
        "parameters": {"MIN_WORDS": MIN_WORDS, "INDONESIAN_THRESHOLD": INDONESIAN_THRESHOLD,
                       "FOREIGN_THRESHOLD": FOREIGN_THRESHOLD},
        "validation": validation,
        "funnel": funnel,
        "flag_counts": flag_counts,
        "balance": {k: v.to_dict(orient="records") for k, v in balances.items()},
        "research": research,
        "overrides_applied": overrides,
    }, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print("\n[4/4] Ringkasan")
    for step in funnel:
        print(f"  {step['step']:<70} -{step['removed']:>4}  -> {step['remaining']}")
    print(f"\nOutput: {out_csv}")
    print(f"        {review_csv}")
    print(f"        {INTERIM_DIR / f'quality_report_{args.version}.md'}")


if __name__ == "__main__":
    main()
