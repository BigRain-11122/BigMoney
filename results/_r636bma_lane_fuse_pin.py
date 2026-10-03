"""r636 bm-a: lane fuse face (crash_fuse.bm-a.json) pin install — byte-surgical."""
import json
import subprocess
import sys

DIV_NOTE = ("keep blocked on bm-a r636: double-burn containment pin -- rightful burner bm-b "
            "2000-draw in flight (r617-r620/r622/r629 division, MSG-1132/1155); 5th double-burn "
            "incident 18:38 claim auto-cleared this pin via code_changed (r626d runner edit made "
            "sha stale, r617 boundary); clear ONLY if bm-b burn dies AND bm-b lane yields")
VAL_NOTE = ("keep blocked on bm-a r636: double-burn containment pin (re-armed post 5th incident "
            "18:16-18:38: autofill claim after code_changed auto-clear of stale-sha pin, burn "
            "killed 18:52 tree-sweep r618, 50 rows discarded, file restored origin-verbatim); "
            "rightful burner bm-b in flight per MSG-1132/1155; clear ONLY if bm-b burn dies AND "
            "bm-b lane yields")

fp = r'results\crash_fuse.bm-a.json'
data = open(fp, 'rb').read()
crlf = data.count(b'\r\n')
lf = data.count(b'\n')
eol = b'\r\n' if crlf * 2 > lf else b'\n'
print('lane fuse eol:', eol, '| crlf:', crlf, '| lf:', lf)

sigs_open = data.find(b'"sigs": {')
assert sigs_open > 0
qanchor = b'"scripts/fund_quality_p1.py|run,--nulls": {'
qi = data.find(qanchor, sigs_open)
assert qi > 0, 'quality anchor missing'
ls = data.rfind(eol, 0, qi) + len(eol)
indent = data[ls:qi]
print('sig entry indent:', repr(indent))

# divlowvol pin insert before quality sig
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

# value sig note (append as new field line before closing brace, keep ALL existing fields)
vsig = b'"scripts/fund_value_p1.py|run,--nulls": {'
vi = nd.find(vsig, sigs_open)
assert vi > 0, 'value sig missing on lane face'
vend = nd.find(b'}', vi)
pre = nd[vi:vend]
if b'"note"' not in pre:
    lasteol = pre.rfind(eol)
    lastline = pre[lasteol + len(eol):]
    fixed = lastline.rstrip()
    if not fixed.endswith(b','):
        fixed = fixed + b','
    nb = (pre[:lasteol + len(eol)] + fixed + eol + indent
          + b'"note": "' + VAL_NOTE.encode() + b'"')
    nd = nd[:vi] + nb + nd[vend:]
    print('value note appended (all fields preserved)')

json.loads(nd.decode('utf-8'))
open(fp, 'wb').write(nd)
after = open(fp, 'rb').read()
cf = json.loads(after.decode('utf-8'))
d = cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls')
assert d and d.get('code_sha256') == '6d49f8ec7b5a2118', 'divlowvol pin missing after write'
v = cf['sigs'].get('scripts/fund_value_p1.py|run,--nulls')
assert v and 'r636' in (v.get('note') or ''), 'value note missing'
assert v.get('last_refusal_ts'), 'value last_refusal_ts LOST'
bare_lf_after = after.count(b'\n') - after.count(b'\r\n')
bare_lf_before = lf - crlf
print('bare-LF before/after:', bare_lf_before, '/', bare_lf_after)
r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                   text=True, encoding='utf-8', errors='replace')
print('numstat:', r.stdout.strip())
print('LANE FUSE OK')
sys.exit(0)
