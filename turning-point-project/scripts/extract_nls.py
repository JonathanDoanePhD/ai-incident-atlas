"""Stream selected columns (by codebook reference number) out of an NLS all-variables CSV inside its zip.

Usage: python scripts/extract_nls.py ZIP CSVNAME SPEC.json KEY OUT.csv
SPEC[KEY] maps analytic names to reference numbers like 'C00001.00' (CSV header 'C0000100').
Reads row by row (the files have 10^5+ columns), so memory stays small.
"""
import csv
import io
import json
import sys
import zipfile

zpath, csvname, specpath, key, out = sys.argv[1:6]
spec = json.load(open(specpath))[key]
names = list(spec)
cols = [spec[n].replace(".", "") for n in names]
with zipfile.ZipFile(zpath).open(csvname) as f, open(out, "w", newline="") as fo:
    tf = io.TextIOWrapper(f, encoding="latin-1", newline="")
    header = [h.strip('"') for h in tf.readline().rstrip("\r\n").split(",")]
    pos = {h: i for i, h in enumerate(header)}
    missing = [c for c in cols if c not in pos]
    if missing:
        sys.exit(f"columns not in file: {missing}")
    ix = [pos[c] for c in cols]
    w = csv.writer(fo)
    w.writerow(names)
    n = 0
    for line in tf:
        p = line.rstrip("\r\n").split(",")
        if len(p) != len(header):
            sys.exit(f"row {n}: {len(p)} fields, expected {len(header)}")
        w.writerow([p[i] for i in ix])
        n += 1
print(out, n, "rows", len(names), "cols")
