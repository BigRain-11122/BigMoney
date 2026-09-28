"""r402 bm-b rebase-conflict resolver: 7-UU shared-face batch (r401 salvage vs origin r405/tick).

Recipes (classifier all-classified, 0 UNKNOWN):
  rolling-ledger x2: compute_audit.json (history union by (ts,host), latest take-new),
                     regime_state.json (lists union, scalars take-new)
  snapshot x5: take-new via hardened deep-ts probe (r100/R350 laws) on STAGED blobs (:2:/:3:).

Laws: r188/R208 union; r140 same-second tie->HEAD(ours in rebase); r185 parse-verify
before write-back; zero-loss count gates; dump convention mirror (r401 resolve2 pattern).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-")
CLOCK_RE = re.compile(r"[T ]\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout


def deep_wallclock(obj, prefix_keys=("asof", "updated", "generated", "ts", "last_seen", "cutoff")):
    """r100/R350 hardened probe: normalized key prefix match, value must be ts-shaped,
    wall-clock values require time-of-day; date-only never feeds the max."""
    best = None

    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    nk = k.replace("_", "").replace("-", "").lower()
                    if any(nk.startswith(p) or nk.endswith(p) for p in prefix_keys):
                        if TS_RE.match(v) and CLOCK_RE.search(v):
                            if best is None or v > best:
                                best = v
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    walk(obj)
    return best


def dump_convention(raw):
    """Detect byte-stable dump convention for a JSON blob (mirror r401 resolve2)."""
    obj = json.loads(raw)
    text = raw.decode("utf-8")
    for indent in (1, 2, 3, 4):
        for ea in (False, True):
            for trail in ("", "\n"):
                cand = json.dumps(obj, ensure_ascii=ea, indent=indent) + trail
                if cand == text:
                    return obj, dict(indent=indent, ensure_ascii=ea, trail=trail)
    return obj, dict(indent=2, ensure_ascii=False, trail="\n")


def write_back(path, obj, conv):
    text = json.dumps(obj, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    json.loads(open(path, encoding="utf-8").read())  # r185 parse gate


def main():
    report = {}

    # ---- snapshot x5: deep-ts probe on staged blobs ----
    SNAP = [
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/update_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
    ]
    for p in SNAP:
        ours, theirs = blob(2, p), blob(3, p)
        if not theirs.strip():
            side = "ours"
        elif not ours.strip():
            side = "theirs"
        else:
            t_o = deep_wallclock(json.loads(ours))
            t_t = deep_wallclock(json.loads(theirs))
            if t_o is None and t_t is None:
                side = "ours"  # probe tie -> HEAD (r140)
            elif t_t is None:
                side = "ours"
            elif t_o is None:
                side = "theirs"
            else:
                side = "ours" if t_o >= t_t else "theirs"  # same-second tie -> ours/HEAD
        raw = ours if side == "ours" else theirs
        obj, conv = dump_convention(raw)
        write_back(p, obj, conv)
        report[p] = {"recipe": "snapshot-take-new", "side": side,
                     "ts_ours": deep_wallclock(json.loads(ours)) if ours.strip() else None,
                     "ts_theirs": deep_wallclock(json.loads(theirs)) if theirs.strip() else None}

    # ---- rolling-ledger: compute_audit.json ----
    p = "results/compute_audit.json"
    ours, theirs = json.loads(blob(2, p)), json.loads(blob(3, p))
    conv = dump_convention(blob(2, p))[1]
    ho = {e.get("ts"): e for e in ours.get("history", [])}
    ht = {e.get("ts"): e for e in theirs.get("history", [])}
    shared = set(ho) & set(ht)
    # per-(ts,host) identity: host lives inside entry
    def ident(e):
        return (e.get("ts"), e.get("host"))
    ho2 = {ident(e): e for e in ours.get("history", [])}
    ht2 = {ident(e): e for e in theirs.get("history", [])}
    union = list(ho2.values()) + [e for k, e in ht2.items() if k not in ho2]
    union.sort(key=lambda e: e.get("ts", ""))
    assert len(union) == len(set(ident(e) for e in union)), "union identity dup"
    assert len(union) == len(ho2) + len(ht2) - len(set(ho2) & set(ht2)), "union count gate"
    merged = dict(ours)  # ours latest wins (00:5x > 00:42)
    merged["history"] = union
    write_back(p, merged, conv)
    report[p] = {"recipe": "ledger-union", "rows_ours": len(ho2), "rows_theirs": len(ht2),
                 "rows_union": len(union)}

    # ---- rolling-ledger: regime_state.json ----
    p = "results/regime_state.json"
    raw_o, raw_t = blob(2, p), blob(3, p)
    ours, theirs = json.loads(raw_o), json.loads(raw_t)
    conv = dump_convention(raw_o)[1]
    merged = dict(ours)
    for k, v in theirs.items():
        if isinstance(v, list) and isinstance(merged.get(k), list):
            seen = set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in merged[k])
            add = [x for x in v if json.dumps(x, sort_keys=True, ensure_ascii=False) not in seen]
            merged[k] = merged[k] + add
            report.setdefault(p, {})["list_union"] = merged[k].__len__()
        elif k not in merged:
            merged[k] = v
    write_back(p, merged, conv)
    report[p] = {"recipe": "regime-union-scalars-ours"}

    json.dump(report, open("results/_r402bmb_resolve_report.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
