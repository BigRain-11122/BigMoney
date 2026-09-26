# _r254bma_pool_addendum.py -- append-only harvest_note addendum on T80 pool entry (R254 dA closure)
# Byte-mirror discipline per R254 law: probed original = no BOM, CRLF, indent=1, ensure_ascii=False.
# Appends one addendum sentence to the existing harvest_note; original text untouched; verifies
# round-trip serialization of the untouched prefix before write. Exit 0 on success.
import json, sys

PATH = 'results/runnable_pool.json'
ADDENDUM = (" || R254 addendum: dA transfer received+verified byte-exact (T-82; receiver manifest "
            "fleet/transfers/T-2026-09-26-82-receiver.json, VERIFY PASS) + semantic comparison "
            "results/_r254bma_da_compare/verdict.json = row-multiset byte-identical 8294x2, zero "
            "field/null diffs, sha mismatch = pure line-emission order permutation -> dA basis "
            "adjudication CLOSED CLEAN, landed run stands; correction of R253 record: quoted 'mine' "
            "hashes 934a7fb6/e839b78c were mis-attributed (t22 canon CE deep family, different "
            "family) -- correct mine-dA hashes 9764513c/c11d1b6d, mismatch real but permutation-only; "
            "results/t54/cells_deep_*_dA.jsonl on bm-a now = bm-b sender-manifest originals "
            "(sha 79585a95/f09329f4), mine re-run copies preserved evidence-only at "
            "results/_r254bma_da_compare/ (gitignored)")

def main():
    raw = open(PATH, 'rb').read()
    assert raw[:3] != b'\xef\xbb\xbf', 'BOM face drifted'
    pool = json.loads(raw.decode('utf-8'))
    entries = pool['entries'] if isinstance(pool, dict) and 'entries' in pool else pool
    hit = None
    for e in entries:
        if e.get('id') == 'T80-AGGR-FULLPOOL-BATTERY':
            hit = e
            break
    assert hit, 'T80 entry absent'
    sh = hit['shards'][0]
    hn = sh['harvest_note']
    assert 'R254 addendum' not in hn, 'addendum already present (idempotency)'
    assert hn.endswith('not bm-b bytes'), 'unexpected harvest_note tail: ' + hn[-60:]
    sh['harvest_note'] = hn + ADDENDUM
    out = json.dumps(pool, indent=1, ensure_ascii=False) + '\n'
    # round-trip + prefix-integrity: original note must be a byte-prefix of new note
    rt = json.loads(out)
    nhn = [e for e in (rt['entries'] if isinstance(rt, dict) and 'entries' in rt else rt)
           if e.get('id') == 'T80-AGGR-FULLPOOL-BATTERY'][0]['shards'][0]['harvest_note']
    assert nhn.startswith(hn) and nhn.endswith(ADDENDUM)
    open(PATH, 'wb').write(out.replace('\n', '\r\n').encode('utf-8'))
    # post-write verification
    back = json.loads(open(PATH, 'rb').read().decode('utf-8-sig'))
    e2 = [e for e in (back['entries'] if isinstance(back, dict) and 'entries' in back else back)
          if e.get('id') == 'T80-AGGR-FULLPOOL-BATTERY'][0]
    assert e2['shards'][0]['harvest_note'] == hn + ADDENDUM
    assert e2['status'] == 'done' and e2['shards'][0]['status'] == 'done', 'status faces must not drift'
    print('harvest_note addendum appended+verified; entry statuses intact (done/done)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
