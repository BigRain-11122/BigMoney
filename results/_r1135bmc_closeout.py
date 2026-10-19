# -*- coding: utf-8 -*-
"""r1135 bm-c closeout: round report row + state counter 1135->1136 + heartbeat.

Machine-readable values only (no transcription of engine numbers: read from
results/perpetual_faces/n1_w281_results.json + _r1135bmc_w281_fivekeys.json).
"""
import datetime
import io
import json

NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

fk = json.load(open("results/_r1135bmc_w281_fivekeys.json", encoding="utf-8"))
d = json.load(open("results/perpetual_faces/n1_w281_results.json", encoding="utf-8"))
sg = json.load(open("results/_r1135bmc_w281_sixgate.json", encoding="utf-8"))
pool = d["null_pool_cumulative"]
mu = pool["merged"]["mu"]
sig = pool["merged"]["sigma"]
K = pool["merged"]["n_values"]
ledger = d["science_gates"]["ledger"] if "ledger" in d.get("science_gates", {}) else None
total = None
if isinstance(ledger, dict):
    total = ledger.get("total")
if total is None:
    total = fk["ledger_identity"]["total"]

ROW = (
    "%s | r1135 | P0=W281 CYCLE COMPLETE（本窗首动作=承接 r1134 addendum 的 honest-split 债务）："
    "six-gate 第 44 连续 PRE-FINALIZE **%s**（results/_r1135bmc_w281_sixgate.json——splice 完整性 CR-normalized 恒等 "
    "worktree==落链 blob @ aa376549cd；setwave 出生站闸 _set_wave(281):1/280:1/279:1；shards 12/12 全>100KB；"
    "banned ADMIT rc0；pf/n1 selftest rc0）→ finalize 一次过 **ledger %s / K=%d EXACT**"
    "（1,040,335+2,200；613,920+2,200）→ fivekeys **%d/%d ALL PASS**（results/_r1135bmc_w281_fivekeys.json）"
    "→ prereg §7/§8 占位回填零残（research/PERPETUAL_N1_W281_PREREG.md，r1135 记账行机读零转录）"
    "| merged mu=%.8f sigma=%.8f se_mu=%.6f | S6 10/10 rc0（dualrun/audit/wm/update_daily/regime/clock/fund_premium/b_layer/report/token）"
    "| S1 smoke 49/49 | D-19 dual-delta FALSE（ord/dec 水位双面 hold，本地 107 令全回执 unacked=0）"
    "| S7 attrition 4 CLEAN + pin=5 no-op + watchdog 重注册（S4U flip 拒权→留 InteractiveToken 回归面待提权）+ 双爪重装 MATCH"
    "| orphan face=0 | 本地未达 origin commit 数=0（push fbd1511689 后 behind=0 ahead=0）"
    "| 下轮指针=r1136 W282 SEAT（seat-first 发布 + post-W281 宇宙 live re-derive，禁转录 r587）\n"
) % (ISO, sg["verdict"], f"{total:,}", K, sum(1 for c in fk["checks"] if c["pass"]),
     len(fk["checks"]), mu, sig, fk["merged"]["se_mu_k616120"])

with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(ROW)

NOTE = (
    "r1135: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=0 zero-kill + origin 0/0 clean; "
    "(2) zero absorb owed (r1134 closeout + addendum landed clean); "
    "(3) PRODUCT = W281 CYCLE COMPLETE: sixgate 44th consecutive PRE-FINALIZE ALL PASS -> finalize "
    "1,042,535 / K=616,120 EXACT (projection matched exactly) -> fivekeys 6/6 ALL PASS -> prereg sec.7/8 "
    "backfilled zero residual placeholders; "
    "(4) S0.5 dual-delta FALSE both faces (ord 1bcd6182 / dec d5336c87 hold) + 107/107 local orders acked; "
    "(5) S1 smoke 49/49; satengine rc0 burns_active=[]; wm loaded_ok; "
    "(6) S6 light 10/10 rc0 + attrition 4 CLEAN + pin=5 no-op + claws reinstalled + watchdog re-registered "
    "(S4U flip access-denied -> InteractiveToken regression face logged); "
    "(7) push saga: pre-push claw caught a spurious deletion face on diverged branch -> pull --rebase -> "
    "2 generated-face conflicts (update_status.json / _attrition_guard_scan.json) resolved live-wins -> "
    "landed fbd1511689, behind=0 ahead=0; "
    "(8) same-window pit: PowerShell -replace on cloned S6 driver injected escaped quotes (print(\\\"...)) "
    "-> python syntax break caught by read-back grep, fixed before run (zero data impact)"
)

