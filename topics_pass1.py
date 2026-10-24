"""
BERTopic putaran 1: mengelompokkan semua komentar yang lolos pemeriksaan kualitas
untuk memisahkan klaster yang relevan dengan kasus GenAI dari yang tidak.

Alur BERTopic: embedding (text_embed) -> UMAP -> HDBSCAN -> c-TF-IDF (text_repr_a/b).
Klaster hanya ditentukan oleh tiga langkah pertama, jadi varian A dan B memakai
klaster yang sama dan hanya berbeda pada kata penciri topik.

Mode:
  --grid   coba beberapa kombinasi parameter, catat metrik ke experiments/runs.csv
  --final  jalankan satu konfigurasi dan simpan output lengkap untuk ditinjau

Penggunaan:
  python topics_pass1.py --grid
  python topics_pass1.py --final --n-neighbors 15 --min-cluster-size 15 --variant b

Output --final (experiments/pass1_<data>_<run>/):
  doc_topics.csv        topik per komentar + konteks kasus
  topic_info.csv        ukuran, kata penciri A dan B, sebaran per kasus
  topic_review.md       contoh komentar per topik untuk pelabelan manual
  labels_template.csv   kolom label relevan / tidak relevan / campuran untuk diisi
  model/                model BERTopic (safetensors)
"""

from datetime import datetime, timezone
from importlib.metadata import version as package_version
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys
import time

import numpy as np
import pandas as pd

SCRIPT_VERSION = "1.0"
PROCESSED_DIR = Path("data/processed")
RESOURCES_DIR = Path("resources")
EXPERIMENTS_DIR = Path("experiments")
RUNS_CSV = EXPERIMENTS_DIR / "runs.csv"

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
RANDOM_STATE = 42

# Parameter tetap
UMAP_N_COMPONENTS = 5
UMAP_MIN_DIST = 0.0
HDBSCAN_MIN_SAMPLES = 5
NGRAM_RANGE = (1, 2)
MIN_DF = 2
TOP_N_WORDS = 10

# Grid
GRID_N_NEIGHBORS = [15, 30]
GRID_MIN_CLUSTER_SIZE = [10, 15, 25]
VARIANTS = {"a": "text_repr_a", "b": "text_repr_b"}

N_REPRESENTATIVE = 8
N_RANDOM = 4

# ---------------------------------------------------------------------------
# Data dan embedding
# ---------------------------------------------------------------------------


def load_data(data_version: str) -> tuple[pd.DataFrame, list[str]]:
    path = PROCESSED_DIR / f"comments_bertopic_{data_version}.csv"
    if not path.exists():
        print(f"ERROR: {path} tidak ditemukan. Jalankan preprocess_bertopic.py dulu.")
        sys.exit(1)
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={"commentId": str})
    for col in ["text_embed", "text_repr_a", "text_repr_b"]:
        df[col] = df[col].fillna("")
    stopwords = (RESOURCES_DIR / f"stopwords_bertopic_{data_version}.txt").read_text(encoding="utf-8").split()
    return df, stopwords


def load_or_compute_embeddings(texts: list[str], data_version: str) -> np.ndarray:
    """Embedding dihitung sekali dan disimpan; dihitung ulang jika teks berubah."""
    digest = hashlib.sha256("\n".join(texts).encode("utf-8")).hexdigest()
    npy = PROCESSED_DIR / f"embeddings_mpnet_{data_version}.npy"
    meta = npy.with_suffix(".json")
    if npy.exists() and meta.exists() and json.loads(meta.read_text())["sha256"] == digest:
        print(f"  Embedding dari cache: {npy}")
        return np.load(npy)

    from sentence_transformers import SentenceTransformer
    print(f"  Menghitung embedding untuk {len(texts)} komentar (CPU, beberapa menit)...")
    t0 = time.time()
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    np.save(npy, embeddings)
    meta.write_text(json.dumps({
        "model": EMBEDDING_MODEL, "max_seq_length": model.max_seq_length, "n": len(texts),
        "dim": int(embeddings.shape[1]), "sha256": digest,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": round(time.time() - t0, 1),
    }, indent=2))
    print(f"  Selesai dalam {time.time() - t0:.0f} detik, disimpan ke {npy}")
    return embeddings


def reduce_umap(embeddings: np.ndarray, n_neighbors: int) -> np.ndarray:
    from umap import UMAP
    umap_model = UMAP(n_neighbors=n_neighbors, n_components=UMAP_N_COMPONENTS,
                      min_dist=UMAP_MIN_DIST, metric="cosine", random_state=RANDOM_STATE)
    return umap_model.fit_transform(embeddings)


