"""r738 bm-c rebase-conflict resolver: 8 non-ALL_FACES faces (push-storm
mirror of bm-a r866 same-window family). ALL_FACES members (3:
lhb_update_status / futures_update_status / token_usage) were resolved via
scripts/merge_lane_views.py resolve BEFORE this script ran (r376 canon
entry point -- union/take-new recipes imported from the merger). The 3
git-auto-merged faces (compute_audit / regime_state / update_status) were
verified post-merge separately: compute_audit history=26 dups=0 sorted=True
union-complete (r685 semantic gate); regime_state + update_status are
both-sides deterministic regens off the same frozen 2026-09-30 panel (only
the ts field differs) -> any merge outcome semantically identical.
This script handles the 8 snapshot/twin faces per the
bigmoney-conflict-resolve skill recipes:
  - twin-regen-md (daily_report + live_usage + live-latest): json face
    take-new by its OWN generation key (deep-scan probe trap avoided),
    md twins byte-copied from the SAME side (twin coupling r327/r329).
  - per-run snapshots (_attrition_guard_scan / fundamental_b_layer_filter):
    take-new by ts/updated, whole doc.
Stage reads via ls-files -u -> git cat-file <sha> (r648 law; :N: reads can
return empty stdout + rc0 in rebase windows). Parse-verify before write
(r185 law). Ties resolve to stage2 = origin side (r140 canon). Verdicts
printed per file; any assertion failure = hard stop (r705 rc-gate law).
No git add here -- the add+continue step runs atomically in the same
shell as the rebase continue (r787 law)."""
import json
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# (path, generation-key) -- md twins resolved by coupling, listed in the
# same order with key=None.
FACES = [
    ('docs/daily_report/REPORT-2026-10-08.json', 'generated_at'),
    ('docs/daily_report/REPORT-2026-10-08.md', None),
    ('docs/live_usage/LIVE-2026-10-08.json', 'generated'),
    ('docs/live_usage/LIVE-2026-10-08.md', None),
    ('docs/live_usage/LIVE-latest.json', 'generated'),
    ('docs/live_usage/LIVE-latest.md', None),
    ('results/_attrition_guard_scan.json', 'ts'),
    ('results/fundamental_b_layer_filter.json', 'updated'),
]

# md path -> its json twin (byte-coupled to the twin's winning side)
TWIN_OF = {
    'docs/daily_report/REPORT-2026-10-08.md':
        'docs/daily_report/REPORT-2026-10-08.json',
    'docs/live_usage/LIVE-2026-10-08.md':
        'docs/live_usage/LIVE-2026-10-08.json',
    'docs/live_usage/LIVE-latest.md': 'docs/live_usage/LIVE-latest.json',
}


def stage_sha(rel, stage):
    """r648 channel: ls-files -u -> stage sha -> cat-file raw bytes."""
    r = subprocess.run(['git', '-C', REPO, 'ls-files', '-u', '--', rel],
                        capture_output=True)
    if r.returncode != 0:
        raise SystemExit('ls-files -u failed for %s: %s'
                         % (rel, r.stderr.decode('utf-8', 'replace')))
    want = str(stage)
    for line in r.stdout.decode('utf-8').splitlines():
        parts = line.split('\t')
        meta = parts[0].split()
        # ls-files -u line: "<mode> <sha> <stage>\t<path>"
        if len(meta) >= 3 and meta[2] == want and len(meta[1]) == 40:
            return meta[1]
    raise SystemExit('no stage %s entry for %s -- ls-files -u empty'
                     % (want, rel))


def blob_bytes(sha):
    r = subprocess.run(['git', '-C', REPO, 'cat-file', '-p', sha],
                        capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit('cat-file empty/failed for %s (rc=%d, %dB)'
                         % (sha, r.returncode, len(r.stdout)))
    return r.stdout


def marker_scan(raw, rel):
    if b'<<<<<<<' in raw or b'>>>>>>>' in raw or b'=======' in raw:
        raise SystemExit('conflict markers in stage blob %s -- polluted'
                         % rel)


def main():
    verdicts = {}
    for rel, key in FACES:
        s2 = blob_bytes(stage_sha(rel, 2))   # origin/base side (r351)
        s3 = blob_bytes(stage_sha(rel, 3))   # replay side = local (r351)
        marker_scan(s2, rel)
        marker_scan(s3, rel)
        if key:
            o2 = json.loads(s2.decode('utf-8'))
            o3 = json.loads(s3.decode('utf-8'))
            t2, t3 = o2[key], o3[key]
            if t3 > t2:
                winner, side, wts = s3, 'LOCAL(replay)', t3
                print('%s: take %s (%s %s vs %s)'
                      % (rel, side, key, wts, t2))
            elif t2 > t3:
                winner, side, wts = s2, 'ORIGIN(base)', t2
                print('%s: take %s (%s %s vs %s)'
                      % (rel, side, key, wts, t3))
            else:
                winner, side, wts = s2, 'ORIGIN(base,tie-r140)', t2
                print('%s: take %s (tie %s=%s, r140 -> origin side)'
                      % (rel, side, key, t2))
            json.loads(winner.decode('utf-8'))   # parse-verify exact bytes
            verdicts[rel] = side
        else:
            twin = TWIN_OF[rel]
            if twin not in verdicts:
                raise SystemExit('twin %s resolved before its json face'
                                 % rel)
            side = verdicts[twin]
            winner = s3 if 'LOCAL' in side else s2
            verdicts[rel] = side
            print('%s: byte-copy %s (twin coupling with %s)'
                  % (rel, side, twin))
        with open(REPO + '\\' + rel.replace('/', '\\'), 'wb') as fh:
            fh.write(winner)
    print('resolver done: 8 faces written (%d LOCAL / %d ORIGIN)'
          % (sum(1 for v in verdicts.values() if 'LOCAL' in v),
             sum(1 for v in verdicts.values() if 'LOCAL' not in v)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
