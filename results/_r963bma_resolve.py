# r963 rebase UU resolver: 7 runtime faces, direction-agnostic newer-wins
# (+ history-union for compute_audit per r962 canon). Left in results/ for audit.
import json, re, sys

FILES = [
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ["ts", "updated", "generated", "last_attempt"]

def split_sides(text):
    """Reconstruct both FULL candidate files: pre + side + post."""
    m = re.search(r"<<<<<<<[^\n]*\n(.*?)\n=======[^\n]*\n(.*?)\n>>>>>>>[^\n]*\n?", text, re.S)
    if not m:
        return None
    pre = text[:m.start()]
    post = text[m.end():]
    return pre + m.group(1) + "\n" + post, pre + m.group(2) + "\n" + post

def ts_of(obj):
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if k in TS_KEYS and isinstance(v, str):
                    if best is None or v > best:
                        best = v
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(obj)
    return best or ""

def deep_union(a, b):
    """dict-key union with newer-wins scalars; list union by ts-ish identity."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in sorted(set(a) | set(b)):
            if k in a and k in b:
                out[k] = deep_union(a[k], b[k])
            else:
                out[k] = a.get(k, b.get(k))
        return out
    if isinstance(a, list) and isinstance(b, list):
        # union by serialized identity, preserve order a-then-new-from-b
        seen = {json.dumps(x, sort_keys=True, default=str) for x in a}
        return a + [x for x in b if json.dumps(x, sort_keys=True, default=str) not in seen]
    # scalar conflict: newer ts side wins — caller handles via ts_of context;
    # here pick by a marker key heuristic done at top level instead
    return a

def merge_obj(a, b, ta, tb):
    winner = a if ta >= tb else b
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(winner)
        # keep any keys present only on the other side (machine sub-faces etc.)
        for k, v in (b if ta >= tb else a).items():
            if k not in out:
                out[k] = v
        # history union if both sides have one
        ha = a.get("history") if isinstance(a, dict) else None
        hb = b.get("history") if isinstance(b, dict) else None
        if isinstance(ha, list) and isinstance(hb, list):
            out["history"] = deep_union(ha, hb)
        return out
    return winner

ok = True
for f in FILES:
    text = open(f, encoding="utf-8", newline="").read()
    sides = split_sides(text)
    if sides is None:
        print(f, "NO-MARKER (auto-merged?) skip")
        continue
    ta_text, tb_text = sides
    try:
        A = json.loads(ta_text)
        B = json.loads(tb_text)
    except Exception as e:
        print(f, "PARSE-FAIL", e)
        ok = False
        continue
    ta, tb = ts_of(A), ts_of(B)
    merged = merge_obj(A, B, ta, tb)
    with open(f, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f, "RESOLVED newer:", max(ta, tb), "| A:", ta[:19], "B:", tb[:19])

print("OK" if ok else "FAIL")
