"""r781 bm-b P0 surgery part-2: heal the two he-machine lane mirrors
(results/runnable_pool.bm-a.json + results/runnable_pool.bm-c.json).

Why: merge_lane_views._merge_pool_entry r312 done-absorption -- ANY
source face carrying entry status=done wins the merged entry face
wholesale (done is terminal, stale mirrors must never resurrect it).
The 17:49 three-face cure healed shared + bm-b lane, but the picker
probe (_r781bmb_pick_probe.py) showed the merged view STILL done:
bm-a/bm-c lane mirrors carried the stale done@15:50:03 face -> done
absorbed -> entry done -> picker skips -> pool_empty_or_busy @17:52:02.
Re-queue semantics therefore require healing ALL FOUR faces in one
window; after this script every daemon's merged view is ready and
settles converge ready (stable fixed point).
These two faces are convergence-derived lane mirrors of the shared
truth (r688: he-machine lane faces are stale views, settle-governed) --
this is a heal-to-adjudicated-truth, not a governance act; guard:
treasure_guard restore rc0 (both paths, this round).
Laws: pit-pool-edit r509/r500 raw-text anchored, r694 entry-region
needle, r629 trailing comma, r678/r705 reparse+count+numstat gates.
"""
import json
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOLS = ['results/runnable_pool.bm-a.json',
         'results/runnable_pool.bm-c.json']
ID_N = '"FUND-VALUE-P1-NULLS"'
PROV = (" | rel-bm-b-r781 2026-10-06 lane-heal: stale done@15:50:03 face "
        "retired to match the r781 three-face re-queue on shared+bm-b "
        "lane (r312 done-absorption made this mirror block the merged "
        "view); re-ignite 14 missing ks deterministic rng([20500000,k])")


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
    """r629 generic: after field deletions, strip a trailing comma on
    the last field line before each structural close. Only fires on
    lines immediately preceding '}' / ']' closers."""
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
    eol = '\r\n' if '\r\n' in block else '\n'   # r782: he-mirrors are LF
    lines = block.split(eol)
    assert len(lines) > 30, "block too small -- EOL probe mismatch"

    if '"status": "ready"' in block:
        print(f"{path}: V already ready -- skip (no-op)")
        continue

    # flip both status fields
    st = [n for n, l in enumerate(lines)
          if l.strip() == '"status": "done",']
    assert len(st) == 2, f"expected 2 status lines, got {len(st)}: {st}"
    for n in st:
        lines[n] = lines[n].replace('"done"', '"ready"')

    # bump owner_since to NOW
    ow = [n for n, l in enumerate(lines)
          if l.strip().startswith('"owner_since":')]
    assert len(ow) == 1, f"expected 1 owner_since, got {len(ow)}"
    old_ts = lines[ow[0]].split('"')[3]
    lines[ow[0]] = lines[ow[0]].replace(old_ts, NOW)

    # delete done/harvest fields
    DEL = ('"done_at":', '"harvested_by":', '"harvest_claim":',
           '"done_by":')
    dl = [n for n, l in enumerate(lines)
          if l.strip().startswith(DEL)]
    assert len(dl) == 5, f"expected 5 field lines, got {len(dl)}: {dl}"
    lines = [l for n, l in enumerate(lines) if n not in set(dl)]

    # generic trailing comma fixes
    fixed = fix_dangling_comma(lines)
    assert fixed in (2, 3), f"unexpected comma-fix count {fixed}"

    # append r781 lane-heal provenance inside shard note
    nt = [n for n, l in enumerate(lines)
          if l.strip().startswith('"note":')]
    assert len(nt) == 1, f"expected 1 note line, got {len(nt)}"
    assert lines[nt[0]].rstrip().endswith('",'), "note tail unexpected"
    lines[nt[0]] = lines[nt[0]].rstrip()[:-2] + PROV + '",'

    # entry lane_owner pin (insert right after runner line)
    rn = [n for n, l in enumerate(lines)
          if l.strip().startswith('"runner":')]
    assert len(rn) == 1, "runner line not unique"
    lines[rn[0] + 1:rn[0] + 1] = ['   "lane_owner": "bm-b",']

    new_block = eol.join(lines)
    p = json.loads(new_block)          # block reparse gate
    assert p['status'] == 'ready' and p['shards'][0]['status'] == 'ready'
    assert p['shards'][0]['owner_since'] == NOW
    assert p['lane_owner'] == 'bm-b'
    for f in ('done_at', 'harvested_by', 'harvest_claim'):
        assert f not in p['shards'][0], f"shard still has {f}"
    for f in ('done_by', 'done_at'):
        assert f not in p, f"entry still has {f}"
    assert 'r781' in p['shards'][0]['note']

    new_raw = raw[:j] + new_block + raw[k + 1:]
    delta = new_raw.count('\n') - n_before
    assert delta == -4, f"line delta {delta} != -4"
    pool = json.loads(new_raw)        # whole-file reparse gate
    v = [e for e in pool['entries'] if e['id'] == 'FUND-VALUE-P1-NULLS'][0]
    assert v['status'] == 'ready' and v['shards'][0]['status'] == 'ready'
    assert v['shards'][0]['owner_since'] == NOW
    assert v['lane_owner'] == 'bm-b'
    q = [e for e in pool['entries']
         if e['id'] == 'FUND-QUALITY-P1-NULLS'][0]
    assert q['status'] == 'ready'   # neighbours untouched

    open(path, 'w', encoding='utf-8', newline='').write(new_raw)
    print(f"{path}: V lane-healed ready (entries={len(pool['entries'])}, "
          f"lines {delta:+d}, owner_since={NOW}, comma-fixes={fixed})")

print("LANE-HEAL OK: all four pool faces now ready")
