# r328 bm-a closeout: round report + state + heartbeat + inbox scan
import io, json, time, datetime as dt

ts = dt.datetime.now().isoformat(timespec="seconds")
epoch = int(time.time())
clock = dt.datetime.now().astimezone().isoformat(timespec="seconds")

REPORT = ("2026-09-27T14:4x+08:00 | R328 bm-a (dept:research+data+engineering) | "
"WM first-line verdict: GREEN (red=false lane healthy @14:37; py low legal-occupied: sina_mf A1 repull "
"PID 47148 alive CPU advancing 184->201s terminal ETA ~15:0x carryover; compute_audit CLEAN flags=[] "
"load_state=pool-supply-gap 1-ready=W2-A lane_owner bm-b; audit py 0.8% 32-core) | "
"S0 stash-pop UU autofill_state resolved by canon recipe (classifier= mixed-dict+ledger; launches 44=44 "
"identity-merged zero-divergence; last_tick probe bug fixed: string-ts missed by int/float probe -> STASH "
"14:10:02 newer than HEAD 14:00:02 taken whole-dict r140 tie-law n/a; CRLF byte-faithful; stash dropped; "
"resolver=results/_r328bma_resolve.py) | S0.5 orders 96/96 double-scan ZERO unacked both scans; "
"decisions origin fetch+show r82 law: D-08/D-10 non-BigMoney-domain zero-action, D-09 receipted r327 "
"(both-fixes on-tree), C-20260927-01 seat-3 opinion issued r326 F-20260927-02; council window to 09-29 "
"12:00 no action | S1 smoke 25/25 PASS | S2 board 0 open, all claimed no collisions; post_review derive "
"YES=44 NO=0 WAIT=5 zero-P0 (12:11 T-90 ring_table NO-row re-derived YES 12:13 by canon runner; 8 open "
"claim rows consumed) | S3 CLOSURE DELIVERED: T-88 s3 repo term-ladder rate collector LANDED -- "
"scripts/update_repo.py (11 terms SH GC001/003/004/007/014/028/091/182 + SZ R-001/R-003/R-007; "
"dual-face arbitration live-fire: newfqkline primary per-year windows complete+deep-history (GC091 "
"2006-11-01, GC001 2011-05-13, SZ 2012-12-10) BUT transposition-glitch rows; fqkline repair face "
"self-consistent but -25 crash-summer-2015 days and -1.3y history; akshare stock_zh_a_hist_tx REJECTED "
"as no-repair-leg same bloodline -- M0923 cache inherited 2.850 glitch = same-blood not evidence; "
"live arbitration: GC001 2021-08-10 vendor close 2.850>high 2.750 vs true 2.085 proven by sibling "
"curve GC003 2.115/GC007 2.23/R-003 1.89/R-007 2.06 same-day + fqkline concur; both glitch rows "
"guard-caught + repaired via fqkline face, zero quarantined) + data/repo_daily/ 39,360 rows 11/11 "
"landed (zero weekend rows, all closes>0, rate-band (0,200) evidence-locked after (0,50) falsified by "
"GENUINE 2015-02-10 pre-CNY squeeze GC001 close 53.44/high 65.00 cross-verified both faces+siblings; "
"near-zero floor prints 0.005-0.1% stable across two-era vendor pulls kept honest) + spec "
"research/shortline/REPO_PANEL.md v1.1 + selftest 10/10 + S6 chain registered (iteration_prompt after "
"update_futures) + DOMAIN_AUDIT row-4 flipped to built + T-88 progress_r328_bma + idempotent rerun +0 "
"verified + S6 chain production no-op gate verified (cutoff 09-24 covers -> zero network exit 0) | "
"S4 memory: tencent dual-endpoint non-cross-validating pitlaw appended CODELY.md (9920B under 10240 "
"line, watch next append) | S6 32/32 rc=0 (repo gate live no-op verified; ah spawned detached "
"first-refresh legal; moneyflow spawned detached rank pass; astock/revosc/fund_premium lane-guards "
"honest no-op; no new bars -> paper chains data-gated out; token delta=15; L2 2 legs) | "
"S7 burn-watch honest: W2-A entry (entered 13:42:50, lane_owner=bm-b) still ready/unburned ~1h; "
"bm-b heartbeat 33.1min stale BUT task-note = deliberate wait on MY sina panel complete+N>=250 gate "
"(dependency wait not stall-dead) -> no unilateral takeover this round; NEXT-ROUND DECISION POINT: if "
"bm-b stale >20min persists AND W2-A unburned at r329 AND sina_mf repull terminal -> health-machine "
"takeover per >20min law (probe subcommand first per entry data_gates note, 4 workers BelowNormal, "
"12GB RAM prep guard, 15-40min prep + 3-6h burn est, checkpoint cross-kill safe) | "
"D-09 receipt line: D-20260927-09 both-fixes on-tree verified r327 (ts-probe deep-scan + memory-union "
"suffix-concat in SKILL.md L34 face) receipt stands, 48h window tracking | "
"next: (1) sina_mf repull terminal three-piece ~15:0x + moneyflow-IC gate open check; (2) W2-A "
"takeover decision point; (3) Mon 09-28 09:15 T-91 s3 auto-fire; (4) 10-01 month trio; (5) R330 5x "
"HANDOVER; (6) CODELY.md near 10KB line - next append likely triggers in-window archival")

