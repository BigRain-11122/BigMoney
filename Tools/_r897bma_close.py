# -*- coding: utf-8 -*-
# r897 bm-a close: state bump + heartbeat + round report append + DEC/ORD canonical watermarks
import json, time, datetime, subprocess, hashlib, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
KT = r"K:\Fluxgroup\FluxGroup"
if not os.path.exists(KT):
    KT = r"C:\Users\sjs20\Desktop\FluxGroup"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def git_show(path):
    p = subprocess.run([GIT, "-C", KT, "show", "origin/main:" + path],
                       capture_output=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError("git show failed for %s: %s" % (path, p.stderr[-200:]))
    return p.stdout

def sha(b):
    return hashlib.sha256(b).hexdigest()

dec_sha = sha(git_show("docs/decisions.md"))
ord_sha = sha(git_show("docs/orders.md"))
print("DEC canonical:", dec_sha)
print("ORD canonical:", ord_sha)

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

DID = ("r897: D-20261009-02 QA per-machine-suffix law bm-a LIVING FIRST-PROOF "
       "(qa/smoke-r897-bm-a.md 5/5 + qa/equity-curve-r897-bm-a.png 64150B + log; 91 trades "
       "determinism=True; runner=shared-source fix pulled in from bm-c r785) + "
       "D-20261009-01-03 pool-replenish dispatch consumed = bm-c in-progress lane "
       "(F-20261009-01 trial-labor W17+ from r786, window 10-10 00:00; bm-a yields anti-dup; "
       "takeover watch) + S6 39-leg green (r897 driver, panel 10-08 no new bar pre-market)")

VERIFY = ("smoke 49/49 + QA pack 5/5 new-naming + S6 39-leg bad NONE (panel 10-08) + attrition "
          "CLEAN (4 ledgers, 5 stale rows healed) + orphan face=0 (18 py faces) + engine ALIVE "
          "idle queue 0 + S7 quartet green (loop pin=8 / watchdog / pre-commit+pre-push claws) "
          "+ orders unacked=0 double-scan + DEC consumed fresh (2 BigMoney dispatch rows "
          "read+adjudicated in-round)")

NEXT = ("W192 bm-c landing watch -> W193 seat chain next bm-a window; pool replenish stall-watch "
        "(bm-c in-progress; healthy-machine takeover if no progress by mid-window); 10-09 bars "
        "land 15:30 today -> evening rounds pick up marks")

CURTASK = ("W192 five-face = bm-c seat in-flight (bm-a yields); W193 chain waits W192 landing; "
           "pool replenish = bm-c lane F-20261009-01 (window 10-10 00:00)")

ART = ("r897 products: qa/smoke-r897-bm-a.md 5/5 + qa/equity-curve-r897-bm-a.png 64150B "
       "(D-20261009-02 per-machine suffix law bm-a living first-proof; 91 trades "
       "determinism=True)")

# ---- state-bm-a.json (fresh read -> targeted update) ----
ST = 'state-bm-a.json'
with open(ST, encoding='utf-8') as fh:
    st = json.load(fh)
st['round_no'] = 897
st['round'] = 897
st['loop_round'] = 897
st['last_round'] = 897
st['last_round_at'] = now
st['last_round_closed'] = now
st['last_round_ts'] = now
st['last_run'] = now
st['last_seen'] = now
st['ts'] = now
st['updated'] = now
st['did'] = DID
st['verify'] = VERIFY
st['next'] = NEXT
st['current_task'] = CURTASK
st['task'] = CURTASK
st['now_active'] = "r897 closed: QA naming first-proof + S6 green; N1 line waits bm-c W192"
st['current'] = "r897 closed: QA naming first-proof + S6 green; N1 line waits bm-c W192"
st['last_action'] = "r897 closeout: QA pack + S6 chain + decision consumption + commit/push"
st['last_artifact'] = ART
st['latest_artifact'] = ART
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['last_decisions_sha'] = dec_sha
st['last_decisions_at'] = now
st['last_decisions_seen'] = ("r897: DEC fresh " + dec_sha[:8] + " (changed from 83813196 "
                             "python-canonical); D-20261009-01-03 + D-20261009-02 consumed "
                             "(01-03 = bm-c in-progress yield; 02 = bm-a living first-proof)")
st['last_orders_sha'] = ord_sha
st['last_orders_at'] = now
st['last_orders_seen'] = ("r897: ORD fresh " + ord_sha[:8] + " canonical re-hash; CEO physical-items "
                          "section re-read; zero new BigMoney rows; unacked=0 double-scan")
with open(ST, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(st, fh, ensure_ascii=False, indent=2)

# ---- heartbeat (fresh read -> targeted update per r840 minimal pattern) ----
HB = 'fleet/machines/bm-a.json'
with open(HB, encoding='utf-8') as fh:
    hb = json.load(fh)
hb['round_no'] = 897
hb['round'] = 897
hb['loop_round'] = 897
hb['last_round'] = 897
hb['last_seen'] = now
hb['clock_read'] = now
hb['ts'] = now
hb['last_run'] = now
hb['heartbeat_epoch_utc'] = epoch
hb['last_heartbeat_epoch_utc'] = epoch
hb['verdict'] = 'green'
hb['health'] = 'ok'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['orphan_faces'] = 0
hb['current'] = st['now_active']
hb['current_task'] = CURTASK
hb['task'] = CURTASK
hb['last_action'] = st['last_action']
hb['last_artifact'] = ART
hb['latest_artifact'] = ART
hb['next_milestone'] = ("W192 bm-c landing -> W193 seat chain next bm-a window; pool replenish "
                        "bm-c lane window 10-10 00:00; 10-09 bars land 15:30 today")
hb['last_decisions_sha'] = dec_sha
hb['last_decisions_at'] = now
hb['last_orders_sha'] = ord_sha
hb['last_orders_at'] = now
hb['notes'] = ("10-08 market reopen done (panel 10-08); sina late-bar watch; W192 burn on bm-c "
               "engine; holiday fullburn window code-face ended 10-09 00:00 per O-1858; "
               "pool replenish dispatch = bm-c in-progress F-20261009-01")
with open(HB, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=2)

# ---- round report append (canonical ROOT file, UTF-8, CRLF tail per r843/r846 law) ----
RR = 'round_reports-bm-a.md'
rr_line = (
    now + " | r897 | bm-a | dept:research/engineering (QA naming first-proof + S6 maintenance; "
    "pool replenish = bm-c in-progress lane) | WM-VERDICT: green (red=false next_pick=claimed "
    "moneyflow-IC; engine ALIVE idle queue 0; pool ready=0 = replenish dispatch in-flight bm-c "
    "lane F-20261009-01) | did: D-20261009-01-3 pool-replenish dispatch consumed = bm-c 承接在案 "
    "(F-20261009-01 trial-labor line from r786, window 10-10 00:00) -> bm-a yields anti-dup + "
    "takeover watch; D-20261009-02 QA per-machine suffix law bm-a 活体首证 = qa/smoke-r897-bm-a.md "
    "5/5 + qa/equity-curve-r897-bm-a.png 64150B (91 trades determinism=True; new naming family "
    "live-verified on bm-a; runner = shared-source pull-in) + S6 39-leg full green (r897 driver, "
    "panel 10-08 no new bar pre-market) + idle GREEN-IDLE -> --worked cleared (real product) | "
    "verify: smoke 49/49 + QA 5/5 + S6 bad NONE + attrition CLEAN + orphan face=0 (18 py) + "
    "engine ALIVE + S7 quartet green + orders unacked=0 double-scan (DEC " + dec_sha[:8] +
    " consumed 2 dispatch rows / ORD " + ord_sha[:8] + " canonical) | next: W192 bm-c landing "
    "watch -> W193 seat chain; pool replenish stall-watch; 10-09 bars 15:30 -> evening marks | "
    "orphan_face=0 | unacked_orders=0 | local_vs_origin=pre-push\r\n")
with open(RR, 'ab') as fh:
    fh.write(rr_line.encode('utf-8'))

# ---- self-checks ----
chk = json.load(open(HB, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int (R170/R178 law)'
assert 'T' in chk['clock_read'], 'clock_read not T-separated (R262 law)'
assert chk['clock_read'] == chk['ts'], 'ts/clock_read same-source law'
assert chk['idle_rounds'] == 0
sc = json.load(open(ST, encoding='utf-8'))
assert sc['round_no'] == 897
raw = open(RR, 'rb').read()
assert raw.endswith(b'\r\n'), 'round report must end CRLF'
assert rr_line.encode('utf-8') in raw, 'rr line not appended verbatim'
print('close ok: round 897, epoch', chk['heartbeat_epoch_utc'], 'DEC', dec_sha[:8], 'ORD', ord_sha[:8])
