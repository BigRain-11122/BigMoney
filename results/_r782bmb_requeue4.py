"""r782 bm-b P0: V re-queue take-3 -- shared+bm-b re-clobber cure.

18:08:22 settle wrote the merged view (then still done via stale
mirrors) back into shared + bm-b lane, restoring entry done@15:50:03 +
5 done/harvest field lines 2 seconds BEFORE the mirror heal landed
(18:08:24) -- requeue3's idempotency guard then false-skipped (it
matched the shard-level '"status": "ready"' inside the block).
Take-3 fixes the guard: surgery needed iff an entry-level
'"status": "done",' line exists. Clobbered shape probed by
_r782bmb_probe_v.py: 1 done-status line (entry only), 5 del-field
lines, lane_owner already pinned (no insert), owner_since bump, r782
provenance note. After this, ALL FOUR faces ready in one window ->
merged ready -> settles converge ready (stable fixed point).
Laws: pit-pool-edit r509/r500 raw-text anchored, r694 entry-region
needle, r629 trailing comma (generic), r678/r705 reparse+count+delta
gates; treasure_guard restore rc0 both paths this round (pre-write).
"""
import json
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOLS = ['results/runnable_pool.json', 'results/runnable_pool.bm-b.json']
ID_N = '"FUND-VALUE-P1-NULLS"'
PROV = (" | rel-bm-b-r782 2026-10-06: take-3 -- 18:08:22 settle "
        "re-clobbered shared+bm-b from done-merged view 2s before mirror "
        "heal; guard fixed to entry-level done; four-face ready fixed "
        "point; re-ignite 14 missing ks rng([20500000,k])")


def v_block(raw):
    i = raw.find(ID_N)
    assert i > 0, "V entry id not found"
    j = raw.rfind('{', 0, i)
    depth = 0
    k = j
    while k < len(raw):
        if raw[k] == '{':
            depth += 1
        elif raw[k] == '}':
            depth -= 1
            if depth == 0:
                break
        k += 1
    return raw[j:k + 1], j, k


def fix_dangling_comma(lines):
    """r629 generic: strip trailing comma on last field line before each
    structural close ('}' / ']' family)."""
    fixed = 0
    for n in range(1, len(lines)):
        t = lines[n].strip()
        if t in ('}', ']', '},', '],'):
            p = lines[n - 1].rstrip()
            if p.endswith(','):
                lines[n - 1] = p[:-1]
                fixed += 1
    return fixed


for path in POOLS:
    raw = open(path, encoding='utf-8', newline='').read()
    n_before = raw.count('\n')
    block, j, k = v_block(raw)
    assert '"runner": "scripts/fund_value_p1.py"' in block, "block sanity"
    eol = '\r\n' if '\r\n' in block else '\n'
    lines = block.split(eol)
    assert len(lines) > 30, "block too small -- EOL probe mismatch"

    # guard (take-3 fixed): needed iff an entry/shard-level done status
    # line remains anywhere in the block
    st = [n for n, l in enumerate(lines)
          if l.strip() == '"status": "done",']
    if not st:
        print(f"{path}: V already ready -- skip (no-op)")
        continue
    assert len(st) == 1, f"expected 1 done-status line, got {len(st)}: {st}"
    lines[st[0]] = lines[st[0]].replace('"done"', '"ready"')

    # bump owner_since to NOW (r311 latest.ts law)
    ow = [n for n, l in enumerate(lines)
          if l.strip().startswith('"owner_since":')]
    assert len(ow) == 1, f"expected 1 owner_since line, got {len(ow)}"
    old_ts = lines[ow[0]].split('"')[3]
    lines[ow[0]] = lines[ow[0]].replace(old_ts, NOW)

    # delete done/harvest field lines (probed: 5)
    DEL = ('"done_at":', '"harvested_by":', '"harvest_claim":',
           '"done_by":')
    dl = [n for n, l in enumerate(lines)
          if l.strip().startswith(DEL)]
    assert len(dl) == 5, f"expected 5 field lines, got {len(dl)}: {dl}"
    lines = [l for n2, l in enumerate(lines) if n2 not in set(dl)]

    fixed = fix_dangling_comma(lines)
    assert fixed in (1, 2, 3), f"unexpected comma-fix count {fixed}"

    # append r782 provenance inside shard note
    nt = [n for n, l in enumerate(lines)
          if l.strip().startswith('"note":')]
    assert len(nt) == 1, f"expected 1 note line, got {len(nt)}"
    assert lines[nt[0]].rstrip().endswith('",'), "note tail unexpected"
    lines[nt[0]] = lines[nt[0]].rstrip()[:-2] + PROV + '",'

    # lane_owner: already pinned by r781 -- verify, do not insert
    lo = [n for n, l in enumerate(lines)
          if l.strip().startswith('"lane_owner":')]
    assert len(lo) == 1, "lane_owner pin missing (r781 face lost?)"

    new_block = eol.join(lines)
    p = json.loads(new_block)              # block reparse gate
    assert p['status'] == 'ready' and p['shards'][0]['status'] == 'ready'
    assert p['shards'][0]['owner_since'] == NOW
    assert p['lane_owner'] == 'bm-b'
    for f in ('done_at', 'harvested_by', 'harvest_claim'):
        assert f not in p['shards'][0], f"shard still has {f}"
    for f in ('done_by', 'done_at'):
        assert f not in p, f"entry still has {f}"
    assert 'r782' in p['shards'][0]['note']

    new_raw = raw[:j] + new_block + raw[k + 1:]
    delta = new_raw.count('\n') - n_before
    assert delta == -5, f"line delta {delta} != -5"
    pool = json.loads(new_raw)             # whole-file reparse gate
    v = [e for e in pool['entries']
         if e['id'] == 'FUND-VALUE-P1-NULLS'][0]
    assert v['status'] == 'ready'
    assert v['shards'][0]['status'] == 'ready'
    assert v['shards'][0]['owner_since'] == NOW
    assert v['lane_owner'] == 'bm-b'
    q = [e for e in pool['entries']
         if e['id'] == 'FUND-QUALITY-P1-NULLS'][0]
    d = [e for e in pool['entries']
         if e['id'] == 'FUND-DIVLOWVOL-P1-NULLS'][0]
    assert q['status'] == 'ready' and d['status'] == 'ready'

    open(path, 'w', encoding='utf-8', newline='').write(new_raw)
    print(f"{path}: V take-3 cured ready (entries={len(pool['entries'])}, "
          f"lines {delta:+d}, owner_since={NOW}, comma-fixes={fixed})")

print("TAKE-3 OK: all four pool faces ready in one window")
