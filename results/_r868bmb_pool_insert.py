"""r868 pool entry insertion (raw-text anchored, r859/r678 law family):
shared face results/runnable_pool.json gets the validated N2-MP1 entry
byte-rendered in the host face (LF, indent=1 semantics, raw CJK), NOT a
whole-file rewrite. Entry dict extracted from the autofill-validated lane
mirror (submit gate passed rc0). Parse-gate BEFORE write; post-write
json.loads + git diff --numstat assertion (target ~40 lines).
"""
import json
import subprocess

SHARED = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"

# 1) validated entry from the lane mirror (submit contract face)
lane = json.load(open(LANE, encoding="utf-8"))
entry = lane["entries"][-1]
assert entry["id"] == "N2-MP1", entry["id"]
assert entry["status"] == "ready", entry["status"]

# 2) host shared-face text + tail anchor uniqueness
txt = open(SHARED, encoding="utf-8", newline="").read()
tail = "\n  }\n ]\n}"
assert txt.endswith(tail), "tail anchor missing"
assert txt.count(tail) == 1, "tail anchor not unique"
before_entries = len(json.loads(txt)["entries"])

# 3) entry block in host render (nested-array indent=1 == host entry face:
#    entry brace 2sp, fields 3sp, nested shard fields 5sp, raw CJK)
wrap = json.dumps({"entries": [entry]}, indent=1, ensure_ascii=False)
i0 = wrap.index("  {\n")
i1 = wrap.rindex("\n ]")
block = wrap[i0:i1]
assert block.startswith('  {\n   "id": "N2-MP1"')
assert block.endswith("\n  }"), block[-10:]

new_txt = txt[:-len(tail)] + "\n  },\n" + block + "\n ]\n}"

# 4) PARSE GATE BEFORE WRITE + semantic assertions
new_pool = json.loads(new_txt)
assert len(new_pool["entries"]) == before_entries + 1, len(new_pool["entries"])
assert new_pool["entries"][-1] == entry, "entry roundtrip mismatch vs lane face"
assert new_pool["entries"][-2]["id"] == "THERMO-OVERLAY-P1-BURN"

# 5) byte-exact write (LF preserved; no CRLF translation)
with open(SHARED, "w", encoding="utf-8", newline="") as fh:
    fh.write(new_txt)

# 6) post-write verification: reparse + diff --numstat assertion
repool = json.load(open(SHARED, encoding="utf-8"))
assert len(repool["entries"]) == 420
assert repool["entries"][-1] == entry
st = subprocess.run(["git", "diff", "--numstat", SHARED],
                     capture_output=True, text=True)
print("diff --numstat:", st.stdout.strip())
ins, dele = st.stdout.split()
assert int(ins) < 80 and int(dele) < 10, ("appearance explosion", st.stdout)
print("insertion OK: 420 entries, last=N2-MP1 ready, diff %s/%s" % (ins, dele))
