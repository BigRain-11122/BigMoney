"""Run the E535 smoke leg standalone (the full suite is ~20 minutes; this is the same block).

    python scripts/run_e535_smoke_leg.py           # run the leg as published
    python scripts/run_e535_smoke_leg.py --doctor  # prove the leg can fail
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

START = "# E535:"
END = 'check(_name535, not _bad535, "; ".join(_bad535)[:240] or _d535)'

LOAD_ANCHOR = ('    _s535 = _f535.get("summary") or {}\n')
DOCTOR_LINE = ('    # doctor: hand-write the verdict in memory; the gate must refuse it\n'
               '    _f535["verdict"] = "a_verdict_this_study_never_publishes"\n')


def leg_code(doctor=False):
    src = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read()
    start = src.index(START)
    end = src.index(END) + len(END)
    code = src[start:end]
    if doctor:
        if LOAD_ANCHOR not in code:
            raise SystemExit("doctor anchor not found: the leg changed shape")
        code = code.replace(LOAD_ANCHOR, DOCTOR_LINE + LOAD_ANCHOR, 1)
    return code


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    doctor = "--doctor" in argv
    code = leg_code(doctor=doctor)
    ns = {"__name__": "__smoke_leg535__"}
    os.chdir(ROOT)
    head = ("import json, os, sys\n"
            "sys.path.insert(0, os.path.join(%r, 'scripts'))\n"
            "sys.path.insert(0, %r)\n"
            "_leg_fails = []\n"
            "def check(name, ok, detail=''):\n"
            "    if not ok:\n"
            "        _leg_fails.append((name, detail))\n") % (ROOT, ROOT)
    try:
        exec(compile(head + code, "smoke_leg535", "exec"), ns)
    except Exception as exc:                            # the leg itself blew up
        print("leg raised:", repr(exc)[:300])
        return 2
    fails = ns.get("_leg_fails") or []
    for name, detail in fails:
        print("FAIL:", name, "|", detail)
    print("legs=1 fails=%d%s" % (len(fails), " (doctor)" if doctor else ""))
    if doctor:
        # a leg that cannot fail is not a leg
        return 0 if fails else 1
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())