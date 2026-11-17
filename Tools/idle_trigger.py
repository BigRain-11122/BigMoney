#!/usr/bin/env python
# idle_trigger.py -- O-20261007-2315 idle hard-trigger loop leg (machine-internal
# structural trigger; enforcement moves from external audit callouts to an
# in-machine per-round construct. CEO root complaint: recurring idle machines).
#
# Law map:
#   - resource-chain 8.2 GREEN-IDLE gate: RAM free >=40% AND no in-flight
#     batch. Declared-standby machines are exempt (8.2.3); here a paused
#     machine does not run rounds at all (loop task stopped), so pause is
#     structurally self-consistent and needs no extra marker.
#   - T-2026-10-10-183 / O-20261010-1825 sec.3 (CEO direct, 10-10): the
#     vram_free>=6GB term is REMOVED from the gate. Claim lane work is
#     CPU-only quant backfill; CEO foreground apps legally occupying VRAM
#     must not collectively punish the CPU lanes (live-fired 10-10 18:1x:
#     vram_free 0.13G blocked all idle-trigger claiming). VRAM stays
#     probed and disclosed (vram_free_gb field) but no longer gates.
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
# r1789 bm-c: a pool line may declare itself unclaimable for a named machine instead
# of being handed a fake claim or a fake expiry. Comma list; other machines unaffected.
EXCLUDE_RE = re.compile(r'not-claimable-for:\s*([A-Za-z0-9\-]+(?:\s*[,，]\s*[A-Za-z0-9\-]+)*)')
# r1304: three states, not two. A pool card can be (a) claimable here, (b) waiting on a
# gate it declares itself (`gate 现状=CLOSED`), or (c) naming an execution face this disk
# does not have. Before this round (b) and (c) both counted as "work available", so a
# machine whose GPU is held by the CEO's own desktops read GREEN-IDLE-with-work for three
# rounds running while nothing could light; and (a) was lost outright on any card that
# merely MENTIONED the claim syntax, because the reader tested the bare substring.
EXEC_FACE_RE = re.compile(r'execution-face:\s*([^\s·）)、,，]+)')
GATE_CLOSED_RE = re.compile(r'gate\s*(?:现状\s*)?=\s*CLOSED')
# r1305: a card can state its GPU door as a number (`headroom>=1.5GB`) or by pointing
# at another card's door (`与 B-CITY3D-01 同 gate`). Both read as claimable work, so
# the idle face printed four claimable lines on a machine whose only GPU held 1.48 GB
# free and left the shortfall for the reader to subtract by hand.
HEADROOM_RE = re.compile(r'headroom\s*(?:>=|\u2265|\uff1e=|\uff1e)\s*([\d.]+)\s*GB', re.I)
REF_GATE_RE = re.compile(r'\u4e0e\s*([A-Za-z0-9\-]+)\s*\u540c\s*gate')
CARD_NAME_RE = re.compile(r'\u3010[^/\u3011]*/([A-Za-z0-9\-]+)\u3011')
# r1305b: some cards state their door as a deal, not a number -- `构建窗与他司产线协商
# 让路`, `他司会话优先不抢`. The face cannot prove a deal is open (it has no reading of
# another desk's session), so it must not print those cards as unqualified work either.
# It prints the clause beside the card and says how many claimable cards carry one.
SOFT_GATE_RE = re.compile(r'(\u4ed6\u53f8\u4f1a\u8bdd\u4f18\u5148[^\uff0c\u3002;\uff1b]*'
                          r'|\u4e0e\u4ed6\u53f8[^\uff0c\u3002;\uff1b]*\u534f\u5546\u8ba9\u8def)')
# the claim-by-file protocol writes completion as `done@<ts>+<commit>`; a card that
# carries one is out of the pool however sloppily it wrote its claim marker (card 1 was
# reading as claimable because `claimed@bm-c 生产泵@10-0x` has no `@<ts>` and the done
# line right after it was never read at all).
DONE_RE = re.compile(r'done@\S+')


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


def _count_pool_ready(entries):
    # Pure counting core of the runnable-pool face (fixture-testable).
    if not isinstance(entries, list):
        return None
    n = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        if str(e.get('status') or '').lower() != 'ready':
            continue
        if e.get('owner'):
            continue
        n += 1
    return n


