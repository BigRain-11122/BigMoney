"""r272 bm-b closing writes: state.json (round 272), heartbeat bm-b.json, round report line.

Byte-face law mirror (R254/R255/R257): state.json = CRLF, indent=1, no trailing NL;
heartbeat = LF, indent=1, no trailing NL; round_reports.md = mixed EOL, current tail
(r271 line) = LF, no trailing NL -> append with one blank LF separator line, LF content,
no trailing NL. epoch = python int; clock_read = ISO 8601 T-separator.
"""
import json, time, datetime, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")  # T-separator law (R262)
EPOCH = int(time.time())  # JSON int law (R170/R178)

VERDICT = ("healthy r272: CODELY.md hot-cold recompile delivered (50,172B->48,912B, "
           "2 flow lines archived zero-loss); S6 ~25 legs exit 0; smoke 25/25; pool 49/49; orders 83/83")
CUR_TASK = ("r272 done: CODELY.md hot-cold recompile (47.8KB, multiset zero-loss PASS); "
            "next: 09-28 Monday-window channels/marks + 10-01 month-first trio")

# ---------- state.json (CRLF face) ----------
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
sb = open(SP, "rb").read()
assert sb.count(b"\r\n") == sb.count(b"\n") and not sb.endswith(b"\n") and sb[:3] != b"\xef\xbb\xbf", "state face drift"
state = json.loads(sb.decode("utf-8"))
assert state["round_no"] == 271, f"unexpected round_no {state['round_no']}"
state.update({
    "round_no": 272,
    "did": "r272: CODELY.md hot-cold recompile (50,172B->48,912B 47.8KB; 2 flow lines to research/memory-archive/202609.md; line-multiset zero-loss PASS) + MF_IC gate recheck honest (bm-a lane) + S6 ~25 legs exit 0 weekend",
    "verdict": "green",
    "next": "r273: 09-28 Monday window (T-76 channels run-6/10/4 + jin-gong 260928 verify + T-78 GRID marks + MF_IC on panel self-heal bm-a lane); 10-01 month-first trio + REGIME_GUARD v3 date gate auto-activation",
    "last_round_ts": NOW_ISO,
    "last_result": "ok",
    "current_task": CUR_TASK,
    "last_tick": NOW.strftime("%H:%M"),
    "updated_at": NOW_ISO,
    "last_seen": NOW.strftime("%Y-%m-%dT%H:%M:%S"),
    "ts": NOW.strftime("%Y-%m-%d %H:%M"),
    "last_run": f"R272 {NOW_ISO}",
    "last_round_at": NOW.strftime("%H:%M"),
    "updated": NOW.strftime("%H:%M"),
})
new_state_bytes = json.dumps(state, ensure_ascii=False, indent=1).encode("utf-8").replace(b"\n", b"\r\n")
open(SP, "wb").write(new_state_bytes)
chk = json.loads(open(SP, "rb").read().decode("utf-8"))
assert chk["round_no"] == 272 and open(SP, "rb").read().endswith(b"}"), "state write verify failed"

