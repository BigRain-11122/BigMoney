"""r626d bm-b: re-establish crash-fuse keep-block on the two runner files
edited this round (MSG-1720 Finding B fix + divlowvol audit-text cosmetic).

Why: autofill's launch gate refuses a relaunch only while the sig's
code_sha256 == _sha16(runner). The edits changed both files, so the old
keep-blocked sigs no longer match -> the gate would auto-clear (code_changed
tombstone) and any machine's tick could claim FUND-VALUE-P1-NULLS /
FUND-DIVLOWVOL-P1-NULLS and double-burn alongside the in-flight canonical
burners (r616 ghost-claim family). Re-stamp both sigs with the NEW sha16 +
a fresh refusal ts (merge newer-event-wins) so the keep-block holds until
the burns complete.

Faces: shared + own lane (r629 pattern). No pool edits. Idempotent: re-run
just refreshes ts/note.
"""
import hashlib, json, os
from datetime import datetime

NOW = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
SIGS = {
    'scripts/fund_value_p1.py|run,--nulls': (
        'scripts/fund_value_p1.py',
        'FUND-VALUE-P1-NULLS', 'fund-value-p1-nulls-0of1', 34396, '04:38'),
    'scripts/fund_divlowvol_p1.py|run,--nulls': (
        'scripts/fund_divlowvol_p1.py',
        'FUND-DIVLOWVOL-P1-NULLS', 'fund-divlowvol-p1-nulls-0of1', 30208,
        '11:54'),
}


def sha16(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]


def main():
    for fuse_path in ('results/crash_fuse.json',
                      'results/crash_fuse.bm-b.json'):
        fuse = json.load(open(fuse_path, encoding='utf-8'))
        sigs = fuse.setdefault('sigs', {})
        for sig, (runner, entry, shard, pid, since) in SIGS.items():
            new_sha = sha16(runner)
            reg = sigs.get(sig)
            if reg is None:
                reg = sigs[sig] = {'count': 0, 'refusals': 0}
            reg.update({
                'code_sha256': new_sha,
                'entry': entry, 'shard': shard, 'machine': 'bm-b',
                'last_refusal_ts': NOW,
                'note': (
                    'keep-blocked bm-b r626d: runner edited this round '
                    '(MSG-2026-10-03-1720 Finding B finalize passive-guard '
                    'fix + divlowvol Y10M->CNY10M audit text) -- in-flight '
                    f'canonical burner pid {pid} since {since} alive '
                    '(r617-r620 division); nulls resume is done-key '
                    'checkpointed so a second process would race the same '
                    'missing k rows (r616 double-burn family). Relaunch '
                    'refused until 2000/2000 complete; clear ONLY if bm-b '
                    'burn dies AND bm-b yields the lane.')})
            print(f'{fuse_path} :: {sig} -> sha {new_sha} keep-block @{NOW}')
        tmp = fuse_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(fuse, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, fuse_path)
        chk = json.load(open(fuse_path, encoding='utf-8'))
        for sig, (runner, *_rest) in SIGS.items():
            got = chk['sigs'][sig]['code_sha256']
            assert got == sha16(runner), f'{fuse_path}/{sig} sha mismatch'
    print('[done] both fuse faces re-stamped with post-edit sha16 + fresh ts')


if __name__ == '__main__':
    main()
