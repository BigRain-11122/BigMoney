"""R302 bm-a wrap: T-87 ticket progress + state 302 + round report line +
heartbeat (epoch int + astimezone clock, r262/r302bmb law) + CODELY kenglu
(one line, <=10KB hard line re-asserted after append)."""
import datetime as dt
import json
import os
import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = dt.datetime.now().astimezone()
ts = now.isoformat()
assert "+08:00" in ts and "T" in ts, "clock face must be astimezone ISO"

# --- 1) T-87 ticket progress line -----------------------------------------
TP = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-26-87-P1.json")
t = json.load(open(TP, encoding="utf-8"))
assert "progress_r302_bma" not in t, "duplicate progress key"
t["progress_r302_bma"] = (
    "s2 queue #4 CN_SECTOR_LEADER_P1 HARVEST CLOSED judged-negative 4/4 "
    "(R302 bm-a): burn landed 07:28:39 pid 64840 elapsed ~503s; POOL DONE-FLIP "
    "FIRST ACTION pre-tick (flip 07:29:5x vs autofill tick 07:30:03 = re-burn "
    "risk killed; r291 re-read assert + result_ref + note_done); judged: x2 "
    "Sharpe FIX10 -0.5378/FIX20 +0.2288/SECT10 -1.3880/STOP10 -1.0618 vs "
    "own-null lines 2.041(H10 mu 0.8413)/3.5375(H20 mu 2.0495) all "
    "line_ok=False, CI95 lower all <=0, DSR<=0.0007, family PBO 0.0 but G1 "
    "fail -> G2 ineligible, batch ann<0 & maxDD -1.0 double-fail; D6 vs ew6 "
    "max|corr|<=0.0375 zero reject, within-batch 0.508-0.873 as predicted; "
    "census 8,466 starts beat6m 0.20-0.39 all<0.5; robust sign-flip p "
    "0.002/0.171/0.0/0.0; ledger 204,445=202,441+2,004; prereg s7/s8 "
    "single-finalization (p2 SECT10 whipsaw MISS honest; p5/p6 full hit); "
    "SCHOOL row-3 leader-lore stream fully judged-closed with WILD-S1, "
    "slot closed reopen=new-prereg only; post_review T-87-CN-SECTOR-LEADER-P1 "
    "registered 23 checks dry-run green, evaluator YES=39 NO=0; keepalive "
    "null-guard fix live-validated (07:30:04 tick zero fault). NEXT: queue #5 "
    "market-neutral prereg draft (R99: CTA-boundary mechanism disclosure + "
    "futures margin/roll cost face + seed registry)"
)
tmp = TP + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
json.load(open(tmp, encoding="utf-8"))
os.replace(tmp, TP)

