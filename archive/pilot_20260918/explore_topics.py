"""
Eksplorasi awal topik pada komentar YouTube menggunakan BERTopic.

Input : comments_IXNas_31uvQ_20260918.csv
Output: topic_info_IXNas.csv, comments_with_topics_IXNas.csv, representative_docs_IXNas.txt
"""

import time
import pandas as pd
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic

# ---------------------------------------------------------------------------
# 1. Baca dan bersihkan data
# ---------------------------------------------------------------------------

INPUT_CSV = "comments_IXNas_31uvQ_20260918.csv"

df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
print(f"Jumlah baris awal: {len(df)}")

docs_raw = df["textOriginal"].copy()

mask_not_null = docs_raw.notna()
mask_not_empty = docs_raw.str.strip().ne("")
mask_min_len = docs_raw.str.len() >= 3

docs_clean = docs_raw[mask_not_null & mask_not_empty & mask_min_len]
before_dedup = len(docs_clean)
docs_clean = docs_clean.drop_duplicates()

print(f"Setelah buang null/kosong/< 3 karakter: {before_dedup}")
print(f"Setelah buang duplikat teks persis    : {len(docs_clean)}")
print()

df_clean = df.loc[docs_clean.index].copy()
documents = docs_clean.tolist()

# ---------------------------------------------------------------------------
# 2. Embedding (dihitung sekali, dipakai ulang untuk eksperimen parameter)
# ---------------------------------------------------------------------------

print("Memuat model embedding...")
embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

print(f"Menghitung embedding untuk {len(documents)} dokumen...")
t0 = time.time()
embeddings = embedding_model.encode(documents, show_progress_bar=True)
print(f"Embedding selesai dalam {time.time() - t0:.1f} detik.\n")

# ---------------------------------------------------------------------------
# 3. Eksperimen parameter: min_cluster_size = 5, 8, 12
# ---------------------------------------------------------------------------

experiment_sizes = [5, 8, 12]
experiment_results = []

for mcs in experiment_sizes:
    print(f"--- Eksperimen min_cluster_size={mcs} ---")

    umap_model = UMAP(
        n_neighbors=10, n_components=5, min_dist=0.0,
        metric="cosine", random_state=42,
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=mcs, min_samples=3,
        metric="euclidean", cluster_selection_method="eom",
        prediction_data=True,
    )
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        language="multilingual",
        calculate_probabilities=True,
        verbose=True,
    )

    topics, probs = topic_model.fit_transform(documents, embeddings)

    n_topics = len(set(topics)) - (1 if -1 in topics else 0)
    n_outliers = topics.count(-1)
    pct_outliers = n_outliers / len(topics) * 100

    experiment_results.append({
        "min_cluster_size": mcs,
        "n_topics": n_topics,
        "n_outliers": n_outliers,
        "pct_outliers": round(pct_outliers, 1),
    })

    print(f"  Topik: {n_topics}, Outlier: {n_outliers} ({pct_outliers:.1f}%)\n")

    # Simpan hasil lengkap hanya untuk min_cluster_size=8
    if mcs == 8:
        saved_topics = topics
        saved_probs = probs
        saved_model = topic_model

# ---------------------------------------------------------------------------
# 4. Perbandingan eksperimen
# ---------------------------------------------------------------------------

print("=" * 60)
print("PERBANDINGAN EKSPERIMEN PARAMETER")
print("=" * 60)
print(f"{'min_cluster_size':>18} {'topik':>8} {'outlier':>10} {'% outlier':>12}")
print("-" * 60)
for r in experiment_results:
    print(f"{r['min_cluster_size']:>18} {r['n_topics']:>8} "
          f"{r['n_outliers']:>10} {r['pct_outliers']:>11.1f}%")
print()

# ---------------------------------------------------------------------------
# 5. Output untuk min_cluster_size=8
# ---------------------------------------------------------------------------

topics = saved_topics
probs = saved_probs
topic_model = saved_model

# 5a. topic_info_IXNas.csv
topic_info = topic_model.get_topic_info()
topic_info.to_csv("topic_info_IXNas.csv", index=False, encoding="utf-8-sig")
print("Disimpan: topic_info_IXNas.csv")

# 5b. comments_with_topics_IXNas.csv
df_clean = df_clean.copy()
df_clean["topic"] = topics
df_clean["topic_probability"] = [p.max() if hasattr(p, "max") else p for p in probs]
df_clean.to_csv("comments_with_topics_IXNas.csv", index=False, encoding="utf-8-sig")
print("Disimpan: comments_with_topics_IXNas.csv")

# 5c. representative_docs_IXNas.txt
representative = topic_model.get_representative_docs()

with open("representative_docs_IXNas.txt", "w", encoding="utf-8") as f:
    topic_ids = sorted(set(topics))
    for tid in topic_ids:
        info_row = topic_info[topic_info["Topic"] == tid]
        count = info_row["Count"].values[0] if len(info_row) > 0 else "?"
        name = info_row["Name"].values[0] if len(info_row) > 0 else ""

        f.write("=" * 70 + "\n")
        f.write(f"TOPIK {tid}  |  {count} dokumen  |  {name}\n")
        f.write("=" * 70 + "\n\n")

        # Ambil dokumen per topik
        topic_docs_idx = [i for i, t in enumerate(topics) if t == tid]

        # Ambil probabilitas per dokumen untuk topik ini
        doc_probs = []
        for i in topic_docs_idx:
            if hasattr(probs[i], "__len__") and len(probs[i]) > 0:
                prob_idx = tid + 1 if tid >= 0 else 0
                if prob_idx < len(probs[i]):
                    doc_probs.append((i, probs[i][prob_idx]))
                else:
                    doc_probs.append((i, probs[i].max() if hasattr(probs[i], "max") else 0))
            else:
                doc_probs.append((i, float(probs[i]) if probs[i] is not None else 0))

        doc_probs.sort(key=lambda x: x[1], reverse=True)
        top_n = doc_probs[:15]

        for rank, (idx, prob) in enumerate(top_n, 1):
            text = documents[idx]
            f.write(f"  [{rank:2d}] (prob={prob:.4f})\n")
            f.write(f"       {text}\n\n")

        f.write("\n")

print("Disimpan: representative_docs_IXNas.txt")

# ---------------------------------------------------------------------------
# 6. Ringkasan ke terminal
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print("RINGKASAN (min_cluster_size=8)")
print("=" * 60)

n_topics = len(set(topics)) - (1 if -1 in topics else 0)
n_outliers = topics.count(-1)
pct_outliers = n_outliers / len(topics) * 100

print(f"Jumlah topik       : {n_topics}")
print(f"Outlier (topik -1) : {n_outliers} ({pct_outliers:.1f}%)")
print(f"Total dokumen      : {len(topics)}")
print()
print("Ukuran per topik:")
print(f"  {'Topik':>8} {'Jumlah':>10} {'%':>8}")
print("  " + "-" * 30)
for _, row in topic_info.sort_values("Topic").iterrows():
    tid = row["Topic"]
    cnt = row["Count"]
    pct = cnt / len(topics) * 100
    print(f"  {tid:>8} {cnt:>10} {pct:>7.1f}%")
