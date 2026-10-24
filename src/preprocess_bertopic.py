"""
Prapemrosesan teks untuk BERTopic (Modul 6: Social Media Data Preprocessing).

BERTopic punya dua komponen yang butuh teks berbeda:
  - embedding (pengelompokan) -> transformer multilingual: pembersihan MINIMAL
    agar konteks, negasi, slang, dan emoji tetap terbaca model   -> text_embed
  - representasi topik (c-TF-IDF) -> hitungan kata: pembersihan tradisional
    (huruf kecil, tanpa emoji/tanda baca, normalisasi slang)     -> text_repr_a / text_repr_b

Stopword TIDAK dihapus dari teks; daftar stopword disimpan terpisah dan
dipakai di CountVectorizer pada tahap BERTopic.

Dua varian representasi dibandingkan sebagai variabel eksperimen:
  A (text_repr_a): huruf kecil, tanpa emoji/tanda baca/angka, huruf berulang dipendekkan
  B (text_repr_b): A + normalisasi slang (kamus + koreksi manual)
                     + reduplikasi penuh (orang-orang -> orang)
                     + pelepasan akhiran -nya bila kata dasarnya ada di korpus

Input : data/interim/comments_quality_<qv>.csv (hanya baris eligible)
Output:
  data/processed/comments_bertopic_<v>.csv     teks siap BERTopic + kolom konteks
  data/processed/preprocess_report_<v>.md      statistik dan contoh sebelum/sesudah
  data/processed/preprocess_config_<v>.json    parameter, sumber, versi
  resources/stopwords_bertopic_<v>.txt         daftar stopword untuk CountVectorizer

Penggunaan:
  python src/preprocess_bertopic.py
  python src/preprocess_bertopic.py --quality-version v2 --version v2
"""

from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version as package_version
from pathlib import Path
import argparse
import json
import sys
import unicodedata

import pandas as pd
import regex as re

SCRIPT_VERSION = "1.0"

INTERIM_DIR = Path("data/interim")
PROCESSED_DIR = Path("data/processed")
RESOURCES_DIR = Path("resources")

LEXICON_CSV = RESOURCES_DIR / "colloquial-indonesian-lexicon.csv"
OVERRIDES_CSV = RESOURCES_DIR / "slang_overrides.csv"
STOPWORDS_ID_TXT = RESOURCES_DIR / "stopwords-id.txt"

SOURCES = {
    "stopwords-id.txt": {
        "name": "stopwords-iso Indonesian",
        "url": "https://github.com/stopwords-iso/stopwords-id",
        "retrieved": "2026-09-30",
    },
    "colloquial-indonesian-lexicon.csv": {
        "name": "Colloquial Indonesian Lexicon (Salsabila et al., 2018, IALP)",
        "url": "https://github.com/nasalsabila/kamus-alay",
        "retrieved": "2026-09-30",
    },
}

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EXAMPLE_SEED = 42
N_EXAMPLES = 12

# ---------------------------------------------------------------------------
# Aturan teks
# ---------------------------------------------------------------------------

ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION = re.compile(r"@+user\b")   # juga "@@user" pada balasan berantai
LEADING_USER = re.compile(r"^(\s*\[USER\][\s,:]*)+")
VIDEO_TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(:\d{2})?\b")
A_DOT_I = re.compile(r"\bA\.I\b\.?", re.IGNORECASE)

# Reduplikasi gaya media sosial: "situs²" dan "anak2" -> "situs-situs", "anak-anak"
SUPERSCRIPT_REDUP = re.compile(r"(\p{L}{2,})²")
DIGIT_REDUP = re.compile(r"\b(\p{L}{3,})2\b")

LAUGHTER_WK = re.compile(r"(?i)\b(wk){3,}w?\b")
LAUGHTER_HA = re.compile(r"(?i)\b(ha){3,}h?\b")
LAUGHTER_HE = re.compile(r"(?i)\b(he){3,}h?\b")
LETTER_RUN_3 = re.compile(r"(\p{L})\1{2,}")          # huruf sama >= 3 kali
OTHER_RUN_4 = re.compile(r"([^\p{L}\p{N}\s])\1{3,}")  # emoji/tanda baca sama >= 4 kali

# Token representasi: kata huruf, boleh bersambung tanda hubung (orang-orang)
REPR_TOKEN = re.compile(r"\p{L}[\p{L}\p{M}]*(?:-\p{L}[\p{L}\p{M}]*)*")