def pool_ready_unclaimed():
    # r1119: the runnable POOL face (results/runnable_pool.json), which is a
    # DIFFERENT work face from fleet/backlog.md. This round both numbers were
    # read side by side (idle_trigger 1 vs compute_audit 3) and looked like a
    # contradiction; they never were -- one counts backlog lines, the other
    # counts ready unowned pool entries. Publish both, named for their face,
    # so no consumer has to guess which "pool" a number refers to.
    p = os.path.join(PROJECT, 'results', 'runnable_pool.json')
    try:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
    except Exception:
        return None
    entries = d.get('entries') if isinstance(d, dict) else d
    return _count_pool_ready(entries)


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


def line_excluded(line, mid):
    """True when the pool line names this machine as `not-claimable-for`.

    r1789: three BigCompute GPU cards sat in the pool counting as claimable on a
    machine whose GPU is parked by order (C-20261014-01 section 3) and whose disk has
    none of the projects they name; two rounds in a row read GREEN-IDLE with work
    available, which is exactly the reading the idle law punishes.
    """
    m = EXCLUDE_RE.search(line)
    if not m:
        return False
    names = [x.strip() for x in re.split(u'[,\uff0c]', m.group(1)) if x.strip()]
    return mid in names


def classify_pool_line(line, mid, exists=os.path.exists, vram_free_gb=None, gate_table=None):
    """Classify one fleet/backlog.md line for one machine.

    Returns (kind, detail):
      'claim'      -> {'mine': bool, 'ts': raw timestamp}
      'drop'       -> reason string (not a pool row / cleared / named not-claimable)
      'struct_wait'-> {'card','reason','face',...}  (door shut / face missing / vram)
      'claimable'  -> the trimmed line
    `exists` is injectable so the selftest can hold a fixture without touching disk.
    `vram_free_gb` is the caller's probe reading (None = probe unavailable, disclosed);
    `gate_table` maps a card name to the numeric GPU door that card declares, so a card
    that only says `与 <card> 同 gate` inherits a real number instead of a guess.
    """
    m = CLAIM_RE.search(line)
    if m:
        return ('claim', {'mine': m.group(1) == mid, 'ts': m.group(2)})
    if not re.match(r'\s*\d+\.\s+\S', line):
        return ('drop', 'not-a-pool-row')
    if u'过期清出' in line:
        return ('drop', 'cleared')
    if DONE_RE.search(line):
        return ('drop', 'done')
    if line_excluded(line, mid):
        return ('drop', 'named-not-claimable')
    cm = re.match(r'\s*(\d+)\.', line)
    card = cm.group(1) if cm else '?'
    fm = EXEC_FACE_RE.search(line)
    face = fm.group(1) if fm else None
    if face and not exists(face):
        return ('struct_wait', {'card': card, 'reason': 'execution_face_missing', 'face': face})
    if GATE_CLOSED_RE.search(line):
        return ('struct_wait', {'card': card, 'reason': 'gate_closed', 'face': face})
    # r1305: the GPU door, when the card states one. A declared number and a number
    # inherited through `同 gate` are the same door; a reference we cannot resolve is
    # NOT an open door (a shut door we failed to read must not print as claimable).
    need = None
    how = None
    hm = HEADROOM_RE.search(line)
    if hm:
        need, how = float(hm.group(1)), 'declared'
    else:
        rm = REF_GATE_RE.search(line)
        if rm:
            ref = rm.group(1)
            if gate_table and ref in gate_table:
                need, how = float(gate_table[ref]), 'inherited:%s' % ref
            else:
                return ('struct_wait', {'card': card, 'reason': 'gate_inherited',
                                        'face': face, 'ref': ref, 'needs_gb': None})
    if need is not None:
        if vram_free_gb is None:
            # a door we cannot measure is not a door we may call open
            return ('struct_wait', {'card': card, 'reason': 'vram_unknown', 'face': face,
                                    'needs_gb': need, 'how': how})
        if float(vram_free_gb) < need:
            return ('struct_wait', {'card': card, 'reason': 'vram_short', 'face': face,
                                    'needs_gb': need,
                                    'have_gb': round(float(vram_free_gb), 2),
                                    'short_gb': round(need - float(vram_free_gb), 2),
                                    'how': how})
    return ('claimable', {'card': card, 'line': line.strip()[:80],
                          'soft_gate': (SOFT_GATE_RE.search(line).group(1).strip()
                                        if SOFT_GATE_RE.search(line) else None)})


