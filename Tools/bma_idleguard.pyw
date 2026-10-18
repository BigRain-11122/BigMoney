# BmaIdleGuard -- bm-a interim 10-min idle guard (O-20261018-2236-bm-c sec.2.1 spec).
# Canonical kit (cph4/fleet/idle-guard-kit/) is pending bm-c push to group origin
# (MSG-20261018-2310-bma-idleguard-kit-push); this interim guards the live CEO
# 10-min SLA now and will be canon-adopted (replaced by the kit face) when it lands.
# Three localizable spots per order sec.3.1: PYW path (this file), bank file name
# (BANK_FILE), SYS_PY (registered action exe). Zero-network by design. Silent on
# all errors (guard must never crash-loop); every fire logs one JSONL line.
import json, subprocess, sys, time, datetime, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bigmoney repo root
SENT = os.path.join(os.path.expanduser('~'), '.codely-cli', 'sentinel')
LOG = os.path.join(SENT, 'bma-idleguard.log')
STATE = os.path.join(SENT, 'bma-idleguard-state.json')
FLAG = r'C:\Users\sjs20\Desktop\FluxGroup\.codely-cli\machine-state.flag'   # CEO yield window
BANK = r'C:\Users\sjs20\Desktop\FluxGroup\cph4\fleet\work-bank\bm-a-gpu-bank.json'
RESIDENT_WHITELIST = ('llama-server', 'ollama')   # resident services = not a burn
BURN_MEM_MB = 800        # non-whitelist GPU proc at/above this = busy burn face
UTIL_BUSY = 20           # nvidia-smi util % >= this = busy (order spec)
TWO_HOP_S = 600          # >=600s between idle mark and action (order spec)

def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')

def log(rec):
    try:
        os.makedirs(SENT, exist_ok=True)
        line = json.dumps(rec, ensure_ascii=True) + '\n'
        with io.open(LOG, 'a', encoding='utf-8') as f:
            f.write(line)
        with io.open(LOG, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if len(lines) > 2000:
            with io.open(LOG, 'w', encoding='utf-8') as f:
                f.writelines(lines[-1000:])
    except Exception:
        pass

def load_state():
    try:
        with io.open(STATE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(st):
    try:
        os.makedirs(SENT, exist_ok=True)
        with io.open(STATE, 'w', encoding='utf-8') as f:
            json.dump(st, f, ensure_ascii=True)
    except Exception:
        pass

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
                            capture_output=True, text=True, timeout=30)
        util = int(u.stdout.strip().splitlines()[0]) if u.returncode == 0 else -1
    except Exception:
        return {'gpu_busy': True, 'util': -1, 'burn_procs': [], 'probe': 'util_probe_failed'}
    burns = []
    try:
        p = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory',
                            '--format=csv,noheader'], capture_output=True, text=True, timeout=30)
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

def satengine_status():
    try:
        r = subprocess.run([sys.executable, os.path.join('scripts', 'saturation_engine.py'), 'status'],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        return 0 if r.returncode == 0 else 1
    except Exception:
        return 2  # unknown -> treat as alive (fail-safe: no revival on unknown)

def satengine_revive():
    try:
        subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                        '-File', os.path.join(ROOT, 'Tools', 'register_satengine_task.ps1')],
                       cwd=ROOT, capture_output=True, timeout=300)
        subprocess.run([sys.executable, os.path.join('scripts', 'saturation_engine.py'), 'tick'],
                       cwd=ROOT, capture_output=True, timeout=300)
        return 'revived'
    except Exception:
        return 'revive_failed'

def main():
    ts = now_iso()
    rec = {'ts': ts, 'guard': 'bma-interim-v1'}
    if pause_flagged():
        save_state({'ts': ts, 'idle_since': None})
        log(dict(rec, pause=True, action='yield-window-zero-action'))
        return
    g = gpu_face()
    se = satengine_status()
    actions = []
    if se == 1:
        actions.append('satengine_' + satengine_revive())
    st = load_state()
    gpu_idle = not g['gpu_busy']
    if not gpu_idle:
        st = {'ts': ts, 'idle_since': None}
        save_state(st)
        log(dict(rec, pause=False, gpu=g, satengine=se, actions=actions,
                 action='busy-clear-mark'))
        return
    prev = st.get('idle_since')
    if not prev:
        save_state({'ts': ts, 'idle_since': ts})
        log(dict(rec, pause=False, gpu=g, satengine=se, actions=actions,
                 action='hop1-idle-marked'))
        return
    try:
        age = (datetime.datetime.now() - datetime.datetime.fromisoformat(prev)).total_seconds()
    except Exception:
        age = -1
    if age >= TWO_HOP_S:
        if not os.path.exists(BANK):
            actions.append('producer_exposure_bank_absent')
        else:
            # canonical bank present but schema pending canon-adopt: no guess-claim
            actions.append('bank_present_claim_pending_canon_adopt')
        log(dict(rec, pause=False, gpu=g, satengine=se, mark_age_s=age, actions=actions,
                 action='hop2-idle-confirmed'))
        save_state({'ts': ts, 'idle_since': prev})
    else:
        log(dict(rec, pause=False, gpu=g, satengine=se, mark_age_s=age, actions=actions,
                 action='hop-wait'))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log({'ts': now_iso(), 'guard': 'bma-interim-v1', 'fatal': str(e)[:200]})
