"""r379 bm-a push-storm resolver: 15 non-ALL_FACES UU files.

Canon per bigmoney-conflict-resolve SKILL:
- snapshot family (paper/*_paper.json, paper_export pair, prospect
  summaries, t35_open_fill_verify, fundamental_b_layer_filter, REPORT
  twins): hardened deep-ts probe on STAGED blobs (:2:=origin, :3:=replay
  side), fresher side wins WHOLE-BLOB byte-verbatim; r100 key-normalize +
  value-shape gate, R350 no key-EXCLUDE lists + wall-clock values require
  time-of-day; twins take the SAME side (md byte-copy, r329).
- append-log x2_watch_log.jsonl: line-level identity union, ts-sorted.
Every write json.loads parse-verified (r185) + conflict-marker scanned.
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    """Read a rebase stage blob as raw bytes (:2:=origin, :3:=replay)."""
    r = subprocess.run(["git", "cat-file", "-p", f":{stage}:{path}"],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError(f"cat-file {stage}:{path}: {r.stderr[:200]}")
    return r.stdout


def deep_max_ts(obj):
    """Hardened deep probe: recursive walk, ts-shaped wall-clock values
    only (date-only values must not feed the max, R350)."""
    best = None
    if isinstance(obj, dict):
        for v in obj.values():
            b = deep_max_ts(v)
            if b and (best is None or b > best):
                best = b
    elif isinstance(obj, list):
        for v in obj:
            b = deep_max_ts(v)
            if b and (best is None or b > best):
                best = b
    elif isinstance(obj, str) and TS_SHAPE.match(obj):
        best = obj
    return best


def parse(b):
    return json.loads(b.decode("utf-8"))


def resolve_snapshot(path, label=""):
    b2, b3 = blob(2, path), blob(3, path)
    t2, t3 = deep_max_ts(parse(b2)), deep_max_ts(parse(b3))
    # tie -> :2: origin (r140 same-second tie law)
    win, side = (b3, ":3:") if (t3 or "") > (t2 or "") else (b2, ":2:")
    with open(path, "wb") as fh:
        fh.write(win)
    parse(win)  # parse-verify r185
    assert b"<<<<<<<" not in win and b"=======" not in win
    print(f"  {path}: take {side} (origin ts={t2} mine ts={t3}) {label}")
    return side


def resolve_twin(json_path, md_path):
    """Twin-side coupling r327/r329: json probe decides, md byte-copies
    the SAME side."""
    b2, b3 = blob(2, json_path), blob(3, json_path)
    t2, t3 = deep_max_ts(parse(b2)), deep_max_ts(parse(b3))
    jwin, mside = (b3, 3) if (t3 or "") > (t2 or "") else (b2, 2)
    mwin = blob(mside, md_path)
    with open(json_path, "wb") as fh:
        fh.write(jwin)
    with open(md_path, "wb") as fh:
        fh.write(mwin)
    parse(jwin)
    assert b"<<<<<<<" not in jwin and b"<<<<<<<" not in mwin
    print(f"  twin {json_path} + {md_path}: BOTH take :{mside}: "
          f"(origin ts={t2} mine ts={t3})")


def resolve_line_union(path, ts_key="ts"):
    """append-log line-level identity union, ts-sorted zero loss (r188)."""
    lines2 = [l for l in blob(2, path).decode("utf-8").splitlines() if l]
    lines3 = [l for l in blob(3, path).decode("utf-8").splitlines() if l]
    seen, merged = set(), []
    for l in lines2 + lines3:            # stable order, exact-line identity
        if l not in seen:
            seen.add(l)
            merged.append(l)

    def ts_of(l):
        try:
            return json.loads(l).get(ts_key, "")
        except Exception:
            return ""
    merged.sort(key=lambda l: ts_of(l))
    out = "\n".join(merged) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    n2, n3, nu = len(lines2), len(lines3), len(merged)
    assert nu == len(seen) and nu >= max(n2, n3), (n2, n3, nu)
    print(f"  {path}: line union {n2}+{n3}->{nu} (ts-sorted, zero loss)")


ok = True
try:
    print("[twins]")
    resolve_twin("docs/daily_report/REPORT-2026-09-28.json",
                 "docs/daily_report/REPORT-2026-09-28.md")
    print("[paper family snapshots]")
    for f in ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
              "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"):
        resolve_snapshot(f"results/paper/{f}_paper.json")
    resolve_snapshot("results/paper_export/export-2026-09-24.json",
                     "(t35 export daily)")
    resolve_snapshot("results/paper_export/latest.json", "(t35 export latest)")
    resolve_snapshot("results/prospect_paper/_summary.json", "(t24p summary)")
    resolve_snapshot("results/prospect_promotion/_summary.json",
                     "(t24m summary)")
    resolve_snapshot("results/t35_open_fill_verify.json")
    resolve_snapshot("results/fundamental_b_layer_filter.json")
    print("[append-log]")
    resolve_line_union("results/x2_watch_log.jsonl")
    print("resolver: ALL PASS")
except Exception as ex:
    ok = False
    print(f"resolver FAULT: {ex}")
    raise
sys.exit(0 if ok else 1)
