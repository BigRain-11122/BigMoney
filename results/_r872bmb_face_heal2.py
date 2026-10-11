# -*- coding: utf-8 -*-
"""r872 face heal take-2: the autofill submit's json.dump used default
ensure_ascii=True -> every CJK string escaped \\uXXXX + Windows text-mode
CRLF translation. Host face per git HEAD (b9475e6c6) = raw CJK + LF +
indent=1. Restore by re-serializing with ensure_ascii=False + LF binary
write; content asserted identical (json roundtrip); diff must collapse
to the surgical entry insertion (~40/1)."""
import json
import subprocess

P = "results/runnable_pool.json"
pool = json.load(open(P, encoding="utf-8"))
before = json.dumps(pool, ensure_ascii=False, indent=1, sort_keys=False)
txt = json.dumps(pool, ensure_ascii=False, indent=1) + "\n"
after_check = json.loads(txt)
assert after_check == pool, "roundtrip content drift"
raw = txt.encode("utf-8")
assert raw.count(b"\r\n") == 0, "CRLF leaked into heal"
with open(P, "wb") as fh:
    fh.write(raw)
rep = json.load(open(P, encoding="utf-8"))
assert len(rep["entries"]) == 421
assert rep["entries"][-1]["id"] == "T-101-V4-A14-PREDFACE"
assert rep["entries"][-1]["status"] == "ready"
st = subprocess.run(["git", "diff", "--numstat", P],
                    capture_output=True, text=True)
lines = [l for l in st.stdout.splitlines() if l.strip()]
print("diff --numstat after face heal:", lines)
assert len(lines) == 1, lines
ins, dele = lines[0].split("\t")[0], lines[0].split("\t")[1]
assert int(ins) < 110 and int(dele) < 10, ("still non-surgical", lines)
print("face heal OK: raw-CJK LF host face restored, diff %s/%s" % (ins, dele))
