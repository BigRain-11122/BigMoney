"""r287 bm-b S0 rebase collision resolver (skill bigmoney-conflict-resolve).

Conflict pair: results/post_review.jsonl (append-log, r188 union) +
results/post_review/REPORT-20260927.md (snapshot take-newest).

Faces: origin side = bm-a tick C9 post-review run 01:20:02/03 (36 rows);
mine side = bm-b tick C9 post-review run 01:30:14/15 (36 rows); same criteria,
same verdicts per id (verified pre-resolve). jsonl blob = mixed EOL face
(bm-a autocrlf=true LF rows vs bm-b producer text-mode CRLF rows) ->
r281/r270 law: LF-normalize union write-back. REPORT md = pure CRLF
producer face -> take MINE block (newest 生成 ts 01:30:15 > 01:20:02),
byte-face preserved.
"""
import json
import sys

JSONL = "results/post_review.jsonl"
REPORT = "results/post_review/REPORT-20260927.md"
MARKS = ("<<<<<<<", "=======", ">>>>>>>")

def resolve_jsonl():
    raw = open(JSONL, "rb").read()
    txt = raw.decode("utf-8")
    lines = txt.split("\n")
    midx = [i for i, l in enumerate(lines) if l.startswith(MARKS)]
    assert len(midx) == 3, f"expected 3 markers, got {midx}"
    s, m, e = midx
    pre = [l for l in lines[:s] if l.strip()]
    head = [l for l in lines[s + 1:m] if l.strip()]
    mine = [l for l in lines[m + 1:e] if l.strip()]
    post = [l for l in lines[e + 1:] if l.strip()]
    assert len(head) == 36 and len(mine) == 36, (len(head), len(mine))

    def rows(ls):
        out = []
        for l in ls:
            l2 = l.rstrip("\r")
            d = json.loads(l2)  # parse gate (r185 law)
            out.append((d["ts"], d["id"], d["verdict"], l2))
        return out

    hr, mr = rows(head), rows(mine)
    # union in ts order, zero loss; dedupe guard on (ts,id) exact pair
    assert len({(t, i) for t, i, v, _ in hr + mr}) == 72, "unexpected dup pair"
    # verdict agreement per id across the two runs (same registry re-derive)
    hmap = {i: v for _, i, v, _ in hr}
    mism = [(i, hmap[i], v) for _, i, v, _ in mr if hmap.get(i) != v]
    assert not mism, f"verdict disagreement between runs: {mism}"

    out = [l.rstrip("\r") for l in pre] + [x[3] for x in hr] + [x[3] for x in mr]
    if post:
        out += [l.rstrip("\r") for l in post]
    blob = "\n".join(out) + "\n"
    # validation: every line parses, no markers, count = pre + 72
    for l in out:
        json.loads(l)
    assert not any(l.startswith(MARKS) for l in out)
    assert len(out) == len(pre) + 72
    open(JSONL, "wb").write(blob.encode("utf-8"))
    return {"jsonl": {"pre": len(pre), "head_rows": len(hr), "mine_rows": len(mr),
                      "total": len(out), "lf_normalized": True}}

def resolve_report():
    raw = open(REPORT, "rb").read()
    txt = raw.decode("utf-8")
    lines = txt.split("\n")  # CRLF face: each element (except last) ends with \r
    midx = [i for i, l in enumerate(lines) if l.split("\r")[0].startswith(MARKS)]
    assert len(midx) == 3, f"expected 3 markers, got {midx}"
    s, m, e = midx
    head_gen = lines[s + 1].split("\r")[0]
    mine_block = [l for l in lines[m + 1:e] if l.strip()]
    assert len(mine_block) == 1, mine_block
    mine_gen = mine_block[0].split("\r")[0]
    # take-newest gate: producer wall-clock key 生成 ts
    assert mine_gen > head_gen, (head_gen, mine_gen)
    out = lines[:s] + mine_block + lines[e + 1:]
    blob = "\n".join(out)
    assert not any(l.split("\r")[0].startswith(MARKS) for l in out)
    assert "生成 2026-09-27 01:30:15" in blob
    open(REPORT, "wb").write(blob.encode("utf-8"))
    return {"report": {"head_gen": head_gen, "kept_gen": mine_gen,
                       "crlf_face_preserved": True}}

if __name__ == "__main__":
    res = {}
    res.update(resolve_jsonl())
    res.update(resolve_report())
    print("RESOLVE OK", json.dumps(res, ensure_ascii=False))
