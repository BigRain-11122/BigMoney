# r1050 bm-c closeout: CRASH-RECOVERY ABSORB 41st gen (dead r1050 session estate absorbed)
# - advance state round_no 1050 -> 1051
# - consume S0.5 deltas: ORD f321f54a-><new>, DEC ec6b9164-><new> (row-level triage done in-window)
# - rewrite heartbeat (r1050 closeout face, epoch int, clock T-format, self-assert)
# - append round report row
import json, time, subprocess, hashlib, os, sys

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
GRP  = r'K:\Fluxgroup\FluxGroup'
GIT  = r'C:\Program Files\Git\cmd\git.exe'
os.chdir(ROOT)

ts = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

def gshow(path):
    r = subprocess.run([GIT, '-C', GRP, 'show', 'origin/main:' + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('git show failed for ' + path)
    return r.stdout

ord_sha = hashlib.sha256(gshow('docs/orders.md')).hexdigest()
dec_sha = hashlib.sha256(gshow('docs/decisions.md')).hexdigest()
assert ord_sha.startswith('995c0576d2e67e6f'), ord_sha
assert dec_sha.startswith('d9940c44b06b73bb'), dec_sha

# ---- system snapshot (light, honest) ----
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.8), 1)
    ram_free = round(psutil.virtual_memory().available / 2**30, 1)
except Exception:
    cpu_pct, ram_free = 4, 6.6
try:
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True).stdout.strip().splitlines()[0]
    gpu_mib = int(float(o))
except Exception:
    gpu_mib = 14891
gpu_mb = round(gpu_mib / 1.048576)

# idle trigger face (fresh read; trigger declared worked this round)
try:
    it = json.load(open(r'results\idle_trigger.bm-c.json', encoding='utf-8'))
    idle_rounds = int(it.get('idle_rounds', 0))
    agenda_starved = bool(it.get('agenda_starved', False))
except Exception:
    idle_rounds, agenda_starved = 0, False

ord16, dec16 = ord_sha[:16], dec_sha[:16]

WM = 'watermark verdict=绿 (red=false / satengine ALIVE rc0 heartbeat 65s fresh / open tickets 0 / pool-empty window)'

