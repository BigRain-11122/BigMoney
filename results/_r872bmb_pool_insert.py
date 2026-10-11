# -*- coding: utf-8 -*-
"""r872 pool entry insertion (raw-text anchored, r859/r678/r868 law family):
shared face results/runnable_pool.json gets the autofill-validated
T-101-V4-A14-PREDFACE entry byte-rendered in the HOST face, NOT a
whole-file rewrite. r500 byte-probe law: current face = indent=1 semantic
+ CRLF + no trailing newline (probed this window: 16,726 CRLF == 16,726
LF, tail '  }\\r\\n ]\\r\\n}') -- r868's LF assumption is stale, the probe
wins. Entry from the autofill-validated lane mirror (submit rc0). Parse
gate BEFORE write; post-write json.loads + git diff --numstat assertion."""
import json
import subprocess

SHARED = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"

# 0) byte-probe the host face (r500 law: probe wins over memory/docs)
raw = open(SHARED, "rb").read()
n_crlf = raw.count(b"\r\n")
n_lf = raw.count(b"\n")
assert n_crlf == n_lf and n_lf > 0, "host face is not uniform CRLF"
tail = "  }\r\n ]\r\n}"
txt = raw.decode("utf-8")
assert txt.endswith(tail), "tail anchor missing"
assert txt.count(tail) == 1, "tail anchor not unique"

# 1) validated entry from the lane mirror (submit contract face)
lane = json.load(open(LANE, encoding="utf-8"))
entry = lane["entries"][-1]
assert entry["id"] == "T-101-V4-A14-PREDFACE", entry["id"]
assert entry["status"] == "ready", entry["status"]
before_entries = len(json.loads(txt)["entries"])

# 2) entry block rendered in the HOST face (indent=1 + CRLF)
wrap = json.dumps({"entries": [entry]}, indent=1, ensure_ascii=False)
i0 = wrap.index("  {\n")
i1 = wrap.rindex("\n ]")
block = wrap[i0:i1].replace("\n", "\r\n")          # host CRLF face
assert block.startswith('  {\r\n   "id": "T-101-V4-A14-PREDFACE"')
assert block.endswith("\r\n  }"), repr(block[-10:])

new_txt = txt[:-len(tail)] + "\r\n  },\r\n" + block + "\r\n ]\r\n}"

# 3) PARSE GATE BEFORE WRITE + semantic assertions
new_pool = json.loads(new_txt)
assert len(new_pool["entries"]) == before_entries + 1, len(new_pool["entries"])
assert new_pool["entries"][-1] == entry, "entry roundtrip mismatch vs lane face"
assert new_pool["entries"][-2]["id"] == "N2-MP1", new_pool["entries"][-2]["id"]

# 4) byte-exact write (CRLF preserved; no translation)
with open(SHARED, "wb") as fh:
    fh.write(new_txt.encode("utf-8"))

# 5) post-write verification: reparse + diff --numstat assertion
repool = json.load(open(SHARED, encoding="utf-8"))
assert len(repool["entries"]) == before_entries + 1
assert repool["entries"][-1] == entry
st = subprocess.run(["git", "diff", "--numstat", SHARED],
                    capture_output=True, text=True)
print("diff --numstat:", st.stdout.strip())
ins, dele = st.stdout.split()
assert int(ins) < 110 and int(dele) < 10, ("appearance explosion", st.stdout)
print("insertion OK: %d entries, last=T-101-V4-A14-PREDFACE ready, diff %s/%s"
      % (before_entries + 1, ins, dele))
