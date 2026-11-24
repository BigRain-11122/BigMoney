"""Negative control for scripts/capital_marginal_road.py (r2076 bm-c).

Proves the check() of the new face actually fails when the world moves, distinguishes "an input
moved" (STALE) from "the face disagrees with itself" (CHECK FAILED), catches a hand-edited page,
and restores every byte it touched.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "capital_marginal_road.json")
PAGE = os.path.join(ROOT, "research", "CAPITAL_MARGINAL_ROAD.md")
SCRIPT = os.path.join(ROOT, "scripts", "capital_marginal_road.py")
PROBE_INPUTS = [
    "results/etf_nobond_vt.json",
    "results/etf_book_capacity_edge.json",
    "results/etf_book_ticket_floor.json",
    "results/idx_fut_carry_open_capital.json",
    "results/idx_fut_carry_lend_breakeven.json",
    "results/idx_fut_roll_cost.json",
    "results/etf_book_cash_rate_flip.json",
]

RESULTS = []


def leg(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def run(args):
    p = subprocess.run([sys.executable, SCRIPT] + args, capture_output=True, text=True, cwd=ROOT)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def sha(path):
    import hashlib
    with io.open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    before = {p: sha(os.path.join(ROOT, p)) for p in PROBE_INPUTS + ["results/capital_marginal_road.json", "research/CAPITAL_MARGINAL_ROAD.md"]}
    tmp = tempfile.mkdtemp(prefix="negctl_marginal_road_")
    face_bak = os.path.join(tmp, "face.json")
    page_bak = os.path.join(tmp, "page.md")
    shutil.copy2(FACE, face_bak)
    shutil.copy2(PAGE, page_bak)

    try:
        # 0 baseline green
        rc, out = run(["--check"])
        leg("baseline check rc0", rc == 0 and "CHECK OK" in out, out.strip()[:120])

        # 1 a number in the face moves -> CHECK FAILED, not STALE
        doc = json.loads(io.open(FACE, encoding="utf-8").read())
        doc["books"]["carry"]["income_cny_upper"] += 25.0
        io.open(FACE, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        rc, out = run(["--check"])
        leg("face number moved -> rc3 CHECK FAILED naming the field",
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out and "income_cny_upper" in out,
            out.strip()[:160])

        # 2 only the inputs digest moves -> STALE, never CHECK FAILED
        shutil.copy2(face_bak, FACE)
        doc = json.loads(io.open(FACE, encoding="utf-8").read())
        doc["inputs_digest"] = "0" * 64
        io.open(FACE, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        rc, out = run(["--check"])
        leg("inputs digest moved -> rc3 STALE without CHECK FAILED",
            rc == 3 and "STALE" in out and "CHECK FAILED" not in out, out.strip()[:160])

        # 3 a hand-edited page line -> rc3 naming the page block
        shutil.copy2(face_bak, FACE)
        page = io.open(PAGE, encoding="utf-8").read()
        target = "| cash | 2,294 a year | always available |"
        leg("page line really exists before editing it", target in page)
        io.open(PAGE, "w", encoding="utf-8", newline="\n").write(page.replace(target, target.replace("2,294", "2,295")))
        rc, out = run(["--check"])
        leg("page edited -> rc3 naming page block",
            rc == 3 and "page block" in out, out.strip()[:160])

        # 4 page markers removed -> unreadable block is a red, not a pass
        shutil.copy2(page_bak, PAGE)
        io.open(PAGE, "w", encoding="utf-8", newline="\n").write("# empty\n")
        rc, out = run(["--check"])
        leg("page block unreadable -> rc3", rc == 3 and ("page block" in out or "page missing" in out), out.strip()[:160])

        # 5 face missing -> STALE face missing
        shutil.copy2(page_bak, PAGE)
        os.remove(FACE)
        rc, out = run(["--check"])
        leg("face missing -> STALE face missing", rc == 3 and "STALE face missing" in out, out.strip()[:160])

        # 6 restore and go green again
        shutil.copy2(face_bak, FACE)
        rc, out = run(["--check"])
        leg("restored -> CHECK OK", rc == 0 and "CHECK OK" in out, out.strip()[:120])

        # 7 zero pollution: every input face byte-identical to before the control
        same = all(sha(os.path.join(ROOT, p)) == before[p] for p in PROBE_INPUTS)
        leg("seven input faces byte-identical after the control", same)
    finally:
        shutil.copy2(face_bak, FACE)
        shutil.copy2(page_bak, PAGE)
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for _, passed, _ in RESULTS if passed)
    for name, passed, detail in RESULTS:
        print("  %s %s%s" % ("OK  " if passed else "FAIL", name, ("  <- " + detail) if not passed else ""))
    print("NEGCTL %d/%d" % (ok, len(RESULTS)))
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
