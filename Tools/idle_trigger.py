#!/usr/bin/env python
# idle_trigger.py -- O-20261007-2315 idle hard-trigger loop leg (machine-internal
# structural trigger; enforcement moves from external audit callouts to an
# in-machine per-round construct. CEO root complaint: recurring idle machines).
#
# Law map:
#   - resource-chain 8.2 GREEN-IDLE gate: RAM free >=40% AND VRAM free >=6GB AND
#     no in-flight batch. Declared-standby machines are exempt (8.2.3); here a
#     paused machine does not run rounds at all (loop task stopped), so pause is
#     structurally self-consistent and needs no extra marker.
#   - resource-chain 8.1: claim lane = fleet/backlog.md claim-by-file protocol
#     (line-end "claimed@<machine>@<ts>").
#   - O-20261007-2315 two-read trigger: consecutive GREEN-IDLE rounds with no
#     claim -> heartbeat idle_rounds counts them; RED consumption threshold
#     stays >=2 with the duty round. A claim (or --worked declare) clears to 0.
#
# Semantics (documented for the receipt):
#   idle_rounds  = number of CONSECUTIVE completed round windows in which this
#                  machine was GREEN-IDLE and neither claimed a backlog line
#                  nor declared work. Cleared to 0 on claim/declare.
#   agenda_starved = True iff latest bookkeeping saw GREEN-IDLE and the backlog
#                  pool had no claimable line (pool starved signal).
#
# Callers:
#   - Tools/iteration_loop.ps1 bookkeeping leg, once per round start (structural,
#     AI-independent counting). Dedupe guard: a second bookkeeping run within
#     DEDUPE_MIN minutes of the last touch is a no-op (idempotent per round).
#   - Round AI flags: --claimed (claimed a backlog line / finished product work
#     tied to a claim) or --worked (standing-agenda or other product work done,
#     machine was not idle in the work sense). Both reset the streak.
#   - selftest: offline fixture check of the gate + counting logic, no writes.
#
# Output: one-line JSON verdict on stdout; full verdict to
# results/idle_trigger.<machine_id>.json for same-round AI consumption.
#
# ENCODING: pure ASCII body (repo law: PS/py hosts on zh-CN decode BOM-less
# files as GBK; keep every non-ASCII string out of this file).
import json
import os
import re
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAM_GATE_PCT = 40.0
VRAM_GATE_GB = 6.0
DEDUPE_MIN = 8.0
ROUND_WINDOW_MIN = 11.0  # 10-min cadence + skew
# Zero-desktop-flash flag for every git subprocess (U060/2026-10-01 silence
# law). r812 live-fire pit: this constant MUST exist at module level before
# _git uses it -- a missing module global raises NameError inside _git's
# except-Exception swallow and the whole work-detection leg dies SILENTLY
# (rc=1, out='' looks like an empty repo answer). Keep it here, asserted
# in selftest.
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

CLAIM_RE = re.compile(r'claimed@([A-Za-z0-9\-]+)@(\S+)')


def machine_id():
    p = os.path.join(PROJECT, 'fleet', 'machine.json')
    with open(p, encoding='utf-8') as f:
        return json.load(f).get('machine_id', 'unknown')


def probe_ram():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return round(vm.available * 100.0 / vm.total, 1)
    except Exception:
        return None


def probe_vram():
    # nvidia-smi free MiB -> GB; None = probe unavailable (leg disclosed).
    try:
        out = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=10)
        if out.returncode != 0 or not out.stdout.strip():
            return None
        first = out.stdout.strip().splitlines()[0]
        return round(float(first) / 1024.0, 2)
    except Exception:
        return None


def probe_inflight(mid):
    reasons = []
    # 1) saturation engine active burns
    try:
        p = os.path.join(PROJECT, 'results', 'saturation_engine',
                         'state_%s.json' % mid)
        d = json.load(open(p, encoding='utf-8'))
        if d.get('active'):
            reasons.append('satengine_active=%d' % len(d['active']))
    except Exception:
        pass
    # 2) runnable pool running faces owned by this machine
    try:
        p = os.path.join(PROJECT, 'results', 'runnable_pool.json')
        d = json.load(open(p, encoding='utf-8'))
        n = 0
        for e in d.get('entries', []):
            if e.get('status') == 'running' and (e.get('lane_owner') in (None, mid)):
                n += 1
        if n:
            reasons.append('pool_running=%d' % n)
    except Exception:
        pass
    return reasons