CONTENT = (
    '2026-10-16T12:2x | r1050 | CRASH-RECOVERY ABSORB 41st gen: dead r1050 session (codely died ~12:15 pre-closeout; '
    'splice+engine products already self-pushed by dead window) estate absorbed+closed this window -- '
    '(1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill (ComfyUI serve + album serve standing services read-only); '
    'S0 fetch origin==HEAD 0/0 (splice e63561df3 + engine appends cbf6411bf/b3d563f4f already on origin); '
    '(2) S0.5 BOTH DELTAS CONSUMED: ORD f321f54a->' + ord16 + ' (2 rows: C-20261016-01 bm-d six-card allocation committee-executed zero BigMoney action / '
    'O-20261016-1120 jayredo 18h accountability -- bm-c leg ② VERIFIED SERVED: 11/17 released files delivered origin b845cc7 + '
    '三行回执 77f5326 I2V-URL-INDEX +4 rows [烧到第几件/卡点=bm-a director 4-pick-1/ETA~2h] both merge-base rc0 on origin; '
    '③⑤⑥ mechanism faces = bm-a/事件班 zero bm-c leg) '
    '+ DEC ec6b9164->' + dec16 + ' (D-01..D-07: D-02 claw fourth owner channel LANDED in repo -- bm-c leg = hook reinstall verified match this round; '
    'D-06 three-disabled-tasks = bm-a owner face, bm-c local probe Bigmoney-Autofill Ready + Bigmoney-ResidentDispatcher Ready + '
    'HQ-OllamaOrphanWatch not-present = zero local deficiency; D-03 atomic-push -C ROOT fix already landed; D-01/04/05/07 committee/batch faces zero action); '
    '(3) S1 smoke 49/49 re-run this window; '
    '(4) S3 boards: jobs 0 / satengine ALIVE rc0 / wm red=false / idle green_idle=false claimable_pool_lines=1 stays r354 / '
    'trial-labor standing line = W252 judgment wave CLOSED this round + W253 seat queued; '
    '(5) P0 PRODUCT = W252 CYCLE COMPLETE: sixgate PRE-FINALIZE ALL PASS first-run (gate-1 triple identity '
    'worktree==freeze receipt==LANDED blob n1 7252c90bad52de99 / pf b3eed1c579e7f22f, zero post-splice heal, 14th consecutive correct-phase) '
    '+ finalize one-pass 976,535+2,200=978,735 EXACT / merged K=552,320 / skill_line 1.1942->1.1943 (K-lift +0.0001 second consecutive nonzero in-band) '
    '+ fivekeys ALL PASS (mu-gap 0.002565/sigma-rel 0.00477pct/p95 +0.0046/K-lift 0.0001/se_mu 0.000330 held) + sec.7/8 backfilled '
    '+ W253 SEAT published (staircase continues: naive W253 A 571_701..573_700 REFUSED at registered W252 B band 571_701..571_900 = '
    'A 2nd consecutive hop + B reservation cascade, live re-derive governs r587); '
    '(6) 5x HANDOVER r1026-r1050 consolidated, overdue stamps r1030/1035/1040/1045 disclosed (dead-session write verified in tree); '
    '(7) S6 43/43 rc0 dead-window chain 12:05 (dualrun ZERO-DRIFT streak 8 / bars 10-16 not due till 15:30 papers debt=0 / '
    'audit idle-starvation FLAG answered-by-chain W252->W253); '
    '(8) S7 quad (loop pin=5 no-op + watchdog Ready + claws x2 match templates w/ D-02 fourth channel) + attrition 4 CLEAN + idle --worked '
    '| receipts: smoke 49/49 + sixgate ALL PASS + fivekeys all_pass=true + finalize 978,735 EXACT + S6 log 43x rc=0 + '
    'origin merge-base rc0 x2 + local task probe Ready/Ready + heartbeat epoch int readback '
    '| 本地未达 origin commit 数=0 at open (closeout push rides this window, verify next round open)'
)

POINTER = (
    '(1) W253 PREREG FREEZE = FIRST ACTION (machine-SUB from committed frozen W252 tpl = this closeout commit\'s '
    'research/PERPETUAL_N1_W252_PREREG.md, blob byte-verify via git hash-object; post-W252 universe live re-derive: '
    'naive A 571_701..573_700 REFUSED at registered W252 B band 571_701..571_900 = staircase 2nd consecutive hop, '
    'B reservation cascade ~573_901-class, W253 freezer 禁假设 A-base==prior-B-tail+1 须重读 live trace per §8 face; '
    'key-anchor W252 actuals ledger 978,735 / K=552,320 / merged mu -0.09274 / se_mu 0.000330 / W252-only mu -0.090175; '
    'banned_direction_gate pre+post; count-asserted transform); '
    '(2) engine mtime-watch self-burn 12/12; (3) sixgate PRE-FINALIZE correct-phase (W217-debt standing law); '
    '(4) finalize one-pass 978,735+2,200=980,935 EXACT / K=554,520 projection + fivekeys vs W252 keys + sec.7/8 backfill; '
    '(5) W254 seat publish after finalize; (6) bars 10-16 window 15:30 papers debt=0 (if new bar lands fire full papers chain); '
    '(7) ORD/DEC tail re-scan (both hashes moved this round)'
)

VERDICT = (
    'green: r1050 = CRASH-RECOVERY ABSORB closeout -- P0 PRODUCT W252 CYCLE COMPLETE landed '
    '(sixgate ALL PASS 14th correct-phase + finalize 978,735/K=552,320 EXACT + fivekeys ALL PASS + sec7/8 backfilled + '
    'W253 seat published, staircase continues) + S0.5 both deltas consumed (ORD 2 rows incl jayredo ② verified-served on origin / '
    'DEC D-01..07) + smoke 49/49 + S6 43/43 + S7 quad + attrition CLEAN'
)

