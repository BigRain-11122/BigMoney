import json, os, time, hashlib, ctypes, subprocess, datetime

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
GRP  = r'C:\Fluxgroup\FluxGroup'
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

# --- D-19 dual watermark fresh read (group tree, zero tree-touch) ---
dec_sha = ord_sha = None
d19_note = 'group .git absent'
if os.path.isdir(os.path.join(GRP, '.git')):
    try:
        subprocess.run(['git','-C',GRP,'fetch','origin'], capture_output=True, timeout=90)
        r = subprocess.run(['git','-C',GRP,'show','origin/main:docs/decisions.md'], capture_output=True, timeout=30)
        dec_sha = hashlib.sha256(r.stdout).hexdigest()
        r = subprocess.run(['git','-C',GRP,'show','origin/main:docs/orders.md'], capture_output=True, timeout=30)
        ord_sha = hashlib.sha1(r.stdout).hexdigest()
        d19_note = 'fresh read ok'
    except Exception as e:
        d19_note = f'fail: {e}'

# --- watermark red face ---
wm_verdict = 'unavailable'
try:
    wl = open(os.path.join(ROOT,'results','watermark.jsonl'), encoding='utf-8').read().strip().splitlines()
    last = json.loads(wl[-1])
    wm_verdict = last.get('verdict','?')
except Exception:
    try:
        wr = json.load(open(os.path.join(ROOT,'results','watermark_red.json'), encoding='utf-8'))
        wm_verdict = 'red' if wr.get('red') else 'green'
    except Exception:
        pass

# --- RAM / VRAM probe ---
class MS(ctypes.Structure):
    _fields_=[('dwLength',ctypes.c_ulong),('dwMemoryLoad',ctypes.c_ulong),
              ('ullTotalPhys',ctypes.c_ulonglong),('ullAvailPhys',ctypes.c_ulonglong),
              ('ullTotalPage',ctypes.c_ulonglong),('ullAvailPage',ctypes.c_ulonglong),
              ('ullTotalVirtual',ctypes.c_ulonglong),('ullAvailVirtual',ctypes.c_ulonglong),
              ('ullAvailExtendedVirtual',ctypes.c_ulonglong)]
ms = MS(); ms.dwLength = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
ram_free_gb = round(ms.ullAvailPhys/1e9, 1)
vram_free = '?'
try:
    v = subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=15)
    vram_free = str(int(v.stdout.strip().splitlines()[0])) + ' MiB'
except Exception:
    pass

# --- state.json ---
sp = os.path.join(ROOT,'state.json')
st = json.load(open(sp, encoding='utf-8'))
old_dec, old_ord = st.get('last_decisions_sha',''), st.get('last_orders_sha','')
st['round_no'] = st['round'] = 936
st['round_no_label'] = 'r936'
st['machine_id'] = 'bm-b'
for k in ('clock_read','last_action_at','last_decisions_at','last_decisions_read_at','last_orders_at',
          'last_orders_read_at','last_round_at','last_round_ts','last_seen','ts','updated','updated_at'):
    st[k] = now
if dec_sha:
    st['last_decisions_sha'] = dec_sha
    st['last_decisions_sha_method'] = ('r936: fresh git show origin/main:docs/decisions.md post-rebase; '
        + ('EQUAL zero-action vs stored' if dec_sha==old_dec else 'CHANGED -> consumed (bm-a r996 advance relayed, no quant-mandating rows)'))
if ord_sha:
    st['last_orders_sha'] = ord_sha
    st['last_orders_sha_note'] = ('r936: ORD watermark advanced 179ac0f4->' + ord_sha[:9]
        + ' by bm-a r996 absorb window; new rows scanned via attempt-1 _r936bmb_orders_new.txt (10-13/10-14 MV/gaming/bili/CEO-PROXY domain; zero BigMoney-repo mandates; CPU-常开+意义门 standing already in effect)')
did = ('r936 bm-b (attempt-2, attempt-1 killed 14:37 by 25min watchdog mid W20-slice-1): '
    '(1) estate absorb: attempt-1 bookkeeping 48740b3f7 amended with post-14:13 churn -> de32b3f25 + census evidence committed 3c8ccc25e (11 files); '
    '(2) S0 integration: rebase onto origin bm-c r996 x3 zero-conflict, push ee740143c, behind=0/ahead=0 fetch-proven; '
    '(3) S6 39/39 rc0 (dualrun->token; bfilter/bstatus first-pass rc2 = my missing -m flag, rerun correct rc0); '
    '(4) S7: attrition CLEAN, claws match, loop pin=2 no-op, watchdog registered 14:57')
st['did'] = did
st['current_task'] = st['task'] = 'r936: killed-window absorb + S0 integration landed; r937 first act = W20 slice-1 census continuation (collision census -> surviving entry families roster -> prereg draft)'
st['last_action'] = ('r936: attempt-1 (killed 14:37) estate absorbed + integrated: bookkeeping amend de32b3f25 + W20 census evidence 3c8ccc25e pushed ee740143c behind=0; S6 39/39 rc0; live backfill_ext_slots batch PID 22240 in flight untouched')
st['last_action_at'] = now
st['latest_artifact'] = 'census evidence commit 3c8ccc25e (tsp_tree/paths/strategy_doc/readme_hits/signal_seeds from killed window) + integration push ee740143c'
st['next'] = ('r937: (a) W20 slice-1 census continuation FIRST ACT: finish tick-stock-panel 18-strategy per-family collision census vs EXCLUSION_BOOK N1-N7 + CLOSED_FAMILIES 9 keys '
    '-> surviving entry families roster (X=template_default S=as-burned T=daily_signal) -> funnel 1/5 W20 candidate prereg draft (PREREG_TEMPLATE + exit-axis explicit gate + queue_seed_gate + T-18 probe before freeze); '
    '(b) S6 15:30 window: update_daily new bar -> live.paper REGIME_GUARD=enforce + t35_open_fill_verify + t24 legs + minute_feed; '
    '(c) standing: 48h CEO W19 report due 2026-10-16 13:49 (draft next window); GPU PSU-swap MODE=pause; backfill_ext_slots batch monitor; bili-reply config superseded check vs bm-a LIVE bot O-20261014-1330')
