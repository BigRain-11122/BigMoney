# -*- coding: utf-8 -*-
"""r872 EOL heal: results/runnable_pool.json -- the autofill submit's
Windows text-mode json.dump CRLF-translated the whole shared face
(16,726/16,690 diff explosion) while the file's git host face is LF
(HEAD b9475e6c6: 0 CRLF / 16,692 LF). r289/r500 byte-probe law: restore
the committed host face (LF), content untouched (json-roundtrip asserted
pre/post). Surgical diff target ~36/1."""
import json
import subprocess

P = "results/runnable_pool.json"
raw = open(P, "rb").read()
before = json.loads(raw.decode("utf-8"))
assert raw.count(b"\r\n") == raw.count(b"\n"), "expected uniform CRLF face"
healed = raw.replace(b"\r\n", b"\n")
after = json.loads(healed.decode("utf-8"))
assert before == after, "content changed in EOL heal"
assert healed.count(b"\r\n") == 0, "CRLF remains after heal"
with open(P, "wb") as fh:
    fh.write(healed)
rep = json.load(open(P, encoding="utf-8"))
assert len(rep["entries"]) == 421 and rep["entries"][-1]["id"] == \
    "T-101-V4-A14-PREDFACE" and rep["entries"][-1]["status"] == "ready"
st = subprocess.run(["git", "diff", "--numstat", P],
                    capture_output=True, text=True)
print("diff --numstat after heal:", st.stdout.strip())
ins, dele = st.stdout.split()
assert int(ins) < 110 and int(dele) < 10, ("still explosive", st.stdout)
print("EOL heal OK: LF host face restored, content identical, diff %s/%s"
      % (ins, dele))
