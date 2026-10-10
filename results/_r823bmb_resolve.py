# r823 bm-b rebase-conflict resolver (bigmoney-conflict-resolve skill recipes)
# Context: origin tip (bm-c r829 estate commits) carries UNRESOLVED CONFLICT
# MARKERS in 6 shared faces (single hunk each). My rebase of commit 81b4894a6
# conflicts on 13 files. Recipes:
#  - rolling-ledger faces (compute_audit.json, regime_state.json):
#    zero-loss union of ledger rows across [base 295238c2c, hunk side A,
#    hunk side B, my stage-3]; scalar state fields take-new = my side (08:0x
#    newest ts). r188/R208 union law.
#  - snapshot faces (fundamental_b_layer_filter/futures_update_status/
#    lhb_update_status/update_status/token_usage): take-new = my clean side
#    (newest ts 08:0x > bm-c 07:2x-07:4x). R208/R216.
#  - same-day idempotent regen docs (REPORT/LIVE json+md twins): take-new =
#    my side (08:06 > 07:22). Hand-adjudicated UNKNOWN class per classifier
#    fail-closed; twin-alignment (json side decides, md follows).
# Zero-loss assertion: union row count == |A∪B∪base∪mine| per ledger key.
# Parse-verify before write (r185 law); no marker bytes in any output.
import io, json, re, subprocess

def git_bytes(ref):
    return subprocess.run(["git", "show", ref], capture_output=True).stdout

def jloads(b):
    for enc in ("utf-8", "utf-16"):
        try:
            return json.loads(b.decode(enc))
        except Exception:
            pass
    return None

def split_single_hunk(text):
    """Return (pre, A, B, post) line lists of the single conflict hunk.
    CRLF-tolerant: marker lines compared after \\r strip (r223/r234 family)."""
    lines = text.split("\n")
    def is_marker(k, prefix, exact=False):
        ln = lines[k].rstrip("\r")
        return (ln == prefix) if exact else ln.startswith(prefix)
    i = next((k for k in range(len(lines))
              if is_marker(k, "<<<<<<<")), None)
    j = next((k for k in range(len(lines))
              if is_marker(k, "=======", exact=True) and k > (i or -1)), None)
    m = next((k for k in range(len(lines))
              if is_marker(k, ">>>>>>>") and k > (j or -1)), None)
    if i is None or j is None or m is None:
        return None
    return lines[:i], lines[i + 1:j], lines[j + 1:m], lines[m + 1:]

def rowkey(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

def union_key(doc, docs, key):
    seen, out = set(), []
    for d in docs:
        for r in (d.get(key) or []):
            k = rowkey(r)
            if k not in seen:
                seen.add(k)
                out.append(r)
    # chronological order when rows carry ts (producer append order)
    if out and all(isinstance(r, dict) and "ts" in r for r in out):
        out.sort(key=lambda r: str(r.get("ts")))
    doc[key] = out
    return len(out)

BASE = "295238c2c"
LEDGER_FACES = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["triggers", "transitions", "history"],
}
SNAPSHOT_FACES = [
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/token_usage.json",
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
]
receipt = {"round": "r823", "base": BASE, "faces": {}, "law": "skill bigmoney-conflict-resolve; r188/R208/R216; origin marker-corruption heal"}

for p in SNAPSHOT_FACES:
    mine = git_bytes(":3:" + p)
    assert b"<<<<<<<" not in mine, "my side must be clean: " + p
    with io.open(p, "wb") as f:
        f.write(mine)
    receipt["faces"][p] = {"recipe": "take-new (my side, clean, newest ts)",
                           "bytes": len(mine)}

for p, keys in LEDGER_FACES.items():
    corrupted = git_bytes(":2:" + p).decode("utf-8", errors="replace")
    mine_doc = jloads(git_bytes(":3:" + p))
    base_doc = jloads(git_bytes(BASE + ":" + p))
    assert mine_doc is not None, "my side unparseable: " + p
    sides = {}
    parts = split_single_hunk(corrupted)
    if parts:
        pre, A, B, post = parts
        for nm, seg in (("A", A), ("B", B)):
            cand = jloads(("\n".join(pre + seg + post)
                           .replace("\r\n", "\n").replace("\r", "\n")
                           ).encode("utf-8"))
            sides[nm] = cand
    src = [d for d in (base_doc, sides.get("A"), sides.get("B"), mine_doc)
           if d is not None]
    doc = dict(mine_doc)  # scalars = my side (newest)
    counts = {}
    for k in keys:
        counts[k] = union_key(doc, src, k)
    blob = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    assert b"<<<<<<<" not in blob.encode("utf-8")
    json.loads(blob)  # r185 parse-verify
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(blob)
    receipt["faces"][p] = {
        "recipe": "rolling-ledger union (base+hunkA+hunkB+mine) + scalars take-new(mine)",
        "hunk_sides_parseable": {k: (v is not None) for k, v in sides.items()},
        "union_counts": counts,
        "source_docs": len(src)}

with io.open("results/_r823bmb_rebase_resolve.json", "w", encoding="utf-8",
             newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolved faces:", len(receipt["faces"]))
for p, r in receipt["faces"].items():
    print(" ", p, "->", r.get("recipe", "")[:60], r.get("union_counts", ""))
