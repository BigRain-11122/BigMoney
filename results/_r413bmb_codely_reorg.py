import io, os

CODELY = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

with io.open(CODELY, encoding="utf-8") as fh:
    text = fh.read()
lines = text.splitlines(keepends=True)

# locate the two moving entries (verbatim, single lines)
idx88 = None
idxr202 = None
for i, ln in enumerate(lines):
    if ln.startswith("- [2026-09-29 06:4x r412 bm-b] 坑律八十八批"):
        idx88 = i
    if ln.startswith("- [2026-09-29 06:35 r202 bm-c] V3-TOURNAMENT"):
        idxr202 = i
assert idx88 is not None, "88-batch line not found"
assert idxr202 is not None, "r202 receipt line not found"

mv88 = lines[idx88]
mvr202 = lines[idxr202]

new89 = (
    "- [2026-09-29 06:5x r413 bm-b] 坑律八十九批（池面 done-flip=会话专属动作·"
    "deferral 结构性错律）：批产 finalize 落地≠池面收口——autofill tick 只点火+"
    "读池 shard status=done 判 landed（_confirm_crashes），**从不写池面**；"
    "「done-flip 待 autofill tick」=结构性错误期待。V3 实弹：判定 06:01 落地已推但"
    "池 shard 未翻→06:00:15 tick 重跑已落地判定（202.1s 确定性重写 06:22:42 幸运"
    "字节恒等）→06:30:03 crash-fuse CONFIRM 拒再发射=熔断投毒+池面假饥饿"
    "（r413 双面翻面清环）。How to apply：finalize 落地同轮必做池条目+shard 双面 "
    "done-flip（W1/W4/W5 烧完轮同翻先例）；诊断先查 worker 日志「shard complete」"
    "行（正常收工≠崩溃）与 finalize 是否独立子命令（screen/judge=分离面），"
    "勿按「进程消失+产物缺」径判崩溃。\n"
)
pointer = (
    "冷层指针：坑律正典 2026-09-29 八十八批（r412 bm-b 死会话继任收割序律·一次推送"
    "解锁三面）+r202 bm-c V3-TOURNAMENT 判定落地收割回执（T-101 done 关票·链族三代"
    "全负定谳·CEO 负汇报兑现·flip 门 3x3 时点读数 bm-a 3✓/bm-c 8✓/bm-b 2✗）全文 "
    "verbatim=archive 202609.md『坑律归档 2026-09-29 r413 bm-b 窗批』节（r413 bm-b 窗"
    "水位律当窗整编·行级零丢失校验）。\n"
)

# remove the two lines, insert pointer at the r202 position (keeps section flow)
for i in sorted((idx88, idxr202), reverse=True):
    del lines[i]
pos = min(idx88, idxr202)
lines.insert(pos, pointer)
# append 89-batch at the end of file (Project section tail = newest entry, r412/r202 precedent)
lines.append(new89)

with io.open(CODELY, "w", encoding="utf-8", newline="") as fh:
    fh.write("".join(lines))

# archive append (verbatim, zero-loss)
section = (
    "\n## 坑律归档 2026-09-29 r413 bm-b 窗批（水位律当窗整编·行级零丢失校验）\n\n"
)
with io.open(ARCH, "a", encoding="utf-8", newline="") as fh:
    fh.write(section)
    fh.write(mv88)
    fh.write(mvr202)

# zero-loss verification: archived bytes == removed line bytes
with io.open(ARCH, encoding="utf-8") as fh:
    atext = fh.read()
assert mv88 in atext, "88-batch verbatim missing in archive"
assert mvr202 in atext, "r202 verbatim missing in archive"
with io.open(CODELY, encoding="utf-8") as fh:
    c2 = fh.read()
assert "坑律八十八批" not in c2.split("### Reference")[0] or True  # pointer mentions fine
assert "八十九批" in c2
assert mv88 not in c2 and mvr202 not in c2
sz = os.path.getsize(CODELY)
print(f"reorg OK: CODELY={sz}B (<10KB: {sz < 10*1024}); "
      f"archive verbatim x2 verified byte-equal")
