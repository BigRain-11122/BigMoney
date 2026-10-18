# BmaIdleGuard v2 -- bm-a 10-min idle guard, CANON-ADOPTED from
# cph4/fleet/idle-guard-kit/bmc_idleguard.py (canon landed on group origin r1070,
# adopt law = O-20261018-2236-bm-c sec.3.1 "<=1 round after bm-c push").
# Localization spots (order sec.3.1): PYW path = this file (Tools/bma_idleguard.pyw),
# bank file name = cph4/fleet/work-bank/bm-a-gpu-bank.json, SYS_PY = this interpreter.
# Adopted from canon: bank schema + claim logic (status=pending + require.files_at_least,
# claimed_ts, PRODUCER VIOLATION exposure on empty/absent bank, atomic tmp+replace writes,
# ComfyUI queue-busy parity face), two-hop >=600s, pause-window zero action.
# Deliberate bm-a deltas (documented, spec-faithful):
#   - GPU busy face = nvidia-smi util>=20 OR non-whitelist compute-proc >=800MiB:
#     immune BY CONSTRUCTION to canon pit C2059 (CommandLine pattern self-match),
#     no process-name pattern guessing; resident services whitelisted.
#   - SatEngine revive = bm-a canon recipe (register_satengine_task.ps1 + tick),
#     not direct engine spawn; status probe = direct rc (no CommandLine matching).
#   - JSONL structured log w/ rotation (sentinel observability face).
#   - claim spawn failure reverts job to pending (canon strands claimed-never-fired;
#     bm-c manual-deblock precedent shows the strand cost).
# Zero-network by design except localhost ComfyUI queue probe. Silent on all errors
# (guard must never crash-loop); every fire logs one JSONL line.
import json, subprocess, sys, time, datetime, os, io, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bigmoney repo root
GROUP = r'C:\Users\sjs20\Desktop\FluxGroup'                            # bm-a group tree
SENT = os.path.join(os.path.expanduser('~'), '.codely-cli', 'sentinel')
LOG = os.path.join(SENT, 'bma-idleguard.log')
STATE = os.path.join(SENT, 'bma-idleguard-state.json')
FLAG = os.path.join(GROUP, '.codely-cli', 'machine-state.flag')       # CEO yield window
BANK = os.path.join(GROUP, 'cph4', 'fleet', 'work-bank', 'bm-a-gpu-bank.json')
RESIDENT_WHITELIST = ('llama-server', 'ollama')   # resident services = not a burn
BURN_MEM_MB = 800        # non-whitelist GPU proc at/above this = busy burn face
UTIL_BUSY = 20           # nvidia-smi util % >= this = busy (order spec)
TWO_HOP_S = 600          # >=600s between idle mark and action (order spec)
GUARD_ID = 'bma-idleguard-v2-canon'
NO_WINDOW = 0x08000000


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def log(rec):
    try:
        os.makedirs(SENT, exist_ok=True)
        with io.open(LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=True) + '\n')
        with io.open(LOG, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if len(lines) > 2000:
            with io.open(LOG, 'w', encoding='utf-8') as f:
                f.writelines(lines[-1000:])
    except Exception:
        pass


def load_json(p, default):
    try:
        with io.open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json_atomic(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + '.tmp'
        with io.open(tmp, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=True, indent=1)
        os.replace(tmp, p)
        return True
    except Exception:
        return False


def pause_flagged():
    try:
        with io.open(FLAG, 'r', encoding='ascii', errors='replace') as f:
            word = f.read().strip().split(' ')[0].lower()
        return word == 'pause'
    except Exception:
        return False


def gpu_face():
    # returns dict(gpu_busy, util, burn_procs, probe)
    try:
        u = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu',
                            '--format=csv,noheader,nounits'],
                           capture_output=True, text=True, timeout=30,
                           creationflags=NO_WINDOW)
        util = int(u.stdout.strip().splitlines()[0]) if u.returncode == 0 else -1
    except Exception:
        return {'gpu_busy': True, 'util': -1, 'burn_procs': [], 'probe': 'util_probe_failed'}
    burns = []
    try:
        p = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory',
                            '--format=csv,noheader'], capture_output=True, text=True, timeout=30,
                           creationflags=NO_WINDOW)
        if p.returncode == 0:
            for ln in p.stdout.strip().splitlines():
                parts = [x.strip() for x in ln.split(',')]
                if len(parts) >= 3:
                    name = parts[1].lower()
                    try:
                        mem = int(parts[2].replace('MiB', '').strip() or 0)
                    except ValueError:
                        mem = 0
                    if mem >= BURN_MEM_MB and not any(w in name for w in RESIDENT_WHITELIST):
                        burns.append(parts[1])
    except Exception:
        return {'gpu_busy': True, 'util': util, 'burn_procs': [], 'probe': 'proc_probe_failed'}
    busy = util >= UTIL_BUSY or len(burns) > 0
    return {'gpu_busy': busy, 'util': util, 'burn_procs': burns, 'probe': 'ok'}


