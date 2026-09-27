"""R315 bm-b S7 resolver #2: second push-collision window vs bm-a f5eeb473
(round 311, 10:14:54, S6 mirror batch + X2-LD done-flip on their side).

Same recipes as _r315bmb_s7_resolve.py, restricted to the 8 UU files:
snapshots take-newer by internal ts (tie -> :3: mine), compute_audit
history-union + latest newer, token machines per-key union, regime_state
rows-union + scalars newer. Parse-verify before write-back (r185).
"""
import json
import subprocess
import sys


def blob(rev):
    return subprocess.run(["git", "show", rev], capture_output=True,
                          check=True).stdout


def jload(rev):
    return json.loads(blob(rev).decode("utf-8-sig"))


def jdump_mirror(obj, base_raw, path):
    nl = "\r\n" if b"\r\n" in base_raw[:2000] else "\n"
    indent = 1 if base_raw[:200].find(b'\n "') >= 0 else 2
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=indent) + nl)
    return json.load(open(path, encoding="utf-8-sig"))


def union_rows(la, lb):
    seen, out = set(), []
    for e in la + lb:
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def ts_of(d):
    for key in ("ts", "updated", "generated", "asof"):
        if d.get(key):
            return str(d[key])
    return ""


def main():
    notes = []

    # snapshots: take-newer by internal ts, tie -> :3: (mine)
    for p in ["results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json",
              "results/update_status.json",
              "results/prospect_promotion/_summary.json"]:
        a, b = jload(":2:" + p), jload(":3:" + p)
        pick = ":2:" if ts_of(a) > ts_of(b) else ":3:"
        raw = blob(pick + p)
        with open(p, "wb") as fh:
            fh.write(raw)
        json.loads(raw.decode("utf-8-sig"))
        notes.append(f"{p}: take {pick[1:2]} (ts {ts_of(jload(pick + p))})")

    # compute_audit: history union + latest newer
    p = "results/compute_audit.json"
    base_raw = blob(":1:" + p)
    a, b = jload(":2:" + p), jload(":3:" + p)
    hist = union_rows(a.get("history", []), b.get("history", []))
    la, lb = a.get("latest", {}), b.get("latest", {})
    newest = la if ts_of(la) >= ts_of(lb) else lb
    chk = jdump_mirror({"history": hist, "latest": newest}, base_raw, p)
    assert len(chk["history"]) >= max(len(a["history"]), len(b["history"]))
    notes.append(f"{p}: history union -> {len(chk['history'])}, "
                 f"latest ts={ts_of(newest)}")

    # token_usage: machines per-key union + scalars newer
    p = "results/token_usage.json"
    base_raw = blob(":1:" + p)
    a, b = jload(":2:" + p), jload(":3:" + p)
    ma, mb = a.get("machines", {}), b.get("machines", {})
    machines = {}
    for k in sorted(set(ma) | set(mb)):
        va, vb = ma.get(k), mb.get(k)
        if va is None:
            machines[k] = vb
        elif vb is None:
            machines[k] = va
        elif k == "bm-a":
            machines[k] = va
        elif k == "bm-b":
            machines[k] = vb
        else:
            machines[k] = va if ts_of(va) >= ts_of(vb) else vb
    newer = a if ts_of(a) >= ts_of(b) else b
    out = dict(newer)
    out["machines"] = machines
    chk = jdump_mirror(out, base_raw, p)
    assert set(chk["machines"]) == set(machines)
    notes.append(f"{p}: machines union {sorted(set(ma) | set(mb))}")

    # regime_state: rows union + scalars newer
    p = "results/regime_state.json"
    base_raw = blob(":1:" + p)
    a, b = jload(":2:" + p), jload(":3:" + p)
    for key in ("triggers", "history", "transitions"):
        if isinstance(a.get(key), list) or isinstance(b.get(key), list):
            a[key] = union_rows(a.get(key, []), b.get(key, []))
    newest = a if ts_of(a) >= ts_of(b) else b
    chk = jdump_mirror(newest, base_raw, p)
    notes.append(f"{p}: union triggers={len(chk.get('triggers', []))} "
                 f"history={len(chk.get('history', []))}, "
                 f"face {ts_of(newest)}")

    print("r315 S7 resolver #2:")
    for n in notes:
        print("  " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
