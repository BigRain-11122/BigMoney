# -*- coding: utf-8 -*-
"""r675 bm-c merge resolver: 20 UU faces from origin wave integrate
(bm-a r823 W173 finalize + W174 seat chain + bm-b keepalive churn).

Canonical per-face law (r440 two-family split / r461 ts-dir-inverted
take-side / r662 token per-key max-union / compute_audit hist union):
- ts-newer-wins for twin-regen snapshot faces (18 faces);
- results/token_usage.json -> per-key max-union (shared keys pick the side
  with newer internal ts; unique keys kept from both sides);
- results/compute_audit.json -> history union zero-loss (dedup by identity,
  order by ts; containment assert: union >= each side).
Raw-bytes side pick (no re-serialization) for ts-newer faces; JSON round-trip
assert for union faces. All git calls stdout-only (r648 law)."""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TS_RE = re.compile(rb"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

UU = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
UNION_FACES = {"results/token_usage.json": "perkey", "results/compute_audit.json": "hist"}


def git_bytes(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=ROOT).stdout


def max_ts(b):
    m = TS_RE.findall(b)
    return max(m) if m else b""


def _key_ts(v):
    return max_ts(json.dumps(v, ensure_ascii=False, default=str).encode("utf-8"))


def union_perkey(ours_b, theirs_b):
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(theirs_b.decode("utf-8"))
    if not isinstance(o, dict) or not isinstance(t, dict):
        return ours_b if max_ts(ours_b) >= max_ts(theirs_b) else theirs_b, "ts-fallback"
    out = {}
    picked = 0
    for k in sorted(set(o) | set(t)):
        if k in o and k in t:
            if json.dumps(o[k], sort_keys=True, default=str) == json.dumps(t[k], sort_keys=True, default=str):
                out[k] = o[k]
            else:
                out[k] = o[k] if _key_ts(o[k]) >= _key_ts(t[k]) else t[k]
                picked += 1
        else:
            out[k] = o.get(k, t.get(k))
    s = json.dumps(out, indent=1, ensure_ascii=False)
    return s.encode("utf-8"), ("perkey-union side_pick=%d" % picked)


def union_hist(ours_b, theirs_b):
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(theirs_b.decode("utf-8"))
    if not isinstance(o, dict) or not isinstance(t, dict):
        return ours_b if max_ts(ours_b) >= max_ts(theirs_b) else theirs_b, "ts-fallback"
    oh = o.get("history", [])
    th = t.get("history", [])
    seen = {}
    for e in oh + th:
        seen[json.dumps(e, sort_keys=True, ensure_ascii=False, default=str)] = e
    merged = sorted(seen.values(), key=lambda e: str(_key_ts(e) if not isinstance(e, str) else e))
    assert len(merged) >= len(oh) and len(merged) >= len(th), "hist union containment failed"
    o["history"] = merged
    o["ts"] = max(str(max_ts(ours_b)), str(max_ts(theirs_b)))
    s = json.dumps(o, indent=1, ensure_ascii=False)
    return s.encode("utf-8"), ("hist-union %d+%d->%d" % (len(oh), len(th), len(merged)))


def main():
    report = {}
    for path in UU:
        ours = git_bytes(["show", ":2:%s" % path])
        theirs = git_bytes(["show", ":3:%s" % path])
        assert ours and theirs, "empty stage blob for " + path
        if path in UNION_FACES:
            if UNION_FACES[path] == "perkey":
                data, note = union_perkey(ours, theirs)
            else:
                data, note = union_hist(ours, theirs)
            json.loads(data.decode("utf-8"))  # round-trip assert
        else:
            to, tt = max_ts(ours), max_ts(theirs)
            if to >= tt:
                data, note = ours, "ours(ts %s>=%s)" % (to.decode(), tt.decode())
            else:
                data, note = theirs, "theirs(ts %s>%s)" % (tt.decode(), to.decode())
        with open(path, "wb") as fh:
            fh.write(data)
        subprocess.run(["git", "add", "--", path], capture_output=True, cwd=ROOT)
        assert b"<<<<<<<" not in data, "conflict marker leaked into " + path
        report[path] = note
    left = git_bytes(["diff", "--name-only", "--diff-filter=U"]).decode("utf-8").strip()
    assert left == "", "unresolved faces remain: " + left
    for k, v in report.items():
        print("RESOLVED", k, "->", v)
    print("ALL UU RESOLVED; staged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
