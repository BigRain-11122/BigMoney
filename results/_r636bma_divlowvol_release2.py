"""r636 bm-a: divlowvol pool release redo with verbose diagnostics."""
import json
import subprocess

REL_NOTE = (" | rel-bm-a-r636 18:4x: divlowvol double-burn claim released (autofill 18:38 "
            "claim after code_changed pin clear, zero rows burned, no launch; "
            "bm-b canonical burn in flight)")

for fp in (r'results\runnable_pool.json', r'results\runnable_pool.bm-a.json'):
    data = open(fp, 'rb').read()
    crlf = data.count(b'\r\n')
    lf = data.count(b'\n')
    eol = b'\r\n' if crlf > (lf - crlf) else b'\n'
    print(f'{fp}: eol={eol!r} crlf={crlf} lf={lf}')
    KEY = b'"key": "fund-divlowvol-p1-nulls-0of1"'
    i = data.find(KEY)
    print(f'  key offset: {i}')
    end = data.find(b'}' + eol, i)
    block = data[i:end]
    print(f'  block len: {len(block)}')
    has_owner = b'"owner": "bm-a"' in block
    has_ts = b'18:38:09' in block
    print(f'  owner-bm-a in block: {has_owner} | 18:38:09 in block: {has_ts}')
    if not (has_owner and has_ts):
        print('  SKIP (no claim in block)')
        continue
    nb = block.replace(b'"owner": "bm-a"', b'"owner": null')
    nb = nb.replace(b'"owner_since": "2026-10-03 18:38:09"', b'"owner_since": null')
    anchor = b'fuse keep-blocked on bm-a",'
    if anchor in nb and b'rel-bm-a-r636' not in nb:
        nb = nb.replace(anchor, b'fuse keep-blocked on bm-a' + REL_NOTE.encode() + b'",', 1)
        print('  note appended')
    nd = data[:i] + nb + data[end:]
    json.loads(nd.decode('utf-8'))
    open(fp, 'wb').write(nd)
    after = open(fp, 'rb').read()
    json.loads(after.decode('utf-8'))
    bare_lf = after.count(b'\n') - after.count(b'\r\n')
    r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    print(f'  RELEASED | bare-LF introduced: {bare_lf} | numstat: {r.stdout.strip()}')
