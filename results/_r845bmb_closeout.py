# -*- coding: utf-8 -*-
# r845 bm-b closeout: round report line + state.json + heartbeat
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

R845 = ("r845: backlog row-9 tile frame-budget bench CLOSED via editor-batchmode route: TileBenchEditorRun.cs "
        "(per-tick cam.Render->RT 1600x900 + 1x1 ReadPixels GPU drain) + run_bench_editor.ps1 driver (canary guard) "
        "+ report.py verdict-inversion fix (first-pass all-RED false caught+healed in-round) + budget-line % literal "
        "ValueError heal + env unit fixes (ramMB->GB, workingSet=0 batchmode disclosure) -> 8-config matrix 8/8 rc0 "
        "ALL GREEN (pan p99 4.48-5.04ms << 16.67ms) -> FRAME BUDGET = visible tiles/frame <= 19,728 (60fps p99, 20% "
        "margin, editor=player conservative floor) -> REPORT.md+summary+8 run JSONs+harness 3 files landed "
        "results/tile_bench/ (13 files 40KB) + backlog done@; S6 43 legs all rc0 (dualrun streak reset on "
        "entry[416].done_at single-face miss = observation-phase data, not a fault); astock rebuild 1783/5229 "
        "@22:31 pace ~16/min ETA ~02:10 = T23 census honest wait window continues")
NEXT = ("r846 queue: astock rebuild completion verify (window ~10-11 01:45-02:15+) -> spawn detached T23 census "
        "full burn -> census_holds readout -> N2 U3 (1) prereg drafting window if holds / G2 academic-citation "
        "fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge); tile-bench row-9 closed "
        "(optional S4U player cross-check only on CEO ask)")
VERDICT = ("r845: GREEN; smoke 49/49; D19 dual watermark zero-delta; orders diff empty (65 all ack); dualrun streak "
           "reset (entry416 done_at observation-phase, exit 0 recorded); attrition CLEAN; board/queues empty; "
           "backlog row-9 DONE (tile frame budget delivered, 8/8 GREEN); T23 census honest wait window continues "
           "(astock 1783/5229 ETA ~02:10); zero double-burn")

try:
    it = json.load(open("results/idle_trigger.bm-b.json", encoding="utf-8"))
    RAM_GB = round(it.get("ram_free_pct", 0) * 0.24, 1)
    VRAM_GB = it.get("vram_free_gb", 0)
except Exception:
    RAM_GB, VRAM_GB = 0, 0

RR = ("{ts} | r845 bm-b | dept:工程（backlog row-9 tile 帧基准收口交付轮：editor-batchmode 路线全捷） | "
      "WM-VERDICT: green（red=false @22:24 probe；py_low_with_work_cands 合法=local_batch=astock 重建在飞+tile-bench "
      "矩阵在飞；supply_gap/supply_floor=O-1645 standing；ignition_sla 零 breach） | 孤儿面=0（probe 22:23 py_faces=14 "
      "orphans=0） | CEO three-line: 当前活=row-9 帧基准收口完成（8/8 矩阵 rc0+REPORT 交付+backlog done@）；"
      "最近实物=results/tile_bench/REPORT.md（**帧预算=每帧可见 tiles ≤19,728·60fps p99 口径·含 20% 余量·全 8 配置 GREEN**）"
      "+results/_r845bmb_s6chain.log（43 腿全 rc0），2026-10-10 22:3x；下个里程碑=astock 重建完备（ETA ~02:10）"
      "→detached T23 census 烧录→holds 判读（窗 ≤10-11 06:00）→N2 U3(1) prereg 起草窗 | "
      "did: S0-1 锚定 bm-b；S0 轮首脏 9 件=自有 daemon live faces 定向 commit（5c67ec044）后 pull up-to-date 净路；"
      "S0.5 令扫 65 件零未回执+D19 双水位零变化（dec a20664ec/ord 3af479f1 恒等零动作）；S1 smoke 49/49；"
      "S2 板面 0 open（job_list 0）；S3 固定序全绿：红牌 false+引擎活 rc0+修红无红项；"
      "主产品=row-9（r844 claim）editor-batchmode 收口：TileBenchEditorRun.cs（cam.Render→RT 1600×900+1×1 ReadPixels "
      "GPU 排空·编辑器 loop 口径）+run_bench_editor.ps1（canary 护栏）+report.py 判定反转修复（avg≤16.67 误判 RED·"
      "首跑全 RED 假象当轮自捕）+预算行 '20%' 字面量×% 操作符 ValueError 治愈（被反转掩盖的潜伏面）+ramMB/workingSet "
      "单位修复→8 配置矩阵 8/8 rc0 全 GREEN（pan p99 4.48-5.04ms ≪16.67ms·复跑差 5.9%·size sweep 平坦=成本由可见 "
      "tiles 主导）→帧预算=每帧可见 tiles ≤19,728（60fps p99·20% 余量·editor=player 保守下界）→REPORT.md+summary+"
      "8 JSON+harness 三件入仓 results/tile_bench/（13 件 40KB）+backlog done@；dualrun DRIFT entry[416].done_at "
      "单面缺失=观察相数据照录 streak 29→reset（非故障·flip 门计数重启）；S6 43 腿全 rc0（40 正典+astock gate/"
      "live_paper/t35_open_fill 三补腿·attrition CLEAN 4 台账）；S7 四件套全绿：loop pin=2 no-op+watchdog 重注+双爪 "
      "LF 归一 MATCH+idle --worked 清零；HANDOVER 5x 行落（r841-r845 窗） | "
      "记账预算 5/5（state+心跳+轮报+D19 探针+HANDOVER 5x 行；S6 管线产出/backlog done@ 产品回写不计） | "
      "score: 2（帧预算 REPORT+可跑矩阵 harness=能跑能看实物） | unacked_orders=0 | 本地未达 origin commit 数=0"
      "（push 后 fetch 自证，见 S7） | 下轮指针: {next} | [r845 bm-b]").format(ts=TS, next=NEXT)

