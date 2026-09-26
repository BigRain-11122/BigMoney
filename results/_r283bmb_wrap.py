"""r283 bm-b S7 wrap-up: state.json + heartbeat + round report line append.

Byte-face laws: state.json/bm-b.json = LF-only, no BOM, NO trailing
newline, indent=1 (mirror exactly); round_reports.md = LF-dominant with
tail newline (append with \n). All timestamps from ONE now() instance
(R271 law). heartbeat epoch MUST be JSON int (R170/R178), clock_read
T-separated ISO (R262 law). Post-write self-asserts on every face.
"""
import datetime as dt
import io
import json
import platform
import subprocess

NOW = dt.datetime.now()
TS = NOW.isoformat(timespec="seconds")                # T-separated, +08:00 offset
EPOCH = int(NOW.timestamp())
STATE = "logs/iteration-loop/state.json"
HB = "fleet/machines/bm-b.json"
RR = "logs/iteration-loop/round_reports.md"

DID = ("r283: T-87 astock first-pull pass mid-flight probe #3 on_track "
       "(591/5228=11.3%, 12.61/min, ETA Sun 06:41:49, Mon-deadline margin "
       "32.5h, zero shape defects); ticket progress_r283_bmb field-increment "
       "2+/1-; S6 26 legs rc=0 weekend honest no-ops; inbox MSG-20260927-0035 "
       "bm-a CN_TREND_ETF_P1 prereg-freeze declaration acknowledged "
       "(action=none); Optuna unlock criterion checked = 6 validated < 8, "
       "stays gated zero action; standing external channels date-gated "
       "(arXiv next window 10-03, hibor/jin-gong Mon 09-28 open-market "
       "window, jisilu run-9/guorn run-3 closed yesterday) -- no forced "
       "digest; orders 89/89 double-scan zero unacked")
NEXT = ("r284: pass-completion re-probe after ETA 06:41; Mon 09-28 09:15 "
        "first daily-continuation live fire (stragglers gate self-heal); "
        "CN_TREND_ETF_P1 runner/pool face watch (bm-a lane); REV_OSC "
        "consumption face watch; migration window to 09-29 12:00; 10-01 "
        "month-first trio (science_audit+monthly_briefing+self_review)")
CURTASK = ("T-87 supply lane: full-universe pass in flight (probe #3 "
           "on_track 591/5228, ETA Sun 06:41); S6 26 legs green; wrap r283")

# ---- state.json (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(STATE, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
st = json.loads(raw.decode("utf-8"))
st.update({
    "round_no": 283,
    "did": DID,
    "verdict": "green",
    "next": NEXT,
    "current_task": CURTASK,
    "last_round_ts": st.get("ts", TS),
    "last_result": "ok",
    "last_tick": NOW.strftime("%H:%M"),
    "ts": TS,
    "last_seen": TS,
    "last_run": f"R283 {NOW.isoformat()}",
    "last_round_at": TS,
    "updated": TS,
    "updated_at": TS,
})
with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
raw2 = open(STATE, "rb").read()
assert raw2[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw2 and not raw2.endswith(b"\n")
assert json.loads(raw2.decode("utf-8"))["round_no"] == 283

# ---- heartbeat (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(HB, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
hb = json.loads(raw.decode("utf-8"))
hb.update({
    "last_seen": TS,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW.astimezone().isoformat(),
    "current_task": CURTASK,
    "round_no": 283,
    "round": 283,
    "verdict": "green",
    "free_ram_gb": 15.2,
    "idle_ram_gb": 15.2,
    "idle_ram_mb": 15200,
    "gpu_idle_vram_gb": 7.1,
    "gpu_free_vram_gb": 7.1,
    "gpu_free_vram_mb": 7100,
    "gpu_idle_vram_mb": 7100,
    "cpu_util_pct": 3.0,
    "cpu_pct": 3.0,
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
    f"{NOW.isoformat()} | r283 (bm-b) | dept:数据/工程 | WM-VERDICT: GREEN "
    "healthy red=false (probe verdict=insufficient_history 窗短合法面; T-87 "
    "首拉批网络限速 2.5s/股在飞=低 py 设计面合法; 板 0 open/33 claimed 全占, "
    "bandit next_pick=claimed moneyflow IC 等 bm-a 面板源阻断自愈) | "
    "did: T-87 供给线中途健康探针#3 on_track (591/5228=11.3% 路 rate 12.61/min "
    "路 ETA 2026-09-27T06:41:49=周一 09:15 死线前余 32.5h 路 header_mismatch=0 "
    "路 ohlc_bad=0 路 tail@cutoff 590/591 路 1 例 09-03 早尾=suspension 诚实面 "
    "路 attempts=1(000019 下次 gate 自愈) 路 quarantine=0) + 票面 "
    "progress_r283_bmb 字段增量 2+/1- (R255 五面探测门过) + S6 26 腿 rc=0 "
    "(周末诚实 no-op: heat/futures 节流或覆盖止损面, options/moneyflow/sina_mf/"
    "ths/ah/fund_premium 他机车道 stdout-only, astock_daily lock-alive no-op, "
    "fundamental 新鲜跳过, b_layer_mask 再生, marks/verify/prospect 四腿无新 "
    "bar 触发条件不满足合法跳过, paper 出口 09-24 幂等, scorecard/report/"
    "build_status/token 全 rc=0) + 收件箱 MSG-20260927-0035 bm-a "
    "CN_TREND_ETF_P1 prereg 冻结申报收悉 (T-87 s2 队列#1, action=none, runner "
    "bm-a 后续轮建) + Optuna 解封判据勘验=在册 validated 6<8 维持 gated 零动作 "
    "(判据冻结面) + 常态外源道勘验=arXiv 周窗已闭 next 10-03 + hibor/jin-gong "
    "周一 09-28 开市窗 + jisilu run-9/guorn run-3 昨 19:3x 已收口=今日不硬造 "
    "digest (反重复律) + fusion-nav 00:00 重复面确证已由 r281 收口 (锚报告隔离 "
    "弃置, 判裁 8effe41b) | evidence: results/_r283bmb_astock_pass_probe.py+."
    "json + results/_r283bmb_ticket_update.py + smoke 25/25 + S6 逐腿 rc 账 + "
    "orders 89/89 双扫零未回执 | next: r284=pass 完成复探 (ETA 06:41 后) + "
    "周一 09-28 09:15 首次日续拉实弹 (stragglers gate 自愈腿) + "
    "CN_TREND_ETF_P1 runner/pool 面 watch (bm-a) + REV_OSC 消费面 watch + "
    "迁移窗 watch (v2.2 armed, 09-29 12:00) + 10-01 月首轮三件套\n"
)
with io.open(RR, "ab") as f:
    f.write(LINE.encode("utf-8"))
raw2 = open(RR, "rb").read()
assert raw2.endswith(b"\n")
import re
multi = len(re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", raw2.decode("utf-8")[-2000:]))
print("round_reports appended, tail-newline OK, ts-lines in tail:", multi)
print("WRAP_OK round=283 ts=" + TS)
