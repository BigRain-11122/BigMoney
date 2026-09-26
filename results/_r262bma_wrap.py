# _r262bma_wrap.py -- R262 S5/S7 wrap: state round_no 261->262, heartbeat final
# write (epoch int + T-separated clock_read = this round's own law), round
# report line append. Every JSON rewrite mirrors producer byte faces probed
# from the live file (R255 five-face law: BOM/EOL/indent/trailing-newline).
import json, time, datetime, os, sys


def probe(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8-sig")
    trailing_nl = text.endswith("\n")
    indent = None
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith('"') and line != s:
            indent = len(line) - len(s)
            break
    return bom, crlf, trailing_nl, indent, raw


def write_mirror(path, obj, bom, crlf, trailing_nl, indent):
    out = json.dumps(obj, ensure_ascii=False, indent=indent)
    if trailing_nl:
        out += "\n"
    if crlf:
        out = out.replace("\n", "\r\n")
    data = out.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as fh:
        fh.write(data)


now = datetime.datetime.now().astimezone()
now_s = now.strftime("%Y-%m-%d %H:%M:%S")

# ---- state-bm-a.json -------------------------------------------------------
P = "state-bm-a.json"
bom, crlf, tnl, ind, _ = probe(P)
st = json.load(open(P, encoding="utf-8-sig"))
st["round_no"] = 262
st["did"] = ("R262 S1 sole-mission red-fix arc: smoke F7 heartbeat clock_read "
             "space-separator RED (R261 S7 writer) -> value fix isoformat() T-sep "
             "+ epoch int self-verified + standing spec pinned in Tools/iteration_prompt.txt "
             "-> smoke re-run 25/25 ALL GREEN; S6 24 legs exit 0 weekend no-ops; "
             "inbox 2 self-addressed msgs processed; board clear legal idle")
st["verdict"] = ("R262: F7 red root-fixed both faces (heartbeat + prompt spec); smoke 25/25; "
                 "R170/R178 family third variant memorized (value+type+format three-face law)")
st["next"] = ("(1) next pool supply = core-leg drawdown-control prereg candidate (R261 doctrine) "
              "+ J-line/PROSPECT/market-clock L4 low-vol/low-turnover sleeve filters from slice-C/D laws; "
              "(2) 09-28 Monday new-bar chain (cutoff 09-24); "
              "(3) 10-01 monthly trio + REGIME_GUARD v3 date gate + 5x HANDOVER at R265; "
              "(4) T-70 C-arm verdict window 10-09")
for k in ("ts", "last_round_ts", "updated_at", "last_round_at", "updated"):
    st[k] = now_s
st["last_round"] = 262
st["current_task"] = "idle (round 262 closed)"
st["last_run"] = now_s
write_mirror(P, st, bom, crlf, tnl, ind)
print("state: round_no=262 faces:", bom, crlf, tnl, ind)

# ---- fleet/machines/bm-a.json (heartbeat) ----------------------------------
P = "fleet/machines/bm-a.json"
bom, crlf, tnl, ind, _ = probe(P)
hb = json.load(open(P, encoding="utf-8-sig"))
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=0.5), 1)
    ram = round(psutil.virtual_memory().available / 1024**3, 1)
except Exception:
    cpu, ram = hb.get("cpu_pct"), hb.get("free_ram_gb")
hb["last_seen"] = now_s
hb["current_task"] = "idle (R262 closed: S1 F7 red-fix green, board clear)"
hb["cpu_pct"] = cpu
hb["free_ram_gb"] = ram
hb["verdict"] = ("GREEN R262: S1 smoke F7 heartbeat clock_read space-separator red root-fixed "
                 "both faces (value isoformat T-sep + epoch int self-verified; standing spec "
                 "pinned in Tools/iteration_prompt.txt with example) -> re-run 25/25 ALL GREEN; "
                 "S6 24 legs exit 0 weekend no-ops (regime ORANGE d2 shadow; clock ORANGE_COOL; "
                 "AH panel 27min spawn-throttle next-round self-heal); board clear legal idle "
                 "(0 open / 0 bandit / pool ready=0, next supply = core-leg dd-control prereg "
                 "+ L4 sleeve filters); orders 82/82 both scans; post T-73 s3 chain complete")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.isoformat(timespec="seconds")
hb["round_no"] = 262
hb["task"] = ("R262 done: F7 red-fix green (value+spec both faces); next supply = core-leg "
              "dd-control prereg candidate + L4 sleeve filters; 09-28 new-bar chain; 10-01 "
              "trio + REGIME_GUARD v3; T-70 verdict 10-09")
