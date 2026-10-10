# -*- coding: utf-8 -*-
# r844 bm-b addendum: tile-bench standalone-player route blocked (hidden-window freeze) -> honest pivot note
import json, time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

ADD = ("{ts} | r844 bm-b ADDENDUM | dept:工程（tile-bench 路线诊断收口：honest pivot） | "
       "实证：standalone player 隐藏窗不跑循环（Player.log：D3D11 RTX3070 设备建好→分辨率切换 1024x768/1600x900 双败→日志止步；"
       "活体 CPU 0.5s/180s 冻结·MainWindowHandle=0；桌面 1024x768）→ run01/02 180s 超时被杀 0 产物；"
       "驱动 22:10:05 止损 kill（禁 8x180s 空转）；零窗律与 player 可见窗需求结构性冲突→放弃 standalone 路线；"
       "r845 续作选型=editor batchmode（无 -nographics）+手动 RenderTexture 1600x900 渲染循环"
       "（仓内先例=城线 demo batchmode 15 断言 PASS·数字=player 保守下界口径如实披露）；"
       "诊断+续作设计已落 C:\\Fluxgroup\\bench-work\\tile-bench\\NEXT_STEPS.md+bench_state.json"
       "（phase=blocked-hidden-window-pivot-r845）；产物保留复用（proj/build rc0/harness 四件勿重建）；"
       "score 修正：r844 实收 1（harness+build 实物+诊断档案）；帧预算数字 r845 batchmode 路线收口 | [r844 bm-b]"
       ).format(ts=TS)

with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(ADD + "\n")

R844B = ("r844: idle-claim row-9 (CPH4 tile frame-budget bench): harness 4 files + Tuanjie t15 player build rc=0, "
         "standalone route DIAGNOSED BLOCKED same round (hidden-window freeze: player loop needs visible window, zero-popup law conflict) "
         "-> honest pivot to editor-batchmode RT benchmark for r845 (NEXT_STEPS.md); driver killed 22:10:05 zero waste; "
         "+ S6 41 legs (40 rc0 + alloc rc=2 known P5 stale-leg); astock rebuild 1193/5229@21:54 pid 10404 alive ETA ~02:05 = T23 census wait window continues")
NEXT = ("r845 queue: tile-bench editor-batchmode RT benchmark (see bench-work/tile-bench/NEXT_STEPS.md: TileBenchEditorRun.cs + "
        "cam.targetTexture 1600x900 manual render loop + driver batchmode matrix) -> report.py frame-budget REPORT.md + backlog done@; "
        "astock rebuild completion verify (window ~10-11 01:45-02:15+) -> spawn detached T23 census full burn -> census_holds readout -> "
        "N2 U3 (1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)")
ART = ("r844: C:\\Fluxgroup\\bench-work\\tile-bench\\ (harness 4 files + TileBench.exe build rc=0 + NEXT_STEPS.md diagnosis/pivot) "
       "+ results/_r844bmb_s6chain.log (41 legs, dualrun streak 29), 2026-10-10 22:1x")

with open("state.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["did"] = R844B
st["last_action"] = R844B
st["note"] = R844B
st["current_task"] = NEXT
st["task"] = NEXT
st["next"] = NEXT
st["now_active"] = "r844 closeout: tile-bench route diagnosis + honest pivot to editor-batchmode (r845) + S6 41 legs + T23 wait window"
st["latest_artifact"] = ART
st["next_milestone"] = ("r845 (window <=10-11 00:00): editor-batchmode RT benchmark burn -> frame-budget REPORT.md + backlog row-9 done@; "
                        "astock complete (~02:05 ETA) -> detached T23 census -> holds verdict (<=10-11 06:00)")
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["did"] = R844B
hb["last_action"] = R844B
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["next"] = NEXT
hb["latest_artifact"] = ART
hb["next_milestone"] = st["next_milestone"]
hb["now_active"] = st["now_active"]
hb["verdict"] = ("GREEN: r844 idle-claim production round (backlog row-9 claimed fefc75c9d + harness + t15 player build rc=0; "
                 "standalone route honestly diagnosed blocked under zero-window law same round -> pivot note landed, zero waste); "
                 "D19 zero-delta; S6 41 legs green (alloc rc=2 known P5 stale-leg); quartet+attrition clean; idle cleared 0; "
                 "T23 census honest wait window continues (astock rebuild ETA ~02:05)")
hb["ts"] = TS
hb["updated"] = TS
hb["updated_at"] = TS
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

print("addendum written ts=%s" % TS)
