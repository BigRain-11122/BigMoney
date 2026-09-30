"""r473 bm-a rebase-conflict resolver (batch-2 vs bm-b r461 a37f6460b).

Classifier: 15 UU -> 13 recipe + resolver-6 (already applied via
merge_lane_views for ALL_FACES) + this script handles:
  - snapshot take-new (deep-ts probe r311/D-09): fundamental_b_layer_filter,
    _attrition_guard_scan (classifier UNKNOWN -> manual class = per-run
    scan evidence snapshot, take-new law R216)
  - twin-side coupling (r327/r329): REPORT-20260930 json decides side,
    md twin byte-copied from the SAME side; LIVE-20260930 json decides,
    all LIVE-* twins (latest pointers share identical blob hashes) same side
  - marks jsonl append-log: line-level byte-dedup union (r188/r217), stable
    ts sort; distinct-content same-ts rows (sync-storm dual-write evidence,
    incl. the 09:35:01 zero-price rows the D-27 audit cites) all preserved
Stage blobs read by explicit hash via git cat-file (r-law: bytes not PS redir).
"""
import io
import json
import re
import subprocess

def raw(h: str) -> bytes:
    r = subprocess.run(['git', 'cat-file', '-p', h], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'cat-file fail {h}: {r.stderr.decode("utf-8", "replace")[:150]}')
    return r.stdout

def deep_ts(obj, acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.match(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}', v):
                acc.append(v)
            else:
                deep_ts(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, acc)
    return acc

def take_new(path, h2, h3):
    a, b = raw(h2).decode('utf-8'), raw(h3).decode('utf-8')
    ja, jb = json.loads(a), json.loads(b)
    ta = max(deep_ts(ja) or [''])
    tb = max(deep_ts(jb) or [''])
    txt, side = (b, 'ours(:3:)') if tb >= ta else (a, 'origin(:2:)')
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)
    json.loads(io.open(path, encoding='utf-8').read())  # parse-verify r185
    print(f'[take_new] {path}: origin={ta} ours={tb} -> {side}')

def twin(path_json, h2j, h3j, md_pairs):
    a, b = raw(h2j).decode('utf-8'), raw(h3j).decode('utf-8')
    ta = max(deep_ts(json.loads(a)) or [''])
    tb = max(deep_ts(json.loads(b)) or [''])
    side = 'ours' if tb >= ta else 'origin'
    with io.open(path_json, 'w', encoding='utf-8', newline='') as f:
        f.write(b if side == 'ours' else a)
    for path_md, h2m, h3m in md_pairs:
        blob = raw(h3m if side == 'ours' else h2m)
        with io.open(path_md, 'wb') as f:
            f.write(blob)
    print(f'[twin] {path_json}: origin={ta} ours={tb} -> {side} (md twins byte-copied same side)')

def marks_union(path, h2, h3):
    la = [l for l in raw(h2).decode('utf-8').splitlines() if l.strip()]
    lb = [l for l in raw(h3).decode('utf-8').splitlines() if l.strip()]
    seen, out = set(), []
    for l in la + lb:
        if l in seen:
            continue
        seen.add(l)
        out.append(l)
    out.sort(key=lambda l: json.loads(l)['ts'])  # stable within same ts
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(out) + '\n')
    rows = [json.loads(l) for l in out]
    zero = sum(1 for r in rows for t in r['traders'].values()
               for p in t['positions'] if not p.get('mark'))
    print(f'[marks_union] {path}: |A|={len(la)} |B|={len(lb)} union={len(out)} '
          f'(byte-dup dropped {len(la) + len(lb) - len(out)}) zero-mark evidence rows kept={zero} '
          f'last tick ts={rows[-1]["ts"]}')

take_new('results/fundamental_b_layer_filter.json',
         '32840840ec4fd6b975b9cabdee0366ade1c9667c', 'ea44bbb64fe9832569882015b112b7c1437a7771')
take_new('results/_attrition_guard_scan.json',
         '5ba4dd8ebe79263dc3baff8f242fb29e2cf6cc38', 'a95c457d795452a754925221727d4fd358736b41')
twin('docs/daily_report/REPORT-2026-09-30.json',
     '0b3774fedf02e970bec1e5dd75d53edb668ba77d', '3b8846f533ccc145fc1c1f894931a0be7f79590b',
     [('docs/daily_report/REPORT-2026-09-30.md',
       '6f53226a0d6c5a6ef195fd55d853f93f7a4269a1', '614966d689756658fbbe04453afe3ede3d3820e4')])
twin('docs/live_usage/LIVE-2026-09-30.json',
     '4fa1cdf70292e32f3b09c3f43105949f268b9d4c', 'df1d8cc9ff6359b03a8a14c23a0f5042e7b01637',
     [('docs/live_usage/LIVE-2026-09-30.md',
       '666e1c04726a1039b28abc2f878eab363eb97f06', '03572f52943b6a688157967417a9aa3965c3eb63'),
      ('docs/live_usage/LIVE-latest.json',
       '4fa1cdf70292e32f3b09c3f43105949f268b9d4c', 'df1d8cc9ff6359b03a8a14c23a0f5042e7b01637'),
      ('docs/live_usage/LIVE-latest.md',
       '666e1c04726a1039b28abc2f878eab363eb97f06', '03572f52943b6a688157967417a9aa3965c3eb63')])
marks_union('results/paper/marks/marks-20260930.jsonl',
            '53e0554d94e3a2aac59b6aee87808001b887e5ab', '61cced5ce05a74f13b09d0f69d6c44751560b9cb')
print('resolve batch-2 done')
