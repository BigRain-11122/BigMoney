"""r223 rebase-conflict resolver (bm-b) -- 11-UU same-window dual-machine S6
collision (r208 family; bm-a S6 chain vs my round commit 8afa4642).

Per-file recipes (r185/r188/r208/r209/r212/r140 authoritative):
  results/autofill_state.json   rolling ledger -> _r221_af_union tool (launches
                                identity-union cap50, last_tick take-newer dict,
                                base key order, line endings mirror base r223)
  results/compute_audit.json    rolling ledger -> history identity-union
                                zero-loss + latest take-newer (r188/r208)
  results/dashboard_status.js   JS-wrapped snapshot -> take-newer side WHOLE
                                BYTES (never re-serialize the wrapper, r209)
  all other results/*.json       snapshot -> take-newer by embedded ts field
                                (ts/generated/updated/updated_at/now/meta.*),
                                tie -> base (r140)

Full-blob sources only (never marker-block sides -- r220 lesson); parse-
validated BEFORE any git add (r185). Prints per-file winner + union counts.
"""
import json
import subprocess
import sys

sys.path.insert(0, "results")

TS_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "now",
           "last_attempt", "date")


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True,
                          check=True).stdout


def jblob(spec):
    return json.loads(blob(spec).decode("utf-8-sig"))


def stamp(d):
    """Extract comparison ts from a snapshot dict (recursive one level)."""
    for k in TS_KEYS:
        if isinstance(d.get(k), str):
            return d[k]
    meta = d.get("meta")
    if isinstance(meta, dict):
        for k in TS_KEYS:
            if isinstance(meta.get(k), str):
                return meta[k]
    return None


def take_newer_json(path):
    base, inc = jblob(f":2:{path}"), jblob(f":3:{path}")
    sb, si = stamp(base) or "", stamp(inc) or ""
    win = "base" if (not si) or (sb and sb >= si) else "mine"   # tie -> base
    data = base if win == "base" else inc
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    json.loads(payload)                                         # parse-validate
    with open(path, "wb") as f:
        f.write((payload + "\n").encode("utf-8"))
    print(f"{path}: take-newer -> {win} (base {sb} vs mine {si})")


def take_newer_whole_bytes(path):
    """JS-wrapped snapshot: whole-side bytes, no re-serialization (r209)."""
    bb, ib = blob(f":2:{path}"), blob(f":3:{path}")
    def inner_ts(b):
        s = b.decode("utf-8-sig")
        i, j = s.find("{"), s.rfind("}")
        return stamp(json.loads(s[i:j + 1])) or ""
    sb, si = inner_ts(bb), inner_ts(ib)
    win = "base" if (not si) or (sb and sb >= si) else "mine"
    with open(path, "wb") as f:
        f.write(bb if win == "base" else ib)
    print(f"{path}: take-newer WHOLE BYTES -> {win} (base {sb} vs mine {si})")


def union_compute_audit(path):
    base, inc = jblob(f":2:{path}"), jblob(f":3:{path}")
    seen, merged = set(), []
    for e in base.get("history", []) + inc.get("history", []):
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k in seen:
            continue
        seen.add(k)
        merged.append(e)
    out = {k: base[k] for k in base}                # base key order (r209)
    out["history"] = merged
    lb, li = stamp(base.get("latest", {})) or "", stamp(inc.get("latest", {})) or ""
    out["latest"] = base["latest"] if (not li) or (lb and lb >= li) else inc["latest"]
    payload = json.dumps(out, ensure_ascii=False, indent=1)
    json.loads(payload)
    with open(path, "wb") as f:
        f.write((payload + "\n").encode("utf-8"))
    print(f"{path}: history union {len(base.get('history', []))}+"
          f"{len(inc.get('history', []))}->{len(merged)} | latest -> "
          f"{'base' if out['latest'] is base['latest'] else 'mine'} ({lb} vs {li})")


if __name__ == "__main__":
    union_compute_audit("results/compute_audit.json")
    take_newer_whole_bytes("results/dashboard_status.js")
    for p in ("results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json", "results/heat_update_status.json",
              "results/lhb_update_status.json", "results/regime_state.json",
              "results/token_usage.json", "results/update_status.json"):
        take_newer_json(p)
    print("resolver done (autofill_state handled by _r221_af_union tool)")
