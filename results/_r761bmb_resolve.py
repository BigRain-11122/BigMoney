# r761 bm-b rebase conflict resolver (S7 push-rejection path, skill-sanctioned).
# Lineage: bigmoney-conflict-resolve SKILL recipes; classifier output r761 (18 classified
# + 1 manual: _attrition_guard_scan.json = per-run scan snapshot -> take-new by ts).
# Rebase stage semantics: :2: = ours = upstream (origin side), :3: = theirs = replayed
# local commit. Idempotent: re-run per conflicted replay step; probes staged blobs only.
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sh(args):
    r = subprocess.run(args, capture_output=True)
    return r.stdout

def blob(spec):
    return sh(["git", "show", spec])

def conflicted():
    out = sh(["git", "diff", "--name-only", "--diff-filter=U"]).decode("utf-8", "replace")
    return [l for l in out.splitlines() if l.strip()]

TS_PREFIXES = ("generated", "updated", "asof", "ts", "stateupdated", "lasttick",
               "clock", "now", "scanned", "ran", "generatedat", "generated_at")

def deep_ts(o, path=""):
    """r100/R350 hardened probe: normalized key prefix, ^20\\d{2}- shape, time-of-day required."""
    best = None
    if isinstance(o, dict):
        for k, v in o.items():
            nk = re.sub(r"[_\-]", "", k).lower()
            if isinstance(v, str) and re.match(r"^20\d{2}-", v) \
                    and re.search(r"[T ]\d{2}:\d{2}", v) \
                    and any(nk.startswith(p.replace("_", "")) for p in TS_PREFIXES):
                if best is None or v > best[0]:
                    best = (v, path + "/" + k)
            r = deep_ts(v, path + "/" + k)
            if r and (best is None or r[0] > best[0]):
                best = r
    elif isinstance(o, list):
        for i, v in enumerate(o[:5]):
            r = deep_ts(v, path + "/%d" % i)
            if r and (best is None or r[0] > best[0]):
                best = r
    return best

