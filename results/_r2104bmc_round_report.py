import io, datetime, sys
p = "round_reports-bm-c.md"
line = (
    "2026-11-25T22:1x+08:00 | r2104 | bm-c | "
    "**CONTENTION 轮**（证据 `results/_repo_write_contention.bm-c.json`：rc3，2 宿主存活〔98008@20:02 interactive + 本窗 97704@22:00〕，"
    "开工前 3 张共享面已被别宿主写过、重叠窗内不可归因 11 张；工作树脏 1,949 件）→ 按 r1907 只落新增文件面，"
    "禁改共享面、禁重跑 S6 链；state/心跳为多宿主共写态面，本窗不碰。"
    "watermark verdict=**绿**（`results/watermark_red.json` red=false lane=healthy）；孤儿面=0（`results/_orphan_face_probe.bm-c.json`；py_faces=9）。"
    "三行面：当前活=carry 暂停规则定价面完工；最近实物=`results/idx_fut_carry_pause_price.json`（2026-11-25T22:12+08:00）；"
    "下个里程碑=把「连续 N 根确认」写进策略文档与 policy_engine（需独占窗，≤48h）。"
    "**PRODUCT**：把 r2103 明列的未做项「停一次值多少钱」结掉——不再用正态近似算概率，而是把写死的规则**套进两条腿自己的日序列**"
    "（`idx_fut_carry_risk.product_spread`，因果序=close t 的窗决定 t+1 的暴露）。实测：**IC 3 次停牌／6 个停牌日／让掉 1.03 pp/年，"
    "IM 3 次／4 日／让掉 2.16 pp/年**；而**回撤没有变浅反而更深**（IC −5.64%→−8.19%，IM −5.05%→−8.30%），因为停掉的正是反弹那几根。"
    "根因量化：三次触发（2024-01-22／2024-02-05／2024-12-27，两腿同日）之后那一根平均 **+2.30（IC）/ +3.05（IM）pp**，"
    "而普通一根只有 +0.035/+0.040 pp，**次日为正占比 100%**——写死的 −2pp 是**反弹探测器**，不是断路器。"
    "可执行修法已验证：同一条线加「**连续 3 根都在线下才停**」→ 两腿都 0 次停牌、0 代价（本段历史一次都不会误伤）。"
    "对照面：宽线 −3.6pp 在 IC 只 1 次/让掉 −0.07pp、IM 0 次——r2103 的 2.5% 尾线在真实历史里几乎是常数。"
    "**验证**：`--selftest` 14/14；`check` rc0（漂移说 STALE、同输入不符说 CHECK FAILED）；负控 `results/_r2104bmc_pause_price_negative.py` "
    "**5/5 ALL_CONTROLS_PASS**（真坏腿会触发且省钱 +5.17pp／关规则=恒等／always-paused 天花板／恢复条款／从面上两数独立重算 cost）；"
    "跨面口径一致 IC 8.6423% vs risk 面 8.642%（差 0.0003pp）。**本窗两枚自捕**：①`rolling_cum` 用小数量纲却和 −2pp 比，"
    "首版 6 个阈值全 0 次停牌（空表格即症状）→ 改 pp 硬算；②年化分母写死 252（本部惯例 244）读出 8.94% vs risk 面 8.64%"
    "（两把尺子）→ 改 import `idx_fut_basis.TRADING_DAYS` 并把跨面对照写成面上永久字段 `cross_face`。"
    "**送达**：commit **e00c07d368** 已直推 origin/main（9439881c60..e00c07d368，非 FF 未发生）；fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0/0**；"
    "`git ls-tree -r --name-only origin/main` 核验 **6/6** 件在位（scripts/idx_fut_carry_pause_price.py、results/idx_fut_carry_pause_price.json、"
    "research/IDX_FUT_CARRY_PAUSE_PRICE.md、qa/carry-pause-price-r2104.md、results/_r2104bmc_pause_price_negative.py、"
    "results/_r2104bmc_pause_price_negative.json）→ **本地未达 origin commit 数=0**。"
    "下轮指针（干净树首件事）：①r2099 的三张 11-23 carry 面仍未重生（CONTENTION 期间禁写共享面）→ 重生后跑 "
    "`python scripts\\idx_fut_carry_one_lot_ruler.py check` 期望 ONE_RULER；②把「连续 3 根确认」写进 `research/STRATEGY-20261125.md §四` 与 "
    "`scripts/policy_engine.py`（本轮属共享面，未动）；③把本面与 `policy_trigger_audit` 一起接进 `Tools/s6_chain_bmc.py`（check-only 腿）。"
    "本轮记账=轮报告 2 处（正文+本行）；未动 state/心跳（对端仍持有，round_no 由下一个拿到独占窗的执行体推进）。\n"
)
with io.open(p, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)
print("appended", len(line), "chars")
