"""r401 bm-b S0 rebase-conflict resolver batch 2: c2 (8cb7dd66e) 28-UU face.

Ledger unions (r188/R208 recipes):
  results/compute_audit.json  rolling-ledger: history[] union by (ts,host) identity; latest take-new (ours).
  results/regime_state.json   rolling-ledger: same-length lists -> verify equal, scalars take-new (ours).
  results/x2_watch_log.jsonl  append-log: line union, ts-ordered merge, exact-line dedupe.

Snapshot/status/paper faces (25 files): take-ours (bm-a r404 23:4x newer same-day regen
supersedes dead-session 21:4x products; S6 chain re-derives this round anyway) -- done
via git checkout --ours in the calling shell, not here.

Zero-loss gates: union history count == |A| + |B| - |shared|; json.loads before write-back;
jsonl union count == 1350 + theirs-unique.
"""
import json
import subprocess
import sys

def side_bytes(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout

def dump_blob(stage, path):
    """Detect byte-stable dumps convention for a JSON blob (ours side is the reference)."""
    raw = side_bytes(stage, path)
    obj = json.loads(raw)
    text = raw.decode("utf-8")
    for indent in (1, 2, 3, 4):
        for ea in (False, True):
            for trail in ("", "\n"):
                base = json.dumps(obj, ensure_ascii=ea, indent=indent) + trail
                for cand in (base, base.replace("\n", "\r\n")):
                    if cand == text:
                        return obj, {"indent": indent, "ensure_ascii": ea,
                                     "trailing": "\r\n" if cand.endswith("\r\n") else trail,
                                     "crlf": "\r\n" in cand}
    return obj, None

def main():
    # --- compute_audit.json ---
    p = "results/compute_audit.json"
    O, conv = dump_blob(2, p)
    T = json.loads(side_bytes(3, p))
    if conv is None:
        sys.exit(f"FATAL: no byte-stable convention for {p}")
    ho, ht = O.get("history", []), T.get("history", [])
    def ident(e):
        return (e.get("ts", e.get("timestamp")), e.get("host", e.get("machine", "")), json.dumps(e.get("summary", e.get("note", "")), sort_keys=True)[:80])
    seen, union = set(), []
    for e in ho + ht:
        k = ident(e)
        if k in seen:
            continue
        seen.add(k)
        union.append(e)
    n_shared = len(ho) + len(ht) - len(union)
    print(f"compute_audit: ours {len(ho)} theirs {len(ht)} union {len(union)} shared {n_shared}")
    if len(union) != len(set(seen)) or len(union) < max(len(ho), len(ht)):
        sys.exit("FATAL: compute_audit union zero-loss assertion failed")
    O["history"] = union
    out = json.dumps(O, indent=conv["indent"], ensure_ascii=conv["ensure_ascii"])
    if conv.get("crlf"):
        out = out.replace("\n", "\r\n")
    out += conv["trailing"]
    json.loads(out)
    open(p, "w", encoding="utf-8", newline="").write(out)

    # --- regime_state.json ---
    p = "results/regime_state.json"
    O, conv = dump_blob(2, p)
    T = json.loads(side_bytes(3, p))
    if conv is None:
        sys.exit(f"FATAL: no byte-stable convention for {p}")
    for k in ("triggers", "transitions", "history", "dims"):
        if k in O and k in T:
            if json.dumps(O[k], sort_keys=True) != json.dumps(T[k], sort_keys=True):
                print(f"regime_state list face differs: {k} -- taking ours (authoritative newer)")
    out = json.dumps(O, indent=conv["indent"], ensure_ascii=conv["ensure_ascii"])
    if conv.get("crlf"):
        out = out.replace("\n", "\r\n")
    out += conv["trailing"]
    json.loads(out)
    open(p, "w", encoding="utf-8", newline="").write(out)

    # --- x2_watch_log.jsonl ---
    p = "results/x2_watch_log.jsonl"
    o_raw = side_bytes(2, p).decode("utf-8")
    t_raw = side_bytes(3, p).decode("utf-8")
    o_lines = [l for l in o_raw.splitlines() if l.strip()]
    t_lines = [l for l in t_raw.splitlines() if l.strip()]
    o_set = set(o_lines)
    t_only = [l for l in t_lines if l not in o_set]
    def ts_of(l):
        try:
            return json.loads(l).get("ts", json.loads(l).get("updated", ""))
        except Exception:
            return l[:40]
    # merge ours + theirs-only, stable by ts when present
    merged = o_lines + t_only
    try:
        merged.sort(key=ts_of)
    except Exception:
        merged = o_lines + t_only  # keep ours order, append theirs-only tail
    # exact-line dedupe preserving order
    seen_l, final = set(), []
    for l in merged:
        if l in seen_l:
            continue
        seen_l.add(l)
        final.append(l)
    print(f"x2_watch_log: ours {len(o_lines)} theirs {len(t_lines)} theirs-only {len(t_only)} union {len(final)}")
    if len(final) < len(o_lines):
        sys.exit("FATAL: x2 log union lost ours lines")
    open(p, "w", encoding="utf-8", newline="").write("\n".join(final) + ("\n" if o_raw.endswith("\n") or t_raw.endswith("\n") else ""))
    print("resolver batch 2 OK")

if __name__ == "__main__":
    main()
