import io, re, json
raw = open('results/_r591bmb_s6_runner.log', 'rb').read()
t = None
for enc in ('utf-8', 'gbk', 'utf-16'):
    try:
        t = raw.decode(enc)
        break
    except Exception:
        pass
if t is None:
    t = raw.decode('utf-8', errors='replace')
out = []
for pat in ('ZERO-DRIFT', 'verdict', 'streak', 'no-op', 'skip', 'LAST_BAR', 'spawn', 'consecutive', 'rc=2', 'rc=3'):
    for m in re.finditer(pat, t, re.I):
        s = max(0, m.start() - 100)
        out.append(t[s:m.end() + 110].replace('\n', ' | '))
        break
io.open('results/_r591bmb_s6_keys.txt', 'w', encoding='utf-8').write('\n\n'.join(out))
print('wrote', len(out), 'keys')
# dualrun jsonl tail
try:
    lines = [json.loads(l) for l in io.open('results/pool_dualrun.bm-b.jsonl', encoding='utf-8') if l.strip()]
    last = lines[-1]
    io.open('results/_r591bmb_s6_keys.txt', 'a', encoding='utf-8').write(
        '\n\nDUALRUN_TAIL: ' + json.dumps({k: last.get(k) for k in ('ts', 'status', 'consecutive_green', 'evidence_cutoff', 'drift')}, ensure_ascii=False))
except Exception as e:
    print('dualrun tail err', e)
# watermark verdict
try:
    wl = [json.loads(l) for l in io.open('results/watermark.jsonl', encoding='utf-8') if l.strip()]
    w = wl[-1]
    io.open('results/_r591bmb_s6_keys.txt', 'a', encoding='utf-8').write(
        '\n\nWM_TAIL: ' + json.dumps(w, ensure_ascii=False)[:600])
except Exception as e:
    print('wm tail err', e)