# Istilah yang tidak boleh berubah atau masuk stopword
PROTECTED_TERMS = {"ai", "genai", "mbg", "indo", "komdigi", "kominfo", "polri", "indomie", "rtv", "bni", "x"}

# Kata berakhiran -nya yang maknanya berubah jika akhirannya dilepas ("makanya" != "maka")
NYA_EXCEPTIONS = {"makanya", "katanya", "soalnya", "rasanya", "bukannya", "sebenarnya", "biasanya",
                  "akhirnya", "tadinya", "harusnya", "emangnya", "memangnya", "apalagi"}

# Kata di stopwords-iso yang dipertahankan karena bermakna untuk tema keberatan
KEEP_FROM_STOPWORDS = {"masalah", "penting", "kurang", "jelas", "rasa", "merasa"}

# Slang, sapaan, dan kata pengisi khas komentar YouTube (dalam bentuk slang dan formal)
CUSTOM_STOPWORDS = {
    "yg", "gak", "ga", "gk", "g", "nggak", "ngga", "ngak", "nga", "enggak", "engga", "kagak", "kaga",
    "aja", "aj", "ae", "udah", "udh", "uda", "sih", "si", "dong", "deh", "dah", "kok", "nih", "ni", "tuh",
    "tu", "nya", "lah", "la", "kan", "kn", "yah", "ya", "yaa", "iya", "oh", "eh", "loh", "lho", "mah",
    "gw", "gue", "gua", "w", "lu", "lo", "elu", "elo", "aku", "ku", "saya", "kamu", "kalian", "kita",
    "bang", "bg", "banh", "bro", "kak", "min", "mas", "mbak", "pak", "bapak", "om", "cuy", "coy",
    "jir", "njir", "anjir", "anjay", "wk", "wkwk", "haha", "hehe", "awok", "awokawok", "hmm", "hm",
    "kek", "kayak", "kaya", "kyk", "emang", "emg", "memang", "gitu", "gini", "begitu", "begini",
    "doang", "cuma", "cuman", "cmn", "tp", "tapi", "kalo", "klo", "kalau", "jg", "juga", "jd", "jadi",
    "dgn", "dg", "utk", "sm", "ama", "sama", "trus", "terus", "sampe", "sampai", "biar", "karna",
    "tau", "tahu", "bilang", "gimana", "bagaimana", "kenapa", "knp", "napa", "mana", "pas", "dll",
}

# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------


def load_lexicon() -> tuple[dict, dict]:
    """Kamus slang -> formal. Koreksi manual (slang_overrides.csv) diutamakan."""
    lexicon = pd.read_csv(LEXICON_CSV, dtype=str).dropna(subset=["slang", "formal"])
    lexicon["slang"] = lexicon["slang"].str.strip().str.lower()
    lexicon["formal"] = lexicon["formal"].str.strip().str.lower()
    # Slang dengan beberapa bentuk formal: ambil yang paling sering muncul di kamus
    mapping = (lexicon.groupby("slang")["formal"]
               .agg(lambda s: s.value_counts().index[0]).to_dict())
    overrides = pd.read_csv(OVERRIDES_CSV, dtype=str).fillna("")
    override_map = dict(zip(overrides["slang"].str.lower(), overrides["formal"].str.lower()))
    return mapping, override_map


def build_stopwords() -> tuple[list[str], dict]:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

    indonesian = set(STOPWORDS_ID_TXT.read_text(encoding="utf-8").split())
    english = set(ENGLISH_STOP_WORDS)
    combined = (indonesian | english | CUSTOM_STOPWORDS) - KEEP_FROM_STOPWORDS - PROTECTED_TERMS
    counts = {
        "stopwords_iso_id": len(indonesian),
        "sklearn_english": len(english),
        "custom_slang_filler": len(CUSTOM_STOPWORDS),
        "kept_meaningful": sorted(KEEP_FROM_STOPWORDS),
        "total": len(combined),
    }
    return sorted(combined), counts


# ---------------------------------------------------------------------------
# Teks embedding
# ---------------------------------------------------------------------------


