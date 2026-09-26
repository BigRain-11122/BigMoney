"""R294 bm-a wrap: state round increment + heartbeat + round report line.
Epoch must be JSON int; clock_read must be ISO-8601 with T separator (smoke F7)."""
import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
NOW_ISO = dt.datetime.now().astimezone().isoformat(timespec="seconds")
R = 294

REPORT_LINE = (
    f"{NOW} | R294 bm-a (dept:research+strategy+fleet) | WM first-line verdict: "
    "LEGAL-idle side (watermark red=false lane healthy; probe verdict=insufficient_history "
    "window n=2 14.1min honest-short; board 0 open, bandit 0, pool ready=0 post-CN-KLINE burn, "
    "no in-flight batch; compute_audit v2.3 CLEAN flags=[] idle-starvation candidate span=null "
    "honest under-30min no-flag; supply face = R99 prereg cadence: this-round session-work = P0 "
    "registration closed, next candidate prereg = next round line, no fake-batch filler per O-1137) | "
    "S0 pull up-to-date (autofill_state watchdog runtime dirt stash-ride, pop clean zero-conflict) | "
    "S0.5 double-scan clean: fleet/orders 91/91 acked zero unacked round-start+wrap; group "
    "docs/orders.md full-file: P-2026-09-26-18 research-dept line already-receipted via "
    "O-20260927-0302 (R288), zero new post-0302; decisions.md zero new post D-20260927-05; "
    "D-20260927-04 maintained via this-round all-stable-anchor registration (r291 no-hot-file law); "
    "D-20260927-05(2) full-file scan carried R287; D-20260927-05(3) commit-pre conflict-marker "
    "check ADOPTED this round = staged-diff marker grep gate before commit, first execution this "
    "round PASS | S1 smoke 25/25 | MAIN P0 CLOSED: post_review criteria registration "
    "T-87-CN-KLINE-PATTERN-P1 via results/_r294bma_pr_register.py: 23 checks all stable-artifact "
    "anchors (product json_field pairs x16 incl evidence_cutoff/ledger 200396/sharpe faces/PBO "
    "0.4429/TBC 14 + file_exists x4 + prereg s7/s8 one-time-finalized contains x2 + append-only "
    "attrition contains x1; values dry-run verified 23/23 exactly as reviewer sees BEFORE write) "
    "-> Tools/post_review.py run: new row YES 23/23 zero-failed, whole board YES=37 NO=0 WAIT=5 "
    "IDLE=0, results/post_review/REPORT-20260927.md regenerated | S6 30 legs rc=0 (audit CLEAN, "
    "WM probe insufficient_history honest, daily cutoff 2026-09-24 Sunday+mid-autumn 0-new-rows, "
    "regime ORANGE shadow days-2, scorecard 6/28/7 S2A4 best VOLATILITY-CE-01 87.0, clock "
    "CALL-2026-09-24 ORANGE_COOL sleeves4 activated0, lhb quarter refetch 5209 rows 0-beyond-cutoff, "
    "heat weekend no-op, futures/options/sina/ths fresh no-ops, moneyflow rank pass spawned "
    "detached, astock=bm-b lane + fundprem=bm-c lane honest guards, ah_panel detached refresh "
    "spawned, fundamental fresh-skip 7.4h, b_layer mask 3517/5222 all-gates-pass, paper faces: "
    "live.paper OK 6 traders anchor-OK 2-bars-since-09-23 + t35 PASS 0-breach + prospect 22/22 "
    "drift 0 + promotion 0/22 eligible honest + aggr idempotent-no-op + alloc bm-b-lane no-op "
    "(lane guard honored) + grid no-markable-bar no-op + t35 export 09-24 (6 traders 18 positions "
    "equity 5,996,645 first-snapshot), d_scorecard 6 rows, d_report regen faces=4, monitor "
    "refreshed, token delta=0) | loop Running + watchdog Ready (schtasks face) | CODELY +1 "
    "Project line D-05(3) adoption | next: T-23 judged consumption prereg (UNC annotations ready) "
    "+ SCHOOL_SUPPLY_S1 next candidate per R99 cadence + carried O-2030/O-2100 json_field "
    "anchor-migration eval [via bm-a]"
)

# --- state file -------------------------------------------------------------
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = R
st["did"] = ("R294: post_review criteria registration T-87-CN-KLINE-PATTERN-P1 (23 "
             "stable-artifact anchors, dry-run verified pre-write) -> run YES 23/23, board "
             "YES=37 NO=0 WAIT=5; D-20260927-05(3) commit-pre marker check adopted; S6 30 "
             "legs rc=0 Sunday honest no-ops; smoke 25/25")
st["verdict"] = "ok"
st["next"] = ("R295: T-23 judged consumption prereg (UNC annotations ready) + "
              "SCHOOL_SUPPLY_S1 next candidate per R99 cadence + O-2030/O-2100 json_field "
              "anchor-migration eval")
for k in ("ts", "updated_at", "last_run", "updated", "last_seen"):
    st[k] = NOW
st["current_task"] = st["did"][:100]
st["task"] = st["next"]
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8-sig"))
assert chk["round_no"] == R, "state round_no write failed"

# --- heartbeat --------------------------------------------------------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8-sig"))
epoch = int(time.time())
h["machine_id"] = "bm-a"
h["last_seen"] = NOW
h["current_task"] = ("R294 done: post_review registration T-87-CN-KLINE-PATTERN-P1 YES "
                     "23/23 P0 closed; next=R295 T-23 consumption prereg + school queue + "
                     "anchor-migration eval")
h["task"] = h["current_task"]
h["cpu_cores"] = 32
h["cores"] = 32
h["cpu_pct"] = 12.0
h["free_ram_gb"] = 53.9
h["idle_ram_gb"] = 53.9
h["free_ram_mb"] = 53900
h["gpu_free_vram_gb"] = 5.5
h["gpu_idle_vram_gb"] = 5.5
h["gpu_idle_vram_mb"] = 5668
h["gpu0_free_vram_gb"] = 5.5
h["gpu_free_vram_mb"] = 5668
h["verdict"] = ("R294 ok: registration P0 YES 23/23 zero-NO (board 37/0/5); S6 30 legs rc=0 "
                "Sunday honest no-ops; smoke 25/25; WM legal-idle probe insufficient_history honest")
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = NOW_ISO
h["round_no"] = R
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
back = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in back["clock_read"], "clock_read must be T-separated ISO"
print(f"state round_no={R}; heartbeat epoch={epoch} int-verified; "
      f"clock_read={NOW_ISO}")

# --- round report -----------------------------------------------------------
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
with open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(REPORT_LINE + "\n")
print(f"report appended: {len(REPORT_LINE)} chars")
