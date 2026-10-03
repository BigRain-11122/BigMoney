"""r629 bm-a: divlowvol pool/fuse hygiene per division.
(1) fuse: tombstone divlowvol SENS sig (data_fixed: T-156 swap verified
    14:39 + QUALITY-SENS clean-burn precedent 500/500 15:15);
    keep-block note on divlowvol NULLS sig (bm-b rightful burner in flight).
    Shared + bm-a lane faces (r603 tombstone pattern, r617 lane law).
(2) pool: release bm-a ghost claims on DIVLOWVOL-NULLS + DIVLOWVOL-SENS
    shards across shared + all 3 lane mirrors (r616 sweep law, r622 note-trail
    shape), raw-text anchored per r509 (no re-serialization).
(3) host_gates dir_nonempty p1c_stock on both divlowvol entries in shared
    face (r603 precedent -- prevents data-root crash on cache-less machines).
"""
import json, os, subprocess
from datetime import datetime

NOW = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
SENS_SIG = 'scripts/fund_divlowvol_p1.py|run,--sensitivity'
NULLS_SIG = 'scripts/fund_divlowvol_p1.py|run,--nulls'
SENS_REASON = ("data_fixed: p1c_stock T-156 swap verified 14:39 (four-point "
               "ALL PASS: vwap_688_check gate true, 13/13 sha256==sender "
               "manifest, 688 magnitude 1.59e6, n_base 3292==bm-b basis); "
               "bm-a QUALITY-SENS clean-burn precedent on new cache "
               "500/500 15:15 rc0; DIVLOWVOL-SENS re-burn unblocked r629")
NULLS_NOTE = ("keep blocked on bm-a r629: double-burn protection -- rightful "
              "burner bm-b 2000-draw in flight (r617-r620 reports, 47+/2000 "
              "at 14:49); off-caliber root resolved by T-156 swap+verify "
              "14:39; clear ONLY if bm-b burn dies AND bm-b lane yields "
              "(per r616 division)")
FUSES = ['results/crash_fuse.json', 'results/crash_fuse.bm-a.json']
POOLS = ['results/runnable_pool.json', 'results/runnable_pool.bm-a.json',
         'results/runnable_pool.bm-b.json', 'results/runnable_pool.bm-c.json']
GATE = ('   "host_gates": [{"kind": "dir_nonempty", '
        '"path": "Money02/data/cache/p1c_stock", "pattern": "*.npy"}],\r\n')

NULLS_NOTE_OLD = ('     "note": "K=2000 same-mask random-selection nulls '
                  '(headline DIVLOWVOL-YIELDVOL rank universe: yield>0 + '
                  'low-vol half + full eligibility, G-MASK identity), eq '
                  'weights, N=20, rng([20520000,k]); feeds skill_line_v2 '
                  'null_pool",\r\n')
SENS_NOTE_OLD = ('     "note": "K=500 space-filling draws over N{10,15,20} '
                 'x vol_screen_frac{0.5,1.0} (1.0 = no-screen ablation), '
                 'rng([20520500,k]); descriptive face only, no verdict",\r\n')
NULLS_OWNER = ('     "owner": "bm-a",\r\n     "owner_since": '
               '"2026-10-03 13:34:07"\r\n')
SENS_OWNER = ('     "owner": "bm-a",\r\n     "owner_since": '
              '"2026-10-03 13:38:15"\r\n')
NULLS_TRAIL = (f' | rel-bm-a-r629 {NOW}: ghost-claim release (burn killed '
              '13:48 r625 off-caliber era; cache T-156 verified 14:39) -- '
              'bm-b rightful burner in flight per division (r617-r620); '
              'fuse keep-blocked on bm-a')
SENS_TRAIL = (f' | rel-bm-a-r629 {NOW}: ghost-claim release (burn killed '
              '13:48 r625 off-caliber era; cache T-156 verified 14:39; fuse '
              'CLEARED r629) -- first claimer re-burns via daemon')

