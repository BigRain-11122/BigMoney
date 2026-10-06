import subprocess, json, sys, re, os

# r800 bm-b rebase conflict resolver v2 (skill: bigmoney-conflict-resolve)
# ours(stage2) = origin/main side (bm-a r811 churn-absorb window)
# theirs(stage3) = replayed bm-b r799/r800 commit side (bm-b live daemon state)
# Recipes: .jsonl=append-log line union; ledgers=union rows; snapshots=take-new-by-ts;
#          bm-b-owned single-writer faces=take-new-by-ts with theirs fallback;
#          js-wrapper=take-side whole bytes; md twins follow their json twin.

TS_KEYS = ['generated', 'updated', 'ts', 'scanned_at', 'asof', 'last_run', 'generated_at', 'time', 'tick_ts']

def stage_bytes(p, n):
    r = subprocess.run(['git', 'show', f':{n}:{p}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def uu_list():
    out = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout
    return [l[3:] for l in out.splitlines() if l.startswith('UU ') or l.startswith('AA ')]

def find_ts(obj):
    if not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        if k in obj and isinstance(obj[k], str):
            return obj[k]
    for k, v in obj.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if k2 in TS_KEYS and isinstance(v2, str):
                    return v2
    return None

def row_ts(row):
    if isinstance(row, dict):
        for k in TS_KEYS:
            if k in row and isinstance(row[k], str):
                return row[k]
    return None

def union_rows(ours_rows, theirs_rows):
    seen, merged, added = set(), [], 0
    for r in ours_rows:
        key = json.dumps(r, sort_keys=True, ensure_ascii=True)
        if key not in seen:
            seen.add(key); merged.append(r)
    for r in theirs_rows:
        key = json.dumps(r, sort_keys=True, ensure_ascii=True)
        if key not in seen:
            seen.add(key); merged.append(r); added += 1
    if merged and all(row_ts(r) for r in merged):
        merged = sorted(merged, key=row_ts)
    return merged, added

def union_lines(ob, tb):
    ol = ob.decode('utf-8', errors='replace').splitlines()
    tl = tb.decode('utf-8', errors='replace').splitlines()
    seen, merged, added = set(), [], 0
    for l in ol:
        s = l.strip()
        if s and s not in seen:
            seen.add(s); merged.append(l)
    for l in tl:
        s = l.strip()
        if s and s not in seen:
            seen.add(s); merged.append(l); added += 1
    return ('\n'.join(merged) + '\n').encode('utf-8'), added, len(merged)

def resolve_ledger(path):
    o = json.loads(stage_bytes(path, 2).decode('utf-8'))
    t = json.loads(stage_bytes(path, 3).decode('utf-8'))
    res = dict(o)
    notes = []
    union_added = 0
    for k in sorted(set(list(o.keys()) + list(t.keys()))):
        ov, tv = o.get(k), t.get(k)
        if isinstance(ov, list) and isinstance(tv, list) and ov and isinstance(ov[0], dict):
            merged, added = union_rows(ov, tv)
            res[k] = merged; union_added += added
        else:
            ot, tt = find_ts(ov) or '', find_ts(tv) or ''
            if tt > ot:
                res[k] = tv; notes.append(f'{k}: take-new(theirs)')
            else:
                res[k] = ov if ov is not None else tv; notes.append(f'{k}: keep-ours')
    return res, notes, union_added

def resolve_snapshot(path, bm_b_owned):
    ob, tb = stage_bytes(path, 2), stage_bytes(path, 3)
    try:
        o = json.loads(ob.decode('utf-8')); t = json.loads(tb.decode('utf-8'))
    except Exception as e:
        return None, None, f'PARSE FAIL {e}'
    ot, tt = find_ts(o) or '', find_ts(t) or ''
    if tt > ot:
        return t, tb, f'take-new theirs (ts {tt[:19]} > {ot[:19]})'
    if ot > tt:
        return o, ob, f'keep ours (ts {ot[:19]} > {tt[:19]})'
    # tie or no ts: bm-b-owned single-writer face -> theirs (bm-b live state authority)
    if bm_b_owned:
        return t, tb, 'no-ts-diff -> take theirs (bm-b owned live face)'
    return o, ob, f'tie/no-ts -> keep ours ({ot[:19]})'

LEDGERS = ['results/compute_audit.json', 'results/regime_state.json']
JS_WRAP = ['results/dashboard_status.js']
MIXED = ['results/autofill_state.bm-b.json']  # launches union/cap50/re-sort asc + last_tick take-new (r203/R208/r245 law)
BM_B_OWNED = ('_bm-b', '.bm-b.')

def resolve_mixed(path):
    o = json.loads(stage_bytes(path, 2).decode('utf-8'))
    t = json.loads(stage_bytes(path, 3).decode('utf-8'))
    res = dict(o)
    notes = []
    ol, tl = o.get('launches', []), t.get('launches', [])
    merged, added = union_rows(ol, tl)
    # cap semantics: keep newest 50 by ts desc, then write back ts ascending (r245 law)
    merged.sort(key=lambda r: row_ts(r) or '', reverse=True)
    merged = merged[:50]
    merged.sort(key=lambda r: row_ts(r) or '')
    res['launches'] = merged
    notes.append(f'launches union+{added} cap50 asc ({len(merged)})')
    # last_tick: compare internal ts, whole dict assign (r140 tie -> HEAD/ours)
    ot = (o.get('last_tick') or {}).get('ts', '')
    tt = (t.get('last_tick') or {}).get('ts', '')
    if tt > ot:
        res['last_tick'] = t.get('last_tick'); notes.append(f'last_tick take-new(theirs {tt[:19]})')
    else:
        res['last_tick'] = o.get('last_tick'); notes.append(f'last_tick keep-ours({ot[:19]})')
    assert isinstance(res['last_tick'], dict), 'last_tick must be dict (r220 law)'
    # other keys: take-new by ts else ours
    for k in set(list(o.keys()) + list(t.keys())):
        if k in ('launches', 'last_tick'):
            continue
        ov, tv = o.get(k), t.get(k)
        ot2, tt2 = find_ts(ov) or '', find_ts(tv) or ''
        res[k] = tv if tt2 > ot2 else (ov if ov is not None else tv)
    # newline mirror from ours blob
    ob = stage_bytes(path, 2)
    crlf = b'\r\n' in ob
    text = json.dumps(res, ensure_ascii=False, indent=1) + '\n'
    blob = text.replace('\n', '\r\n').encode('utf-8') if crlf else text.encode('utf-8')
    return blob, '; '.join(notes)

def main():
    uus = uu_list()
    if not uus:
        print('NO UU/AA conflicts found'); return 0
    verdicts = {}
    for p in uus:
        if p in MIXED:
            blob, note = resolve_mixed(p)
            with open(p, 'wb') as f:
                f.write(blob)
            verdicts[p] = f'mixed-dict+ledger: {note}'
        elif p.endswith('.jsonl'):
            blob, added, total = union_lines(stage_bytes(p, 2), stage_bytes(p, 3))
            with open(p, 'wb') as f:
                f.write(blob)
            verdicts[p] = f'append-log line union +{added} -> {total} lines'
        elif p in LEDGERS:
            res, notes, added = resolve_ledger(p)
            blob = (json.dumps(res, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
            with open(p, 'wb') as f:
                f.write(blob)
            verdicts[p] = f'ledger-union rows+{added}; ' + '; '.join(notes[:4])
        elif p in JS_WRAP:
            ob, tb = stage_bytes(p, 2), stage_bytes(p, 3)
            ot = re.search(r'"ts"\s*:\s*"([^"]+)"', ob.decode('utf-8', errors='replace'))
            tt = re.search(r'"ts"\s*:\s*"([^"]+)"', tb.decode('utf-8', errors='replace'))
            ots, tts = ot.group(1) if ot else '', tt.group(1) if tt else ''
            blob = tb if tts > ots else ob
            with open(p, 'wb') as f:
                f.write(blob)
            verdicts[p] = f'js-wrapper take-side {"theirs" if tts > ots else "ours"} (ts {max(ots, tts)[:19]})'
        elif p.endswith('.md'):
            base = p[:-3]
            jv = verdicts.get(base + '.json') or verdicts.get(base.replace('LIVE-latest', 'LIVE-2026-10-07') + '.json')
            side = 3 if (jv and 'theirs' in jv) else 2
            blob = stage_bytes(p, side)
            with open(p, 'wb') as f:
                f.write(blob)
            verdicts[p] = f'md-twin take side {side} (follows json twin)'
        else:
            owned = BM_B_OWNED[0] in os.path.basename(p) or BM_B_OWNED[1] in os.path.basename(p)
            res, raw, note = resolve_snapshot(p, owned)
            if res is None:
                print(f'MANUAL REQUIRED: {p}: {note}'); return 2
            blob = raw if (note.startswith('no-ts-diff') or note.startswith('tie')) else (json.dumps(res, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
            with open(p, 'wb') as f:
                f.write(blob)
            verdicts[p] = note + (' [bm-b-owned]' if owned else '')
    for p in verdicts:
        if p.endswith('.json'):
            json.loads(open(p, encoding='utf-8').read())
    for p in verdicts:
        subprocess.run(['git', 'add', p], capture_output=True)
    for p, v in verdicts.items():
        print(f'{p} :: {v}')
    with open('results/_r800bmb_resolve_receipt.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'batch': [{'path': p, 'verdict': v} for p, v in verdicts.items()]}, ensure_ascii=False) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
