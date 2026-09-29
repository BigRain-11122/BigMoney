# Hot/cold re-arch v2 (fail-closed first run corrected): r431 row is
# verbatim-in-archive (pure demotion note); r443 row differs from the
# archive r440-batch copy (hot layer carries the later amended text with
# the r445 closing parenthetical) -> migrate the FULL hot row verbatim
# into this window-batch section, then drop from hot layer. Zero-loss:
# every dropped row text byte-present in archive post-write.
import io, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CODELY = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

cod = io.open(CODELY, encoding="utf-8").read()
arc = io.open(ARCH, encoding="utf-8").read()

DROP_PREFIXES = [
    "- [2026-09-29 15:5x r431 bm-b]",
    "- [2026-09-29 19:4x r443 bm-a]",
]
dropped = []
kept = []
for l in cod.splitlines(keepends=True):
    if any(l.startswith(p) for p in DROP_PREFIXES):
        dropped.append(l)
    else:
        kept.append(l)
assert len(dropped) == 2, f"expected 2 drops, got {len(dropped)}"
cod_new = "".join(kept)

r431_row = next(l for l in dropped if l.startswith(DROP_PREFIXES[0]))
r443_row = next(l for l in dropped if l.startswith(DROP_PREFIXES[1]))
# r431 full text already verbatim in archive (verified in v1 run)
assert r431_row.strip() in arc, "r431 not verbatim in archive"
# r443 hot row is the amended later version -> verbatim migration required
r443_migration = "\n" + r443_row.rstrip("\n") + "\n"

receipt = """

## 热冷整编 2026-09-29 r441 bm-b 窗批（CODELY.md 10,451B 复超 ≤10KB 硬线当窗即办·行级零丢失）

- 迁移记录（r431 bm-b 探针条件率 NaN 归桶伪影律行）：全文已于『热冷整编 2026-09-29 r440 bm-b 窗批』节 verbatim 在档（v1 运行 assert 通过），本节只记降级不复制文本；CODELY.md 冷层指针行（r433/r431/r443/r438/r233 五条）继续携带指针不变。
- verbatim 迁移（r443 bm-a 跨索引 reindex 静默全 NaN+日期键混型空交集坑行）：热层行为 r445 A12 关闭兑现后的增补版（与 r440 bm-b 窗批节旧版存在尾部差异·v1 运行 fail-closed 拦截实证），全文 verbatim 迁入本节为唯一全文位：
""" + r443_migration + """- 判定留热面：r442 双坑律压缩行=bm-a r443 窗批刻意热留（law carried by attrition）不动；r444 fork-point 行操作面活跃不动；r441 bm-b W11 撞带竞态律新条留热（W12 起草面）。校验=被删行文本逐字在本档在场（脚本 assert）+水位回线。
"""
arc_new = arc.rstrip("\n") + receipt
io.open(CODELY, "w", encoding="utf-8", newline="\n").write(cod_new)
io.open(ARCH, "w", encoding="utf-8", newline="\n").write(arc_new + "\n")

cod_chk = io.open(CODELY, encoding="utf-8").read()
arc_chk = io.open(ARCH, encoding="utf-8").read()
for l in dropped:
    assert l.strip() in arc_chk, f"post-check: dropped text not in archive: {l[:50]}"
    assert l.strip() not in cod_chk, f"post-check: drop leaked: {l[:50]}"
print("re-arch v2 done. CODELY.md:", os.path.getsize(CODELY), "B | archive:", os.path.getsize(ARCH), "B")
print("rows dropped:", len(dropped), "| zero-loss verified")
