# -*- coding: utf-8 -*-
"""r862 bm-a round-close bookkeeping: pit direct-write + round report line +
state bump + heartbeat refresh. Fresh-read-modify-write per r806 law
(multi-writer files: never the replace tool for appends)."""
import json
import time
import datetime

# ---------- 1) pit direct-write (pit-git-staged.md, r830 precedent) ----------
PIT = r"research\pit-git-staged.md"
pit_entry = (
    "\n- [2026-10-08 04:4x r862 bm-a] **close 提交吞活写手 stderr 件锁 rebase 逃生链（r861 实弹·双窗治愈零损失）**："
    "r861 close 的 add -A 把分离判决进程（pid 81116 在跑）正持有句柄的 stderr 件（_r861bma_judge_finalize.err·0 字节空 blob）"
    "卷进提交——后续 S0 pull --rebase 换基 checkout-onto 需 unlink 该件，Windows 句柄锁→unlink 'Invalid argument' 失败留为未跟踪面"
    "→重放 pick 撞 'untracked would be overwritten' 停窗（abort 亦被同面拦）；正法=等进程退出解锁→删未跟踪同路径空件"
    "（内容与提交内空 blob 恒等零损失）→rebase --abort→checkout -- 恢复跟踪件→重跑 pull --rebase；"
    "根治律=收口窗 add -A 前必排活写手在持文件（stderr/日志重定向件=进程退出前禁入提交）。"
    "How to apply：分离长活与轮收口同窗时，收口提交定向 add 产出件、活写手件留给进程退出后的下一窗吸收。\n"
)
with open(PIT, "a", encoding="utf-8", newline="") as fh:
    fh.write(pit_entry)
print("pit appended:", len(pit_entry.encode("utf-8")), "B ->", PIT)