# --- 2) state-bm-a.json -----------------------------------------------------
SP = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(SP, encoding="utf-8"))
st["round_no"] = 302
st["did"] = (
    "R302: CN-SECTOR-LEADER-P1 judged harvest closed -- 4/4 cells NEGATIVE "
    "(x2 Sharpe -0.5378/+0.2288/-1.3880/-1.0618 vs own-null lines "
    "2.041/3.5375 all line_ok=False, DSR<=0.0007, batch ann<0 & maxDD -1.0 "
    "double-fail; D6 <=0.0375 zero reject; 17,771 entries/cell gate pass); "
    "SCHOOL row-3 leader-lore fully judged-closed with WILD-S1; pool "
    "done-flip pre-tick (re-burn risk killed); post_review 23-check "
    "registration evaluator YES=39 NO=0"
)
st["verdict"] = "ok"
st["next"] = (
    "R303: supply #5 market-neutral prereg draft (PREREG_TEMPLATE + CTA "
    "no-reopen boundary mechanism disclosure + futures margin/roll cost "
    "face + seed registry R250 one-step) -- pool ready=0 post-harvest, R99 "
    "cadence; watch moneyflow detached rank-pass self-heal + ah_panel "
    "refresh completion"
)
st["ts"] = ts
st["last_round_ts"] = ts
st["updated_at"] = ts
st["current_task"] = "R302 done: sector-leader judged closure + pool flip"
st["last_run"] = ts
st["last_round_at"] = ts
st["last_round"] = 301
st["updated"] = now.strftime("%Y-%m-%dT%H:%M:%S")
st["last_seen"] = ts
st["task"] = "R303: #5 market-neutral prereg draft"
with open(SP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
chk = json.load(open(SP, encoding="utf-8"))
assert chk["round_no"] == 302

# --- 3) round report line ---------------------------------------------------
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
line = (
    f"{ts} | R302 bm-a (dept:research+strategy+fleet) | WM first-line "
    "verdict: red=false lane healthy (probe insufficient_history window n=2 "
    "11.6min honest-short; board 0 open + bandit 0 + pool ready=0 "
    "post-harvest = supply face R99 cadence #5 market-neutral prereg = "
    "next session work, judged-closure round no violation face) | did: "
    "CN-SECTOR-LEADER-P1 HARVEST CLOSED -- burn landed 07:28:39 (pid 64840 "
    "~503s) -> POOL DONE-FLIP FIRST ACTION pre-tick (07:29:5x flip vs "
    "07:30:03 autofill tick = re-burn risk killed; r291 re-read assert + "
    "result_ref + note_done) -> judged 4/4 cells NEGATIVE (x2 Sharpe "
    "FIX10 -0.5378/FIX20 +0.2288/SECT10 -1.3880/STOP10 -1.0618 vs own-null "
    "lines 2.041/3.5375 all line_ok=False; CI95 lower -0.92/-0.17/-1.74/"
    "-1.44 all <=0; DSR<=0.0007; family PBO 0.0 but G1 fail -> G2 "
    "ineligible 4/4; batch ann -0.71..-0.83 <0 AND maxDD -1.0 double-fail; "
    "OOS 2025+ oos_sharpe 1.45-4.01 positive disclosed single-window-no-"
    "rescue) | D6 max|corr| vs ew6 canon <=0.0375 zero reject + "
    "within-batch 0.508-0.873 (s5.6 predicted); robust sign-flip p "
    "0.002/0.171/0.0/0.0; census 8,466 starts beat6m 0.20-0.39 all<0.5 "
    "four segments sufficient; ledger 204,445=202,441+2,004 single-count; "
    "attrition row entries face (runner-written ts 07:28:39, r248 law) | "
    "prereg s7/s8 single-finalization (P1 hit null-floor 2.04/3.54 + thin "
    "negative gross -0.95..+0.50; P2 MISS honest: SECT10 whipsaw -158% vs "
    "+-20% band + maxDD no differentiation = KLINE p3 law re-proven; P3 "
    "hit decay direction via oos_halves/wf; P5 x1>=x2 4/4; P6 full hit) | "
    "SCHOOL row-3 leader-lore stream FULLY judged-closed (WILD-S1 limit "
    "face DEAD + sector-monopoly face negative) slot closed reopen=new-"
    "prereg only, next supply #5 market-neutral | post_review T-87-CN-"
    "SECTOR-LEADER-P1 registered 23 checks dry-run green -> evaluator "
    "YES=39 NO=0 WAIT=5 zero-X (no P0 from review face next round) | "
    "keepalive fix LIVE-VALIDATED: 07:30:04 tick zero fault line (R301 "
    "null-guard, no running shard clean no-op) | S6 30/30 rc=0 (audit v2.3 "
    "CLEAN; no new bar = Mid-Autumn 09-25 holiday, cutoff 09-24 consistent "
    "-> live.paper chain legs legal skip; moneyflow detached rank-pass "
    "spawn = 30-min self-heal face; ah_panel detached refresh in-flight; "
    "lane guards honest no-op astock=bm-b fundprem=bm-c; ths same-day "
    "idempotent; daily_report faces=4 token=1; scorecard 6/28/7 cards; "
    "build_status OK; token L2 local legs 0 today) | S0.5 orders "
    "double-scan 91/91 zero unacked (README basename false-face of scan "
    "noted, not an order) + decisions.md zero new lines (D-20260927-04 "
    "pending-weekly not-due noted; D-20260927-05 items standing) | smoke "
    "25/25 | S0 pull clean + push a664fa7f rc=0 | schtasks alive (loop "
    "Running next 07:38 + watchdog Ready 07:50) | inbox zero | state 302 "
    "+ heartbeat epoch int verified | NEXT: R303 supply #5 market-neutral "
    "prereg draft (R99) OR moneyflow self-heal watch; pool ready=0\n"
)
with open(RR, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)

# --- 4) heartbeat -----------------------------------------------------------
HP = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(HP, encoding="utf-8"))
cpu = psutil.cpu_percent(interval=1.0)
vm = psutil.virtual_memory()
h["last_seen"] = ts
h["current_task"] = (
    "R302 done: sector-leader queue#4 judged-negative closure + pool "
    "done-flip + post_review registration; next: #5 market-neutral prereg"
)
h["cpu_pct"] = cpu
h["free_ram_gb"] = round(vm.available / 2**30, 1)
h["verdict"] = (
    "py_low_board_clear LEGAL-side: judged-closure round (harvest+flip+"
    "registration session work); board 0 open + bandit 0 + pool ready=0 "
    "post-harvest; supply line = R99 prereg cadence #5 market-neutral next"
)
h["heartbeat_epoch_utc"] = int(dt.datetime.now().timestamp())
h["clock_read"] = ts
h["round_no"] = 302
h["task"] = "R303: #5 market-neutral prereg draft"
tmp = HP + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
h2 = json.load(open(tmp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"] and "+08:00" in h2["clock_read"]
os.replace(tmp, HP)

# --- 5) CODELY kenglu (one line, <=10KB hard line re-assert) ----------------
CP = os.path.join(ROOT, "CODELY.md")
txt = open(CP, encoding="utf-8").read()
size_before = len(txt.encode("utf-8"))
k = txt.find("### Project")
ins = txt.find("\n", k) + 1
entry = (
    "- [2026-09-27 07:3x r302 bm-a] 坑律：runner 落产物后池 entry 仍 "
    "ready，autofill 下 tick 即重烧完备批（checkpoint 幂等=浪费非损坏）；"
    "收割轮第一动作=done-flip 先于任何产物分析（本批 flip 07:29:5x vs tick "
    "07:30:03=10s 余量实弹）。指针=commit a664fa7f+logs/autofill.log 07:30:04 行\n"
)
txt2 = txt[:ins] + entry + txt[ins:]
size_after = len(txt2.encode("utf-8"))
assert size_after <= 10240, f"CODELY {size_after}B breaches 10KB hard line"
with open(CP, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(txt2)
print(f"wrap OK: ticket+state302+report+heartbeat(epoch {h2['heartbeat_epoch_utc']}) "
      f"+codely {size_before}->{size_after}B")