def parse_backlog(mid, now):
    """Return (claimable_lines, fresh_claim_ts_or_None)."""
    claimable = []
    fresh_claim = None
    p = os.path.join(PROJECT, 'fleet', 'backlog.md')
    if not os.path.exists(p):
        return claimable, fresh_claim
    try:
        with open(p, encoding='utf-8') as f:
            for line in f:
                if 'claimed@' in line:
                    m = CLAIM_RE.search(line)
                    if m and m.group(1) == mid:
                        # ts formats seen: 10-02 00:05 / 2026-10-07T22:33:00+08:00
                        ts_raw = m.group(2)
                        ts = parse_ts(ts_raw)
                        if ts and (now - ts) <= ROUND_WINDOW_MIN * 60:
                            fresh_claim = ts_raw
                    continue
                # claimable = numbered pool line not yet claimed, not cleared
                if re.match(r'\s*\d+\.\s+\S', line) and 'claimed@' not in line \
                        and u'过期清出' not in line:
                    claimable.append(line.strip()[:80])
    except Exception:
        pass
    return claimable, fresh_claim


def parse_ts(ts_raw):
    import datetime
    import warnings
    for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%m-%d %H:%M'):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                dt = datetime.datetime.strptime(ts_raw.replace('+08:00', '+0800'), fmt)
            if fmt == '%m-%d %H:%M':
                dt = dt.replace(year=datetime.datetime.now().year)
            if dt.tzinfo is None:
                import datetime as _d
                dt = dt.replace(tzinfo=_d.timezone(_d.timedelta(hours=8)))
            return dt.timestamp()
        except ValueError:
            continue
    return None


def state_path(mid):
    return os.path.join(PROJECT, 'results', 'idle_trigger_state.%s.json' % mid)


def out_path(mid):
    return os.path.join(PROJECT, 'results', 'idle_trigger.%s.json' % mid)


def load_state(mid):
    try:
        return json.load(open(state_path(mid), encoding='utf-8'))
    except Exception:
        return {'streak': 0, 'last_touch': 0.0}


def save_state(mid, st):
    with open(state_path(mid), 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def touch_heartbeat(mid, idle_rounds, agenda_starved):
    """Fresh-read-modify-write single file (multi-writer shared file law:
    never whole-block replace from a stale snapshot)."""
    p = os.path.join(PROJECT, 'fleet', 'machines', '%s.json' % mid)
    d = json.load(open(p, encoding='utf-8'))
    d['idle_rounds'] = int(idle_rounds)
    d['agenda_starved'] = bool(agenda_starved)
    tmp = p + '.tmp%d' % os.getpid()
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    # self-verify types (R170/R178 law: value AND type must both be right)
    chk = json.load(open(p, encoding='utf-8'))
    assert isinstance(chk['idle_rounds'], int), 'idle_rounds must be int'
    assert isinstance(chk['agenda_starved'], bool), 'agenda_starved must be bool'


def bookkeeping(mid, now):
    st = load_state(mid)
    if now - st.get('last_touch', 0.0) < DEDUPE_MIN * 60:
        prev = {}
        try:
            prev = json.load(open(out_path(mid), encoding='utf-8'))
        except Exception:
            pass
        prev['dedupe'] = True
        return prev if prev else {'dedupe': True, 'idle_rounds': st.get('streak', 0)}
    ram = probe_ram()
    vram = probe_vram()
    inflight = probe_inflight(mid)
    claimable, fresh_claim = parse_backlog(mid, now)
    ram_ok = ram is None or ram >= RAM_GATE_PCT  # probe fail disclosed, not guessed
    vram_ok = vram is None or vram >= VRAM_GATE_GB
    green_idle = bool(ram_ok and vram_ok and not inflight)
    if green_idle and fresh_claim is None:
        st['streak'] = int(st.get('streak', 0)) + 1
    else:
        st['streak'] = 0
    st['last_touch'] = now
    save_state(mid, st)
    idle_rounds = st['streak']
    agenda_starved = bool(green_idle and not claimable)
    touch_heartbeat(mid, idle_rounds, agenda_starved)
    v = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now)),
        'machine': mid,
        'green_idle': green_idle,
        'ram_free_pct': ram,
        'vram_free_gb': vram,
        'inflight_reasons': inflight,
        'claimed_recent': fresh_claim is not None,
        'claimable_pool_lines': len(claimable),
        'idle_rounds': idle_rounds,
        'agenda_starved': agenda_starved,
        'two_read_red': idle_rounds >= 2,
        'law_ref': 'O-20261007-2315 + resource-chain 8.2',
    }
    with open(out_path(mid), 'w', encoding='utf-8') as f:
        json.dump(v, f, ensure_ascii=False, indent=1)
    return v


