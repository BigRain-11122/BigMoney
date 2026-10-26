"""Supply-floor four-tuple alignment face (D-20261026-11 / D-20261025-16 sec.2).

Why this file exists: the fleet judges every company's supply by the same four
numbers -- ready_fresh / effective_ignitable / ignitable / floor -- and BigMoney
could not sign that statement on 2026-10-26 because nothing here computed it.
`compute_audit.py` already carries three of the four (ready, ready_ignitable,
floor) but never says what "fresh" means and never names the second cause of a
supply gap: a lane with ready work and no ignition face still burns nothing.

This module is a pure reader + arithmetic layer over those two faces
(results/compute_audit.json, results/runnable_pool.json) plus one host probe
(the round-ignition scheduled task). It never writes into either input, never
claims a batch, and never decides that an item is claimable when its owner is
merely silent -- `compute_audit`'s own corroboration rule is carried through
verbatim as `takeover_needs_corroboration`.

Output: results/supply_alignment.json  (single face, no history append)
Exit:   0 = face written, 2 = input face missing/unreadable (honest, no guess)
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, 'results', 'compute_audit.json')
POOL = os.path.join(ROOT, 'results', 'runnable_pool.json')
OUT = os.path.join(ROOT, 'results', 'supply_alignment.json')

# Deliberately explicit: a silent owner is NOT a dead owner (r1100/r1101), so
# its item is never counted as ignitable here even when the audit offers it as a
# takeover candidate.
FRESH_MAX_TRADING_DAYS = 5


def _read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _trading_days_between(d_old, d_new):
    """Official-day lag, read from the exchange calendar when available.

    Falls back to calendar days: a wrong direction (reporting a staleness that is
    too small) would hide a stale premise, so the fallback is only used when the
    calendar itself is unreadable and is disclosed in the face.
    """
    try:
        import csv
        cal = os.path.join(ROOT, 'data', 'exchange_calendar.csv')
        days = set()
        # utf-8-sig: the calendar is written by csv module on a BOM-tolerant
        # host, and a leading BOM turns the first column name into '\ufeffdate'
        # -- which silently empties this set and drops the code to the calendar
        # (weekend-inflated) fallback.
        with open(cal, 'r', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                key = (row.get('date') or row.get('trade_date') or '').strip()
                if key:
                    days.add(key)
        # compare as ISO strings: the calendar set holds text, and a date-vs-str
        # comparison raises TypeError, which the except below would swallow into
        # the calendar-day fallback (weekend-inflated lag) without a trace.
        s_old, s_new = d_old.isoformat(), d_new.isoformat()
        n = sum(1 for d in days if s_old < d <= s_new)
        if n or s_old == s_new:
            return n, 'exchange_calendar'
    except Exception:
        pass
    return (d_new - d_old).days, 'calendar_days_fallback'


def _item_fresh(item, newest_cutoff):
    """Fresh = the premise of the batch still describes today's panel."""
    ev = (item.get('evidence_cutoff') or '').strip()
    if not ev or not newest_cutoff:
        return None, 'no_evidence_cutoff'
    try:
        d_old = datetime.strptime(ev, '%Y-%m-%d').date()
        d_new = datetime.strptime(newest_cutoff, '%Y-%m-%d').date()
    except ValueError:
        return None, 'unparsable_cutoff'
    if d_new < d_old:
        return None, 'ahead_of_panel'
    lag, src = _trading_days_between(d_old, d_new)
    return (lag <= FRESH_MAX_TRADING_DAYS), '%s lag=%d src=%s' % (
        'fresh' if lag <= FRESH_MAX_TRADING_DAYS else 'stale', lag, src)


