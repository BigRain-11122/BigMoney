# -*- coding: utf-8 -*-
"""r787 bm-c W192 selftest prose-leg inserter (five-face #4 completion):
the freeze landed faces 1-3+5 (pf row / n1 cfg row / n1 materializer face /
prereg; the face asserts now RUN inside selftest body pre-T-141); the
per-wave summary print leg was not rolled by the adopted draft. This
gated inserter rolls the W191 prose leg (machine-read numbers from the
ADMIT probe receipt per r587/r359 laws) and inserts it after the W191 leg
(r560 insert-after-last law). EOL-adaptive (r370); AST + py_compile gate
(r580/r581); post-insert selftest must print the W192 leg (r359 count
prose from gate machine output)."""
import ast
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PROBE_RCPT = os.path.join(ROOT, "results", "_r787bmc_w192_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r787bmc_w192_selftest_leg_receipt.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

LEG_START = '"+ W191 materializer face [same guard set, dep=W17..W190 "'
T141_START = '"+ T-141 s2 "'

R = [
    (LEG_START, '"+ W192 materializer face [same guard set, dep=W17..W191 "', 1),
    ('"outputs ALL PRESENT (landed net chain head 825,328 = "',
     '"outputs ALL PRESENT (landed net chain head 833,536 = "', 1),
    ('"W190 bm-a r892 one-pass, K=415,920 merged pool; ZERO "',
     '"W191 bm-a r895 one-pass, K=418,120 merged pool; ZERO "', 1),
    ('"in-flight upstream seats), ONE HUNDRED-AND-NINETY-FIRST "',
     '"in-flight upstream seats), ONE HUNDRED-AND-NINETY-SECOND "', 1),
    ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 180 "',
     '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 181 "', 1),
    ("+ candidate) bm-a's one-hundred-seventh owned claim per ",
     "+ candidate) bm-c's thirty-fifth owned claim per ", 1),
    ('"machine-derive (engine_owner==bm-a rows 106 + candidate), "',
     '"machine-derive (engine_owner==bm-c rows 34 + candidate), "', 1),
    ('"A=FIRST-CLEAN past the registered W190 B band (staircase "',
     '"A=FIRST-CLEAN past the registered W191 B band (staircase "', 1),
    ('"FIFTY-FIRST instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
     '"FIFTY-SECOND instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
    ('"results/_r892bma_w191_probe_receipt.json, law sec.4 W191 row, "',
     '"results/_r787bmc_w192_probe_receipt.json, law sec.4 W192 row, "', 1),
    ('"r894 bm-a] "', '"r787 bm-c] "', 1),
]


def rep(text, old, new, expect, tag):
    n = text.count(old)
    assert n == expect, "REPLACEMENT COUNT MISMATCH [%s]: got %d expect %d\nliteral=%r" % (
        tag, n, expect, old[:120])
    return text.replace(old, new)


def main():
    facts = {"round": 787, "machine": "bm-c", "wave": 192}

    # G0 idempotence
    raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    assert '"+ W192 materializer face' not in raw, "ALREADY APPLIED"

    # G1 receipt parity (r587/r359 machine numbers)
    r = json.load(open(PROBE_RCPT, encoding="utf-8"))
    leg0 = r["legs"]["leg0"]
    assert leg0["ordinal"] == 182 and leg0["bmc_ordinal"] == 35 \
        and leg0["owner_rows"] == 181 and leg0["bmc_rows"] == 34 \
        and leg0["w191_ledger_head"] == 833536, "probe receipt leg0 drift"
    leg1 = r["legs"]["leg1"]
    assert leg1["A"] == [437204, 439203] and leg1["B"] == [439204, 439403] \
        and leg1["hops_A"] == 1 and leg1["hops_B"] == 1, "probe receipt leg1 drift"

    # G2 EOL detect (r370)
    crlf = raw.count("\r\n") > raw.count("\n") / 2
    n = raw.replace("\r\n", "\n")
    facts["eol_crlf"] = crlf

    # G3 extract W191 leg chunk, roll
    i = n.find(LEG_START)
    assert i >= 0, "W191 prose leg start not found"
    j = n.find(T141_START, i)
    assert j > i, "T-141 prose fragment not found after W191 leg"
    leg = n[i:j]
    assert leg.count('"r894 bm-a] "') == 1 and leg.rstrip().endswith('bm-a] "'), \
        "W191 leg tail drift"
    m = leg
    for k, (old, new, cnt) in enumerate(R):
        m = rep(m, old, new, cnt, "leg-%02d" % k)
    facts["replacements"] = len(R)

    # G4 insert after the W191 leg (r560), pre/post intactness
    out = n[:j] + m + n[j:]
    assert out.count(LEG_START) == 1, "W191 leg not unique post-insert"
    assert out.count('"+ W192 materializer face') == 1
    assert out.count(T141_START) == 1
    assert out.find('"+ W192 materializer face') > out.find(LEG_START)
    assert out.find(T141_START) > out.find('"+ W192 materializer face')

    # G5 AST gate before write (r580/r581/r445)
    ast.parse(out)

    # G6 write back EOL-adaptive
    with open(N1P, "w", encoding="utf-8", newline="") as fh:
        fh.write(out.replace("\n", "\r\n") if crlf else out)

    # G7 py_compile + selftest must print the W192 leg
    prc = subprocess.run([sys.executable, "-m", "py_compile", N1P],
                         capture_output=True, creationflags=CNW)
    assert prc.returncode == 0, "py_compile failed"
    st = subprocess.run([sys.executable, N1P, "selftest"],
                        capture_output=True, creationflags=CNW, cwd=ROOT)
    stxt = st.stdout.decode("utf-8", "replace")
    assert st.returncode == 0, "selftest failed after leg insert"
    assert "+ W192 materializer face" in stxt, "W192 leg missing from selftest output"
    assert "selftest: PASS" in stxt, "selftest PASS banner missing"
    facts["selftest_leg_printed"] = True

    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/3 W192 selftest prose leg rolled: %d count-asserted "
          "replacements from the W191 leg (numbers machine-read from the "
          "ADMIT probe receipt leg0/leg1, r587/r359)" % len(R))
    print("PASS 2/3 insert-after-last-registered-leg (r560) + EOL-adaptive "
          "(r370) + AST gate + py_compile green; W191 leg + T-141 fragment "
          "byte-intact")
    print("PASS 3/3 selftest re-run PASS with the W192 leg printed; receipt="
          "results/_r787bmc_w192_selftest_leg_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
