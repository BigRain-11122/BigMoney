"""r782 bm-b: dump the clobbered V entry block from shared+bm-b faces."""
import json

for path in ('results/runnable_pool.json',
             'results/runnable_pool.bm-b.json'):
    raw = open(path, encoding='utf-8', newline='').read()
    i = raw.find('"FUND-VALUE-P1-NULLS"')
    j = raw.rfind('{', 0, i)
    d = 0
    k = j
    while k < len(raw):
        if raw[k] == '{':
            d += 1
        elif raw[k] == '}':
            d -= 1
            if d == 0:
                break
        k += 1
    blk = raw[j:k + 1]
    eol = '\r\n' if '\r\n' in blk else '\n'
    lines = blk.split(eol)
    print('=' * 20, path, 'EOL:', 'CRLF' if eol == '\r\n' else 'LF',
          'lines:', len(lines))
    p = json.loads(blk)
    print('entry status:', p.get('status'),
          '| done_at:', p.get('done_at'),
          '| done_by:', p.get('done_by'),
          '| lane_owner:', p.get('lane_owner'))
    sh = p['shards'][0]
    print('shard status:', sh.get('status'),
          '| owner:', sh.get('owner'),
          '| owner_since:', sh.get('owner_since'),
          '| done_at:', sh.get('done_at'),
          '| harvested_by:', sh.get('harvested_by'),
          '| harvest_claim:', (sh.get('harvest_claim') or '')[:60])
    done_lines = [n for n, l in enumerate(lines)
                  if l.strip() == '"status": "done",']
    del_lines = [n for n, l in enumerate(lines)
                 if l.strip().startswith(('"done_at":', '"harvested_by":',
                                          '"harvest_claim":', '"done_by":'))]
    ow_lines = [n for n, l in enumerate(lines)
                if l.strip().startswith('"owner_since":')]
    rn_lines = [n for n, l in enumerate(lines)
                if l.strip().startswith('"runner":')]
    lo_lines = [n for n, l in enumerate(lines)
                if l.strip().startswith('"lane_owner":')]
    print('done-status lines:', done_lines, '| del-field lines:', del_lines,
          '| owner_since lines:', ow_lines, '| runner lines:', rn_lines,
          '| lane_owner lines:', lo_lines)
