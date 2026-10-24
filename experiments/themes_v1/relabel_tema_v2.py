"""Theme codes v2: Claude v1 codes + Claude's v2 changes outside the sample + adjudicated human codes on the validation sample."""
import json
from pathlib import Path

import pandas as pd

from tema_v1 import proportions

DIR = Path(__file__).parent


def main():
    df = pd.read_csv(DIR / "tema_claude_v1.csv")
    ch = pd.read_csv(DIR / "perubahan_tema_v2_claude.csv")
    val = pd.read_csv(DIR / "validasi_tema_final.csv")
    assert not set(ch["idx"]) & set(val["idx"]), "changes must be outside the validation sample"
    cur = df.set_index("idx").loc[ch["idx"], "tema_utama"]
    assert (cur.values == ch["tema_utama_v1"].values).all(), "change log does not match v1 codes"

    df["tema_utama_claude_v1"] = df["tema_utama"]
    df["source"] = "claude_v1"
    m = df["idx"].isin(ch["idx"])
    df.loc[m, "tema_utama"] = df.loc[m, "idx"].map(ch.set_index("idx")["tema_utama_v2"])
    df.loc[m, "source"] = "claude_v2"
    v = df["idx"].isin(val["idx"])
    df.loc[v, "tema_utama"] = df.loc[v, "idx"].map(val.set_index("idx")["final"])
    df.loc[v, "source"] = "manusia"
    # tema_kedua is kept from v1 unless it now equals tema_utama
    df.loc[df["tema_kedua"] == df["tema_utama"], "tema_kedua"] = None
    df.to_csv(DIR / "tema_final_v2.csv", index=False, encoding="utf-8")

    summary = {
        "codebook_version": "v2",
        "n": len(df),
        "source": df["source"].value_counts().to_dict(),
        "tema_utama": df["tema_utama"].value_counts().to_dict(),
        "tema_utama_pct": (df["tema_utama"].value_counts(normalize=True) * 100).round(1).to_dict(),
        "n_with_tema_kedua": int(df["tema_kedua"].notna().sum()),
        "by_org_type": proportions(df, "org_type"),
        "by_video_type": proportions(df, "video_type"),
        "by_case": proportions(df, "case_id"),
    }
    (DIR / "tema_final_v2.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["n", "source", "tema_utama", "tema_utama_pct"]}, indent=2))
    for col in ["org_type", "video_type"]:
        print(pd.DataFrame(summary[f"by_{col}"]["pct"]).to_string())


if __name__ == "__main__":
    main()
