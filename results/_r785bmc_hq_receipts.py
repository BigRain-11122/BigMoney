# -*- coding: utf-8 -*-
"""r785 bm-c decision-receipt rows -> HQ-FEEDBACK.md (append-only, utf-8).
D-20261009-01 item-3 pool-replenish dispatch -> F-20261009-01 (acceptance +
baseline read + supply plan, window 10-10 00:00);
D-20261009-02 QA pack per-machine suffix ruling -> F-20261009-02 (executed
this round: runner synced-named, window 10-10 00:00)."""
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

R1 = ("- F-20261009-01 [bm-c r785 " + NOW + "·决策回执面·D-20261009-01③ bigmoney "
      "备货池补货派单窗（10-10 00:00）承接回执+基线读数] **池补货承接：基线实读+真实供给"
      "计划落账，补货执行 r786 起分轮推进**——①基线读数（本轮实测）：runnable_pool.json "
      "408 entries **全 done·ready_unclaimed=0**（updated_at 2026-10-08T03:47:32 冻结"
      "至今·claimable_pool_lines=2 与 idle_trigger 一致）；②候选供给面诚实评估：moneyflow "
      "IC reference batch（watermark next_pick claimed）=panel blocked **非可即供**"
      "（results/moneyflow_update_status.json 实读：complete=false·53/5222 symbols·"
      "connection-level source-blocked 自 09-25·rank lane 10-08 22:20 fetch_failed="
      "RemoteDisconnected 复证·采集道宿主=bm-a 按 R31 车道律）；W192 引擎波（本机交互窗 "
      "CEO 填料令 23:51 领占·prereg 冻结 de1ad11f9）=引擎本地队列车道·席位 MSG 明文"
      "「burn = engine local queue, NOT pool」不计入池补货；③**真实供给计划**=S3 试用劳动"
      "力常设线触发条件三面坐实（板空〔fleet 票 0 open〕+池饿〔ready=0<floor 3〕+无在飞"
      "判决批）→ r786 起按 firm/TRIAL_LABOR_LAW 起草下一波候选试用期大考批（冻结语法生成"
      "→去重门 T-84s3→廉价初筛→存活者全量判决→真实活入池），池回 ≥10 目标在窗 10-10 "
      "00:00 内；④执行面分轮如实推进、到窗读数随班回执。状态=in-progress（承接+基线"
      "落账·执行 r786 起·窗 10-10 00:00）\n")

R2 = ("- F-20261009-02 [bm-c r785 " + NOW + "·决策回执面·D-20261009-02 QA 证据包路径"
      "机器后缀裁定执行回执（窗 10-10 00:00）] **runner 同步命名当窗执行毕**——"
      "scripts/qa_smoke_run.py per-machine 后缀落地：tag=qa/smoke-r<N>-<machine>.md+"
      "png=qa/equity-curve-r<N>-<machine>.png+log 同源（<machine>=fleet/machine.json "
      "machine_id 实读，本机实读验证=smoke-r786-bm-c.md/equity-curve-r786-bm-c.png）；"
      "py_compile rc0+模板实读三验过；**runner=仓内共享单源→三机随下次 pull 自然同步"
      "（bm-a/bm-b 零单机改动）**；存量历史包零改名（裁定落账前产物含本窗 det-100th "
      "qa/smoke-r785.md 存量留档·git 史保全）；轮号空间仍按机独立计数不变；charter "
      "命名律节=集团侧已落 docs/qa-smoke-test-charter.md（裁定文）。三机活体首证随各机"
      "下一包自然产生（bm-c 首证=r786 包 smoke-r786-bm-c.md）。状态=closed（执行+回执"
      "双落窗内·活体首证 r786 随包自证）\n")

path = REPO + r"\HQ-FEEDBACK.md"
before = open(path, "rb").read()
with open(path, "ab") as fh:
    fh.write((R1 + R2).encode("utf-8"))
after = open(path, "rb").read()
assert after.startswith(before) and after[len(before):] == (R1 + R2).encode("utf-8")
print("HQ receipts appended: +%dB (F-20261009-01 in-progress, F-20261009-02 closed)"
      % (len(after) - len(before)))
