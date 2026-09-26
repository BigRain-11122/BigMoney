# -*- coding: utf-8 -*-
"""R281 pool byte-face probe + CN-TREND-ETF-P1 registration (r255/r257
five-face law: BOM / EOL / ensure_ascii / indent / trailing newline all
probed before any write-back; append-only entry + updated_at refresh)."""
import json
import time

PATH = "results/runnable_pool.json"
raw = open(PATH, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in raw
text = raw.decode("utf-8-sig")
d = json.loads(text)
indent_face = None
for line in text.splitlines()[1:6]:
    if line.startswith(" "):
        indent_face = len(line) - len(line.lstrip(" "))
        break
ascii_face = any(ord(c) > 127 for c in text)
# raw non-ASCII present => the original writer used ensure_ascii=False
# (R281 self-catch: inverting this face re-escaped the whole file to
# \uXXXX and showed up as the 25-deletion whole-file diff; r255 law)
tail_nl = raw.endswith(b"\n")
print("BOM", bom, "| CRLF", crlf, "| indent", indent_face,
      "| non_ascii(raw,utf8)", ascii_face, "| tail_nl", tail_nl)
assert not any(e["id"] == "CN-TREND-ETF-P1" for e in d["entries"]), \
    "entry already present"

entry = {
    "id": "CN-TREND-ETF-P1",
    "ticket_ref": "T-2026-09-26-87 s2 queue #1 trend-following ETF face "
                  "(SCHOOL_SUPPLY_S1.md sec.2 queue order, zero-invention; "
                  "claimed bm-a R277; F-04 MSG declared R280)",
    "prereg_ref": "research/CN_TREND_ETF_PREREG.md FROZEN feb36786 precedes "
                  "runner build precedes ANY run (R99); seed "
                  "cn_trend_etf_p1=20270201 registered at freeze commit; "
                  "RANDOM_LARGE_SAMPLE_LAW v1.0 binding (7 judged x2 cells "
                  "+ 2000 same-mask weekly-Bernoulli nulls + full-census "
                  "virtual starts + block-bootstrap/sign-flip dual nulls)",
    "runner": "scripts/cn_trend_etf_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "data_gates": "in-runner fail-closed exit 2: universe re-derive==23 + "
                  "probe symbol cross-check + truncated-face "
                  "last==2026-09-22 zero-NaN + sse coverage>=0.95; per-cell "
                  "JSON+npy idempotent checkpoints; finalize single-shot "
                  "(CN_TREND_ETF_P1_REFINALIZE=1 = only redo); selftest "
                  "21/21 pre-pooling (r263 law); real-data gate probe "
                  "PASSED 2026-09-27 00:5x bm-a (T=5248 N=23 sse_cover "
                  "0.9939, panel load 15s, MA_BASE x2 probe sharpe 0.4516 "
                  "inside prereg s5 band 0.2-0.6)",
    "workers_plan": {
        "workers": 4,
        "priority": "BelowNormal",
        "note": "nulls via shared parallel_runner run_cells_parallel "
                "(4 procs, keyed consumption r259 law); judged 14 cell-face "
                "serial sims ~0.4s each; est wall 5-8min; RAM peak <1GB",
    },
    "shards": [{"key": "cntrend-0of1", "status": "ready", "owner": None,
                "owner_since": None, "checkpoint": None}],
}
d["entries"].append(entry)
d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
out = json.dumps(d, ensure_ascii=False, indent=indent_face or 1)
if tail_nl:
    out += "\n"
enc = "utf-8-sig" if bom else "utf-8"
with open(PATH, "w", encoding=enc, newline=("\r\n" if crlf else "\n")) as fh:
    fh.write(out)
print("registered CN-TREND-ETF-P1 ready; entries:",
      len(d["entries"]), "bytes:", len(out))
