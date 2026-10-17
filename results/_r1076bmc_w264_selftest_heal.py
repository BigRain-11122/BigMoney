# -*- coding: utf-8 -*-
"""r1076 bm-c: post-splice W264 selftest token heal (3 un-rolled index tokens).

Defect (runtime-proven): `python scripts/perpetual_faces_n1.py selftest` died
"W264 A hits W263" at the new-section disjointness loop -- the dead r1076
splice window (landed 216b578b0) failed to roll three index tokens in the NEW
W264 selftest section; w244_a held W263 bands (A_SEED_BASE from _set_wave(263))
-> full intersection with the W263 registry row. Convention confirmed against
the 216b578b0^ blob: the current-wave section calls _set_wave(<current>) and
its band-facts asserts index WAVE_CONFIGS[<current>] (pre-splice W263 section
called _set_wave(263) with band-facts WAVE_CONFIGS[263]).

Heals (all same-length, zero byte-length delta):
  H1: _set_wave(263) -> _set_wave(264)     [2nd occurrence, W264 section,
      anchored by the section comment tail 'W138..W206+W211..W263)']
  H2: WAVE_CONFIGS[263]["a_seed_base"] == 596101      -> [264]  (band-facts A)
  H3: WAVE_CONFIGS[263]["b_exit_seed_base"] == 598101 -> [264]  (band-facts B)

Engine mechanics untouched (WAVE_CONFIGS rows / shard dir / burn arithmetic all
verified green by sixgate gates 1-6 aside from n1_selftest; the engine already
self-burned 12/12 shards from the correct registry rows).
Atomic write per r985 law: full in-memory bytes -> temp -> os.replace.
Receipt: results/_r1076bmc_w264_selftest_heal.json
"""
import hashlib
import io
import json
import os
import tempfile

P = 'scripts/perpetual_faces_n1.py'
b = io.open(P, 'rb').read()
old_len = len(b)
old_sha16 = hashlib.sha256(b).hexdigest()[:16]
heals = []

# H2/H3: byte-unique (count==1 each) -- value 596101/598101 are the W264
# bases; the [263] row holds 593901/595901 so the un-healed asserts false-fail.
for pat, rep, name in [
    (b'WAVE_CONFIGS[263]["a_seed_base"] == 596101',
     b'WAVE_CONFIGS[264]["a_seed_base"] == 596101', 'H2_bandfacts_a'),
    (b'WAVE_CONFIGS[263]["b_exit_seed_base"] == 598101',
     b'WAVE_CONFIGS[264]["b_exit_seed_base"] == 598101', 'H3_bandfacts_b'),
]:
    n = b.count(pat)
    assert n == 1, (name, 'count!=1', n)
    off = b.find(pat)
    b = b.replace(pat, rep)
    heals.append({"name": name, "offset": off, "count": n,
                  "from": pat.decode('ascii'),
                  "to": rep.decode('ascii')})

# H1: _set_wave(263) occurs exactly 2x (W263 section at ~L71921 + W264
# section at ~L72567); replace only the SECOND (byte order == line order).
pat = b'_set_wave(263)'
idxs = []
i = b.find(pat)
while i >= 0:
    idxs.append(i)
    i = b.find(pat, i + 1)
assert len(idxs) == 2, ('_set_wave(263) occurrence count != 2', idxs)
j = idxs[1]
ctx = b[max(0, j - 400):j]
anchor = 'W138..W206+W211..W263)'.encode('utf-8')
assert anchor in ctx, 'W264-section comment anchor missing before 2nd _set_wave(263)'
b = b[:j] + b'_set_wave(264)' + b[j + len(pat):]
heals.insert(0, {"name": "H1_set_wave", "offset": j, "occurrences": 2,
                 "replaced": "second (W264 section)",
                 "anchor": "W138..W206+W211..W263) within 400B before"})

assert len(b) == old_len, ('byte-length delta!', len(b), old_len)
new_sha16 = hashlib.sha256(b).hexdigest()[:16]

# atomic write (r985 wb-truncation law: full bytes -> temp -> os.replace)
d = os.path.dirname(os.path.abspath(P))
fd, tmp = tempfile.mkstemp(dir=d, suffix='.heal.tmp')
os.close(fd)
io.open(tmp, 'wb').write(b)
os.replace(tmp, P)

receipt = {
    "machine": "bm-c", "round": "r1076", "wave": 264,
    "phase": "post-splice post-burn PRE-finalize selftest token heal",
    "file": P,
    "old_sha16_crlf": old_sha16,
    "new_sha16_crlf": new_sha16,
    "bytes_before": old_len, "bytes_after": len(b),
    "splice_commit": "216b578b095b653728a5c18d6835d4e0b968b1dc",
    "freeze_receipt_n1_sha16_post_preheal": "c72e02c2c4f43f44",
    "defect_runtime_proof": "selftest AssertionError: W264 A hits W263 "
        "(w244_a held W263 bands via _set_wave(263))",
    "heals": heals,
    "verdict": "HEALED 3 same-length tokens; engine mechanics untouched",
}
io.open('results/_r1076bmc_w264_selftest_heal.json', 'w',
        encoding='utf-8').write(json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"old_sha16": old_sha16, "new_sha16": new_sha16,
                  "bytes": old_len, "heals": [h['name'] for h in heals]},
                 indent=1))
