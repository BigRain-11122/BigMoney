# -*- coding: utf-8 -*-
"""R345 bm-a rebase wave-2 UU batch resolver (28 UU vs bm-c r98 same-window
S6 family; skill SKILL.md shape table applied manually per classifier RED --
16 UNKNOWN = snapshot family, hand-classified here).

Recipes (SKILL.md):
  snapshot files        -> deep-ts probe (r311 nested-layer law, r319
                           path-exists-first) -> newer side WHOLE-BLOB bytes
                           verbatim; tie -> HEAD side (r140)
  compute_audit.json    -> rolling-ledger: history rows union zero-loss +
                           state fields take-new (r188/R208/r85)
  regime_state.json     -> rolling-ledger: histories/transitions union +
                           state take-new
  x2_watch_log.jsonl    -> append-log: line-level union (r188)
  autofill_state.json   -> mixed-dict+ledger (r322/r140; same recipe as
                           _r345bma_resolve.py wave-1)
  dashboard_status.js   -> js-wrapper-snapshot: take-side whole bytes by
                           embedded ts (R209)
  REPORT-2026-09-27.*   -> twin-regen-md: json deep generated_at picks side;
                           md copies the SAME side bytes (r327/r329)
"""
import json
import subprocess
import sys

TS_KEYS = ("ts", "generated_at", "updated_at", "asof", "time", "datetime",
           "last_tick", "now", "generated", "checked_at", "accept_ts")


