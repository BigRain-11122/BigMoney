"""R351 bm-a fold-landing rolling-ledger resolver (compute_audit / regime_state).

Skill canon (rolling-ledger): history union zero-loss (|A|+|B| keyed), state fields take-new
by DEEP ts probe (compute_audit latest.ts / regime_state updated), producer rolling-window
discipline (r85: union shrink vs producer window != loss), face mirror base blob, parse-verify.

Usage: python results/_r351bma_resolve_ledger.py <path> <hist_key> <hist_entry_key> <state_ts_path_dot>
  e.g. python ..._resolve_ledger.py results/compute_audit.json history ts latest.ts
       python ..._resolve_ledger.py results/regime_state.json history asof updated
"""
import json, subprocess, sys

def blob(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={out.returncode}")
    return out.stdout

def deepget(d, dotted):
    cur = d
    for p in dotted.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None  # probe path existence first (r319): missing key = no silent-false
        cur = cur[p]
    return cur

def main(path, hist_key, entry_key, state_ts_path):
    ours_b = blob(":2", path)
    theirs_b = blob(":3", path)
    ours = json.loads(ours_b.decode("utf-8-sig"))
    theirs = json.loads(theirs_b.decode("utf-8-sig"))

    # --- state side by deep ts probe ---
    ots, tts = str(deepget(ours, state_ts_path) or ""), str(deepget(theirs, state_ts_path) or "")
    state_side = ours if ots >= tts else theirs
    side_name = "ours" if state_side is ours else "theirs"
    print(f"state side={side_name} ours_ts={ots!r} theirs_ts={tts!r}")

    # --- history union by entry key ---
    oH = ours.get(hist_key, [])
    tH = theirs.get(hist_key, [])
    pool = {}
    same_key_divergence = []
    for e in oH + tH:
        k = e.get(entry_key)
        if k in pool and pool[k] != e:
            same_key_divergence.append(k)
        pool[k] = e  # same-key later wins divergence check; keep first occurrence otherwise
    # rebuild: keep FIRST occurrence (ours-first), flag true divergence
    pool = {}
    for e in oH + tH:
        k = e.get(entry_key)
        if k not in pool:
            pool[k] = e
        elif pool[k] != e:
            same_key_divergence.append(k)
    merged = sorted(pool.values(), key=lambda e: str(e.get(entry_key, "")))
    print(f"history ours={len(oH)} theirs={len(tH)} union={len(merged)} divergence={sorted(set(same_key_divergence))[:5]}")

    out = dict(state_side)
    out[hist_key] = merged
    # keys only present on the other side (non-ledger) -> carry over
    other = theirs if state_side is ours else ours
    for k, v in other.items():
        if k not in out and k != hist_key:
            out[k] = v

    # --- face mirror base blob (state side) ---
    base_b = ours_b if state_side is ours else theirs_b
    crlf = b"\r\n" in base_b
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if crlf:
        text = text.replace("\n", "\r\n")
    if base_b.endswith(b"\n"):
        text += "\r\n" if crlf else "\n"
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))
    json.loads(open(path, encoding="utf-8").read())  # parse-verify (r185)
    print(f"written {path} hist_union={len(merged)} (zero-loss: |A∪B| keyed by {entry_key})")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
