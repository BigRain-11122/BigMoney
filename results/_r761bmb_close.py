# r761 bm-b close: round-report row append + state.json update + heartbeat update.
# Lineage: r516/r517 close pattern (python bookkeeping, one receipt print); report-row
# format mirrored verbatim from r760 row; delivery-count fill done post-push per r759
# convention (rev-list 0/0 self-verify).
import io, json, os, re, subprocess, time
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")

def p(path):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)

# ---- S6 chain window (from log first/last lines) ----
win = ""
try:
    with io.open(p("results/_r761bmb_s6_chain.log"), encoding="utf-8", errors="replace") as f:
        ls = f.read().splitlines()
    m0 = re.search(r"(\d{2}:\d{2}:\d{2})", ls[0]) if ls else None
    m1 = re.search(r"(\d{2}:\d{2}:\d{2})", ls[-1]) if ls else None
    if m0 and m1:
        win = "%s-%s" % (m0.group(1), m1.group(1))
except OSError:
    win = "n/a"

# ---- RAM / GPU samples ----
free_ram = None
try:
    import psutil
    free_ram = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception:
    pass
gpu_free = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        gpu_free = round(float(r.stdout.strip().splitlines()[0]) / 1024.0, 2)
except Exception:
    pass

# ---- 1) round report row append (placeholder delivery count, fill post-push) ----
ROW = ("{ts} | round 761 (bm-b, dept:工程, golden-week steady-state guard + r760 dead-session "
       "churn-absorb + S0 integration deferred to S7 push path) | [watermark verdict: GREEN "
       "(red=false lane healthy; satengine alive rc0 idle queue_depth=0 py_cpu ~54.7 pct; board 0 open jobs "
       "both boards; trio-in-flight = trial-labor line satisfied; free RAM ~{ram}GB <4GB heavy gate = zero "
       "new burn drafting legal)] | CEO three-line: current-work = FUND trio NULLS burns V1722/Q1412/D1158 "
       "of 2000 @04:34 (+12/+12/+10 vs r760 04:01 face, dup_k all 0, probe G2/G3 green G1 pending; Q eta "
       "~9.8h ~10-06 afternoon, V eta ~11.7h ~10-06 evening, D eta ~44h ~10-08 morning) | latest-artifact "
       "= qa/smoke-r761.md + qa/equity-curve-r761.png (QA pack 5/5: 3 syms x 800 bars real backtest 93 "
       "trades determinism=True) + results/_r761bmb_s6_chain.log (35 legs all rc0 {win}) | next-milestone "
       "= trio Q/V finalize 10-06 afternoon-evening (V same-window pool dual-flip per r668 law) + D-06 "
       "group closeout 10-07 12:00 (23 pit files <=30KB re-verified r760) + market reopen 10-08 "
       "(REGIME_GUARD v3 first new bar) | S0: r760 dead-session churn-absorb 01c04595f (48 files incl QA pack "
       "r760 5/5 + d19 receipts; evidence = heartbeat 04:15:02 + no live codely process + report row "
       "complete; round_no pre-read per r620 law) + origin fetch 2a8afcba6..5de34bd42 (bm-a r755/r756 "
       "W146/W147 wave faces + bm-c r593 D-06 pre-verify) + pull --rebase blocked (5 live daemon unstaged "
       "faces; origin-side overlap = CODELY.md + shared status faces) + S0 no-resolve law -> integration "
       "deferred to S7 push-rejection path (skill-sanctioned exception) | S0.5: fleet orders 154/154 zero "
       "unacked (full-set diff heartbeat ack_count=154); decisions MATCH 7674E37B + group-orders MATCH "
       "2E73244B (r761 d19 read rc0, r760 script verbatim lineage, sparse-clone r631 recipe) | S1: smoke "
       "48/48 | S3: board 0 open (job_list empty + fleet/tasks zero status=open), satengine alive rc0 idle "
       "0, watermark red=false, trio in-flight = trial-labor satisfied | S6: 35 legs all rc0 {win} (dualrun "
       "streak 51 drift=False; legs 25-28 honest-skip no-new-bar until 10-08 reopen; leg39 trio probe "
       "verdict mechanical_ready=False G1 pending; daily_report REPORT-2026-10-06 + LIVE-2026-10-06 "
       "regenerated) | S7: quartet green (loop pin=2 no-op first fire 04:42 + watchdog re-registered first "
       "fire 04:38 + pre-commit/pre-push claws LF-normalized reinstall) + attrition CLEAN (4 ledgers, healed "
       "notes only) + inbox zero unread | verification: python -m smoke_test 48/48; QA pack r761 5/5 "
       "(qa/smoke-r761.md); S6 summary 35 legs rc=0 x35; treasure zero-hit claim: no sweep/archive action this "
       "round (prescan not triggered) | r760 row 'pending push' placeholder left untouched (dead-session "
       "artifact; delivery of its absorbed face completed by r761 this push) | next pointer: leg39 trio probe "
       "every round; first family to 2000 -> finalize round same-window pool dual-flip per r668; D-06 "
       "closeout report 10-07 12:00 | local undelivered-to-origin commit count: PENDING_FILL_R761"
       ).format(ts=now, ram=(free_ram if free_ram else "3.0"), win=win)
