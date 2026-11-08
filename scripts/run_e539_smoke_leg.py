"""Run the E539 smoke leg standalone (the full suite is ~20 minutes; this is the same block).

    python scripts/run_e539_smoke_leg.py           # run the leg as published
    python scripts/run_e539_smoke_leg.py --doctor  # prove the leg can fail
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

START = "# E539:"
END = 'check(_name539, not _bad539, "; ".join(_bad539)[:240] or _d539)'

LOAD_ANCHOR = ('    _s539 = _f539.get("summary") or {}\n')
DOCTOR_LINE = ('    # doctor: hand-write the verdict in memory; the gate must refuse it\n'
               '    _f539["verdict"] = "a_verdict_this_study_never_publishes"\n')


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
    ns = {"__name__": "__smoke_leg539__"}
    os.chdir(ROOT)
    head = ("import json, os, sys\n"
            "sys.path.insert(0, os.path.join(%r, 'scripts'))\n"
            "_fails = []\n"
            "def check(name, ok, detail=''):\n"
            "    print(('PASS ' if ok else 'FAIL ') + name + (' -- ' + detail if detail else ''))\n"
            "    if not ok:\n"
            "        _fails.append(name)\n" % ROOT)
    exec(compile(head + code, "smoke_leg539", "exec"), ns)
    fails = ns.get("_fails") or []
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())