def build(entry_face, audit_latest, newest_cutoff, self_id='bm-c',
          ignition_face=None):
    """Pure function: the four-tuple plus the evidence for each number."""
    sf = audit_latest.get('supply_floor') or {}
    pi = audit_latest.get('pool_ignitable') or {}
    floor = sf.get('floor')
    owner_silent_min = pi.get('owner_silent_min', 120.0)
    silent_owners = pi.get('silent_owners') or {}

    ready = [e for e in entry_face if e.get('status') == 'ready']
    rows = []
    counts = {'ready': len(ready), 'ready_fresh': 0, 'ignitable': 0,
              'effective_ignitable': 0, 'fresh_unknown': 0}
    for it in ready:
        fresh, fresh_note = _item_fresh(it, newest_cutoff)
        owner = it.get('lane_owner') or it.get('claimed_by')
        # lane_owner is ownership, not a claim: compute_audit's gate treats the
        # declared lane host as the owner, and this face must not publish a
        # second truth about who may pick the item up (that is the whole point
        # of D-20261026-11).
        if not owner or owner == self_id:
            ignitable, ign_note = True, 'unowned_or_self'
        elif owner in silent_owners and silent_owners[owner] >= owner_silent_min:
            # silent owner: a candidate, never a permit
            ignitable, ign_note = False, 'owner_silent_%s' % owner
        else:
            ignitable, ign_note = False, 'owned_alive_%s' % owner
        if fresh:
            counts['ready_fresh'] += 1
        elif fresh is None:
            counts['fresh_unknown'] += 1
        if ignitable:
            counts['ignitable'] += 1
        if ignitable and fresh:
            counts['effective_ignitable'] += 1
        rows.append({
            'id': it.get('id'), 'owner': owner, 'fresh': fresh,
            'fresh_note': fresh_note, 'ignitable': ignitable,
            'ignitable_note': ign_note,
        })

    breaches = []
    if isinstance(floor, int):
        if counts['ready'] < floor:
            breaches.append('ready<%d' % floor)
        if counts['effective_ignitable'] < floor:
            breaches.append('effective_ignitable<%d' % floor)

    # Cross-check against the audit's own arithmetic. A disagreement is data
    # about the two faces, not something to paper over.
    audit_ready = sf.get('ready')
    audit_ign = sf.get('ready_ignitable')
    mismatches = []
    if isinstance(audit_ready, int) and audit_ready != counts['ready']:
        mismatches.append('ready %d!=%d' % (audit_ready, counts['ready']))
    if isinstance(audit_ign, int) and audit_ign != counts['ignitable']:
        mismatches.append('ignitable %d!=%d' % (audit_ign, counts['ignitable']))

    causes = []
    if breaches:
        if counts['ready'] == 0:
            causes.append('no_ready_inventory')
        elif counts['ignitable'] == 0:
            causes.append('inventory_owned_elsewhere')
        elif counts['ready'] < (floor or 0):
            causes.append('inventory_below_floor')
        if counts['ignitable'] > 0 and counts['effective_ignitable'] == 0:
            causes.append('inventory_stale_premise')
        if ignition_face and ignition_face.get('present') is False:
            causes.append('no_local_ignition_face')

    return {
        'self': self_id,
        'newest_panel_cutoff': newest_cutoff,
        'definitions': {
            'ready_fresh': 'status==ready AND evidence_cutoff within %d official '
                           'days of the newest panel cutoff (missing cutoff = unknown,'
                           ' never fresh)' % FRESH_MAX_TRADING_DAYS,
            'ignitable': 'ready AND (unclaimed or owned by self or owner heartbeat '
                         'fresh); a silent owner stays a takeover CANDIDATE, not a permit',
            'effective_ignitable': 'ignitable AND fresh',
            'floor': 'read from compute_audit.supply_floor.floor -- never hardcoded',
        },
        'four_tuple': {
            'ready': counts['ready'],
            'ready_fresh': counts['ready_fresh'],
            'ignitable': counts['ignitable'],
            'effective_ignitable': counts['effective_ignitable'],
            'floor': floor,
            'fresh_unknown': counts['fresh_unknown'],
        },
        'breach': breaches,
        'gap_causes': causes,
        'owner_silent_min': owner_silent_min,
        'silent_owners': silent_owners,
        'takeover_needs_corroboration': pi.get('takeover_needs_corroboration'),
        'ignition_face': ignition_face,
        'audit_mismatch': mismatches,
        'items': rows,
    }


def _ignition_face():
    """Is the round-ignition task registered on this host right now?"""
    out = {'present': None, 'detail': 'probe_failed'}
    try:
        p = subprocess.run(
            ['schtasks', '/query', '/fo', 'csv', '/nh'],
            capture_output=True, text=True, errors='replace', timeout=60)
        found = {}
        for line in (p.stdout or '').splitlines():
            for name in ('Bigmoney-IterationLoop', 'Bigmoney-LoopWatchdog'):
                if name in line and name not in found:
                    parts = [c.strip('"') for c in line.split('","')]
                    found[name] = parts[1] if len(parts) > 1 else 'unknown'
        out = {'present': bool(found), 'tasks': found,
               'detail': 'registered' if found else 'no_round_task_registered'}
    except Exception as exc:  # noqa: BLE001 - probe must never mask the face
        out = {'present': None, 'detail': 'probe_failed: %s' % exc}
    return out