# ---------- 2) round report line (root canon per r844) ----------
now = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
line = (
    f"{now} | r862 | bm-a | dept:策略+工程 | watermark verdict: 绿 (red=false lane=healthy; engine ALIVE rc0 idle queue0; "
    "probe=board clear + W16 line in-flight consume this round) | 当前活: W16-JUDGE finalize 验证+消费收口（r861 遗产·<=06:30 限兑现）+ W181 席位链落地 | "
    "最近实物: results/trial_labor_w16/w16_judge.json + w16_intake.json @2026-10-08T04:48/05:0x + fleet/inbox/MSG-2026-10-08-0505-bma-w181-seat.md + "
    "results/_r862bma_w181_probe_receipt.json | 下个里程碑: W181 prereg build+freeze（两窗律 r797/r799·proj ledger 801,905+2,200/K 393,920+2,200）+ "
    "10-08 15:30 复市数据链 re-arm 首采+REGIME_GUARD v3 新bar enforce（窗≤今日收盘）| did: S0 双风暴治愈=①r861 close 含活写手 .err 件锁 rebase 停窗"
    "（unlink Invalid argument→untracked-block 第三态；等 finalize 进程 04:48 退出→删未跟踪空件→abort→checkout 恢复→重 rebase；坑已直写 pit-git-staged）"
    "②14-UU 批（6 ALL_FACES merge_lane_views+REPORT/LIVE 孪生 :2: origin-fresher+快照 take-new·_r862bma_rebase_resolve.py 留痕）+第二窗 5-UU"
    "（lhb 正典工具+dashboard/scorecard 4 面 :2: origin-fresher 04:49-50 整字节）+E42 author env 三行法 commit -F+continue 假拒第三态 r835 逃生"
    "（quit+branch -f 755dd45fb 复挂·余 3 churn pick=守护陈旧快照 live-wins 零损失跳过）+writer-pause 窗（SatEngine 停/复）churn-absorb x5；"
    "S0.5 orders 双扫零未回执+DEC/ORD 双水位 python raw-bytes 恒等（ee659451/2bb2ee75·K 缺席走实径 C:\\FluxGroup fallback）零动作；S1 smoke 49/49；"
    "S3 主产=W16-JUDGE finalize 验证（grammar 锚 ebf15822d2c8472e 恒等·40/40 判完·G1'v2 0/40 全灭→eligible_g2=0=prereg §5.3 众数零兑现"
    "（预告 [0,10]·OOS 双正 9/40·dd_ok 40/40·family_pbo patterns 0.3@9cells·trials 账本 802,278+40=802,318 LOWAMP-P1/P2 voids）→s4 intake 合法零产物"
    "（n_eligible=0·admitted=[]·rejected=[]·零引擎跑·零账本行·负结果照报律）+W181 pre-seat probe 5 腿全绿 AD（leg0 178 行 tail=W180·171st wave bm-a 97th·"
    "W180 账本头 801,905 机读；leg1 A 413_004..415_003 hops=1 阶梯第41例 E36（W180 B 带 412_804..413_003 拒 naive A 于其首）+B 415_004..415_203 hops=1 "
    "own-A 互斥保留走（naive B 413_004..413_203 落 own-A 内）；leg2 冲突 0；leg3 origin 空位；leg4 W182+ 投影 A 415_004..417_003/B 415_204..415_403）"
    "→seat MSG published=reserved 3 件 payload 推送；S6 38 门全 rc0（dualrun ZERO-DRIFT streak 51@408·复市前全门诚实 no-op cutoff 09-30·"
    "scorecard 6/28/7+REPORT/LIVE-2026-10-08/build_status 再生·token L2 0·attrition CLEAN 4 账本·moneyflow rank+ah_panel 分离 spawn 合法）；"
    "S7 quartet 绿+idle_trigger --worked idle_rounds=0 | verify: w16_judge/intake 机读键恒等+grammar 锚过；probe 5 腿断言全过+receipt 在仓；"
    "seat+consume 推送送达 fetch+rev-list 双向 0 自证（2931fe563..f8d127690）；smoke 49/49；S6 38/38 rc0；lhb reconcile ZERO-DRIFT | "
    "计分: 2（能跑/能看/能用实物=W16 判决终件+intake 零产物+W181 席位链三件套——负结果与常供线双实物增量）| 记账预算: 4/5（state+轮账行+心跳+pit 条）| "
    "宝藏捕获问: 本批零新方法零新宝藏（finalize/intake/probe=r859/r851 血统 verbatim 复用非新方法论·TREASURE/METHODOLOGY 零 append）| "
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 未触发·dec/ord snap 与 classify 草稿=本窗临时件 untracked 留位如实注记 r839 先例）| "
    "孤儿面=1（BigDomain 跨公司只读·round-zero 探针·r857 姿态维持）| 本地未达 origin commit 数=0（收尾 push 后 fetch 复核）| "
    "下轮指针: r863=W181 prereg build（xform W180→W181·facts=probe 回执+seat MSG·banned gate）+freeze 两窗律分窗+10-08 15:30 复市数据链 re-arm+"
    "trial-labor 线 W17 供给决策（W16 全灭后下一波语法起草 vs O-2315 意义门复核）\n"
)
with open(r"round_reports-bm-a.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(line)
print("round report appended:", len(line.encode("utf-8")), "B")

# ---------- 3) state bump ----------
st = json.load(open(r"state-bm-a.json", encoding="utf-8"))
st["round_no"] = 863
st["current_task"] = ("r862: W16-JUDGE consumed zero-eligible (judge+intake on origin); W181 seat published=reserved; "
                      "r863 = W181 prereg build (two-window law r797/r799) + 10-08 15:30 market-reopen data chain re-arm "
                      "+ trial-labor W17 supply decision")
st["did"] = ("r862: S0 double-storm heal (live-writer .err file lock -> wait-exit+delete-dup+abort+restore+re-rebase; "
             "14-UU + 5-UU batches canon-resolved; E42 author-env + r835 third-state escape; writer-pause window) + "
             "orders unacked=[] both sweeps + DEC/ORD hash identical zero action + smoke 49/49 + "
             "PRODUCT: W16-JUDGE finalize verified+consumed (40/40 judged, G1'v2 0/40 -> eligible_g2=0 lawful modal-zero "
             "per prereg sec5.3, trials ledger 802,318, s4 intake lawful-zero) + W181 seat chain (probe 5-legs ADMIT "
             "A 413_004..415_003 staircase 41st E36 / B 415_004..415_203 W141 leg2; seat MSG published=reserved) + "
             "S6 38/38 rc0 + pit direct-write pit-git-staged (live-writer stderr admission law) + idle --worked")
json.dump(st, open(r"state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state bumped: round_no=", st["round_no"])

# ---------- 4) heartbeat ----------
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
hb = json.load(open(r"fleet\machines\bm-a.json", encoding="utf-8"))
hb["last_seen"] = clock
hb["current_task"] = "W181 seat published; next W181 prereg build + 15:30 reopen re-arm"
hb["cpu_cores"] = 32
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["verdict"] = "green"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["ts"] = clock
json.dump(hb, open(r"fleet\machines\bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(r"fleet\machines\bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat: epoch int OK,", clock)
print("BOOKKEEPING_OK")
