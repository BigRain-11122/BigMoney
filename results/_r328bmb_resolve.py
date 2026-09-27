# -*- coding: utf-8 -*-
"""r328 bm-b push-collision canon resolve (4 UU, classifier GREEN 0 UNKNOWN).

Sides: stage1=base dd34727b, stage2=ours=HEAD=bm-a ef92ff78 (landed first),
stage3=theirs=bmb 07f65450 (replayed, late-comer yields order).

Recipes (SKILL.md + classifier output):
- CODELY.md            memory-union: base + bm-a new line + bmb new line (commit-time order), dedupe identical, <10KB assert
- autofill_state.json  mixed-dict+ledger: launches composite-key (ts,machine,pid,runner_sha256,entry,shard)
                       field-union dedup (r322/r83: present beats absent; conflicting non-null = flag), sort desc cap 50,
                       re-sort asc for write-back; last_tick newer-ts whole-dict (r140); CRLF mirror base (r223); indent=1
- compute_audit.json   rolling-ledger: history union by ts zero-loss, sort ts asc; latest take-new by ts;
                       producer recipe json.dump({"latest","history"}, indent=2, ensure_ascii=False) CRLF
- regime_state.json    only 'updated' differs (14:04:26 newer) -> take stage3 bytes verbatim (CRLF already)
Verification (r185): parse-verify before write-back; zero-loss line/key counts; isinstance(last_tick,dict).
"""
import io
import json
import subprocess
import sys

BLOBS = {
    'codely': ('d71db210e12ab2775856f3dd6d581ba6672beefa', 'f839b8aa41ed93141f8bb84f707d422983fb684a', 'e8ede267ab88be048e9c6962df2749a5d645bb2d'),
    'autofill': ('6ba831dffa39989f4b3599b58eb6a11a9bb64fcf', 'f285dd88d421362d61a5f035da785eba395dc84a', 'c85b1d455bd433f8e4f379aa1679b53bd2da7851'),
    'audit': ('e0de731b008cb3496325a59bfb1d445924ff8aa6', '247eac38e04e0060c6a73e94524c5dd80d492a2e', '2003b12bdd7d722cd933bae2046b930a5819266b'),
    'regime': ('84122e73a54d4cd73d9b6dcc52715001db73ac34', '9de12c77c137791bc6c4c6895263b33560837e21', '766c1c1cbb506de73411b4c9e3db1410e1ccd609'),
}

def blob(sha):
    return subprocess.run(['git', 'cat-file', 'blob', sha], capture_output=True).stdout

def resolve_codely():
    b1, b2, b3 = (blob(s) for s in BLOBS['codely'])
    l1, l2, l3 = (b.decode('utf-8').splitlines() for b in (b1, b2, b3))
    base_set = set(l1)
    a_new = [x for x in l2 if x not in base_set]      # bm-a's new line(s)
    b_new = [x for x in l3 if x not in base_set]      # bmb's new line(s)
    assert len(a_new) == 1 and len(b_new) == 1, (a_new, b_new)
    resolved = l1 + a_new + b_new                     # late-comer (bmb) appends after landed-first (bm-a)
    out = ('\n'.join(resolved) + '\n').encode('utf-8')
    assert len(out) < 10240, len(out)                 # 10KB hard line
    assert out.count(b'\r\n') == 0
    with open('CODELY.md', 'wb') as f:
        f.write(out)
    # verify: union contains both sides verbatim
    chk = open('CODELY.md', 'rb').read()
    assert chk == out and a_new[0].encode() in chk and b_new[0].encode() in chk
    print('CODELY.md union: %d bytes (bm-a line + bmb line), <10KB' % len(chk))

def key6(e):
    return (e['ts'], e['machine'], e['pid'], e['runner_sha256'], e['entry'], e['shard'])

