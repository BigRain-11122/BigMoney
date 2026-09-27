# results/_r144bmc_fold35.py -- batch-35 hot-cold archival (r144 bm-c window)
# Trigger: post-append CODELY.md 10,258B > 10,240B hard line (watermark law:
# fold in-window). Oldest hot entries r389-CRLF + r365 (07:1x storm wave)
# migrate verbatim to archive 202609.md; pointer + migration record kept.
# Laws: r209 byte reads (BOM preserved by byte-faithful line ops), r361 parse
# gate, r365 atomic single write, line-level zero-loss both directions.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CP = os.path.join(ROOT, "CODELY.md")
AP = os.path.join(ROOT, "research", "memory-archive", "202609.md")
S = lambda t: t.encode()

with open(CP, "rb") as fh:
    codely = fh.read()
with open(AP, "rb") as fh:
    arch = fh.read()
nl = b"\r\n" if b"\r\n" in codely[:4096] else b"\n"
assert codely.startswith(b"\xef\xbb\xbf"), "BOM lost before fold"
assert S("三十五批") not in codely, "batch-35 pointer already present"
assert S("坑律归档 2026-09-28 三十五批") not in arch, "batch-35 section present"

lines = codely.splitlines(keepends=True)
def pick(prefix):
    idx = [i for i, ln in enumerate(lines)
           if ln.rstrip(b"\r\n").startswith(S(prefix))]
    assert len(idx) == 1, f"{prefix[:26]}... x{len(idx)}"
    return idx[0], lines[idx[0]].rstrip(b"\r\n")

iA, eA = pick("- [2026-09-28 07:1x r389 bm-a] 坑律：**文本模式")
iB, eB = pick("- [2026-09-28 07:1x r365 bm-b] 坑律：**resolver")
assert iA != iB
kept = [ln for i, ln in enumerate(lines) if i not in (iA, iB)]
out = []
for ln in kept:
    if ln.strip() == b"" and out and out[-1].strip() == b"":
        continue
    out.append(ln)
codely_new = b"".join(out)

ptr35 = (S("冷层指针：坑律正典 2026-09-28 三十五批（r144 bm-c 窗·水位律当窗整编：")
         + S("CODELY union 10,258B 超 ≤10KB 硬线）：r389 文本模式字节恒等假象 CRLF 血统律 / ")
         + S("r365 resolver 原子写+悬对象恢复律 两条全文 verbatim=")
         + S("archive 202609.md『坑律归档 2026-09-28 三十五批』节（行级零丢失校验）。"))
i34 = [i for i, ln in enumerate(out)
       if ln.rstrip(b"\r\n").startswith(S("冷层指针：坑律正典 2026-09-28 三十四批"))]
assert len(i34) == 1, f"batch-34 pointer x{len(i34)}"
out.insert(i34[0] + 1, ptr35 + nl)
codely_new = b"".join(out)

assert eA not in codely_new and eB not in codely_new, "entries still hot"
assert codely_new.startswith(b"\xef\xbb\xbf"), "BOM lost in fold"
assert b"<<<<<<<" not in codely_new and b">>>>>>>" not in codely_new
codely_new.decode("utf-8")
assert len(codely_new) <= 10240, f"still over: {len(codely_new)}B"

nl_a = b"\r\n" if b"\r\n" in arch[:4096] else b"\n"
section = (nl_a
           + S("## 坑律归档 2026-09-28 三十五批（r144 bm-c 窗·水位律当窗整编：")
           + S("CODELY union 10,258B 超 ≤10KB 硬线）") + nl_a + nl_a
           + eA + nl_a + nl_a
           + eB + nl_a + nl_a
           + S("> 迁移记录：三十五批=两条件（r389 文本模式字节恒等假象 CRLF 血统律/")
           + S("r365 resolver 原子写+悬对象恢复律）自 CODELY.md 热层 verbatim 外迁")
           + S("（行级零丢失校验）；热层留三十五批指针行，检索按日期段。") + nl_a)
arch_new = arch
if not arch_new.endswith(nl_a):
    arch_new += nl_a
arch_new += section
arch_new.decode("utf-8")
assert b"<<<<<<<" not in arch_new and b">>>>>>>" not in arch_new

old_set = [ln.rstrip(b"\r\n") for ln in lines if ln.strip()]
new_set = [ln.rstrip(b"\r\n") for ln in codely_new.splitlines() if ln.strip()]
folded = {eA, eB}
lost = [ln for ln in old_set if ln not in folded and ln not in set(new_set)]
assert not lost, f"hot-line loss: {lost[:2]}"

with open(CP, "wb") as fh:
    fh.write(codely_new)
with open(AP, "wb") as fh:
    fh.write(arch_new)
print(f"CODELY.md: {len(codely)}B -> {len(codely_new)}B (hard line OK, BOM kept)")
print(f"archive: {len(arch)}B -> {len(arch_new)}B (batch-35)")
print(f"folded verbatim: r389-CRLF {len(eA)}B + r365 {len(eB)}B; zero-loss pass")
