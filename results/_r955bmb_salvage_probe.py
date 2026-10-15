# r955 salvage probe: try git index-pack --fix-thin on orphaned tmp_packs from killed
# fetch/push chains. Complete packs index fine; salvage = free objects, zero network.
import os, subprocess, time, json

bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
packdir = os.path.join(bm, '.git', 'objects', 'pack')
LOG = os.path.join(bm, 'results', '_r955bmb_salvage.log')
OUT = os.path.join(bm, 'results', '_r955bmb_salvage_receipt.json')

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%dT%H:%M:%S') + ' ' + m + '\n')

W('salvage probe start')
results = []
tmps = sorted(x for x in os.listdir(packdir) if x.startswith('tmp_pack'))
W('tmp_packs found=%d' % len(tmps))
ok_count = 0
for t in tmps:
    src = os.path.join(packdir, t)
    sz = os.path.getsize(src)
    t0 = time.time()
    r = subprocess.run(['git', '-C', bm, 'index-pack', '-v', '--fix-thin', src],
                       capture_output=True, timeout=600)
    el = round(time.time() - t0, 1)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    ok = r.returncode == 0
    # index-pack on success: writes <tmp>.idx? no - check for new pack files
    if ok:
        ok_count += 1
    results.append({'pack': t, 'bytes': sz, 'rc': r.returncode, 'elapsed': el,
                    'tail': out.strip().split('\n')[-1][:120] if out.strip() else ''})
    W('%s bytes=%d rc=%s elapsed=%ss tail=%s' % (t, sz, r.returncode, el,
      (out.strip().split('\n')[-1][:100] if out.strip() else '')))

# check what idx/pack files appeared next to tmps
idx_next = [x for x in os.listdir(packdir) if x.endswith('.idx')]
W('idx files in packdir now=%d (canonical packs=%d)' % (
    len(idx_next), len([x for x in os.listdir(packdir) if x.startswith('pack') and x.endswith('.pack')])))
json.dump({'salvage_ok_packs': ok_count, 'total': len(tmps), 'details': results},
          open(OUT, 'w', encoding='utf-8'), indent=1)
W('salvage probe done ok=%d/%d' % (ok_count, len(tmps)))
