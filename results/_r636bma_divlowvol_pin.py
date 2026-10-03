"""r636 bm-a: divlowvol claim release + division-pin install (fuse) + value-sig note.

URGENT window before next daemon tick. Byte-surgical edits only (r509), eol
probed per face, json.loads + numstat asserts. Division pins per r616/r617/r625:
sig + current-sha anchor, honest count=0 with division note (r625 law).
"""
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
REL_NOTE = (" | rel-bm-a-r636 18:41: divlowvol double-burn claim released (auto-fill 18:38 "
            "claim after code_changed pin clear, zero rows burned, no launch occurred; "
            "bm-b canonical burn in flight)")


def probe_eol(fp):
    d = open(fp, 'rb').read()
    return d.count(b'\r\n'), d.count(b'\n')


results = []

# ---------- 1) pool faces: release divlowvol claim ----------
for fp in (r'results\runnable_pool.json', r'results\runnable_pool.bm-a.json',
           r'results\runnable_pool.bm-b.json', r'results\runnable_pool.bm-c.json'):
    data = open(fp, 'rb').read()
    crlf, lf = probe_eol(fp)
    KEY = b'"key": "fund-divlowvol-p1-nulls-0of1"'
    i = data.find(KEY)
    if i < 0:
        results.append(f'{fp}: no divlowvol shard (skip)')
        continue
    eol = b'\r\n' if crlf > (lf - crlf) else b'\n'
    end = data.find(b'}' + eol, i)
    block = data[i:end]
    if b'"owner": "bm-a"' not in block or b'18:38:09' not in block:
        results.append(f'{fp}: shard present, no bm-a 18:38:09 claim (skip)')
        continue
    nb = block.replace(b'"owner": "bm-a"', b'"owner": null')
    nb = nb.replace(b'"owner_since": "2026-10-03 18:38:09"', b'"owner_since": null')
    anchor = b'fuse keep-blocked on bm-a",'
    if anchor in nb:
        nb = nb.replace(anchor, b'fuse keep-blocked on bm-a' + REL_NOTE.encode() + b'",', 1)
    nd = data[:i] + nb + data[end:]
    json.loads(nd.decode('utf-8'))
    open(fp, 'wb').write(nd)
    after = open(fp, 'rb').read()
    assert after.count(b'\r\n') == crlf, f'{fp}: eol drift!'
    json.loads(after.decode('utf-8'))
    r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    results.append(f'{fp}: RELEASED | eol ok | numstat {r.stdout.strip()}')

# ---------- 2) fuse faces: install divlowvol division pin + value note ----------
for fp in (r'results\crash_fuse.json', r'results\crash_fuse.bm-a.json'):
    data = open(fp, 'rb').read()
    crlf, lf = probe_eol(fp)
    eol = b'\r\n' if crlf > (lf - crlf) else b'\n'
    nl = eol
    IND = b' ' * (4 if b'\r\n    "' in data or b'\n    "' in data else 1)
    sigs_open = data.find(b'"sigs": {')
    assert sigs_open > 0, f'{fp}: no sigs section'

    # a) divlowvol pin: insert before quality sig entry
    qanchor = b'"scripts/fund_quality_p1.py|run,--nulls": {'
    qi = data.find(qanchor, sigs_open)
    assert qi > 0, f'{fp}: quality sig anchor missing'
    # probe indent of the quality sig line
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
        (b'"note": "' + DIV_NOTE.encode() + b'"'),
        b'},',
    ]
    pin = eol.join(indent + ln if ln != b'},' else indent + b'},' for ln in pin_lines)
    pin = eol.join(indent + l for l in pin_lines) + eol
    nd = data[:qi] + pin + data[qi:]
    # b) value sig: append/refresh note (anchor on its shard field line inside value sig block)
    vsig = b'"scripts/fund_value_p1.py|run,--nulls": {'
    vi = nd.find(vsig, sigs_open)
    assert vi > 0, f'{fp}: value sig not found'
    vend = nd.find(b'}', vi)
    vblock = nd[vi:vend]
    if b'"note"' not in vblock:
        if not vblock.rstrip().endswith(b','):
            # make preceding field end with comma then append note line
            vblock2 = vblock.rstrip() + b',' + nl
        else:
            vblock2 = vblock
        vindent = indent
        vnb = (b'"note": "' + VAL_NOTE.encode() + b'"')
        vend2 = nd.find(b'}', vi)
        pre = nd[vi:vend2]
        # find last field line indent
        lasteol = pre.rfind(eol)
        pre2 = pre[:lasteol].rstrip()
        if not pre2.endswith(b','):
            pre2 = pre2 + b','
        newline_block = pre2 + eol + indent + vnb + eol + indent
        nd = nd[:vi] + newline_block + nd[vend2:]
    json.loads(nd.decode('utf-8'))
    open(fp, 'wb').write(nd)
    after = open(fp, 'rb').read()
    assert after.count(b'\r\n') == crlf, f'{fp}: eol drift!'
    cf = json.loads(after.decode('utf-8'))
    assert cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls', {}).get('code_sha256') == '6d49f8ec7b5a2118'
    vs = cf['sigs'].get('scripts/fund_value_p1.py|run,--nulls', {})
    assert 'keep blocked on bm-a r636' in (vs.get('note') or '')
    r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    results.append(f'{fp}: divlowvol pin + value note installed | numstat {r.stdout.strip()}')

print('\n'.join(results))
print('ALL DONE')
sys.exit(0)
