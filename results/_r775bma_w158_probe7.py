# -*- coding: utf-8 -*-
import io

src = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()

# claim region physical text: from '"r772 bm-a] "' to '"+ T-141 s2 "'
cs = src.find('"r772 bm-a] "')
assert cs > 0
ce = src.find('"+ T-141 s2 "', cs)
claim = src[cs:ce]
io.open(r"results\_r775bma_w158_claim157.txt", "w", encoding="utf-8", newline="").write(claim)
print("claim len", len(claim), "lines", claim.count("\r\n"))
# indent of the line before T-141 s2
print("last 120 repr:", repr(claim[-120:]))

# mat pre / post full
w = src.find("# --- W157 materializer face")
t2 = src.find("# --- T-141 s2 lane face", w)
block = src[w:t2]
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
io.open(r"results\_r775bma_w158_pre_full.txt", "w", encoding="utf-8", newline="").write(pre)
io.open(r"results\_r775bma_w158_post_full.txt", "w", encoding="utf-8", newline="").write(post)
io.open(r"results\_r775bma_w158_chain_full.txt", "w", encoding="utf-8", newline="").write(chain)
print("pre", len(pre), "chain", len(chain), "post", len(post))

# pf.py projection segment physical text (malformed, pre-heal)
pfs = io.open(r"scripts\perpetual_faces.py", encoding="utf-8", newline="").read()
pi = pfs.find("    # W157+ projection")
pj = pfs.find("never transcribe r587).", pi) + len("never transcribe r587).")
proj = pfs[pi:pj]
io.open(r"results\_r775bma_w158_pfproj_orig.txt", "w", encoding="utf-8", newline="").write(proj)
print("pf proj len", len(proj), "repr head:", repr(proj[:100]))

# count critical needles across BOTH target files
for label, txt in (("pf.py", pfs), ("n1.py", src)):
    print(f"--- {label} needle counts ---")
    for n in ("362_204..362_003", "362_404..360_403", "362_204..364_203", "362_404..362_603",
              "jumps to 362_204", "157: {\"a\": (360_204", '"a_seed_base": 360_204',
              '"b_exit_seed_base": 362_204', "n3r1_used157", "w157_a", "w157_b"):
        print(f"  {n!r} -> {txt.count(n)}")