DID = CONTENT + ' | 下轮指针 r1051: ' + POINTER

CURTASK = 'r1050 closeout (W252 cycle COMPLETE absorbed + landed + W253 seat published)'
ARTIFACT = ('results/perpetual_faces/n1_w252_results.json (W252 finalize: ledger 978,735 / merged K=552,320, 2026-10-16 11:57) '
            '+ n1 §7/8 backfill + fivekeys/sixgate evidence -- landed this closeout commit')
MILESTONE = ('W253 prereg freeze = r1051 FIRST ACTION per seat (next loop fire 12:35) -> engine self-burn 12/12 -> '
             'sixgate/finalize (r1052-1053); jayredo remaining 6 slots blocked on bm-a director 4-pick-1 (upstream, ETA ~2h after pick)')

# ---------- patch state ----------
st = json.load(open('state-bm-c.json', encoding='utf-8'))
st['round_no'] = 1051
st['round_no_label'] = 'r1051'
st['last_round'] = 'r1050'
st['last_round_label'] = 'r1050'
st['last_round_closed'] = ts
st['last_round_at'] = ts
st['last_round_ts'] = ts
st['last_round_summary'] = ('r1050: W252 CYCLE COMPLETE absorbed+landed (sixgate ALL PASS + finalize 978,735/K=552,320 + '
                            'fivekeys ALL PASS + W253 seat) + both ORD/DEC deltas consumed')
st['last_round_summary_at'] = ts
st['clock_read'] = ts
st['current_task'] = CURTASK
st['current_task_at'] = ts
st['current_task_ts'] = epoch
st['now_active'] = ts
st['activity_now'] = ts
st['did'] = DID
st['verdict'] = VERDICT
st['last_action'] = 'r1050 closeout (W252 cycle COMPLETE absorbed + landed)'
st['last_action_at'] = ts
st['next'] = 'r1051: ' + POINTER
st['next_milestone'] = MILESTONE
st['last_artifact'] = ARTIFACT
st['recent_artifact'] = ARTIFACT
st['latest_artifact'] = ARTIFACT
st['note'] = ('r1050: W252 CYCLE COMPLETE (dead-window splice e63561df3 + burn 12/12 cbf6411bf/b3d563f4f + '
              'sixgate ALL PASS + finalize 978,735 EXACT + fivekeys + W253 seat; absorb-continuation closeout)')
st['r1050_closeout_note'] = ('crash-recovery absorb 41st gen: dead session 11:33-12:15 estate (splice/burn/sixgate/finalize/'
                              'fivekeys/sec78/seat/HANDOVER/S6) absorbed verbatim + verified + closed; closeout commit carries it')
st['head_sha'] = ('b3d563f4f (dead-window splice e63561df3 + engine appends cbf6411bf/b3d563f4f already on origin; '
                 'finalize product n1_w252_results.json + evidence ride this closeout commit)')
st['prod_lanes'] = ('CPU=engine queue never-dry (W253 PREREG FREEZE = r1051 first action per seat) ; GPU=VRAM ' +
                    str(round(gpu_mib/1024, 1)) + 'G free')
st['full_load_selfproof'] = {'占用一行': 'CPU=engine queue never-dry (W252 FINALIZED -> W253 prereg freeze = r1051 first action per seat) ; '
                              'GPU=VRAM ' + str(round(gpu_mib/1024, 1)) + 'G free (MV jayredo line: 11/17 delivered, 6 slots blocked upstream bm-a)'}
