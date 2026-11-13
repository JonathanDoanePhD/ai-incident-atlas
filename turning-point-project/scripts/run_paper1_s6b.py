"""Paper 1, sensitivity S6b (frozen plan): NLS custom longitudinal weight, complete cases.

Step 1 (done once): `python scripts/run_paper1_s6b.py --make-ids` writes data/processed/nlsy97_s6b_ids.txt (git-ignored):
         the PUBIDs of respondents whose attainment counts as observed (last interview round >= 14).
Step 2 (PI): paste those IDs at https://www.nlsinfo.org/weights/nlsy97 -> "Weight IDs" -> Download.
Step 3: `python scripts/run_paper1_s6b.py --weights <downloaded file>` -> outputs/paper1_s6b_results.json
"""
import argparse
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import run_paper1 as rp  # noqa: E402

warnings.filterwarnings("ignore")


def read_custom_weights(path):
    rows = []
    for line in Path(path).read_text(errors="ignore").splitlines():
        m = re.match(r"^\s*(\d+)\s+(\d+)\s*$", line)
        if m:
            rows.append((int(m.group(1)), int(m.group(2)) / 100.0))  # 2 implied decimals
    if not rows:
        sys.exit("No 'ID weight' rows found in the weights file.")
    return pd.Series(dict(rows), name="w_custom")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--make-ids", action="store_true"); ap.add_argument("--weights")
    a = ap.parse_args()
    df, _ = rp.prepare()
    ids = pd.read_csv(ROOT / "data/raw/nlsy97/paper1_extract.csv", usecols=["R0000100"])["R0000100"]
    df["pubid"] = ids.values
    if a.make_ids:
        keep = df.loc[df["last_round"] >= 14, "pubid"].astype(int)
        out = ROOT / "data/processed/nlsy97_s6b_ids.txt"; out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(map(str, keep)) + "\n")
        print(f"wrote {out.relative_to(ROOT)} ({len(keep)} IDs)"); return
    w = read_custom_weights(a.weights)
    df["w_custom"] = df["pubid"].map(w)
    res = {}
    for who in ("mother", "father"):
        s = df[(df[f"{who}_universe"] == 1) & df[f"{who}_vs"].notna()]
        cc = s.dropna(subset=["hgc", "w_custom", *[c for c in rp.COVARIATES if c in s.columns]])
        cc = cc[cc["w_custom"] > 0]
        est = rp.single_contrasts(rp.linear_fit(rp.pad(cc, df), who, wcol="w_custom"))
        res[who] = {"n": int(len(cc)), "estimates": est.to_dict("records")}
        t = est.set_index("quantity")
        print(who, len(cc), "theta14 %.3f (%.3f, %.3f)" % tuple(t.loc["theta_14", ["estimate", "ci_low", "ci_high"]]),
              "delta %.3f (%.3f, %.3f)" % tuple(t.loc["delta_16_vs_12", ["estimate", "ci_low", "ci_high"]]))
    (ROOT / "outputs/paper1_s6b_results.json").write_text(json.dumps(res, indent=2, default=float))


if __name__ == "__main__":
    main()
