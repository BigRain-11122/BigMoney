"""r268 bm-b rebase resolver -- 14-UU snapshot-family batch (S7 push collision
with bm-a r264 same-window S6 runs). Classified by
tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py:
10 auto-classified + 4 UNKNOWN hand-adjudicated per r242/r267 laws.

Rebase face semantics (r245 law): ours=:2:=origin side (bm-a r264, runs
19:01-19:04), theirs=:3:=replayed commit (bm-b r268, runs 19:08-19:09).
Nested ts probe (r267 recursive-flatten law) shows theirs newer on every
face -> snapshots take theirs; ledgers union with zero row loss.

Recipes:
- compute_audit.json / regime_state.json: rolling-ledger union (history /
  transitions lists deduped, ts-ascending) + state fields take-new (R208)
- dashboard_status.json + 8 *_status/scorecard/token faces: snapshot
  take-new whole bytes (R208/R216)
- scorecard_v1 / strategy_scorecard (UNKNOWN->hand): deterministic L1
  re-derive snapshots, only drift = generated/elapsed -> take-new by ts
- REPORT-20260926 json/md pair (UNKNOWN->hand, r242): take-side by json
  twin generated_at -> md whole-byte same side
- dashboard_status.js (R209): wrapper snapshot, whole-byte take-side
"""
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

SNAPSHOTS = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "docs/daily_report/REPORT-2026-09-26.json",
]
WHOLE_BYTES_SAME_SIDE = {
    "docs/daily_report/REPORT-2026-09-26.md": "docs/daily_report/REPORT-2026-09-26.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
LEDGERS = ["results/compute_audit.json", "results/regime_state.json"]


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show %s -> %d" % (spec, r.returncode))
    return r.stdout


def flat_ts(d, pre="", depth=0):
    """Recursive ts probe (r267 law: nested two levels minimum)."""
    out = {}
    if depth > 3 or not isinstance(d, dict):
        return out
    for k, v in d.items():
        kl = k.lower()
        if isinstance(v, (str, int, float)) and any(
                t in kl for t in ("ts", "updated", "generated", "as_of", "at")):
            out[pre + k] = str(v)
        elif isinstance(v, dict):
            out.update(flat_ts(v, pre + k + ".", depth + 1))
    return out


def newest_side(path):
    a = json.loads(blob(":2:" + path))
    b = json.loads(blob(":3:" + path))
    fa, fb = flat_ts(a), flat_ts(b)
    ka = max(fa.values()) if fa else ""
    kb = max(fb.values()) if fb else ""
    side = "theirs" if kb >= ka else "ours"
    print("  ts probe %s: ours=%s theirs=%s -> %s" % (path, ka, kb, side))
    return side


def write_bytes(path, raw):
    p = os.path.join(ROOT, path.replace("/", os.sep))
    with io.open(p, "wb") as fh:
        fh.write(raw)


def byte_faces(raw):
    return {"BOM": raw[:3] == b"\xef\xbb\xbf", "CRLF": b"\r\n" in raw,
            "trailing_nl": raw.endswith(b"\n")}


def union_ledger(path, list_keys, state_take_from="theirs"):
    a = json.loads(blob(":2:" + path))
    b = json.loads(blob(":3:" + path))
    out = dict(b if state_take_from == "theirs" else a)  # state fields face
    for k in list_keys:
        la = a.get(k, [])
        lb = b.get(k, [])
        seen = set()
        merged = []
        for row in la + lb:
            key = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
        merged.sort(key=lambda r: str(r.get("ts", r.get("asof", ""))))
        out[k] = merged
        print("  union %s.%s: %d+%d -> %d (zero-loss %s)" %
              (path, k, len(la), len(lb), len(merged),
               "OK" if len(merged) >= max(len(la), len(lb)) else "FAIL"))
    base = blob(":2:" + path)
    faces = byte_faces(base)
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    if faces["CRLF"]:
        txt = txt.replace("\n", "\r\n")
    if faces["trailing_nl"] and not txt.endswith("\n"):
        txt += "\n"
    if not faces["trailing_nl"] and txt.endswith("\n"):
        txt = txt[:-1]
    p = os.path.join(ROOT, path.replace("/", os.sep))
    with io.open(p, "wb") as fh:
        fh.write(txt.encode("utf-8"))
    json.load(io.open(p, encoding="utf-8"))  # parse verify (r185 law)
    print("  resolved ledger %s faces=%s" % (path, faces))


def main():
    print("== snapshot take-new family ==")
    sides = {}
    for path in SNAPSHOTS:
        side = newest_side(path)
        sides[path] = side
        raw = blob(":%s:%s" % ("3" if side == "theirs" else "2", path))
        write_bytes(path, raw)
        json.load(io.open(os.path.join(ROOT, path.replace("/", os.sep)),
                          encoding="utf-8"))
    print("== whole-byte same-side family (R209/r242) ==")
    for path, twin in WHOLE_BYTES_SAME_SIDE.items():
        side = sides[twin]
        raw = blob(":%s:%s" % ("3" if side == "theirs" else "2", path))
        write_bytes(path, raw)
        print("  %s <- %s side whole bytes (%d B)" % (path, side, len(raw)))
    print("== rolling-ledger union family ==")
    union_ledger("results/compute_audit.json", ["history"])
    union_ledger("results/regime_state.json", ["transitions", "history"])
    print("resolver done; verify + add next")


if __name__ == "__main__":
    main()
