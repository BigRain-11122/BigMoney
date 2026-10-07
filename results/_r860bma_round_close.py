"""r860 bm-a round close: state round_no, heartbeat, round report line,
HANDOVER 5x stamp. Fresh-read-modify-write on every multi-writer file."""
import json
import time
import datetime
import io

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
NOW_COMPACT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
R = 860

# --- state-bm-a.json: round_no +1 ----------------------------------------
SP = r"state-bm-a.json"
s = json.load(open(SP, encoding="utf-8"))
if s.get("round_no") == 859:
    s["round_no"] = R
    s["last_round_closed"] = f"r{R}"
    s["last_round_ts"] = NOW
    tmp = SP + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)
    import os
    os.replace(tmp, SP)
print("state round_no ->", json.load(open(SP, encoding="utf-8"))["round_no"])

# --- heartbeat fleet/machines/bm-a.json -----------------------------------
HP = r"fleet\machines\bm-a.json"
h = json.load(open(HP, encoding="utf-8"))
if h.get("round_no") != R:
h["machine_id"] = "bm-a"
                "(25min cooldown post instant-exit; runner_args FIXED "
                "both faces)")
h["current_task"] = (f"r{R}: W16 screen-finalize LANDED + judge-prep PASS "
                     "+ JUDGE seat enrolled (pool 408) + args fix + fuse "
                     "false-crash tombstones x2 + SCREEN harvest flip done")
h["task"] = "TRIAL_LABOR_W16 judge line (T-172 standing supply)"
h["last_artifact"] = ("results/trial_labor_w16/w16_screen.json + "
                      "w16_screen_cells.csv (null p95 0.5116 in-band, "
                      "survivors 40/173) @2026-10-08T03:44+08:00")
h["latest_artifact"] = h["last_artifact"]
h["next_milestone"] = ("W16 judge burn (daemon claim ~04:16) -> "
                       "judge-finalize + s4 intake <=06:30 today; 48h CEO "
                       "report clock starts at judge-finalize")
h["verdict"] = ("W16 funnel advanced (SCREEN done 03:58 + JUDGE ready; "
                "ignition cooldown window lawful ~04:16; watermark "
                "red=false healthy; orphan face=1 BigDomain cross-company "
                "read-only)")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["last_seen"] = NOW
h["ts"] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["round"] = R
h["round_no"] = R
h["loop_round"] = f"r{R}"
h["last_round"] = f"r{R}"
h["now_active"] = (f"r{R} closing; W16-JUDGE daemon ignition ~04:16 "
                   "post-cooldown")
h["notes"] = ("10-08 market reopen; CPU reserve law held (BelowNormal); "
              "holiday fullburn window code-face ends 10-09 00:00 per "
              "O-1858")
tmp = HP + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
os.replace(tmp, HP)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat written | epoch:", chk["heartbeat_epoch_utc"],
      "| int-type OK")

# --- round report line ------------------------------------------------------
RP = r"results\round_reports-bm-a.md"
raw = io.open(RP, encoding="utf-8", newline="").read()
sep = "\r\n" if raw.endswith("\r\n") else "\n"
assert "| r860 |" not in raw, "r860 line already present"
line = (
    f"{NOW} | r{R} | bm-a | dept:策略+研究 | S0-1 anchor + orphan probe 孤儿面=1 "
    "(BigDomain cross-company read-only) | orders unacked=[] 双扫描 + DEC/ORD "
    "hash identical (ee659451/2bb2ee75) 零动作 | smoke 49/49 + watermark "
    "red=false healthy + satengine alive | 当前活=W16 漏斗三层推进（SCREEN->JUDGE）| "
    "最近实物=results/trial_labor_w16/w16_screen.json + w16_screen_cells.csv "
    "(03:44 finalize, null p95 0.5116 带内[0.50,0.52], 存活 40/173) + "
    "judge_state.json | 下个里程碑=W16-JUDGE daemon 点火 ~04:16 -> "
    "judge-finalize + s4 intake <=06:30 今日（48h CEO 呈报钟起于 judge-finalize）| "
    "PRODUCT: W16 SCREEN 373-cell burn complete 03:37 (checkpoint full) -> "
    "screen-finalize LANDED (null p95 0.5116 in-band, survivors 40/173) -> "
    "w16_screen.json + cells csv; judge-prep PASS 30s (manifest 48/48, census "
    "L/D frozen-equal, sixteen-gate dual-leg meta); TRIAL-LABOR-W16-JUDGE "
    "seat enrolled two-leg r859 law (submit validate + raw-text insert, "
    "pool 408) | infra heals: pool stale-compact revert (03:32:12 post-claim "
    "write lost owner_since -> origin-verbatim restore, claim 03:32:08 "
    "intact zero-info-loss); enrollment runner_args comma-string bug fixed "
    "both faces (W16-JUDGE argparse instant-exit root cause); fuse "
    "false-crash tombstones x2 (r824 precedent: JUDGE args-bug + SCREEN "
    "harvest-gap completion); SCREEN worker-claim + harvest flip done 03:58 "
    "(W13/W14 observing-round law) | S6 35 legs rc0 (dualrun ZERO-DRIFT "
    "408 entries streak 51 + pre-market no-ops legal + CEO faces regen "
    "REPORT/LIVE-2026-10-08 + dashboard + scorecard) | 3 pits appended "
    "(pit-pool-edit: runner_args 逗号串 / worker-claim 收割缺半三件套 / "
    "claim 后 compact 覆写) | HANDOVER 5x stamp r856-r860 | "
    "本地未达 origin commit 数=0（push 后 fetch 自证；被拒则 addendum 披露）"
)
if not raw.endswith("\n"):
    raw += sep
new = raw + line + sep
io.open(RP, "w", encoding="utf-8", newline="").write(new)
print("round report r860 line appended")

# --- HANDOVER 5x stamp (r860 % 5 == 0) -------------------------------------
HD = r"research\HANDOVER.md"
raw = io.open(HD, encoding="utf-8", newline="").read()
hs = "\r\n" if "\r\n" in raw else "\n"
assert "bm-a round 860 窗复核" not in raw, "5x stamp already present"
stamp = (
    f"> bm-a round 860 窗复核（2026-10-08 03:5x）：覆盖 r856-r860（法面权威="
    f"round_reports-bm-a.md 全量在库）。本窗净产出=**TRIAL_LABOR_W16 漏斗三层推进**"
    "（GENERATE done 10-07 19:20 n=173 -> SCREEN 373 cells 烧录 03:37 + finalize "
    "03:44〔null p95 0.5116 带内·存活 40/173·w16_screen.json+cells csv〕-> "
    "judge-prep PASS 30s 双腿 census 冻结恒等 -> JUDGE seat 入池 408 + 实参修正 + "
    "fuse 假崩双 tombstone（r824 范式）+ SCREEN 收割翻面 done 03:58〔W13/W14 观察轮 "
    "接管律〕；JUDGE 烧录 04:16 后 daemon 自取）+ r856-r859 三连 S0 风暴正典解"
    "（r857 cycle_position 普查产品 + r858/r859 双风暴收口）+ 3 坑律入册"
    "（pit-pool-edit：runner_args 逗号串 / worker-claim 收割缺半三件套 / claim 后 "
    "compact 覆写）。"
)
if not raw.endswith("\n"):
    raw += hs
new = raw + stamp + hs
io.open(HD, "w", encoding="utf-8", newline="").write(new)
print("HANDOVER 5x stamp appended (r856-r860)")
print("ROUND-CLOSE WRITES DONE")
