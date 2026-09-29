# -*- coding: utf-8 -*-
"""_r445bmb_resolve.py -- runnable_pool.json rebase conflict resolver
(r445 bm-b; bigmoney-conflict-resolve SKILL + r444 bm-c pool-union
precedent). Face: 127 common entries byte-identical; base-only
INNOVATION-QUOTA-SLOT-5 (bm-c 03:17:58 enqueue); mine-only
TRIAL-LABOR-W12-GENERATE (bm-b fill_ladder this round). Union by id,
base order preserved, mine-only appended; meta takes base (newer
updated_at). Byte-format mirror of base blob (r223/r234 law)."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = "results/runnable_pool.json"


def raw(stage):
    return subprocess.run(["git", "show", ":%d:%s" % (stage, PATH)],
                          capture_output=True).stdout


b_raw, m_raw = raw(2), raw(3)
b, m = json.loads(b_raw.decode("utf-8")), json.loads(m_raw.decode("utf-8"))
be, me = b["entries"], m["entries"]
bi = {e["id"]: e for e in be}
mi = {e["id"]: e for e in me}
common = set(bi) & set(mi)
assert len(common) == len(bi) - 1 == len(mi) - 1
for k in common:
    assert json.dumps(bi[k], sort_keys=True) == json.dumps(mi[k],
                                                          sort_keys=True), k
union = list(be) + [e for e in me if e["id"] not in bi]
assert len(union) == len(be) + 1 == 129, len(union)
ids = [e["id"] for e in union]
assert len(ids) == len(set(ids))
out = dict(b)          # base meta wholesale (newer updated_at 03:17:58)
out["entries"] = union
out["_stamp_note"] = (b["_stamp_note"] +
                      " + r445 bm-b union append TRIAL-LABOR-W12-GENERATE"
                      " (rebase conflict zero-loss union; "
                      "INNOVATION-QUOTA-SLOT-5 kept from base)")
# byte-format mirror: detect indent + newline style from base blob
nl = "\r\n" if b"\r\n" in b_raw else "\n"
second = b_raw.split(nl.encode())[1] if nl.encode() in b_raw else b""
indent = len(second) - len(second.lstrip(b" "))
text = json.dumps(out, ensure_ascii=False, indent=indent or 1)
if nl == "\r\n":
    text = text.replace("\n", "\r\n")
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(text + nl)
# verify parse-back + counts
chk = json.load(open(PATH, encoding="utf-8"))
assert len(chk["entries"]) == 129
assert {e["id"] for e in chk["entries"]} == set(bi) | set(mi)
print("RESOLVED: 129 entries, union zero-loss; nl=%r indent=%d" %
      (nl, indent or 1))
