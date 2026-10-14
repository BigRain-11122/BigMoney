"""r992 bm-a rebase conflict resolver (estate pick onto bm-b r1000 base).
Canonical recipes per bigmoney-conflict-resolve skill:
- twin-regen-md (3 pairs): json deep-probe generated_at pick side -> md byte-copy SAME side (r327/r329)
- snapshot take-new by deep ts (attrition scan / fundamental_b_layer / prospect summary)
- host-authority faces (strategy_scorecard/scorecard_v1/dashboard json+js = bm-a sole writer r378): take stage-3 local
- stage law r351: :2: = origin/base side, :3: = local side during rebase
- parse-verify before write; tie -> stage2 (r140 take-HEAD)
Receipt -> results/_r992bma_resolve_receipt.json
"""
import subprocess, json, hashlib, sys, io

def stage_bytes(path, stage):
    return subprocess.check_output(['git', 'show', ':%d:%s' % (stage, path)])

TS_KEYS = ['generated_at', 'ts', 'generated', 'asof', 'updated_at', 'clock_read', 'last_seen']

def deep_ts(obj, depth=0):
    if depth > 4 or obj is None:
        return None
    if isinstance(obj, dict):
        for k in TS_KEYS:
            if k in obj and isinstance(obj[k], str) and obj[k]:
                return obj[k]
        for k in TS_KEYS:
            if k in obj and isinstance(obj[k], (int, float)):
                return str(obj[k])
        for v in obj.values():
            r = deep_ts(v, depth + 1)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = deep_ts(v, depth + 1)
            if r:
                return r
    return None

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

receipt = {'machine': 'bm-a', 'round': 992, 'files': {}}

def resolve_snapshot(path, prefer_local=False):
    b2, b3 = stage_bytes(path, 2), stage_bytes(path, 3)
    try:
        j2, j3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    except Exception as e:
        receipt['files'][path] = {'verdict': 'PARSE-FAIL', 'error': str(e)}
        return False
    t2, t3 = deep_ts(j2), deep_ts(j3)
    if prefer_local:
        side, pick, ts = 3, j3, t3
        reason = 'host-authority bm-a sole writer r378'
    else:
        if t3 is not None and t2 is not None:
            side, pick, ts = (3, j3, t3) if t3 > t2 else (2, j2, t2)
            reason = 'snapshot take-new deep-ts (%s vs %s)' % (t2, t3)
        elif t3 is not None:
            side, pick, ts, reason = 3, j3, t3, 'stage2 no-ts, stage3 has ts'
        elif t2 is not None:
            side, pick, ts, reason = 2, j2, t2, 'stage3 no-ts, stage2 has ts'
        else:
            side, pick, ts, reason = 2, j2, None, 'no ts both sides, tie->stage2 (r140)'
    out = json.dumps(pick, ensure_ascii=False, indent=1).encode('utf-8')
    json.loads(out.decode('utf-8'))  # parse-verify written form
    with open(path, 'wb') as f:
        f.write(out)
    receipt['files'][path] = {'verdict': 'RESOLVED', 'side': side, 'ts': ts,
                              'reason': reason, 'sha16_out': sha16(out),
                              'sha16_s2': sha16(b2), 'sha16_s3': sha16(b3)}
    return True

def resolve_twin(json_path, md_path):
    b2, b3 = stage_bytes(json_path, 2), stage_bytes(json_path, 3)
    j2, j3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    t2, t3 = deep_ts(j2), deep_ts(j3)
    if t3 is not None and t2 is not None and t3 > t2:
        side, jb = 3, b3
    else:
        side, jb = 2, b2  # tie or stage2 newer -> stage2 (r140 take-HEAD on tie)
    md = stage_bytes(md_path, side)
    with open(json_path, 'wb') as f:
        f.write(jb)
    with open(md_path, 'wb') as f:
        f.write(md)
    receipt['files'][json_path] = {'verdict': 'RESOLVED', 'side': side,
                                  'reason': 'twin json ts-diffpick whole-byte (t2=%s t3=%s)' % (t2, t3),
                                  'sha16_out': sha16(jb)}
    receipt['files'][md_path] = {'verdict': 'RESOLVED', 'side': side,
                                  'reason': 'twin md byte-copy from same side (r329 no-json-parse)',
                                  'sha16_out': sha16(md)}

ok = True
# 3 twin pairs
resolve_twin('docs/daily_report/REPORT-2026-10-14.json', 'docs/daily_report/REPORT-2026-10-14.md')
resolve_twin('docs/live_usage/LIVE-2026-10-14.json', 'docs/live_usage/LIVE-2026-10-14.md')
resolve_twin('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')
# snapshots take-new
for p in ['results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json',
          'results/prospect_promotion/_summary.json']:
    ok = resolve_snapshot(p) and ok
# host-authority faces: bm-a sole writer (strategy_scorecard chain + dashboard status chain)
for p in ['results/strategy_scorecard.json', 'results/scorecard_v1.json',
          'results/dashboard_status.json']:
    ok = resolve_snapshot(p, prefer_local=True) and ok
# js wrapper: byte-take SAME side as dashboard_status.json decision (R209: no json.dumps unwrap)
dside = receipt['files']['results/dashboard_status.json']['side']
jsb = stage_bytes('results/dashboard_status.js', dside)
with open('results/dashboard_status.js', 'wb') as f:
    f.write(jsb)
receipt['files']['results/dashboard_status.js'] = {'verdict': 'RESOLVED', 'side': dside,
    'reason': 'js-wrapper byte-take same side as dashboard_status.json (R209)', 'sha16_out': sha16(jsb)}

with open('results/_r992bma_resolve_receipt.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('resolver done, parse-fail:', [k for k, v in receipt['files'].items() if v['verdict'] != 'RESOLVED'])
sys.exit(0 if ok else 2)
