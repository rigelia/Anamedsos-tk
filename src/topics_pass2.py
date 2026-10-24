"""
BERTopic putaran 2: mengelompokkan komentar yang berisi keberatan (sikap `tolak`)
menjadi kandidat tema keberatan (RQ1). Tema final ditetapkan lewat codebook manual.

Memakai ulang fungsi putaran 1 (embedding cache, UMAP, BERTopic, metrik, log) supaya
kedua putaran sebanding. Embedding diambil dari cache korpus penuh (baris yang sama),
tidak dihitung ulang.

Mode:
  --grid   coba beberapa kombinasi parameter, catat metrik ke experiments/runs.csv
  --final  jalankan satu konfigurasi dan simpan output lengkap untuk ditinjau

Penggunaan:
  python src/topics_pass2.py --grid
  python src/topics_pass2.py --final --n-neighbors 15 --min-cluster-size 10 --variant a

Output --final (experiments/pass2_<data>_<run>/):
  doc_topics.csv        topik per komentar + konteks kasus, org type, video type
  topic_info.csv        ukuran, kata penciri A dan B, sebaran per kasus / org type / video type
  topic_review.md       contoh komentar per topik (dengan komentar induk) untuk penamaan tema
  themes_template.csv   kolom nama tema / catatan untuk diisi
  model/                model BERTopic (safetensors)
"""

from pathlib import Path
import argparse
import sys

import numpy as np
import pandas as pd

import topics_pass1 as p1

SCRIPT_VERSION = "1.0"
STANCE_FILE = Path("experiments/stance_v1/sikap_final_v2.csv")
STANCE_INPUT = Path("experiments/stance_v1/stance_input.csv")
STANCE_LABEL = "tolak"

# Korpus lebih kecil (~1.600 komentar) daripada putaran 1, jadi grid digeser ke klaster lebih kecil
GRID_N_NEIGHBORS = [10, 15, 30]
GRID_MIN_CLUSTER_SIZE = [8, 10, 15, 20]


def load_subset(data_version: str) -> tuple[pd.DataFrame, list[str], np.ndarray]:
    df, stopwords = p1.load_data(data_version)
    embeddings = p1.load_or_compute_embeddings(df["text_embed"].tolist(), data_version)
    stance = pd.read_csv(STANCE_FILE, dtype={"commentId": str})
    keep = set(stance.loc[stance["sikap"] == STANCE_LABEL, "commentId"])
    mask = df["commentId"].isin(keep).to_numpy()
    if mask.sum() != len(keep):
        print(f"ERROR: {len(keep)} komentar {STANCE_LABEL}, tetapi hanya {mask.sum()} ditemukan di korpus.")
        sys.exit(1)
    sub = df[mask].reset_index(drop=True)
    # Komentar induk dan judul video, untuk membaca balasan pendek saat meninjau topik
    ctx = pd.read_csv(STANCE_INPUT, dtype={"commentId": str})[["commentId", "title", "parent_text"]]
    sub = sub.merge(ctx, on="commentId", how="left")
    assert len(sub) == mask.sum()
    return sub, stopwords, embeddings[mask]


def tag_row(row: dict, data_version: str) -> dict:
    row["dataset_version"] = f"comments_bertopic_{data_version}[sikap=={STANCE_LABEL},{STANCE_FILE.name}]"
    row["code"] = f"topics_pass2.py v{SCRIPT_VERSION}"
    return row


