"""r241 closing: ticket progress + state.json + round report + heartbeat."""
import json, time, os

TS = time.strftime("%Y-%m-%d %H:%M:%S")

# 1) T-78 ticket progress_r241 (probe original indent per R230 law)
tp = "fleet/tasks/T-2026-09-26-78-P1.json"
raw = open(tp, encoding="utf-8-sig").read()
d = json.loads(raw)
indent = 2
probe = raw.splitlines()[1] if "\n" in raw else raw
if probe.startswith("  ") is False and probe.startswith("\t"):
    indent = "\t"
d["progress_r241"] = (
    "s2+s3 DELIVERED same-day (claim r240 -> freeze r240 -> machinery+run r241): "
    "engine/backtester.py dd_control additive flag (None=legacy byte-equal, entry-size "
    "face only, no forced liquidation per CASH_LEG precedent, hysteresis "
    "dd_trigger/de_risk_to/re_up_at, day-end state from NAV incl. parked, new metric "
    "keys only when ON; selftest legs crash-forcing + V-recovery + guards 5/5) + "
    "scripts/exit_overlay_p1.py runner (hermetic selftest 5/5, anchor gate via "
    "live.paper.anchor_gate 6/6 OK, batch cutoff 09-24, 42 engine runs inline 33s). "
    "VERDICT: 6 WIN / 18 REJECT (ledger 184826->184856, N_eff=30; gate_attrition row). "
    "WINs: COMPOSITE-01 tp_ladder / COMPOSITE-02 tp_ladder+dd_control+full / ENGULF "
    "trail_peak+full. Honest faces: dd_control never triggered on 4 members (NAV dd "
    "<10% structurally) = zero-gain REJECT per frozen law; predictions hit 4/5 "
    "(ov_full 2/6 WIN slightly above the <=1/6 call, disclosed in prereg 7). "
    "NEXT (s4): winner wiring per prereg 10 -- member registration exit_overrides/params "
    "updates in independent commit + paper wiring + smoke anchor expectations re-derive "
    "+ three-state notation + AGGR sleeve inheritance check; CN-GRID-SLEEVE prereg (9) "
    "parallel lane.")
d["status"] = "claimed"
out = json.dumps(d, indent=indent, ensure_ascii=False)
if not out.endswith("\n"):
    out += "\n"
open(tp, "w", encoding="utf-8", newline="").write(out)
print("ticket progress_r241 written")

# 2) state.json (bm-b own state; round_no 240->241)
sp = "logs/iteration-loop/state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 241
s["did"] = ("r241: T-78 s2+s3 -- engine dd_control additive flag + EXIT-OVERLAY-P1 "
            "paired-judgment bench RUN (anchor 6/6, 6 WIN / 18 REJECT, ledger 184856) "
            "+ prereg 7/8 backfill; commit afee27e5 pushed")
s["verdict"] = "GREEN"
s["next"] = ("T-78 s4 winner wiring (6 WIN cells -> registrations + paper + smoke re-derive); "
             "CN-GRID-SLEEVE prereg draft; S6 chain legs this round were pre-empted by the "
             "25-min budget -- next round S0 must run the full chain first")
s["ts"] = TS
s["updated_at"] = TS
s["updated"] = TS
open(sp, "w", encoding="utf-8", newline="").write(json.dumps(s, indent=2, ensure_ascii=False))
print("state.json -> 241")

# 3) round report line (bm-b canon file)
line = (f"{TS} | r241 | T-78 s2+s3: engine dd_control additive flag (entry-size face, "
        f"None byte-equal, hysteresis; selftest 5/5) + EXIT-OVERLAY-P1 bench run "
        f"(anchor 6/6 OK, 6 WIN/18 REJECT, cutoff 09-24, 42 runs 33s, ledger 184826->184856, "
        f"gate_attrition row, prereg s7/s8 backfilled) | evidence: commit afee27e5 pushed "
        f"origin/main; results/exit_overlay_p1.json + research/exit_overlay_p1_results.csv "
        f"| next: T-78 s4 winner wiring (6 WIN cells) + CN-GRID-SLEEVE prereg; S6 chain "
        f"deferred to next round (25-min budget), S0 must run it first\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(line)
print("round report appended")

# 4) heartbeat (bm-b own file only; epoch int per R170/R178 law)
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8-sig"))
h["last_seen"] = TS
h["current_task"] = "T-78 s2+s3 delivered (r241); s4 winner wiring next"
h["round_no"] = 241
h["verdict"] = "GREEN"
epoch = int(time.time())
assert isinstance(epoch, int)
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
open(hp, "w", encoding="utf-8", newline="").write(json.dumps(h, indent=2, ensure_ascii=False))
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written, epoch int verified:", epoch)

print("CLOSING BLOCK DONE")
