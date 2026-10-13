# -*- coding: utf-8 -*-
# r965 closeout: state round_no/act/watermarks + round-report line + heartbeat
import datetime, hashlib, json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

def group_sha():
    r = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", r"K:\Fluxgroup\FluxGroup",
                        "show", "origin/main:docs/orders.md"], capture_output=True).stdout
    return hashlib.sha256(r).hexdigest()

def dec_sha():
    raw = open("_r957_decisions_head.md", "rb").read()
    return hashlib.sha256(raw).hexdigest()

# ---- state ----
sp = "state-bm-c.json"
s = json.load(open(sp, encoding="utf-8-sig"))
assert s["round_no"] == 964
s["round_no"] = 965
s["activity_now"] = ("2026-10-13 12:2x | r965 | bm-c: W231 PREREG DERIVED+LANDED (fifteen-level replay 46/46 zero false-fails, "
                     "bands A 523_004..525_003 / B 525_004..525_203, sha16 0d01f528, commit aebe0a5ac pushed) "
                     "+ ORD delta TRUE consumed 29c2ba65->c7d3ee65 (MV-lane @bm-c rows, zero BigMoney action, MV window domain) "
                     "+ DEC delta TRUE consumed fb5825cb->f41caf26 (D-20261013-01/02 + C-20261012-01 rows, zero bm-c action) "
                     "| counter 964->965 | W231 five-face freeze splice = next window FIRST ACTION")
s["last_decisions_sha"] = dec_sha()
s["last_orders_sha"] = group_sha()
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state: round 965, dec", s["last_decisions_sha"][:8], "ord", s["last_orders_sha"][:8])

# ---- round report (root face, r958-r963 consecutive-window practice) ----
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
line = (now + " | r965 | bm-c: W231 PREREG DERIVED+LANDED (PRODUCT: research/PERPETUAL_N1_W231_PREREG.md 24,492B-class freeze-time face "
        "sha16 0d01f528a408ee46, commit aebe0a5ac pushed origin-verified 34c17deaf..aebe0a5ac) -- FIFTEEN-level lineage replay "
        "46/46 preflight ZERO false-fails first-run (pairs216+SUB17..SUB30, one deeper than W230 fourteen-level); find sides "
        "machine-generated m28 from committed _w230 SUB new-sides via _w231bmc_subgen.py (zero transcription); authored repls R31 "
        "(_w231bmc_r31_data.py) runtime count-asserted; bands A 523_004..525_003 / B 525_004..525_203 per ADMIT receipt "
        "_w231bmc_20261013 (A staircase NINETY-FIRST hops=1 refused at start by registered W230 B 522_804..523_003 per W230 seat leg4 "
        "projection honored verbatim; B own-A exclusion hops=1 naive 523_004..523_203 inside own-A); S5 anchors machine-read "
        "n1_w230_results ledger 929,789/K=503,920/mu -0.09269286/sigma 0.24504776/w230-only -0.090772/A p95 0.3069/KL -0.0001/"
        "se_mu 0.000345; S5.5 W232+ projection A 525_004..527_003 / B 525_204..525_403 NINETY-SECOND anticipated; STALE x73 zero "
        "NEW x51 present; freeze label r964 2026-10-13 12:1x; tpl advanced via _r964bmc_tplgen.py machine transform (90 replacements "
        "of committed W230 tpl, zero transcription) | pitfall: fmt8 8-decimal precision face (w230-only 0.09077200 vs 6-sig prose "
        "0.090772 -- W229-only was exactly 8-sig so the face never fired before; W232 face risk noted) + tpl string \u2212 escape "
        "literal face (source carries backslash-u2212 text not the glyph) | S0.5 ORD delta TRUE consumed 29c2ba65->c7d3ee65 (10-13 "
        "03:3x-12:2x rows ALL BigStream MV-lane incl @bm-c V3 refire 5-shot order -- MV exec-window/night-GPU domain, this quant "
        "loop does not cross-domain; zero BigMoney action, receipt here) + DEC delta TRUE consumed fb5825cb->f41caf26 "
        "(D-20261013-01 receipt batch 31 + D-20261013-02 C-20261012-01 Phase0 + C-20261012-01 top-level case rows; zero bm-c-action "
        "face, item6 bigmoney E1 re-enable window 00:00-08:00 in-flight night-shift domain) | S1 smoke 49/49 | satengine rc0 ALIVE "
        "(burns_active=[] queue_next=[] verified at derive) | S6: dualrun ZERO-DRIFT streak 51 + audit FLAG pool_starvation/"
        "supply_floor structural (answered by this W231 prereg, splice+burn chain next) + wm py_low_board_clear legal (Tue bars "
        "pending 15:30) + update_daily 0 new rows cutoff 10-12 + market_regime ORANGE (hs300<MA200 + breadth 0.75) + scorecard "
        "6/28/7 cards 88.5s + market_clock CALL-2026-10-12 ORANGE_COOL sleeves=4 + daily_report REPORT-2026-10-13 + ceo_live_usage "
        "LIVE-2026-10-13 (ORANGE cap 50% heat COOL) + token delta=0 + 20 lane-guard collectors honest no-ops (bm-a/bm-b lanes + "
        "fund_premium snapshot-fresh 17.9h + options RETIRED per O-20261009-1105) | attrition 4 CLEAN | S7 quad green (loop pin=5 "
        "no-op first-fire 12:25 + watchdog registered first-fire 12:23 + pre-commit/pre-push claws installed) + round-zero probe "
        "py_faces=5 orphans=2 zero-kill (MV-lane infra: ComfyUI 8188 + album_serve kept) | round-report face note: r913 heal said "
        "canonical=logs/iteration-loop/ but r958-r963 four consecutive windows wrote root face -- this window follows the "
        "consecutive practice (root), face ambiguity left for governance window | counter 964->965 | W231 five-face freeze "
        "splice + engine mtime-watch self-burn = next window FIRST ACTION + Tue 15:30 new-bar papers full chain | 3-line face: "
        "now=W231 prereg derived+landed; recent=research/PERPETUAL_N1_W231_PREREG.md sha16 0d01f528 12:1x; next=W231 splice+burn"
        "+finalize (next window, <48h) + Tue 15:30 papers chain")
with open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write("\n" + line + "\n")
print("round report appended (root practice face)")

# ---- heartbeat ----
hp = "fleet/machines/bm-c.json"
h = json.load(open(hp, encoding="utf-8-sig"))
epoch = int(datetime.datetime.now().timestamp())
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
h["ts"] = h["clock_read"]
h["last_seen"] = h["clock_read"]
h["current_task"] = "W231 prereg landed; splice+burn next window"
h["verdict"] = "green (W231 prereg product landed, engine alive, chain continues)"
h["idle_rounds"] = 0
h["agenda_starved"] = False
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
v = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be int (F7 law)"
assert "T" in v["clock_read"], "clock_read must be T-separated (F7 law)"
print("heartbeat: epoch", epoch, "int-verified")
