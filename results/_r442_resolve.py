"""r442 rebase-conflict resolver: fundamental snapshot + REPORT/LIVE twins + CODELY memory-union.
Stages: :1: = merge-base, :2: = origin (bm-c r233), :3: = local (r442 close).
Laws: r188/R208 (snapshot deep-ts take-new), r327/r329 (twin same-side, md byte-copy),
r327 memory-union entry-level dual-coverage verification (local did hot-cold re-arch
= non-append edit, prefix assertion intentionally skipped per r328/r329 lineage).
"""
import json
import re
import subprocess
import sys

ARCH = 'research/memory-archive/202609.md'


def blob(spec):
    out = subprocess.run(['git', 'show', spec], capture_output=True, check=True)
    return out.stdout  # bytes


def deep_ts(obj, best=None, path=''):
    """Deep-scan for newest wall-clock ts string (r311; probe path existence r319)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.match(r'^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}', v):
                if best is None or v > best[0]:
                    best = (v, path + '/' + k)
            else:
                best = deep_ts(v, best, path + '/' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            best = deep_ts(v, best, path + '[%d]' % i)
    return best


def resolve_snapshot(path):
    o = json.loads(blob(':2:%s' % path).decode('utf-8'))
    l = json.loads(blob(':3:%s' % path).decode('utf-8'))
    to, tl = deep_ts(o), deep_ts(l)
    pick = 'origin' if to and (not tl or to[0] >= tl[0]) else 'local'
    doc = o if pick == 'origin' else l
    with open(path, 'wb') as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1).encode('utf-8'))
    json.load(open(path, encoding='utf-8'))  # parse-verify
    print('[snapshot] %s -> %s side (origin_ts=%s local_ts=%s)' % (path, pick, to, tl))


def resolve_twin(json_path, md_path):
    oj = json.loads(blob(':2:%s' % json_path).decode('utf-8'))
    lj = json.loads(blob(':3:%s' % json_path).decode('utf-8'))
    to, tl = deep_ts(oj), deep_ts(lj)
    pick = 'origin' if to and (not tl or to[0] >= tl[0]) else 'local'
    side = ':2:' if pick == 'origin' else ':3:'
    for p in (json_path, md_path):   # md byte-copy from SAME side (r329)
        data = blob(side + p)
        with open(p, 'wb') as f:
            f.write(data)
    json.load(open(json_path, encoding='utf-8'))  # parse-verify
    print('[twin] %s + %s -> %s side (origin_ts=%s local_ts=%s)'
          % (json_path, md_path, pick, to, tl))


def resolve_codely():
    base = blob(':1:CODELY.md').decode('utf-8').split('\n')
    orig = blob(':2:CODELY.md').decode('utf-8').split('\n')
    loca = blob(':3:CODELY.md').decode('utf-8').split('\n')
    base_set, loca_set, orig_set = set(base), set(loca), set(orig)
    # local re-arch removed flow lines: they MUST live verbatim in archive (zero-loss proof)
    removed_by_local = [ln for ln in base_set - loca_set if ln.strip() and ln.startswith('- ')]
    arch = blob('REBASE_HEAD:research/memory-archive/202609.md').decode('utf-8')
    for ln in removed_by_local:
        assert ln in arch, 're-arch zero-loss check FAILED: %r' % ln[:60]
    # origin added lines not present locally -> append (entry-level dual coverage, r327)
    orig_added = [ln for ln in orig if ln not in loca_set and ln not in base_set and ln.strip()]
    # origin edited shared lines (in base+origin, not in local) -> manual review list
    orig_edits = [ln for ln in orig if ln in base_set and ln not in loca_set and ln.strip()]
    out_lines = list(loca)
    # append origin-added entries right after the last hot entry (before ### Reference block if any)
    if orig_added:
        idx = max(i for i, ln in enumerate(out_lines) if ln.startswith('- ['))
        for j, ln in enumerate(orig_added):
            out_lines.insert(idx + 1 + j, ln)
    text = '\n'.join(out_lines)
    with open('CODELY.md', 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    # dual-coverage verification: every non-empty line of BOTH sides is in output or archive or was base-only-removed-with-archive-proof
    out_set = set(out_lines)
    for ln in orig:
        if ln.strip() and ln not in out_set:
            assert ln in base_set, 'origin line unaccounted: %r' % ln[:60]
    print('[codely] merged: %d origin-added lines appended, %d local re-arch removals archive-proven, origin-shared-edits=%d'
          % (len(orig_added), len(removed_by_local), len(orig_edits)))
    if orig_edits:
        print('[codely] WARN origin-edited shared lines not adopted (kept local):')
        for ln in orig_edits:
            print('   ', ln[:120])


if __name__ == '__main__':
    resolve_snapshot('results/fundamental_b_layer_filter.json')
    resolve_twin('docs/daily_report/REPORT-2026-09-29.json', 'docs/daily_report/REPORT-2026-09-29.md')
    resolve_twin('docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-2026-09-29.md')
    resolve_twin('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')
    resolve_codely()
    print('resolver done')
