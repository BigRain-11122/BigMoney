# -*- coding: utf-8 -*-
"""r506 bm-a S7: state + heartbeat + round-report line (one-shot)."""
import json
import time
import datetime
import psutil

# ---- state-bm-a.json
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 506
st["last_round"] = 505
st["did"] = ("r506 bm-a: prior r506 session cut post-build pre-commit -> portfolio_book.py adopted per r471 "
             "(py_compile+selftest 31/31) -> multicore conversion (O-2026-09-30-2355 law-1: parallel_runner "
             "run_cells_parallel, min(worker_cap(),12), BLAS 1/worker, BelowNormal init, S-mp parity legs 5/5, "
             "autofill _runner_core_verdict=multiproc) -> prep PASS (12 workers, probe sha 50b77e2a == frozen pin, "
             "18 sleeves 6.6s) -> pool entry PORTFOLIO-BOOK-P1-BURN surgical 30+/1- -> daemon claimed + burned "
             "members 18/18 x2 (9.7s) -> config-stage real crash (_beat6m_book panel-vs-window index space, "
             "r471-adoption x W14-real-path pit) -> fix p->p-w0+1 + k-parity leg (37/37) -> real run 3s -> "
             "finalize judged-negative eligible 0/4 (determinism sha gate 4/4 match) -> prereg sec.7/8 backfilled "
             "-> T-138 done")
st["verify"] = ("smoke 47/47 + selftest 37/37 (31 adopted + 5 S-mp + 1 k-parity) + attrition guard CLEAN (4 "
                "ledgers, healed-2 historical) + S6 28 legs rc0 (reconcile ZERO-DRIFT streak 10/3 189 entries; "
                "holiday no-new-bar trigger group legally skipped; monthly trio already r496) + D-19 sha "
                "ED4E0EAB MATCH (r481 temp-clone recipe) + orders 133/133 zero unacked (double scan) + ledger "
                "368815->368819 +4")
st["next"] = ("r507: 10-03 RW-5 external-review unfreeze watch -> T-126 s1 REEVAL18 prereg (48h from unfreeze); "
              "W14/N1-W3 pool convergence watch (bm-b lanes); T-131 GM-signature gate hold; TRIAL_LABOR standing "
              "line: next wave prereg when board empties")
st["current_task"] = ("r506: PORTFOLIO_BOOK_P1 judged-negative closed (eligible 0/4, ledger +4, s3 not triggered); "
                      "combination-book L2 line closed this window -- reopen needs new prereg/new window")
st["last_round_at"] = "2026-10-01T08:2x+08:00"
st["updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no ->", st["round_no"])

# ---- heartbeat fleet/machines/bm-a.json
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
now = datetime.datetime.now().astimezone()
h["last_seen"] = now.strftime("%Y-%m-%dT%H:%M") + "x+08:00"
h["current_task"] = st["current_task"]
h["task"] = st["current_task"]
vm = psutil.virtual_memory()
h["cpu_cores"] = psutil.cpu_count()
h["cpu_pct"] = psutil.cpu_percent(interval=1)
h["free_ram_gb"] = round(vm.available / 1024**3, 1)
h["idle_ram_gb"] = round(vm.available / 1024**3, 1)
h["verdict"] = ("r506 closed: PORTFOLIO_BOOK_P1 judged-negative (0/4 eligible, diversification claim falsified "
                "this window, ledger +4); multicore conversion law-1 compliant; next = RW-5 unfreeze watch "
                "10-03 + pool convergence")
h["round_no"] = 506
epoch = int(time.time())
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now.isoformat(timespec="seconds")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat epoch int ok:", h2["heartbeat_epoch_utc"], h2["clock_read"])

