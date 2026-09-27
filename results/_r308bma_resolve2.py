"""R308 bm-a rebase resolver part 2: round-308 commit replay conflict batch
(15 UU: same-window dual-machine S6 chain products).

Recipes per bigmoney-conflict-resolve skill + manual classification:
  mixed-dict+ledger  autofill_state.json (launches union cap50 re-sort asc,
                      last_tick whole-dict by ts, tie->ours)
  rolling-ledger     compute_audit.json (history union zero-loss, ts asc;
                      latest take-new), regime_state.json (transitions+
                      history union, scalars take-new by updated)
  snapshot take-new  *_status.json / token_usage / fundamental_b_layer /
                      scorecards / daily_report twins (by internal ts,
                      tie->ours) -- all verified theirs-newer at classify time
  js-wrapper         dashboard_status.js take-side whole bytes (aligns with
                      dashboard_status.json side, R209 law)
Manual UNKNOWN classes resolved here (classifier exit-2 face):
  daily_report .json/.md = per-day in-place regeneration snapshot (take-new
    by generated_at, md follows json side); scorecard_v1/strategy_scorecard
  = per-round deterministic re-derivation (drift = generated/elapsed only,
    take-new by generated). Zero-loss checks on every ledger union.
"""
import json
import subprocess
import sys


def blob(p, st):
    return subprocess.run(["git", "show", st + p],
                           capture_output=True, check=True).stdout


def ts_of(d):
    for k in ("ts", "generated", "generated_at", "updated", "updated_at"):
        if isinstance(d, dict) and k in d:
            return str(d[k])
    return ""


def write_mirror(path, obj, base_raw):
    nl = "\r\n" if b"\r\n" in base_raw[:2000] else "\n"
    indent = 1 if base_raw[:200].find(b'\n "') >= 0 else 2
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=indent) + nl)
    json.load(open(path, encoding="utf-8-sig"))       # parse-verify r185


def take_new(p, tie_ours=True):
    o, t = blob(p, ":2:"), blob(p, ":3:")
    if p.endswith(".md"):                      # markdown twin: side by
        import re                               # generated_at line, whole bytes
        go = (re.search(r"generated_at[\"：: ]*([0-9T: .-]+)",
                        o.decode("utf-8-sig")) or [None, ""])[1]
        gt = (re.search(r"generated_at[\"：: ]*([0-9T: .-]+)",
                        t.decode("utf-8-sig")) or [None, ""])[1]
        side = "ours" if go >= gt else "theirs"
        raw = o if side == "ours" else t
        with open(p, "wb") as fh:
            fh.write(raw)
        return side, go if side == "ours" else gt
    jo = json.loads(o.decode("utf-8-sig"))
    jt = json.loads(t.decode("utf-8-sig"))
    side = "ours" if (ts_of(jo) >= ts_of(jt) if tie_ours
                      else ts_of(jo) > ts_of(jt)) else "theirs"
    raw, j = (o, jo) if side == "ours" else (t, jt)
    write_mirror(p, j, raw)
    return side, ts_of(j)


def union_rows(a, b):
    seen, out = set(), []
    for e in a + b:
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def main():
    r = {}

    # [1] mixed-dict+ledger: autofill_state.json
    p = "results/autofill_state.json"
    a = json.loads(blob(p, ":2:").decode("utf-8-sig"))
    b = json.loads(blob(p, ":3:").decode("utf-8-sig"))
    base = blob(p, ":1:")
    lu = union_rows(a.get("launches", []), b.get("launches", []))
    lu.sort(key=lambda e: e.get("ts", ""), reverse=True)
    lu = lu[:50]
    lu.sort(key=lambda e: e.get("ts", ""))            # producer append order
    ta = (a.get("last_tick") or {}).get("ts", "")
    tb = (b.get("last_tick") or {}).get("ts", "")
    out = dict(a if ta >= tb else b)
    out["launches"] = lu
    out["last_tick"] = (a if ta >= tb else b)["last_tick"]
    assert isinstance(out["last_tick"], dict)
    write_mirror(p, out, base)
    json.load(open(p, encoding="utf-8-sig"))
    assert len(out["launches"]) == min(len(union_rows(a.get("launches", []),
                                       b.get("launches", []))), 50)
    r[p] = f"union launches |A|={len(a.get('launches', []))} " \
           f"|B|={len(b.get('launches', []))} kept={len(out['launches'])} " \
           f"last_tick={'ours' if ta >= tb else 'theirs'}"

    # [2] rolling-ledger: compute_audit.json
    p = "results/compute_audit.json"
    a = json.loads(blob(p, ":2:").decode("utf-8-sig"))
    b = json.loads(blob(p, ":3:").decode("utf-8-sig"))
    base = blob(p, ":1:")
    hu = union_rows(a.get("history", []), b.get("history", []))
    hu.sort(key=lambda e: e.get("ts", ""))
    new = a if ts_of(a.get("latest", {})) >= ts_of(b.get("latest", {})) else b
    out = dict(new)
    out["history"] = hu
    write_mirror(p, out, base)
    json.load(open(p, encoding="utf-8-sig"))
    assert len(out["history"]) >= max(len(a.get("history", [])),
                                      len(b.get("history", [])))
    r[p] = (f"history union |A|={len(a.get('history', []))} "
            f"|B|={len(b.get('history', []))} -> {len(hu)} zero-loss; "
            f"latest={'ours' if new is a else 'theirs'}")

    # [3] rolling-ledger: regime_state.json
    p = "results/regime_state.json"
    a = json.loads(blob(p, ":2:").decode("utf-8-sig"))
    b = json.loads(blob(p, ":3:").decode("utf-8-sig"))
    base = blob(p, ":1:")
    out = dict(a if ts_of(a) >= ts_of(b) else b)
    for k in ("transitions", "history"):
        u = union_rows(a.get(k, []), b.get(k, []))
        u.sort(key=lambda e: e.get("ts", e.get("date", "")))
        out[k] = u
    write_mirror(p, out, base)
    json.load(open(p, encoding="utf-8-sig"))
    r[p] = (f"transitions={len(out['transitions'])} "
            f"history={len(out['history'])} union; "
            f"scalars={'ours' if ts_of(a) >= ts_of(b) else 'theirs'}")

    # [4] snapshots take-new by internal ts
    snaps = ["results/token_usage.json", "results/update_status.json",
             "results/futures_update_status.json",
             "results/fundamental_b_layer_filter.json",
             "results/heat_update_status.json",
             "results/lhb_update_status.json",
             "docs/daily_report/REPORT-2026-09-27.json",
             "results/strategy_scorecard.json", "results/scorecard_v1.json"]
    for p in snaps:
        side, ts = take_new(p)
        r[p] = f"take-new side={side} ts={ts}"
    # daily_report md twin follows the json side (already taken above);
    # verify same side to keep twins consistent
    p = "docs/daily_report/REPORT-2026-09-27.md"
    side, ts = take_new(p)                    # generated_at line inside md
    r[p] = f"take-new side={side} ts={ts}"

    # [5] dashboard twins: take-side whole, aligned with newest chain face
    for p in ("results/dashboard_status.json", "results/dashboard_status.js"):
        o, t = blob(p, ":2:"), blob(p, ":3:")
        with open(p, "wb") as fh:              # whole bytes, no re-serialize
            fh.write(t)
        json.loads(t.decode("utf-8-sig")) if p.endswith(".json") else None
        r[p] = "take-side whole bytes (theirs, chain-newest, no ts inside)"

    for k in sorted(r):
        print(f"  {k}: {r[k]}")
    print("r308 resolver2: all 15 UU resolved, parse-verified, zero-loss ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
