# r800 bm-b close script: state 799->800 + ledger row append (r752 tail-newline law)
# + heartbeat (epoch int law R170/R178/R262) + orders_ack 163->164 + self-verify.
# ASCII comments only (PS5.1 ANSI pit law).
import json, time, re, subprocess, datetime, os

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- 1) root state.json (TRUE state per r646 path-split epoch law) ---
SP = "state.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 799, f"state round_no {st['round_no']} != 799 (wrong face?)"
st["round_no"] = 800
st["round_no_label"] = "r800"
st["note"] = ("r800: six-dead-session takeover closeout (07:52/08:22/09:02/09:32/10:02/10:32 all "
    "25min wrapper kills, zero rows/state landed, absorb per r714/r792 law): O-20261007-0935-bm-c.md "
    "bm-b receipt (local compute capability inventory, written by dead 10:32 session 10:5x) absorbed "
    "+ committed + pushed; trio Q heal COMPLETE 2000/2000 (pool dual-flip done 07:18:03 both faces, "
    "r668 law satisfied; heal closed 12-key gap from dead r801 pre-scan); D 1709/2000 burning; "
    "V 2000/2000; smoke 48/48; S6 absorbed 35/35 rc0; attrition CLEAN; quartet 4/4; orders 163->164")
st["did"] = st["note"]
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_seen"] = NOW
st["clock_read"] = NOW
st["last_orders_sha"] = "E9FA5DA4927D557B"
st["last_orders_read_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_sha_note"] = ("r800: orders dir 164 vs ack 163 -> +1 O-20261007-0935-bm-c.md (receipt "
    "absorbed, ack 164); D-19 dual-face: decisions 635C3024 MATCH unchanged zero action; group "
    "orders.md E9FA5DA4 changed vs r798 9BE6A74F -> re-scan zero new BigMoney dispatch rows = "
    "watermark update only")
st["verdict"] = ("green: r800 takeover closeout landed (6 dead sessions absorbed); O-0935 bm-b receipt "
    "delivered ahead of 10-09 deadline; Q 2000/2000 complete (dual-flip verified), D 1709/2000 "
    "in-flight, V 2000/2000; smoke 48/48; attrition CLEAN; orders 164/164; satengine alive rc0 idle")
st["next"] = ("(1) QA pack r800 debt FIRST ACTION next round (time-budget guard this round, honest "
    "debt) + 5x HANDOVER r800 check debt same round; (2) D lane first-to-2000 ~10-08 05:00 @0.27/min "
    "(1709/2000 @11:1x) -> trio finalize G1-G4 window 10-05..10-09 (G2+G3 green, G4 r638 fallback "
    "armed); (3) post-trio-close O-20261006-2358 self-claim <=1h; (4) market reopen 10-08: S6 legs "
    "25-28 resume + REGIME_GUARD v3 first new bar enforce; (5) D-06 group closeout 10-07 12:00 "
    "(bm-c lane)")
st["current_task"] = ("r800 closed; next = QA r800 debt + 5x HANDOVER / D burn watch to 2000 / trio "
    "finalize when Q+D both 2000 / market reopen 10-08")
