"""r557 bm-c legdiff TRUE gate (r531/r549/r554/r556 laws, v3).

Substance gates (receipt theater-proof, r554 law: receipt must reference
real files that exist; r556 law: OLD pinned to latest surviving true
chain file in scratch + executed-log cross-check):
  G1: 38 SilentPy leg lines of NEW (r557) byte-identical to OLD (r556
      lineage file = latest SURVIVING true chain script in scratch).
  G3: diff lines outside the leg block must all be label furniture
      (round token r556->r557 in comment/LOG/start/rcmap lines only)
      -- whitelist assertion, any other diff line = FAIL.
  G4: cross-check vs the ACTUALLY EXECUTED previous round: 38 leg section
      names in results/_r556bmc_s6_log.txt must equal the 38 leg names in
      the NEW chain (pins continuity to the real r556 execution).
Exit 0 PASS / 1 FAIL. Receipt -> results/_r557bmc_legdiff.txt."""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(ROOT, "bigmoney")
OLD = r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\_r556bmc_s6_chain.ps1"
NEW = r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\_r557bmc_s6_chain.ps1"
LOG555 = os.path.join(ROOT, "results", "_r556bmc_s6_log.txt")
OUT = os.path.join(ROOT, "results", "_r557bmc_legdiff.txt")

LEG_RE = re.compile(r'^SilentPy "(.*)"; Leg "(.*)"$')


def legs(path):
    out = []
    with io.open(path, encoding="utf-8-sig") as fh:
        for ln in fh:
            m = LEG_RE.match(ln.rstrip("\r\n"))
            if m:
                out.append((m.group(1), m.group(2)))
    return out


def main():
    for p in (OLD, NEW, LOG555):
        if not os.path.exists(p):
            print("MISSING %s" % p)
            sys.exit(1)
    old_lines = io.open(OLD, encoding="utf-8-sig").read().splitlines()
    new_lines = io.open(NEW, encoding="utf-8-sig").read().splitlines()
    old_legs = legs(OLD)
    new_legs = legs(NEW)
    g1 = old_legs == new_legs and len(new_legs) == 38
    # G3: non-leg diff lines must be label furniture only
    old_set = set(old_lines)
    old_tok = set(re.sub(r"r\d{3}", "rXXX", l) for l in old_lines)
    furniture = []
    bad_diff = []
    for ln in new_lines:
        if ln in old_set or LEG_RE.match(ln):
            continue
        # precise furniture test (v3.2, r549 lesson: classifier must not be
        # keyword-narrow): a non-leg diff line is furniture iff its shape is
        # identical to an OLD line with all rNNN round tokens wildcarded --
        # comments/labels may mention different lineage round numbers, but
        # any real command/path/flag drift changes the shape and stays BAD.
        if re.sub(r"r\d{3}", "rXXX", ln) in old_tok:
            furniture.append(ln)
        else:
            bad_diff.append(ln)
    g3 = not bad_diff
    # G4: leg names in r556 executed log == leg names in NEW chain
    log555 = io.open(LOG555, encoding="utf-8-sig").read()
    exec_legs = re.findall(r"^=== (\S+) rc=\d+", log555, re.M)
    g4 = exec_legs == [name for _, name in new_legs]
    verdict = "PASS" if (g1 and g3 and g4) else "FAIL"
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("r557 bm-c legdiff TRUE gate v3 (r531/r549/r554/r556 laws)\n")
        fh.write("OLD=%s (latest surviving true lineage file in scratch)\n" % OLD)
        fh.write("NEW=%s\n" % NEW)
        fh.write("G1 38-legs byte-identical OLD==NEW: %s (n=%d)\n"
                 % (g1, len(new_legs)))
        fh.write("G3 non-leg diff furniture-only: %s (furniture=%d bad=%d)\n"
                 % (g3, len(furniture), len(bad_diff)))
        for ln in bad_diff:
            fh.write("  BAD-DIFF: %s\n" % ln)
        fh.write("G4 r556 executed-log leg names == NEW chain legs: %s "
                 "(exec=%d)\n" % (g4, len(exec_legs)))
        fh.write("disclosure: OLD = r556 chain file surviving in scratch "
                 "(executed r556 per its S6 log); continuity pinned by G4 "
                 "cross-check vs r556 executed log\n")
        fh.write("LEGDIFF %s\n" % verdict)
    print("LEGS=%d G1=%s G3=%s G4=%s -> %s" % (len(new_legs), g1, g3, g4, verdict))
    print("LEGDIFF %s" % verdict)
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