def resolve_autofill():
    b1, b2, b3 = (blob(s) for s in BLOBS['autofill'])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    m2 = {key6(e): e for e in d2['launches']}
    m3 = {key6(e): e for e in d3['launches']}
    # composite-key field-union (r322/r83): present beats absent; conflicting non-null = flag
    merged, flags = {}, []
    for k in set(m2) | set(m3):
        e2, e3 = m2.get(k), m3.get(k)
        if e2 is None:
            merged[k] = e3
            continue
        if e3 is None:
            merged[k] = e2
            continue
        u = dict(e2)
        for f, v in e3.items():
            if f not in u or u[f] is None:
                u[f] = v
            elif u[f] != v and v is not None:
                flags.append((k, f, u[f], v))       # true divergence -> flagged, not silent double-store
        merged[k] = u
    lst = sorted(merged.values(), key=lambda e: e['ts'], reverse=True)[:50]   # cap 50 newest (R215)
    lst.sort(key=lambda e: e['ts'])                                            # write-back ascending (r245)
    # last_tick: newer inner ts wins whole-dict (r140); tie -> HEAD/stage2
    lt2, lt3 = d2['last_tick'], d3['last_tick']
    last_tick = lt3 if lt3['ts'] > lt2['ts'] else lt2
    assert isinstance(last_tick, dict)
    out = json.dumps({'launches': lst, 'last_tick': last_tick}, ensure_ascii=False, indent=1)
    data = out.encode('utf-8').replace(b'\n', b'\r\n')                         # CRLF mirror base (r223)
    with open('results/autofill_state.json', 'wb') as f:
        f.write(data)
    chk = json.loads(io.open('results/autofill_state.json', encoding='utf-8').read())
    assert isinstance(chk['last_tick'], dict) and len(chk['launches']) == len(lst)
    assert {key6(e) for e in chk['launches']} >= (set(m2) & set(m3))
    print('autofill_state: union %d entries (cap50 kept %d), last_tick ts=%s, flags=%d'
          % (len(merged), len(lst), chk['last_tick']['ts'], len(flags)))
    for fl in flags:
        print('  TRUE-DIVERGENCE-FLAG', fl)

def resolve_audit():
    b2, b3 = (blob(s) for s in BLOBS['audit'][1:])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    h2 = {e['ts']: e for e in d2['history']}
    h3 = {e['ts']: e for e in d3['history']}
    union = dict(h2)
    diverged = 0
    for ts, e in h3.items():
        if ts in union and union[ts] != e:
            diverged += 1                            # same ts different content
            u = dict(union[ts]); u.update({k: v for k, v in e.items()})
            union[ts] = u
        else:
            union[ts] = e
    hist = sorted(union.values(), key=lambda e: e['ts'])
    latest = d3['latest'] if d3['latest']['ts'] >= d2['latest']['ts'] else d2['latest']
    assert len(hist) == len(set(h2) | set(h3)), (len(hist), len(set(h2) | set(h3)))   # zero-loss
    with open('results/compute_audit.json', 'w', encoding='utf-8', newline='') as f:
        json.dump({'latest': latest, 'history': hist}, f, indent=2, ensure_ascii=False)
    raw = open('results/compute_audit.json', 'rb').read()
    # producer writes text-mode CRLF on Windows; replicate
    if raw.count(b'\r\n') == 0:
        raw = raw.replace(b'\n', b'\r\n')
        with open('results/compute_audit.json', 'wb') as f:
            f.write(raw)
    chk = json.loads(io.open('results/compute_audit.json', encoding='utf-8').read())
    assert len(chk['history']) == len(set(h2) | set(h3)) and chk['latest']['ts'] == latest['ts']
    print('compute_audit: history union %d rows (zero-loss |A u B|=%d, same-ts field merges=%d), latest ts=%s, CRLF=%d'
          % (len(chk['history']), len(set(h2) | set(h3)), diverged, chk['latest']['ts'],
             open('results/compute_audit.json', 'rb').read().count(b'\r\n')))

def resolve_regime():
    b2, b3 = (blob(s) for s in BLOBS['regime'][1:])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    diffs = [k for k in set(d2) | set(d3) if d2.get(k) != d3.get(k)]
    assert diffs == ['updated'], diffs               # only 'updated' differs; theirs (14:04:26) is newer
    assert d3['updated'] > d2['updated']
    with open('results/regime_state.json', 'wb') as f:
        f.write(b3)                                  # take stage3 whole bytes (CRLF, producer-identical)
    chk = json.loads(io.open('results/regime_state.json', encoding='utf-8').read())
    assert chk['updated'] == d3['updated']
    print("regime_state: take-new 'updated'=%s (stage3 bytes verbatim, CRLF preserved)" % chk['updated'])

if __name__ == '__main__':
    resolve_codely()
    resolve_autofill()
    resolve_audit()
    resolve_regime()
    print('ALL 4 RESOLVED + PARSE-VERIFIED')