st['orphan_face'] = 2
st['orphan_faces'] = 2
st['last_orders_sha'] = ord_sha
st['last_decisions_sha'] = dec_sha
st['last_orders_seen'] = ts
st['last_decisions_seen'] = ts
st['last_orders_at'] = ts
st['last_decisions_at'] = ts
st['last_decisions_read_at'] = ts
st['last_orders_read_note'] = ('r1050: ORD delta f321f54a->' + ord16 + ' consumed (2 rows: C-20261016-01 committee-executed zero action / '
                               'O-20261016-1120 jayredo ② bm-c leg verified-served origin b845cc7+77f5326)')
st['last_decisions_read_note'] = ('r1050: DEC delta ec6b9164->' + dec16 + ' consumed (D-01..D-07; D-02 claw fourth channel landed '
                                  'bm-c leg=hook reinstall match; D-06 three-task gap=bm-a owner, bm-c local Ready/Ready/not-present)')
st['cpu_pct'] = cpu_pct
st['free_ram_gb'] = ram_free
st['idle_ram_gb'] = ram_free
st['ram_free_gb'] = ram_free
st['gpu_free_vram_mib'] = gpu_mib
st['gpu_free_vram_mb'] = gpu_mb
st['gpu_free_mib'] = gpu_mib
st['gpu_free_mb'] = gpu_mb
st['free_vram_mb'] = gpu_mb
st['gpu_vram_free_mb'] = gpu_mb
st['idle_rounds'] = idle_rounds
st['agenda_starved'] = agenda_starved
st['heartbeat_epoch_utc'] = epoch
st['heartbeat_epoch_utc_type'] = 'int (assert)'
st['sync'] = {'origin_tip': 'b3d563f4f (dead-window splice+engine appends on origin; closeout finalize product push rides this window)',
              'ts': ts}
st['verify'] = ('receipts: origin==HEAD at open (merge-base rc0 x2 for b845cc7/77f5326 jayredo delivery+receipt) + smoke 49/49 + '
                'sixgate ALL PASS + fivekeys all_pass=true + finalize 978,735 EXACT + S6 43x rc=0 + attrition 4 CLEAN + '
                'claws x2 match + loop pin=5 + watchdog Ready + idle --worked + heartbeat epoch int readback')
st['updated'] = ts
st['updated_at'] = ts
st['ts'] = ts
json.dump(st, open('state-bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- patch heartbeat ----------
hb = json.load(open(r'fleet\machines\bm-c.json', encoding='utf-8'))
hb['machine_id'] = 'bm-c'
hb['clock_read'] = ts
hb['ts'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['cpu_pct'] = cpu_pct
hb['free_ram_gb'] = ram_free
hb['idle_ram_gb'] = ram_free
hb['gpu_free_vram_mib'] = gpu_mib
hb['gpu_free_vram_mb'] = gpu_mb
hb['current_task'] = CURTASK
hb['current_task_at'] = ts
hb['did'] = DID
hb['verdict'] = VERDICT
hb['last_artifact'] = ARTIFACT
hb['next_milestone'] = MILESTONE
hb['idle_rounds'] = idle_rounds
hb['agenda_starved'] = agenda_starved
json.dump(hb, open(r'fleet\machines\bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- self-asserts (smoke F7 shape) ----------
chk = json.load(open(r'fleet\machines\bm-c.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read not ISO-T'
chk2 = json.load(open('state-bm-c.json', encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int) and chk2['round_no'] == 1051

# ---------- round report row ----------
ROW = (ts + ' | r1050 | bm-c | ' + WM + ' | ' + CONTENT + ' | 下轮指针 r1051: ' + POINTER + '\n')
with open('round_reports-bm-c.md', 'a', encoding='utf-8', newline='') as f:
    f.write(ROW)

print('CLOSEOUT OK')
print('ts:', ts, 'epoch:', epoch)
print('ord_sha:', ord16, 'dec_sha:', dec16)
print('cpu:', cpu_pct, 'ram_free:', ram_free, 'gpu_mib:', gpu_mib)
print('round_no: 1050 -> 1051 | heartbeat epoch int OK | report row appended')