# --- append round report line ---
p = "logs/iteration-loop/round_reports-bm-a.md"
b = open(p, "rb").read()
t = b.decode("utf-8")
crlf = "\r\n" in t
t2 = t if t.endswith("\n") else t + "\n"
t2 += REPORT + ("\r\n" if crlf else "\n")
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(t2)
print("round report appended, CRLF=%s" % crlf)

# --- state file ---
sp = "state-bm-a.json"
d = {
    "round_no": 328,
    "did": ("R328: T-88 s3 repo term-ladder collector LANDED (11 terms, 39,360 rows, dual-face "
            "arbitration 2-repaired/0-quarantined, band (0,200) evidence-locked; S6+iteration_prompt "
            "registered; DOMAIN_AUDIT row-4 built) + S0 stash-pop autofill_state canon-resolved "
            "(44-launches identity-union; last_tick string-ts probe fix) + orders 96/96 double-scan "
            "clean + smoke 25/25 + post_review derive 44 YES zero P0 + S6 32/32 rc=0"),
    "verdict": ("green: audit CLEAN flags=[]; py low legal-occupied (sina_mf repull in-flight "
                "terminal ~15:0x); pool 77 done + 1 ready W2-A lane_owner=bm-b unburned 1h "
                "(bm-b 33min stale = deliberate wait on sina panel, decision point r329); "
                "board 0 open; orders 96/96 double-scan zero-unacked"),
    "next": ("R329+: (1) sina_mf repull terminal three-piece ~15:0x + moneyflow-IC gate; "
             "(2) W2-A takeover decision point (>20min stale + unburned + repull terminal -> "
             "bm-a takeover probe+burn); (3) Mon 09-28 09:15 T-91 s3 auto-fire; (4) 10-01 month "
             "trio; (5) R330 5x HANDOVER; (6) CODELY.md 9920B near 10KB line watch"),
    "ts": ts, "last_round_ts": ts, "updated_at": ts, "last_seen": ts,
    "current_task": ("R328 done: T-88 s3 repo collector landed; R329: sina_mf terminal + W2-A "
                     "takeover decision + T-91 s3 auto-fire Mon"),
}
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
json.load(io.open(sp, encoding="utf-8"))
print("state written, round_no=328")

# --- heartbeat ---
hp = "fleet/machines/bm-a.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = ts
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = clock
h["current_task"] = d["current_task"]
h["verdict"] = d["verdict"]
h["cpu_cores"] = 32
import psutil  # noqa: F401 -- best-effort; fall back silently
try:
    import psutil
    h["idle_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    pass
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")
back = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in back["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat written; epoch int OK; clock:", back["clock_read"])