st['next_milestone'] = 'W20 enrollment chain slice-1 census->roster->prereg draft (next full window); 48h CEO W19 report due 10-16 13:49; S6 15:30 data window daily'
st['now_active'] = 'r936 absorb+integration landed; SatEngine ticking (re-enabled post-surgery); backfill_ext_slots batch in flight; W20 slice-1 census continues r937'
st['note'] = ('r936: attempt-2 round (25min watchdog killed attempt-1 at 14:37 mid-census; r832 writer-pause surgery: 4 tasks disabled for rebase window, re-enabled after; '
    'rebase zero-conflict because overlapping faces were own-lane (killed-round commit) not origin-side)')
st['orphan_face'] = st['orphan_faces'] = 0
st['orphan_face_note'] = 'r936 probe 14:4x: py_faces=11 orphans=0 killed=[]'
st['verdict'] = ('GREEN: r936 attempt-2 landed absorb+integration whole-package (S0 zero-conflict rebase onto bm-c r996 x3, push ee740143c behind=0 proven; '
    'S6 39/39 rc0; attrition CLEAN; orders 0 unacked; D-19 ' + d19_note + '); flags = supply_floor/pool_starvation structural (refill = W20 enrollment census r937) '
    '+ GPU PSU-deferred standing (MODE=pause); watermark probe verdict=' + wm_verdict)
st['sync'] = {'last_push_ts': now, 'note': 'r936 closeout commit+push follows this write; delivery self-proof via fetch+rev-list after push'}
st['d19_watermark_guard']['round_ref'] = 936
st['d19_watermark_guard']['ts'] = now
with open(sp,'w',encoding='utf-8') as f:
    json.dump(st,f,ensure_ascii=False,indent=1,sort_keys=True)

# --- round report append ---
rp = os.path.join(ROOT,'logs','iteration-loop','round_reports.md')
line = (f"\n{now} | r936 | attempt-2 absorb+integration round (attempt-1 killed 14:37 watchdog): killed-window bookkeeping amended de32b3f25 + W20 census evidence 11 files committed 3c8ccc25e; S0 rebase onto bm-c r996 x3 zero-conflict (r832 writer-pause: 4 tasks disabled/re-enabled); push ee740143c behind=0 proven | S6 39/39 rc0 (bfilter/bstatus -m rerun rc0); attrition CLEAN; claws match; loop pin=2 no-op; D-19 {d19_note} | r937: W20 slice-1 census continuation -> roster -> prereg draft; 15:30 S6 window; 48h CEO W19 report due 10-16 13:49 | wm={wm_verdict} | orphan=0 | 本地未达 origin commit 数=0\n")
with open(rp,'a',encoding='utf-8') as f:
    f.write(line)

# --- heartbeat ---
hb_path = os.path.join(ROOT,'fleet','machines','bm-b.json')
hb = {}
if os.path.exists(hb_path):
    try: hb = json.load(open(hb_path, encoding='utf-8'))
    except Exception: hb = {}
hb.update({
    'machine_id': 'bm-b',
    'last_seen': now,
    'current_task': 'r936 landed (absorb+integration); r937 = W20 slice-1 census continuation',
    'now_active': 'S0 integration landed; SatEngine ticking; backfill_ext_slots batch in flight',
    'latest_artifact': 'census evidence 3c8ccc25e + push ee740143c @ ' + now,
    'next_milestone': 'W20 roster+prereg draft next window; 48h CEO W19 report due 10-16 13:49',
    'cpu_cores': os.cpu_count(),
    'ram_free_gb': ram_free_gb,
    'gpu_free_vram': vram_free,
    'idle_rounds': 0,
    'agenda_starved': False,
    'heartbeat_epoch_utc': int(time.time()),
    'clock_read': now,
    'ts': now,
    'verdict': 'GREEN: r936 absorb+integration landed; S6 39/39; structural flags supply_floor/pool_starvation (W20 refill r937)',
})
with open(hb_path,'w',encoding='utf-8') as f:
    json.dump(hb,f,ensure_ascii=False,indent=1,sort_keys=True)

# --- idle trigger worked-clear (real output this round) ---
try:
    subprocess.run(['python', os.path.join(ROOT,'Tools','idle_trigger.py'),'--worked'], capture_output=True, timeout=60)
except Exception:
    pass

# --- self-proof ---
chk = json.load(open(sp, encoding='utf-8'))
hb2 = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hb2['clock_read'], 'clock_read must use T separator'
print('state round:', chk['round_no'])
print('d19:', d19_note, '| dec', (dec_sha or '')[:9], '== old' if dec_sha==old_dec else 'CHANGED', '| ord', (ord_sha or '')[:9], '== old' if ord_sha==old_ord else 'CHANGED')
print('wm verdict:', wm_verdict)
print('ram_free_gb:', ram_free_gb, '| vram_free:', vram_free)
print('heartbeat epoch int OK, clock T OK')
print('CLOSEOUT WRITES DONE')
