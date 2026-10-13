"""r920 bm-b: N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN waiting->ready supply flip.

Gate adjudication (r909 flip pin "free RAM >=4GB post-batch"):
- RAM leg: live probe at flip time, floor 4GB (r909 pin; r797 family law).
- Batch leg: i2v CEO batch is PAUSED (PSU-deferred, 27/53) -> ComfyUI
  STOPPED -> the pin's protective purpose (8-worker train OOM-risk to a
  RUNNING ComfyUI) is moot; entry is pure-CPU BelowNormal designed to
  coexist with the i2v GPU lane (workers_plan note verbatim). CEO
  standing orders O-20261013-2215 (fleet CPU always open) + O-20261013
  -2245 (all projects continue, full speed) govern the CPU lane.

Laws: pit-pool-edit r509 (raw-text anchored surgery, no re-serialize),
r500 (byte-probe before write), r678 (roundtrip-first assertion),
r694 (entry-id-anchored needle + uniqueness), parse-before-write;
pit-pool-burn r316 (host_gates local re-verify before ignition).
Single-writer law: writes ONLY the bm-b lane file (O-20260928-1855 v1).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANE = os.path.join(ROOT, "results", "runnable_pool.bm-b.json")
ENTRY_ID = "N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN"

receipt = {"entry": ENTRY_ID, "ts_local": None, "preflight": {}, "surgery": {}}

# ---- preflight (r316: local state, not registration-time state) ----
def _dir_nonempty(p):
    return os.path.isdir(p) and len(os.listdir(p)) > 0

gates = {
    "results/alphagen_rg nonempty": _dir_nonempty(os.path.join(ROOT, "results", "alphagen_rg")),
    "results/alphagen_rl_p1/ckpt nonempty": _dir_nonempty(os.path.join(ROOT, "results", "alphagen_rl_p1", "ckpt")),
    "panel_cache_2026-10-09.npz": os.path.isfile(os.path.join(ROOT, "results", "alphagen_rg", "panel_cache_2026-10-09.npz")),
    "runner scripts/alphagen_rl_p1.py": os.path.isfile(os.path.join(ROOT, "scripts", "alphagen_rl_p1.py")),
}
ram_ok = False
try:
    import psutil
    vm = psutil.virtual_memory()
    free_gb = vm.available / (1024 ** 3)
    ram_ok = free_gb >= 4.0
    gates["free_ram_gb>=4 (live)"] = "%.2f" % free_gb
except Exception as ex:
    gates["free_ram_gb>=4 (live)"] = "probe fault: %r" % ex
receipt["preflight"]["host_gates"] = gates

fuse_note = "no ACTIVE train sig in fuse"
try:
    with open(os.path.join(ROOT, "results", "crash_fuse.json"), encoding="utf-8") as f:
        fuse = json.load(f)
    # r798 three-step law step 1: judge by EXACT sig, not substring.
    # (the cleared probe sig `probe,--episodes,256` is a different face;
    # r893 tombstone: post-completion confirm artifact, zero real crash)
    train_sig = "scripts/alphagen_rl_p1.py|train,--episodes,4096"
    hit = fuse.get(train_sig) if isinstance(fuse, dict) else None
    if hit and not hit.get("cleared_ts"):
        fuse_note = "ACTIVE FUSE on train sig -- ABORT (manual adjudication)"
    elif hit:
        fuse_note = "train sig present but CLEARED (%s)" % hit.get("reason")
except FileNotFoundError:
    pass
receipt["preflight"]["crash_fuse"] = fuse_note

ok = all(v is True for k, v in gates.items() if isinstance(v, bool)) and ram_ok
if "ABORT" in fuse_note:
    ok = False
if not ok:
    receipt["preflight"]["verdict"] = "ABORT preflight"
    json.dump(receipt, open(os.path.join(ROOT, "results", "_r920bmb_n2u3_flip.json"), "w"),
              ensure_ascii=True, indent=1)
    print("PREFLIGHT ABORT: %s" % json.dumps(gates))
    sys.exit(2)

# ---- byte probe (r500) ----
raw = open(LANE, "rb").read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
receipt["surgery"]["eol_probe"] = {"crlf_pairs": crlf, "bare_lf": lf_only}

# ---- roundtrip-first assertion (r678) ----
pool = json.loads(raw.decode("utf-8"))
rt = json.dumps(pool, ensure_ascii=False, indent=1).encode("utf-8")
roundtrip_identical = (rt == raw)
receipt["surgery"]["roundtrip_identical"] = roundtrip_identical
# expect False (daemon writer format); surgery path taken regardless.

# ---- entry-anchored needle surgery (r509/r694) ----
text = raw.decode("utf-8")
anchor = text.find('"%s"' % ENTRY_ID)
assert anchor > 0, "entry id not found"
region_end = text.find('\n  {', anchor)  # next entry start at same depth
if region_end == -1:
    region_end = len(text)
region = text[anchor:region_end]

pat = re.compile(r'^(?P<indent>\s*)"status": "waiting"(?P<comma>,?)\r?$', re.M)
hits = list(pat.finditer(region))
receipt["surgery"]["waiting_status_hits"] = len(hits)
assert len(hits) == 2, "expected exactly 2 waiting status lines (entry+shard), got %d" % len(hits)

def _flip(m):
    # preserve host CRLF (r485 EOL-mixing law; lane file is CRLF-throughout)
    return '%s"status": "ready"%s\r' % (m.group("indent"), m.group("comma"))

new_region = pat.sub(_flip, region)
assert new_region.count('"status": "ready"') - region.count('"status": "ready"') == 2

# shard note: document the flip adjudication (ASCII only, one line)
old_note = '"note": ""'
note_pos = new_region.find(old_note)
assert note_pos != -1, "shard note field not found in entry region"
new_region = new_region.replace(
    old_note,
    '"note": "flipped ready bm-b r920: RAM gate passed (ComfyUI stopped, PSU-deferred; '
    'r909 pin purpose=OOM protection moot); CEO O-20261013-2215 CPU-always-open + O-2245 full-speed"',
    1)

new_text = text[:anchor] + new_region + text[region_end:]
new_raw = new_text.encode("utf-8")

# ---- parse-before-write (r859 law) ----
check = json.loads(new_raw.decode("utf-8"))
ent = [e for e in check["entries"] if e.get("id") == ENTRY_ID]
assert len(ent) == 1
assert ent[0]["status"] == "ready", "entry status not ready after surgery"
assert ent[0]["shards"][0]["status"] == "ready", "shard status not ready after surgery"
assert ent[0]["shards"][0].get("owner") in (None, ""), "shard unexpectedly owned"
receipt["surgery"]["verified"] = {"entry_status": "ready", "shard_status": "ready",
                                 "lane_owner": ent[0]["lane_owner"]}

open(LANE, "wb").write(new_raw)

# ---- readback identity assertion ----
back = open(LANE, "rb").read()
assert back == new_raw, "readback mismatch"
receipt["surgery"]["readback_identical"] = True
receipt["surgery"]["changed_lines_expected"] = "3 (2 status flips + 1 shard note)"
json.dump(receipt, open(os.path.join(ROOT, "results", "_r920bmb_n2u3_flip.json"), "w"),
          ensure_ascii=True, indent=1)
print("FLIP OK: entry+shard waiting->ready; preflight=%s" % json.dumps(gates))