# --- 1. fuse faces ---
for FUSE in FUSES:
    with open(FUSE, encoding='utf-8') as fh:
        fuse = json.load(fh)
    sigs = fuse.get('sigs', {})
    assert SENS_SIG in sigs, f'{FUSE}: sens sig missing'
    assert NULLS_SIG in sigs, f'{FUSE}: nulls sig missing'
    sig = sigs.pop(SENS_SIG)
    assert sig.get('last_refusal_ts', '') < NOW, 'cleared_ts must beat refusals'
    fuse.setdefault('cleared', {})[SENS_SIG] = {
        'cleared_ts': NOW, 'cleared_by': 'bm-a', 'reason': SENS_REASON,
        'crashes': int(sig.get('count', 0)),
        'old_code_sha256': sig.get('code_sha256'),
        'old_note': sig.get('note'),
    }
    sigs[NULLS_SIG]['note'] = NULLS_NOTE
    tmp = FUSE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(fuse, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FUSE)
    chk = json.load(open(FUSE, encoding='utf-8'))
    assert SENS_SIG not in chk['sigs'] and SENS_SIG in chk.get('cleared', {})
    assert NULLS_NOTE[:40] in chk['sigs'][NULLS_SIG].get('note', '')
    print(f'[fuse] {FUSE}: SENS tombstoned, NULLS keep-block note landed')

# --- 2. pool faces: raw-text release (r509 law, r616 all-lane sweep) ---
for POOL in POOLS:
    raw = open(POOL, 'rb').read()
    txt = raw.decode('utf-8')
    assert '\r\n' in txt, f'{POOL}: expected CRLF'
    assert txt.count(NULLS_NOTE_OLD) == 1, f'{POOL}: nulls note anchor x{txt.count(NULLS_NOTE_OLD)}'
    assert txt.count(SENS_NOTE_OLD) == 1, f'{POOL}: sens note anchor x{txt.count(SENS_NOTE_OLD)}'
    assert txt.count(NULLS_OWNER) == 1, f'{POOL}: nulls owner anchor x{txt.count(NULLS_OWNER)}'
    assert txt.count(SENS_OWNER) == 1, f'{POOL}: sens owner anchor x{txt.count(SENS_OWNER)}'
    nulls_new = NULLS_NOTE_OLD[:-4] + NULLS_TRAIL + '",\r\n'
    sens_new = SENS_NOTE_OLD[:-4] + SENS_TRAIL + '",\r\n'
    txt = txt.replace(NULLS_NOTE_OLD, nulls_new)
    txt = txt.replace(SENS_NOTE_OLD, sens_new)
    txt = txt.replace(NULLS_OWNER, '')
    txt = txt.replace(SENS_OWNER, '')
    open(POOL, 'wb').write(txt.encode('utf-8'))
    json.loads(txt)  # parse gate
    print(f'[pool] {POOL}: 2 ghost claims released (raw-text, CRLF preserved)')

# --- 3. host_gates on shared face divlowvol entries (r603 pattern) ---
POOL = 'results/runnable_pool.json'
txt = open(POOL, 'rb').read().decode('utf-8')
inserted = 0
for eid in ('FUND-DIVLOWVOL-P1-NULLS', 'FUND-DIVLOWVOL-P1-SENS'):
    anchor = f'   "id": "{eid}",\r\n'
    i = txt.find(anchor)
    assert i >= 0, f'anchor not found: {eid}'
    j = i + len(anchor)
    assert '"host_gates"' not in txt[j:j + 400], f'already gated: {eid}'
    txt = txt[:j] + GATE + txt[j:]
    inserted += 1
open(POOL, 'wb').write(txt.encode('utf-8'))
json.loads(txt)
print(f'[pool] host_gates inserted x{inserted} (shared face, raw-text)')

# --- 4. surgical diff assertion (r509 law) ---
for f in POOLS + FUSES:
    r = subprocess.run(['git', 'diff', '--numstat', '--', f],
                      capture_output=True)
    line = r.stdout.decode('utf-8', 'replace').strip()
    print(f'[diff] {f}: {line or "(unchanged)"}')
print('[done] r629 divlowvol hygiene edits landed')