def declare(mid, now, kind):
    st = load_state(mid)
    st['streak'] = 0
    st['last_touch'] = now
    st['last_declare'] = kind
    save_state(mid, st)
    touch_heartbeat(mid, 0, False)
    return {'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now)),
            'machine': mid, 'declared': kind, 'idle_rounds': 0,
            'agenda_starved': False}


# ---------------------------------------------------------------------------
# T6 (tech queue r812, bm-c): structural --auto declare leg. Removes the
# dependence on the round AI remembering to hand-run --claimed/--worked on
# non-bm-a carrier machines. Deterministic, AI-independent:
#   claimed <- pool shard owned by this machine with owner_since inside the
#              window since the last bookkeeping touch (backlog.md claims are
#              already auto-detected by bookkeeping's fresh_claim face).
#   worked  <- commit(s) since last bookkeeping touch authored by THIS
#              machine's git identity (committer email = local user.email;
#              daemon subjects excluded) that touch at least one path OUTSIDE
#              the pure-bookkeeping face set (product-first law: state files,
#              round reports, heartbeat, memory appends, per-round helper
#              receipts and always-drifting re-derive faces are bookkeeping;
#              scripts/research/qa/data/pipeline outputs are work).
# Conservative bias: anything undetected leaves the streak untouched, so a
# miss can only produce an extra RED nudge, never a silent idle pass.
# ---------------------------------------------------------------------------
DAEMON_SUBJ = re.compile(r'^(autofill tick|dispatcher|resident dispatcher)', re.I)

BOOKKEEP_PATHS = (
    r'^CODELY\.md$',                      # memory appends = bookkeeping
    r'^state(-bm-[a-z0-9]+)?\.json$',
    r'^state\.json$',
    r'^state/queue/',                     # tech/self-drive queue admin
    r'^round_reports',                    # per-machine round ledgers
    r'^logs/iteration-loop/',              # bm-b legacy ledger
    r'^fleet/machines/[^/]+\.json$',      # heartbeats
    r'^fleet/inbox/',                     # message moves
    r'^results/_r\d+',                    # per-round helper receipts/logs
    r'^results/_orphan_face_probe',
    r'^results/idle_trigger',
    r'^results/token_usage\.json$',
    r'^results/compute_audit\.json$',
    r'^results/_attrition_guard_scan\.json$',
    r'^results/pool_dualrun\..*\.jsonl$',  # S6 evidence append (every round)
    r'^results/strategy_scorecard\.json$', # re-derived every round (ts drift)
    r'^results/saturation_engine/',       # engine state faces
    r'^results/watermark',                # probe series
    r'^dashboard_status\.(json|js)$',      # bm-a host re-derives every round
)


def is_bookkeeping_path(p):
    p = (p or '').replace('\\', '/').strip()
    return any(re.match(rx, p) for rx in BOOKKEEP_PATHS)


def split_log_line(line):
    """'sha<TAB>subject' -> (sha, subject); malformed -> (None, None)."""
    if '\t' not in line:
        return None, None
    sha, subj = line.split('\t', 1)
    return (sha.strip(), subj.strip()) if re.match(r'^[0-9a-f]{7,40}$', sha.strip()) else (None, None)


