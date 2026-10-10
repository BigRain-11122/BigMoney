"""r833 bm-c mini-split: CODELY.md main blob 31,807B > 30,720B cap ->
same-window migration per r731/r747/r896 precedent. 3 rows verbatim out
to their domain files, 1 pointer row in, byte-accounting receipt.
Zero-loss assertion: extracted block bytes == appended bytes (verbatim),
main-file retained face unchanged apart from the 3 removals + 1 insert."""

import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")

# (line-prefix bytes, target domain file)
MOVES = [
    ("- [2026-10-10 11:5x r829 bm-c]".encode("utf-8"),
     os.path.join(ROOT, "research", "pit-machine.md")),
    ("- [2026-10-10 04:5x r816 bm-b] **sina 1m".encode("utf-8"),
     os.path.join(ROOT, "research", "pit-data.md")),
    ("- [2026-10-10 05:4x r817 bm-b]".encode("utf-8"),
     os.path.join(ROOT, "research", "pit-tooling.md")),
]

PTR_ANCHOR = "- \u57df\u6307\u9488\u00b7r816 bm-c mini-split".encode("utf-8")

PTR_ROW = (
    "- \u57df\u6307\u9488\u00b7r833 bm-c mini-split\uff0810-10 14:4x\u00b7\u4e3b\u4ef6 "
    "31,807B \u8d8a\u5e3d 1,087B \u5f53\u7a97\u5373\u529e\u00b7\u4eea\u5f0f "
    "r731/r747/r896 \u540c\u6b3e\uff09\uff1ar829 bm-c \u540c\u673a\u53cc CEO "
    "\u4ee4 GPU \u51b2\u7a81\u6392\u7a0b\u5224\u4f8b\uff08\u5f71\u7247\u94fe>LoRA "
    "\u8bad\u7ec3\u00b7\u6740\u8bad\u7ec3\u4e94\u4ef6\u5957\uff0c1,103B\uff09verbatim "
    "\u8fc1 pit-machine.md\uff3bmachine-state/GPU \u57df\u00b7machine/Ollama/"
    "\u663e\u5b58\u9762\u52a8\u4f5c\u524d\u6539\u8bfb\u8be5\u4ef6\uff3d+r816 bm-b "
    "sina 1m \u6536\u76d8\u96c6\u5408\u7ade\u4ef7\u6d1e\uff08796B\uff09verbatim \u8fc1 "
    "pit-data.md\uff3b\u5206\u949f\u6e90\u5f62\u72b6\u57df\u00b7\u5206\u949f\u9762\u6d88"
    "\u8d39/\u6821\u9a8c\u524d\u6539\u8bfb pit-data\uff3d+r817 bm-b \u811a\u672c\u53cc"
    "\u5165\u53e3\u5206\u652f\u6f0f\u63d2 ROOT \u5751\uff08757B\uff09verbatim \u8fc1 "
    "pit-tooling.md\uff3b\u591a\u5165\u53e3\u811a\u672c sys.path \u57df\u00b7selftest "
    "\u76f4\u8c03\u9762\u52a8\u4f5c\u524d\u6539\u8bfb\u8be5\u4ef6\uff3d\u2014\u2014\u9010"
    "\u5757\u5b57\u8282\u5bf9\u8d26=receipt results/_r833bmc_codely_minisplit.json"
    "\uff08\u96f6\u4e22\u5931\u65ad\u8a00=\u9010\u5757 bytes in target verbatim+\u4e3b"
    "\u4ef6\u4fdd\u7559\u9762\u6052\u7b49+\u4e3b/\u57df\u4ef6 \u226430KB\uff09\uff1b\u65b0"
    "\u5751\u5f8b\u4ecd\u5148\u5165\u4e3b\u4ef6\u540e\u56de\u626b\u3002\n"
).encode("utf-8")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    mb = open(MAIN, "rb").read()
    size_before = len(mb)
    lines = mb.splitlines(keepends=True)
    receipt = {"ts_round": "r833 bm-c", "law": "D-20261002-06 main<=30KB",
               "main_before_bytes": size_before, "blocks": [], "targets": {}}
    removed_idx = {}
    blocks = []
    for prefix, target in MOVES:
        hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
        assert len(hits) == 1, "prefix hit !=1: %r -> %d hits" % (prefix, len(hits))
        i = hits[0]
        blk = lines[i]
        assert blk.endswith(b"\n"), "line lacks terminator (tail-adjacency law)"
        blocks.append((i, blk, target))
        removed_idx[i] = True
        receipt["blocks"].append({
            "line_index": i, "bytes": len(blk), "sha16": sha16(blk),
            "target": os.path.relpath(target, ROOT),
            "prefix": prefix.decode("utf-8"),
        })
    # append verbatim to each target (assert target ends with newline first)
    for i, blk, target in blocks:
        tb = open(target, "rb").read()
        t_size_before = len(tb)
        if tb and not tb.endswith(b"\n"):
            raise SystemExit("target lacks trailing newline: " + target)
        with open(target, "ab") as f:
            f.write(blk)
        chk = open(target, "rb").read()
        assert chk.endswith(blk), "verbatim append failed (bytes not in target)"
        receipt["targets"][os.path.relpath(target, ROOT)] = {
            "before": t_size_before, "after": len(chk),
            "delta": len(chk) - t_size_before, "assert_delta_eq_block": True}
    # rebuild main: drop removed lines, insert pointer row after r816 anchor
    anchor_hits = [i for i, ln in enumerate(lines)
                   if ln.startswith(PTR_ANCHOR)]
    assert len(anchor_hits) == 1, "anchor hit !=1"
    anchor_i = anchor_hits[0]
    # find end of anchor line block (anchor row may span multiple physical
    # lines: it is one row here per precedent format, single line w/ \n)
    out = []
    for i, ln in enumerate(lines):
        if i in removed_idx:
            continue
        out.append(ln)
        if i == anchor_i:
            out.append(PTR_ROW)
    nb = b"".join(out)
    open(MAIN, "wb").write(nb)
    size_after = len(nb)
    receipt["pointer_row_bytes"] = len(PTR_ROW)
    receipt["removed_bytes_total"] = sum(len(b) for _, b, _ in blocks)
    receipt["main_after_bytes"] = size_after
    receipt["main_cap"] = 30720
    receipt["main_under_cap"] = size_after <= 30720
    # zero-loss: every block byte-for-byte present in its target tail
    for i, blk, target in blocks:
        tb = open(target, "rb").read()
        assert blk in tb, "zero-loss assertion failed for " + str(target)
    # domain files under cap
    for _, _, target in blocks:
        sz = os.path.getsize(target)
        assert sz <= 30720, "domain file over cap: " + str(target)
        receipt["targets"][os.path.relpath(target, ROOT)]["after"] = sz
    rp = os.path.join(ROOT, "results", "_r833bmc_codely_minisplit.json")
    json.dump(receipt, open(rp, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    print(json.dumps({"main_before": size_before, "main_after": size_after,
                      "removed": receipt["removed_bytes_total"],
                      "ptr_row": len(PTR_ROW), "under_cap": size_after <= 30720,
                      "blocks": len(blocks), "zero_loss": "PASS",
                      "receipt": os.path.relpath(rp, ROOT)}))


if __name__ == "__main__":
    main()
