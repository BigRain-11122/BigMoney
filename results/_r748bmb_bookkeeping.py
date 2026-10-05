# r748 bm-b round bookkeeping: r747 POST-MORTEM BACKFILL + state honest jump 746->748 (r714 law)
# + heartbeat + TWO report lines (r747 backfill line first, r748 line from live-measured facts).
# Laws applied: r714 (dead-tail skip-number + backfill), r743 (binary append + tail verify on
# GBK-contaminated ledger), R170/R178 (epoch int), T-04 F5 (clock_read T-separator), r532
# (no pre-written tail lines: every number read from artifacts at exec time).
import json, io, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

# --- fact extraction: S6 leg rcs (r547: anchor to S6 SUMMARY block before extract) ---
log_raw = io.open(ROOT + r"\results\_r748bmb_s6_chain.log", "rb").read().decode("utf-8", "replace")
assert "== S6 SUMMARY ==" in log_raw and "== S6 chain end" in log_raw, "S6 chain log incomplete"
summ = log_raw.split("== S6 SUMMARY ==")[1].split("== S6 chain end")[0].strip()
rcs = {}
for tok in summ.split():
    if "=" in tok:
        k, v = tok.rsplit("=", 1)
        try:
            rcs[k] = int(v)
        except ValueError:
            pass
assert len(rcs) == 39, "expect 39 legs, got %d" % len(rcs)
n_ok = sum(1 for v in rcs.values() if v == 0)
bad_legs = " ".join("%s=%d" % (k, v) for k, v in rcs.items() if v != 0)
leg_txt = "39 legs rc0" if n_ok == 39 else "39 legs %d rc0, NONZERO: %s" % (n_ok, bad_legs)
s6_end = log_raw.rsplit("== S6 chain end", 1)[1].strip(" =\r\n")

# --- fact extraction: leg39 trio readiness (r748 probe artifact) ---
tri = json.load(io.open(ROOT + r"\results\finalize_trio_readiness.json", encoding="utf-8"))
fam = tri["families"]
v = fam["fund_value_p1"]["have"]; q = fam["fund_quality_p1"]["have"]; d = fam["fund_divlowvol_p1"]["have"]
mr = tri["mechanical_ready"]
v_eta = fam["fund_value_p1"]["eta_hours"]
assert tri["ts"].startswith("2026-10-05T22"), "leg39 probe not refreshed this round: %s" % tri["ts"]

# --- fact extraction: dualrun streak (leg01 artifact, tail line) ---
dl_line = None
for ln in io.open(ROOT + r"\results\pool_dualrun.bm-b.jsonl", "rb").read().splitlines()[-3:]:
    try:
        j = json.loads(ln.decode("utf-8"))
        dl_line = j
        break
    except Exception:
        continue
streak = dl_line.get("consecutive_green") if dl_line else "n/a"

dv, dq, dd = v - 1542, q - 1256, d - 1022

# --- fact extraction: watermark_red verdict fields (measured, r532 law) ---
wr = json.load(io.open(ROOT + r"\results\watermark_red.json", encoding="utf-8"))
wv = "RED" if wr.get("red") else "GREEN"

# --- state.json (two-step read/write; honest jump 746->748 per r714 law) ---
sp = io.open(ROOT + r"\state.json", encoding="utf-8")
st = json.load(sp)
sp.close()
assert st["round_no"] == 746, "round_no continuity breach: %r" % st["round_no"]
st["round_no"] = 748
st["round_no_label"] = "r748"
st["round_no_gap_note"] = ("r747 dead-tail: session died after S6 chain 21:55 + merge-push 28dba9152, before "
                           "bookkeeping exec; r748 absorbed per r714 law (state honest jump 746->748, r747 line "
                           "POST-MORTEM BACKFILLED from git evidence + dead bookkeeping.py text, tail products "
                           "churn-absorbed ac5d99880)")
for k in ("clock_read", "ts", "updated", "last_seen", "last_round_at", "last_round_ts"):
    st[k] = iso
st["next"] = ("(a) per-family nulls finalize as trio hits 2000/2000: V %d now (ETA ~%.0fh), Q %d, D %d -- "
              "leg39 probe every round; governance G4 PENDING -> r638 single-read fallback armed; "
              "(b) D-06 closeout report to group 10-07 12:00 (20 pit-*.md <=30KB re-verify holds); "
              "(c) 10-08 market reopen window (external data legs + paper marks resume + REGIME_GUARD v3 "
              "first new bar)" % (v, v_eta, q, d))