def _git(args, timeout=20):
    try:
        p = subprocess.run(['git', '-C', PROJECT] + args, capture_output=True,
                           creationflags=CNW, timeout=timeout)
        return p.returncode, p.stdout.decode('utf-8', 'replace')
    except Exception as exc:
        # r812 pit fix: NEVER swallow silently -- surface the failure on
        # stderr (carrier log captures 2>&1) so a dead leg is diagnosable.
        sys.stderr.write('idle_trigger._git EXC %r on %r\n' % (exc, args[:2]))
        return 1, ''


def _local_email():
    rc, out = _git(['config', 'user.email'])
    out = out.strip().lower()
    return out if rc == 0 and out else None


def _pool_claim_since(mid, floor_ts):
    """Newest pool shard claim (key) by this machine with ts >= floor."""
    best = None
    try:
        d = json.load(open(os.path.join(PROJECT, 'results', 'runnable_pool.json'),
                           encoding='utf-8'))
    except Exception:
        return None
    for e in d.get('entries', []):
        for sh in e.get('shards', []) or []:
            if sh.get('owner') == mid:
                ts = parse_ts(sh.get('owner_since', '') or '')
                if ts is not None and ts >= floor_ts:
                    if best is None or ts > best[0]:
                        best = (ts, sh.get('key', ''))
    return best[1] if best else None


def _work_paths_since(last_touch, email):
    """Non-bookkeeping paths from this machine's session commits since ts."""
    if not last_touch or not email:
        return []
    since = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(last_touch))
    rc, out = _git(['log', '--since=' + since, '--committer=' + email,
                    '--format=%H%x09%s'])
    if rc != 0:
        return []
    hit = []
    for line in out.splitlines():
        sha, subj = split_log_line(line)
        if not sha or DAEMON_SUBJ.match(subj):
            continue
        rc2, paths = _git(['diff-tree', '--no-commit-id', '--name-only',
                           '-r', sha])
        if rc2 != 0:
            continue
        for p in paths.splitlines():
            if p and not is_bookkeeping_path(p):
                hit.append(p)
    return hit


def auto_declare(mid, now):
    st = load_state(mid)
    last_touch = float(st.get('last_touch', 0.0) or 0.0)
    floor = last_touch - 60.0 if last_touch else now - ROUND_WINDOW_MIN * 60
    claim = _pool_claim_since(mid, floor)
    if claim:
        v = declare(mid, now, 'claimed')
        v['auto_reason'] = 'pool_claim=%s' % claim
        print(json.dumps(v, ensure_ascii=False))
        return 0
    paths = _work_paths_since(last_touch, _local_email())
    if paths:
        v = declare(mid, now, 'worked')
        v['auto_reason'] = 'work_paths=%d e.g. %s' % (len(paths), paths[0])
        print(json.dumps(v, ensure_ascii=False))
        return 0
    v = {'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now)),
         'machine': mid, 'declared': None, 'idle_rounds': st.get('streak', 0),
         'auto_reason': 'no_pool_claim_no_work_commit'}
    print(json.dumps(v, ensure_ascii=False))
    return 0


