import subprocess, json, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# classify M files: wall-clock direction between worktree copy and origin/main blob
files = subprocess.check_output(['git', 'diff', '--name-only']).decode().split()
TS_KEYS = ['updated', 'now', 'generated', 'ts', 'generated_at', 'asof', 'last_run', 'run_at']
for f in files:
    try:
        local = open(f, encoding='utf-8-sig').read()
    except Exception:
        local = ''
    origin = subprocess.check_output(['git', 'show', f'origin/main:{f}'], stderr=subprocess.DEVNULL).decode('utf-8', 'replace')
    def stamps(txt):
        s = set(re.findall(r'2026-10-01[ T]?(\d{2}:\d{2}:\d{2})', txt))
        return max(s) if s else ''
    ls, os_ = stamps(local), stamps(origin)
    verdict = 'LOCAL-NEWER' if ls > os_ else ('ORIGIN-NEWER' if os_ > ls else 'SAME/none')
    print(f"{verdict:14} | local {ls or '-'} | origin {os_ or '-'} | {f}")
