"""r284 bm-b S7 wrap-up: state.json + heartbeat + round report line append.

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

DID = ("r284: T-87 astock first-pull mid-flight probe #4 on_track "
       "(714/5228=13.7%, 12.65/min lock-start face, ETA Sun 06:40:36, "
       "Mon-deadline margin 26.5h, 713/714 at cutoff 2026-09-24, zero "
       "shape defects); ticket progress_r284_bmb field-increment 2+/1-; "
       "watch faces: REV-OSC pool re-entry ready since 00:31 (bm-a lane, "
       "autofill to fire), CN_TREND_ETF_P1 pool face absent (bm-a runner "
       "pending), Optuna gate re-checked 6 validated < 8 stays gated "
       "(template-id false-anomaly resolved in-round, counting-face law "
       "appended to CODELY.md); S6 22 legs rc=0 (WM=py_low_board_clear "
       "legal idle face, compute_audit CLEAN flags=[]); orders 89/89 "
       "double-scan zero unacked")
NEXT = ("r285: pass-completion re-probe after ETA ~06:41 (frozen-probe "
        "lineage face #5); Mon 09-28 09:15 first daily-continuation live "
        "fire (stragglers gate self-heal); REV-OSC autofill launch watch "
        "(bm-a lane, pool ready since 00:31); CN_TREND_ETF_P1 runner/pool "
        "face watch (bm-a); migration window to 09-29 12:00 (v2.2 armed, "
        "editor-gated); 10-01 month-first trio (science_audit+monthly_"
        "briefing+self_review); HANDOVER 5x check due (r285 multiple of 5)")
CURTASK = ("T-87 supply lane: first-pull pass in flight (probe #4 "
           "on_track 714/5228, ETA Sun 06:40); S6 22 legs green; wrap r284")

# ---- state.json (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(STATE, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
st = json.loads(raw.decode("utf-8"))
st.update({
    "round_no": 284,
    "did": DID,
    "verdict": "green",
    "next": NEXT,
    "current_task": CURTASK,
    "last_round_ts": st.get("ts", TS),
    "last_result": "ok",
    "last_tick": NOW.strftime("%H:%M"),
    "ts": TS,
    "last_seen": TS,
    "last_run": f"R284 {NOW.isoformat()}",
    "last_round_at": TS,
    "updated": TS,
    "updated_at": TS,
})
with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
raw2 = open(STATE, "rb").read()
assert raw2[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw2 and not raw2.endswith(b"\n")
assert json.loads(raw2.decode("utf-8"))["round_no"] == 284

# ---- heartbeat (byte face: LF, no BOM, indent=1, NO trailing newline)
raw = open(HB, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw and not raw.endswith(b"\n")
hb = json.loads(raw.decode("utf-8"))
hb.update({
    "last_seen": TS,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW.astimezone().isoformat(),
    "current_task": CURTASK,
    "round_no": 284,
    "round": 284,
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
    f"{NOW.isoformat()} | r284 (bm-b) | dept:数据/工程 | WM-VERDICT: GREEN "
    "healthy red=false (probe verdict=py_low_board_clear 板清合法闲面: 板 0 "
    "open/33 claimed 全占, bandit next_pick=claimed, bm-b 车道零 ready 候选"
    "——REV-OSC ready 属 bm-a lane_owner, T-87 首拉批=网络限速采集在飞低 py "
    "合法面) | did: T-87 供给线中途健康探针#4 on_track (714/5228=13.7% 路 "
    "rate 12.65/min lock-start 面 路 ETA 2026-09-27T06:40:36=周一 09:15 "
    "死线前余 26.5h 路 713/714@cutoff 2026-09-24 路 1 例早尾=suspension 诚实面 "
    "路 header_mismatch=0 路 ohlc_bad=0 路 lock alive 路 探针谱系=冻结复用 "
    "r283 正典零重建, 本轮临时速率探针 a/b/c 已废弃删除) + 票面 "
    "progress_r284_bmb 字段增量 2+/1- (R255 五面探测门过, 首跑 stat 摘要列解析 "
    "小修后幂等复核) + watch 面: REV-OSC 池 re-entry ready@00:31 (bm-a lane, "
    "autofill 待点火) + CN_TREND_ETF_P1 池面未见 (bm-a runner 待建, watch "
    "only) + Optuna 门复核 6 validated<8 维持 gated (探针初跑把 _template.json "
    "示例 id TREND-001 误计=轮内自捕矫正, 计数面坑律已入 CODELY.md, 零真实"
    "缺陷) + S6 22 腿 rc=0 (周末诚实 no-op: update_daily 无新行, astock_daily "
    "lock-alive no-op, market_clock CALL-2026-09-24 ORANGE_COOL 幂等再生, "
    "compute_audit CLEAN flags=[], 他机车道 stdout-only, fundamental 新鲜跳过) "
    "+ S0 预拉维护 commit e41d5791 (autofill 尾件解锁 rebase, r280/r281 律) + "
    "orders 89/89 双扫零未回执 + 决策审核步=本机无 ..\\..\\docs\\decisions.md "
    "(集团层在 bm-a 侧) 零动作 | evidence: results/_r284bmb_astock_pass_probe."
    "py+.json + results/_r284bmb_ticket_update.py + results/_r284bmb_watch.py+"
    "_r284bmb_watch_faces.json + results/_r284bmb_s6_chain.py+_r284bmb_s6_"
    "summary.json+_r284bmb_s6_logs/ + smoke 25/25 + schtasks 三任务在册 "
    "(Autofill/IterationLoop/Watchdog) | next: r285=pass 完成复探 (ETA 06:41 "
    "后, 谱系探针#5) + 周一 09-28 09:15 首次日续拉实弹 (stragglers gate 自愈腿) "
    "+ REV-OSC autofill 点火 watch (bm-a) + CN_TREND runner/pool 面 watch + "
    "迁移窗 watch (v2.2 armed 至 09-29 12:00) + 10-01 月首轮三件套 + HANDOVER "
    "5x 核对 (r285=5 倍数轮)\n"
)
with io.open(RR, "ab") as f:
    f.write(LINE.encode("utf-8"))
raw2 = open(RR, "rb").read()
assert raw2.endswith(b"\n")
import re
multi = len(re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", raw2.decode("utf-8")[-2500:]))
print("round_reports appended, tail-newline OK, ts-lines in tail:", multi)
print("WRAP_OK round=284 ts=" + TS)