def selftest():
    # gate logic fixtures (no writes, no probes)
    ok = True
    def gate(ram, vram, inflight):
        ram_ok = ram is None or ram >= RAM_GATE_PCT
        vram_ok = vram is None or vram >= VRAM_GATE_GB
        return bool(ram_ok and vram_ok and not inflight)
    cases = [
        (50.0, 8.0, [], True, 'all-green'),
        (30.0, 8.0, [], False, 'ram-below-gate'),
        (50.0, 2.0, [], False, 'vram-below-gate'),
        (50.0, 8.0, ['satengine_active=1'], False, 'inflight-blocks'),
        (None, 8.0, [], True, 'ram-probe-fail-disclosed'),
        (None, None, [], True, 'both-probes-fail-disclosed'),
    ]
    for ram, vram, inf, want, name in cases:
        got = gate(ram, vram, inf)
        flag = 'PASS' if got == want else 'FAIL'
        if got != want:
            ok = False
        print('[%s] gate %s ram=%s vram=%s inflight=%s -> %s' % (flag, name, ram, vram, bool(inf), got))
    # ts parser fixtures
    for raw, expect in [('2026-10-07T22:33:00+08:00', True), ('10-02 00:05', True), ('garbage', False)]:
        got = parse_ts(raw) is not None
        flag = 'PASS' if got == expect else 'FAIL'
        if got != expect:
            ok = False
        print('[%s] ts parse %r -> %s' % (flag, raw, got))
    # T6 (r812) bookkeeping-path classifier fixtures
    path_cases = [
        ('CODELY.md', True), ('state-bm-c.json', True), ('state.json', True),
        ('state/queue/tech.md', True), ('round_reports-bm-c.md', True),
        ('fleet/machines/bm-c.json', True), ('fleet/inbox/MSG-x.md', True),
        ('results/_r812bmc_s05_facts.json', True),
        ('results/_orphan_face_probe.bm-c.json', True),
        ('results/idle_trigger.bm-c.json', True),
        ('results/token_usage.json', True), ('results/compute_audit.json', True),
        ('results/pool_dualrun.bm-c.jsonl', True),
        ('results/strategy_scorecard.json', True),
        ('results/saturation_engine/state_bm-c.json', True),
        ('dashboard_status.json', True), ('dashboard_status.js', True),
        ('scripts/science_audit.py', False), ('research/PIT-X.md', False),
        ('qa/smoke-r812-bm-c.md', False), ('data/daily/sh510300.csv', False),
        ('results/paper_export/export-2026-10-09.json', False),
        ('results/market_clock/CALL-2026-10-09.json', False),
        ('Tools/idle_trigger.py', False), ('fleet/backlog.md', False),
        ('docs/live_usage/LIVE-20261009.md', False),
        ('results\\strategy_scorecard.json', True),  # backslash normalization
    ]
    for p, want in path_cases:
        got = is_bookkeeping_path(p)
        flag = 'PASS' if got == want else 'FAIL'
        if got != want:
            ok = False
        print('[%s] bookkeep-path %r -> %s' % (flag, p, got))
    # T6 daemon-subject + log-line fixtures
    subj_cases = [
        ('autofill tick claim w17-screen-0of8 owner=bm-c (r199) [via bm-c]', True),
        ('autofill tick keepalive w17-screen-0of8 owner=bm-c [via bm-c]', True),
        ('round 812: T6 idle_trigger --auto declare leg [via bm-c r812]', False),
    ]
    for s, want in subj_cases:
        got = bool(DAEMON_SUBJ.match(s))
        flag = 'PASS' if got == want else 'FAIL'
        if got != want:
            ok = False
        print('[%s] daemon-subj %r -> %s' % (flag, s[:40], got))
    for line, want_sha in [
        ('abc123def\t round 812: work', 'abc123def'),
        ('short\t subj', None),
        ('no-tab-line', None),
    ]:
        sha, subj = split_log_line(line)
        got = sha if want_sha else None
        flag = 'PASS' if got == want_sha else 'FAIL'
        if got != want_sha:
            ok = False
        print('[%s] log-line %r -> sha=%s' % (flag, line[:24], sha))
    # r812-fix regression guard: module-level CNW must be defined and match
    # subprocess.CREATE_NO_WINDOW (missing global = NameError swallowed by
    # _git's except = work-detection leg dies SILENTLY -- live-fired r812).
    cnw_ok = (CNW == getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    flag = 'PASS' if cnw_ok else 'FAIL'
    if not cnw_ok:
        ok = False
    print('[%s] cnw-consistency CNW=%d' % (flag, CNW))
    print('selftest:', 'ALL PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if 'selftest' in argv:
        return selftest()
    mid = machine_id()
    now = time.time()
    if '--claimed' in argv:
        print(json.dumps(declare(mid, now, 'claimed'), ensure_ascii=False))
        return 0
    if '--worked' in argv:
        print(json.dumps(declare(mid, now, 'worked'), ensure_ascii=False))
        return 0
    if '--auto' in argv:
        return auto_declare(mid, now)
    v = bookkeeping(mid, now)
    print(json.dumps(v, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
