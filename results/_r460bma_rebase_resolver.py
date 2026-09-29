#!/usr/bin/env python
"""r460 bm-a rebase conflict resolver (15-face batch, classify_conflicts + ALL_FACES via
merge_lane_views already handled 6 union faces; this script finishes the rest):
  - snapshot take-new by deep-scanned ts: results/fundamental_b_layer_filter.json,
    results/_attrition_guard_scan.json
  - twin-regen same-day pairs (md+json MUST take the SAME side, r327/r329):
    docs/daily_report/REPORT-2026-09-30.{json,md},
    docs/live_usage/LIVE-2026-09-30.{json,md}, docs/live_usage/LIVE-latest.{json,md}
  - append-union (both sides added distinct archive sections):
    research/memory-archive/202609.md
Rebase stage law r351: :2: = origin side, :3: = local (bm-a) side.
Zero-loss laws: snapshots verify ts probe existence first (r319); twins side-couple by
the json's own generated/updated ts; archive union = base-prefix identity assert, else
entry-level bidirectional supersets (r327), byte-verified.
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT,
                        capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_ts(obj, best=None):
    """Deep-scan for the newest 20xx- ts-ish value (r311/D-09)."""
    if best is None:
        best = ""
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and re.match(r"^20\d{2}-", obj):
        if obj > best:
            best = obj
    return best


def resolve_snapshot(path):
    a, b = stage_blob(2, path), stage_blob(3, path)
    ja, jb = json.loads(a), json.loads(b)
    ta, tb = deep_ts(ja), deep_ts(jb)
    print(f"[snapshot] {path}: origin_ts={ta!r} local_ts={tb!r}")
    if not ta or not tb:
        side = "local" if tb else "origin"
        print(f"  probe miss one side -> take {side} (existence-first law r319)")
        data, raw = (jb, b) if tb else (ja, a)
    else:
        data, raw = (jb, b) if tb > ta else (ja, a)
        print(f"  take-{'local' if tb > ta else 'origin'} (newer ts)")
    json.loads(raw)  # parse-verify before write
    with open(path, "wb") as fh:
        fh.write(raw)
    json.load(open(path, encoding="utf-8"))
    print(f"  wrote + parse-verified")


def resolve_twin(json_path, md_path):
    ja, jb = json.loads(stage_blob(2, json_path)), json.loads(stage_blob(3, json_path))
    ta, tb = deep_ts(ja), deep_ts(jb)
    side = 3 if (tb or "") > (ta or "") else 2
    print(f"[twin] {json_path}: origin_ts={ta!r} local_ts={tb!r} -> take "
          f"{'local' if side == 3 else 'origin'} BOTH twins")
    for p in (json_path, md_path):
        raw = stage_blob(side, p)
        if raw is None:
            print(f"  !! stage {side} missing for {p} -- manual look")
            continue
        with open(p, "wb") as fh:
            fh.write(raw)
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8"))
        print(f"  wrote {p}")


def resolve_archive_union(path):
    base = stage_blob(1, path).decode("utf-8", errors="replace")
    a = stage_blob(2, path).decode("utf-8", errors="replace")
    b = stage_blob(3, path).decode("utf-8", errors="replace")
    # base-prefix identity: both sides edited AFTER the base prefix?
    pa = a.startswith(base)
    pb = b.startswith(base)
    print(f"[archive-union] {path}: base-prefix identity "
          f"origin={pa} local={pb} (base {len(base)}B A {len(a)}B B {len(b)}B)")
    if pa and pb:
        merged = a + b[len(base):]
        law = "prefix-identity direct concat"
    else:
        # entry-level bidirectional supersets (r327): both sides' sections must
        # survive; sections are '## <heading>' blocks in this archive file.
        def sections(txt):
            parts = re.split(r"(?=^## )", txt, flags=re.M)
            return {p.splitlines()[0][3:].strip(): p for p in parts
                    if p.startswith("## ")}
        sa, sb = sections(a), sections(b)
        heads = list(sa) + [h for h in sb if h not in sa]
        merged = a if not pb else (b if not pa else None)
        if merged is None:
            # rebuild: keep origin's face then append local-only sections at end
            merged = a
            for h in heads:
                if h not in sa:
                    merged += "\n" + sb[h]
            law = "entry-level section union (r327 fallback)"
        else:
            law = f"take-{'origin' if not pb else 'local'} (other side == base edit)"
    # zero-loss account: every '## ' heading from both sides must be present
    ha = set(re.findall(r"^## (.+)$", a, flags=re.M))
    hb = set(re.findall(r"^## (.+)$", b, flags=re.M))
    hm = set(re.findall(r"^## (.+)$", merged, flags=re.M))
    missing = (ha | hb) - hm
    assert not missing, f"section loss: {missing}"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(merged)
    print(f"  union law={law}; headings A={len(ha)} B={len(hb)} merged={len(hm)} "
          f"zero-loss OK; wrote {len(merged)}B")


if __name__ == "__main__":
    resolve_snapshot("results/fundamental_b_layer_filter.json")
    resolve_snapshot("results/_attrition_guard_scan.json")
    resolve_twin("docs/daily_report/REPORT-2026-09-30.json",
                 "docs/daily_report/REPORT-2026-09-30.md")
    resolve_twin("docs/live_usage/LIVE-2026-09-30.json",
                 "docs/live_usage/LIVE-2026-09-30.md")
    resolve_twin("docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md")
    resolve_archive_union("research/memory-archive/202609.md")
    print("RESOLVER DONE")