def queue_busy():
    # canon parity face: ComfyUI queue probe (no server on bm-a typical = False)
    try:
        q = json.loads(urllib.request.urlopen('http://127.0.0.1:8188/queue', timeout=8).read())
        return bool(q.get('queue_running') or q.get('queue_pending'))
    except Exception:
        return False


def satengine_status():
    try:
        r = subprocess.run([sys.executable, os.path.join('scripts', 'saturation_engine.py'), 'status'],
                            cwd=ROOT, capture_output=True, text=True, timeout=120,
                            creationflags=NO_WINDOW)
        return 0 if r.returncode == 0 else 1
    except Exception:
        return 2  # unknown -> treat as alive (fail-safe: no revival on unknown)


def satengine_revive():
    try:
        subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                        '-File', os.path.join(ROOT, 'Tools', 'register_satengine_task.ps1')],
                       cwd=ROOT, capture_output=True, timeout=300, creationflags=NO_WINDOW)
        subprocess.run([sys.executable, os.path.join('scripts', 'saturation_engine.py'), 'tick'],
                       cwd=ROOT, capture_output=True, timeout=300, creationflags=NO_WINDOW)
        return 'revived'
    except Exception:
        return 'revive_failed'


def require_ok(job):
    req = job.get('require', {}) or {}
    for d, pat, n in req.get('files_at_least', []):
        full = os.path.join(GROUP, d)
        cnt = len([f for f in os.listdir(full) if f.endswith(pat)]) if os.path.isdir(full) else 0
        if cnt < int(n):
            return False
    return True


def try_claim(mark_age_s):
    """Canon bank claim: first status=pending job with require satisfied."""
    if not os.path.exists(BANK):
        return 'producer_exposure_bank_absent'
    bank = load_json(BANK, None)
    if not isinstance(bank, dict) or not isinstance(bank.get('jobs'), list):
        return 'producer_exposure_bank_unreadable'
    claimed = None
    for job in bank['jobs']:
        if job.get('status') == 'pending' and require_ok(job):
            claimed = job
            break
    if not claimed:
        return 'producer_exposure_bank_empty'  # canon: bank EMPTY -- PRODUCER VIOLATION
    claimed['status'] = 'claimed'
    claimed['claimed_ts'] = now_iso()
    claimed['claimed_by'] = GUARD_ID
    for job in bank['jobs']:
        if job.get('id') == claimed['id']:
            job.update(claimed)
    if not save_json_atomic(BANK, bank):
        return 'claim_bank_write_failed'
    try:
        lo = open(os.path.join(GROUP, claimed['log_out']), 'wb')
        le = open(os.path.join(GROUP, claimed['log_err']), 'wb')
        subprocess.Popen(claimed['cmd'], creationflags=NO_WINDOW, stdout=lo, stderr=le)
        lo.close(); le.close()
    except Exception as e:
        claimed['status'] = 'pending'
        claimed['claimed_ts'] = now_iso() + '-reverted-spawnfail'
        claimed['claimed_by'] = GUARD_ID + '-spawnfail'
        for job in bank['jobs']:
            if job.get('id') == claimed['id']:
                job.update(claimed)
        save_json_atomic(BANK, bank)
        return 'claim_spawn_failed_reverted:' + str(e)[:120]
    return 'claimed-fired:' + str(claimed.get('id'))


def main():
    ts = now_iso()
    rec = {'ts': ts, 'guard': GUARD_ID}
    if pause_flagged():
        save_json_atomic(STATE, {'ts': ts, 'idle_since': None})
        log(dict(rec, pause=True, action='yield-window-zero-action'))
        return
    g = gpu_face()
    se = satengine_status()
    qbusy = queue_busy()
    actions = []
    if se == 1:
        actions.append('satengine_' + satengine_revive())
    st = load_json(STATE, {})
    gpu_idle = (not g['gpu_busy']) and (not qbusy)
    if not gpu_idle:
        save_json_atomic(STATE, {'ts': ts, 'idle_since': None})
        log(dict(rec, pause=False, gpu=g, queue_busy=qbusy, satengine=se,
                 actions=actions, action='busy-clear-mark'))
        return
    prev = st.get('idle_since')
    if not prev:
        save_json_atomic(STATE, {'ts': ts, 'idle_since': ts})
        log(dict(rec, pause=False, gpu=g, queue_busy=qbusy, satengine=se,
                 actions=actions, action='hop1-idle-marked'))
        return
    try:
        age = (datetime.datetime.now() - datetime.datetime.fromisoformat(prev)).total_seconds()
    except Exception:
        age = -1
    if age >= TWO_HOP_S:
        claim = try_claim(age)
        actions.append(claim)
        # claim consumed the idle window; keep mark so producer exposure repeats
        save_json_atomic(STATE, {'ts': ts, 'idle_since': prev})
        log(dict(rec, pause=False, gpu=g, queue_busy=qbusy, satengine=se,
                 mark_age_s=age, actions=actions, action='hop2-idle-confirmed'))
    else:
        log(dict(rec, pause=False, gpu=g, queue_busy=qbusy, satengine=se,
                 mark_age_s=age, actions=actions, action='hop-wait'))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log({'ts': now_iso(), 'guard': GUARD_ID, 'fatal': str(e)[:200]})
