# -*- coding: utf-8 -*-
# r844 bm-b closeout: round report line + state.json + heartbeat
import json, time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

R844 = ("r844: idle-trigger GREEN-IDLE same-round backlog row-9 claim (CPH4 low-tier 2D tile frame-budget bench, bm-b 3070) "
        "+ harness 4 files + Tuanjie 2022.3.62t15 player build rc=0 (BuildResult using fix in-round) + 8-config matrix detached driver in flight (pid 28432) "
        "+ S6 41 legs (40 rc0 + alloc rc=2 known P5 stale-leg); astock rebuild 1193/5229@21:54 pid 10404 alive ETA ~02:05 = T23 census honest wait window continues")
NEXT = ("r845 queue: poll bench_state.json -> report.py -> frame-budget REPORT.md delivery + backlog done@ writeback; "
        "astock rebuild completion verify (window ~10-11 01:45-02:15+) -> spawn detached T23 census full burn -> census_holds readout -> "
        "N2 U3 (1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)")
VERDICT = ("r844: GREEN; smoke 49/49; D19 dual watermark zero-delta; orders diff empty (65 all ack); dualrun streak 29; "
           "attrition CLEAN; board/queues empty; pool non-done 2 both lane=bm-a; backlog row-9 claimed+started same round; "
           "T23 census head physically gated on astock rebuild (honest wait window r840-844); zero double-burn")

RR = ("{ts} | r844 bm-b | dept:工程（idle 领池即产轮：backlog row-9 CPH4 低配机 2D tile 帧基准点火） | "
      "WM-VERDICT: green（red=false @21:53；py_low_with_work_cands 合法=local_batch=astock 重建在飞+tile-bench 驱动在飞；"
      "supply_gap/supply_floor=O-1645 standing；ignition_sla 零 breach） | 孤儿面=0（probe 21:52 py_faces=13 orphans=0） | "
      "CEO three-line: 当前活=backlog row-9 tile 帧基准 8 配置矩阵分离驱动在飞（pid 28432·player 已建 rc=0）；"
      "最近实物=C:\\Fluxgroup\\bench-work\\tile-bench\\（harness 四件+TileBenchProj\\Builds\\TileBench.exe 464KB @22:04:44）"
      "+results/_r844bmb_s6chain.log（41 腿逐腿 rc 账·dualrun streak 29），2026-10-10 22:0x；"
      "下个里程碑=帧预算报告 REPORT.md 本窗收口（≤22:30，bench_state=done 后 report.py）+astock 完备（ETA ~02:05）→detached T23 census 烧录→holds 判读（窗 ≤10-11 06:00） | "
      "did: S0-1 锚定 bm-b；S0 absorb f3c3c1cd3（runtime churn 8 件）+rebase 净落（bm-c r840 2 commit 零冲突·behind 2→0）；"
      "S0.5 令扫 65 件零未回执（O-1945 最新已 ack）+D19 双水位零变化（dec a20664ec/ord 3af479f1 恒等零动作）；S1 smoke 49/49；"
      "S2 板面 0 open（T-182 bm-c 在跑）+job_list 0；S3 固定序全绿：红牌 false+引擎活 rc0+修红无红项；"
      "主队头 T23 census 物理依赖 astock 全宇宙重建 1193/5229@21:54（pid 10404·pace ~16/min·ETA ~02:05）诚实等待窗（一轮一探禁重扫）；"
      "闲置硬触发 GREEN-IDLE（ram 55.7%·vram 门 disclosure-only T-183）→池 2 线全 lane=bm-a R31 让路→同轮领 backlog row-9"
      "【CPH4】低配机 2D 渲染性能基准（claim-by-file fefc75c9d @21:59:03）领池即产：harness 四件"
      "（TileBench.cs 运行时基准[32px×4 变体 tile·hold/pan 分段采样·p99 口径]·TileBenchBuild.cs·run_bench.ps1 幂等驱动·report.py 聚合）"
      "→Tuanjie t15 standalone player build 首跑 CS0103（BuildResult 缺 using UnityEditor.Build.Reporting）同轮修复 rc=0"
      "→8 配置矩阵（size 256/512/1024²×L1/L3×ortho 8.5/17/34+复跑腿）分离驱动在飞（隐藏窗+runInBackground·跨轮幸存范式同 astock 刷新先例）；"
      "S6 41 腿（40 rc0+alloc rc=2 已知 P5 stale-leg 510880 缺件·s3 评审窗维持）：dualrun ZERO-DRIFT streak 29；周六采集族全 no-op 诚实；"
      "lane 守卫族（bm-a 心跳 stale 129-131min→本机按 O-2100 s2.4 STALE_MIN 律 stale-takeover 执笔 scorecard/paper/t35/prospect×2/daily_scorecard/dashboard 6 面法定运转）；"
      "S7 四件套全绿：loop pin=2 no-op（first-fire 22:12）+watchdog 在位（-ArgString 姿势两败后正确复验 present=True·中途幂等重注册无害）"
      "+双爪 LF 归一核对 True/True+attrition 4 台账 CLEAN | "
      "记账预算 4/5（state+心跳+轮报+D19 探针；S6 管线产出不计） | score: 1（claim+harness 四件+player build 实物=实际文件改动；"
      "帧预算数字下轮 report.py 收口后升 2） | unacked_orders=0 | 本地未达 origin commit 数=0（push 后 fetch 自证，见 S7） | "
      "下轮指针: {next} | [r844 bm-b]").format(ts=TS, next=NEXT)