# ---- round report line
line = ("2026-10-01T08:2x+08:00 | r506（猝死续作+同轮全链收口窗：前 r506 会话 ~07:45 猝死于 runner 构建完成与 commit 之间·"
        "半成品 scripts/portfolio_book.py 55KB 逐件验后收养零重做 r471）| dept:研究/策略+工程 | WM=insufficient_history"
        "（n=1 重采样中）+compute_audit supply_gap 旗如实（ready13=BM-B N1-W3 12 分片+本批·floor3 不破·点火 SLA 零违）| "
        "**主产品=PORTFOLIO_BOOK_P1 s2 烧批+判决同轮收口（judged-negative·eligible 0/4）**：①收养半成品 selftest 31/31 验后采纳"
        "②多核转换落地（O-2026-09-30-2355 law-1：parallel_runner run_cells_parallel·min(cap,12)·BLAS 1/worker·BelowNormal init·"
        "S-mp pool==inline 五腿 5/5·autofill _runner_core_verdict=multiproc 实证）③prep PASS（12 workers·探针同面 payload sha "
        "50b77e2a==冻结钉·18 袖盘 6.6s）④池入链 PORTFOLIO-BOOK-P1-BURN（外科 30+/1-·r289 律）⑤daemon 认领真烧 18/18 x2 9.7s "
        "⑥config 段真路径崩（_beat6m_book 面板空间位×窗空间书曲线索引混用 IndexError·r471 收养×r494 真跑交叉坑）→修 p→p−w0+1 索引翻译"
        "（零判据触碰）+k-parity 新腿 37/37→真跑 3s 完成 ⑦finalize 判决=determinism 门 4/4 sha match（多核字节恒等实证）+"
        "bh_fdr_q 全败（最优 0.50-EW p=0.0564→q=0.1934>0.10）+0.70-IVOL 分散差 −0.0799 负→**judged-negative eligible 0/4·"
        "§5 分散主张证伪诚实收线（δ=0.70 双配置 0.9521/0.5201 均<最强单员 1.6839）**·trials ledger 368,815→368,819 +4·"
        "gate_attrition judgment 行入册 08:15:26 ⑧prereg §7/§8 一次定稿回填（预测对账：选择面对/x2 衰减全败如实记·E1 面=无双跑门"
        "外可对账腿·以 sha 恒等门承担）⑨T-138 done（result_ref 齐·s3 不触发=0 eligible→无 TRIAL-BOOK-* 接线·重开须新预注册）| "
        "S6=28 腿 rc0（reconcile ZERO-DRIFT streak 10/3·189 entries·compute_audit v2.4.2·WM probe·update_daily/regime ORANGE d4/"
        "scorecard 6-28-7 卡/CALL-09-30 ORANGE_COOL 幂等·采集器假期 no-op 全合法·moneyflow rank+AH 分离后台 spawn·fundamental fresh"
        "·b_layer 过·promotion 0/22 诚实·marks 幂等 no-op×3·t35e export-09-30 再生·dscore/dreport faces5/ceo_live ORANGE cap50/"
        "build_status 10-432-6/token L2 0=host bm-a 执笔面·无新 bar=live.paper 触发组假日合法跳过·月首三件套 r496 已交零重跑）| "
        "S0.5 双扫=orders 133/133 零未回执+D-19 sha ED4E0EAB MATCH（r481 temp partial clone 配方·raw-blob 面）零新决策·"
        "orders.md 存照 239KB 同窗 | inbox 2 件均 GM 收件（0400 W3 供给 v1.1/048x LOWAMP VOID-vs-stands）非本机动作留位 | "
        "verify: smoke 47/47+selftest 37/37+attrition CLEAN（healed-2 历史）+自愈三件套（loop pin=8 Running 08:18 班·"
        "watchdog Ready 08:40·claw in sync）+心跳 epoch int 自证 | 坑律新条=收养半成品首烧坑（CODELY 已固化：selftest 全绿≠可烧·"
        "首烧前真跑 assembly 段·跨空间索引族必查）| 当前活=组合书线 L2 判负收口完毕+W14/N1-W3 池收敛看守；"
        "最近实物=results/portfolio_book/BOOK-2026-09-22.json+book_cells.csv+prereg §7/8 回填（08:1x·T-138 闭环）；"
        "下里程碑=10-03 RW-5 外审解冻→T-126 s1 REEVAL18 prereg（48h 自解冻起算）+10-02 晨报三机行·假窗无新 bar 维持至 10-08·窗≤48h | "
        "next: r507 RW-5 解冻看守+W14/N1-W3 收敛观察+T-131 GM 门守候+板空后 TRIAL_LABOR 供给波起草 [via bm-a]\n")
with open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
