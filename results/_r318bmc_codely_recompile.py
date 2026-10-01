"""r318 bm-c HARD-FIRST: CODELY.md hot-cold recompile (D-20260925-01④ >50KB watermark,
D-20260924-01 范式, r444 pointer-merge style, line-level zero-loss verify).

Movable set = flow/receipt rows ONLY (r504 水位注记: in-service pit laws stay hot;
threshold re-anchor = group/GM decision). This window's qualifying set = the two
O-1332 receipt rows (r517 bm-a + r317 bm-c) — pure duplicates of git-verifiable
canon (order file + round reports + heartbeat orders_ack), per 记忆入口四问门 ②.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202610.md")

PREFIX_A = "- [2026-10-01 13:4x r517 bm-a] O-1332"
PREFIX_B = "- [2026-10-01 13:3x r317 bm-c] O-1332 算力饱和恢复令回执行"

raw = open(CODELY, "rb").read()
text = raw.decode("utf-8")
before_bytes = len(raw)

# split keeping line endings, byte-exact reassembly
lines = text.splitlines(keepends=True)


def find_rows(prefix):
    hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    assert len(hits) == 1, f"prefix {prefix!r}: expected 1 line, got {hits}"
    return hits[0]

ia = find_rows(PREFIX_A)
ib = find_rows(PREFIX_B)
row_a = lines[ia].rstrip("\r\n")
row_b = lines[ib].rstrip("\r\n")
assert "\n" not in row_a and "\r" not in row_a
assert "\n" not in row_b and "\r" not in row_b

keep = [ln for i, ln in enumerate(lines) if i not in (ia, ib)]
new_text = "".join(keep)

# ---- zero-loss verify (line multiset: original == new + removed x1 each) ----
assert sorted(lines) == sorted(keep + [lines[ia], lines[ib]]), "line multiset zero-loss check FAILED"
assert new_text.count(PREFIX_A) == 0 and new_text.count(PREFIX_B) == 0
assert row_a in text and row_b in text  # sanity: they were there

# ---- archive append (r444 范式 section) ----
araw = open(ARCH, "rb").read()
atext = araw.decode("utf-8")
eol = "\r\n" if atext.count("\r\n") * 2 > atext.count("\n") else "\n"
section = (
    eol + "## 热冷整编 2026-10-01 r318 bm-c 窗批" + eol + eol
    + "（D-20260925-01④ 50KB 水位触发·r444 范式·行级零丢失校验；本窗批可迁集=O-1332 双回执行"
    "〔r517 bm-a+r317 bm-c·正典=fleet/orders/O-20261001-1332-bm-c.md+双机轮报告+心跳 orders_ack 已全载·"
    "记忆入口四问门②复述禁令〕；余热层=在役坑律正典·结构性注记沿用 r504 指针行——阈值重锚=集团/GM 裁定面，"
    "各机勿为字节数归档在役律）" + eol + eol
    + row_a + eol + row_b + eol
)
new_atext = atext + section
assert new_atext.startswith(atext), "archive prefix lost"
open(ARCH, "wb").write(new_atext.encode("utf-8"))

open(CODELY, "wb").write(new_text.encode("utf-8"))
chk = open(CODELY, "rb").read().decode("utf-8")
assert chk == new_text, "CODELY re-read mismatch"
achk = open(ARCH, "rb").read().decode("utf-8")
assert achk == new_atext, "archive re-read mismatch"
assert row_a in achk and row_b in achk, "moved rows not verbatim in archive"

print(f"CODELY.md: {before_bytes} -> {os.path.getsize(CODELY)} bytes (-{before_bytes - os.path.getsize(CODELY)})")
print(f"archive 202610.md: {len(araw)} -> {os.path.getsize(ARCH)} bytes")
print("moved rows: 2 (r517 bm-a O-1332 receipt, r317 bm-c O-1332 receipt)")
print("RECOMPILE-OK zero-loss verified (multiset equal, rows verbatim in archive)")
