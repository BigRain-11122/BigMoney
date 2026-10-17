# -*- coding: utf-8 -*-
# r991 bm-b: (a) delete degraded word-anchor outputs (words=0, punkt_tab-era) so the
#            next anchor-runner tick re-runs them with punkt_tab now installed;
#            treasure_guard prescan gate before any delete (TREASURE_PROTECTION_LAW s2).
#        (b) quarantine r989 leftover temp git index (results/_r989bmb_tmp_index).
# Receipt: results/_r991bmb_anchor_cleanup.json
import json, os, subprocess, sys, shutil, datetime, glob

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
ANCHORS = r'C:\Fluxgroup\FluxGroup\cph4\fleet\mv-album-001-jay\anchors'
GUARD = os.path.join(ROOT, 'Tools', 'treasure_guard.py')
TMPIDX = os.path.join(ROOT, 'results', '_r989bmb_tmp_index')
QUAR = os.path.join(ROOT, 'results', '_quarantine', 'r991-20261017')
RECEIPT = os.path.join(ROOT, 'results', '_r991bmb_anchor_cleanup.json')
receipt = {'ts': datetime.datetime.now().isoformat(timespec='seconds'), 'round': 'r991', 'machine': 'bm-b'}

def prescan(paths):
    r = subprocess.run([sys.executable, GUARD, 'prescan'] + paths,
                       capture_output=True, cwd=ROOT)
    return r.returncode, (r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace'))[-400:]

# --- (a) degraded words outputs ---
degraded, kept = [], []
for p in sorted(glob.glob(os.path.join(ANCHORS, '*-words.json'))):
    try:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        if int(d.get('word_count', 0)) == 0:
            degraded.append(p)
        else:
            kept.append((os.path.basename(p), d.get('word_count')))
    except Exception as e:
        receipt['words_read_error'] = [os.path.basename(p), repr(e)]
if degraded:
    rc, out = prescan(degraded)
    receipt['words_prescan_rc'] = rc
    receipt['words_prescan_tail'] = out
    if rc == 0:
        os.makedirs(QUAR, exist_ok=True)
        for p in degraded:
            dst = os.path.join(QUAR, os.path.basename(p))
            shutil.move(p, dst)
        with open(os.path.join(QUAR, 'manifest-r991.md'), 'a', encoding='utf-8') as f:
            f.write('%s quarantine: degraded words=0 outputs (punkt_tab missing era) -> re-burn via next anchor tick\n'
                    % receipt['ts'])
            for p in degraded:
                f.write('- %s\n' % os.path.basename(p))
        receipt['words_quarantined'] = [os.path.basename(p) for p in degraded]
    else:
        receipt['words_delete_refused'] = 'prescan rc=%d (registry hit) - kept in place' % rc
receipt['words_kept'] = kept

# --- (b) r989 leftover temp index ---
if os.path.exists(TMPIDX):
    rc, out = prescan([TMPIDX])
    receipt['tmpidx_prescan_rc'] = rc
    if rc == 0:
        os.makedirs(QUAR, exist_ok=True)
        dst = os.path.join(QUAR, os.path.basename(TMPIDX))
        if os.path.isdir(TMPIDX):
            shutil.move(TMPIDX, dst)
        else:
            shutil.move(TMPIDX, dst + '.file')
        with open(os.path.join(QUAR, 'manifest-r991.md'), 'a', encoding='utf-8') as f:
            f.write('%s quarantine: r989 GIT_INDEX_FILE temp leftover (regenerable)\n' % receipt['ts'])
        receipt['tmpidx_quarantined'] = True
else:
    receipt['tmpidx_quarantined'] = 'already-absent'

with open(RECEIPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps(receipt, ensure_ascii=False, indent=1))
