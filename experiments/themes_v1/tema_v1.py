"""
Kode tema Claude v1 (codebook v1) untuk semua komentar `tolak`: gabungkan, ringkas, dan siapkan validasi buta.

Input:
  kode_claude_v1.txt   satu baris per komentar: "<idx> <tema_utama> [tema_kedua]" (idx = stance_input.csv)
Output (experiments/themes_v1/):
  tema_claude_v1.csv       kode + konteks kasus, org type, video type
  tema_claude_v1.json      jumlah dan proporsi tema_utama per org type, video type, kasus
  validasi_tema_ids.csv    100 komentar acak (seed 42, di luar 50 komentar pilot)
  validasi_tema.xlsx       lembar validasi buta (sheet Petunjuk = codebook v1, sheet Kode = isian)

Penggunaan:
  python experiments/themes_v1/tema_v1.py
"""

import json
from pathlib import Path

import pandas as pd

import prep_kalibrasi

DIR = Path(__file__).parent
STANCE_DIR = DIR.parent / "stance_v1"
SEED = 42
N_VALID = 100
CODES = ["KV", "PK", "HC", "AK", "KO", "AU", "EJ", "LT"]


def load_codes() -> pd.DataFrame:
    rows = []
    for line in (DIR / "kode_claude_v1.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if parts:
            rows.append({"idx": int(parts[0]), "tema_utama": parts[1],
                         "tema_kedua": parts[2] if len(parts) > 2 else None})
    codes = pd.DataFrame(rows)
    assert codes["idx"].is_unique
    assert set(codes["tema_utama"]) | set(codes["tema_kedua"].dropna()) <= set(CODES)
    assert not (codes["tema_utama"] == codes["tema_kedua"]).any()
    return codes


def proportions(df: pd.DataFrame, col: str) -> dict:
    ct = pd.crosstab(df["tema_utama"], df[col])
    pct = (ct / ct.sum() * 100).round(1)
    return {"n": ct.to_dict(), "pct": pct.to_dict()}


def main():
    stance = pd.read_csv(STANCE_DIR / "stance_input.csv", dtype={"commentId": str})
    final = pd.read_csv(STANCE_DIR / "sikap_final_v2.csv", dtype={"commentId": str})
    tolak = stance.merge(final[["commentId", "sikap"]], on="commentId")
    tolak = tolak[tolak["sikap"] == "tolak"]

    codes = load_codes()
    missing = set(tolak["idx"]) - set(codes["idx"])
    extra = set(codes["idx"]) - set(tolak["idx"])
    assert not missing and not extra, f"missing {len(missing)}, extra {len(extra)}"

    df = tolak.merge(codes, on="idx")
    cols = ["idx", "commentId", "case_id", "videoId", "org_type", "video_type", "isReply",
            "tema_utama", "tema_kedua"]
    df[cols].to_csv(DIR / "tema_claude_v1.csv", index=False, encoding="utf-8")

    summary = {
        "codebook_version": "v1",
        "n": len(df),
        "tema_utama": df["tema_utama"].value_counts().to_dict(),
        "tema_utama_pct": (df["tema_utama"].value_counts(normalize=True) * 100).round(1).to_dict(),
        "n_with_tema_kedua": int(df["tema_kedua"].notna().sum()),
        "any_mention": {c: int(((df["tema_utama"] == c) | (df["tema_kedua"] == c)).sum()) for c in CODES},
        "by_org_type": proportions(df, "org_type"),
        "by_video_type": proportions(df, "video_type"),
        "by_case": proportions(df, "case_id"),
    }
    (DIR / "tema_claude_v1.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    pilot = set(pd.read_csv(DIR / "pilot_codebook_ids.csv")["idx"])
    pool = df[~df["idx"].isin(pilot)]
    sample = pool.sample(N_VALID, random_state=SEED).reset_index(drop=True)
    sample[["idx", "commentId"]].to_csv(DIR / "validasi_tema_ids.csv", index=False)
    sample["parent_text"] = sample["parent_text"].fillna("")
    prep_kalibrasi.write_sheet(sample, DIR / "validasi_tema.xlsx", title="Validasi buta codebook tema v1 (100 komentar)")

    print(json.dumps({k: summary[k] for k in ["n", "tema_utama", "tema_utama_pct", "n_with_tema_kedua"]},
                     indent=2, ensure_ascii=False))
    print(f"Validasi: {len(sample)} komentar -> {DIR / 'validasi_tema.xlsx'}")


if __name__ == "__main__":
    main()
