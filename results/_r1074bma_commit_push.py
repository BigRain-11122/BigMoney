# r1074 bm-a: commit + push (claw-guarded), with one pull --rebase retry on race
import subprocess, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
def g(*args):
    r = subprocess.run(['git','-C',REPO]+list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '')+(r.stderr or '')
rc, out = g('status','--porcelain=v1','-uall')
print('status head:'); print('\n'.join(out.splitlines()[:15]))
rc, _ = g('add','-A')
print('add rc', rc)
MSG = ('round 1074: A5 acceptance-record carrier landed (scripts/a5_acceptance_pack.py, frozen V1-V5 machine-read, '
       'selftest 10/10; live V1/V3/V4 PASS + V2 1/5 + V5 1/3 honest PENDING, S6 standing leg) + group-plan BigMoney '
       'section CAS refresh + detail pointer first-try (e9b916301561 group-side, receipt on disk) + sequence repair '
       '(r1073 closeout state write lost in rebase-race surgery, canonical face governs, round_no -> 1075) + '
       'S6 45-leg all rc0 + smoke 49/49 + board CLEAN + D-19 dual HOLD')
rc, out = g('commit','-m',MSG)
print('commit rc', rc, out.strip()[:300])
if rc == 0:
    rc, out = g('rev-parse','HEAD'); head = out.strip(); print('HEAD', head[:12])
    rc, out = g('push')
    print('push rc', rc, out.strip()[:300])
    if rc != 0:
        print('-- push rejected: one pull --rebase retry --')
        rc2, out2 = g('pull','--rebase','--autostash')
        print('pull rc', rc2, out2.strip()[:200])
        if rc2 == 0:
            rc3, out3 = g('push')
            print('push#2 rc', rc3, out3.strip()[:300])
            sys.exit(0 if rc3 == 0 else 1)
        sys.exit(1)
    sys.exit(0)
print('commit failed'); sys.exit(1)
