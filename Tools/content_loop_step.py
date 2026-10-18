"""CONTENT-LOOP v0.1 queue engine (drama line, bm-b host).

Blueprint: cph4/fleet/CONTENT-OS-LOOP-BLUEPRINT-v1.md sec.3 (20-30min loop,
queue-ledger self-claim, five-piece gates stay in-loop, director step-gate,
CEO terminal review only). Order refs: O-20261018-2144-bm-c sec.2.1,
O-20261018-2236-bm-c (10-min idle SLA).

Commands:
  round   -- locked scan -> claim first runnable station -> execute runner ->
             regenerate QUEUE.md face -> book round row. Emits one JSON line.
  scan    -- read-only verdict (no claim, no write).
  selftest -- offline assertions.

Machine ledger = content/drama/queue.json (single-writer via pid+age lock,
FleetLink worker v1.6 law). QUEUE.md is a regenerated human face, never hand-
edited. Claims append to content/drama/CLAIMS.jsonl (append-only). Round rows
append to content/drama/ROUND-LOG.md. Loop state = content/drama/loop_state.json.
All writes fresh-read-modify-write inside the lock (r1006 multi-writer law).
"""
import io
import json
import os
import subprocess
import sys
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, 'content', 'drama')
QPATH = os.path.join(QDIR, 'queue.json')
MDPATH = os.path.join(QDIR, 'QUEUE.md')
CLAIMS = os.path.join(QDIR, 'CLAIMS.jsonl')
RLOG = os.path.join(QDIR, 'ROUND-LOG.md')
LSTATE = os.path.join(QDIR, 'loop_state.json')
LOCK = os.path.join(QDIR, '.loop.lock')
GRP = r'C:\Fluxgroup\FluxGroup'
STALE_LOCK_S = 600


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def rd_json(p, default):
    try:
        with io.open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def wr_json(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def acquire_lock():
    if os.path.exists(LOCK):
        st = rd_json(LOCK, {})
        try:
            age = time.time() - st.get('ts_epoch', 0)
        except Exception:
            age = 1e9
        alive = False
        try:
            pid = int(st.get('pid', 0))
            if pid and os.name == 'nt':
                r = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                                    "(Get-Process -Id %d -ErrorAction SilentlyContinue) -ne $null" % pid],
                                   capture_output=True, text=True, timeout=30)
                alive = r.stdout.strip().lower() == 'true'
        except Exception:
            alive = False
        if alive and age < STALE_LOCK_S:
            return False, 'lock-held-pid-%s' % st.get('pid')
        # stale or dead holder -> reclaim
    wr_json(LOCK, {'pid': os.getpid(), 'ts_epoch': time.time(), 'ts': now_iso()})
    return True, 'ok'


def release_lock():
    try:
        os.remove(LOCK)
    except Exception:
        pass


def append_line(p, line):
    with io.open(p, 'a', encoding='utf-8') as f:
        f.write(line.rstrip('\n') + '\n')


def require_ok(q, st):
    req = st.get('require') or 'none'
    if req == 'none':
        return True, 'none'
    if req.startswith('manual-gate:'):
        gate = q['gates'].get(req.split(':', 1)[1])
        if gate and gate.get('state') == 'open':
            return True, 'gate-open'
        return False, 'gate-closed:' + req.split(':', 1)[1]
    if req.startswith('st') and len(req) == 6:
        for s in q['stations']:
            if s['id'] == req and s['state'] == 'done':
                return True, 'dep-done'
        return False, 'dep-open:' + req
    return False, 'unknown-require:' + req


