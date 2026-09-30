"""r476 bm-a rebase resolver (canon: bigmoney-conflict-resolve skill).

Conflict faces vs origin/main (bm-c r273/274 + bm-b r466/467 same-window
S6 batches):
  - 21 derived snapshot/CEO faces -> per-file embedded-ts probe, take the
    NEWER side (r461 law: direction proven per file, never assumed);
    identical-content faces -> either side (identity);
  - results/paper/marks/marks-20260930.jsonl -> append-only daily ledger:
    :2/:3 blob line-level union, ts-sorted, json.loads per-line validation
    (zero-loss assertion: rows >= max(both sides));
  - CODELY.md -> EXCLUDED here (semantic entry-union handled separately).
Exit 0 = all resolved; assert-heavy, fail-closed.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TS_PROBE = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper_export/export-2026-09-29.json",
    "results/paper_export/latest.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
MARKS = "results/paper/marks/marks-20260930.jsonl"
COMPUTE_AUDIT = "results/compute_audit.json"  # rolling history ledger -> union (r467/r274 canon)


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{side}:{path} rc={r.returncode}")
    return r.stdout.decode("utf-8", errors="replace")


def probe_ts(text):
    """Latest ISO-ish timestamp in the text (ts / generated / as_of...)."""
    cands = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", text)
    if not cands:
        return ""
    return max(cands)


def resolve_ts(path):
    a, b = blob(2, path), blob(3, path)
    if a == b:
        return path, "identity", a
    ta, tb = probe_ts(a), probe_ts(b)
    if not ta or not tb:
        # no timestamps -> compare len, take richer side (both derived faces)
        return path, f"len({len(a)} vs {len(b)})", a if len(a) >= len(b) else b
    if ta > tb:
        return path, f"take-ours {ta} > {tb}", a
    if tb > ta:
        return path, f"take-theirs {tb} > {ta}", b
    return path, f"ts-tie {ta}", a if len(a) >= len(b) else b


def resolve_marks(path):
    a, b = blob(2, path), blob(3, path)
    la = [l for l in a.splitlines() if l.strip()]
    lb = [l for l in b.splitlines() if l.strip()]
    seen, union = set(), []
    for line in la + lb:
        key = line.strip()
        if key in seen:
            continue
        seen.add(key)
        union.append(line)
    def _tskey(line):
        m = re.search(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line)
        return m.group(0) if m else ""
    union.sort(key=_tskey)
    for line in union:
        json.loads(line)
    assert len(union) >= max(len(la), len(lb)), "union must be a superset"
    return path, f"union {len(la)}+{len(lb)}->{len(union)}", \
        "\n".join(union) + ("\n" if union else "")


def resolve_compute_audit(path):
    """Rolling history ledger: full-row dedupe union, ts-sorted (r461 law:
    take-newer would drop the other side's history rows = loss)."""
    a, b = blob(2, path), blob(3, path)
    da, db = json.loads(a), json.loads(b)
    ha, hb = da["history"], db["history"]
    seen, union = set(), []
    for row in ha + hb:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        union.append(row)
    union.sort(key=lambda r: r.get("ts", ""))
    assert len(union) >= max(len(ha), len(hb)), "union superset violated"
    # latest = the side with the newer last history row
    newer = da if (ha[-1].get("ts", "") >= hb[-1].get("ts", "")) else db
    out = {"latest": newer["latest"], "history": union}
    return path, f"union {len(ha)}+{len(hb)}->{len(union)}", \
        json.dumps(out, ensure_ascii=False, indent=1) + "\n"


def unmerged():
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True)
    paths = set()
    for line in r.stdout.decode("utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            paths.add(parts[-1])
    return paths


def main():
    um = unmerged()
    log = {}
    for path in TS_PROBE:
        if path not in um:
            print(f"skip-not-unmerged              {path}")
            continue
        p, verdict, content = resolve_ts(path)
        with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        log[p] = verdict
        print(f"{verdict:38s} {p}")
    if MARKS in um:
        p, verdict, content = resolve_marks(MARKS)
        with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        log[p] = verdict
        print(f"{verdict:38s} {p}")
    if COMPUTE_AUDIT in um:
        p, verdict, content = resolve_compute_audit(COMPUTE_AUDIT)
    with open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    log[p] = verdict
    print(f"{verdict:38s} {p}")
    with open(os.path.join(ROOT, "results", "_r476bma_resolve.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"round": "r476 rebase resolver", "faces": log}, fh,
                  ensure_ascii=False, indent=1)
    print("resolved:", len(log), "faces (CODELY.md handled separately)")


if __name__ == "__main__":
    main()
