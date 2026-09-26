"""r243 hot-cold memory reorg (D-20260925-01④ water-level trigger, 50.7KB>50KB).

Move the consumed overnight batch (CODELY.md Reference entries L8-L52,
2026-09-26 00:2x..09:3x, 45 law/record lines) verbatim into
research/memory-archive/202609.md; keep recent-window entries
(06:0x+ active tickets T-70/T-74/T-77/T-78 + User meta-law + cold-layer
pointer) in the hot layer. Line-level zero-loss verification (R156 pattern).
"""
import io
import os

P_HOT = "CODELY.md"
P_COLD = "research/memory-archive/202609.md"

hot_lines = io.open(P_HOT, encoding="utf-8").read().splitlines()
cold_txt = io.open(P_COLD, encoding="utf-8").read()
cold_n_before = len(cold_txt.splitlines())

# batch = 1-based L8..L52 (0-based 7..51), verified by content probes
BATCH = hot_lines[7:52]
assert len(BATCH) == 45, len(BATCH)
assert "[2026-09-26 00:2x]" in BATCH[0][:30], BATCH[0][:60]
assert "[2026-09-26 09:3x] 坑律（bm-b r237·compute_audit" in BATCH[-1][:60], BATCH[-1][:60]
# keep-set sanity: recent window + meta lines stay
keep = [l for i, l in enumerate(hot_lines) if not (7 <= i <= 51)]
assert any("实战出真知" in l for l in keep), "User meta-law must stay"
assert any("冷层指针" in l for l in keep), "cold-layer pointer must stay"
assert sum(1 for l in keep if "[2026-09-2" in l[:30]) >= 12, "recent window"

header = (
    " - [2026-09-26 11:5x] 热冷整编执行记录（bm-a R243·D-20260925-01④ 水位"
    "触发 50.7KB>50KB 当窗即办）：下 45 条=09-26 00:2x→09:3x 夜批（T-70 pilot"
    " 双臂/T-57/T-64/T-68/T-72/T-35 闭票流水+数据面收线+坑律族），自热层"
    " CODELY.md 逐字整编入本档（行级零丢失：每条原文逐字落档+git 全史双通道）；"
    "留热=近窗活跃票（T-70 10-09 窗/T-74/T-77/T-78）+User 元律+冷层指针；"
    "resolver 族坑律的正典面已由 .codely-cli 技能 bigmoney-conflict-resolve 承载。")

with io.open(P_COLD, "a", encoding="utf-8", newline="") as fh:
    fh.write(header + "\n")
    for l in BATCH:
        fh.write(l + "\n")

new_hot = "\n".join(keep) + "\n"
io.open(P_HOT, "w", encoding="utf-8", newline="").write(new_hot)

# ---- line-level zero-loss verification ----
cold_after = io.open(P_COLD, encoding="utf-8").read()
cold_lines_after = cold_after.splitlines()
hot_after = io.open(P_HOT, encoding="utf-8").read()
moved = 0
for l in BATCH:
    assert l in cold_after, "MISSING IN COLD: " + l[:60]
    assert l not in hot_after, "STILL IN HOT: " + l[:60]
    moved += 1
n_cold_gain = len(cold_lines_after) - cold_n_before
assert n_cold_gain == 1 + 45, n_cold_gain          # header + 45 lines
assert moved == 45
hot_ref_after = sum(1 for l in hot_after.splitlines()
                    if l.startswith(" - ["))
print(f"moved {moved} lines to cold; cold {cold_n_before} -> "
      f"{len(cold_lines_after)} (+{n_cold_gain})")
print(f"hot size: {os.path.getsize(P_HOT)} bytes "
      f"({os.path.getsize(P_HOT)/1000:.1f} KB decimal); "
      f"hot reference entries now: {hot_ref_after}")
print("ZERO-LOSS VERIFY OK")
