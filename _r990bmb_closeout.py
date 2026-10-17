# -*- coding: utf-8 -*-
# r990 bm-b closeout: state.json + heartbeat + round report row + live metrics.
import os, sys, json, time, datetime, ctypes, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')

NOW = now_iso()

# live metrics (dependency-free)
free_ram_gb = None
try:
    class MS(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
    ms = MS()
    ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    free_ram_gb = round(ms.ullAvailPhys / (1024 ** 3), 1)
except Exception:
    pass
gpu_free_mb = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'], capture_output=True, timeout=30)
    gpu_free_mb = int(r.stdout.decode().strip().splitlines()[0])
except Exception:
    pass
cpu_pct = None
try:
    r = subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage'],
                       capture_output=True, timeout=30)
    for line in r.stdout.decode('utf-8', 'replace').splitlines():
        s = line.strip()
        if s.isdigit():
            cpu_pct = int(s)
            break
except Exception:
    pass

EPOCH = int(time.time())

DID = (r"r990: (a) S0 estate-absorb+sync surgery: dead-predecessor r989 closeout completed and landed "
       r"(r988+r989 both on origin via rebase replay e3e3a7f8e, push sha-verified; r988 'PUSHED_VERIFIED' "
       r"was fake-green debt now paid); r989-sync-window stash 4-face verified-absorbed then dropped; "
       r"rebase --continue r1032-deadlock broken via manual-commit+quit path; absorb-commit e16084787 "
       r"dropped from replay (daemon regen faces only, live-wins zero loss); r989 heartbeat face did "
       r"not survive replay (HEAD carries r988 12:45 face; state.json carries full r989 record, zero loss). "
       r"(b) D-19 double-hold: orders 1df82bab / decisions 1d4741e4 both zero-delta (r660 raw-bytes probe; "
       r"bm-c r1067 1fd5fc30ac = their own probe anomaly, not ours). fleet/orders unacked set = 0 "
       r"(O-0131 @bm-b legs all closed by r987 in-file receipt + r989 EPBurn git delivery). "
       r"(c) POOL-0018/0019 IGNITION: madmom death root-cause CORRECTED - not Job-Object; the r989 bat "
       r"dies post-vcvars both under CLI child AND under scheduled-task host (structural defect) -> "
       r"step A rewritten to python env-capture path (vcvars env capture + cython preflight + pip madmom, "
       r"retry-cap 3 fuse); anchor burn hosted by NEW self-healing schtask bm-b-AnchorBurn-r990 "
       r"(every 8min, IgnoreNew, InvisibleRunner hidden chain, 4h instance cap, self-disable at DONE) "
       r"= survives session death; whisperX words batch alive at closeout (venv verified, zh wav2vec2 "
       r"align, priority=3 in-production songs, per-song resume-safe; torchcodec warnings benign; "
       r"model download in flight). (d) E1 receipt-2 addendum LOCATED: spawn-gate defer log = "
       r"logs/iteration-loop/run_<stamp>.log 'spawn_gate:' lines (no dedicated file - why default "
       r"position sweeps missed it). (e) round-zero orphan probe 8 faces 0 orphans; S1 smoke re-run "
       r"post-closeout (this script is pre-smoke; smoke verdict rides commit message + r991 report). "
       r"(f) S6 chain 38/38 rc=0 (Saturday no-op faces legal; live.paper family skipped no-new-bar). "
       r"(g) local self-drive pool STARVED open=0; idle_rounds cleared via --worked (real product work).")

NEXT = (r"r991: 1) anchor-burn progress read (words outputs count vs audio=10; madmom VERIFY_RC after "
        r"env-capture retry; fuse state) 2) words-anchor lyric_calibration.py compatibility validation "
        r"1 song 3) POOL-0018 first-batch receipt (orders row + POOL.json faces for dispatcher writer "
        r"seat; missing in-production songs audio = Taildrop dependency per card note) 4) "
        r"results/_r989bmb_tmp_index prescan+cleanup 5) MSG-1249 bm-a pickup watch")

VERDICT = (r"GREEN: r989+r988 landed origin (debt paid) + POOL-0018/0019 anchor burn ignited on "
           r"session-death-proof scheduled task + S6 38/38; honest defers: madmom rebuild now on "
           r"env-capture retry path (fuse 3), words batch in model-download phase, heartbeat r989 "
           r"face lost in replay (superseded by this r990 face)")

