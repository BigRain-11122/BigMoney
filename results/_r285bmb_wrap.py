"""r285 bm-b S7 wrap-up: state.json + heartbeat + round report line append.

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

DID = ("r285: T-87 astock first-pull mid-flight probe #5 on_track "
       "(828/5228=15.8%, 12.68/min lock-start face, ETA Sun 06:39:35 = "
       "26.6h before Mon 09:15 live fire, 827/828 at cutoff 2026-09-24, "
       "zero shape defects, rate face stable probes 3->5 "
       "12.61/12.65/12.68); ticket progress_r285_bmb field-increment "
       "2+/1-; watch faces: REV-OSC pool ready (lane_owner bm-a, bm-b "
       "autofill skip correct per 00:50 tick), CN_TREND_ETF_P1 pool face "
       "absent (bm-a runner pending), Optuna 6 validated < 8 stays "
       "gated; S6 22 legs rc=0 (WM probe verdict=py_low_with_work_cands "
       "legal-idle proven: only ready shard REV-OSC=bm-a lane, bandit "
       "next_pick=claimed/parked MF panel source-blocked, board 0 open; "
       "compute_audit CLEAN flags=[]; unified ledger 187,845 flat-read); "
       "HANDOVER 5x check delivered (r285 multiple of 5); orders 89/89 "
       "double-scan zero unacked")
NEXT = ("r286: T-87 mid-flight probe #6 (frozen lineage continuation); "
        "pass-completion re-probe queued after ETA ~06:40; Mon 09-28 09:15 "
        "first daily-continuation live fire (stragglers gate self-heal); "
        "REV-OSC autofill launch watch (bm-a lane, pool ready since "
        "00:31); CN_TREND_ETF_P1 runner/pool face watch (bm-a); migration "
        "window to 09-29 12:00 (v2.2 armed, editor-gated); 10-01 "
        "month-first trio (science_audit+monthly_briefing+self_review)")
CURTASK = ("T-87 supply lane: first-pull pass in flight (probe #5 "
           "on_track 828/5228, ETA Sun 06:40); S6 22 legs green; "
           "HANDOVER 5x; wrap r285")

# ---- state.json (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(STATE, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
st = json.loads(raw.decode("utf-8"))
st.update({
    "round_no": 285,
    "did": DID,
    "verdict": "green",
    "next": NEXT,
    "current_task": CURTASK,
    "last_round_ts": st.get("ts", TS),
    "last_result": "ok",
    "last_tick": NOW.strftime("%H:%M"),
    "ts": TS,
    "last_seen": TS,
    "last_run": f"R285 {NOW.isoformat()}",
    "last_round_at": TS,
    "updated": TS,
    "updated_at": TS,
})
with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
raw2 = open(STATE, "rb").read()
assert raw2[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw2 and not raw2.endswith(b"\n")
assert json.loads(raw2.decode("utf-8"))["round_no"] == 285

# ---- heartbeat (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(HB, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
hb = json.loads(raw.decode("utf-8"))
hb.update({
    "last_seen": TS,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW.astimezone().isoformat(),
    "current_task": CURTASK,
    "round_no": 285,
    "round": 285,
    "verdict": "green",
    "free_ram_gb": 13.8,
    "idle_ram_gb": 13.8,
    "idle_ram_mb": 13800,
    "gpu_idle_vram_gb": 7.1,
    "gpu_free_vram_gb": 7.1,
    "gpu_free_vram_mb": 7100,
    "gpu_idle_vram_mb": 7100,
    "cpu_util_pct": 14.2,
    "cpu_pct": 14.2,
})
# orders_ack untouched (89/89, zero-missing double-scan this round)
with io.open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
raw2 = open(HB, "rb").read()
d2 = json.loads(raw2.decode("utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in d2["clock_read"], "clock_read must be T-separated"
assert abs(int(dt.datetime.now().timestamp()) - d2["heartbeat_epoch_utc"]) < 120
n_ack = len([x for x in d2["orders_ack"].split() if x])
print(f"heartbeat: epoch={d2['heartbeat_epoch_utc']} (int OK) clock={d2['clock_read']} ack={n_ack}")

# ---- round_reports.md append (LF + trailing newline, r281 law pre-probe)
raw = open(RR, "rb").read()
assert raw.endswith(b"\n"), "ledger tail newline missing (r281 law)"
LINE = (
    f"{NOW.isoformat()} | r285 (bm-b) | dept:数据/工程 | WM-VERDICT: GREEN "
    "healthy red=false (probe verdict=py_low_with_work_cands 合法闲面证明: "
    "板 0 open/33 claimed 全占, bandit next_pick=claimed (MF IC 参照批停靠"
    "=moneyflow 面板 source-blocked, bm-a 车道 30min 自愈中), 池唯一 ready "
    "分片 REV-OSC lane_owner=bm-a 本机 autofill 依法跳过 (00:50 tick 在案) "
    "→ bm-b 零可领分片=§四合法 idle 白名单; T-87 首拉批=网络限速采集在飞低 "
    "py 合法面) | did: T-87 供给线中途健康探针#5 on_track (828/5228=15.8% 路 "
    "rate 12.68/min lock-start 面 路 ETA 2026-09-27T06:39:35=周一 09:15 死线"
    "前余 26.6h 路 827/828@cutoff 2026-09-24 路 1 例早尾=suspension 诚实面 路 "
    "header_mismatch=0 路 ohlc_bad=0 路 lock alive 路 探针谱系=r284 冻结面逐"
    "字复刻零重建 路 速率面 3→5 稳定 12.61/12.65/12.68) + 票面 "
    "progress_r285_bmb 字段增量 2+/1- (R255 五面探测门过) + watch 面: REV-OSC "
    "池 ready (bm-a lane, autofill 待点火) + CN_TREND_ETF_P1 池面未见 (bm-a "
    "runner 待建, watch only) + Optuna 门复核 6 validated<8 维持 gated + S6 "
    "22 腿 rc=0 (周末诚实 no-op: update_daily 无新行, astock_daily "
    "lock-alive no-op, market_clock CALL-2026-09-24 ORANGE_COOL sleeves=4 "
    "幂等再生, compute_audit CLEAN flags=[], 统一链 187,845 实读平持, 他机车"
    "道 stdout-only, fundamental 新鲜跳过) + HANDOVER 5x 核对行落档 (r285=5 "
    "倍数轮) + S0 预拉维护 commit 40b3b377 (autofill 尾件解锁 rebase, "
    "r280/r281 律) + orders 89/89 双扫零未回执 + 决策审核步=本机无 ..\\..\\"
    "docs\\decisions.md (集团层在 bm-a 侧) 零动作 | evidence: results/"
    "_r285bmb_astock_pass_probe.py+.json + results/_r285bmb_ticket_update.py "
    "+ results/_r285bmb_watch.py+_r285bmb_watch_faces.json + results/"
    "_r285bmb_s6_chain.py+_r285bmb_s6_summary.json+_r285bmb_s6_logs/ + "
    "research/HANDOVER.md 5x 行 + smoke 25/25 + schtasks 双任务健康 "
    "(IterationLoop 正在运行/Watchdog 就绪) | next: r286=T-87 中途探针#6 (谱"
    "系续) + ETA 06:40 后 pass 完成复探 + 周一 09-28 09:15 首次日续拉实弹 "
    "(stragglers gate 自愈腿) + REV-OSC autofill 点火 watch (bm-a) + "
    "CN_TREND runner/pool 面 watch + 迁移窗 watch (v2.2 armed 至 09-29 "
    "12:00) + 10-01 月首轮三件套\n"
)
with io.open(RR, "ab") as f:
    f.write(LINE.encode("utf-8"))
raw2 = open(RR, "rb").read()
assert raw2.endswith(b"\n")
import re
multi = len(re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", raw2.decode("utf-8")[-2500:]))
print("round_reports appended, tail-newline OK, ts-lines in tail:", multi)
print("WRAP_OK round=285 ts=" + TS)