# ---------------------------------------------------------------------------
# BERTopic
# ---------------------------------------------------------------------------


def fit_topic_model(docs: list[str], reduced: np.ndarray, min_cluster_size: int, stopwords: list[str]):
    """UMAP sudah dihitung di luar; BERTopic menerima embedding tereduksi apa adanya."""
    from bertopic import BERTopic
    from bertopic.dimensionality import BaseDimensionalityReduction
    from bertopic.vectorizers import ClassTfidfTransformer
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer

    model = BERTopic(
        umap_model=BaseDimensionalityReduction(),
        hdbscan_model=HDBSCAN(min_cluster_size=min_cluster_size, min_samples=HDBSCAN_MIN_SAMPLES,
                              metric="euclidean", cluster_selection_method="eom", prediction_data=True),
        vectorizer_model=CountVectorizer(stop_words=stopwords, token_pattern=r"(?u)[^\s]+",
                                         ngram_range=NGRAM_RANGE, min_df=MIN_DF),
        ctfidf_model=ClassTfidfTransformer(reduce_frequent_words=True),
        top_n_words=TOP_N_WORDS,
        calculate_probabilities=False,
        verbose=False,
    )
    topics, probs = model.fit_transform(docs, embeddings=reduced)
    return model, np.array(topics), np.array(probs)


def topic_words(model, n: int = TOP_N_WORDS) -> dict[int, list[str]]:
    return {t: [w for w, _ in (model.get_topic(t) or [])][:n] for t in model.get_topics() if t != -1}


# ---------------------------------------------------------------------------
# Metrik
# ---------------------------------------------------------------------------


def topic_diversity(words: dict[int, list[str]]) -> float:
    """Proporsi kata unik di antara top-N kata semua topik (Dieng dkk., 2020)."""
    all_words = [w for ws in words.values() for w in ws]
    return round(len(set(all_words)) / len(all_words), 3) if all_words else 0.0


def coherence(words: dict[int, list[str]], docs: list[str], stopwords: set) -> tuple[float, float]:
    """c_v dan NPMI dari gensim, dihitung pada unigram (bigram dipecah)."""
    from gensim.corpora import Dictionary
    from gensim.models.coherencemodel import CoherenceModel

    texts = [[w for w in d.split() if w not in stopwords] for d in docs]
    dictionary = Dictionary(texts)
    topics = []
    for ws in words.values():
        unigrams = []
        for w in ws:
            for part in w.split():
                if part in dictionary.token2id and part not in unigrams:
                    unigrams.append(part)
        if len(unigrams) >= 2:
            topics.append(unigrams[:TOP_N_WORDS])
    if not topics:
        return float("nan"), float("nan")
    scores = []
    for measure in ["c_v", "c_npmi"]:
        cm = CoherenceModel(topics=topics, texts=texts, dictionary=dictionary,
                            coherence=measure, processes=1)
        scores.append(round(cm.get_coherence(), 4))
    return scores[0], scores[1]