# ---------- heartbeat bm-b.json (LF face, indent=1, no trailing NL) ----------
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb_b = open(HB, "rb").read()
assert hb_b.count(b"\r\n") == 0 and not hb_b.endswith(b"\n") and hb_b[:3] != b"\xef\xbb\xbf", "heartbeat face drift"
hb = json.loads(hb_b.decode("utf-8"))
hb.update({
    "last_seen": NOW_ISO,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW_ISO,
    "current_task": CUR_TASK,
    "round_no": 272,
    "verdict": VERDICT,
    "cpu_cores": 16, "cores": 16,
    "free_ram_gb": 12.8, "idle_ram_gb": 12.8, "idle_ram_mb": 12800,
    "total_ram_gb": 23.9,
    "cpu_util_pct": 1.5, "cpu_pct": 1.5,
    "gpu_free_vram_gb": 2.4, "gpu_idle_vram_gb": 2.4, "gpu_free_vram_mb": 2413, "gpu_idle_vram_mb": 2413,
    "n_orders_ack": hb.get("n_orders_ack", 83),  # unchanged this round (diff empty)
})
open(HB, "wb").write(json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8"))
b2 = open(HB, "rb").read()
chk_hb = json.loads(b2.decode("utf-8"))
assert isinstance(chk_hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk_hb["clock_read"] and "+" in chk_hb["clock_read"], "clock_read must be T-sep ISO with offset"
assert b2.count(b"\r\n") == 0 and not b2.endswith(b"\n"), "heartbeat face broken"

# ---------- round_reports.md (append r272 line, LF, blank separator, no trailing NL) ----------
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
rp_b = open(RP, "rb").read()
assert not rp_b.endswith(b"\n"), "round reports gained trailing NL -- face drift"
line = (
    NOW_ISO + " | r272 (bm-b) | dept:工程/治理 | WM-VERDICT: GREEN insufficient_history "
    "(probe 20:07 early window n=2 py 0.2%; board 0 open / pool 49/49 done / bandit next_pick moneyflow IC "
    "parked bm-a-lane panel-empty honest; red=false; audit FLAG pool_starvation = supply-gap legal idle per O-1137) "
    "| did: S0 tick-faces (autofill_state + p1d_gates watchdog regen) stash + checkout discard per R252 recipe "
    "(stash pop output lost to nonexistent pipe target, recovered by stash-list/status probe -- r252 family), "
    "pull up-to-date; S0.5 orders 83/83 canonical orders_diff empty + decisions.md absent P-32 zero-action + inbox 0; "
    "S1 smoke 25/25; S2 board 0 open / job_list empty / post_review 29 YES 0 NO 5 WAIT zero debt; "
    "S3 MAIN = CODELY.md hot-cold recompile r272 batch per r271 pointer4 (50,172B->48,912B 47.8KB; 2 flow lines "
    "[执行记录 bm-b r252 / bm-a R263] moved verbatim into research/memory-archive/202609.md under "
    "round-discriminated batch header; line-multiset zero-loss + verbatim-in-cold + byte-face gates all PASS; "
    "deterministic script results/_r272bmb_recompile.py idempotent exit-2 guard); MF_IC_P1 gate recheck honest "
    "(panel bm-a lane empty on bm-b = legal wait, bandit stays parked); S4 four-question gate: zero append "
    "(recompile = existing-law execution, no new pit dimension); S6 ~25 legs all exit 0 weekend faces "
    "(audit FLAG pool_starvation supply / watermark insufficient_history early-window / daily 0 new rows cutoff 09-24 / "
    "regime ORANGE shadow breadth 0.77 / scorecard 6/28/7 cards 12.0s / clock CALL-2026-09-24 ORANGE_COOL sleeves=4 "
    "activated=0 idempotent / lhb 30min guard / heat weekend / futures cutoff-covered zero network / "
    "options+mf+sina_mf+ths+ah bm-a-lane + fp bm-c-lane honest no-ops / fundamental 23.0h fresh skip / blf pass / "
    "aggr+alloc+grid marks no-ops / t35 export 2026-09-24 regen / dsc 6 traders / daily report REPORT-20260926 "
    "faces=4 token=1 / monitor 432combos 5/7 milestones / token delta 0 L2 1 retro leg watchdog) "
    "| evidence: recompile gates PASS + git diff --stat CODELY.md 2- / archive 4+ field-level + S6 leg exit codes "
    "in transcript + smoke 25/25 | next: (1) 09-28 Monday window: T-76 channels run-6/10/4 + jin-gong 260928 "
    "verify + T-78 GRID marks + MF_IC on panel self-heal (bm-a lane); (2) 10-01 month-first trio + REGIME_GUARD v3 "
    "date gate auto-activation; (3) #90 AO pick-two rides T-34; (4) CODELY.md 47.8KB headroom ~2KB"
)
open(RP, "wb").write(rp_b + b"\n\n" + line.encode("utf-8"))
rp_b2 = open(RP, "rb").read()
assert not rp_b2.endswith(b"\n"), "round reports must keep no-trailing-NL face"
assert rp_b2.count(b"\r\n") == rp_b.count(b"\r\n"), "CRLF lines must be untouched"
assert line[:26].encode("utf-8") in rp_b2, "r272 line missing after write"

print("close PASS: state 272 | heartbeat epoch int", chk_hb["heartbeat_epoch_utc"],
      "| clock", chk_hb["clock_read"], "| report line", len(line), "chars")
