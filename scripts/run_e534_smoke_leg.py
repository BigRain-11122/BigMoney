"""Run the E534 smoke leg standalone (the full suite is ~20 minutes; this is the same block).

    python scripts/run_e534_smoke_leg.py           # run the leg as published
    python scripts/run_e534_smoke_leg.py --doctor  # prove the leg can fail
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

START = "# E534:"
END = "check(_name534, not _bad534, \"; \".join(_bad534)[:240] or _d534)"
DOCTOR_END = "check(_name534, not _bad534, \"DOCTORED\")"


def leg_code(doctor=False):
    src = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read()
    start = src.index(START)
    end = src.index(END) + len(END)
    code = src[start:end]
    if doctor:
        # a leg that cannot fail is not a leg: point the gate at a face with a hand-written verdict
        code = code.replace(
            "_f534 = json.load(open(os.path.join(\"results\", \"state_tilt\", "
            "\"captopayload_latest.json\"),\n                           encoding=\"utf-8\"))",
            "_f534 = json.load(open(os.path.join(\"results\", \"state_tilt\", "
            "\"captopayload_latest.json\"),\n                           encoding=\"utf-8\"))\n"
            "    _f534[\"verdict\"] = _m534.V_ABSENCE_IS_PUBLISHED")
    return code


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    doctor = "--doctor" in argv
    sys.path.insert(0, HERE)
    os.chdir(ROOT)
    ns = {"json": json, "os": os,
          "check": lambda n, ok, d: print("%s %s :: %s" % ("PASS" if ok else "FAIL", n, d))}
    exec(compile(leg_code(doctor), "smoke_test.py:E534", "exec"), ns)
    bad = ns.get("_bad534") or []
    print("E534 smoke leg%s: %s" % (" (doctored)" if doctor else "",
                                    "clean" if not bad else "%d problem(s)" % len(bad)))
    if doctor:
        return 0 if bad else 1
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())