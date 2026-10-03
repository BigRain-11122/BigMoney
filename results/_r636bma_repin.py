"""r636 bm-a: re-install divlowvol division pin (post-rebase loss) on both fuse faces."""
import json
import subprocess
import sys

DIV_NOTE = ("keep blocked on bm-a r636: double-burn containment pin -- rightful burner bm-b "
            "2000-draw in flight (r617-r620/r622/r629 division, MSG-1132/1155); 5th double-burn "
            "incident 18:38 claim auto-cleared this pin via code_changed (r626d runner edit made "
            "sha stale, r617 boundary); clear ONLY if bm-b burn dies AND bm-b lane yields")

ok = []
for fp in (r'results\crash_fuse.json', r'results\crash_fuse.bm-a.json'):
    data = open(fp, 'rb').read()
    crlf = data.count(b'\r\n')
    lf = data.count(b'\n')
    eol = b'\r\n' if crlf * 2 > lf else b'\n'
    cf = json.loads(data.decode('utf-8'))
    if cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls', {}).get('code_sha256') == '6d49f8ec7b5a2118':
        ok.append(f'{fp}: pin already present')
        continue
    qanchor = b'"scripts/fund_quality_p1.py|run,--nulls": {'
    qi = data.find(qanchor)
    assert qi > 0, f'{fp}: quality anchor missing'
    ls = data.rfind(eol, 0, qi) + len(eol)
    indent = data[ls:qi]
    pin_lines = [
        b'"scripts/fund_divlowvol_p1.py|run,--nulls": {',
        b'"count": 0,',
        b'"refusals": 0,',
        b'"code_sha256": "6d49f8ec7b5a2118",',
        b'"entry": "FUND-DIVLOWVOL-P1-NULLS",',
        b'"shard": "fund-divlowvol-p1-nulls-0of1",',
        b'"machine": "bm-a",',
        b'"note": "' + DIV_NOTE.encode() + b'"',
        b'},',
    ]
    pin = eol.join(indent + l for l in pin_lines) + eol
    nd = data[:qi] + pin + data[qi:]
    json.loads(nd.decode('utf-8'))
    open(fp, 'wb').write(nd)
    after = json.loads(open(fp, encoding='utf-8').read())
    d = after['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls', {})
    assert d.get('code_sha256') == '6d49f8ec7b5a2118', 'pin missing after write'
    v = after['sigs'].get('scripts/fund_value_p1.py|run,--nulls', {})
    assert v.get('last_refusal_ts'), 'value last_refusal_ts lost'
    r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    ok.append(f'{fp}: pin re-installed | numstat {r.stdout.strip()}')
print('\n'.join(ok))
sys.exit(0)
