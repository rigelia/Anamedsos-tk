"""Apply guide v2: Claude's v2 stance labels plus the final labels (human labels for the 100-comment sample)."""
import json
from pathlib import Path

import pandas as pd

DIR = Path(__file__).parent


def main():
    c = pd.read_csv(DIR / "sikap_claude_v1.csv")
    ch = pd.read_csv(DIR / "perubahan_v2_claude.csv")
    assert ch.idx.is_unique
    m = c.merge(ch, on="idx", how="left")
    assert (m.loc[m.dari.notna(), "dari"] == m.loc[m.dari.notna(), "sikap_claude"]).all(), "log does not match v1"
    m["sikap_claude_v2"] = m["ke"].fillna(m["sikap_claude"])
    m["aturan_v2"] = m["aturan"]

    val = pd.read_csv(DIR / "validasi_sikap_final.csv")[["commentId", "sikap_final"]]
    assert not set(val.commentId) & set(m.loc[m.dari.notna(), "commentId"]), "sample rows must not be relabelled"
    m = m.merge(val.rename(columns={"sikap_final": "sikap_manusia"}), on="commentId", how="left")
    m["sikap"] = m["sikap_manusia"].fillna(m["sikap_claude_v2"])
    m["sumber_sikap"] = m["sikap_manusia"].notna().map({True: "validasi_adjudikasi", False: "claude_v2"})

    cols = ["idx", "commentId", "case_id", "org_type", "video_type", "sikap_claude", "sikap_claude_v2", "aturan_v2", "sikap", "sumber_sikap"]
    m[cols].rename(columns={"sikap_claude": "sikap_claude_v1"}).to_csv(DIR / "sikap_final_v2.csv", index=False, encoding="utf-8")

    t = m[m.sikap == "tolak"]
    pct = lambda col: (m.groupby(col).sikap.apply(lambda s: round(100 * (s == "tolak").mean(), 1))).to_dict()
    summary = {
        "n": len(m),
        "n_changed_by_v2": int(m.dari.notna().sum()),
        "changes": ch.groupby(["dari", "ke"]).size().rename("n").reset_index().to_dict(orient="records"),
        "counts_v1": c.sikap_claude.value_counts().to_dict(),
        "counts_final": m.sikap.value_counts().to_dict(),
        "tolak_pct_by_case": pct("case_id"),
        "tolak_pct_by_org_type": pct("org_type"),
        "tolak_pct_by_video_type": pct("video_type"),
        "dukung_pct_by_case": m.groupby("case_id").sikap.apply(lambda s: round(100 * (s == "dukung").mean(), 1)).to_dict(),
        "n_tolak": len(t),
    }
    (DIR / "sikap_final_v2.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