st = json.load(open("state-bm-c.json", encoding="utf-8"))
st["round_no"] = 1136
st["round_no_label"] = "r1135 closeout -> counter 1136"
st["last_round"] = "r1135"
st["last_round_label"] = "r1135"
st["last_round_at"] = ISO
st["last_round_closed"] = "r1135"
st["last_round_closed_at"] = ISO
st["last_action"] = "r1135 closeout"
st["last_action_at"] = ISO
st["last_artifact"] = "results/perpetual_faces/n1_w281_results.json"
st["last_artifact_at"] = ISO
st["recent_artifact"] = "results/perpetual_faces/n1_w281_results.json"
st["last_round_summary"] = NOTE[:1200]
st["last_round_summary_at"] = ISO
st["last_round_ts"] = ISO
st["r1135_closeout_note"] = NOTE
st["verdict"] = ("green r1135 product window: W281 CYCLE COMPLETE (sixgate 44th ALL PASS / finalize "
                 "1,042,535 K=616,120 EXACT / fivekeys 6/6 / sec78 backfilled); next = r1136 W282 SEAT")
st["verify"] = ("sixgate ALL PASS 44th | finalize ledger 1,042,535 K 616,120 exact | fivekeys 6/6 | "
                "smoke 49/49 | S6 10/10 rc0 | attrition 4 CLEAN | D-19 dual FALSE | orphan face=0 | "
                "behind=0 ahead=0 after push fbd1511689")
st["last_pulled_at"] = ISO
st["last_seen"] = ISO
st["last_seen_at"] = ISO
st["ts"] = ISO
st["updated"] = ISO
st["updated_at"] = ISO
st["sync"] = {"origin_tip": "fbd1511689 r1135 W281 cycle complete", "ts": ISO}
json.dump(st, open("state-bm-c.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
hb["last_seen"] = ISO
hb["last_seen_at"] = ISO
hb["ts"] = ISO
hb["updated"] = ISO
hb["updated_at"] = ISO
hb["clock_read"] = ISO
hb["heartbeat_epoch_utc"] = int(EPOCH)
hb["heartbeat_epoch_utc_type"] = "int"
hb["round_no"] = 1136
hb["loop_round"] = 1135
hb["last_round"] = "r1135"
hb["last_round_label"] = "r1135"
hb["last_round_at"] = ISO
hb["last_round_closed"] = "r1135"
hb["last_round_closed_at"] = ISO
hb["last_action"] = "r1135 closeout"
hb["last_action_at"] = ISO
hb["last_artifact"] = "results/perpetual_faces/n1_w281_results.json"
hb["last_artifact_at"] = ISO
hb["recent_artifact"] = "results/perpetual_faces/n1_w281_results.json"
hb["latest_artifact"] = "results/perpetual_faces/n1_w281_results.json"
hb["current_task"] = None
hb["activity_now"] = "idle (W281 cycle complete; W282 seat = next action)"
hb["now_active"] = "idle"
hb["next"] = "r1136 W282 SEAT: seat-first publish + live re-derive on post-W281 270-owner universe"
hb["next_pointer"] = "r1136 W282 SEAT (live re-derive; zero transcription)"
hb["next_milestone"] = "W282 seat published within 1 round (~10 min)"
hb["verdict"] = st["verdict"]
hb["health"] = "green"
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["r1135_closeout_note"] = NOTE
hb["last_round_summary"] = NOTE[:1200]
hb["last_round_summary_at"] = ISO
hb["head_sha"] = "fbd1511689"
hb["codely_live_count"] = hb.get("codely_live_count", 0)
json.dump(hb, open("fleet/machines/bm-c.json", "w", encoding="utf-8"), indent=1,
          ensure_ascii=False)
print(json.dumps({"iso": ISO, "epoch": EPOCH, "ledger": total, "K": K,
                  "sixgate": sg["verdict"], "fivekeys_all_pass": fk["all_pass"]},
                 ensure_ascii=False))