json.dump(st, open(SP, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- 2) ledger row append (r752 tail-newline probe + line-count assert) ---
LP = "logs/iteration-loop/round_reports.md"
raw = open(LP, "rb").read()
old_lines = sum(1 for ln in raw.split(b"\n") if ln.strip())
ROW = (NOW + " | round 800 (bm-b, dept:engineering, six-dead-session takeover closeout + O-0935 "
    "receipt landing round) | [watermark verdict: GREEN (red=false lane healthy @11:06 daemon face; "
    "satengine alive rc0 idle queue_depth=0; boards 0 open; trio D in-flight burn = trial-labor "
    "line satisfied)] | CEO three-line: current-work = r800 takeover closeout of 6 consecutive "
    "timeout-killed sessions (07:52/08:22/09:02/09:32/10:02/10:32 run logs all 'ROUND TIMEOUT after "
    "25min' wrapper budget kills not hangs, zero rows/state landed, absorb per r714/r792 law) + "
    "FUND trio Q heal COMPLETE 2000/2000 (pool dual-flip done 07:18:03 BOTH faces verified = r668 "
    "same-window law satisfied; heal burn closed 12-key gap found by dead r801 session pre-scan) / "
    "D 1709/2000 burning ~0.27/min ETA ~10-08 05:00 / V 2000/2000 | latest-artifact = "
    "fleet/orders/O-20261007-0935-bm-c.md bm-b receipt (local compute capability inventory table + "
    "TTS mainline + cloud-submission tri-gate ack, written by dead 10:32 session 10:5x, absorbed+"
    "committed+pushed this round, <=10-09 deadline beaten 2 days) + results/_r800bmb_s6_chain.log "
    "(35 legs all rc0 173s absorbed regen) | next-milestone = QA r800 debt + 5x HANDOVER check next "
    "round first actions + D lane 2000/2000 ~10-08 05:00 -> trio finalize (window 10-05..10-09) + "
    "post-trio-close O-20261006-2358 self-claim <=1h + market reopen 10-08 S6 legs 25-28 + "
    "REGIME_GUARD v3 first new bar + D-06 group closeout 10-07 12:00 (bm-c lane) | S0: identity=bm-b "
    "anchored (machine.json first-read; TRUE state = root state.json per r646 path-split epoch law, "
    "logs/iteration-loop/state.json = r350 frozen orphan untouched); dead-session forensics via run "
    "logs + order-file diff (receipt found half-landed in dirty tree); single-executor law honored | "
    "S0.5: orders dir 164 vs ack 163 -> +1 O-20261007-0935-bm-c.md (bm-b leg receipt ack 163->164); "
    "D-19 dual-face: decisions 635C3024 MATCH unchanged zero action + group orders.md E9FA5DA4 "
    "changed vs r798 9BE6A74F -> re-scanned, zero new BigMoney dispatch rows = watermark update "
    "only; inbox scan below | S1: smoke 48/48 rc0 (second-run verify after first output lost to "
    "tool flood) | S3: satengine alive rc0 idle; watermark red=false; trio probe Q 2000/D 1709/V "
    "2000 (nulls.jsonl row counts authoritative; nulls.log counter 1745 counts heal-attempts too); "
    "FUND-DIVLOWVOL-P1-NULLS pool entry stays ready (burn in-flight, autofill keepalive owner=bm-b) "
    "| S6: absorbed dead-session r800 chain 35 legs rc0 173s (run-2 partial legs 01-08 rc0 idempotent "
    "no corruption); golden-week legs 25-28 honest-skip (cutoff 2026-09-30, reopen 10-08) | S7: "
    "quartet 4/4 (IterationLoop pin=2 no-op first-fire 11:22 + LoopWatchdog re-registered first-fire "
    "11:14 + precommit/prepush claws LF-normalized reinstall) + attrition guard CLEAN rc0 (4 "
    "ledgers, healed rows historical, evidence results/_attrition_guard_scan.json) + state 799->800 "
    "+ heartbeat epoch int self-verified + orders_ack 164 | treasure zero-hit claim: zero "
    "sweep/archive/delete actions this round | verification: smoke 48/48 + attrition CLEAN + pool "
    "FUND trio 13 entries dual-face consistent + D-19 decisions MATCH + quartet 4/4 | honest "
    "debts: QA pack r800 NOT produced (time-budget guard after 6 dead sessions, landing closeout "
    "prioritized; next round first action) + 5x HANDOVER r800 check deferred (same) | local "
    "undelivered-to-origin commit count: post-push self-verify below | product score 1 (O-0935 "
    "receipt = CEO-visible order closure actual file deliverable; S6 absorbed regen product chain; "
    "rest bookkeeping within <=5 budget)")
if raw and not raw.endswith(b"\n"):
    open(LP, "ab").write(b"\n")
open(LP, "ab").write(ROW.encode("utf-8") + b"\n")
raw2 = open(LP, "rb").read()
new_lines = sum(1 for ln in raw2.split(b"\n") if ln.strip())
assert new_lines == old_lines + 1, f"ledger line count {old_lines}->{new_lines} not +1"
assert ROW.encode("utf-8") in raw2

# --- 3) heartbeat fleet/machines/bm-b.json ---
HP = "fleet/machines/bm-b.json"
hb = json.load(open(HP, encoding="utf-8"))
assert hb["round_no"] == 799
try:
    import psutil
    free_gb = round(psutil.virtual_memory().available / 1024**3, 2)
except Exception:
    free_gb = hb.get("free_ram_gb", 7.33)
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["free_ram_gb"] = free_gb
hb["round_no"] = 800
hb["round"] = 800
hb["last_round_at"] = NOW
hb["ts"] = NOW
hb["updated"] = NOW
hb["orders_ack"].append("O-20261007-0935-bm-c.md")
hb["orders_ack_count"] = len(hb["orders_ack"])
assert hb["orders_ack_count"] == 164
hb["verdict"] = ("green: r800 takeover closeout landed (6 dead sessions absorbed); O-0935 bm-b "
    "receipt delivered ahead of 10-09; Q 2000/2000 complete (dual-flip 07:18 verified), D 1709/2000, "
    "V 2000/2000; smoke 48/48; attrition CLEAN; orders 164/164; satengine alive rc0 idle")
hb["last_action"] = ("r800: dead-session forensics (6x 25min kills) + O-0935 receipt absorb-commit + "
    "Q heal 2000/2000 dual-flip verify + smoke 48/48 + attrition CLEAN + quartet 4/4 + state 800")
hb["now_active"] = ("FUND trio: Q 2000/2000 COMPLETE (heal closed) / D 1709/2000 burning ~0.27/min "
    "ETA ~10-08 05:00 / V 2000/2000; G1 pending D, G2+G3 green, G4 PENDING r638 fallback armed; "
    "finalize window 10-05..10-09")
hb["latest_artifact"] = ("fleet/orders/O-20261007-0935-bm-c.md bm-b receipt (capability inventory, "
    "CEO order closure) + results/_r800bmb_s6_chain.log (35 legs rc0) @" + NOW)
hb["next_milestone"] = ("QA r800 debt + 5x HANDOVER next round first actions + D 2000/2000 ~10-08 "
    "05:00 -> trio finalize + O-20261006-2358 self-claim <=1h post-close + market reopen 10-08 "
    "(S6 legs 25-28 + REGIME_GUARD v3) - within 48h window")
hb["current_task"] = "r800 closed; see state.next"
hb["task"] = "r800 closed; see state.next"
json.dump(hb, open(HP, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- 4) self-verify (R170/R178/R262 int+T-separator laws) ---
hb2 = json.load(open(HP, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"], "clock_read must use T separator"
st2 = json.load(open(SP, encoding="utf-8"))
assert st2["round_no"] == 800

# --- 5) inbox + group orders 10-06/10-07 dispatch scan (record only) ---
inbox = [f for f in os.listdir("fleet/inbox") if f.lower().endswith(".md")]
print("inbox_unread:", inbox if inbox else "0")
try:
    txt = subprocess.run(["git", "-C", r"C:\Users\Administrator\FluxGroup", "show",
        "origin/main:docs/orders.md"], capture_output=True).stdout.decode("utf-8", "replace")
    rows = [ln[:150] for ln in txt.splitlines()
            if re.match(r"^\|\s*10-0[67]", ln) and re.search(r"BigMoney|bm-b|quant", ln)]
    print("group_orders_new_bigmoney_rows:", rows if rows else "0")
except Exception as ex:
    print("group_orders_scan_error:", ex)

print("CLOSE OK r800 epoch=", EPOCH, "now=", NOW, "free_ram_gb=", free_gb)