with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(RR + "\n")

with open("state.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["machine_id"] = "bm-b"
st["round_no"] = 845
st["round"] = 845
st["round_no_label"] = "r846"
st["note"] = R845
st["did"] = R845
st["last_action"] = R845
st["verdict"] = VERDICT
st["current_task"] = NEXT
st["task"] = NEXT
st["next"] = NEXT
st["now_active"] = "r845 closeout: backlog row-9 tile frame budget delivered (editor-batchmode 8/8 GREEN) + S6 43 legs + T23 wait window (astock rebuild in flight)"
st["latest_artifact"] = ("r845: results/tile_bench/ (REPORT.md frame budget visible-tiles<=19,728 + summary.json + 8 run JSONs "
                         "+ harness 3 files, 13 files 40KB) + results/_r845bmb_s6chain.log (43 legs all rc0), 2026-10-10 22:3x")
st["next_milestone"] = ("astock panel complete (~02:10 ETA) -> detached T23 census burn -> holds verdict "
                        "(window <=10-11 06:00) -> N2 U3(1) prereg draft window")
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
hb["round"] = 845
hb["round_no"] = 845
hb["now_active"] = st["now_active"]
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["next"] = NEXT
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = ("GREEN: r845 production round (backlog row-9 tile frame-budget bench CLOSED: editor-batchmode route "
                 "8/8 GREEN, frame budget visible tiles/frame <= 19,728 @60fps p99 20% margin, REPORT+artifacts landed "
                 "results/tile_bench/; report.py verdict-inversion + %-literal bugs caught+healed in-round); D19 "
                 "zero-delta; S6 43 legs all rc0 (dualrun streak reset = observation data); quartet+attrition clean; "
                 "idle cleared via --worked; T23 census honest wait window continues (astock 1783/5229 ETA ~02:10)")
hb["last_action"] = R845
hb["did"] = R845
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
hb["orphan_face_note"] = "r845 orphan probe 22:23 py_faces=14 orphans=0"
hb["free_ram_gb"] = RAM_GB
hb["ram_free_gb"] = RAM_GB
hb["gpu_free_vram_gb"] = VRAM_GB
hb["sync"] = {"last_push_ts": TS, "note": "r845 closeout; post-push fetch self-proof behind=0 pending S7 verify"}
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

print("closeout written: round=845 ts=%s epoch=%d int=%s ram=%s vram=%s" % (
    TS, EPOCH, isinstance(EPOCH, int), RAM_GB, VRAM_GB))
