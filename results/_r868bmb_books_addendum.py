# -*- coding: utf-8 -*-
"""r868 same-window harvest books addendum: state.json + heartbeat updated
to the finalize-landed facts (CRLF host face preserved); round-report
addendum line appended (LF, recent-writer face)."""
import json
import subprocess
import time
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

NOW_ACTIVE = ("r868 same-window harvest: N2-MP1 burned+finalized same round "
              "(daemon claim 07:38:09 bm-b, 1724/1724, finalize rc0: PASS=25 PARTIAL=43 "
              "FAIL=110 N/A=0; sec7/8 backfilled; registries closed)")
LATEST = ("r868: results/mp1_tsgate_p1.json + research/MP1_TSGATE.md (verdict face: "
          "25/43/110/0, price-level q10 family top reads OOS +1.1~1.3%/20d) + "
          "research/N2_MP1_PREREG.md sec7/8 backfilled + pool entry N2-MP1 (autofill "
          "claim 07:38:09, done-flip = daemon next tick per r497) + tech.md T24 done")
VERDICT = ("GREEN: r868 (N2-MP1 full-lifecycle same-round close: slice-2 runner+FROZEN "
           "v1.0 five-condition chain + pool entry + daemon burn + finalize verdict face "
           "PASS=25/PARTIAL=43/FAIL=110/N/A=0 + sec7/8 backfill + registries; sec5.2/5.3 "
           "prediction misses honestly disclosed; wave-counts generator pit healed "
           "in-window; smoke 49/49; behind=0)")
NEXT = ("r869 queue: pool done-flip verify (daemon tick r497 law) + GATE-RECHECK-MP1 "
        "registration per queue discipline (25 PASS gates independent-recheck candidacy, "
        "D6 adjacency audit + independent OOS recheck, price-level family cluster "
        "disclosure first) -> CODELY.md mini-split stays batched at next append -> W210 "
        "freeze watch (bm-a chain) -> moneyflow IC panel-ready watch (bm-a lane) -> "
        "O-20261011-0012 CPU-max maintained")

DID_ADD = (" SAME-WINDOW HARVEST: autofill tick claimed N2-MP1 07:38:09 (bm-b, origin-refs "
           "gate, 12 workers) -> burn 1724/1724 checkpoint complete -> finalize rc0: "
           "PASS=25/PARTIAL=43/FAIL=110/N/A=0 (1013 insts >=500 bars; price-level q10 "
           "family top reads OOS med_net +1.1~1.3%/20d pos_share 0.74-0.77; wave split "
           "W19 8/32/56 W20 17/11/54; M1 band 0/5/13 of 18; anchor 3341/390/149 in-run "
           "double-reproduced) -> sec7/8 backfilled (sec5.2/5.3 prediction misses "
           "disclosed: PASS band [0,12] actual 25, FAIL>=120 actual 110; calibration law = "
           "anchor prediction bands to same-mechanism realized rates) + TREASURE row + "
           "E54 methodology card + pit-ps generator-pit entry (verdict_counts_by-wave "
           "single-use generator zeroed non-PASS wave counts; totals correct via "
           "dict-view; per-gate faces intact; healed via _r868bmb_wave_heal.py with "
           "8+32+56+17+11+54==178 reconciliation) + tech.md T24 done (queue 1->0)")

for path in ("state.json", "fleet/machines/bm-b.json"):
    p = json.load(open(path, encoding="utf-8"))
    p["now_active"] = NOW_ACTIVE
    p["latest_artifact"] = LATEST
    p["verdict"] = VERDICT
    p["current_task"] = NEXT
    p["task"] = NEXT
    p["next"] = NEXT
    p["did"] = p["did"] + DID_ADD
    p["last_action"] = p["last_action"] + DID_ADD
    p["clock_read"] = NOW
    p["ts"] = NOW
    p["last_seen"] = NOW
    p["updated"] = NOW
    p["updated_at"] = NOW
    p["last_round_at"] = NOW
    p["last_action_at"] = NOW
    if path.endswith("bm-b.json"):
        p["heartbeat_epoch_utc"] = int(time.time())
        p["next_milestone"] = ("GATE-RECHECK-MP1 registration + independent recheck verdict "
                              "<=2026-10-15 (25 PASS gates, price-level family); pool "
                              "done-flip daemon tick verify r869")
    else:
        p["next_milestone"] = ("GATE-RECHECK-MP1 registration + independent recheck <=2026-10-15; "
                               "MP1 verdict face landed in-window (W20 sec.0 <=10-13 honored)")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(p, ensure_ascii=False, indent=1).replace("\n", "\r\n"))
    b = open(path, "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n"), path
    rp = json.loads(b.decode("utf-8"))
    assert rp["round"] == 868
    if path.endswith("bm-b.json"):
        assert isinstance(rp["heartbeat_epoch_utc"], int)
    st = subprocess.run(["git", "diff", "--numstat", path], capture_output=True, text=True)
    print(path, "->", st.stdout.strip())

LINE = (NOW + " | r868 bm-b 同窗收割补记 | 实况三行：当前活=N2-MP1 同窗全链闭环收口（daemon 认领 07:38:09→烧录 1,724/1,724→finalize rc0 判读面落盘）/最近实物=results/mp1_tsgate_p1.json+research/MP1_TSGATE.md（**PASS=25·PARTIAL=43·FAIL=110·N/A=0**·价格水位类 q10 门族主发现 OOS 净差中位 +1.1%~+1.3%/20d·锚 3341/390/149 in-run 双复现）/下个里程碑=GATE-RECHECK-MP1 独立复核批登记+判读 ≤10-15（25 PASS 门·价格水位族机械相关披露先行·D6 邻接审计+独立 OOS 复核·镜像 GATE-RECHECK-A158 先例） | §7/§8 已回填（§5.2/§5.3 预测 MISS 如实披露：PASS 带 [0,12] 实测 25·FAIL≥120 实测 110——预测带未锚定同机械先例实绩率·校准律入 E54 卡）| 波次分组 W19 8/32/56·W20 17/11/54（和=178 恒等）·M1 带 0/5/13=换用法独立假设实证 | 机制坑同窗治愈：verdict_counts_by-wave generator 单次消费坑（总计数经 dict 视图恒正确·逐门面完好·真值重算+双面 raw-text heal+对账 assert·pit-ps 新坑 r666 直写例外）| TREASURE 出入行+E54 方法论卡+tech.md T24 done（队列 1→0）| 池条目 done-flip=daemon 下 tick（r497 律·claim 已在 origin 41bb4463e）| 本地未达 origin commit 数=0（本补记 commit 后 push+fetch 自证）| 孤儿面=0 | next r869: pool done-flip 验证+GATE-RECHECK-MP1 登记起草窗→CODELY.md mini-split 续批于下次 append→W210 freeze watch 维持")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(LINE + "\n")
print("addendum line:", len(LINE), "chars")