def make_text_embed(text: str) -> str:
    """Pembersihan minimal: konteks, kapitalisasi, negasi, slang, dan emoji dipertahankan."""
    text = SUPERSCRIPT_REDUP.sub(r"\1-\1", text)       # sebelum NFKC (² -> 2)
    text = unicodedata.normalize("NFKC", text)           # huruf fancy 𝐁𝐓𝐕 -> BTV
    text = ZERO_WIDTH.sub("", text)
    text = DIGIT_REDUP.sub(r"\1-\1", text)
    text = URL_PATTERN.sub("[URL]", text)
    text = MENTION.sub("[USER]", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = LEADING_USER.sub("", text)                    # sapaan balasan di awal
    text = VIDEO_TIMESTAMP.sub("", text)
    text = A_DOT_I.sub("AI", text)
    text = LAUGHTER_WK.sub("wkwk", text)
    text = LAUGHTER_HA.sub("haha", text)
    text = LAUGHTER_HE.sub("hehe", text)
    text = LETTER_RUN_3.sub(r"\1\1", text)               # "bangettttt" -> "bangett"
    text = OTHER_RUN_4.sub(r"\1\1\1", text)              # "😂😂😂😂😂" -> "😂😂😂"
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Teks representasi
# ---------------------------------------------------------------------------


def repr_tokens(text_embed: str) -> list[str]:
    """Varian A: huruf kecil, hanya token kata, huruf berulang dipendekkan ke satu."""
    text = text_embed.replace("[USER]", " ").replace("[URL]", " ").casefold()
    tokens = []
    for token in REPR_TOKEN.findall(text):
        token = re.sub(r"(\p{L})\1{2,}", r"\1", token)   # "anjirrr" -> "anjir"
        if len(token) >= 2:
            tokens.append(token)
    return tokens


def normalize_token(token: str, lexicon: dict, overrides: dict, english: set) -> tuple[str, str]:
    """Mengembalikan (hasil, sumber) untuk satu token."""
    if token in overrides:
        return overrides[token], "override"
    if token in PROTECTED_TERMS or token in english:
        return token, ""
    return lexicon.get(token, token), "lexicon" if token in lexicon else ""


def reduce_reduplication(token: str) -> str:
    parts = token.split("-")
    if len(parts) == 2 and parts[0] == parts[1]:
        return parts[0]
    return token


def strip_nya(token: str, vocabulary: Counter, min_count: int) -> str:
    """'iklannya' -> 'iklan' jika 'iklan' sendiri muncul >= min_count kali di korpus."""
    if not token.endswith("nya") or len(token) <= 3 or token in NYA_EXCEPTIONS:
        return token
    base = token[:-3].rstrip("-")
    if (len(base) >= 3 or base in PROTECTED_TERMS) and vocabulary[base] >= min_count:
        return base
    return token


def make_repr_b(tokens: list[str], lexicon: dict, overrides: dict, english: set,
                vocabulary: Counter, nya_min_count: int, change_log: Counter) -> list[str]:
    result = []
    for token in tokens:
        token = reduce_reduplication(token)
        normalized, source = normalize_token(token, lexicon, overrides, english)
        if normalized != token:
            change_log[(token, normalized, source)] += 1
        for word in normalized.split():
            stripped = strip_nya(word, vocabulary, nya_min_count)
            if stripped != word:
                change_log[(word, stripped, "nya")] += 1
            result.append(stripped)
    return result


# ---------------------------------------------------------------------------
# Laporan
# ---------------------------------------------------------------------------


def token_lengths(texts: pd.Series):
    """Jumlah token subword model embedding; None jika tokenizer tidak tersedia offline."""
    try:
        import os
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
        tokenizer.model_max_length = 10**6   # hanya menghitung; hindari peringatan panjang
    except Exception as error:
        print(f"  PERINGATAN: tokenizer tidak bisa dimuat ({error}); cek truncation dilewati")
        return None
    return texts.map(lambda t: len(tokenizer(t, add_special_tokens=True)["input_ids"]))


def top_words(texts: pd.Series, stopwords: set, n: int = 30) -> list[tuple[str, int]]:
    counts = Counter(w for t in texts for w in t.split() if w not in stopwords)
    return counts.most_common(n)


def md_table(rows: list[dict]) -> str:
    if not rows:
        return "(kosong)"
    cols = list(rows[0].keys())
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in rows:
        lines.append("| " + " | ".join(str(row[c]).replace("|", "\\|").replace("\n", " ") for c in cols) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prapemrosesan teks untuk BERTopic.")
    parser.add_argument("--quality-version", default="v1", help="Versi output quality_check.py yang dipakai")
    parser.add_argument("--version", default="v1", help="Label versi output prapemrosesan")
    parser.add_argument("--nya-min-count", type=int, default=3,
                        help="Frekuensi minimal kata dasar agar akhiran -nya dilepas")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    in_csv = INTERIM_DIR / f"comments_quality_{args.quality_version}.csv"
    out_csv = PROCESSED_DIR / f"comments_bertopic_{args.version}.csv"
    stopwords_txt = RESOURCES_DIR / f"stopwords_bertopic_{args.version}.txt"
    if not in_csv.exists():
        print(f"ERROR: {in_csv} tidak ditemukan. Jalankan quality_check.py dulu.")
        sys.exit(1)
    if out_csv.exists() and not args.overwrite:
        print(f"ERROR: {out_csv} sudah ada. Gunakan --version baru atau --overwrite.")
        sys.exit(1)

    print("=== Prapemrosesan untuk BERTopic ===")
    df = pd.read_csv(in_csv, encoding="utf-8-sig", dtype={"commentId": str, "parentId": str})
    df = df[df["eligible"].astype(str).str.lower() == "true"].copy()
    print(f"Input: {len(df)} komentar eligible dari {in_csv}")

    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    english = set(ENGLISH_STOP_WORDS)
    lexicon, overrides = load_lexicon()
    stopwords, stopword_counts = build_stopwords()
    stopword_set = set(stopwords)

    print("[1/4] text_embed...")
    df["text_embed"] = df["textOriginal"].fillna("").map(make_text_embed)

    print("[2/4] text_repr_a...")
    tokens_a = df["text_embed"].map(repr_tokens)
    df["text_repr_a"] = tokens_a.map(" ".join)

    print("[3/4] text_repr_b...")
    # Kosakata untuk pelepasan -nya: token setelah reduplikasi dan normalisasi slang
    base_vocab = Counter()
    for tokens in tokens_a:
        for token in tokens:
            normalized, _ = normalize_token(reduce_reduplication(token), lexicon, overrides, english)
            base_vocab.update(normalized.split())
    change_log = Counter()
    df["text_repr_b"] = tokens_a.map(
        lambda t: " ".join(make_repr_b(t, lexicon, overrides, english, base_vocab,
                                       args.nya_min_count, change_log)))

    df["n_tokens_repr"] = df["text_repr_b"].str.split().str.len()
    df["n_content_tokens_repr"] = df["text_repr_b"].map(lambda t: sum(w not in stopword_set for w in t.split()))
    df["repr_no_content_words"] = df["n_content_tokens_repr"] == 0

    print("[4/4] Cek panjang token model embedding...")
    lengths = token_lengths(df["text_embed"])
    max_seq_length = 128
    if lengths is not None:
        df["n_model_tokens"] = lengths
        df["embed_truncated"] = lengths > max_seq_length

    # Output
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    keep = [
        "commentId", "videoId", "case_id", "organization", "org_type", "video_type",
        "verification_status", "isReply", "parentId", "likeCount", "publishedAt", "authorHash",
        "lang", "n_words", "flag_short", "textOriginal", "text_embed", "text_repr_a", "text_repr_b",
        "n_tokens_repr", "n_content_tokens_repr", "repr_no_content_words",
    ] + (["n_model_tokens", "embed_truncated"] if lengths is not None else [])
    df[keep].to_csv(out_csv, index=False, encoding="utf-8-sig")
    stopwords_txt.write_text("\n".join(stopwords) + "\n", encoding="utf-8")

    # Statistik
    vocab_a = Counter(w for t in df["text_repr_a"] for w in t.split())
    vocab_b = Counter(w for t in df["text_repr_b"] for w in t.split())
    content_a = {w for w in vocab_a if w not in stopword_set}
    content_b = {w for w in vocab_b if w not in stopword_set}
    changes = Counter()
    for (before, after, source), n in change_log.items():
        changes[source] += n
    top_changes = [{"sebelum": b, "sesudah": a, "sumber": s, "n": n}
                   for (b, a, s), n in change_log.most_common(40)]
    stats = {
        "komentar": len(df),
        "kosakata_A_semua": len(vocab_a),
        "kosakata_B_semua": len(vocab_b),
        "kosakata_A_tanpa_stopword": len(content_a),
        "kosakata_B_tanpa_stopword": len(content_b),
        "token_diubah_B": dict(changes),
        "komentar_tanpa_kata_isi_setelah_stopword": int(df["repr_no_content_words"].sum()),
        "rata2_token_repr": round(df["n_tokens_repr"].mean(), 1),
    }
    if lengths is not None:
        stats["model_max_seq_length"] = max_seq_length
        stats["komentar_terpotong_di_model"] = int(df["embed_truncated"].sum())
        stats["median_token_model"] = int(lengths.median())
        stats["p95_token_model"] = int(lengths.quantile(0.95))

    examples = df.sample(N_EXAMPLES, random_state=EXAMPLE_SEED)
    # Tambah contoh yang memperlihatkan aturan khusus bila ada
    for pattern in [r"@user", r"(?i)wkwk", r"²|\p{L}2\b", r"(?i)nya\b"]:
        matches = df["textOriginal"].fillna("").map(lambda t: bool(re.search(pattern, t)))
        hit = df[matches & ~df.index.isin(examples.index)]
        if not hit.empty:
            examples = pd.concat([examples, hit.sample(1, random_state=EXAMPLE_SEED)])
    example_rows = [{
        "asli": r.textOriginal[:160], "text_embed": r.text_embed[:160],
        "text_repr_a": r.text_repr_a[:120], "text_repr_b": r.text_repr_b[:120],
    } for r in examples.itertuples()]

    meta = {
        "version": args.version,
        "script_version": SCRIPT_VERSION,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input": str(in_csv),
        "output": str(out_csv),
        "stopwords_file": str(stopwords_txt),
        "embedding_model": EMBEDDING_MODEL,
        "libraries": {p: package_version(p) for p in ["pandas", "regex", "scikit-learn", "transformers"]},
    }
    config = {
        "meta": meta,
        "sources": SOURCES,
        "parameters": {
            "nya_min_count": args.nya_min_count,
            "protected_terms": sorted(PROTECTED_TERMS),
            "keep_from_stopwords": sorted(KEEP_FROM_STOPWORDS),
            "nya_exceptions": sorted(NYA_EXCEPTIONS),
            "n_slang_overrides": len(overrides),
            "n_lexicon_entries": len(lexicon),
            "example_seed": EXAMPLE_SEED,
        },
        "stopwords": stopword_counts,
        "bertopic_usage": {
            "embeddings": "text_embed",
            "representation_docs": "text_repr_a (pipeline A) atau text_repr_b (pipeline B)",
            "vectorizer": "CountVectorizer(stop_words=<stopwords file>, token_pattern=r'(?u)[^\\s]+', "
                          "min_df/max_df ditentukan di tahap BERTopic)",
            "note": "Dokumen embedding dan representasi harus berurutan sama (baris CSV yang sama).",
        },
        "stats": stats,
        "top_changes_B": top_changes,
    }
    (PROCESSED_DIR / f"preprocess_config_{args.version}.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    L = [f"# Laporan prapemrosesan BERTopic ({args.version})\n"]
    L.append(f"- Dibuat: {meta['created_at_utc']} (preprocess_bertopic.py v{SCRIPT_VERSION})")
    L.append(f"- Input: `{in_csv}` ({len(df)} komentar eligible)")
    L.append(f"- Output: `{out_csv}`, stopword: `{stopwords_txt}`\n")
    L.append("## Statistik\n")
    L.append(md_table([{"ukuran": k, "nilai": v} for k, v in stats.items()]) + "\n")
    L.append("## Stopword (dipakai di CountVectorizer, tidak dihapus dari teks)\n")
    L.append(md_table([{"komponen": k, "jumlah": v} for k, v in stopword_counts.items()]) + "\n")
    L.append("## Normalisasi terbanyak (varian B)\n")
    L.append(md_table(top_changes) + "\n")
    L.append("## Kata terbanyak setelah stopword\n")
    top_a, top_b = top_words(df["text_repr_a"], stopword_set), top_words(df["text_repr_b"], stopword_set)
    L.append(md_table([{"#": i + 1, "A": f"{a[0]} ({a[1]})", "B": f"{b[0]} ({b[1]})"}
                       for i, (a, b) in enumerate(zip(top_a, top_b))]) + "\n")
    L.append("## Contoh sebelum/sesudah\n")
    L.append(md_table(example_rows) + "\n")
    (PROCESSED_DIR / f"preprocess_report_{args.version}.md").write_text("\n".join(L), encoding="utf-8")

    print("\n=== Ringkasan ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\nOutput: {out_csv}")
    print(f"        {PROCESSED_DIR / f'preprocess_report_{args.version}.md'}")
    print(f"        {stopwords_txt}")


if __name__ == "__main__":
    main()