write_mirror(P, hb, bom, crlf, tnl, ind)
chk = json.load(open(P, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
print("heartbeat: epoch", chk["heartbeat_epoch_utc"], chk["clock_read"], "| cpu", cpu, "| ram", ram)

# ---- logs/iteration-loop/round_reports-bm-a.md ------------------------------
P = "logs/iteration-loop/round_reports-bm-a.md"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
line = (
    "2026-09-26 18:1x | R262 bm-a | watermark: GREEN (18:00 probe py 0.0-0.3% open=0 bandit=0 "
    "pool ready=0 verdict=py_low_board_clear board-clear legal-idle face; supply honest answer: "
    "post-T-73-s3-chain zero runnable batches, next supply = core-leg dd-control prereg candidate "
    "+ J-line/PROSPECT/market-clock L4 low-vol/low-turnover sleeve filters from slice-C/D laws) | "
    "did: S0 pull-rebase Already up to date 5206d901; S0.5 orders 82/82 BOTH scans zero diff "
    "(dir census == orders_ack) + decisions.md zero new rows (tail D-20260926-01..11 all prior-gated; "
    "D-10 IntradayMarks E2=HQ executor zero-action receipted, D-11 counting law executed R249); "
    "S1 smoke 24/25 RED fleet heartbeat epoch fields F7: R261 S7 writer emitted clock_read "
    "space-separated (2026-09-26 17:53:59+08:00), judge `\"T\" in clock_read` FAIL -> SOLE MISSION "
    "red-fix BOTH faces: value fix results/_r262bma_hb_fix.py (five-face probe bom=F crlf=F indent=1 "
    "trailing_nl=F; isoformat T-sep + epoch int 1790416772; json.loads self-verify) + standing-spec fix "
    "results/_r262bma_prompt_fix.py (Tools/iteration_prompt.txt clock_read now pins ISO 8601 T-separated "
    "+ example 2026-09-26T17:59:32+08:00 + space=F7-red R262; 1 occurrence; byte faces preserved) "
    "-> re-run smoke 25/25 ALL GREEN; S2 job_list empty + board 0 open (28 active all claimed); "
    "S3 = red-fix closed loop per S1 sole-mission law, no new batch fired, pool gap disclosed "
    "above, no fabricated busywork O-1137; S4 memory pit-law line appended (R170/R178 family third "
    "variant value+type+format three-face law) repo CODELY.md 41.6->42.4KB <50KB no recompile; "
    "S6 24 legs ALL exit 0 weekend no-ops (audit CLEAN idle-starvation candidate answered by "
    "board-clear probe; watermark probe; update_daily 0 rows cutoff 09-24; regime ORANGE d2 shadow "
    "hs300<MA200 breadth 0.77; clock CALL-2026-09-24 idempotent ORANGE_COOL sleeves 4 activated 0; "
    "lhb 28min throttle; heat weekend; futures+options+sina cutoff no-op; moneyflow 28.3min rank "
    "throttle self-heal; ths same-day idempotent; AH spawn throttled 27min window next-round "
    "self-heal; fund_premium bm-c lane; fundamental 20.6h fresh; blf gates all_pass; aggr+grid "
    "marks-at-cutoff no-op; alloc bm-b lane; t35_export 6 traders 18 positions first-snapshot; "
    "scorecard 6; daily_report faces=4 token=1; build_status; token_meter delta=0 L2 1 leg 6135 tok "
    "local) + no-new-bar Saturday -> live.paper/t35_open_fill/t24 x2 conditional legs legally "
    "skipped; S7 schtasks R49 law IterationLoop Running + Watchdog Ready; inbox 2 self-addressed "
    "msgs processed->processed/ (MSG-1745 T-73 s3 slice-5 claim = arc closed same-round R261 judged "
    "negative family complete; MSG-174x T-82 deep-bcd receipt = closed R260 4/4 family cross-check); "
    "state 261->262 + heartbeat epoch int + T-sep clock_read self-verified | evidence: smoke 25/25 "
    "output + results/_r262bma_hb_fix.py SELFTEST PASS + results/_r262bma_prompt_fix.py replaced OK "
    "len_delta=67 + S6 exit codes 24x0 in transcript + git rename pairs staged both sides | next: "
    "(1) core-leg drawdown-control prereg candidate (R261 doctrine: dd-control sits on CORE leg; "
    "no verdict, future prereg) + L4 sleeve filters; (2) 09-28 Monday new-bar chain (cutoff 09-24); "
    "(3) 10-01 monthly trio + REGIME_GUARD v3 date gate + 5x HANDOVER at R265; (4) T-70 C-arm "
    "verdict window 10-09"
)
if not raw.endswith(b"\n"):
    raw += b"\r\n" if crlf else b"\n"
data = raw + line.encode("utf-8") + (b"\r\n" if crlf else b"\n")
with open(P, "wb") as fh:
    fh.write(data)
print("round report appended; crlf=", crlf)
print("WRAP SELFTEST PASS")
