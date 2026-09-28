"""r419 bm-a merge-back resolver 2 — memory files union.

CODELY.md: r327/r329 entry-level recipe — both sides rewrote tail in-place
(independent hot-cold integrations). Union = common prefix + ours tail
(renumber 八十九批->九十批, batch-71 renumber law, ours merges later)
+ theirs tail verbatim. 禁行级去重 (r311): lines kept verbatim per side.
archive 202609.md: base + ours suffix + theirs suffix (both pure tail-append,
prefix identity TRUE) — line-level union zero-loss.
"""
import subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    assert r.returncode == 0, (stage, path)
    return r.stdout.decode("utf-8")

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

# ---- archive 202609.md: suffix union ----
ARCH = "research/memory-archive/202609.md"
b = blob(1, ARCH); o = blob(2, ARCH); t = blob(3, ARCH)
assert o.startswith(b) and t.startswith(b), "archive prefix identity failed"
o_suf, t_suf = o[len(b):], t[len(b):]
union_arch = b + o_suf + t_suf
write(ARCH, union_arch)
nl = lambda s: s.count("\n")
print(f"archive: base={nl(b)} ours_suf={nl(o_suf)} theirs_suf={nl(t_suf)} "
      f"union={nl(union_arch)} zero_loss={nl(union_arch)==nl(b)+nl(o_suf)+nl(t_suf)}")
assert nl(union_arch) == nl(b) + nl(o_suf) + nl(t_suf)
subprocess.run(["git", "add", ARCH], check=True)

# ---- CODELY.md: entry-level union ----
C = "CODELY.md"
b = blob(1, C); o = blob(2, C); t = blob(3, C)
bl, ol, tl = b.split("\n"), o.split("\n"), t.split("\n")
# common prefix: identical leading lines (diagnostic said first-div idx 25)
i = 0
while i < min(len(ol), len(tl)) and ol[i] == tl[i]:
    i += 1
print(f"CODELY: common prefix lines={i} ours_tail={len(ol)-i} "
      f"theirs_tail={len(tl)-i}")
ours_tail = ol[i:]
theirs_tail = tl[i:]
# renumber ours' colliding batch number: 八十九批 -> 九十批 (batch-71 law)
ren = sum("坑律八十九批" in ln for ln in ours_tail)
assert ren == 1, f"expected 1 renumber target, got {ren}"
ours_tail = [ln.replace("坑律八十九批", "坑律九十批") for ln in ours_tail]
union = "\n".join(ol[:i] + ours_tail + theirs_tail)
if not union.endswith("\n"):
    union += "\n"
write(C, union)
ub = union.encode("utf-8")
print(f"CODELY union: lines={union.count(chr(10))} bytes={len(ub)} "
      f"(ours={len(o.encode())} theirs={len(t.encode())}) renumbered 八十九->九十 x1")
# entry-level bidirectional coverage: every tail line preserved verbatim
for ln in ours_tail + theirs_tail:
    assert ln in union, f"lost line: {ln[:60]!r}"
print("coverage check: all ours+theirs tail lines present verbatim OK")
subprocess.run(["git", "add", C], check=True)
print("memory union done")
