# -*- coding: utf-8 -*-
"""R234 bm-a: text-level minimal-diff insert progress_r234 into T-72 ticket.

Per R230 law: shared JSON single-field append = text-level insertion
(preserve 2-space indent + CRLF + existing EOL), not json rewrite.
"""
import json

path = "fleet/tasks/T-2026-09-26-72-P1.json"
raw = open(path, "rb").read()
assert raw.endswith(b'"' + b"\r\n" + b"}"), repr(raw[-20:])

entry_text = (
    "R234 08:1x (dept:数据) s2 first-pull SUPERVISION R7 (no pull-touch): "
    "done 4905/5228 @08:12 checkpoint fresh, attempts-map zero per-symbol failures, "
    "PID 29132 alive since 04:33:37; rate ~21-24/min -> remaining ~323 ETA ~08:26-27 "
    "(acceptance round ~R235-236); spot QC 6/6 freshest-tail sample PASS "
    "(688343..688350: 14-col frozen schema opendate+13 raw-ASCII cols identical, "
    "exactly 100 rows frozen num=100 caliber, tail 2026-09-24 = latest bar day, "
    "netamount vs sum r0..r3_net dev <=2.1e-10 = sina four-tier self-consistency law "
    "holds, probe=results/_r234_bma_sina_qc.py); compute_audit CLEAN flags[] "
    "load_state=idle-starvation pool_ready=0 (P1E-SYNTH harvested by bm-b r231, "
    "board clear legal idle); ACCEPTANCE TURNKEY unchanged: "
    "python scripts\\sina_mf_accept.py run -> exit 0=PASS/1=FAIL/2=machinery; "
    "s3 wiring follows PASS only."
)
entry = '  "progress_r234": ' + json.dumps(entry_text, ensure_ascii=False) + "\r\n"

new = raw[:-1] + b",\r\n" + entry.encode("utf-8") + b"}"
open(path, "wb").write(new)

t = json.load(open(path, encoding="utf-8-sig"))
prog_keys = sorted(k for k in t if k.startswith("progress_r2"))
print("parse ok; last two progress keys:", prog_keys[-2:])
print("progress_r234 len:", len(t["progress_r234"]))
