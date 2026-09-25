# r201 memory: hot-cold reorg (D-20260925-01 watermark trigger) + new pitfall entry
# R156/R164 recipe: migration note at archive tail + migrated lines verbatim +
# hot-layer line order preserved + two-phase line-level zero-loss check.
import io, sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

raw = open(CODELY, "rb").read()
# detect EOL from first line ending
if raw.split(b"\n", 1)[0].endswith(b"\r"):
    eol = b"\r\n"
else:
    eol = b"\n"
text = raw.decode("utf-8")
NL = eol.decode()
lines = text.split(NL)
if lines and lines[-1] == "":
    trailing = True
    lines = lines[:-1]
else:
    trailing = False

MIG_PREFIXES = [
    "- [2026-09-25 14:5x] 坑律（bm-b r183·T-61 转移接收面",
    " - [2026-09-25 18:5x] 坑律（bm-a R182·guorn 基线建立",
]
NEW = ("- [2026-09-25 20:1x] 坑律（bm-b r201·中断 rebase 现场×autofill tick·P0/E1 自捕零外泄）："
       "**会话死于 mid-rebase（UU 未解）时 autofill tick 读工作树 marker 件→_load_state except 兜底 fresh"
       "→_save_state 把 49 条 launches 覆写成 1+无 owner 发射（r159 拉取滞后窗叠加=SHARD-2 双烧）**；"
       "修（6f2616f6）=tick 入口 mid-rebase/merge 三探针守卫（冲突树=诚实 no-op 零状态写零发射）"
       "+corrupt 件拒绝（存在件解析失败=exit 2 禁 fresh 兜底覆写）+S14/S14b/S14c 配对腿 23/23。"
       "连带：**rebase --continue 冲突已解后仍报「You must edit all merge conflicts」=误导报文，"
       "实因=无关已跟踪件未暂存**（tick 刚写的 p1d_gates 漂移，还原零信息损失后即过）；"
       "三方 union=stage2+stage3+现工作树（tick 覆写后的工作树是 20:00 发射记录唯一载体，"
       "r161 双源配方的工作树维度补篇）。指针=round_reports.md r201 行+Tools/autofill.py S14")

migrated = []
kept = []
for ln in lines:
    if any(ln.startswith(p) or ln.lstrip().startswith(p.strip()) and p.strip() in ln[:60]
           for p in MIG_PREFIXES):
        migrated.append(ln)
    else:
        kept.append(ln)
assert len(migrated) == 2, f"expected 2 migrated lines, got {len(migrated)}"
# phase 1: order/zero-loss check -- kept+migrated interleave must reconstruct cur
cur = [ln for ln in lines]
assert sorted(map(len, cur)) == sorted(map(len, kept + migrated)), "line-set drift"
i = j = 0
for ln in cur:
    if j < len(migrated) and ln == migrated[j]:
        j += 1
    else:
        assert ln == kept[i], f"order drift at {i}"
        i += 1
assert i == len(kept) and j == len(migrated), "interleave check failed"

out_lines = kept + [NEW]
out_text = NL.join(out_lines) + (NL if trailing else "")
open(CODELY, "wb").write(out_text.encode("utf-8"))

NOTE = ("- [2026-09-25 20:1x] 迁移注（bm-b r201 热冷整编·D-20260925-01④ 水位触发：append r201 坑律后越"
        " 50KB）：以下 2 条已闭一站式记录逐字迁入冷层（R156/R164 范式：迁出行逐字在档+热层行序保持+"
        "两段式核账 2/2）；热层留 r201 新坑律。检索按日期段。")
with open(ARCHIVE, "ab") as f:
    araw_tail_probe = open(ARCHIVE, "rb").read()
    aeol = b"\r\n" if araw_tail_probe.split(b"\n", 1)[0].endswith(b"\r") else b"\n"
    f.write(aeol + NOTE.encode("utf-8"))
    for m in migrated:
        f.write(aeol + m.encode("utf-8"))

# phase 2: verify on-disk result
raw2 = open(CODELY, "rb").read()
lines2 = raw2.decode("utf-8").replace("\r\n", "\n").split("\n")
kept_lf = [l.replace("\r", "") for l in kept]
assert lines2[:len(kept_lf)] == kept_lf, "phase-2 prefix mismatch"
assert lines2[len(kept_lf)] == NEW, "new entry not at tail"
for m in migrated:
    assert m not in lines2, "migrated line still in hot layer"
size = len(raw2)
print(f"reorg OK: hot {len(raw)}B -> {size}B (<50000: {size < 50000}); "
      f"migrated {len(migrated)} lines verbatim to archive; new entry appended")
