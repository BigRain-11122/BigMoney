# r969 bm-b S0.5 group probe: param-level reuse of _r968bmb_s05_scan.py.
# Group fetch (capped, tree-kill law r953), hash both ledgers, compare vs
# state watermarks, save fresh views if changed, extract delta @bm-b rows.
# Zero network beyond one fetch. ASCII only. NO_WINDOW per U060.
import hashlib, json, subprocess, time

GROUP = r'C:\Fluxgroup\FluxGroup'
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
STATE = BM + r'\state.json'
OUT = BM + r'\results\_r969bmb_s05_scan.json'
NO_WINDOW = 0x08000000

def run_capped(cmd, cap):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         creationflags=NO_WINDOW)
    try:
        out = p.communicate(timeout=cap)[0].decode('utf-8', 'replace')
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        try:
            p.communicate(timeout=10)
        except Exception:
            pass
        return -99, 'TIMEOUT_%ss' % cap

st = json.load(open(STATE, encoding='utf-8'))
rc, out = run_capped(['git', '-C', GROUP, 'fetch', 'origin'], 120)
res = {'fetch_rc': rc, 'fetch_out_tail': out.strip().splitlines()[-1][:120] if out.strip() else ''}
if rc == 0:
    for key, path, algo in (('orders', 'docs/orders.md', 'sha1'),
                            ('decisions', 'docs/decisions.md', 'sha256')):
        r2, content = run_capped(['git', '-C', GROUP, 'show', 'origin/main:' + path], 90)
        if r2 != 0:
            res[key + '_read_rc'] = r2
            continue
        raw = content.encode('utf-8', 'surrogateescape')
        h = hashlib.sha1(raw).hexdigest() if algo == 'sha1' else hashlib.sha256(raw).hexdigest()
        res[key + '_sha'] = h
        wm = st.get('last_orders_sha') if key == 'orders' else st.get('last_decisions_sha')
        res[key + '_changed'] = (h != wm)
        if h != wm:
            fresh = BM + r'\results\_r969bmb_%s_fresh.md' % key
            with open(fresh, 'wb') as f:
                f.write(raw)
            rows = [l for l in content.splitlines() if ('bm-b' in l.lower())]
            res[key + '_bmb_delta_rows'] = rows[-40:]
    res['verdict'] = ('NO_DELTA_ZERO_ACTION' if not res.get('orders_changed', False)
                      and not res.get('decisions_changed', False) else 'DELTA_PRESENT')
else:
    res['verdict'] = 'FETCH_FAIL_NONBLOCKING'
res['ts'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if not isinstance(v, list) else '(%d rows)' % len(v))
                  for k, v in res.items()}, ensure_ascii=False, indent=1))