def regen_md(q):
    lines = []
    a = lines.append
    a('# CONTENT-LOOP QUEUE -- drama line (bm-b host, v0.1)')
    a('')
    a('> Carrier: Bigmoney-ContentLoop S4U task (20-min). Machine ledger = queue.json (single-writer);')
    a('> this file is a regenerated face -- never hand-edit. Protocol: claim-by-file, station states')
    a('> open/claimed/done/blocked; five-piece gates stay in-loop (no downgrade); director step-gate')
    a('> per station; CEO = terminal review only; account writes = physical-domain pause face.')
    a('> Law refs: CONTENT-OS-LOOP-BLUEPRINT-v1 sec.3; O-20261018-2144-bm-c sec.2.1; DIRECTOR-STEP-GATE-v1.')
    a('')
    a('## Gates')
    a('')
    a('| gate | state | note |')
    a('|---|---|---|')
    for k, g in q.get('gates', {}).items():
        a('| %s | %s | %s |' % (k, g.get('state'), (g.get('note') or '')[:160]))
    a('')
    a('## Stations')
    a('')
    a('| id | state | lane | runner | require | title | claim |')
    a('|---|---|---|---|---|---|---|')
    for s in q['stations']:
        a('| %s | %s | %s | %s | %s | %s | %s |' % (
            s['id'], s['state'], s['lane'], s.get('runner'), s.get('require'),
            s['title'][:80], s.get('claim') or '-'))
    a('')
    st = rd_json(LSTATE, {})
    a('Loop state: rounds=%s last=%s' % (st.get('rounds', 0), st.get('last_ts', '-')))
    with io.open(MDPATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


# ---------------- runners (v0.1 registry) ----------------

def _git(args, timeout=180):
    r = subprocess.run(['git', '-C', GRP] + args, capture_output=True, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace')


def st001_rootcause_gather(st):
    """ST-001: collect J-D0-1 taildrop evidence from group origin and emit a
    root-cause face into the outbox. Honest-bounded: facts first, root-cause
    candidate clearly labeled as bm-b-side self-cert draft; the LEDGER backfill
    row lands on group via the next push window (queued, not auto-pushed)."""
    out_dir = os.path.join(QDIR, 'outbox')
    os.makedirs(out_dir, exist_ok=True)
    facts = []
    rc, out = _git(['ls-tree', '-r', '--name-only', 'origin/main'])
    hits = [l for l in out.splitlines() if 'taildrop' in l.lower()]
    facts.append(('group-origin tree scan', 'rc=%d, taildrop-named files=%d' % (rc, len(hits))))
    for h in hits[:10]:
        facts.append(('file', h))
    rc, out = _git(['show', 'origin/main:cph4/fleet/drama-dept-v1/LEDGER.md'])
    led_lines = [l for l in out.splitlines() if 'J-D0-1' in l or 'taildrop' in l.lower()]
    facts.append(('LEDGER rows', '%d hit(s)' % len(led_lines)))
    for l in led_lines[:5]:
        facts.append(('ledger', l[:300]))
    # probe group orders for the original dispatch contract
    rc, out = _git(['show', 'origin/main:docs/orders.md'])
    ord_hits = [l for l in out.splitlines() if 'taildrop' in l.lower() and 'drama' in l.lower()]
    facts.append(('orders rows', '%d hit(s)' % len(ord_hits)))
    for l in ord_hits[:5]:
        facts.append(('order', l[:300]))
    md = []
    md.append('# J-D0-1 root-cause self-cert (draft) -- bm-b taildrop SLA violation')
    md.append('')
    md.append('> Station ST-001 product (CONTENT-LOOP v0.1 first runner). Source: drama-dept-v1 LEDGER')
    md.append('> row J-D0-1 (2026-10-16 drama-pilot-taildrop-bmb OVERDUE, hit=0/1, 12:45 deadline,')
    md.append('> 21:06 poke; bm-b-side self-cert pending). PILOT-001 3x20s samples WERE delivered')
    md.append('> (RECIPE-EPBURN-v1 preface) -- the violation is about the delivery channel, not the product.')
    md.append('')
    md.append('## Facts collected (group origin @ %s)' % now_iso())
    for k, v in facts:
        md.append('- **%s**: %s' % (k, v))
    md.append('')
    md.append('## Root-cause candidate (bm-b side)')
    md.append('')
    md.append('- Delivery mechanism was fleet Taildrop file transfer (drop to peer Downloads scan face,')
    md.append('  r1044 pit law). hit=0/1 with poke at 21:06 after a 12:45 deadline = the receiving-side')
    md.append('  pickup never registered during the SLA window; delivery only completed via a later')
    md.append('  alternate channel (git/manual), so the watch contract counted a violation.')
    md.append('- Candidate root causes (ranked): (1) taildrop drop landed outside the scanned inbox face')
    md.append('  (r1044: must-scan-Downloads face); (2) sender-side send receipt not written while the')
    md.append('  receive actually happened late; (3) peer offline during the window.')
    md.append('- Gate recommendation: delivery-watch contract should pin the scan face list (Downloads +')
    md.append('  fleet inbox) and require a sender receipt row; deadline contracts for cross-machine')
    md.append('  physical-channel deliveries should carry a fallback-to-git clause so SLA is provable.')
    md.append('')
    md.append('## Status')
    md.append('')
    md.append('- This face = local evidence product (ST-001 done locally). The LEDGER backfill row rides')
    md.append('  the next group push window -- queued as outbox payload, NOT auto-pushed (group tree =')
    md.append('  shared live tree, CAS push required).')
    outp = os.path.join(out_dir, 'J-D0-1-rootcause.md')
    with io.open(outp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    return {'runner': 'st001_rootcause_gather', 'product': outp,
            'facts_collected': len(facts), 'verdict': 'done-local-ledger-row-pending-group-push'}


RUNNERS = {
    'st001_rootcause_gather': st001_rootcause_gather,
}


def station_plan(q):
    """Returns (verdict, station, why) for the first actionable station."""
    for st in q['stations']:
        if st['state'] == 'claimed':
            # crashed-claim reclaim after 30min not implemented in v0.1; honest hold
            return 'held', st, 'claim-in-place (v0.1 has no reclaim yet)'
        if st['state'] != 'open':
            continue
        ok, why = require_ok(q, st)
        if not ok:
            continue  # gate/dep closed -> try next station
        runner = st.get('runner') or 'none'
        if runner in RUNNERS:
            return 'claimable', st, 'runner-ready'
        return 'held', st, 'runner-pending:' + runner
    return 'no-station', None, 'all stations blocked/pending/done'


def do_round():
    ok, why = acquire_lock()
    if not ok:
        return {'verdict': 'lock-held', 'why': why, 'ts': now_iso()}
    try:
        q = rd_json(QPATH, None)
        if q is None:
            return {'verdict': 'mechanism-fault', 'why': 'queue.json unreadable', 'ts': now_iso()}
        verdict, st, why = station_plan(q)
        action = None
        if verdict == 'claimable':
            st['state'] = 'claimed'
            st['claim'] = 'claimed@bm-b@' + now_iso()
            wr_json(QPATH, q)
            append_line(CLAIMS, json.dumps({'ts': now_iso(), 'station': st['id'],
                                           'action': 'claimed', 'by': 'bm-b'}, ensure_ascii=False))
            try:
                action = RUNNERS[st['runner']](st)
                st['state'] = 'done'
                st['done_at'] = now_iso()
            except Exception as e:
                st['state'] = 'open'   # honest rollback; station stays queued
                action = {'runner': st['runner'], 'verdict': 'runner-error', 'err': str(e)[:200]}
            q = rd_json(QPATH, q)
            for s2 in q['stations']:
                if s2['id'] == st['id']:
                    s2['state'] = st['state']
                    s2['claim'] = st.get('claim')
                    if 'done_at' in st:
                        s2['done_at'] = st['done_at']
            wr_json(QPATH, q)
            append_line(CLAIMS, json.dumps({'ts': now_iso(), 'station': st['id'],
                                            'action': st['state'], 'detail': action},
                                           ensure_ascii=False))
        regen_md(q)
        ls = rd_json(LSTATE, {'rounds': 0})
        ls['rounds'] = int(ls.get('rounds', 0)) + 1
        ls['last_ts'] = now_iso()
        wr_json(LSTATE, ls)
        append_line(RLOG, '%s | round %s | %s | %s | %s' % (
            now_iso(), ls['rounds'], verdict, (st or {}).get('id', '-'),
            json.dumps(action or why, ensure_ascii=False)[:220]))
        return {'verdict': verdict, 'station': (st or {}).get('id'), 'why': why,
                'action': action, 'ts': now_iso(), 'loop_rounds': ls['rounds']}
    finally:
        release_lock()


def do_scan():
    q = rd_json(QPATH, None)
    if q is None:
        return {'verdict': 'mechanism-fault', 'why': 'queue.json unreadable'}
    verdict, st, why = station_plan(q)
    return {'verdict': verdict, 'station': (st or {}).get('id'), 'why': why, 'ts': now_iso()}


def selftest():
    asserts = []
    q = rd_json(QPATH, {})
    asserts.append(('queue-readable', isinstance(q.get('stations'), list) and len(q['stations']) >= 1))
    ids = [s['id'] for s in q.get('stations', [])]
    asserts.append(('ids-unique', len(ids) == len(set(ids))))
    v, st, why = station_plan(q)
    asserts.append(('plan-verdict-valid', v in ('claimable', 'held', 'no-station')))
    known = all((s.get('runner') or 'none') in list(RUNNERS) + ['none', 'v0.2-pending']
                for s in q.get('stations', []))
    asserts.append(('runners-known-or-pending', known))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL', 'asserts':
                      {k: ok for k, ok in asserts}}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'round'
    if cmd == 'round':
        print(json.dumps(do_round(), ensure_ascii=False))
    elif cmd == 'scan':
        print(json.dumps(do_scan(), ensure_ascii=False))
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print(json.dumps({'verdict': 'usage', 'cmds': ['round', 'scan', 'selftest']}))
