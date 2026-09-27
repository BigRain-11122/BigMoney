"""R315 bm-b S7 push-collision resolver (rebase replay of 1e515f13 vs bm-a
dc69716f/21d33e44 window, dual-machine S6 mirror batch, r246/r283 family).

Stages mid-rebase: :1: = merge base, :2: = ours = origin/bm-a face (10:06),
:3: = theirs = my replayed commit face (10:1x). Recipes per skill table:
  - byte take-side: dashboard_status.js/.json + scorecard_v1.json +
    strategy_scorecard.json + fundamental_b_layer_filter.json -> take :2:
    (bm-a s4-wired derivations, content-newer; my 10:15 face ran old code);
    futures/heat/lhb/update_status.json -> take :3: (newer internal ts,
    semantically identical no-op faces).
  - compute_audit.json: history union by ts (rolling ledger) + latest
    take-newer.
  - token_usage.json: machines per-key union, per-machine authority (bm-a
    key from bm-a face, bm-b key from bm-b face) + scalars newer.
  - regime_state.json: triggers/history union + scalars take-newer.
  - HANDOVER.md: my full text (anchor chain superset) + bm-a-added tail
    rows (vs :1: base) inserted before my r315 row, dedup-safe.
Parse-verify before write-back (r185); newline mirror base blob (r223).
"""
import json
import subprocess
import sys

ROOT = "."


def blob_bytes(rev):
    return subprocess.run(["git", "show", rev], capture_output=True,
                          check=True).stdout


def jload(rev):
    return json.loads(blob_bytes(rev).decode("utf-8-sig"))


def jdump_mirror(obj, base_raw, path):
    nl = "\r\n" if b"\r\n" in base_raw[:2000] else "\n"
    indent = 1 if base_raw[:200].find(b'\n "') >= 0 else 2
    text = json.dumps(obj, ensure_ascii=False, indent=indent)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + nl)
    return json.load(open(path, encoding="utf-8-sig"))


def take_byte(rev, path):
    raw = blob_bytes(rev)
    with open(path, "wb") as fh:
        fh.write(raw)
    if path.endswith(".json"):
        json.loads(raw.decode("utf-8-sig"))  # parse-verify
    return len(raw)


def union_rows(la, lb, ts_key="ts"):
    seen, out = set(), []
    for e in la + lb:
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def main():
    notes = []

    # [A] byte take-side files
    for path, side in [
        ("results/dashboard_status.js", ":2:"),
        ("results/dashboard_status.json", ":2:"),
        ("results/scorecard_v1.json", ":2:"),
        ("results/strategy_scorecard.json", ":2:"),
        ("results/fundamental_b_layer_filter.json", ":2:"),
        ("results/futures_update_status.json", ":3:"),
        ("results/heat_update_status.json", ":3:"),
        ("results/lhb_update_status.json", ":3:"),
        ("results/update_status.json", ":3:"),
    ]:
        n = take_byte(side + path, path)
        notes.append(f"{path}: take {side[1:2]} byte ({n}B)")

    # [B] compute_audit.json: history union + latest take-newer
    p = "results/compute_audit.json"
    base_raw = blob_bytes(":1:" + p)
    a, b = jload(":2:" + p), jload(":3:" + p)
    hist = union_rows(a.get("history", []), b.get("history", []))
    la, lb = a.get("latest", {}), b.get("latest", {})
    newest = la if str(la.get("ts", "")) >= str(lb.get("ts", "")) else lb
    chk = jdump_mirror({"history": hist, "latest": newest}, base_raw, p)
    assert len(chk["history"]) >= max(len(a["history"]), len(b["history"]))
    notes.append(f"{p}: history union {len(a['history'])}|{len(b['history'])}"
                 f"->{len(chk['history'])}, latest ts={newest.get('ts')}")

    # [C] token_usage.json: per-key machines union + scalars newer
    p = "results/token_usage.json"
    base_raw = blob_bytes(":1:" + p)
    a, b = jload(":2:" + p), jload(":3:" + p)
    ma, mb = a.get("machines", {}), b.get("machines", {})
    machines = {}
    for k in sorted(set(ma) | set(mb)):
        va, vb = ma.get(k), mb.get(k)
        if va is None:
            machines[k] = vb
        elif vb is None:
            machines[k] = va
        elif k == "bm-a":            # per-machine authority
            machines[k] = va
        elif k == "bm-b":
            machines[k] = vb
        else:
            ta = str(va.get("generated", va.get("ts", "")))
            tb = str(vb.get("generated", vb.get("ts", "")))
            machines[k] = va if ta >= tb else vb
    newer = a if str(a.get("generated", "")) >= str(b.get("generated", "")) \
        else b
    out = dict(newer)
    out["machines"] = machines
    chk = jdump_mirror(out, base_raw, p)
    assert set(chk["machines"]) == set(machines)
    notes.append(f"{p}: machines union {sorted(set(ma) | set(mb))}, "
                 f"scalars generated={newer.get('generated')}")

    # [D] regime_state.json: triggers/history union + scalars newer
    p = "results/regime_state.json"
    base_raw = blob_bytes(":1:" + p)
    a, b = jload(":2:" + p), jload(":3:" + p)
    for key in ("triggers", "history", "transitions"):
        if isinstance(a.get(key), list) or isinstance(b.get(key), list):
            a[key] = union_rows(a.get(key, []), b.get(key, []))
    ta, tb = str(a.get("updated", a.get("asof", ""))), \
        str(b.get("updated", b.get("asof", "")))
    newest = a if ta >= tb else b
    chk = jdump_mirror(newest, base_raw, p)
    notes.append(f"{p}: triggers {len(chk.get('triggers', []))} "
                 f"history {len(chk.get('history', []))} union, "
                 f"state face updated={newest.get('updated')} "
                 f"({':2:' if newest is a else ':3:'} side)")

    # [E] HANDOVER.md: my text + bm-a-added tail rows before my r315 row
    p = "research/HANDOVER.md"
    base = blob_bytes(":1:" + p).decode("utf-8-sig")
    a_txt = blob_bytes(":2:" + p).decode("utf-8-sig")
    m_txt = blob_bytes(":3:" + p).decode("utf-8-sig")
    base_lines = base.splitlines()
    a_lines = a_txt.splitlines()
    m_lines = m_txt.splitlines()
    base_set = set(base_lines)
    added = [ln for ln in a_lines if ln not in base_set and ln.strip()]
    assert len(added) <= 4, f"unexpected bm-a additions: {added[:4]}"
    m_set = set(m_lines)
    new_added = [ln for ln in added if ln not in m_set]
    nl = "\r\n" if b"\r\n" in blob_bytes(":3:" + p)[:4000] else "\n"
    if new_added:
        insert_at = len(m_lines)
        while insert_at > 0 and not m_lines[insert_at - 1].strip():
            insert_at -= 1
        for ln in new_added:
            m_lines.insert(insert_at, ln)
            insert_at += 1
    text = nl.join(m_lines) + nl
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    chk = open(p, encoding="utf-8-sig").read()
    for ln in new_added:
        assert ln in chk, f"lost bm-a line: {ln[:60]}"
    assert "最近核对=bm-b round 315" in chk
    notes.append(f"{p}: bm-a added rows inserted {len(new_added)} "
                 f"(skipped dup {len(added) - len(new_added)})")

    print("r315 S7 resolver:")
    for n in notes:
        print("  " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