def run_grid(df: pd.DataFrame, stopwords: list[str], embeddings: np.ndarray, data_version: str) -> None:
    stopword_set = set(stopwords)
    rows = []
    for nn in GRID_N_NEIGHBORS:
        print(f"\n  UMAP n_neighbors={nn}...")
        reduced = p1.reduce_umap(embeddings, nn)
        for mcs in GRID_MIN_CLUSTER_SIZE:
            for variant, column in p1.VARIANTS.items():
                docs = df[column].tolist()
                model, topics, _ = p1.fit_topic_model(docs, reduced, mcs, stopwords)
                row = tag_row(p1.run_row("pass2_grid", data_version, nn, mcs, variant,
                                         topics, p1.topic_words(model), docs, stopword_set), data_version)
                p1.log_run(row)
                rows.append(row)
                print(f"    mcs={mcs:>2} {variant.upper()}: {row['n_topics']:>3} topik, outlier "
                      f"{row['outlier_pct']:>5}%, terbesar {row['largest_topic_pct']:>4}%, "
                      f"c_v {row['coherence_cv']}, npmi {row['coherence_npmi']}, div {row['topic_diversity']}")
    table = pd.DataFrame(rows)[["run_id", "n_topics", "outlier_pct", "largest_topic_pct", "median_topic_size",
                                "coherence_cv", "coherence_npmi", "topic_diversity"]]
    print("\n" + table.to_string(index=False))
    print(f"\nSemua run dicatat di {p1.RUNS_CSV}")


