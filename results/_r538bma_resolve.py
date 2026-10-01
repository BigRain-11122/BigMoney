# -*- coding: utf-8 -*-
# r538 bm-a rebase resolver: twin-regen-md families (same-side) + snapshot deep-ts take-new
# Laws: r98/r99/r100 (twins same side), r439bmb (LIVE family all-same-side), R209 (js wrapper whole bytes),
#       r100/R350 hardened ts probe (key normalize, ^20\d{2}- value guard, staged blob not worktree), r185 parse-verify
import subprocess, re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def blob(stage, path):
    # stage = 2 or 3 (int) -> git show :<stage>:<path>
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

def deep_ts(obj, best=''):
    # deep-scan for the newest 20xx- prefixed timestamp value on generated/updated/ts-ish keys
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r'[_\-]', '', str(k)).lower()
            if isinstance(v, str) and re.match(r'^20\d{2}-', v) and any(t in nk for t in ('generated', 'updated', 'ts', 'time', 'asof', 'cutoff')):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def pick_side(path, probe='json'):
    a = blob(2, path)  # rebase: stage2 = upstream bm-c side
    b = blob(3, path)  # stage3 = ours (bm-a r538)
    if probe == 'json':
        try:
            ta, tb = deep_ts(json.loads(a)), deep_ts(json.loads(b))
        except Exception as e:
            print(f'  {path}: json probe failed ({e}) -> raw string scan')
            ta = max(re.findall(rb'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', a)) or b''
            tb = max(re.findall(rb'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', b)) or b''
            ta, tb = ta.decode(), tb.decode()
    else:
        ra = re.findall(rb'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', a)
        rb = re.findall(rb'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', b)
        ta = max(ra).decode() if ra else ''
        tb = max(rb).decode() if rb else ''
    side = 2 if ta >= tb else 3
    print(f'  {path}: ts[stage2]={ta!r} ts[stage3]={tb!r} -> stage {side}')
    return side

def write_side(stage, path, binary_ok=True):
    data = blob(stage, path)
    # line-ending + BOM faithfulness: write raw bytes exactly as the chosen blob
    with open(path, 'wb') as f:
        f.write(data)

print('== twin families: pick ONE side for all members ==')
# REPORT twin
s = pick_side('docs/daily_report/REPORT-2026-10-01.json')
for p in ['docs/daily_report/REPORT-2026-10-01.json', 'docs/daily_report/REPORT-2026-10-01.md']:
    write_side(s, p)
# LIVE family (dated + latest pointers, all same side)
s = pick_side('docs/live_usage/LIVE-2026-10-01.json')
for p in ['docs/live_usage/LIVE-2026-10-01.json', 'docs/live_usage/LIVE-2026-10-01.md',
          'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md']:
    write_side(s, p)
# dashboard twin: probe json, copy js from same side (R209 whole bytes)
s = pick_side('results/dashboard_status.json')
write_side(s, 'results/dashboard_status.json')
write_side(s, 'results/dashboard_status.js')

print('== single snapshots: per-file deep-ts take-new ==')
for p in ['results/fundamental_b_layer_filter.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/_attrition_guard_scan.json']:
    s = pick_side(p)
    write_side(s, p)

print('== parse verify (r185) ==')
ok = True
for p in ['docs/daily_report/REPORT-2026-10-01.json', 'docs/live_usage/LIVE-2026-10-01.json',
          'docs/live_usage/LIVE-latest.json', 'results/dashboard_status.json',
          'results/fundamental_b_layer_filter.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/_attrition_guard_scan.json']:
    try:
        json.load(open(p, encoding='utf-8'))
        print(f'  json.loads OK: {p}')
    except Exception as e:
        ok = False
        print(f'  json.loads FAIL: {p}: {e}')
js = open('results/dashboard_status.js', encoding='utf-8').read()
w = js.startswith('window.DASH_DATA') and js.rstrip().endswith(';')
print('  js wrapper intact:', w)
ok = ok and w
print('RESOLVER RESULT:', 'ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