# ---- state.json ----
sp = os.path.join(ROOT, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 990
st['round'] = 990
st['round_no_label'] = 'r990'
st['current'] = 'r990: estate+sync surgery + anchor-burn ignition'
st['current_task'] = 'r990: closeout'
st['task'] = 'r990: closeout (state/heartbeat/round-report/push)'
st['did'] = DID
st['last_action'] = 'r990: S0 landed r988+r989 on origin + POOL-0018/0019 anchor-burn self-healing task ignited'
st['last_action_at'] = NOW
st['now_active'] = 'r990 closed; anchor burn in flight (bm-b-AnchorBurn-r990 task, words phase)'
st['next'] = NEXT
st['next_milestone'] = 'POOL-0018 first-batch words anchors before card window 10-18 17:41; madmom env-capture retry r991'
st['verdict'] = VERDICT
st['latest_artifact'] = 'anchor-burn-r990.log + anchor-words-r990.log + schtask bm-b-AnchorBurn-r990 (media/drama-tools/)'
st['last_artifact'] = st['latest_artifact']
for k in ('clock_read', 'last_seen', 'last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at',
          'last_orders_at', 'last_orders_read_at', 'last_decisions_at', 'last_decisions_read_at'):
    st[k] = NOW
st['orphan_face'] = 8
st['orphan_face_note'] = 'r990 round-zero probe (17:0x): 8 py faces, 0 orphans'
st['orphan_faces'] = 8
st['sat_engine'] = {
    'status': 'alive (r990 live-probed rc=0: status exit 0, last_verdict idle)',
    'checked_at': NOW,
}
d19 = st.get('d19_watermark_guard') or {}
d19['round_ref'] = 990
d19['ts'] = NOW
st['d19_watermark_guard'] = d19
st['decisions_delta_pending'] = False
st['orders_delta_pending'] = False
st['last_orders_probe_at'] = NOW
st['last_orders_sha_probe'] = '1df82bab4faea632fb2593a54fce799680878091aea9184220635e9d43c1dfa7'
st['last_orders_sha_probe_note'] = 'r990: zero-delta confirmed (orders 1df82bab / decisions 1d4741e4 both hold)'
st['last_decisions_probe_at'] = NOW
st['sync'] = st.get('sync') or {}
st['sync']['r990_main_push'] = {
    'status': 'PENDING (this commit)',
    'pushed_sha': 'pending',
    'consumed_at': 'pending r991',
    'behind_origin_main': 0,
    'note': 'r990 payload = own faces (state/heartbeat/round report + S6 regen faces + r990 work files); r988+r989 landed earlier this round (push sha-verified e3e3a7f8e)',
}
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
hb = json.load(open(hp, encoding='utf-8'))
hb['machine_id'] = 'bm-b'
hb['last_seen'] = NOW
hb['task'] = 'r990: closeout'
hb['did'] = DID
if free_ram_gb is not None:
    hb['free_ram_gb'] = free_ram_gb
if gpu_free_mb is not None:
    hb['gpu_free_vram_mb'] = gpu_free_mb
if cpu_pct is not None:
    hb['cpu_load_pct'] = cpu_pct
hb['verdict'] = VERDICT
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['ts'] = NOW
hb['round_no'] = 990
hb['round'] = 990
hb['current_task'] = 'r990: closeout'
hb['orders_ack'] = (r"r990: D-19 double-hold zero-delta (orders 1df82bab/decisions 1d4741e4, r660 "
                   r"raw-bytes probe verified); fleet/orders unacked set=0 (O-0131 @bm-b legs closed "
                   r"r987 receipt + r989 EPBurn delivery; O-0100 closed r988); watermarks hold; "
                   r"POOL-0018/0019 ignition this round (anchor-burn task live), receipts follow "
                   r"first-batch completion")
hb['note'] = (r"r990: anchor burn hosted by schtask bm-b-AnchorBurn-r990 (every 8min self-healing, "
              r"survives session death); madmom bat structural defect corrected to env-capture path; "
              r"orphan face 8/0 at round-zero probe")
hb['latest_artifact'] = st['latest_artifact']
hb['next'] = NEXT
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- round report row ----
row = '%s | r990 | %s | evidence: push sha e3e3a7f8e (r988+r989 landed); S6 38/38 rc=0; orphan 8/0; idle --worked; satengine rc=0; anchor-burn task Running | next: %s\n' % (
    NOW, DID, NEXT)
with open(os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md'), 'a', encoding='utf-8') as f:
    f.write(row)

print('CLOSEOUT-OK now=%s ram=%s vram=%s cpu=%s epoch=%d' % (NOW, free_ram_gb, gpu_free_mb, cpu_pct, EPOCH))
