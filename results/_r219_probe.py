# R219 rebase resolver: results/autofill_state.json UU (bm-a autofill tick 04:50 vs bm-b r224 closeout)
# Class: mixed-dict+ledger (r203/R208) + CRLF producer-format law (r223)
# Recipe: launches = union both blobs zero-loss; last_tick = compare inner ts -> whole-dict assign; parse-verify before write-back (r185)
import json, subprocess, sys

def blob(stage):
    raw = subprocess.run(["git", "show", f":{stage}:results/autofill_state.json"], capture_output=True).stdout
    assert raw, f"empty stage {stage}"
    crlf = b"\r\n" in raw
    return raw, json.loads(raw.decode("utf-8-sig")), crlf

raw2, ours, crlf2 = blob(2)   # base = origin/main (bm-b r224 closeout)
raw3, theirs, crlf3 = blob(3) # incoming = bm-a autofill tick 04:50

print("stage2 last_tick:", repr(ours.get("last_tick")))
print("stage3 last_tick:", repr(theirs.get("last_tick")))
print("stage2 launches:", len(ours.get("launches", [])), "crlf:", crlf2)
print("stage3 launches:", len(theirs.get("launches", [])), "crlf:", crlf3)
l2 = ours.get("launches", []); l3 = theirs.get("launches", [])
k2 = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in l2}
k3 = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in l3}
print("launches union:", len(k2 | k3), "only2:", len(k2 - k3), "only3:", len(k3 - k2))
print("top keys 2:", sorted(ours.keys()))
print("top keys 3:", sorted(theirs.keys()))
