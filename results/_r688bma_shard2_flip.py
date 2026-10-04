"""r688 bm-a S3d: surgical pool flip for MASS-TRIAL-W3-JUDGE-SHARD-2 (ready -> done).

Laws: r678 (no load-dump on runnable_pool.json; line surgery + roundtrip probe first),
r668 (finalize/claim flow must flip pool entry same-window; done ticket must carry result_ref),
r474 (no owner_since regression on other entries -- single-entry targeted edit only).

Lineage note for the entry: burn launched r687 addendum (pid 26224, claim commit 03f7ac259);
claim row lost in r687 close-window merge (pool theirs-canonical, stale-fetch artifact);
work product verified complete this round: 194/194 interleaved cells i%4==2, candidate_id
unique, zero byte-dup rows (r482/r685 id-dup probes PASS).
"""
import json
import re
from datetime import datetime

PATH = "results/runnable_pool.json"
blob = open(PATH, "rb").read()

# roundtrip probe (r678 law): confirm non-identity -> must use line surgery
try:
    rt = json.dumps(json.loads(blob.decode("utf-8")), indent=1).encode("utf-8")
    print("roundtrip identical:", rt == blob, "(if False -> line surgery mandatory)")
except Exception as e:
    print("parse err:", e)
    raise SystemExit(1)

text = blob.decode("utf-8")

# locate the SHARD-2 entry block: from '"MASS-TRIAL-W3-JUDGE-SHARD-2"' to the next '"id"' at same depth or entry end
m = re.search(r'\{\s*"id":\s*"MASS-TRIAL-W3-JUDGE-SHARD-2"', text)
assert m, "SHARD-2 entry not found"
start = m.start()
# find the matching closing brace of this entry object
depth = 0
i = start
while True:
    c = text[i]
    if c == "{":
        depth += 1
    elif c == "}":
        depth -= 1
        if depth == 0:
            break
    i += 1
end = i + 1
entry_text = text[start:end]
print("entry len:", len(entry_text), "| head:", entry_text[:80].replace("\n", " "))

ent = json.loads(entry_text)
assert ent.get("status") == "ready", f"unexpected status {ent.get('status')}"

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ent["status"] = "done"
ent["done_at"] = now
ent["result_ref"] = "results/mass_trial/w3_judge_shard_2of4.jsonl (194/194 cells i%4==2 verified unique+complete r688; burn pid 26224 launch 17:15:02 claim 03f7ac259; claim row lost in r687 merge theirs-canonical stale-fetch artifact, per r668 flip same-window recovered)"
new_entry = json.dumps(ent, ensure_ascii=False, indent=1)
# re-indent to match file style: entries are nested one level under "entries": [
# json.dumps with indent=1 gives keys at 3 spaces when re-indented; match by replacing
# the produced flat text with the original entry's indentation scheme.
# Simplest safe approach: keep the SAME leading whitespace per line as original entry had.
orig_lines = entry_text.split("\n")
new_lines = new_entry.split("\n")
assert len(orig_lines) >= 2
# original entry lines: first line '{', then N indented lines, last '}' (indent depends on depth)
# detect original indent of second line:
indent = re.match(r"\s*", orig_lines[1]).group(0)
# build final entry preserving original structure: we edit fields in-place instead.
# in-place field surgery: status value, done_at insertion, result_ref insertion.
mod = entry_text
assert mod.count('"status": "ready"') == 1
mod = mod.replace('"status": "ready"', '"status": "done"')
# remove any existing done_at: null / result_ref: null forms if present
if '"done_at": null' in mod:
    mod = mod.replace('"done_at": null', f'"done_at": "{now}"')
else:
    # insert done_at after status line
    mod = mod.replace('"status": "done"', f'"status": "done",\n{indent}"done_at": "{now}"')
if '"result_ref"' not in mod:
    mod = mod.replace(f'"done_at": "{now}"', f'"done_at": "{now}",\n{indent}"result_ref": "{ent["result_ref"]}"')
json.loads(mod)  # reparse gate
text2 = text[:start] + mod + text[end:]
json.loads(text2)  # full-file reparse gate
open(PATH, "wb").write(text2.encode("utf-8"))

# post checks: entries count unchanged, other shard entries untouched
pool2 = json.loads(open(PATH, encoding="utf-8").read())
print("total entries:", len(pool2.get("entries", [])))
for e in pool2.get("entries", []):
    if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE-SHARD"):
        print("POST:", e.get("id"), e.get("status"), e.get("done_at"), (e.get("result_ref") or "")[:60])
