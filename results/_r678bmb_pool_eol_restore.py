"""r678 bm-b pool EOL restoration -- byte-level LF->CRLF on the shared
runnable_pool.json face. Content bytes preserved EXACTLY (only bare-LF
newlines get their CR restored); the drift root = bm-c r480 merge
resolution commit 231fe8313 (first LF blob; prior commits e2f746374 /
c36a087ea / 240df7e9d / 3fbfb4ed0 all CRLF=14301) -- the autofill tick
e8173b2a0 merely absorbed the already-LF face (settle mirrors the shared
probe). pf selftest leg 8 (r289 format law) hard-pins CRLF as the
canonical producer face -> red until restored.
Evidence: results/_r678bmb_pool_eol_probe.py (four-point blob timeline).
"""
import json, os, subprocess, sys

CREAT = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

b = open(POOL, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
assert crlf0 == 0, f"unexpected pre-state: CRLF={crlf0} (expected 0 = drifted LF face)"
assert lf0 > 1000, f"unexpected pre-state: LF={lf0}"
# byte surgery: every bare LF gets a CR (file is pure-LF by pre-state assert)
out = b.replace(b"\n", b"\r\n")
assert out.count(b"\r\n") == lf0 == out.count(b"\n"), "EOL surgery count identity FAIL"
assert len(out) == len(b) + lf0, "length identity FAIL"
# content identity: parse both, compare canonical dumps
c_before = json.dumps(json.loads(b.decode("utf-8")), ensure_ascii=False,
                      sort_keys=True)
c_after = json.dumps(json.loads(out.decode("utf-8")), ensure_ascii=False,
                     sort_keys=True)
assert c_before == c_after, "content identity FAIL (json canonical compare)"
tmp = POOL + ".eol.tmp"
with open(tmp, "wb") as f:
    f.write(out)
os.replace(tmp, POOL)
b2 = open(POOL, "rb").read()
assert b2 == out, "atomic write verify FAIL"
n_crlf = b2.count(b"\r\n")
print(f"pool EOL restored: {len(b)}B LF-only -> {len(b2)}B CRLF "
      f"(CRLF={n_crlf}, content byte-identical modulo CR, "
      f"json-canonical-equal)")
print("POOL_EOL_RESTORE_OK")