def parse_backlog(mid, now, vram_free_gb=None):
    """Return (claimable_lines, fresh_claim_ts_or_None, struct_wait_rows).

    r1304: a pool line is claimable here only when nothing it says about itself
    rules this machine out. Two things it can say are now read instead of being
    counted as work: `execution-face: <path>` (the project a job needs -- a
    missing path is a structural wait, not a job this disk can light) and
    `gate 现状=CLOSED` (the card declares its own door shut). Claim detection
    moved from a bare substring to the claim marker itself: card 19 had been
    dropping out of every face for weeks because its text explains the syntax
    `claimed@<机>@<ts>` and the reader skipped the whole line.

    r1305: the GPU door is read as a number. Pass 1 collects every card that
    declares `headroom>=<n>GB` under its own name; pass 2 lets a card written as
    `与 <card> 同 gate` inherit that number, so the two City3D cards are judged by
    the same door the pool wrote down once.
    """
    claimable = []
    struct_wait = []
    fresh_claim = None
    p = os.path.join(PROJECT, 'fleet', 'backlog.md')
    if not os.path.exists(p):
        return claimable, fresh_claim, struct_wait
    try:
        with open(p, encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return claimable, fresh_claim, struct_wait
    gate_table = {}
    for line in lines:
        nm = CARD_NAME_RE.search(line)
        hm = HEADROOM_RE.search(line)
        if nm and hm:
            gate_table[nm.group(1)] = float(hm.group(1))
    try:
        for line in lines:
            kind, detail = classify_pool_line(line, mid, vram_free_gb=vram_free_gb,
                                              gate_table=gate_table)
            if kind == 'claim':
                if detail['mine']:
                    # ts formats seen: 10-02 00:05 / 2026-10-07T22:33:00+08:00
                    ts = parse_ts(detail['ts'])
                    if ts and (now - ts) <= ROUND_WINDOW_MIN * 60:
                        fresh_claim = detail['ts']
            elif kind == 'struct_wait':
                struct_wait.append(detail)
            elif kind == 'claimable':
                claimable.append(detail)
    except Exception:
        pass
    return claimable, fresh_claim, struct_wait


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
    claimable, fresh_claim, struct_wait = parse_backlog(mid, now, vram_free_gb=vram)
    ram_ok = ram is None or ram >= RAM_GATE_PCT  # probe fail disclosed, not guessed
    vram_ok = vram is None or vram >= VRAM_GATE_GB
    # T-2026-10-10-183: vram_ok is disclosure-only (VRAM decoupled from the
    # CPU-only claim lane per O-20261010-1825 sec.3).
    green_idle = bool(ram_ok and not inflight)
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
        'vram_gate_satisfied': bool(vram_ok),
        'vram_gate_note': 'disclosure-only since T-2026-10-10-183 (O-20261010-1825 sec.3)',
        'inflight_reasons': inflight,
        'claimed_recent': fresh_claim is not None,
        'backlog_claimable_lines': len(claimable),
        'pool_ready_unclaimed': pool_ready_unclaimed(),
        # r1304: a card that names a shut gate or a face this disk does not hold is a
        # structural wait, published beside the count instead of inside it. Without this
        # split "three lines are claimable" and "nothing here can light" printed the same
        # face, and idle_rounds grew with no stated reason.
        'backlog_struct_wait_n': len(struct_wait),
        'backlog_struct_wait': struct_wait[:8],
        # r1305b: claimable is not the same as unconditional. A card that asks for a
        # negotiated window prints its clause here, and the count of such cards is
        # published beside the claimable count so "2 claimable" cannot be read as
        # "2 things this machine may start right now".
        'backlog_claimable_n_soft_gated': len([c for c in claimable if c.get('soft_gate')]),
        'backlog_claimable': claimable[:8],
        # deprecated alias: this is the BACKLOG line count, not the runnable
        # pool (see pool_ready_unclaimed / pool_count_note).
        'claimable_pool_lines': len(claimable),
        'pool_count_note': 'backlog_claimable_lines==fleet/backlog.md claim-by-file lines; '
                           'pool_ready_unclaimed==results/runnable_pool.json ready+unowned entries',
        'idle_rounds': idle_rounds,
        'agenda_starved': agenda_starved,
        'two_read_red': idle_rounds >= 2,
        'law_ref': 'O-20261007-2315 + resource-chain 8.2 + T-2026-10-10-183 vram-decouple',
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
    # T-2026-10-10-183: vram decoupled from the CPU-only claim lane -- the
    # gate no longer consumes the vram term; fixtures reflect the new law.
    ok = True
    def gate(ram, vram, inflight):
        ram_ok = ram is None or ram >= RAM_GATE_PCT
        return bool(ram_ok and not inflight)
    cases = [
        (50.0, 8.0, [], True, 'all-green'),
        (30.0, 8.0, [], False, 'ram-below-gate'),
        (50.0, 2.0, [], True, 'vram-below-gate-cpu-lane-allowed'),
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
    # r1119 two-face fixture: the runnable POOL count must not swallow owned or
    # non-ready entries, and an unreadable face must be None (not 0 -- 0 would
    # claim "no work" from a face we never read).
    pool_cases = [
        ([{'status': 'ready'}, {'status': 'claimed', 'owner': 'bm-c'},
          {'status': 'ready', 'owner': 'bm-a'}, {'status': 'done'},
          'not-a-dict'], 1, 'mixed'),
        ([], 0, 'empty'),
        (None, None, 'unreadable-face'),
    ]
    for entries, want, name in pool_cases:
        got = _count_pool_ready(entries)
        flag = 'PASS' if got == want else 'FAIL'
        if got != want:
            ok = False
        print('[%s] pool-ready %s -> %s' % (flag, name, got))
    # r1789: a card that names its own excluded machines must not count as claimable for
    # them, and must keep counting for everyone else (one machine's parked GPU is not
    # another machine's excuse). No marker, no exclusion.
    excl_cases = [
        ('19. card not-claimable-for: bm-c (gpu parked)', 'bm-c', True),
        ('19. card not-claimable-for: bm-c (gpu parked)', 'bm-b', False),
        ('19. card not-claimable-for: bm-a, bm-c', 'bm-c', True),
        ('19. card not-claimable-for: bm-b', 'bm-c', False),
        ('19. card with no marker', 'bm-c', False),
    ]
    for line, mid_, want in excl_cases:
        got = line_excluded(line, mid_)
        flag = 'PASS' if got == want else 'FAIL'
        if got != want:
            ok = False
        print('[%s] excluded %r for %s -> %s' % (flag, line[:34], mid_, got))
    # r1304: three states. Card 19 had been invisible for weeks because its own text
    # spells the claim syntax; cards 20-22 counted as work while naming a shut gate.
    # The reader now answers "can this disk light it", and a shut door is published
    # beside the count rather than inside it.
    no_disk = lambda _p: False
    any_disk = lambda _p: True
    state_cases = [
        # (line, exists, want_kind, want_detail_key)
        ('19. 【BigCompute】card (claimed 需写 claimed@<机>@<ts>)', no_disk,
         'claimable', None),
        ('19. 【BigCompute】card claimed@bm-b@2026-10-02T00:05:00+08:00', any_disk,
         'claim', 'mine'),
        ('20. 【BigCompute】card -workload=x execution-face: D:\\nowhere\\City3D', no_disk,
         'struct_wait', 'execution_face_missing'),
        ('20. 【BigCompute】card execution-face: D:\\here\\City3D', any_disk,
         'claimable', None),
        ('21. 【BigCompute】card **gate 现状=CLOSED** 算力窗到了才能点火', any_disk,
         'struct_wait', 'gate_closed'),
        ('22. 【BigCompute】card remains', any_disk, 'claimable', None),
        ('23. 【BigCompute】card not-claimable-for: bm-a', any_disk, 'drop', None),
        ('1. 【城线】card —claimed@bm-c 生产泵@10-01 → done@10-02 00:05+MiniGame 1ffc', any_disk,
         'drop', None),
        ('not a pool row', any_disk, 'drop', None),
    ]
    for line, exists, want_kind, want_reason in state_cases:
        kind, detail = classify_pool_line(line, 'bm-a', exists=exists)
        good = kind == want_kind and (want_reason is None or detail.get('reason') == want_reason
                                     or (want_reason == 'mine' and detail.get('mine') is False))
        flag = 'PASS' if good else 'FAIL'
        if not good:
            ok = False
        print('[%s] pool-state %r -> %s/%s' % (flag, line[:38], kind,
                                              detail.get('reason') if isinstance(detail, dict) else detail))
    # r1305: the GPU door as a number. A card that states `headroom>=n GB` is claimable
    # only when the probe reads at least n; an unmeasured door is not an open door; and
    # `与 <card> 同 gate` inherits that card's number rather than inventing an open door.
    gate_cases = [
        # (line, vram_free_gb, gate_table, want_kind, want_reason, want_extra)
        ('20. 【BigCompute/B-CITY3D-01】card headroom>=1.5GB', 1.48,
         None, 'struct_wait', 'vram_short', {'needs_gb': 1.5, 'have_gb': 1.48,
                                             'short_gb': 0.02}),
        ('20. 【BigCompute/B-CITY3D-01】card headroom>=1.5GB', 3.0,
         None, 'claimable', None, None),
        ('20. 【BigCompute/B-CITY3D-01】card headroom>=1.5GB', None,
         None, 'struct_wait', 'vram_unknown', {'needs_gb': 1.5}),
        ('21. 【BigCompute/B-CITY3D-02】card 与 B-CITY3D-01 同 gate（vram 窗）', 1.48,
         {'B-CITY3D-01': 1.5}, 'struct_wait', 'vram_short', {'how': 'inherited:B-CITY3D-01'}),
        ('21. 【BigCompute/B-CITY3D-02】card 与 B-CITY3D-01 同 gate（vram 窗）', 1.48,
         None, 'struct_wait', 'gate_inherited', {'ref': 'B-CITY3D-01'}),
        # a card with no GPU door at all must not be dragged into one by the probe
        ('22. 【BigCompute/B-XIDUDU-02】card **无算力门槛** 他司会话优先不抢', 0.1,
         None, 'claimable', None, None),
    ]
    for line, vram, table, want_kind, want_reason, want_extra in gate_cases:
        kind, detail = classify_pool_line(line, 'bm-a', exists=any_disk,
                                          vram_free_gb=vram, gate_table=table)
        good = kind == want_kind and (want_reason is None or detail.get('reason') == want_reason)
        if good and want_extra:
            for k, want_v in want_extra.items():
                if detail.get(k) != want_v:
                    good = False
        flag = 'PASS' if good else 'FAIL'
        if not good:
            ok = False
        print('[%s] gate %r vram=%s -> %s/%s %s' % (
            flag, line[:40], vram, kind,
            detail.get('reason') if isinstance(detail, dict) else detail,
            {k: detail.get(k) for k in ('needs_gb', 'have_gb', 'short_gb', 'how', 'ref')}
            if isinstance(detail, dict) else ''))
    # r1305b: a card whose door is a negotiation is claimable, but the clause must be
    # printed instead of hidden -- otherwise "2 claimable" reads as "2 may start now".
    soft_cases = [
        ('22. 【BigCompute/B-XIDUDU-02】card 资源=GUI 会话档，他司会话优先不抢；验收=截图',
         '他司会话优先不抢'),
        ('21. 【BigCompute/B-XIDUDU-01】card 构建窗与他司产线协商让路；验收=构建报告',
         '与他司产线协商让路'),
        ('23. 【BigCompute/B-OTHER】card 资源=CPU 档；验收=报告', None),
    ]
    for line, want_soft in soft_cases:
        kind, detail = classify_pool_line(line, 'bm-a', exists=any_disk)
        got = detail.get('soft_gate') if isinstance(detail, dict) else None
        good = kind == 'claimable' and got == want_soft
        flag = 'PASS' if good else 'FAIL'
        if not good:
            ok = False
        print('[%s] soft-gate %r -> %s' % (flag, line[:38], got))
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
