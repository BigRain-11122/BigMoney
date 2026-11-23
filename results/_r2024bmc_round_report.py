import json

ROW = (
    "| 2026-11-24 04:3x | r2024（**竞争探针 rc=3 CONTENTION·只落新增文件面**·回撤预算换到日频盯市这把尺上重算） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=6 / resident_servers=1=ComfyUI 空闲）。"
    "**产品（产品优先律）**：r2023 把「要买多少保险」做成了一张按回撤预算查的价格表，判 `BUDGET_HOLDS_OUT_OF_SAMPLE`——但它自己的 spec 里写着一句 `drawdown: on the book's own 20-bar period curve, not a daily mark-to-market`。"
    "预算是一个账户每天睁眼都要坐过去的东西，20 根 bar 看一次等于说「只要每个月的最后一天不难受就不算难受」。本轮把同一本书、同一把 beta、同一个 77 期，**逐交易日盯市**重算，两条规则在两把尺上各读一遍。"
    "**读数一（更细的尺只会看到更多，不会看到更少）**：日频回撤 / 期间回撤的中位数是 **1.335x**（最狠 1.511x，在 k=0.50）；k=0 的账面本身 25.92% → **34.17%**。这条不是精度噪声，是期间内曾经发生过、期间曲线看不见的亏。"
    "**读数二（20% 预算在两把尺上是两个答案）**：期间尺上规则 A 选 **k=0.65**、样本外 **14.64% 守住**（就是 r2023 的判词）；日频尺上规则 A 选 **k=1.10**，样本外 **20.74% 击穿**——判 `DAILY_MARKS_BREACH_THE_BUDGET`。"
    "上半句的意思是：日频尺下样本内回撤对 k 更敏感，规则 A（预算内年化最高）就会多买保险；多买的那部分在样本内是对的，出了样本就是错的。"
    "**读数三（10% 预算从来买不到）**：期间尺给的样本内地板是 9.80%，日频尺是 **12.07%**——10% 预算在日频口径下网格上任何一档都不达标，判 `BUDGET_UNREACHABLE_ON_DAILY_MARKS`（不是「选错了档」，是「这个预算不存在」）。"
    "**读数四（预算到底能买到多少，用事后最优印出来）**：全网格样本外日频回撤最低 **18.07%（k=0.75，事后挑）**，最高 51.05%（k=2.00，过度对冲把空头的波动买回来）——20% 预算的真实答案是「勉强够，但要事后才知道该买 0.75」，而两条规则都选不到它。"
    "**读数五（规则 B 也守不住）**：预算优先的最小档（0.20 预算 → k=0.35）样本外 **21.71%**，比规则 A 选的 1.10 更差——在这个面上「少买」不是保守，是少削回撤；风险优先规则只在 25% 预算那一格守住。"
    "｜**验证证据**：`--selftest` **18/18 PASS**（回撤原语两条 / 入场日因子把期间精确落在 1+net=1.0123 / k=0 逐项复现账面 / 日频臂第 20 根等于 arm_series 公式 gap 0.00e+00 / 期间看似走平却藏着 6% 的洞 / 规则 A 取预算内最高收益而非最高收益 / 规则 B 取最小可行 / 不可达返回 None / 判词三态 / 放大判词三态 / 缺价期不按免费对冲 / 自相矛盾的判词可检出 / 窗口按期间自己的日期切且按比值步进）；"
    "`run` rc0（77 期 / 1540 个盯市日，evidence_cutoff **2026-11-20**，期间恒等式最大缺口 **5.1e-15**）→ `results/astock_veto_hedge_daily.json` + `research/ASTOCK_VETO_HEDGE_DAILY.md`；"
    "`check` **rc0**（4 个预算判词逐格重判 + 41 条曲线单调性 + 三窗口存在性与「全窗不浅于子窗」+ 放大比逐条重算）。"
    "**锚腿（这条最重要）**：把 k=0.65 与 k=1.00 两臂 **77×2=154 期**逐个与本仓 `arm_series` 对上，最大缺口 **5.2e-15**；期间尺重推的规则 A 仍是 **k=0.65 == r2023 的 0.65**——说明日频尺量的就是那本书，不是别的书。"
    "**负控 `results/_r2024bmc_hedge_daily_negative.py` 9/9 PASS**（翻判词 / 把日频回撤压到期间回撤以下 / 谎报放大比 / 改期间回撤 / 截断曲线 / 删掉整张曲线表 → 全部 CHECK FAILED；原样 rc0；每次还原后真面逐字节未动且仍绿），"
    "**并当场抓到一枚真缺陷**：首版 `check` 在曲线表被删时直接 KeyError 崩掉，且不校验每条曲线的三个窗口——崩掉的自检等于没有自检；已修为「缺面/缺窗口一律 CHECK FAILED」，并把「全窗回撤不浅于任一子窗」写成可断言的不变量。"
    "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=6 **orphans=0** 零杀；`repo_write_contention` **rc=3 CONTENTION**（2 宿主存活：pid 51252＝11-22 20:10 起的 interactive 常驻，本宿 63940；27 张共享面在本轮开始前被对端写，重叠窗内 0 张）→ 按 r1927 只落**新增文件面**，未改共享代码/数据面、未跑 S6 链、未跑全量 smoke；fetch 后 0 ahead / 0 behind。"
    "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零动作；fleet/inbox 0 件；无新增 O 令。"
    "｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是对端写的共享面，竞争窗不覆盖）；本轮以 18/18 selftest + 9/9 负控 + run/check 双 rc0 + 154 期锚腿背书，**不宣称全绿**。"
    "｜**S6**：未跑（链腿与链产物为共享面）。"
    "｜**S7**：`state round_no 2023→2024`（rounds_done +1，round_no_prev 留痕 2023）；心跳经 `Tools/heartbeat_write.py apply` 合并写；`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/24 04:25 未动）；`attrition_ledger_guard scan` **CLEAN**（4 账本，2 处历史缩行 healed 注记照录）；`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）比对。"
    "｜**CEO 过程可见面**：当前活＝把回撤预算从「20 根 bar 看一次」换成真实账户的日频盯市，看「守住了」这句话还成不成立；"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_DAILY.md`（2026-11-24 04:3x·日频尺严 1.335x；20% 预算期间尺 14.64% 守住 vs 日频尺 20.74% 击穿；10% 预算日频不可达，地板 12.07%；事后最优 18.07%@k=0.75）＋`results\\astock_veto_hedge_daily.json`＋`scripts\\astock_veto_hedge_daily.py`（selftest 18/18）＋`results\\_r2024bmc_hedge_daily_negative.py`（负控 9/9）；"
    "下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；（b）**日频预算 × 期间选档的交叉规则**：日频尺下规则 A 系统性买过头，下一步测「用日频定预算、用期间选档」能否两窗都守（≤48h）。"
    "｜**未验证（如实）**：①逐日盯市仍是「入场日等权、期内不调仓」的固定股数篮子，不是真实每日再平衡；②日频未建模追保与强平，只说跌到多深、不说券商会在这个深度平你；③期间内缺印的个股按上一笔印带上，未做停牌/退市处理；④仍是 77 期（IS 43 / OOS 34），「守住/击穿」是一次观测不是分布；⑤预算与 k 网格与 r2023 保持一致，未搜最优；⑥本面是口径/证据件不是可交易策略；⑦全量 smoke 与 S6 未跑（竞争窗），本面尚未接链。"
    "｜**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把一个已发布的预算换到真实盯市尺上重算，属证据与载体）。 |\n"
)

path = "fleet/round_reports-bm-c.md"
with open(path, encoding="utf-8") as fh:
    body = fh.read()
assert body.endswith("\n")
with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(body + ROW)
print("appended %d chars; file now %d chars" % (len(ROW), len(body) + len(ROW)))