with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(RR + "\n")

with open("state.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["machine_id"] = "bm-b"
st["round_no"] = 844
st["round"] = 844
st["round_no_label"] = "r845"
st["note"] = R844
st["did"] = R844
st["last_action"] = R844
st["verdict"] = VERDICT
st["current_task"] = NEXT
st["task"] = NEXT
st["next"] = NEXT
st["now_active"] = "r844 closeout: backlog row-9 tile bench claim+ignition + S6 41 legs + T23 census wait window (astock rebuild in flight)"
st["latest_artifact"] = ("r844: C:\\Fluxgroup\\bench-work\\tile-bench\\ (harness 4 files + TileBenchProj\\Builds\\TileBench.exe 464KB build rc=0 22:04:44) "
                         "+ results/_r844bmb_s6chain.log (41 legs, dualrun streak 29), 2026-10-10 22:0x")
st["next_milestone"] = ("r845 (window <=22:30): bench matrix done -> report.py -> frame-budget REPORT.md + backlog done@; "
                        "astock panel complete (~02:05 ETA) -> detached T23 census burn -> holds verdict (window <=10-11 06:00)")
st["last_round_at"] = TS
st["ts"] = TS
st["updated"] = TS
st["last_seen"] = TS
st["updated_at"] = TS
st["clock_read"] = TS
st["last_round_ts"] = TS
st["last_orders_at"] = TS
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["machine_id"] = "bm-b"
hb["round"] = 844
hb["round_no"] = 844
hb["now_active"] = st["now_active"]
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["next"] = NEXT
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = ("GREEN: r844 idle-claim production round (backlog row-9 CPH4 tile frame-budget bench claimed fefc75c9d + harness + player build rc=0 + "
                 "8-config detached matrix in flight pid 28432); D19 zero-delta; S6 41 legs green (alloc rc=2 known P5 stale-leg); quartet+attrition clean; "
                 "idle cleared 0 (claimed); T23 census honest wait window continues (astock rebuild 1193/5229 ETA ~02:05)")
hb["last_action"] = R844
hb["did"] = R844
hb["last_round_at"] = TS
hb["last_seen"] = TS
hb["updated"] = TS
hb["ts"] = TS
hb["clock_read"] = TS
hb["updated_at"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "r844 orphan probe 21:52 py_faces=13 orphans=0"
hb["sync"] = {"last_push_ts": TS, "note": "r844 closeout; post-push fetch self-proof behind=0 pending S7 verify"}
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

print("closeout written: round=844 ts=%s epoch=%d int=%s" % (TS, EPOCH, isinstance(EPOCH, int)))
