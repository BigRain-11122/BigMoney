# -*- coding: utf-8 -*-
"""R263 bm-a -- rebase 14-UU resolver (bm-b r265 chain vs my 263f S6
commit) per bigmoney-conflict-resolve skill recipes.

Stage faces during THIS rebase (replay of my 263f onto origin/main
fa012689): stage :2 = ours = origin/bm-b side, stage :3 = theirs = my
263f side. All take-new comparisons are direction-agnostic (ts probe).

Recipes:
  * compute_audit.json      rolling-ledger: history union by ts (zero
                            loss, ts-asc) + latest take-new by nested ts
  * regime_state.json      rolling-ledger: transitions union identity +
                            fields take-new by ts
  * autofill_state.json    mixed-dict+ledger: launches union -> cap 50
                            (keep newest) -> RE-SORT ts ASC before
                            write-back (r245 write-order law); last_tick
                            by internal ts dict-compare (same-sec tie =
                            HEAD); byte faces mirrored from origin blob
  * dashboard_status.js    js-wrapper: whole-byte take-side by
                            meta.generated_at
  * dashboard_status.json / *_update_status.json /
    fundamental_b_layer_filter.json / token_usage.json /
    update_status.json / daily_scorecard.json
                           snapshot: take-new whole doc by ts-key probe
  * REPORT-2026-09-26 pair   same-day regenerated snapshot (r242
                            precedent): json twin generated_at governs,
                            md same-side whole bytes
Parse-verify before every write (r185). Zero loss asserted for ledger
unions. Exit 0; 2 on any refusal.
"""
import json
import subprocess
import sys

TS_KEYS = ("ts", "updated", "updated_at", "generated", "generated_at",
           "as_of", "last_attempt", "last_run", "written_at")


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True, check=True)
    return r.stdout


def probe_ts(obj):
    """Depth-2 ts probe over candidate keys; returns best (key, val)."""
    best = None
    def scan(d, depth):
        nonlocal best
        if not isinstance(d, dict) or depth > 2:
            return
        for k in TS_KEYS:
            v = d.get(k)
            if isinstance(v, str) and len(v) >= 10:
                if best is None or v > best[1]:
                    best = (k, v)
        for v in d.values():
            scan(v, depth + 1)
    scan(obj, 0)
    return best


def write_faces(path, payload, origin_bytes):
    """Mirror origin byte faces: LF, indent probed, trailing newline
    probed, raw UTF-8 (ensure_ascii probed via \\u scan)."""
    txt = origin_bytes.decode("utf-8")
    indent = 1
    for line in txt.splitlines():
        if line.startswith(" "):
            indent = len(line) - len(line.lstrip(" "))
            break
    ensure_ascii = ("\\u" in txt)
    out = json.dumps(payload, ensure_ascii=ensure_ascii, indent=indent,
                     default=str)
    if txt.endswith("\n"):
        out += "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    json.loads(open(path, encoding="utf-8").read())       # r185 verify


def resolve_take_new(path):
    o, t = blob(2, path), blob(3, path)
    jo, jt = json.loads(o), json.loads(t)
    po, pt = probe_ts(jo), probe_ts(jt)
    if po and pt:
        side = t if pt[1] > po[1] else o          # strictly newer wins
        why = f"ts {pt[1] if pt[1] > po[1] else po[1]}"
    elif po and not pt:
        side, why = o, "theirs lacks ts -> ours kept"
    elif pt and not po:
        side, why = t, "ours lacks ts -> theirs kept"
    else:
        print(f"UNKNOWN ts face both sides: {path} -> manual required")
        return False
    write_faces(path, json.loads(side), o if side is o else t)
    print(f"  take-new {path}: {why}")
    return True


def resolve_audit(path):
    o, t = json.loads(blob(2, path)), json.loads(blob(3, path))
    ho, ht = o.get("history", []), t.get("history", [])
    union = {e.get("ts"): e for e in ho}
    for e in ht:
        union.setdefault(e.get("ts"), e)
    merged = sorted(union.values(), key=lambda e: e.get("ts"))
    assert len(merged) >= max(len(ho), len(ht)), "union loss"
    lo, lt = o.get("latest", {}), t.get("latest", {})
    latest = (lt if (lt.get("ts") or "") > (lo.get("ts") or "")
              else lo)
    out = dict(o)
    out.update({k: v for k, v in t.items()
                if k not in ("history", "latest") and k not in out})
    out["history"] = merged
    out["latest"] = latest
    write_faces(path, out, blob(2, path))
    print(f"  union {path}: history {len(ho)}|{len(ht)}->{len(merged)} "
          f"ts-asc; latest take-new {latest.get('ts')}")
    return True