def _selftest():
    ok = 0

    def chk(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError(msg)
        ok += 1

    audit = {'supply_floor': {'ready': 1, 'floor': 3, 'ready_ignitable': 0},
             'pool_ignitable': {'owner_silent_min': 120.0,
                                'silent_owners': {'bm-b': 5000.0},
                                'takeover_needs_corroboration': True}}
    face = [{'id': 'A', 'status': 'ready', 'lane_owner': 'bm-b',
             'evidence_cutoff': '2026-10-21'}]
    r = build(face, audit, '2026-10-23', 'bm-c', {'present': False})
    chk(r['four_tuple']['ready'] == 1, 'ready counted')
    chk(r['four_tuple']['ignitable'] == 0, 'silent foreign owner is not ignitable')
    chk(r['four_tuple']['effective_ignitable'] == 0, 'effective needs ignitable')
    chk(r['four_tuple']['floor'] == 3, 'floor read from audit')
    chk('no_local_ignition_face' in r['gap_causes'], 'ignition cause named')
    chk(r['audit_mismatch'] == [], 'agrees with audit')

    # unclaimed + fresh = effective ignitable
    face2 = [{'id': 'B', 'status': 'ready', 'evidence_cutoff': '2026-10-23'}]
    r2 = build(face2, audit, '2026-10-23', 'bm-c', {'present': True})
    chk(r2['four_tuple']['ignitable'] == 1, 'unclaimed is ignitable')
    chk(r2['four_tuple']['ready_fresh'] == 1, 'same-day evidence is fresh')
    chk(r2['four_tuple']['effective_ignitable'] == 1, 'effective = ignitable+fresh')

    # stale premise: ignitable but not effective
    face3 = [{'id': 'C', 'status': 'ready', 'evidence_cutoff': '2026-09-01'}]
    r3 = build(face3, audit, '2026-10-23', 'bm-c', {'present': True})
    chk(r3['four_tuple']['ignitable'] == 1, 'stale item still ignitable')
    chk(r3['four_tuple']['ready_fresh'] == 0, 'stale item not fresh')
    chk(r3['four_tuple']['effective_ignitable'] == 0, 'stale item not effective')

    # missing evidence_cutoff is unknown, never fresh
    face4 = [{'id': 'D', 'status': 'ready'}]
    r4 = build(face4, audit, '2026-10-23', 'bm-c', {'present': True})
    chk(r4['four_tuple']['fresh_unknown'] == 1, 'unknown counted separately')
    chk(r4['four_tuple']['ready_fresh'] == 0, 'unknown is not fresh')

    # disagreement with the audit is reported, not smoothed
    bad = dict(audit)
    bad['supply_floor'] = {'ready': 5, 'floor': 3, 'ready_ignitable': 4}
    r5 = build(face, bad, '2026-10-23', 'bm-c', {'present': True})
    chk(len(r5['audit_mismatch']) == 2, 'both mismatches surfaced')

    # no ready inventory is named as such
    r6 = build([], audit, '2026-10-23', 'bm-c', {'present': True})
    chk('no_ready_inventory' in r6['gap_causes'], 'empty pool cause named')

    # the official calendar must actually be the source when it is on disk: a
    # transparent fallback once reported a Friday->Monday lag as 3 days
    lag, src = _trading_days_between(datetime(2026, 10, 17).date(),
                                     datetime(2026, 10, 22).date())
    if os.path.exists(os.path.join(ROOT, 'data', 'exchange_calendar.csv')):
        chk(src == 'exchange_calendar', 'calendar is the lag source when present')
        chk(lag == 4, 'official-day lag (Sat 10-17 -> Thu 10-22 = 4 sessions, not 5 days)')

    print('supply_alignment selftest: %d/%d PASS' % (ok, ok))
    return 0


def main(argv):
    if '--selftest' in argv:
        return _selftest()
    try:
        audit = _read(AUDIT)['latest']
        pool = _read(POOL)
    except Exception as exc:  # noqa: BLE001
        print('supply_alignment: input face unreadable: %s' % exc)
        return 2
    entries = pool.get('entries') or []
    newest = ''
    for e in entries:
        c = (e.get('evidence_cutoff') or '').strip()
        if c > newest:
            newest = c
    face = build(entries, audit, newest, _self_id(), _ignition_face())
    face['generated_at'] = datetime.now().astimezone().isoformat(timespec='seconds')
    face['inputs'] = {'compute_audit': os.path.relpath(AUDIT, ROOT).replace('\\', '/'),
                      'runnable_pool': os.path.relpath(POOL, ROOT).replace('\\', '/')}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    ft = face['four_tuple']
    print('supply_alignment: ready=%s fresh=%s ignitable=%s effective=%s floor=%s '
          'breach=%s causes=%s' % (ft['ready'], ft['ready_fresh'], ft['ignitable'],
                                   ft['effective_ignitable'], ft['floor'],
                                   ','.join(face['breach']) or 'none',
                                   ','.join(face['gap_causes']) or 'none'))
    return 0


def _self_id():
    try:
        with open(os.path.join(ROOT, 'fleet', 'machine.json'), encoding='utf-8') as f:
            return json.load(f).get('machine_id', 'unknown')
    except Exception:  # noqa: BLE001
        return 'unknown'


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))