def run_final(df: pd.DataFrame, stopwords: list[str], embeddings: np.ndarray, data_version: str,
              nn: int, mcs: int, variant: str, overwrite: bool) -> None:
    out_dir = p1.EXPERIMENTS_DIR / f"pass2_{data_version}_nn{nn}_mcs{mcs}_{variant}"
    if out_dir.exists() and not overwrite:
        print(f"ERROR: {out_dir} sudah ada. Gunakan --overwrite.")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)
    stopword_set = set(stopwords)

    print(f"\n  UMAP n_neighbors={nn}...")
    reduced = p1.reduce_umap(embeddings, nn)
    docs = df[p1.VARIANTS[variant]].tolist()
    model, topics, probs = p1.fit_topic_model(docs, reduced, mcs, stopwords)
    words = p1.topic_words(model)
    row = tag_row(p1.run_row("pass2_final", data_version, nn, mcs, variant, topics, words, docs, stopword_set),
                  data_version)
    p1.log_run(row)

    other = "a" if variant == "b" else "b"
    other_model, other_topics, _ = p1.fit_topic_model(df[p1.VARIANTS[other]].tolist(), reduced, mcs, stopwords)
    if not np.array_equal(other_topics, topics):
        print("  PERINGATAN: klaster varian lain berbeda; kata pembanding mungkin tidak sebanding")
    other_words = p1.topic_words(other_model)

    df = df.copy()
    df["topic"] = topics
    df["topic_prob"] = np.round(probs, 4)
    df[["commentId", "videoId", "case_id", "org_type", "video_type", "verification_status", "isReply",
        "likeCount", "topic", "topic_prob", "textOriginal", "text_embed"]].to_csv(
        out_dir / "doc_topics.csv", index=False, encoding="utf-8-sig")

    case_counts = pd.crosstab(df["topic"], df["case_id"])
    org_counts = pd.crosstab(df["topic"], df["org_type"])
    vt_counts = pd.crosstab(df["topic"], df["video_type"])
    info_rows = []
    for t in sorted(df["topic"].unique()):
        n = int((df["topic"] == t).sum())
        cases = case_counts.loc[t]
        info_rows.append({
            "topic": t,
            "n": n,
            "pct": round(n / len(df) * 100, 1),
            f"words_{variant}": ", ".join(words.get(t, [])) if t != -1 else "(outlier)",
            f"words_{other}": ", ".join(other_words.get(t, [])) if t != -1 else "(outlier)",
            "dominant_case": cases.idxmax(),
            "dominant_case_pct": round(cases.max() / n * 100, 1),
            "n_cases": int((cases > 0).sum()),
            **{c: int(cases.get(c, 0)) for c in sorted(case_counts.columns)},
            **{o: int(org_counts.loc[t].get(o, 0)) for o in sorted(org_counts.columns)},
            **{v: int(vt_counts.loc[t].get(v, 0)) for v in sorted(vt_counts.columns)},
        })
    info = pd.DataFrame(info_rows)
    info.to_csv(out_dir / "topic_info.csv", index=False, encoding="utf-8-sig")

    themes = info[["topic", "n", f"words_{variant}", "dominant_case", "dominant_case_pct", "n_cases"]].copy()
    themes["theme_name"] = ""      # nama kandidat tema keberatan
    themes["merge_with"] = ""      # topik lain dengan tema yang sama
    themes["note"] = ""
    themes.to_csv(out_dir / "themes_template.csv", index=False, encoding="utf-8-sig")

    rng = np.random.default_rng(p1.RANDOM_STATE)
    L = [f"# Tinjauan topik BERTopic putaran 2: keberatan ({out_dir.name})\n"]
    L.append(f"- {len(df)} komentar `{STANCE_LABEL}`, {len(words)} topik, outlier {row['outlier_pct']}%")
    L.append(f"- c_v {row['coherence_cv']}, NPMI {row['coherence_npmi']}, diversity {row['topic_diversity']}")
    L.append(f"- Kata penciri utama: varian {variant.upper()}; pembanding: varian {other.upper()}")
    L.append("- Contoh 'representatif' = keanggotaan HDBSCAN tertinggi; 'acak' = sampel acak anggota lain.")
    L.append("- Balasan ditampilkan dengan komentar induknya (↳).\n")
    for r in info_rows:
        t = r["topic"]
        top, random = p1.representative_rows(df, t, rng)
        title = "OUTLIER (-1)" if t == -1 else f"Topik {t}"
        L.append(f"## {title}: {r['n']} komentar ({r['pct']}%)\n")
        if t != -1:
            L.append(f"- Kata {variant.upper()}: {r[f'words_{variant}']}")
            L.append(f"- Kata {other.upper()}: {r[f'words_{other}']}")
        spread = ", ".join(f"{c} {r[c]}" for c in sorted(case_counts.columns) if r[c])
        L.append(f"- Sebaran kasus: {spread} (dominan {r['dominant_case']} {r['dominant_case_pct']}%)")
        L.append(f"- Pemerintah {r.get('government', 0)} / komersial {r.get('commercial', 0)}; "
                 f"reupload {r.get('reupload_archive', 0)} / third_party {r.get('third_party', 0)}\n")
        for label, rows in [("Representatif", top), ("Acak", random)]:
            if len(rows):
                L.append(f"**{label}:**\n")
                for x in rows.itertuples():
                    text = str(x.text_embed).replace("\n", " ")[:220]
                    L.append(f"- [{x.case_id}] {text}")
                    if x.isReply and isinstance(x.parent_text, str):
                        L.append(f"  - ↳ induk: {x.parent_text.replace(chr(10), ' ')[:140]}")
                L.append("")
    (out_dir / "topic_review.md").write_text("\n".join(L), encoding="utf-8")

    model.save(str(out_dir / "model"), serialization="safetensors", save_ctfidf=True,
               save_embedding_model=p1.EMBEDDING_MODEL)

    print(f"\n  {len(words)} topik, outlier {row['outlier_pct']}%, c_v {row['coherence_cv']}, "
          f"npmi {row['coherence_npmi']}, diversity {row['topic_diversity']}")
    print(f"  Output: {out_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BERTopic putaran 2 (tema keberatan).")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--grid", action="store_true")
    mode.add_argument("--final", action="store_true")
    parser.add_argument("--data-version", default="v1")
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--min-cluster-size", type=int, default=10)
    parser.add_argument("--variant", choices=["a", "b"], default="a")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=== BERTopic putaran 2 ===")
    df, stopwords, embeddings = load_subset(args.data_version)
    print(f"Input: {len(df)} komentar {STANCE_LABEL}, {len(stopwords)} stopword")
    if args.grid:
        run_grid(df, stopwords, embeddings, args.data_version)
    else:
        run_final(df, stopwords, embeddings, args.data_version, args.n_neighbors,
                  args.min_cluster_size, args.variant, args.overwrite)


if __name__ == "__main__":
    main()