def resolve_regime(path):
    o, t = json.loads(blob(2, path)), json.loads(blob(3, path))
    to, tt = o.get("transitions", []), t.get("transitions", [])
    seen, merged = set(), []
    for e in to + tt:
        key = json.dumps(e, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            merged.append(e)
    merged.sort(key=lambda e: e.get("ts", ""))
    out = dict(o)
    for k, v in t.items():
        if k != "transitions" and k not in out:
            out[k] = v
    po, pt = probe_ts(o), probe_ts(t)
    if pt and (not po or pt[1] > po[1]):
        for k in ("state", "verdict", "checked_at", "updated"):
            if k in t:
                out[k] = t[k]
    out["transitions"] = merged
    assert len(merged) >= max(len(to), len(tt)), "union loss"
    write_faces(path, out, blob(2, path))
    print(f"  union {path}: transitions {len(to)}|{len(tt)}"
          f"->{len(merged)}; fields take-new")
    return True


def resolve_autofill(path):
    o_b, t_b = blob(2, path), blob(3, path)
    o, t = json.loads(o_b), json.loads(t_b)
    lo, lt = o.get("launches", []), t.get("launches", [])
    union = {json.dumps(e, sort_keys=True, default=str): e
             for e in lo}
    for e in lt:
        union.setdefault(json.dumps(e, sort_keys=True, default=str), e)
    newest = sorted(union.values(),
                    key=lambda e: e.get("ts", ""), reverse=True)[:50]
    newest.sort(key=lambda e: e.get("ts", ""))     # ASC write-back (r245)
    to, tt = o.get("last_tick", {}), t.get("last_tick", {})
    last_tick = (tt if isinstance(tt, dict)
                 and (tt.get("ts") or "") > (to.get("ts") or "")
                 else to) if isinstance(to, dict) else tt
    assert isinstance(last_tick, dict), "last_tick not a dict"
    out = dict(o)
    for k, v in t.items():
        if k not in ("launches", "last_tick") and k not in out:
            out[k] = v
    out["launches"] = newest
    out["last_tick"] = last_tick
    write_faces(path, out, o_b)
    print(f"  mixed {path}: launches {len(lo)}|{len(tt and lt)}->"
          f"{len(newest)} (cap50, ASC write-back); last_tick ts="
          f"{last_tick.get('ts')}")
    return True


def resolve_js_wrapper(path):
    import re
    o_b, t_b = blob(2, path), blob(3, path)

    def gen(b):
        m = re.search(rb'"generated_at"\s*:\s*"([^"]+)"', b)
        return m.group(1).decode() if m else None
    go, gt = gen(o_b), gen(t_b)
    if go and gt:
        side = t_b if gt > go else o_b
        why = f"generated_at {gt} vs {go}"
    elif gt:
        side, why = t_b, "ours lacks generated_at"
    elif go:
        side, why = o_b, "theirs lacks generated_at"
    else:
        print(f"UNKNOWN generated_at both sides: {path}")
        return False
    with open(path, "wb") as fh:
        fh.write(side)
    json.loads(re.search(r"=\s*(\{.*\})\s*;?\s*$",
                         side.decode("utf-8"),
                         re.S).group(1))          # r185 verify
    print(f"  js take-side {path}: {why}")
    return True


def resolve_report_pair(jpath, mpath):
    jo, jt = json.loads(blob(2, jpath)), json.loads(blob(3, jpath))
    po, pt = probe_ts(jo), probe_ts(jt)
    take_theirs = bool(pt and (not po or pt[1] > po[1]))
    why = f"json ts {pt[1] if pt else None} vs {po[1] if po else None}"
    jb = blob(3 if take_theirs else 2, jpath)
    mb = blob(3 if take_theirs else 2, mpath)
    json.loads(jb)                                  # r185 verify
    with open(jpath, "wb") as fh:
        fh.write(jb)
    with open(mpath, "wb") as fh:
        fh.write(mb)
    side = "theirs(mine)" if take_theirs else "ours(bm-b)"
    print(f"  report pair take-{side}: {why} (md same-side whole bytes)")
    return True


def main():
    ok = True
    ok &= resolve_audit("results/compute_audit.json")
    ok &= resolve_regime("results/regime_state.json")
    ok &= resolve_autofill("results/autofill_state.json")
    ok &= resolve_js_wrapper("results/dashboard_status.js")
    for p in ("results/dashboard_status.json",
              "results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json",
              "results/fundamental_b_layer_filter.json",
              "results/token_usage.json",
              "results/update_status.json",
              "results/daily_scorecard.json"):
        ok &= resolve_take_new(p)
    ok &= resolve_report_pair("docs/daily_report/REPORT-2026-09-26.json",
                              "docs/daily_report/REPORT-2026-09-26.md")
    print("resolver:", "OK" if ok else "REFUSED")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
