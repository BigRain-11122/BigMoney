line = (
    "\n- [2026-10-11 17:2x] [r888 bm-b] E16_ALPHAGEN_RG_CENSUS_P1 finalize：census_holds=true"
    "（obs family max |ICIR| 0.455 > null family p95 0.077·n_ok 200/200·"
    "results/alphagen_rg/CENSUS-2026-10-09.json·12/12 分片 autofill 链烧录~20min/片；"
    "prereg L85 回执腿——CODELY 主件 30,686/30,720B 满员，流水行按 D-20261024-01 路由落本档）"
    "——holds→N2 U3 channel-1 drafting window 开窗指针（judged 面若开走 PREREG_TEMPLATE 正门+D6>=0.7 拒收+出场轴显式门）；"
    "队列行 state/queue/explore.md E16 同轮翻面 done。\n"
)
with open("research/memory-archive/202610.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("appended", len(line.encode("utf-8")), "bytes")
