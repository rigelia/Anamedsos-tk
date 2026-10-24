"""
Langkah 3 pipeline: sentimen pada komentar relevan (alat bantu, bukan keputusan akhir).

Dua model dijalankan supaya bisa dibandingkan:
  - id:   w11wo/indonesian-roberta-base-sentiment-classifier (RoBERTa Indonesia, data SmSA/IndoNLU)
  - xlmr: cardiffnlp/twitter-xlm-roberta-base-sentiment (XLM-R multibahasa, data Twitter)
Input teks: `text_embed` (pembersihan minimal; negasi, emoji, slang dan intensifier tetap ada).

Kolom `sent_agree` = kedua model sepakat. Komentar negatif tetap dikonfirmasi dengan dibaca,
karena sarkasme ("Kreatif sekali", "Bagus bgt🗿") sering terbaca positif oleh model.

Penggunaan:
  python src/sentiment_relevant.py [--version v1] [--overwrite]
"""

from datetime import datetime, timezone
from importlib.metadata import version as package_version
from pathlib import Path
import argparse
import json
import sys
import time

import numpy as np
import pandas as pd

SCRIPT_VERSION = "1.0"
PROCESSED_DIR = Path("data/processed")
MODELS = {
    "id": "w11wo/indonesian-roberta-base-sentiment-classifier",
    "xlmr": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
}
LABELS = ["negative", "neutral", "positive"]
BATCH_SIZE = 32
MAX_LENGTH = 256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sentimen komentar relevan (dua model).")
    parser.add_argument("--version", default="v1")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def predict(model_name: str, texts: list[str]) -> np.ndarray:
    """Probabilitas per kelas, urutan kolom mengikuti LABELS."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).eval()
    order = [next(i for i, l in model.config.id2label.items() if l.lower() == lab) for lab in LABELS]
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), BATCH_SIZE):
            enc = tok(texts[i:i + BATCH_SIZE], padding=True, truncation=True, max_length=MAX_LENGTH,
                      return_tensors="pt")
            out.append(torch.softmax(model(**enc).logits, dim=-1)[:, order].numpy())
    return np.vstack(out)


def main():
    args = parse_args()
    out_csv = PROCESSED_DIR / f"comments_sentiment_{args.version}.csv"
    if out_csv.exists() and not args.overwrite:
        print(f"ERROR: {out_csv} sudah ada. Gunakan --overwrite.")
        sys.exit(1)

    df = pd.read_csv(PROCESSED_DIR / f"comments_relevance_{args.version}.csv", encoding="utf-8-sig",
                     dtype={"commentId": str})
    df = df[df["relevant"] == "y"].reset_index(drop=True)
    texts = df["text_embed"].fillna("").tolist()
    print(f"  {len(df)} komentar relevan")

    timings = {}
    for key, name in MODELS.items():
        t0 = time.time()
        probs = predict(name, texts)
        timings[key] = round(time.time() - t0, 1)
        df[f"sent_{key}"] = [LABELS[i] for i in probs.argmax(axis=1)]
        for j, lab in enumerate(LABELS):
            df[f"p_{key}_{lab[:3]}"] = probs[:, j].round(4)
        print(f"  {key}: {df[f'sent_{key}'].value_counts().to_dict()} ({timings[key]} s)")

    df["sent_agree"] = df["sent_id"] == df["sent_xlmr"]
    df.drop(columns=["route"]).to_csv(out_csv, index=False, encoding="utf-8-sig")

    summary = {
        "script": f"sentiment_relevant.py v{SCRIPT_VERSION}",
        "executed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input": f"comments_relevance_{args.version}.csv (relevant == y)",
        "text_column": "text_embed",
        "models": MODELS,
        "max_length": MAX_LENGTH,
        "library_versions": {p: package_version(p) for p in ["transformers", "torch"]},
        "seconds": timings,
        "n": len(df),
        "counts": {k: df[f"sent_{k}"].value_counts().to_dict() for k in MODELS},
        "agreement": round(float(df["sent_agree"].mean()), 3),
        "crosstab_id_vs_xlmr": pd.crosstab(df["sent_id"], df["sent_xlmr"]).to_dict(orient="index"),
    }
    out_csv.with_suffix(".json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Kesepakatan kedua model: {summary['agreement']}")
    print(f"  Output: {out_csv}")


if __name__ == "__main__":
    main()
