# r374 bm-a S0 stash-pop resolve evidence: results/autofill_state.json (1-UU)
# Trigger: S0 pull --rebase OK (f64d23b1 -> ea20570a fast-forward, no conflict);
#          stash pop of local watchdog runtime faces (results/autofill_state.json
#          + results/autofill_state.bm-a.json) hit 1-UU on the shared autofill face.
# Classifier: mixed-dict+ledger (GREEN 1/1, 0 UNKNOWN). Canon: r203/R208/r215/r220.
#
# Probe result (dual stage blob, subprocess bytes, r209 repr discipline):
#   stage :2: (HEAD post-pull)  16417 B, CRLF 668/668 -> producer format LF-全部-CRLF
#   stage :3: (STASH local)     16417 B, CRLF 668/668
#   keys: both {last_tick, launches}
#   last_tick: ts IDENTICAL '2026-09-28 02:50:01' (same-second tie),
#              machine HEAD=bm-c vs STASH=bm-a, py_cpu 0.0 both,
#              verdict pool_empty_or_busy both
#   launches: 50 vs 50, composite-key set (ts,machine,pid,runner_sha256,entry,shard)
#             EQUAL, same-key content-diff count = 0, order identical
#
# Decision (canon):
#   launches union = identity no-op (50 = 50, zero key/content delta) -> 50 kept
#   last_tick same-second tie -> HEAD side (r140 law) -> whole-dict assign stage :2:
#   => resolved content == stage :2: byte-for-byte; write-back = verbatim :2: bytes
#      (newline mirror satisfied by construction; isinstance(dict) asserted on parse)
# Zero-loss check: |A union B| = 50 = both sides; only divergent field resolved by
# tie law, no data dropped.
import json
import subprocess

PATH = "results/autofill_state.json"
b2 = subprocess.run(["git", "show", ":2:" + PATH], capture_output=True).stdout
b3 = subprocess.run(["git", "show", ":3:" + PATH], capture_output=True).stdout
j2, j3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))

kh = {
    (e.get("ts"), e.get("machine"), e.get("pid"), e.get("runner_sha256"),
     e.get("entry"), e.get("shard")): e
    for e in j2["launches"]
}
ks = {
    (e.get("ts"), e.get("machine"), e.get("pid"), e.get("runner_sha256"),
     e.get("entry"), e.get("shard")): e
    for e in j3["launches"]
}
assert set(kh) == set(ks), "composite-key set divergence -> escalate, no blind union"
assert all(kh[k] == ks[k] for k in kh), "same-key content divergence -> escalate"
assert j2["last_tick"]["ts"] == j3["last_tick"]["ts"], "not a same-second tie"
assert isinstance(j2["last_tick"], dict)

# tie -> HEAD (r140); union of launches is identity -> resolved == stage :2:
with open(PATH, "wb") as f:
    f.write(b2)

# post-write verify: parse + byte identity to chosen side
back = open(PATH, "rb").read()
assert back == b2, "write-back byte drift"
json.loads(back.decode("utf-8"))
print("resolved: tie->HEAD(bm-c tick), launches 50/50 identity-union, bytes", len(back))
