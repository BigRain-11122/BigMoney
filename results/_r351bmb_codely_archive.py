"""r351 bm-b: CODELY.md append + 当窗热冷整编 v2 (O-20260927-0230 ≤10KB).
v2 fix: entry blocks anchored AFTER the '### Reference' header only
(User-section rows are structurally exempt -- User 节元律不随批归档);
verification = three independent assertions (moved verbatim in archive,
kept verbatim in src, size under hard line).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")
HARD = 10240

NEW_ENTRY = ("- [2026-09-28 01:3x r351 bm-b] 坑律：tick claim/keepalive「读新」纪律不充分——树级落后窗"
 "（b5be80cd 实弹 00:52:51：tick 忠实读盘写盘，但本地树 fork 于 bm-c 00:41:57 入池之前，"
 "写回结构上不可能携带他机新池件→提交必经 rebase 重放税（会话 S7 三波）+本地盲池窗；"
 "model-blind 已有 r201/r331/r349 律族覆盖，tree-blind 是新面）。正典=pool-behind-origin defer 探针"
 "（fetch -q + git diff --quiet HEAD...origin/main -- 池路径，三 dot=只测 origin 在 fork 后动没动池，"
 "本地领先未推的 r290 滞留面不误伤；exit-code 面骑 _git 桩保 hermetic）→命中即缓写"
 "（bytes 还原零 git ops·refresh 幂等于 age gate·fire 门=push 成功 r199 不变）·探针故障 fail-open。"
 "指针=Tools/autofill.py _pool_origin_stale + selftest S15k/S15k2/S17i + commit afa02906。")

src = open(CODELY, "rb").read().decode("utf-8")
src_bytes = len(src.encode("utf-8"))
lines = src.split("\n")
ref_idx = next(i for i, l in enumerate(lines) if l.strip() == "### Reference")
starts = [i for i, l in enumerate(lines)
          if i > ref_idx and l.startswith("- [2026-")]
assert starts, "no pitlaw entries after ### Reference"
head = lines[:starts[0]]
tail_trailing = "\n" if lines and lines[-1] == "" else ""
if tail_trailing and lines[-1] == "":
    lines = lines[:-1]
    starts = [i for i in starts if i < len(lines)]
blocks = []
for n, i in enumerate(starts):
    j = starts[n + 1] if n + 1 < len(starts) else len(lines)
    blocks.append("\n".join(lines[i:j]))

blocks.append(NEW_ENTRY)

moved, kept = [], list(blocks)
while len(("\n".join(head) + "\n" + "".join(b + "\n" for b in kept))
          .encode("utf-8")) > HARD and kept:
    moved.append(kept.pop(0))
assert kept, "refusing to archive everything"
assert all(b is not NEW_ENTRY for b in moved), "new entry must stay"

new_text = "\n".join(head) + "\n" + "".join(b + "\n" for b in kept)
new_bytes = len(new_text.encode("utf-8"))

arch_note = ("\n## 坑律归档 2026-09-28 二十四批（r351 bm-b 窗·O-20260927-0230 ≤10KB 硬线当窗整编）\n\n"
             + "".join(b + "\n" for b in moved))
arch_prev = open(ARCHIVE, "rb").read().decode("utf-8") if os.path.exists(ARCHIVE) else ""

# -- three assertions BEFORE any write --
assert all(b in src for b in kept if b is not NEW_ENTRY), "kept verbatim"
assert all(b in src for b in moved), "moved came from src"
assert new_bytes <= HARD, f"still over hard line: {new_bytes}"
assert "### User" in new_text and "CEO 最高判据宣言" in new_text, "User row intact"

open(ARCHIVE, "wb").write((arch_prev + arch_note).encode("utf-8"))
open(CODELY, "wb").write(new_text.encode("utf-8"))
arch_now = open(ARCHIVE, "rb").read().decode("utf-8")
assert all(b in arch_now for b in moved), "moved verbatim landed in archive"
assert open(CODELY, "rb").read().decode("utf-8") == new_text, "byte-identical write"
print("src", src_bytes, "-> new", new_bytes, "| moved", len(moved),
      "blocks:", [b[:28] for b in moved])
print("OK")