def log_run(row: dict) -> None:
    EXPERIMENTS_DIR.mkdir(exist_ok=True)
    new_file = not RUNS_CSV.exists()
    with open(RUNS_CSV, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def run_row(stage: str, data_version: str, n_neighbors: int, mcs: int, variant: str,
            topics: np.ndarray, words: dict, docs: list[str], stopwords: set) -> dict:
    n_topics = len(words)
    outliers = float((topics == -1).mean() * 100)
    sizes = pd.Series(topics[topics != -1]).value_counts()
    c_v, npmi = coherence(words, docs, stopwords)
    return {
        "run_id": f"{stage}_{data_version}_nn{n_neighbors}_mcs{mcs}_{variant}",
        "executed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stage": stage,
        "dataset_version": f"comments_bertopic_{data_version}",
        "representation_variant": variant.upper(),
        "embedding_model": EMBEDDING_MODEL,
        "umap": f"n_neighbors={n_neighbors},n_components={UMAP_N_COMPONENTS},min_dist={UMAP_MIN_DIST},metric=cosine",
        "hdbscan": f"min_cluster_size={mcs},min_samples={HDBSCAN_MIN_SAMPLES},eom",
        "vectorizer": f"ngram={NGRAM_RANGE},min_df={MIN_DF},stopwords=stopwords_bertopic_{data_version}",
        "ctfidf": "reduce_frequent_words=True",
        "random_state": RANDOM_STATE,
        "n_docs": len(topics),
        "n_topics": n_topics,
        "outlier_pct": round(outliers, 1),
        "largest_topic_pct": round(sizes.max() / len(topics) * 100, 1) if len(sizes) else 0,
        "median_topic_size": int(sizes.median()) if len(sizes) else 0,
        "coherence_cv": c_v,
        "coherence_npmi": npmi,
        "topic_diversity": topic_diversity(words),
        "code": f"topics_pass1.py v{SCRIPT_VERSION}",
        "bertopic_version": package_version("bertopic"),
    }


# ---------------------------------------------------------------------------
# Mode grid
# ---------------------------------------------------------------------------


def run_grid(df: pd.DataFrame, stopwords: list[str], embeddings: np.ndarray, data_version: str) -> None:
    stopword_set = set(stopwords)
    rows = []
    for nn in GRID_N_NEIGHBORS:
        print(f"\n  UMAP n_neighbors={nn}...")
        reduced = reduce_umap(embeddings, nn)
        for mcs in GRID_MIN_CLUSTER_SIZE:
            for variant, column in VARIANTS.items():
                docs = df[column].tolist()
                model, topics, _ = fit_topic_model(docs, reduced, mcs, stopwords)
                row = run_row("pass1_grid", data_version, nn, mcs, variant,
                              topics, topic_words(model), docs, stopword_set)
                log_run(row)
                rows.append(row)
                print(f"    mcs={mcs:>2} {variant.upper()}: {row['n_topics']:>3} topik, outlier "
                      f"{row['outlier_pct']:>5}%, terbesar {row['largest_topic_pct']:>4}%, "
                      f"c_v {row['coherence_cv']}, npmi {row['coherence_npmi']}, div {row['topic_diversity']}")
    table = pd.DataFrame(rows)[["run_id", "n_topics", "outlier_pct", "largest_topic_pct", "median_topic_size",
                                "coherence_cv", "coherence_npmi", "topic_diversity"]]
    print("\n" + table.to_string(index=False))
    print(f"\nSemua run dicatat di {RUNS_CSV}")


# ---------------------------------------------------------------------------
# Mode final
# ---------------------------------------------------------------------------


def representative_rows(df: pd.DataFrame, topic: int, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    members = df[df["topic"] == topic].sort_values("topic_prob", ascending=False)
    top = members.head(N_REPRESENTATIVE)
    rest = members.iloc[N_REPRESENTATIVE:]
    random = rest.sample(min(N_RANDOM, len(rest)), random_state=int(rng.integers(1_000_000))) if len(rest) else rest
    return top, random


def run_final(df: pd.DataFrame, stopwords: list[str], embeddings: np.ndarray, data_version: str,
              nn: int, mcs: int, variant: str, overwrite: bool) -> None:
    out_dir = EXPERIMENTS_DIR / f"pass1_{data_version}_nn{nn}_mcs{mcs}_{variant}"
    if out_dir.exists() and not overwrite:
        print(f"ERROR: {out_dir} sudah ada. Gunakan --overwrite.")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)
    stopword_set = set(stopwords)

    print(f"\n  UMAP n_neighbors={nn}...")
    reduced = reduce_umap(embeddings, nn)
    docs = df[VARIANTS[variant]].tolist()
    model, topics, probs = fit_topic_model(docs, reduced, mcs, stopwords)
    words = topic_words(model)
    row = run_row("pass1_final", data_version, nn, mcs, variant, topics, words, docs, stopword_set)
    log_run(row)

    # Kata penciri varian lain pada klaster yang sama (untuk perbandingan A/B)
    other = "a" if variant == "b" else "b"
    other_model, other_topics, _ = fit_topic_model(df[VARIANTS[other]].tolist(), reduced, mcs, stopwords)
    if not np.array_equal(other_topics, topics):
        print("  PERINGATAN: klaster varian lain berbeda; kata pembanding mungkin tidak sebanding")
    other_words = topic_words(other_model)

    df = df.copy()
    df["topic"] = topics
    df["topic_prob"] = np.round(probs, 4)
    df[["commentId", "videoId", "case_id", "org_type", "video_type", "verification_status", "isReply",
        "likeCount", "topic", "topic_prob", "textOriginal", "text_embed"]].to_csv(
        out_dir / "doc_topics.csv", index=False, encoding="utf-8-sig")

    # Ringkasan topik + sebaran per kasus
    case_counts = pd.crosstab(df["topic"], df["case_id"])
    info_rows = []
    for t in sorted(df["topic"].unique()):
        n = int((df["topic"] == t).sum())
        cases = case_counts.loc[t]
        dominant = cases.idxmax()
        info_rows.append({
            "topic": t,
            "n": n,
            "pct": round(n / len(df) * 100, 1),
            f"words_{variant}": ", ".join(words.get(t, [])) if t != -1 else "(outlier)",
            f"words_{other}": ", ".join(other_words.get(t, [])) if t != -1 else "(outlier)",
            "dominant_case": dominant,
            "dominant_case_pct": round(cases.max() / n * 100, 1),
            **{c: int(cases.get(c, 0)) for c in sorted(case_counts.columns)},
        })
    info = pd.DataFrame(info_rows)
    info.to_csv(out_dir / "topic_info.csv", index=False, encoding="utf-8-sig")

    # Template label untuk tinjauan manual
    labels = info[["topic", "n", f"words_{variant}", "dominant_case", "dominant_case_pct"]].copy()
    labels["label"] = ""          # relevant / not_relevant / mixed
    labels["topic_name"] = ""
    labels["note"] = ""
    labels.to_csv(out_dir / "labels_template.csv", index=False, encoding="utf-8-sig")

    # Dokumen tinjauan
    rng = np.random.default_rng(RANDOM_STATE)
    L = [f"# Tinjauan topik BERTopic putaran 1 ({out_dir.name})\n"]
    L.append(f"- {len(df)} komentar, {len(words)} topik, outlier {row['outlier_pct']}%")
    L.append(f"- c_v {row['coherence_cv']}, NPMI {row['coherence_npmi']}, diversity {row['topic_diversity']}")
    L.append(f"- Kata penciri utama: varian {variant.upper()}; pembanding: varian {other.upper()}")
    L.append("- Contoh 'representatif' = keanggotaan HDBSCAN tertinggi; 'acak' = sampel acak anggota lain.")
    L.append("- Isi `labels_template.csv`: label = relevant / not_relevant / mixed.\n")
    for r in info_rows:
        t = r["topic"]
        top, random = representative_rows(df, t, rng)
        title = "OUTLIER (-1)" if t == -1 else f"Topik {t}"
        L.append(f"## {title}: {r['n']} komentar ({r['pct']}%)\n")
        if t != -1:
            L.append(f"- Kata {variant.upper()}: {r[f'words_{variant}']}")
            L.append(f"- Kata {other.upper()}: {r[f'words_{other}']}")
        spread = ", ".join(f"{c} {r[c]}" for c in sorted(case_counts.columns) if r[c])
        L.append(f"- Sebaran kasus: {spread} (dominan {r['dominant_case']} {r['dominant_case_pct']}%)\n")
        for label, rows in [("Representatif", top), ("Acak", random)]:
            if len(rows):
                L.append(f"**{label}:**\n")
                for x in rows.itertuples():
                    text = str(x.text_embed).replace("\n", " ")[:220]
                    L.append(f"- [{x.case_id}] {text}")
                L.append("")
    (out_dir / "topic_review.md").write_text("\n".join(L), encoding="utf-8")

    model.save(str(out_dir / "model"), serialization="safetensors", save_ctfidf=True,
               save_embedding_model=EMBEDDING_MODEL)

    print(f"\n  {len(words)} topik, outlier {row['outlier_pct']}%, c_v {row['coherence_cv']}, "
          f"npmi {row['coherence_npmi']}, diversity {row['topic_diversity']}")
    print(f"  Output: {out_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BERTopic putaran 1 (relevansi).")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--grid", action="store_true")
    mode.add_argument("--final", action="store_true")
    parser.add_argument("--data-version", default="v1")
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--min-cluster-size", type=int, default=15)
    parser.add_argument("--variant", choices=["a", "b"], default="b")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=== BERTopic putaran 1 ===")
    df, stopwords = load_data(args.data_version)
    print(f"Input: {len(df)} komentar, {len(stopwords)} stopword")
    embeddings = load_or_compute_embeddings(df["text_embed"].tolist(), args.data_version)
    if args.grid:
        run_grid(df, stopwords, embeddings, args.data_version)
    else:
        run_final(df, stopwords, embeddings, args.data_version, args.n_neighbors,
                  args.min_cluster_size, args.variant, args.overwrite)


if __name__ == "__main__":
    main()
