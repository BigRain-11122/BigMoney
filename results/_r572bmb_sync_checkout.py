import subprocess, os

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'

def git(args):
    return subprocess.run(['git', '-C', REPO] + args, capture_output=True)

keep_local = {
    'results/autofill_state.bm-b.json',
    'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
    'results/pool_core_samples.jsonl',  # already union-merged this round
}
status = git(['status', '--porcelain']).stdout.decode('utf-8', 'replace')
checkout = []
for raw in status.splitlines():
    if len(raw) < 4:
        continue
    st = raw[:2]
    path = raw[3:]
    if path in keep_local:
        continue
    if st.strip() in ('D', 'M'):
        checkout.append(path)
print('CHECKOUT_COUNT=%d' % len(checkout))
r = git(['checkout', '--'] + checkout)
print('BATCH_RC=%d' % r.returncode)
if r.returncode != 0:
    print(r.stderr.decode('utf-8', 'replace')[:300])
    ok = 0
    for p in checkout:
        r2 = git(['checkout', '--', p])
        if r2.returncode != 0:
            print('FAIL %s: %s' % (p, r2.stderr.decode('utf-8', 'replace')[:120]))
        else:
            ok += 1
    print('PER-FILE OK=%d/%d' % (ok, len(checkout)))
print('===FINAL STATUS===')
print(git(['status', '--porcelain']).stdout.decode('utf-8', 'replace'))
