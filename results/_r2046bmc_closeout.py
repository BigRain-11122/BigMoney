# -*- coding: utf-8 -*-
"""r2046 closeout: append the round report row (single fresh read-modify-write)."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROW = (
    "| 2026-11-24T12:50+0800 | r2046 | "
    "**watermark: red=false / lane=healthy · 孤儿面=0**（py_faces=5 / resident_servers=1）。"
    "**新增文件面（竞争窗 rc=3·不动共享面）**：把 r2045 的「等 5 天 = 13.1 天超额」拆成逐年——"
    "`scripts/cash_shelf_year_by_year.py` + `results/cash_shelf_year_by_year.json` + "
    "`research/CASH_SHELF_YEAR_BY_YEAR.md` + 负控 `results/_r2046bmc_year_negative.py`。"
    "**读数一（同一份等待，年份不同差 6 倍）**：`511360` 在七年平均上 18.9 天，最好的一年 2021 只要 **10.5 天**，"
    "最差的一年 2025 要 **61.7 天**，最贴近当下的 2026 要 **23.0 天**；六个整年里只有 2021/2024 落在 20 天预算内"
    "（WAIT_FITS_ONLY_IN_GOOD_YEARS）。"
    "**读数二（副产物·报价翻转审计）**：`511360` 在 2023-09-08 单日跌 104.7bp、2023-09-11 就回到下跌前收盘价的 "
    "4.3bp 以内——35% 修复规则看不见、货币 ETF 读取器只抹掉下跌却留下回跳，窗口年化被虚高 **0.1677pp/年**；"
    "把两根 bar 都记零后窗口超额 3,088→**2,134 元/年**，排队从 13.1 天变 **18.9 天**（预算 20 天，余量剩 1.1 天而不是 6.9 天）。"
    "**读数三（负年份点名可数）**：`511380` 2020/2022/2023/2026 超额为负、`511180` 2022/2023/2026、"
    "`511010` 2020/2025、`511880` 七个整年全负；最新整年 2026 里 `511010` 只多赚 **+0.01pp**（r2042 的赢家今年几乎不赚），"
    "`511380` -16.11pp。"
    "**验证**：`--selftest` **21/21 PASS**；`run` rc0；`--check` **rc0（5 货架 / 35 货架年 / 1 翻转对逐格复算）**；"
    "负控 **9/9**（手改逐年超额 rc1 点名 code/year/field 且不带 STALE、上游一字节 rc3 STALE 且不带 CHECK FAILED、"
    "关掉翻转中性化 extra 回到污染线、预算放宽到 70 天判词翻面、缺面 STALE 不崩、四个发布件逐字节未动）。"
    "| S0: machine.json=bm-c；orphan_face_probe orphans=0 零杀；竞争探针 rc=3 CONTENTION（对端 interactive pid 51252 "
    "自 11-22 20:10 存活，轮首前 16 张共享面为他所写、重叠窗 0 张）→ 只落新增文件面、未改共享代码/数据面、"
    "未跑 S6 链与全量冒烟（连续第 4 轮推迟，如实记）。S0.5：orders 116 令 / 329 回执 / 零未回执；decisions.md 原字节 "
    "sha256 79e3083b85c130b8 与水位恒等（零新决策行）；fleet/inbox 0 件。S7：IterationLoop phase ok（pin=0，首燃 12:50）；"
    "LoopWatchdog 在位（S4U 仍待提权，carried）；两爪 CR 归一逐字节 MATCH；attrition 守卫 CLEAN（4 账本 / 3 处 healed）。"
    "| **CEO 过程可见面**：当前活＝把「等 5 天」从 13.1 天超额改成逐年算，并审计出一条被两种数据规则同时漏过的报价翻转；"
    "最近实物＝**K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\CASH_SHELF_YEAR_BY_YEAR.md**"
    "（2026-11-24 12:5x·511360 最好年 10.5 天 / 最差年 61.7 天 / 翻转审计后 18.9 天）；"
    "下个里程碑＝(a) 竞争窗关后二十三面接 S6 链腿 + 全量冒烟（≤48h）；(b) 511360 票面改用翻转中性口径（≤48h，需改共享面）。"
    "| **未验证（如实）**：①不重算滑点/在途 carry（继承 r2043/r2044）；②逐年超额是历史分段不是预测；"
    "③翻转审计只覆盖「单 bar 深跌 + 快速回原位」；④全量冒烟与 S6 链连续第 4 轮未跑。"
    "| 本地未达 origin commit 数=推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3。 |\n"
)

PATH = "fleet/round_reports-bm-c.md"
text = io.open(PATH, encoding="utf-8").read()
if "| r2046 |" in text:
    print("ALREADY PRESENT")
else:
    io.open(PATH, "a", encoding="utf-8", newline="\n").write(ROW)
    print("appended %d chars" % len(ROW))
