# results/_r144bmc_fold.py -- batch-34 hot-cold archival (r144 bm-c window)
# Trigger: post-union CODELY.md 10,895B > 10,240B hard line (watermark law:
# fold in-window, never wait for the monthly pass). Oldest hot entries
# r141/r142 (06:5x wave) migrate verbatim to archive 202609.md per the
# batch-32/33 precedent; pointer line + migration record kept.
# Laws: r209 byte reads, r361 parse gate, r365 atomic single write,
# line-level zero-loss verification both directions.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CP = os.path.join(ROOT, "CODELY.md")
AP = os.path.join(ROOT, "research", "memory-archive", "202609.md")

with open(CP, "rb") as fh:
    codely = fh.read()
with open(AP, "rb") as fh:
    arch = fh.read()

nl = b"\r\n" if b"\r\n" in codely[:4096] else b"\n"
S = lambda t: t.encode()

assert S("三十四批") not in codely, "batch-34 pointer already present"
assert S("坑律归档 2026-09-28 三十四批") not in arch, "batch-34 section already present"

lines = codely.splitlines(keepends=True)
def is_r141(ln):
    return ln.rstrip(b"\r\n").startswith(S("- [2026-09-28 06:5x r141 bm-c] 坑律"))
def is_r142(ln):
    return ln.rstrip(b"\r\n").startswith(S("- [2026-09-28 06:5x r142 bm-c] 坑律"))

i141 = [i for i, ln in enumerate(lines) if is_r141(ln)]
i142 = [i for i, ln in enumerate(lines) if is_r142(ln)]
assert len(i141) == 1 and len(i142) == 1, f"r141 x{len(i141)} r142 x{len(i142)}"
e141 = lines[i141[0]].rstrip(b"\r\n")
e142 = lines[i142[0]].rstrip(b"\r\n")

# remove the two entry lines, then collapse any doubled blank lines
kept = [ln for i, ln in enumerate(lines) if i not in (i141[0], i142[0])]
out = []
for ln in kept:
    if ln.strip() == b"" and out and out[-1].strip() == b"":
        continue
    out.append(ln)
codely_new = b"".join(out)

# insert batch-34 pointer right after the (collision-noted) batch-33 pointer
ptr34 = (S("冷层指针：坑律正典 2026-09-28 三十四批（r144 bm-c 窗·水位律当窗整编：")
         + S("CODELY union 10,895B 超 ≤10KB 硬线）：r141 CLI 子命令分发表零参调用+池分片键唯一律 / ")
         + S("r142 crash-fuse 静默死盲窗断言律 两条全文 verbatim=")
         + S("archive 202609.md『坑律归档 2026-09-28 三十四批』节（行级零丢失校验）。"))
i33 = [i for i, ln in enumerate(out)
       if ln.rstrip(b"\r\n").startswith(S("冷层指针：坑律正典 2026-09-28 三十三批"))]
assert len(i33) == 1, f"batch-33 pointer x{len(i33)}"
out.insert(i33[0] + 1, ptr34 + nl)
codely_new = b"".join(out)

assert e141 not in codely_new and e142 not in codely_new, "entries still hot"
assert b"<<<<<<<" not in codely_new and b">>>>>>>" not in codely_new
codely_new.decode("utf-8")
assert len(codely_new) <= 10240, f"still over hard line: {len(codely_new)}B"

# archive: append batch-34 section verbatim (header + entries + record)
nl_a = b"\r\n" if b"\r\n" in arch[:4096] else b"\n"
section = (nl_a
           + S("## 坑律归档 2026-09-28 三十四批（r144 bm-c 窗·水位律当窗整编：")
           + S("CODELY union 10,895B 超 ≤10KB 硬线）") + nl_a + nl_a
           + e141 + nl_a + nl_a
           + e142 + nl_a + nl_a
           + S("> 迁移记录：三十四批=两条件（r141 CLI 子命令分发表零参调用+池分片键唯一律/")
           + S("r142 crash-fuse 静默死盲窗断言律）自 CODELY.md 热层 verbatim 外迁")
           + S("（行级零丢失校验）；热层留三十四批指针行，检索按日期段。") + nl_a)
assert e141 in section and e142 in section, "entries not in archive section"
arch_new = arch
if not arch_new.endswith(nl_a):
    arch_new += nl_a
arch_new += section
arch_new.decode("utf-8")
assert b"<<<<<<<" not in arch_new and b">>>>>>>" not in arch_new

# line-level zero-loss: every hot line except the 2 folded entries survives
old_set = [ln.rstrip(b"\r\n") for ln in lines if ln.strip()]
new_set = [ln.rstrip(b"\r\n") for ln in codely_new.splitlines() if ln.strip()]
folded = {e141, e142}
lost = [ln for ln in old_set if ln not in folded
        and ln not in set(new_set)
        and not ln.startswith(S("冷层指针：坑律正典 2026-09-28 三十三批"))]
# batch-33 pointer line was note-modified in the union step -> prefix check
lost = [ln for ln in lost
        if not any(ml.startswith(ln) for ml in new_set)]
assert not lost, f"hot-line loss: {lost[:2]}"

with open(CP, "wb") as fh:
    fh.write(codely_new)
with open(AP, "wb") as fh:
    fh.write(arch_new)

print(f"CODELY.md: {len(codely)}B -> {len(codely_new)}B (hard line OK)")
print(f"archive 202609.md: {len(arch)}B -> {len(arch_new)}B (batch-34 +yield-section)")
print(f"folded verbatim: r141 {len(e141)}B + r142 {len(e142)}B; zero-loss audit pass")
