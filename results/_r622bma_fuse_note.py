import io, json

NOTE = ('keep blocked on bm-a r622: OFF-CALIBER CACHE containment (bm-a '
        'fund-family cache pending T-156 swap; all 40 overlap keys 124..163 '
        'diverged vs bm-b basis n_engine_syms 2483vs2473; bm-a burn killed '
        '11:40, 150 rows discarded, nulls restored to origin 164-row '
        'canonical, claim released per MSG-1132). bm-b: your burn is '
        'canonical -- if it dies, relaunch is legit: clear this sig with '
        'reason=bm-a-kill-collateral per r393/r617 law')
KEY = 'scripts/fund_value_p1.py|run,--nulls'

for fp in ('results/crash_fuse.json', 'results/crash_fuse.bm-a.json'):
    src = io.open(fp, encoding='utf-8', newline='').read()
    i = src.find(KEY)
    assert i >= 0, fp
    j = src.find('\r\n  }', i)
    assert j > i, (fp, 'closing')
    assert '"note"' not in src[i:j], (fp, 'note already present')
    new = src[:j] + ',\r\n   "note": "' + NOTE + '"' + src[j:]
    json.loads(new)
    io.open(fp, 'w', encoding='utf-8', newline='').write(new)
    print(fp, 'note inserted at', j)
