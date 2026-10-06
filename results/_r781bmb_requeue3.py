"""r781 bm-b P0 surgery: V re-queue take-2 -- THREE-FACE cure.

r780 (commit 61310a4f6) flipped only the SHARED face and DELETED
owner_since; the 17:24 keepalive tick (544fd09f1) clobbered it back to
done via two live paths this round diagnosed:
  (1) stale closed+ok worker claim file -> autofill._harvest_done_flips
      re-lands status=done every tick (Tools/autofill.py L961/L1005);
  (2) lane mirror runnable_pool.bm-b.json kept the full done@15:50:03
      face -> merged-view/settle re-imports done over a ts-less ready
      face (shared had NO owner_since after r780 deleted it -> any
      ts-bearing face wins).
Cure (all three faces, one window):
  A. claim file state closed -> superseded  (harvest scan skips it:
     requires state==closed; picker reads heartbeat 15:41 = stale ->
     takeable; fresh worker claim overwrites this file on re-ignite);
  B. shared + lane: shard.status & entry.status done -> ready,
     DELETE done_at/harvested_by/harvest_claim/done_by (5 lines per
     file), KEEP owner/claimed_since, BUMP owner_since to NOW
     (newer-wins beats every stale done face at any machine's settle,
     r311 latest.ts law + r720 shards-layer);
  C. entry lane_owner=bm-b pin (fleet adjudication MSG-1132/1155/1838
     canonical-burner enforcement -- blocks bm-a off-caliber steal;
     bm-a picker: lane_owner != myid -> skip).
Laws: pit-pool-edit.md r509/r500 (raw-text anchored, no json
re-serialization of pool), r694 (needle anchored inside entry block),
r629 (trailing comma on tail-field deletion), r678/r705 (reparse +
entry-count + diff-stat gates), treasure_guard restore rc0 (all three
paths, passed this round before this script ran).
Re-ignition: daemon claims on next tick -> runner done-key skip burns
only the 14 missing ks deterministically rng([20500000,k]) (r780
forensic _r780bmb_forensic.py), ~3min/draw.
"""
import json
import sys
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CLAIM = ('results/pool_claims/FUND-VALUE-P1-NULLS/'
         'fund-value-p1-nulls-0of1.bm-b.json')
POOLS = ['results/runnable_pool.json', 'results/runnable_pool.bm-b.json']
ID_N = '"FUND-VALUE-P1-NULLS"'
PROV = (" | rel-bm-b-r781 2026-10-06: three-face re-queue take-2 -- r780 "
        "shared-only flip was clobbered by 17:24 keepalive (stale "
        "closed+ok claim harvest re-flip + lane done@15:50:03 settle "
        "restore over ts-less ready face); cure = claim superseded + both "
        "faces ready + owner_since bumped fresh + lane_owner=bm-b pin "
        "(MSG-1132/1155/1838 canonical-burner); re-ignite 14 missing ks "
        "deterministic rng([20500000,k])")


def v_block(raw):
    """Locate the V entry block (r694 needle anchored on entry id)."""
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


# ---------- A. claim file supersede (roundtrip-probed: LF + indent2) ----
craw = open(CLAIM, encoding='utf-8', newline='').read()
assert json.dumps(json.loads(craw), ensure_ascii=False,
                 indent=2) == craw.replace('\r\n', '\n') or \
       json.dumps(json.loads(craw), ensure_ascii=False,
                 indent=2).replace('\n', '\r\n') == craw, \
    "claim roundtrip probe failed"
c = json.loads(craw)
if c.get('state') == 'superseded':
    print("claim: ALREADY superseded -- no-op")
else:
    assert c.get('state') == 'closed' and c.get('outcome') == 'ok', \
        f"unexpected claim state {c.get('state')}/{c.get('outcome')}"
    c['state'] = 'superseded'
    c['supersede_note'] = ("r781: result_ref N=2000 was false-on-disk "
                           "(14 rows lost in r779 17-UU rebase window, "
                           "r780 forensics _r780bmb_forensic.py); harvest "
                           "re-flip face retired; fresh worker claim "
                           "overwrites this file on re-ignite")
    new_craw = json.dumps(c, ensure_ascii=False, indent=2)
    if '\r\n' in craw:
        new_craw = new_craw.replace('\n', '\r\n')
    open(CLAIM, 'w', encoding='utf-8', newline='').write(new_craw)
    print(f"claim: state -> superseded ({len(new_craw)}B)")

