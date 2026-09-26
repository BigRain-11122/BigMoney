# _r254bma_t80_progress.py -- append progress_r254 (dA closure, receiver lane) to T-80 ticket
# Byte-mirror per R254 law: no BOM, CRLF, indent=1, ensure_ascii=False (probed).
import json, sys

PATH = 'fleet/tasks/T-2026-09-26-80-P1.json'
NOTE = ("R254 bm-a (lane owner) dA basis adjudication CLOSED CLEAN via T-82 transfer: bm-b originals "
        "received byte-exact (sha 79585a95/f09329f4 = sender manifest; transfer_manifest VERIFY PASS; "
        "receiver json written) + semantic comparison results/_r254bma_da_compare.py = row-multiset "
        "byte-identical 8294x2 rows x 27 fields zero diffs -- sha mismatch = pure line-emission order "
        "permutation (parallel worker write order), not even float noise; two-machine independent "
        "re-run reproduces the identical cell set = census+passive-gate discipline held. Landed run "
        "stands; results/t54/cells_deep_*_dA.jsonl on bm-a now = bm-b sender-manifest originals. "
        "Correction of R253 record (append-only addendum in pool harvest_note): quoted 'mine' hashes "
        "934a7fb6/e839b78c were mis-attributed to the dA family -- they are the t22 canon CE deep family "
        "(6 CE x 1506, different family); correct mine-dA hashes 9764513c/c11d1b6d, mismatch real but "
        "permutation-only, transfer request protocol-correct. Reply MSG-20260926-1531-bm-a; T-82 close "
        "face complete on receiver side (both manifests + verdict)")

def main():
    raw = open(PATH, 'rb').read()
    assert raw[:3] != b'\xef\xbb\xbf'
    t = json.loads(raw.decode('utf-8'))
    assert 'progress_r254' not in t, 'idempotency'
    assert t['status'] == 'claimed' and t['claimed_by'].startswith('bm-b'), 'owner face drifted'
    items = list(t.items())
    out = {}
    for k, v in items:
        out[k] = v
        if k == 'progress_r256':
            out['progress_r254'] = NOTE
    assert 'progress_r254' in out, 'anchor key progress_r256 not found'
    s = json.dumps(out, indent=1, ensure_ascii=False) + '\n'
    rt = json.loads(s)
    assert rt['progress_r254'] == NOTE and rt['status'] == 'claimed'
    open(PATH, 'wb').write(s.replace('\n', '\r\n').encode('utf-8'))
    back = json.loads(open(PATH, 'rb').read().decode('utf-8-sig'))
    assert back['progress_r254'] == NOTE
    print('progress_r254 appended+verified; owner faces intact')
    return 0

if __name__ == '__main__':
    sys.exit(main())
