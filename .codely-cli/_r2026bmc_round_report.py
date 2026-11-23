import io
import os

PATH = os.path.join("fleet", "round_reports-bm-c.md")
LINE = (
    "| 2026-11-24 05:1x | r2026（**竞争探针 rc=3 CONTENTION·只落新增文件面**·把「默认档」写成可执行件："
    "一单位 beta 在什么预算下站得住、什么条件下才准换掉） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=3 / resident_servers=1=ComfyUI 空闲）。"
    "**产品（产品优先律）**：r2023 定价、r2024 换日频尺、r2025 赛马九条规则，三轮都留了同一件事没做——"
    "**没人说这本书默认拿多少去对冲，也没人说什么时候可以不用它**。本面只回答这两问，全部读数照抄父面已发布 cell，零重拟合。"
    "**读数一（默认档=一单位 beta，即 90.13% 账面）**：beta=0.9013，k=1.00 → 对冲名义 = **90.13% 的账面**"
    "（保证金/可借券/强制召回不在本面建模，如实标注）。"
    "**读数二（默认档的余量，逐档印）**：10% 档 -9.89pp、15% 档 -4.89pp（两档**没有任何规则**站得住，"
    "限制是预算不是档位——「把档位调小去凑一个谁都凑不上的预算」不是风控，是对一个付不出的数做算术）；"
    "20% 档 **只剩 +0.11pp**（p=0.69，约三成重采样会破）；25% 档 +5.11pp（p=0.87）。"
    "**读数三（九条规则常设表）**：RETIRED=B_PERIOD（四档全破）、ROBUST=A_PERIOD/MAX_SHARPE/MID_DAILY"
    "（在有规则站得住的档全站住）、CONDITIONAL=A_DAILY/B_DAILY/B_MARGIN/MIN_IS_DD、DEFAULT=FIXED_ONE——"
    "下一轮读者不必重跑赛马就知道该用哪条。"
    "**读数四（换档测试：三条件全过才换，结果 NO SWAP EARNED）**：25% 档父面判 FITTING_HELPS，可 "
    "**B_DAILY 年化 15.87% vs 默认 9.82%（+6.05pp）而守预算概率 0.242 vs 0.873**——多出来的收益是"
    "「一个你预测不了更多的数」，不是更好的数；A_PERIOD（+3.06pp）p 0.768 同样低于默认，MIN_IS_DD 的 p 略高但年化更低"
    " → **没有任何拟合规则同时满足三条件**。｜"
    "**验证证据**：`--selftest` **25/25 PASS**（摘要忽略运行时戳但看得见读数改动 / RETIRED-CONDITIONAL-ROBUST-DEFAULT 四态 / "
    "只在无规则站住的档里成立不算站住 / 余量正负 / k=0 归零 / 判词四态阶梯 / 换档三条件逐条单因子 / 四条行为腿："
    "真 check 在父面移动时读 STALE 且不说 CHECK FAILED、在篡改读数时读 CHECK FAILED 且不说 STALE、手改页面报红、缺规则报红不崩）；"
    "`run` rc0（evidence_cutoff **2026-11-20**，beta 0.9013）→ `results/astock_veto_hedge_default.json` + "
    "`research/ASTOCK_VETO_HEDGE_DEFAULT.md`；`check` **rc0**（136 项读数从父面 cell 重推 + 页面逐字节）。"
    "**负控 `results/_r2026bmc_hedge_default_negative.py` 11/11 PASS**（原样绿 / 改回撤 / 翻规则判词 / 翻换档结论 / "
    "改今日名义额 / 改头条判词 / 手改页面 / 父面移动读 STALE / 缺规则不崩 / 面不可读不崩 / 负控跑完发布面仍绿）。｜"
    "**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=3 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（2 宿主：本宿 pid 76120；对端 interactive pid 51252＝11-22 20:10 起常驻，"
    "22 张共享面在轮首前被对端写；重叠窗 0 张）→ 只落新增文件面，未改共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。｜"
    "**S0.5 双扫**：`orders_ack_scan` 差集=0（116 令 / 329 回执）；集团 `git cat-file blob origin/main:docs/decisions.md` "
    "**原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零动作；orders.md 原字节 sha 亦与水位相等；"
    "fleet/inbox 0 件。｜"
    "**S1（诚实边界）**：全量 smoke 已在本窗启动（后台 `python -u -m smoke_test`），本轮收口时**尚未返回**，"
    "且它会写 `logs/smoke_legs.json`（共享面）→ 本轮**不宣称全绿**；本面以 25/25 selftest + 11/11 负控 + run/check 双 rc0 背书。｜"
    "**S6**：未跑（链腿与链产物=对端写的共享面）。｜"
    "**S7**：`state round_no 2025→2026`（rounds_done 1961→1962，round_no_prev 留痕）；心跳经 `Tools/heartbeat_write.py apply` "
    "合并写（ack 329 保持、GPU 族自动重述同一探针）；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，首燃 05:10 未动）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；`pre-commit`/`pre-push` 与 "
    "`Tools/git-hooks/` 逐字节（CR 归一）**MATCH**。｜"
    "**CEO 过程可见面**：当前活＝把「默认拿多少去对冲」写成一条可执行指令，并写死「什么条件下才准换掉它」；"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_DEFAULT.md`"
    "（2026-11-24 05:1x·默认=一单位 beta=**90.13% 账面**；20% 预算只剩 **+0.11pp** 余量、p=0.69；"
    "25% 档拟合多赚 6.05pp 但守预算概率从 0.873 掉到 0.242 → **NO SWAP EARNED**）"
    "＋`results\\astock_veto_hedge_default.json`＋`scripts\\astock_veto_hedge_default.py`（selftest 25/25）"
    "＋`results\\_r2026bmc_hedge_default_negative.py`（负控 11/11）；"
    "下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；（b）**把「90.13% 账面」翻成资金与手数**："
    "这条指令现在说名义占比，账户还不知道要卖多少手、占用多少保证金、借券够不够——接父面的可持仓与融券面把它算成一张"
    "下单前的检查单（≤48h）。｜"
    "**未验证（如实）**：①对冲名义占比未含保证金/可借券/召回风险；②默认档的 p=0.69 是 34 期重采样的一次估计，不是分布保证；"
    "③换档测试只在 25% 档做（最松档），更紧档位的换档问题被「没有规则站得住」掩盖；④全量 smoke 与 S6 未跑（竞争窗），"
    "本面尚未接链；⑤本面是口径/指令件，不是可交易信号。｜"
    "**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
    "（无方法论新增：把「默认档」从无到有写成一条带换档条件的指令，属证据与载体）。 |\n"
)

with io.open(PATH, "r", encoding="utf-8", newline="") as fh:
    body = fh.read()
nl = "\r\n" if "\r\n" in body else "\n"
if not body.endswith(nl):
    body += nl
body += LINE.replace("\n", nl)
with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(body)
print("appended", len(LINE), "chars; eol", repr(nl))