# ---------- B+C. both pool faces raw-text surgery -------------------------
changed = {}
for path in POOLS:
    raw = open(path, encoding='utf-8', newline='').read()
    n_before = raw.count('\n')
    block, j, k = v_block(raw)
    assert '"runner": "scripts/fund_value_p1.py"' in block, "block sanity"
    lines = block.split('\r\n')
    assert len(lines) > 30, "block too small -- EOL probe mismatch"

    # idempotent guard: already ready (surgery applied / daemon ignited)
    if '"status": "ready"' in block:
        print(f"{path}: V already ready -- skip (no-op)")
        changed[path] = None
        continue

    # pass 1: flip both status fields (exactly 2 expected)
    st = [n for n, l in enumerate(lines)
          if l.strip() == '"status": "done",']
    assert len(st) == 2, f"expected 2 status lines, got {len(st)}: {st}"
    for n in st:
        lines[n] = lines[n].replace('"done"', '"ready"')

    # pass 2: bump owner_since to NOW (shard layer, r311 latest.ts law)
    ow = [n for n, l in enumerate(lines)
          if l.strip().startswith('"owner_since":')]
    assert len(ow) == 1, f"expected 1 owner_since line, got {len(ow)}"
    old_ts = lines[ow[0]].split('"')[3]
    lines[ow[0]] = lines[ow[0]].replace(old_ts, NOW)

    # pass 3: delete done/harvest fields (5 lines: shard done_at +
    # harvested_by + harvest_claim + entry done_by + done_at)
    DEL = ('"done_at":', '"harvested_by":', '"harvest_claim":',
           '"done_by":')
    dl = [n for n, l in enumerate(lines)
          if l.strip().startswith(DEL)]
    assert len(dl) == 5, f"expected 5 field lines, got {len(dl)}: {dl}"
    lines = [l for n, l in enumerate(lines) if n not in set(dl)]

    # pass 4: trailing comma fixes (r629) -- claimed_since now last shard
    # field; host_gates '],' now last entry field
    cs = [n for n, l in enumerate(lines)
          if l.strip().startswith('"claimed_since":')]
    assert len(cs) == 1, "claimed_since not unique"
    assert lines[cs[0]].rstrip().endswith('",'), "claimed_since tail"
    assert lines[cs[0] + 1].strip() == '}', "line after claimed_since"
    lines[cs[0]] = lines[cs[0]].rstrip()[:-1]
    close = max(n for n, l in enumerate(lines) if l.strip() == '}')
    assert lines[close - 1].strip() == '],', \
        f"unexpected pre-close: {lines[close - 1]!r}"
    lines[close - 1] = lines[close - 1].rstrip()[:-1]

    # pass 5: append r781 provenance inside shard note
    nt = [n for n, l in enumerate(lines)
          if l.strip().startswith('"note":')]
    assert len(nt) == 1, f"expected 1 note line, got {len(nt)}"
    lines[nt[0]] = lines[nt[0]].rstrip()[:-2] + PROV + '",'

    # pass 6: entry lane_owner pin (insert right after runner line; host
    # format has NO blank lines -- earlier dump blanks were CR render
    # artifacts, 38-line block / 37 CRLF probed)
    rn = [n for n, l in enumerate(lines)
          if l.strip().startswith('"runner":')]
    assert len(rn) == 1, "runner line not unique"
    lines[rn[0] + 1:rn[0] + 1] = ['   "lane_owner": "bm-b",']

    new_block = '\r\n'.join(lines)
    # block reparse gates
    p = json.loads(new_block)
    assert p['status'] == 'ready' and p['shards'][0]['status'] == 'ready'
    assert p['shards'][0]['owner_since'] == NOW
    assert p['lane_owner'] == 'bm-b'
    sh = p['shards'][0]
    for f in ('done_at', 'harvested_by', 'harvest_claim'):
        assert f not in sh, f"shard still has {f}"
    for f in ('done_by', 'done_at'):
        assert f not in p, f"entry still has {f}"
    assert 'r781' in sh['note'] and 'r780' in sh['note']
    assert p['runner'] == 'scripts/fund_value_p1.py'
    assert p['workers_plan']['workers'] == 32

    new_raw = raw[:j] + new_block + raw[k + 1:]
    delta = new_raw.count('\n') - n_before
    assert delta == -4, f"line delta {delta} != -4 (-5 del +1 lane_owner)"
    pool = json.loads(new_raw)            # whole-file reparse gate
    v = [e for e in pool['entries'] if e['id'] == 'FUND-VALUE-P1-NULLS'][0]
    assert v['status'] == 'ready'
    assert v['shards'][0]['status'] == 'ready'
    assert v['shards'][0]['owner_since'] == NOW
    assert v['lane_owner'] == 'bm-b'
    q = [e for e in pool['entries']
         if e['id'] == 'FUND-QUALITY-P1-NULLS'][0]
    d = [e for e in pool['entries']
         if e['id'] == 'FUND-DIVLOWVOL-P1-NULLS'][0]
    assert q['status'] == 'ready' and d['status'] == 'ready'
    assert q['shards'][0].get('owner') == 'bm-b'   # alive-claim intact

    open(path, 'w', encoding='utf-8', newline='').write(new_raw)
    changed[path] = (len(pool['entries']), delta)
    print(f"{path}: V re-queued ready (entries="
          f"{len(pool['entries'])}, lines +{delta}, "
          f"owner_since={NOW}, lane_owner=bm-b)")

print("SURGERY OK: three-face cure landed "
      f"(claim superseded + {len([1 for v in changed.values() if v])} "
      "pool faces ready)")
