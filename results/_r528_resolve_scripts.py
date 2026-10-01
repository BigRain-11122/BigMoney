# r528 bm-b constructive merge for scripts/perpetual_faces_n1.py selftest region
# (conflict: my W34 materializer block vs origin bm-a W35 materializer block, 3 chained hunks)
# Law: r531 constructive merge (both blocks kept, W34 first, W35 second) + the PRE-DECLARED
# +34 auto-join amendment (r531-1/r541 minimal-amendment precedent, declared in bm-a's own
# W35 comment: "when bm-b lands the W34 freeze+finalize, the dep pin auto-joins +34").
# Deterministic text surgery on conflict markers. Zero network, zero LLM.
import re, sys, py_compile

PATH = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\perpetual_faces_n1.py"
raw = open(PATH, encoding="utf-8", newline="").read()

MARK_START = re.compile(r"^<<<<<<< HEAD\r?\n", re.M)
MARK_MID = re.compile(r"^=======\r?\n", re.M)
MARK_END = re.compile(r"^>>>>>>> b954d8ab2[^\r\n]*\r?\n", re.M)

starts = [m.start() for m in MARK_START.finditer(raw)]
mids = [m.start() for m in MARK_MID.finditer(raw)]
ends = [m.end() for m in MARK_END.finditer(raw)]
assert len(starts) == len(mids) == len(ends) == 3, f"expected 3 conflicts, got {len(starts)}/{len(mids)}/{len(ends)}"

def region(i):
    head = raw[starts[i] + len("<<<<<<< HEAD\n"):mids[i]]
    mine = raw[mids[i] + len("=======\n"):ends[i] - len(">>>>>>> b954d8ab2 ...\n")]
    # trim the end marker line precisely
    seg = raw[mids[i] + len("=======\n"):ends[i]]
    seg = MARK_END.sub("", seg)
    return raw[starts[i] + len("<<<<<<< HEAD\n"):mids[i]], seg

headA, mineA = region(0)
headB, mineB = region(1)
headC, mineC = region(2)

# anchors
assert "_set_wave(35)" in headA and "W35 materializer face" in headA, "headA anchor"
assert "_set_wave(34)" in mineA and "W34 materializer face" in mineA, "mineA anchor"
assert 'f"W35 shard dir collides' in headB and 'f"W34 shard dir collides' in mineB, "B anchors"
assert 'f"W35 finalize cumulative dep' in headC and 'f"W34 finalize cumulative dep' in mineC, "C anchors"

# shared segments between conflicts
shared1 = raw[ends[0]:starts[1]]          # for-wprev shard-dir loop head (ends mid-assert)
shared2 = raw[ends[1]:starts[2]]          # dep loop header
post = raw[ends[2]:]                       # pickle assert + finally + rest
assert "for wprev in (" in shared1 and "shard_subdir" in shared1, "shared1 anchor"
assert "for _depw in (17," in shared2, "shared2 anchor"
assert 'pickle.dumps(_worker_init)' in post.splitlines()[0], "post anchor"

pickle_finally = '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"\n    finally:\n        _set_wave(2)\n'
assert post.startswith(pickle_finally), "post must start with pickle+finally tail"

# ---- amendments to the W35 (origin) block per the pre-declared +34 auto-join ----
# A: prior-wave disjointness loop + comment
old_loop = "        # prior-wave disjointness incl. W30/W31/W32/W33 (all registered;\n" \
           "        # W34 has NO registry row yet -- bm-b pre-scan ADMIT-READY r527,\n" \
           "        # freeze pending at the bm-b seat; its published projection is\n" \
           "        # asserted disjoint from W35 by the band-gate PUBLISHED leg and\n" \
           "        # the arithmetic-continuation facts below).\n" \
           "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,\n" \
           "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n" \
           "                      31, 32, 33):\n"
new_loop = "        # prior-wave disjointness incl. W30/W31/W32/W33/W34 (all\n" \
           "        # registered; W34 registered by the bm-b r528 freeze adopted\n" \
           "        # in this same merge -- the +34 auto-join of the r531-1/r541\n" \
           "        # minimal-amendment precedent; the band-gate PUBLISHED leg\n" \
           "        # and the arithmetic-continuation facts below cover it).\n" \
           "        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,\n" \
           "                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,\n" \
           "                      31, 32, 33, 34):\n"
assert headA.count(old_loop) == 1, "prior-wave loop anchor not found verbatim"
headA_m = headA.replace(old_loop, new_loop)

# B: deps comment (+34 auto-join executed)
old_dep_comment = ("        # W35 finalize cumulative deps: W17..W33 outputs ALL PRESENT;\n"
                   "        # W34 has no registry row at this freeze (bm-b pre-scan pending\n"
                   "        # at their seat) -- when bm-b lands the W34 freeze+finalize,\n"
                   "        # the dep pin auto-joins +34 per the r531-1/r541 minimal-amendment\n"
                   "        # precedent (finalize runtime composes every registry key below\n"
                   "        # 35 = FAIL-CLOSED honest wait for the W34 output once registered).\n")
new_dep_comment = ("        # W35 finalize cumulative deps: W17..W33 outputs ALL PRESENT;\n"
                   "        # W34 registered at the bm-b r528 freeze adopted in this merge\n"
                   "        # -- the dep pin auto-joined +34 per the r531-1/r541 minimal-\n"
                   "        # amendment precedent (finalize runtime composes every registry\n"
                   "        # key below 35 = FAIL-CLOSED honest wait for the W34 output).\n")
assert headB.count(old_dep_comment) == 1, "deps comment anchor not found verbatim"
headB_m = headB.replace(old_dep_comment, new_dep_comment)

# shared2: dep loop header gains 34 (W35 face only)
shared2_m = shared2.replace("30, 31, 32, 33):", "30, 31, 32, 33, 34):")
assert shared2_m != shared2, "dep loop header amendment failed"

# C: wave-set assert list + message include 34
old_ws = ("        assert sorted(w for w in WAVE_CONFIGS if w < 35) == \\\n"
          "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n"
          "             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], \\\n"
          "            \"W35 prior-wave set must derive from registry keys (no 15, no 34)\"\n")
new_ws = ("        assert sorted(w for w in WAVE_CONFIGS if w < 35) == \\\n"
          "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n"
          "             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], \\\n"
          "            \"W35 prior-wave set must derive from registry keys (no 15, incl. 34)\"\n")
assert headC.count(old_ws) == 1, "wave-set anchor not found verbatim"
headC_m = headC.replace(old_ws, new_ws)

# ---- assemble: W34 block (mine, complete with tail) then W35 block (amended origin) ----
pre = raw[:starts[0]]
w34_block = mineA + shared1 + mineB + shared2 + mineC + pickle_finally
w35_block = headA_m + shared1 + headB_m + shared2_m + headC_m + post
merged = pre + w34_block + w35_block

# safety: no markers remain anywhere
for bad in ("<<<<<<< HEAD", "=======", ">>>>>>> b954d8ab2"):
    assert bad not in merged, f"marker remains: {bad}"
open(PATH, "w", encoding="utf-8", newline="").write(merged)
py_compile.compile(PATH, doraise=True)
print("CONSTRUCTIVE MERGE OK: W34 block then W35 block (+34 auto-join amendments applied)")
print(f"pre={len(pre)}B w34={len(w34_block)}B w35={len(w35_block)}B total={len(merged)}B (was {len(raw)}B)")
