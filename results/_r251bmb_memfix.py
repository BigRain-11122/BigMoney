# r251 bm-b memory append (four-gate passed: lesson-first, one-thing, pointer-only) + script artifact honesty note
import json

# --- 1. correction note appended to this round's close script (artifact honesty: pattern regression caught at closing double-scan) ---
note = (
    "# POST-RUN CORRECTION (r251 closing double-scan catch, zero leakage): the orders_ack token pattern above\n"
    "# was copied from r97-era script (_r97_ack.py 3-segment tokens) -- STALE. Current law (r220, see\n"
    "# Tools/orders_diff.py header 'Ack format contract' + _r241bma_wrapup.py header) = FULL filename incl .md\n"
    "# suffix. The 3-segment write made the closing scan report 79/79 false-unacked (format mismatch vs fleet\n"
    "# canonical bm-a face). Fixed same minute by full-filename regeneration + Tools/orders_diff.py re-verify\n"
    "# (diff empty 79/79). Lesson: before copying a pattern from a historical one-shot script, grep the LIVE\n"
    "# canonical carrier for the current contract; run orders diffs via Tools/orders_diff.py, never hand-rolled.\n"
)
with open("results/_r251bmb_close.py", "a", encoding="utf-8") as fh:
    fh.write(note)
print("correction note appended to _r251bmb_close.py")

# --- 2. CODELY.md Reference section: one-line lesson (binary append, CRLF, r97 pattern) ---
entry = (
    "- [2026-09-26 13:26] \u5751\u5f8b\uff08bm-b r251\u00b7\u5fc3\u8df3 orders_ack \u5f62\u6001\u9762\u00b7E1 \u6536\u5c3e\u53cc\u626b\u81ea\u6355\u96f6\u5916\u6cc4\uff09\uff1a"
    "**\u62f7\u8d1d\u65e7\u4e00\u6b21\u6027\u8f6e\u811a\u672c\u5f53\u8303\u5f0f\u524d\u5fc5\u5148\u6838\u73b0\u884c\u6cd5\u2014\u2014r251 \u6536\u5c3e\u811a\u672c\u7167\u6284 r97 _r97_ack.py \u7684 3 \u6bb5\u5f0f token\uff0c"
    "\u800c r220 law \u5df2\u5b9a orders_ack=\u5168\u6587\u4ef6\u540d\u542b .md\uff08bm-a \u73b0\u884c\u9762\uff09\uff0c\u5199\u540e\u6536\u5c3e\u53cc\u626b\u7acb\u523b\u66b4\u9732 79/79 \u5168\u91cf\u5047\u672a\u56de\u6267**\uff1b"
    "\u6b63\u5f8b=\u62f7\u8d1d\u5386\u53f2\u811a\u672c\u6a21\u5f0f\u5148 grep \u73b0\u884c\u6b63\u5178\u8f7d\u4f53\uff08Tools/orders_diff.py \u5934\u6ce8 Ack format contract\uff09\u6838\u5bf9\u5f62\u6001\u518d\u843d\u7b14\uff0c"
    "\u4ee4\u5dee\u96c6\u4e00\u5f8b\u7528 Tools/orders_diff.py \u5e38\u8bbe\u5de5\u5177\u8dd1\u52ff\u624b\u641c\uff1b\u4fee\u590d=\u5168\u6587\u4ef6\u540d\u91cd\u751f\u6210+canonical \u5de5\u5177\u590d\u9a8c diff empty\u3002"
    "\u6307\u9488=Tools/orders_diff.py \u5951\u7ea6\u6ce8+results/_r251bmb_close.py \u5c3e\u90e8\u4fee\u6b63\u6ce8\r\n"
)
raw = open("CODELY.md", "rb").read()
sep = b"\r\n" if b"\r\n" in raw[:2000] else b"\n"
if not raw.endswith((b"\r\n", b"\n")):
    raw += sep
with open("CODELY.md", "ab") as fh:
    fh.write(entry.encode("utf-8"))
print("CODELY.md lesson appended; size now:", len(open('CODELY.md','rb').read()), "bytes (<50KB, no reorganization)")