def blob_bytes(rev, path):
    out = subprocess.run(["git", "show", f"{rev}{path}"], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {rev}{path}: {out.stderr[:120]}")
    return out.stdout


def deep_max_ts(o, depth=0):
    """Recursive max ts probe (r311: ts lives in NESTED layers; r319: probe
    path existence first). Returns max string ts found anywhere."""
    best = ""
    if depth > 8:
        return best
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and any(t in str(k).lower()
                                          for t in TS_KEYS) and len(v) >= 8:
                best = max(best, v)
            else:
                best = max(best, deep_max_ts(v, depth + 1))
    elif isinstance(o, list):
        for v in o:
            best = max(best, deep_max_ts(v, depth + 1))
    elif isinstance(o, str) and len(o) >= 8 and ("2026-" in o or "T" in o):
        pass
    return best


def parse(b):
    return json.loads(b.decode("utf-8"))


def resolve_snapshot(path, tie_head=True):
    ours, theirs = blob_bytes(":2:", path), blob_bytes(":3:", path)
    try:
        to, tt = deep_max_ts(parse(ours)), deep_max_ts(parse(theirs))
    except Exception:
        to = tt = ""
    if to > tt:
        pick, side = ours, "ours"
    elif tt > to:
        pick, side = theirs, "theirs/HEAD"
    else:
        pick, side = (theirs if tie_head else ours), ("tie->HEAD" if
                                                     tie_head else "tie->ours")
    with open(path, "wb") as fh:
        fh.write(pick)
    return f"{path}: {side} (ts {to} vs {tt})"


def resolve_union_json(path, ledger_keys):
    """rolling-ledger: ledger keys union (rows as frozen-JSON identity sets);
    everything else take-new by deep ts."""
    ours, theirs = blob_bytes(":2:", path), blob_bytes(":3:", path)
    o, t = parse(ours), parse(theirs)
    merged = dict(t) if deep_max_ts(t) >= deep_max_ts(o) else dict(o)
    for k in ledger_keys:
        lo = [json.dumps(r, sort_keys=True, ensure_ascii=False)
              for r in o.get(k, [])]
        lt = [json.dumps(r, sort_keys=True, ensure_ascii=False)
              for r in t.get(k, [])]
        union, seen = [], set()
        for line in lo + lt:
            if line not in seen:
                seen.add(line)
                union.append(line)
        merged[k] = [json.loads(x) for x in union]
        print(f"  {path}.{k}: |ours|={len(lo)} |theirs|={len(lt)} "
              f"-> |union|={len(union)}")
    s = json.dumps(merged, ensure_ascii=False, indent=2)
    if theirs.endswith(b"\r\n"):
        s = s.replace("\n", "\r\n")
    if not s.endswith("\n"):
        s += "\r\n" if theirs.endswith(b"\r\n") else "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(s)
    json.loads(open(path, encoding="utf-8").read())
    return f"{path}: ledger-union + take-new state"


def resolve_jsonl(path):
    ours, theirs = blob_bytes(":2:", path), blob_bytes(":3:", path)
    lo = [l for l in ours.decode("utf-8").splitlines() if l.strip()]
    lt = [l for l in theirs.decode("utf-8").splitlines() if l.strip()]
    union, seen = [], set()
    for l in lo + lt:
        if l not in seen:
            seen.add(l)
            union.append(l)
    tail = "\r\n" if ours.endswith(b"\r\n") or theirs.endswith(b"\r\n") \
        else "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(union) + tail if union else tail)
    return f"{path}: line-union {len(lo)}|{len(lt)}->{len(union)}"


def resolve_autofill():
    path = "results/autofill_state.json"
    KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    ours, theirs = blob_bytes(":2:", path), blob_bytes(":3:", path)
    o, t = parse(ours), parse(theirs)
    by_key = {}
    for rec in o.get("launches", []) + t.get("launches", []):
        k = tuple(str(rec.get(f, "")) for f in KEY)
        if k in by_key:
            a, b = by_key[k], rec
            if a == b:
                continue
            fa, fb = set(a), set(b)
            if fa <= fb or fb <= fa:
                by_key[k] = {**a, **b}
                continue
            raise SystemExit(f"FLAG divergence {k}")
        by_key[k] = rec
    launches = sorted(by_key.values(), key=lambda r: str(r.get("ts", "")))
    if len(launches) > 50:
        launches = launches[-50:]
    launches = sorted(launches, key=lambda r: str(r.get("ts", "")))
    ot, tt = o.get("last_tick"), t.get("last_tick")
    def _ts(x):
        return str(x.get("ts", "")) if isinstance(x, dict) else ""
    pick = ot
    if isinstance(tt, dict) and (not isinstance(ot, dict)
                                  or _ts(tt) >= _ts(ot)):
        pick = tt
    merged = dict(t)
    merged["launches"] = launches
    merged["last_tick"] = pick
    assert isinstance(pick, dict)
    s = json.dumps(merged, ensure_ascii=False, indent=2)
    if theirs.endswith(b"\r\n"):
        s = s.replace("\n", "\r\n")
    if not s.endswith("\n"):
        s += "\r\n" if theirs.endswith(b"\r\n") else "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(s)
    json.loads(open(path, encoding="utf-8").read())
    return (f"{path}: launches union->{len(launches)} last_tick "
            f"ours={_ts(ot)} theirs={_ts(tt)} "
            f"pick={'HEAD' if pick is tt else 'ours'}")


def resolve_twin():
    jp = "docs/daily_report/REPORT-2026-09-27.json"
    mp = "docs/daily_report/REPORT-2026-09-27.md"
    ours, theirs = blob_bytes(":2:", jp), blob_bytes(":3:", jp)
    o, t = parse(ours), parse(theirs)
    to, tt = str(o.get("generated_at", "")), str(t.get("generated_at", ""))
    if to >= tt:
        side, jbytes = "ours", ours
    else:
        side, jbytes = "theirs/HEAD", theirs
    with open(jp, "wb") as fh:
        fh.write(jbytes)
    mbytes = blob_bytes(":2:" if side == "ours" else ":3:", mp)
    with open(mp, "wb") as fh:
        fh.write(mbytes)
    return f"{jp}+{mp}: twin side-coupled {side} (gen {to} vs {tt})"


def resolve_js_wrapper():
    path = "results/dashboard_status.js"
    ours, theirs = blob_bytes(":2:", path), blob_bytes(":3:", path)
    to = deep_max_ts(parse(ours[ours.index(b"{"):ours.rindex(b"}") + 1]))
    tt = deep_max_ts(parse(theirs[theirs.index(b"{"):theirs.rindex(b"}") + 1]))
    pick, side = (ours, "ours") if to >= tt else (theirs, "theirs/HEAD")
    with open(path, "wb") as fh:
        fh.write(pick)
    return f"{path}: whole-bytes {side} (ts {to} vs {tt})"


def main():
    # dynamic UU set (never resolve non-conflicted files)
    out = subprocess.run(["git", "ls-files", "-u"], capture_output=True,
                        text=True)
    uu = sorted({l.split("\t", 1)[1].strip() for l in out.stdout.splitlines()
                 if "\t" in l})
    print("UU set:", len(uu))
    ledger = {"results/compute_audit.json": ["history"],
              "results/regime_state.json": ["histories", "transitions"]}
    handled = set()
    log = []
    for p in [x for x in uu
              if x not in ledger and x not in (
                  "results/x2_watch_log.jsonl", "results/autofill_state.json",
                  "docs/daily_report/REPORT-2026-09-27.json",
                  "docs/daily_report/REPORT-2026-09-27.md",
                  "results/dashboard_status.js")]:
        log.append(resolve_snapshot(p))
        handled.add(p)
    for p, keys in ledger.items():
        if p in uu:
            log.append(resolve_union_json(p, keys))
            handled.add(p)
    if "results/x2_watch_log.jsonl" in uu:
        log.append(resolve_jsonl("results/x2_watch_log.jsonl"))
        handled.add("results/x2_watch_log.jsonl")
    if "results/autofill_state.json" in uu:
        log.append(resolve_autofill())
        handled.add("results/autofill_state.json")
    if ("docs/daily_report/REPORT-2026-09-27.json" in uu
            or "docs/daily_report/REPORT-2026-09-27.md" in uu):
        log.append(resolve_twin())
        handled.add("docs/daily_report/REPORT-2026-09-27.json")
        handled.add("docs/daily_report/REPORT-2026-09-27.md")
    if "results/dashboard_status.js" in uu:
        log.append(resolve_js_wrapper())
        handled.add("results/dashboard_status.js")
    missed = [p for p in uu if p not in handled]
    if missed:
        raise SystemExit(f"UNHANDLED UU: {missed}")
    for l in log:
        print(l)


if __name__ == "__main__":
    main()
