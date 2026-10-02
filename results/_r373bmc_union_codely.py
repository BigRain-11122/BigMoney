# -*- coding: utf-8 -*-
# _r373bmc_union_codely.py -- CODELY.md union for r373 push (r581 bm-b law:
# my_files INTERSECT their_mod on append-only CODELY.md -> union, never
# whole-file snapshot). Blob space = LF (repo convention, autocrlf=true);
# working tree = CRLF. Union = origin blob base + my split delta (-16 pool
# entries, +pointer) with their 4 tail lines (3x r580 bm-b + 1x r581 bm-b)
# preserved verbatim.
import hashlib, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = ROOT + r"\CODELY.md"
CREATE_NO_WINDOW = 0x08000000

def git_show(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        sys.exit("git show FAIL %s: %s" % (spec, r.stderr.decode("utf-8", "replace")))
    return r.stdout

origin_lf = git_show("origin/main:CODELY.md")            # LF blob
assert origin_lf.count(b"\r") == 0
origin_md5 = hashlib.md5(origin_lf).hexdigest()
o_lines = origin_lf.decode("utf-8").split("\n")           # 150 items: 145 base + 4 tail + ""
assert len(o_lines) == 150 and o_lines[-1] == "", (len(o_lines), repr(o_lines[-1]))

# their 4 tail lines (LF space)
tail4 = o_lines[145:149]
assert sum("r580 bm-b" in t for t in tail4) == 3, tail4
assert sum("r581 bm-b" in t for t in tail4) == 1, tail4
assert o_lines[144].startswith("- [2026-10-02 15:3x r581 bm-a]"), o_lines[144][:60]

# my local working-tree file (CRLF) -> LF space
local_raw = open(SRC, "rb").read()
local_lf = local_raw.replace(b"\r\n", b"\n")
l_lines = local_lf.decode("utf-8").split("\n")
# local = base - 16 entries + pointer; base tail (last 3 content lines) must equal origin's
assert l_lines[127:130] == o_lines[142:145], "local tail drift vs origin base tail"
assert len(l_lines) == 131 and l_lines[-1] == "", (len(l_lines),)

# union = local lines + their tail4, inserted before trailing ""
union_lf_text = "\n".join(l_lines[:-1] + tail4 + [""])
union_lf = union_lf_text.encode("utf-8")
union_md5 = hashlib.md5(union_lf).hexdigest()

# byte accounting vs origin blob (LF space): -16 entries +pointer
# moved bytes = the 16 entry lines in LF = their CRLF sum (13,881B) - 16
MOVED_LF = sum(len(o_lines[i].encode("utf-8")) + 1 for i in
              [8, 12, 37, 39, 54, 59, 60, 62, 63, 64, 67, 70, 74, 78, 88, 89])
PTR_LF = None
for ln in l_lines:
    if ln.startswith("- ") and "池域拆件" in ln:
        PTR_LF = len(ln.encode("utf-8")) + 1
        break
assert PTR_LF is not None
assert MOVED_LF == 13881 - 16, MOVED_LF
assert PTR_LF == 535 - 1, PTR_LF
assert len(union_lf) == len(origin_lf) - MOVED_LF + PTR_LF, (len(union_lf), len(origin_lf))

# zero-loss: 16 moved entries absent from union (they live in pit-pool.md);
# their 4 tail lines present verbatim
union_set = set(union_lf_text.split("\n"))
for i in [8, 12, 37, 39, 54, 59, 60, 62, 63, 64, 67, 70, 74, 78, 88, 89]:
    assert o_lines[i] not in union_set, "moved entry %d still in union" % i
    assert o_lines[i].startswith("- "), o_lines[i][:50]
for t in tail4:
    assert t in union_set, "origin tail line lost!"
# sanity: my own bm-c line + both pin lines survive
assert any("r371 bm-c] lane_io origin-ref" in x for x in union_set)
assert any("§4 跳位语义钉死行" in x for x in union_set)

# write back as CRLF working tree (git add clean-filters to LF blob on commit)
union_crlf = union_lf.replace(b"\n", b"\r\n")
open(SRC, "wb").write(union_crlf)
print("origin blob (LF): %dB md5=%s" % (len(origin_lf), origin_md5))
print("union  blob (LF): %dB md5=%s  (= origin %dB - %dB moved16 + %dB pointer)" % (
    len(union_lf), union_md5, len(origin_lf), MOVED_LF, PTR_LF))
print("union  tree (CRLF): %dB written to CODELY.md" % len(union_crlf))
print("their tail4 verbatim: %s" % " | ".join(t[:28] for t in tail4))
print("UNION PASS: zero-loss (16->pit-pool.md, 4 theirs kept, pointer in)")
