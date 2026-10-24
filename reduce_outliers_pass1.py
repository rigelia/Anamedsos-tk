"""
BERTopic putaran 1, langkah lanjutan: memasukkan outlier (topik -1) ke topik terdekat,
lalu mewariskan label relevansi topik (labels_final.csv) ke setiap komentar.

Strategi: setara BERTopic reduce_outliers(strategy="embeddings"), tetapi dihitung di
ruang embedding asli (768 dimensi). Model pass 1 di-fit dengan embedding hasil UMAP,
jadi topic_embeddings_ yang tersimpan berdimensi 5 dan tidak bisa dibandingkan dengan
embedding komentar. Centroid topik = rata-rata embedding (dinormalisasi) anggota HDBSCAN.

Ambang: outlier hanya dipindahkan jika kemiripan kosinus ke centroid terdekat >= ambang.
Default 0.555 = persentil ke-5 kemiripan anggota asli ke centroid topiknya sendiri,
artinya outlier dipindahkan hanya jika sedekat 95% anggota asli.

Rute per komentar (kolom `route`):
  relevant          topik berlabel relevant
  check_comment     topik berlabel mixed, atau tetap outlier: perlu dicek per komentar
  excluded          topik berlabel not_relevant

Penggunaan:
  python reduce_outliers_pass1.py [--run pass1_v1_nn15_mcs15_a] [--threshold 0.555] [--overwrite]
"""

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import sys

import numpy as np
import pandas as pd

SCRIPT_VERSION = "1.0"
EXPERIMENTS_DIR = Path("experiments")
PROCESSED_DIR = Path("data/processed")
RANDOM_STATE = 42
N_SAMPLE = 15

ROUTE = {"relevant": "relevant", "mixed": "check_comment", "not_relevant": "excluded"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reduksi outlier pass 1 + warisan label relevansi.")
    parser.add_argument("--run", default="pass1_v1_nn15_mcs15_a")
    parser.add_argument("--data-version", default="v1")
    parser.add_argument("--threshold", type=float, default=None,
                        help="default: persentil ke-5 kemiripan anggota asli ke centroidnya")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    run_dir = EXPERIMENTS_DIR / args.run
    out_csv = run_dir / "doc_topics_reduced.csv"
    if out_csv.exists() and not args.overwrite:
        print(f"ERROR: {out_csv} sudah ada. Gunakan --overwrite.")
        sys.exit(1)

    docs = pd.read_csv(run_dir / "doc_topics.csv", encoding="utf-8-sig", dtype={"commentId": str})
    proc = pd.read_csv(PROCESSED_DIR / f"comments_bertopic_{args.data_version}.csv",
                       encoding="utf-8-sig", dtype={"commentId": str})
    if not (docs["commentId"].values == proc["commentId"].values).all():
        print("ERROR: urutan doc_topics.csv tidak sama dengan data embedding.")
        sys.exit(1)
    labels = pd.read_csv(run_dir / "labels_final.csv", encoding="utf-8-sig").set_index("topic")

    emb = np.load(PROCESSED_DIR / f"embeddings_mpnet_{args.data_version}.npy")
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    topics = docs["topic"].to_numpy()
    n_topics = topics.max() + 1
    centroids = np.stack([emb[topics == k].mean(axis=0) for k in range(n_topics)])
    centroids /= np.linalg.norm(centroids, axis=1, keepdims=True)
    sims = emb @ centroids.T

    members = topics != -1
    own_sim = sims[members][np.arange(members.sum()), topics[members]]
    threshold = args.threshold if args.threshold is not None else round(float(np.percentile(own_sim, 5)), 3)

    nearest = sims.argmax(axis=1)
    best = sims.max(axis=1)
    reassign = (~members) & (best >= threshold)

    out = docs.copy()
    out["topic_orig"] = topics
    out["topic"] = np.where(reassign, nearest, topics)
    out["assigned_by"] = np.select([members, reassign], ["hdbscan", "reduce_outliers"], "none")
    out["sim_to_topic"] = np.round(np.where(out["topic"] >= 0, sims[np.arange(len(out)), out["topic"].clip(0)], best), 4)
    out["topic_label"] = out["topic"].map(labels["label_final"])
    out["label_source"] = out["topic"].map(labels["source"])
    out["route"] = out["topic_label"].map(ROUTE).fillna("check_comment")
    cols = ["commentId", "videoId", "case_id", "org_type", "video_type", "verification_status", "isReply",
            "likeCount", "topic_orig", "topic", "assigned_by", "sim_to_topic", "topic_label", "label_source",
            "route", "textOriginal", "text_embed"]
    out[cols].to_csv(out_csv, index=False, encoding="utf-8-sig")

    # Ringkasan
    reduced = out[out["assigned_by"] == "reduce_outliers"]
    summary = {
        "script": f"reduce_outliers_pass1.py v{SCRIPT_VERSION}",
        "run": args.run,
        "executed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strategy": "cosine similarity to 768-d topic centroids (equivalent to reduce_outliers strategy='embeddings')",
        "threshold": threshold,
        "threshold_rule": "default = 5th percentile of member-to-own-centroid similarity" if args.threshold is None else "manual",
        "n_docs": len(out),
        "n_outliers_before": int((~members).sum()),
        "n_reassigned": int(reassign.sum()),
        "n_outliers_after": int((out["topic"] == -1).sum()),
        "reassigned_by_label": reduced["topic_label"].value_counts().to_dict(),
        "route_counts": out["route"].value_counts().to_dict(),
        "route_by_assigned_by": pd.crosstab(out["assigned_by"], out["route"]).to_dict(orient="index"),
        "route_by_case": pd.crosstab(out["case_id"], out["route"]).to_dict(orient="index"),
    }
    (run_dir / "reduce_outliers_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                                          encoding="utf-8")

    # Sampel untuk dicek manusia: outlier yang dipindah, per label warisan
    L = [f"# Cek sampel reduce_outliers ({args.run})\n",
         f"- Ambang kemiripan: {threshold}; {summary['n_reassigned']} dari {summary['n_outliers_before']} "
         f"outlier dipindahkan, {summary['n_outliers_after']} tetap outlier.",
         "- Untuk tiap komentar: apakah label warisan (relevant / not_relevant) cocok? "
         "Komentar mixed tidak perlu dicek di sini karena akan dicek per komentar.\n"]
    for lab in ["relevant", "not_relevant"]:
        part = reduced[reduced["topic_label"] == lab]
        sample = part.sample(min(N_SAMPLE, len(part)), random_state=RANDOM_STATE)
        L.append(f"## Diwarisi `{lab}` ({len(part)} komentar, sampel {len(sample)})\n")
        for x in sample.itertuples():
            text = str(x.text_embed).replace("\n", " ")[:200]
            L.append(f"- [{x.case_id}] (topik {x.topic}, sim {x.sim_to_topic:.2f}) {text}")
        L.append("")
    (run_dir / "reduce_outliers_check.md").write_text("\n".join(L), encoding="utf-8")

    print(f"  Ambang {threshold}: {summary['n_reassigned']} outlier dipindah, {summary['n_outliers_after']} tetap -1")
    print(f"  Label warisan: {summary['reassigned_by_label']}")
    print(f"  Rute: {summary['route_counts']}")
    print(f"  Output: {out_csv}, reduce_outliers_summary.json, reduce_outliers_check.md")


if __name__ == "__main__":
    main()