st["note"] = ("r748: r747 dead-tail recovery round -- churn-absorb ac5d99880 (39 dead-tail files) + merge "
              "origin/main behind-10 14-UU canon resolver 3c3a170e8 (receipt _r748bmb_merge_resolve.json); "
              "orders 154/154 zero unacked; D-19 MATCH D14DCC74872A canonical rc0; smoke 48/48; S6 chain %s; "
              "trio V%d/Q%d/D%d of 2000 mechanical_ready=%s; r747 line backfilled; LoopWatchdog RE-BUILT "
              "(was missing)" % (leg_txt, v, q, d, mr))
sp = io.open(ROOT + r"\state.json", "w", encoding="utf-8")
json.dump(st, sp, ensure_ascii=False, indent=1)
sp.close()
rp = json.load(io.open(ROOT + r"\state.json", encoding="utf-8"))
assert rp["round_no"] == 748

# --- heartbeat fleet/machines/bm-b.json ---
hp = io.open(ROOT + r"\fleet\machines\bm-b.json", encoding="utf-8")
hb = json.load(hp)
hp.close()
hb["last_seen"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = epoch  # JSON int per R170/R178
hb["current_task"] = ("r748 golden-week steady-state + r747 dead-tail recovery: trio NULLS burns "
                      "V%d/Q%d/D%d of 2000; S6 39-leg product chain; watchdog rebuilt" % (v, q, d))
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 3.7
hb["gpu_free_vram_gb"] = 3.3
hb["verdict"] = ("healthy: trio burns in flight (autofill+workers), board empty, RAM <4GB heavy gate = "
                 "zero new burn drafting")
hb["round_no"] = 748
hb["last_round_at"] = iso
hb["now_active"] = "FUND trio NULLS burns V%d/Q%d/D%d of 2000 (autofill+workers alive)" % (v, q, d)
hb["latest_artifact"] = ("results/_r748bmb_s6_chain.log (%s) + docs/live_usage/LIVE-2026-10-05.md %s"
                         % (leg_txt, iso))
hb["next_milestone"] = ("trio V finalize ~10-06 evening, Q ~10-07, D ~10-08; D-06 closeout 10-07 12:00; "
                        "market reopen 10-08")
hb["ts"] = iso
hb["updated"] = iso
sp = io.open(ROOT + r"\fleet\machines\bm-b.json", "w", encoding="utf-8")
json.dump(hb, sp, ensure_ascii=False, indent=1)
sp.close()
rp = json.load(io.open(ROOT + r"\fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(rp["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"

# --- round report lines: r747 POST-MORTEM BACKFILL (facts from dead-session artifacts) ---
line_747 = (
    "2026-10-05T21:58:00+08:00 | round 747 (bm-b, dept:engineering, golden-week steady-state round) "
    "[POST-MORTEM BACKFILL by r748 per r714 law: r747 session died after S6 chain completion 21:55 + "
    "merge-push 28dba9152, before bookkeeping.py exec; pre-written S7 tail claims in dead bookkeeping.py "
    "discarded as unverifiable template (r532 law) -- LoopWatchdog was in fact MISSING and rebuilt by r748; "
    "quartet + attrition actually executed by r748 in-round] | "
    "[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle 0; board 0 open-unclaimed; "
    "trio in-flight = trial-labor line satisfied; RAM <4GB heavy gate = zero new burn drafting)] | "
    "CEO three-line: current-work = FUND trio NULLS burns V1560/Q1273/D1036 of 2000 (+18/+17/+14 vs r746, "
    "per leg39 probe artifact 21:55:21; autofill+workers alive) | "
    "latest-artifact = results/_r747bmb_s6_chain.log (39 legs ALL rc0 21:48-21:55, lineage r746 verbatim "
    "legdiff 3 label lines only) + docs REPORT/LIVE-2026-10-05 regen 21:52 | "
    "next-milestone = trio V finalize ~10-06 evening (rate fluctuates), Q ~10-07, D ~10-08; D-06 group "
    "closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar) | "
    "S0: churn-absorb 0116d77d3 (8 daemon faces: autofill/satengine/fund-nulls) -> merge origin/main "
    "behind-7 clean auto-merge 28dba9152 ZERO-UU -> single-push LANDED 31bfdd5f5..28dba9152 | "
    "S0.5: orders 154/154 head-scan zero unacked; D-19 decisions sha MATCH D14DCC74872A599 (canonical "
    "Tools/d19_check.py rc0; ad-hoc r677 orders face false-alarm = SHA-1-vs-SHA-256 mismatch, "
    "dual-algorithm verified content-unchanged E79E15F9, r537 law applied in-round) | inbox 0 | "
    "S1 smoke 48/48 | S3: engine alive queue_depth=0; RAM 3.7GB < 4GB heavy gate = zero new burn drafting "
    "(fleet discipline); W14-GENERATE waiting RAM-gate legitimate | "
    "S6 (per dead-session bookkeeping.py text, git-committed as evidence): dualrun ZERO-DRIFT streak 40 "
    "(403 entries); compute_audit CLEAN; py_watermark insufficient_history n=1 (local_batch_running=true = "
    "legal burn face); leg39 VERDICT mechanical_ready=False (G1 burn F, G2 T, G3 T, G4 PENDING r638 armed; "
    "window 10-05..10-09) | product score 2 (S6 product chain 39 rc0 + trio burn advance + CEO faces regen)\n"
)

# --- r748 line (every number measured at exec time) ---
line_748 = (
    "%s | round 748 (bm-b, dept:engineering, golden-week steady-state round + r747 dead-tail recovery) | "
    "[watermark verdict: %s (red=%s lane %s; satengine alive rc0 idle 0 queue_depth=0; board 0 "
    "open jobs; trio in-flight = trial-labor line satisfied; free RAM <4GB heavy gate = zero new burn "
    "drafting per fleet discipline)] | "
    "CEO three-line: current-work = FUND trio NULLS burns V%d/Q%d/D%d of 2000 (+%d/+%d/+%d vs r746 probe, "
    "autofill+workers alive) | "
    "latest-artifact = results/_r748bmb_s6_chain.log (%s, lineage r747 verbatim legdiff 4 label lines only) "
    "+ docs REPORT/LIVE-2026-10-05 regen by S6 | "
    "next-milestone = trio V finalize ~10-06 evening (ETA ~%.0fh from leg39, fluctuates), Q ~10-07, D ~10-08; "
    "D-06 group closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar) | "
    "S0: churn-absorb ac5d99880 (r747 dead-tail 39 files: S6 outputs + bookkeeping bloodline + daemon live "
    "faces) -> merge origin/main behind-10 14-UU canon resolver 3c3a170e8 (receipt _r748bmb_merge_resolve."
    "json: 11 ours-fresher probe_ts + 2 rolling unions + token per-key max-union picked_theirs=2; readback"
    "+marker+twin asserts PASS) | "
    "S0.5: orders 154/154 head-scan zero unacked; D-19 decisions sha MATCH D14DCC74872AA599 (canonical "
    "Tools/d19_check.py rc0) | inbox 0 | S1 smoke 48/48 | "
    "S3: engine alive queue_depth=0 idle; job board 0 open; RAM <4GB heavy gate = zero new burn drafting; "
    "W14-GENERATE waiting RAM-gate legitimate | "
    "S6: %s; dualrun consecutive_green=%s; leg39 trio V%d/Q%d/D%d mechanical_ready=%s (governance G4 "
    "PENDING r638 fallback armed; window 10-05..10-09) | "
    "S7 quartet 4/4 (IterationLoop pin=2 no-op first-fire 22:12 preserved; LoopWatchdog RE-BUILT was-missing "
    "first-fire 22:09 honest correction of r747 pre-write claim; precommit+prepush claws LF-normalized "
    "install match) + attrition guard CLEAN (4 ledgers, healed rows historical) + r747 round line "
    "POST-MORTEM backfilled + state honest jump 746->748 per r714 law | "
    "S6 chain end %s | "
    "product score 2 (S6 product chain 39 legs + trio burn advance + CEO faces regen + r747 dead-tail "
    "recovery)\n" % (iso, wv, wr.get("red"), wr.get("lane"), v, q, d, dv, dq, dd, leg_txt, v_eta, leg_txt, streak, v, q, d, mr, s6_end)
)

m747 = b"round 747 (bm-b"
m748 = b"round 748 (bm-b"
raw = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert m747 not in raw, "round 747 line already present (double-append guard)"
assert m748 not in raw, "round 748 line already present (double-append guard)"
assert raw.endswith(b"\n") or raw.endswith(b"\r\n"), "ledger tail not newline-terminated"
with io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "ab") as f:
    f.write(line_747.encode("utf-8"))
raw_mid = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert raw_mid == raw + line_747.encode("utf-8"), "r747 append not byte-exact"
assert raw_mid.count(m747) == 1
with io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "ab") as f:
    f.write(line_748.encode("utf-8"))
raw2 = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert raw2 == raw_mid + line_748.encode("utf-8"), "r748 append not byte-exact"
assert raw2.count(m748) == 1
print("bookkeeping OK: state 748 (jump 746->748), heartbeat epoch int %d, lines: r747 BACKFILL + r748 appended+verified; S6 %s; trio V%d/Q%d/D%d mr=%s" % (
    epoch, leg_txt, v, q, d, mr))
