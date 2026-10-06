import json, os, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
receipt = {"window": "pick2-c4924674b resolve (3 lane faces)", "faces": {}}

MARKERS = (b"<<<<<<< ", b">>>>>>> ", b"======= ", b"||||||| ")

def split_blocks(raw):
    # returns (list_of_lines, head_lines, ours_lines) with marker lines removed
    lines = raw.split(b"\n")
    out, head, ours = [], [], []
    mode = None  # None=common, 'head', 'ours'
    for l in lines:
        if l.startswith(b"<<<<<<<"):
            mode = "head"; continue
        if l.startswith(b">>>>>>>"):
            mode = None; continue
        if l == b"=======" or l.startswith(b"======= "):
            mode = "ours"; continue
        if mode == "head":
            head.append(l)
        elif mode == "ours":
            ours.append(l)
        else:
            out.append(l)
    return lines, out, head, ours

def resolve_nulls(path, key="k"):
    raw = open(path, "rb").read()
    assert b"\r" not in raw, f"{path}: unexpected CR"
    lines, common, head, ours = split_blocks(raw)
    def keyof(l):
        d = json.loads(l.decode("utf-8"))
        return d[key]
    # union by key, chronological (numeric k)
    merged = {}
    dup_conflict = []
    for src, side in ((head, "HEAD"), (ours, "OURS")):
        for l in src:
            k = keyof(l)
            if k in merged and merged[k] != l:
                dup_conflict.append((k, side))
                continue  # first write wins (HEAD); log conflict
            merged.setdefault(k, l)
    # verify common lines don't collide with merged keys
    for l in common:
        if not l.strip():
            continue
        k = keyof(l)
        if k in merged and merged[k] != l:
            dup_conflict.append((k, "COMMON"))
        merged.setdefault(k, l)
    final = [merged[k] for k in sorted(merged)]
    # byte-termination: preserve trailing newline if original had one
    trailing_nl = raw.endswith(b"\n")
    blob = b"\n".join(x for x in final if x.strip() != b"")
    if trailing_nl:
        blob += b"\n"
    open(path, "wb").write(blob)
    receipt["faces"][path] = {
        "recipe": "union-by-k (HEAD block + OURS block + common, dedupe first-write-wins)",
        "head_lines": len(head), "ours_lines": len(ours), "common_lines": len([x for x in common if x.strip()]),
        "final_lines": blob.count(b"\n") + (0 if trailing_nl else 1),
        "dup_conflicts": dup_conflict,
    }
    # sanity: all final lines parse as json
    for l in blob.split(b"\n"):
        if l.strip():
            json.loads(l.decode("utf-8"))

def resolve_history(path):
    # daemon live-wins: daemon rolling-window rewrite already consumed the <<<<<<< / ======= markers;
    # only orphan >>>>>>> remains. Keep daemon's live content verbatim, strip any marker lines.
    # r367 law: split conserves \r under LF split -> detect EOL first, strip trailing \r per line.
    raw = open(path, "rb").read()
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    nl = b"\r\n" if crlf > lf_only else b"\n"
    lines = raw.split(nl)
    kept, stripped = [], []
    for l in lines:
        if l.startswith(MARKERS):
            stripped.append(l[:60]); continue
        kept.append(l)
    blob = nl.join(kept)
    assert b"\r\r" not in blob, f"{path}: double-terminator leak (r367)"
    open(path, "wb").write(blob)
    n_json = sum(1 for l in kept if l.strip())
    for l in kept:
        if l.strip():
            json.loads(l.decode("utf-8"))
    # verify epoch monotonic non-decreasing (daemon writes chronologically)
    epochs = [json.loads(l.decode("utf-8"))["epoch"] for l in kept if l.strip()]
    assert all(a <= b for a, b in zip(epochs, epochs[1:])), f"{path}: epoch not monotonic"
    receipt["faces"][path] = {"recipe": "daemon-live-wins (orphan markers stripped, daemon content verbatim, %s EOL)" % nl.decode("ascii", "replace"),
                               "json_lines": n_json, "stripped": [s.decode("utf-8", "replace") for s in stripped]}

resolve_nulls("results/fund_divlowvol_p1/nulls.jsonl")
resolve_nulls("results/fund_quality_p1/nulls.jsonl")
resolve_history("results/saturation_engine/history_bm-b.jsonl")

with open("results/_r791bmb_pick2_resolve.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
sys.stdout.write("PICK2-RESOLVE-OK\n")
for p, info in receipt["faces"].items():
    print(p, info.get("recipe"), "final:", info.get("final_lines", info.get("json_lines")))
