# r411 bm-a closeout: CODELY pit-law 78 + round report + state + heartbeat
import json, time, datetime, os

now = datetime.datetime.now().astimezone()
ts_short = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

with open("CODELY.md", "a", encoding="utf-8") as f:
    f.write("\n- [%s] r411 bm-a 坑律七十八批（5x 核对漏检=轮末指针非承诺律）：r409 state next 明写「next 5x=r410 HANDOVER check」而 r410 did/commit 全无核对动作=指针写了≠执行了——r411 补做闭环（HANDOVER r410 补核对行已插：R406-410 窗综述+链 328,615 实读+池 107+产物 8/8 在位）。How to apply：接手轮 S2 必逐项核对上轮 state next 指针清单（写下的义务=必核项）；5x 轮 S7 state 写回前加机械自查「round_no%%5==0→HANDOVER 核对行已落?」，禁靠记忆。" % now.strftime("%Y-%m-%d %H:%M"))

line = (
    now.isoformat(timespec="seconds")
    + " | r411 bm-a (dept:总经办+工程·5x 核对补录轮) | WM first-line verdict: green (red=false; probe 03:13 insufficient_history 短窗合法态·local_batch_running=moneyflow rank pass+AH refresh 分离刷新在飞·板 0 open+W5-JUDGE lane=bm-b 点火待=非本机可烧) | did: S0-1 anchor bm-a + S0 clean pull + S0.5 orders 122/122 差集零未回执 + decisions 尾行 C-20260928-02 已回执零新行 + S1 smoke 26/26 + S2 job_list 0 open + fleet T-116=claimed bm-c s1（s2-s4 依赖 s1 不碰）+ 池 107 双源对账（共享面权威·七十七批执行）+ W5-JUDGE checkpoint absent=bm-b 未点火监视面 || 主活：**r410 漏 5x HANDOVER 核对=r411 补做**（r409 next 明写而 r410 未执行=指针非承诺教训；HANDOVER.md r410 补核对行插入总头首位：R406-410 窗综述〔T-115 claims-face gate+W5 generate fix-first 双 bug+W5 screen-finalize 3926+200 null p95 0.5164 survivors 372+ledger 324489->328615 +4126 入链+W6 volconf DRAFT freeze-pending〕+统一链 328,615 实读线性+池 107 条+产物 8/8 磁盘在位验证+下轮 5x=r415）+ S4 CODELY 坑律七十八批 || S6 36 legs rc=0（_r411bma_s6_chain.py 复用 r410 谱系：audit v2.4.1+WM probe+daily 0-new cutoff 09-28+regime ORANGE shadow breadth 0.83+scorecard 6/28/7+clock CALL-0928+LHB/heat/futures/repo/options cutoff 覆盖零网络 no-op+MF spawn rank pass+sinaMF 20td 窗内+astock/etf/revosc/minfeed/alloc/fund_prem 车道护栏 no-op+ths 同日幂等+AH refresh spawn 分离后台+fundamental 17.4h fresh-skip+b_layer all_pass+live.paper 6 员 OK+t35v PASS 零 pending+t24 22/22 drift0+promo 0/22 合法+aggr/grid/sysv1 幂等 no-op+export 0928+daily_scorecard+REPORT-20260929 faces=4 token=1+LIVE-20260929+build_status 432combos+token delta=0） || S7 自愈三查全绿（Loop Running pin :X8 next 3:28/Watchdog Ready 3:20/claw identical） | verify: smoke 26/26; S6 JSON 36/36 rc=0 nonzero=[]; chain head 328,615 live-read (w5_screen.json trials_ledger.total); pool 107 shared==lane 同谳; HANDOVER insert verified; CODELY <=10KB 线内 | next: (1) W5-JUDGE bm-b 点火监视（checkpoint judge_shard_0of1.jsonl 出现即 judge 烧中）->judge-finalize（48h CEO 报钟起）->intake->W6 freeze trigger 判定（full-chain+判官零在飞->FROZEN+seed 注册）；(2) moneyflow IC next_pick=claimed 等 panel complete（source-blocked 53/5222 自愈窗续）；(3) r415=下轮 5x HANDOVER（机械自查入 S7）；(4) 10-01 月首轮三件套+REGIME_GUARD v3 日期门自动激活\n"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)

st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 411
st["round"] = 411
st["loop_round"] = 411
st["did"] = ("r411: 5x HANDOVER check BACKFILL for r410 (r409 next-pointer said it, r410 never did -- pointer-written != executed, r411 closes the loop: HANDOVER r410 line inserted with R406-410 window recap + chain 328,615 live-read + pool 107 + products 8/8 on disk) + pit-law batch-78 (next-pointer obligation checklist law) + S6 36 legs rc=0; W5-JUDGE watch (bm-b lane, checkpoint absent=not ignited)")
st["verify"] = ("smoke 26/26; S6 36/36 rc=0 nonzero=[]; chain head 328,615 linear (324,489+4,126 W5-SCREEN); pool 107 shared==lane; orders 122/122; CODELY <=10KB")
st["next"] = ("(1) W5-JUDGE bm-b ignite watch -> judge-finalize (48h CEO clock) -> intake -> W6 freeze trigger; (2) moneyflow IC batch panel source-blocked self-heal watch (53/5222); (3) r415 next 5x HANDOVER (mechanical self-check in S7); (4) 10-01 month-first triple fire + REGIME_GUARD v3 date gate opens")
st["last_round_at"] = ts_short
st["current_task"] = "r411: 5x HANDOVER backfill for r410 landed; watch W5-JUDGE burn on bm-b"
st["updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
with open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
hb["machine_id"] = "bm-a"
hb["last_seen"] = ts_short
hb["current_task"] = "r411: 5x HANDOVER backfill for r410 + pit-law batch-78; watch W5-JUDGE ignite (bm-b lane) + moneyflow panel self-heal"
hb["verdict"] = "green; r410 5x HANDOVER backfill landed (chain 328,615, pool 107, orders 122/122); W5-JUDGE ready on bm-b lane awaiting their autofill ignite (checkpoint absent); W6 DRAFT freeze-pending same trigger; board 0 open; moneyflow IC next_pick=claimed panel source-blocked self-heal; S6 36 legs rc=0"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_short
hb["round_no"] = 411
hb["round"] = 411
hb["loop_round"] = 411
hb["task"] = "round-closed"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and chk["clock_read"] == ts_short
print("closeout written; epoch int OK:", chk["heartbeat_epoch_utc"], "| clock:", chk["clock_read"])
print("CODELY.md size:", os.path.getsize("CODELY.md"))