def ident(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

def entry_ts(e):
    if isinstance(e, dict):
        for k in ("ts", "updated", "at", "time", "datetime"):
            v = e.get(k)
            if isinstance(v, str) and re.match(r"^20\d{2}-", v):
                return v
    return None

def resolve_ledger(path, a_raw, b_raw):
    """union list keys (A + B-minus-A, identity dedupe), then re-sort ts-ascending keys that
    were ascending on the newer side; non-list fields from newer-ts side. indent-2 mirror."""
    A, B = json.loads(a_raw), json.loads(b_raw)
    ta, tb = deep_ts(A), deep_ts(B)
    newer = A if (ta and (not tb or ta[0] >= tb[0])) else B
    merged = {}
    for k, v in newer.items():
        if isinstance(v, list):
            other = (B if newer is A else A).get(k, [])
            seen = set(ident(e) for e in v)
            union = list(v) + [e for e in other if ident(e) not in seen]
            # preserve producer chronology: re-sort only if A-side was verifiably ascending
            tss = [entry_ts(e) for e in v]
            if tss and all(t is not None for t in tss) \
                    and all(tss[i] <= tss[i + 1] for i in range(len(tss) - 1)):
                union.sort(key=lambda e: (entry_ts(e) or ""))
            merged[k] = union
        else:
            merged[k] = v
    out = json.dumps(merged, ensure_ascii=False, indent=2)
    if (a_raw.rstrip(b"\n") != a_raw) or (b_raw.rstrip(b"\n") != b_raw):
        out += "\n"
    return out.encode("utf-8"), {"class": "rolling-ledger", "ts_A": ta, "ts_B": tb,
                                 "side_state": "A" if newer is A else "B"}

def take_side(path, a_raw, b_raw, forced=None):
    """snapshot take-new by hardened deep-ts probe (whole bytes verbatim)."""
    try:
        ta = deep_ts(json.loads(a_raw))
        tb = deep_ts(json.loads(b_raw))
    except Exception:
        ta = tb = None
    if forced in ("A", "B"):
        side = forced
    elif ta and (not tb or ta[0] >= tb[0]):
        side = "A"
    elif tb:
        side = "B"
    else:
        return None, {"class": "snapshot", "error": "NO_TS_BOTH_SIDES - manual review"}
    return (a_raw if side == "A" else b_raw), {"class": "snapshot", "ts_A": ta, "ts_B": tb,
                                               "side": side}

def resolve_codely(a_raw, b_raw):
    """memory-union strict recipe: merge-base prefix-identity assertion on BOTH sides,
    then direct-concat suffixes: new = base + A-suffix + B-suffix (R208/r212/r311)."""
    rh = sh(["git", "rev-parse", "REBASE_HEAD"]).decode().strip()
    base_spec = (rh + "^:CODELY.md") if rh else "99329b49f:CODELY.md"
    base = blob(base_spec)
    ok_a = a_raw.startswith(base)
    ok_b = b_raw.startswith(base)
    if not (ok_a and ok_b):
        return None, {"class": "memory-union", "base_spec": base_spec, "prefix_A": ok_a,
                      "prefix_B": ok_b, "error": "PREFIX-IDENTITY FAIL - manual review"}
    new = base + a_raw[len(base):] + b_raw[len(base):]
    exp = len(base) + (len(a_raw) - len(base)) + (len(b_raw) - len(base))
    return new, {"class": "memory-union", "base_bytes": len(base), "A_suffix": len(a_raw) - len(base),
                 "B_suffix": len(b_raw) - len(base), "new_bytes": len(new),
                 "byte_math": (len(new) == exp), "base_spec": base_spec}

TWIN_JSON_FOR = {
    "docs/daily_report/REPORT-2026-10-06.md": "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md": "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
LEDGERS = {"results/compute_audit.json", "results/regime_state.json"}
SNAPSHOTS = {
    "results/_attrition_guard_scan.json",  # manual class (classifier UNKNOWN): per-run scan snapshot
    "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/lhb_update_status.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/token_usage.json", "results/update_status.json",
    "docs/daily_report/REPORT-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.json",
}

def main():
    files = conflicted()
    if not files:
        print(json.dumps({"status": "NO_CONFLICTS"}))
        return 0
    receipt = {"status": "OK", "resolved": {}, "unresolved": []}
    twin_side = {}
    # pass 1: json snapshots decide sides (twins consume the decision)
    for f in files:
        a_raw = blob(":2:" + f)
        b_raw = blob(":3:" + f)
        if f in LEDGERS:
            data, meta = resolve_ledger(f, a_raw, b_raw)
        elif f == "CODELY.md":
            data, meta = resolve_codely(a_raw, b_raw)
        elif f in SNAPSHOTS:
            data, meta = take_side(f, a_raw, b_raw)
            if data is not None and f in TWIN_JSON_FOR.values():
                twin_side[f] = meta.get("side")
        elif f in TWIN_JSON_FOR:
            continue  # pass 2
        else:
            receipt["unresolved"].append({"path": f, "error": "UNCLASSIFIED - manual"})
            continue
        if data is None:
            receipt["unresolved"].append({"path": f, **meta})
            continue
        # verify parse-ability for json faces before write-back (r185 law)
        if f.endswith(".json"):
            json.loads(data.decode("utf-8"))
        with open(os.path.join(BASE, f), "wb") as fh:
            fh.write(data)
        sh(["git", "add", "--", f])
        receipt["resolved"][f] = meta
    # pass 2: twins take the SAME side as their json twin (js/md verbatim bytes)
    import re as _re
    def text_gen_ts(raw):
        """text-level generated-ts probe for md/js twins (twin json stages already cleared).
        CJK producers use auto-generated markers -> fallback = max full datetime in file."""
        cands = []
        for m in _re.finditer(rb"generat(?:ed|ed_at|ion)", raw):
            window = raw[m.end():m.end() + 60]
            for t in _re.findall(rb"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", window):
                cands.append(t.decode())
        if not cands:
            cands = [t.decode() for t in
                     _re.findall(rb"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", raw)]
        return max(cands) if cands else None
    for f in files:
        if f not in TWIN_JSON_FOR:
            continue
        j = TWIN_JSON_FOR[f]
        side = twin_side.get(j)
        if side is None:
            fa, fb = blob(":2:" + f), blob(":3:" + f)
            ta, tb = text_gen_ts(fa), text_gen_ts(fb)
            if ta and (not tb or ta >= tb):
                side = "A"
            elif tb:
                side = "B"
        if side is None:
            receipt["unresolved"].append({"path": f, "error": "TWIN side undecidable"})
            continue
        raw = blob((":2:" if side == "A" else ":3:") + f)
        with open(os.path.join(BASE, f), "wb") as fh:
            fh.write(raw)
        sh(["git", "add", "--", f])
        receipt["resolved"][f] = {"class": "twin-verbatim", "side": side, "twin": j}
    receipt["unresolved_count"] = len(receipt["unresolved"])
    print(json.dumps(receipt, ensure_ascii=False))
    return 2 if receipt["unresolved"] else 0

if __name__ == "__main__":
    sys.exit(main())