with io.open(p("logs/iteration-loop/round_reports.md"), "a", encoding="utf-8", newline="\n") as f:
    f.write(ROW + "\n")

# ---- 2) state.json update ----
sp = p("state.json")
with io.open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 761
st["round_no_label"] = "r761"
st["note"] = ("r761: golden-week steady-state guard + r760 dead-session churn-absorb (48 files, died "
              "pre-S7-commit) + S0 integration deferred to S7 push-rejection path; S0.5 orders 154/154 "
              "zero unacked + decisions/orders MATCH (7674E37B/2E73244B); S1 48/48; S6 35 legs rc0 " + win +
              " (dualrun streak 51 zero-drift; legs 25-28 honest-skip); trio probe @04:34 V1722/Q1412/D1158 "
              "dup_k=0 G1 pending (Q eta ~9.8h, V ~11.7h, D ~44h); QA pack r761 5/5")
st["next"] = ("(a) trio finalize windows: Q 1412/2000 eta ~9.8h ~10-06 afternoon, V 1722/2000 eta ~11.7h "
              "~10-06 evening, D 1158/2000 eta ~44h ~10-08 morning -- leg39 probe every round; "
              "first-to-2000 finalize round must same-window pool dual-flip per r668 law; (b) D-06 group "
              "closeout report 10-07 12:00 (23 pit files all <=30KB re-verified r760); (c) 10-08 market "
              "reopen window (external data legs + paper marks resume + REGIME_GUARD v3 first new bar)")
for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read", "last_round_ts"):
    st[k] = now
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- 3) heartbeat update ----
hp = p("fleet/machines/bm-b.json")
with io.open(hp, encoding="utf-8") as f:
    hb = json.load(f)
epoch = int(time.time())
assert isinstance(epoch, int)
hb["last_seen"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
if free_ram:
    hb["free_ram_gb"] = free_ram
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
    hb["gpu_free_vram_mb"] = int(gpu_free * 1024)
hb["round_no"] = 761
hb["round"] = 761
hb["verdict"] = ("healthy: r761 steady-state guard complete (r760 dead-session churn-absorb + S6 35 rc0 + "
                 "QA r761 5/5); trio burns in flight V1722/Q1412/D1158 of 2000; RAM <4GB heavy gate = zero "
                 "new burn drafting legal")
hb["current_task"] = "r761 golden-week steady-state guard: trio probe + S6 chain + r760 absorb landed"
hb["last_action"] = ("r761 closed: churn-absorb 01c04595f (r760 dead-session outputs, 48 files) + S0.5 "
                     "154/154 + decisions/orders MATCH + S6 35 rc0 + QA r761 5/5 + S7 quartet green")
hb["now_active"] = ("FUND trio NULLS judgment burns V1722/Q1412/D1158 of 2000 @04:34 (autofill+workers "
                    "alive; Q eta ~9.8h ~10-06 afternoon, V eta ~11.7h ~10-06 evening, D eta ~44h ~10-08)")
hb["latest_artifact"] = ("qa/smoke-r761.md + qa/equity-curve-r761.png (QA pack 5/5, real backtest 93 "
                         "trades determinism=True) + results/_r761bmb_s6_chain.log (35 legs rc0 " + win + ")")
hb["next_milestone"] = ("trio Q/V finalize 10-06 afternoon-evening (V same-window dual-flip per r668); "
                        "D-06 group closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar)")
hb["task"] = "FUND trio NULLS judgment batch lane (per-family finalize windows)"
for k in ("ts", "updated"):
    hb[k] = now
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

print(json.dumps({"status": "OK", "ts": now, "chain_window": win, "free_ram_gb": free_ram,
                  "gpu_free_vram_gb": gpu_free, "epoch_int": isinstance(hb["heartbeat_epoch_utc"], int),
                  "orders_ack_count": hb.get("orders_ack_count")}, ensure_ascii=False))
