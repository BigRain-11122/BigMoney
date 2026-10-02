# r582 bm-b S7 self-heal (loop task, watchdog, pre-commit/pre-push claws) -- python argv, zero PS quoting
import subprocess, os, sys

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)
PS = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File']

def ps(script):
    r = subprocess.run(PS + [script], capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ''

rc, last = ps(r'Tools\register_loop_task.ps1')
print('loop_task rc=%s | %s' % (rc, last))

r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                    '-File', r'Tools\Invoke-SilentExe.ps1',
                    '-ExePath', 'schtasks', '-Arguments', '/query', '/tn', 'Bigmoney-LoopWatchdog'],
                   capture_output=True, text=True, timeout=60)
if r.returncode != 0:
    rc, last = ps(r'Tools\register_watchdog_task.ps1')
    print('watchdog MISSING -> re-registered rc=%s | %s' % (rc, last))
else:
    print('watchdog OK')

def claw(name, register):
    hook = os.path.join('.git', 'hooks', name)
    canon = os.path.join('Tools', 'git-hooks', name)
    a = open(hook, encoding='utf-8', errors='replace').read().replace('\r', '') if os.path.exists(hook) else None
    b = open(canon, encoding='utf-8', errors='replace').read().replace('\r', '') if os.path.exists(canon) else None
    if a != b:
        rc, last = ps(register)
        print('%s claw MISSING/DIFF -> re-installed rc=%s | %s' % (name, rc, last))
    else:
        print('%s claw OK' % name)

claw('pre-commit', r'Tools\register_precommit_claw.ps1')
claw('pre-push', r'Tools\register_prepush_claw.ps1')
