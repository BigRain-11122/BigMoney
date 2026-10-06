import json, os, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
receipt = {"window": "pick3-f14468d56 resolve (6 faces)", "faces": {}}

def read_eol(raw):
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    return b"\r\n" if crlf > lf_only else b"\n"

def split_blocks(raw, nl):
    """returns (pre_lines, blocks, post_lines); blocks=[(head_lines, ours_lines), ...]"""
    lines = raw.split(nl)
    out, blocks = [], []
    cur_head, cur_ours, mode = [], [], None
    for l in lines:
        if l.startswith(b"<<<<<<<"):
            mode = "head"; continue
        if l.startswith(b">>>>>>>"):
            blocks.append((cur_head, cur_ours)); cur_head, cur_ours, mode = [], [], None; continue
        if l == b"=======" or l.startswith(b"======= "):
            mode = "ours"; continue
        if mode == "head":
            cur_head.append(l)
        elif mode == "ours":
            cur_ours.append(l)
        else:
            out.append(l)
    return out, blocks

def strip_trailing(l):
    return l.rstrip(b"\r")

def resolve_nulls(path):
    raw = open(path, "rb").read()
    nl = read_eol(raw)
    common, blocks = split_blocks(raw, nl)
    merged = {}
    def keyof(l):
        return json.loads(l.decode("utf-8"))["k"]
    head_n = ours_n = 0
    # order: common first (both-agreed), then per-block HEAD then OURS, first-write-wins
    for l in common:
        if l.strip(): merged.setdefault(keyof(l), l)
    for head, ours in blocks:
        head_n += len([x for x in head if x.strip()]); ours_n += len([x for x in ours if x.strip()])
        for l in head:
            if l.strip(): merged.setdefault(keyof(l), l)
        for l in ours:
            if l.strip(): merged.setdefault(keyof(l), l)
    final = [merged[k] for k in sorted(merged)]
    trailing_nl = raw.endswith(nl)
    blob = nl.join(final)
    if trailing_nl: blob += nl
    open(path, "wb").write(blob)
    for l in final:
        if l.strip(): json.loads(l.decode("utf-8"))
    receipt["faces"][path] = {"recipe": "union-by-k first-write-wins", "blocks": len(blocks),
                              "head_lines": head_n, "ours_lines": ours_n, "final_lines": len(final)}
    return len(blocks)

def resolve_history(path):
    raw = open(path, "rb").read()
    nl = read_eol(raw)
    common, blocks = split_blocks(raw, nl)
    merged = {}
    dups_diff = []
    def ep(l):
        return json.loads(l.decode("utf-8"))["epoch"]
    def add(l):
        if not l.strip(): return
        e = ep(l)
        if e in merged and merged[e] != l:
            dups_diff.append(e); return  # first-seen wins
        merged.setdefault(e, l)
    for l in common: add(l)
    for head, ours in blocks:
        for l in head: add(l)
        for l in ours: add(l)
    final = [merged[k] for k in sorted(merged)]
    trailing_nl = raw.endswith(nl)
    blob = nl.join(final)
    if trailing_nl: blob += nl
    open(path, "wb").write(blob)
    for l in final: json.loads(l.decode("utf-8"))
    epochs = [ep(l) for l in final]
    assert all(a <= b for a, b in zip(epochs, epochs[1:])), "epoch not monotonic"
    receipt["faces"][path] = {"recipe": "daemon-live/union epoch-dedupe sorted", "blocks": len(blocks),
                              "final_lines": len(final), "dup_diff_epochs": dups_diff}

def resolve_single_json(path, side):
    """side: 'ours' (owner daemon faces) or 'head' (newer origin regen). If no markers (daemon live-wins), keep as-is."""
    raw = open(path, "rb").read()
    nl = read_eol(raw)
    common, blocks = split_blocks(raw, nl)
    if not blocks:
        receipt["faces"][path] = {"recipe": "daemon-live-wins (no markers, keep worktree)", "blocks": 0}
        return
    assert len(blocks) == 1, f"{path}: expected 1 block, saw {len(blocks)}"
    head, ours = blocks[0]
    chosen = ours if side == "ours" else head
    out = []
    idx_common = 0
    # common lines surrounding the single block: rebuild common+chosen
    blob = nl.join(common[:len(common)-0])  # placeholder, rebuild below
    # rebuild: common lines with chosen block inserted at the position where the block was
    # since split_blocks loses block position, reconstruct as: common[0:i] + chosen + common[i:]
    # find insertion point: the block was between... we track by rebuilding from raw line order
    lines = raw.split(nl)
    res, mode, head_b, ours_b = [], None, [], []
    inserted = False
    for l in lines:
        if l.startswith(b"<<<<<<<"):
            mode = "head"; continue
        if l.startswith(b">>>>>>>"):
            res.extend(chosen); inserted = True
            mode = None; head_b, ours_b = [], []; continue
        if l == b"=======" or l.startswith(b"======= "):
            mode = "ours"; continue
        if mode == "head":
            head_b.append(l)
        elif mode == "ours":
            ours_b.append(l)
        else:
            res.append(l)
    assert inserted, f"{path}: no block inserted"
    trailing_nl = raw.endswith(nl)
    blob = nl.join(res)
    if trailing_nl: blob += nl
    open(path, "wb").write(blob)
    json.loads(blob.decode("utf-8"))  # validity check
    receipt["faces"][path] = {"recipe": f"take-{side} block (head={len([x for x in head if x.strip()])} ours={len([x for x in ours if x.strip()])} lines)",
                              "blocks": 1}

b1 = resolve_nulls("results/fund_divlowvol_p1/nulls.jsonl")
resolve_nulls("results/fund_quality_p1/nulls.jsonl")
resolve_history("results/saturation_engine/history_bm-b.jsonl")
resolve_single_json("results/saturation_engine/face_bm-b.json", side="ours")   # bm-b-owned daemon face: owner side
resolve_single_json("results/saturation_engine/state_bm-b.json", side="ours") # bm-b-owned daemon face: owner side
resolve_single_json("results/p1d_gates.json", side="head")                    # shared regen face: origin newer (01:41 vs 01:09)

with open("results/_r791bmb_pick3_resolve.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
sys.stdout.write("PICK3-RESOLVE-OK\n")
for p, info in receipt["faces"].items():
    print(p, "->", info.get("recipe"), "| blocks:", info.get("blocks"))
