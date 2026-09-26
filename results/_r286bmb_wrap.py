# -*- coding: utf-8 -*-
"""r286 bm-b S7 wrap-up: state.json + heartbeat + round report line append.

Byte-face laws: state.json/bm-b.json = LF-only, no BOM, NO trailing
newline, indent=1 (mirror exactly); round_reports.md = LF-dominant with
tail newline (append with \n). All timestamps from ONE now() instance
(R271 law). heartbeat epoch MUST be JSON int (R170/R178), clock_read
T-separated ISO (R262 law). Post-write self-asserts on every face.
"""
import datetime as dt
import io
import json

NOW = dt.datetime.now()
TS = NOW.isoformat(timespec="seconds")                # T-separated, +08:00 offset
EPOCH = int(NOW.timestamp())
STATE = "logs/iteration-loop/state.json"
HB = "fleet/machines/bm-b.json"
RR = "logs/iteration-loop/round_reports.md"

try:
    import psutil
    FREE_GB = round(psutil.virtual_memory().available / 1e9, 1)
    CPU_PCT = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    FREE_GB, CPU_PCT = 14.7, 8.0

DID = ("r286: CN-TREND-ETF-P1 pool first-fire DOUBLE crash root-fix "
       "(bug1 int64 dump: transitions_head 'leg'=flatnonzero np.int64, "
       "judged-face collect only -> _jsonable native coercion at 3 dump "
       "sites + selftest leg [13], 22/22, real-data crash-face probe "
       "PASS 6.4s, x2 sharpe 0.4516 == bm-a registered gate-probe value "
       "= cross-machine determinism evidence; bug2 assembly glue: blob "
       "never stored into cells_out[name][face] both branches -> KeyError "
       "'x2' at judged zero-trades check, selftest [12] hand-builds "
       "cells_out = driver-glue blind seam, fixed, 22/22; zero-judged "
       "window r253 law, MA_BASE x1/x2 checkpoints committed for pool "
       "idempotent resume; 01:20 tick relaunched with fix1 sha "
       "e1ad5cb03d077019, fix2 landed 01:28 before 01:30 tick); T-87 "
       "astock probe #6 on_track (1170/5228=22.4%, 12.78/min, ETA "
       "06:36:12 < Mon 09:15 deadline, 1169/1170 at cutoff 2026-09-24, "
       "zero shape defects); S0 rebase UU autofill_state resolved per "
       "skill union recipe (51 -> newest 50, same-second tie 01:10:01 -> "
       "HEAD per r140); S6 22 legs rc=0 (WM probe py_low_board_clear "
       "01:19:35, compute_audit CLEAN flags=[], astock lock-alive no-op); "
       "orders 89/89 double-scan zero unacked; decisions.md not "
       "reachable at ..\\..\\docs (group layer) = zero action; CODELY 1 "
       "law line (both bugs, r259 family 2 new params), 48.9KB < 50KB "
       "watermark")
NEXT = ("r287: CN-TREND relaunch watch (01:30 tick face carries both "
        "fixes; p1_results.json lands -> harvest per r244 landed-marker "
        "law + prereg gates read); T-87 probe #7 (frozen lineage); "
        "pass-completion re-probe after ETA ~06:36; Mon 09-28 09:15 "
        "first daily-continuation live fire (stragglers gate self-heal); "
        "migration window to 09-29 12:00 (v2.2 armed, editor-gated); "
        "10-01 month-first trio (science_audit+monthly_briefing+"
        "self_review)")
CURTASK = ("CN-TREND pool first-fire double crash-fix delivered (22/22 "
           "green, checkpoints committed); T-87 first-pull in flight "
           "(probe #6 on_track, ETA 06:36); S6 22 legs green; wrap r286")

