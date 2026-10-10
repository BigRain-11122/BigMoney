"""r841 bm-b closeout: state.json + heartbeat updates (load-modify-save,
r818 law -- orders_ack list never hand-retyped)."""
import datetime as dt
import json

now = dt.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")

# ---- state.json (bm-b uses root state.json per fleet README sec.6)
p = "state.json"
s = json.load(open(p, encoding="utf-8"))
s["round_no"] = 841
s["round_no_label"] = "r842"
s["note"] = ("r841: T23 slice-2 random-grammar census runner built "
             "(scripts/t23_random_grammar_census.py: frozen readout K=64 "
             "formula trees + B=64 within-day same-mask permutation nulls, "
             "primary face h1 rank-IC ICIR family-max vs null p95, negative-"
             "stops law; selftest 21/21 + real-data path probe PASS on "
             "partial per-set + gate legs live-fired awaiting_panel exit 2; "
             "seeds t23_grammar_census_gen/null 20_615_000/20_615_100 "
             "registered same-commit, rg 20615-band zero-hit, W17 band gap "
             "2500). astock rebuild verified alive (per-files disk count "
             "221->347 growing, pid 10404).")
s["last_round_at"] = ts
s["ts"] = ts
s["updated"] = ts
s["last_seen"] = ts
s["last_round_ts"] = ts
s["did"] = ("r841: T23 census runner built (selftest 21/21 + probe PASS) + "
            "seeds registered + astock rebuild progress verify + S6 41 legs")
s["verdict"] = ("r841: GREEN; smoke 49/49; census runner selftest 21/21; "
                "gate legs live-fired awaiting_panel exit 2 honest; dualrun "
                "ZERO-DRIFT streak 26; supply_gap standing flag (O-1645); "
                "alloc rc=2 known P5 stale-leg 510880; zero double-burn; "
                "idle cleared via --worked")
s["current_task"] = ("r842 queue: astock rebuild completion verify (window "
                     "~10-11 01:00+ per disk-count pace) -> spawn detached "
                     "T23 census full burn (~15-25min long job) -> "
                     "census_holds readout -> N2 U3 (1) prereg drafting "
                     "window if holds / G2 academic-citation fallback if "
                     "negative + S6 chain")
s["next"] = s["current_task"]
s["now_active"] = ("r841 closeout: T23 census runner + seeds + astock "
                   "rebuild verify + S6 41 legs")
s["latest_artifact"] = ("r841: scripts/t23_random_grammar_census.py "
                        "(+ scripts/science_gates.py seed berth "
                        "20_615_000/20_615_100) + "
                        "results/_r841bmb_t23_census_probe.py real-data "
                        "path probe PASS, 2026-10-10 21:1x")
s["next_milestone"] = ("r842-3 (window <=10-11 06:00): astock panel complete "
                       "-> detached T23 census burn -> holds verdict; W18 "
                       "legs stay drain-gated (bm-a owns w17-judge)")
s["task"] = s["current_task"]
s["last_action"] = s["did"]
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(p, "a", encoding="utf-8").write("\n")

# ---- heartbeat fleet/machines/bm-b.json
p2 = "fleet/machines/bm-b.json"
h = json.load(open(p2, encoding="utf-8"))
import time as _t
h["last_seen"] = ts
h["ts"] = ts
h["current_task"] = s["current_task"]
h["heartbeat_epoch_utc"] = int(_t.time())
h["clock_read"] = ts
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["verdict"] = ("GREEN-IDLE cleared via --worked: r841 product work = T23 "
                "census runner (selftest 21/21) + astock rebuild in flight "
                "(disk count 347/5229 growing)")
h["did"] = s["did"]
h["latest_artifact"] = s["latest_artifact"]
h["next_milestone"] = s["next_milestone"]
json.dump(h, open(p2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(p2, "a", encoding="utf-8").write("\n")

# self-verify epoch int + clock_read T-separator (F7 law)
h2 = json.load(open(p2, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"], "clock_read must be ISO T-separated"
print("closeout writes OK:", ts, "| epoch", h2["heartbeat_epoch_utc"],
      "| ack list len", len(h2.get("orders_ack", [])))
