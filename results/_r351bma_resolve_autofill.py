"""R351 bm-a fold-landing autofill_state UU resolver (reusable across replay stops).

Skill canon (mixed-dict+ledger):
- launches: union -> composite-key (ts,machine,pid,runner_sha256,entry,shard) dedup BEFORE cap
  (same-key pair: field-set diff = supplementary only -> field-union merge keep one;
   true divergence -> FLAG escalate, no silent double-keep)
  -> sort ts desc -> cap 50 -> re-sort ts asc for write-back (producer append order)
- last_tick: compare by internal ts (str->dict first), newer wins; same-second tie -> HEAD (ours)
- face mirror: base blob (ours) byte-tail/indent detection, newline translation mode on write
- post: json.loads + isinstance(last_tick, dict) assert

Usage: python results/_r351bma_resolve_autofill.py <path>
Reads stage blobs :2: (ours/HEAD) and :3: (theirs) via `git show`, writes union, prints report.
"""
import json, subprocess, sys

CAP = 50
KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")

def blob(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={out.returncode} {out.stderr[:200]!r}")
    return out.stdout  # bytes

def main(path):
    ours_b = blob(":2", path)
    theirs_b = blob(":3", path)
    ours = json.loads(ours_b.decode("utf-8-sig"))
    theirs = json.loads(theirs_b.decode("utf-8-sig"))
    report = {"path": path}

    # --- launches union ---
    oL = ours.get("launches", [])
    tL = theirs.get("launches", [])
    pool = {}
    flags = []
    for e in oL + tL:
        k = tuple(e.get(f) for f in KEY)
        if k in pool:
            a, b = pool[k], e
            if a == b:
                continue
            sa, sb = set(a), set(b)
            if sa <= sb or sb <= sa:  # supplementary-only divergence
                m = dict(a); m.update(b)
                pool[k] = m
                report.setdefault("merged_field_union_keys", []).append(k)
            else:
                flags.append(k)
                pool[k] = a  # keep first (HEAD side); escalate, no silent double-keep
        else:
            pool[k] = e
    merged = sorted(pool.values(), key=lambda e: e.get("ts", ""), reverse=True)[:CAP]
    merged.sort(key=lambda e: e.get("ts", ""))  # producer append order for write-back
    report["launches"] = {"ours": len(oL), "theirs": len(tL), "union": len(merged), "capped_out": max(0, len(pool) - len(merged))}

    # --- last_tick by internal ts, tie -> ours ---
    oT, tT = ours.get("last_tick"), theirs.get("last_tick")
    pick, side = oT, "ours"
    if isinstance(oT, dict) and isinstance(tT, dict):
        ots, tts = str(oT.get("ts", "")), str(tT.get("ts", ""))
        if tts > ots:
            pick, side = tT, "theirs"
        # tts <= ots: theirs older or same-second tie -> ours (HEAD) per r140
    elif oT is None and isinstance(tT, dict):
        pick, side = tT, "theirs"
    report["last_tick"] = {"side": side, "ts": pick.get("ts") if isinstance(pick, dict) else None}
    assert isinstance(pick, dict), "last_tick must be dict"

    # --- other keys: theirs-wins for keys only theirs has; else ours (single-writer-ish) ---
    out = dict(ours)
    for k, v in theirs.items():
        if k not in out:
            out[k] = v
    out["launches"] = merged
    out["last_tick"] = pick

    # --- face mirror base blob (ours): newline + trailing newline ---
    crlf = b"\r\n" in ours_b
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if crlf:
        text = text.replace("\n", "\r\n")
    if ours_b.endswith(b"\n"):
        text += "\r\n" if crlf else "\n"
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))

    json.loads(open(path, encoding="utf-8").read())  # parse-verify before add
    report["flags_true_divergence"] = flags
    print(json.dumps(report, ensure_ascii=False))
    if flags:
        sys.exit(3)

if __name__ == "__main__":
    main(sys.argv[1])