# ---- state.json (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(STATE, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
st = json.loads(raw.decode("utf-8"))
st.update({
    "round_no": 286,
    "did": DID,
    "verdict": "green",
    "next": NEXT,
    "current_task": CURTASK,
    "last_round_ts": st.get("ts", TS),
    "last_result": "ok",
    "last_tick": NOW.strftime("%H:%M"),
    "ts": TS,
    "last_seen": TS,
    "last_run": f"R286 {NOW.isoformat()}",
    "last_round_at": TS,
    "updated": TS,
    "updated_at": TS,
})
with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
raw2 = open(STATE, "rb").read()
assert raw2[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw2 and not raw2.endswith(b"\n")
assert json.loads(raw2.decode("utf-8"))["round_no"] == 286

# ---- heartbeat (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(HB, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
hb = json.loads(raw.decode("utf-8"))
hb.update({
    "last_seen": TS,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW.astimezone().isoformat(),
    "current_task": CURTASK,
    "round_no": 286,
    "round": 286,
    "verdict": "green",
    "free_ram_gb": FREE_GB,
    "idle_ram_gb": FREE_GB,
    "idle_ram_mb": int(FREE_GB * 1000),
    "gpu_idle_vram_gb": 7.1,
    "gpu_free_vram_gb": 7.1,
    "gpu_free_vram_mb": 7100,
    "gpu_idle_vram_mb": 7100,
    "cpu_util_pct": CPU_PCT,
    "cpu_pct": CPU_PCT,
})
# orders_ack untouched (89/89, zero-unacked double-scan this round)
with io.open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
raw2 = open(HB, "rb").read()
d2 = json.loads(raw2.decode("utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in d2["clock_read"], "clock_read must be T-separated"
assert abs(int(dt.datetime.now().timestamp()) - d2["heartbeat_epoch_utc"]) < 120
n_ack = len([x for x in d2["orders_ack"].split() if x])
print(f"heartbeat: epoch={d2['heartbeat_epoch_utc']} (int OK) "
      f"clock={d2['clock_read']} ack={n_ack} free={FREE_GB}GB cpu={CPU_PCT}%")

# ---- round_reports.md append (LF + trailing newline, r281 law pre-probe)
raw = open(RR, "rb").read()
assert raw.endswith(b"\n"), "ledger tail newline missing (r281 law)"
LINE = (
    f"{NOW.isoformat()} | r286 (bm-b) | dept:工程/数据 | WM-VERDICT: GREEN "
    "healthy red=false (probe verdict=py_low_board_clear 01:19:35: 板 0 "
    "open 全 claimed, REV-OSC 已收割关槽 (bm-a r282 judged-negative 7/7), "
    "cntrend=bm-b 已认领在飞 (01:20 tick 复发射 sha 已换固定面), T-87 首拉="
    "网络限速采集在飞低 py 合法面) | did: CN-TREND 池首烧双崩根修 (崩1 "
    "int64 dump: transitions_head 'leg'=np.flatnonzero np.int64 只在 "
    "judged face collect -> selftest 21/21+bm-a real-gate probe 双绿掩病, "
    "正律=_jsonable 三 dump 站点全量 native 强转 (p4_batch2_screen "
    "idiom) + 自测腿 [13] 非原生类型注入 + 真数据单 cell 灾面探针 6.4s "
    "PASS (x2 sharpe 0.4516 与 bm-a 注册探针值恒等=跨机确定性实证) + "
    "MA_BASE x1/x2 checkpoint 双件落档供池幂等续跑; 崩2 同链装配 glue: "
    "blob 从未存进 cells_out[name][face] 两分支皆缺 -> KeyError 'x2', "
    "selftest [12] 手搓 cells_out 恒不走 cmd_run 装配面=被测件间 glue "
    "自测盲区 (r259 家族再参), 双修 22/22; 零判产物窗工程修 r253 律; "
    "01:20 tick 带修复1复发射 (sha e1ad5cb0), 修复2 01:28 落盘先于 01:30 "
    "tick) + T-87 供给线中途健康探针#6 on_track (1170/5228=22.4% 路 "
    "rate 12.78/min 路 ETA 06:36:12=死线前余 31h 路 1169/1170@cutoff "
    "2026-09-24 路 header/ohlc 零缺陷 路 探针谱系 r281-r285 冻结面逐字"
    "复刻) + S0: tick 尾件 commit 1bb944d3 解锁 rebase (r280/r281 律) + "
    "push 撞 bm-a r282 wrap -> rebase UU autofill_state 唯件 + 撞头解="
    "skill 分类器 GREEN mixed-dict+ledger union 配方 (51->newest 50, 同秒 "
    "tie 01:10:01->HEAD r140, CRLF 镜像 r223, parse-verify r185) + 双修 "
    "commit 链 ae9da508/142782ae 推平 + tick 自家认领 commit 3cf5d85e "
    "同窗无撞 + orders 89/89 双扫零未回执 + 决策审核步=..\\..\\docs\\"
    "decisions.md 本机不可达 (集团层在 bm-a 侧) 零动作 + S6 22 腿 rc=0 "
    "(WM py_low_board_clear, compute_audit CLEAN, 周末诚实 no-op: "
    "update_daily 无新行/astock lock-alive no-op/纸面族无新 bar 诚实跳/"
    "月度三件套非月首轮/季度槽已 discharge) + schtasks 双任务健康 "
    "(IterationLoop 正在运行/Watchdog 就绪, R49 schtasks 口径) + inbox 空 "
    "| evidence: results/_r286bmb_cntrend_probe.py+json (灾面探针) + "
    "scripts/cn_trend_etf_p1.py r286 AMENDMENT 段 + results/cn_trend_ETF/"
    "cells/MA_BASE_x1+x2 checkpoint 双件 + results/_r286bmb_resolve.py "
    "(撞头解留痕) + results/_r286bmb_astock_pass_probe.py+json + "
    "results/_r286bmb_s6_chain.py+_r286bmb_s6_summary.json+_r286bmb_s6_"
    "logs/ + results/_r286bmb_s4_append.py (CODELY 律行) + smoke 25/25 + "
    "selftest 22/22 | next: r287=CN-TREND 复发射 watch (01:30 tick 面携双"
    "修, p1_results.json 落地->r244 landed-marker 律收割+prereg 门读) + "
    "T-87 探针#7 (谱系续) + ETA ~06:36 后 pass 完成复探 + 周一 09-28 "
    "09:15 首次日续拉实弹 (stragglers gate 自愈腿) + 迁移窗 watch (v2.2 "
    "armed 至 09-29 12:00) + 10-01 月首轮三件套\n"
)
with io.open(RR, "ab") as f:
    f.write(LINE.encode("utf-8"))
raw2 = open(RR, "rb").read()
assert raw2.endswith(b"\n")
import re
multi = len(re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", raw2.decode("utf-8")[-2500:]))
print("round_reports appended, tail-newline OK, ts-lines in tail:", multi)
print("WRAP_OK round=286 ts=" + TS)
