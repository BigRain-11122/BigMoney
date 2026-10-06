import json, os, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
receipt = {"window": "pick4-a8b89872e resolve (final pick)", "faces": {}}

def read_eol(raw):
    crlf = raw.count(b"\r\n"); lf_only = raw.count(b"\n") - crlf
    return b"\r\n" if crlf > lf_only else b"\n"

def rebuild(raw, choose):
    """choose(head_lines, ours_lines) -> list of lines to substitute for the conflict block."""
    nl = read_eol(raw)
    lines = raw.split(nl)
    res, mode, head_b, ours_b = [], None, [], []
    nblocks = 0
    for l in lines:
        if l.startswith(b"<<<<<<<"):
            mode = "head"; continue
        if l.startswith(b">>>>>>>"):
            res.extend(choose(head_b, ours_b)); nblocks += 1
            mode = None; head_b, ours_b = [], []; continue
        if l == b"=======" or l.startswith(b"======= "):
            mode = "ours"; continue
        if mode == "head": head_b.append(l)
        elif mode == "ours": ours_b.append(l)
        else: res.append(l)
    trailing_nl = raw.endswith(nl)
    blob = nl.join(res)
    if trailing_nl: blob += nl
    return blob, nblocks, nl

# nulls: union-by-k (HEAD block + OURS block, dedupe first-write-wins, sorted)
p = "results/fund_divlowvol_p1/nulls.jsonl"
raw = open(p, "rb").read()
def choose_nulls(head, ours):
    merged = {}
    for l in head:
        if l.strip(): merged.setdefault(json.loads(l.decode("utf-8"))["k"], l)
    for l in ours:
        if l.strip(): merged.setdefault(json.loads(l.decode("utf-8"))["k"], l)
    return [merged[k] for k in sorted(merged)]
blob, nb, nl = rebuild(raw, choose_nulls)
open(p, "wb").write(blob)
for l in blob.split(nl):
    if l.strip(): json.loads(l.decode("utf-8"))
receipt["faces"][p] = {"recipe": "union-by-k", "blocks": nb, "final_lines": blob.count(nl)}

# p1d_gates: take HEAD (origin newer date 01:43 vs ours 01:11)
p = "results/p1d_gates.json"
raw = open(p, "rb").read()
blob, nb, nl = rebuild(raw, lambda h, o: h)
open(p, "wb").write(blob)
json.loads(blob.decode("utf-8"))
receipt["faces"][p] = {"recipe": "take-head (newer date 01:43)", "blocks": nb}

with open("results/_r791bmb_pick4_resolve.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
sys.stdout.write("PICK4-RESOLVE-OK\n")
for p, info in receipt["faces"].items():
    print(p, "->", info.get("recipe"), "| blocks:", info.get("blocks"))
