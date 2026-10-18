# -*- coding: utf-8 -*-
# r1086 bm-c: W266 post-splice selftest heal (SINGLE TOKEN) -- the dead
# 09:25-09:50 splice window's editor left the W266 selftest block roll line
# un-rolled: _set_wave(265) inside the W266 section (H1 family, r1076 W264
# precedent, 3rd recurrence). Runtime proof pre-heal: n1 selftest died
# "W266 A hits W265" (w244_a held W265 bands 598301..600300 via the
# un-rolled _set_wave; sixgate results/_r1086bmc_w266_sixgate.json FAIL face,
# n1_selftest_rc=1, all other gates green). MINIMALITY: exactly one
# same-length token, engine mechanics untouched (registry rows / shard dir /
# burn arithmetic verified green by the other six gates; the engine already
# self-burned 12/12 from the correct W266 registry rows -- the defect is
# selftest-section-local only).
import hashlib
import io
import json
import subprocess
import sys

P = 'scripts/perpetual_faces_n1.py'
old = io.open(P, 'rb').read()
old_sha16 = hashlib.sha256(old).hexdigest()[:16]
assert old_sha16 == '992f2f3b7b380bf6', ('pre-heal worktree face drift', old_sha16)

pat = b'_set_wave(265)'
idxs = []
k = old.find(pat)
while k >= 0:
    idxs.append(k)
    k = old.find(pat, k + 1)
assert len(idxs) == 2, idxs  # W265 block roll (legit) + W266 block un-rolled roll (defect)
jj = idxs[1]
anchor = 'W138..W206+W211..W265)'.encode('utf-8')
assert anchor in old[max(0, jj - 2000):jj], 'W266-section anchor missing'
new = old[:jj] + b'_set_wave(266)' + old[jj + len(pat):]
assert len(new) == len(old), 'heal must be same-length'
io.open(P, 'wb').write(new)
new_sha16 = hashlib.sha256(io.open(P, 'rb').read()).hexdigest()[:16]

r = subprocess.run([sys.executable, 'scripts/perpetual_faces_n1.py', 'selftest'],
                  capture_output=True, text=True)
receipt = {
 "machine": "bm-c", "wave": 266,
 "defect": "H1 un-rolled _set_wave: W266 selftest block roll line held _set_wave(265) (dead 09:25-09:50 splice-window editor authoring defect; r1076 W264 H1 family 3rd recurrence)",
 "token": "_set_wave(265)->_set_wave(266) (W266 section, 2nd occurrence, same length)",
 "runtime_proof_pre_heal": 'n1 selftest died "W266 A hits W265" (sixgate n1_selftest_rc=1, results/_r1086bmc_w266_sixgate.json FAIL face)',
 "old_sha16_crlf": old_sha16,
 "new_sha16_crlf": new_sha16,
 "occurrences_pre": len(idxs),
 "anchor": "W138..W206+W211..W265) within 2000B before the healed token (W266 section header parity-rows face)",
 "selftest_rc_post": r.returncode,
 "selftest_tail": (r.stdout or '').strip()[-200:],
 "phase": "post-splice post-burn PRE-finalize (engine mechanics untouched; engine already self-burned 12/12 from the correct W266 registry rows)",
}
io.open('results/_r1086bmc_w266_selftest_heal.json', 'w', encoding='utf-8').write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps(receipt, indent=1))
sys.exit(0 if r.returncode == 0 else 1)
