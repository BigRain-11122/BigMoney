"""r2056 negative controls for scripts/money_accrual_rate.py.

Three things must be true, and each is exercised on the real face:
  1. a poisoned row is CHECK FAILED and the text does NOT say STALE (it is my arithmetic);
  2. a moved upstream face is STALE and the text does NOT say CHECK FAILED (it is input drift);
  3. after restoring both by bytes, check is rc0 again -- so the controls prove what they claim.
Writes qa/money-accrual-rate-r2056.md.  Touches nothing else.
"""
import io
import json
import os
import shutil
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FACE = os.path.join(ROOT, "results", "money_accrual_rate.json")
UP = os.path.join(ROOT, "results", "money_shelf_placement.json")
SCRIPT = os.path.join(ROOT, "scripts", "money_accrual_rate.py")
QA = os.path.join(ROOT, "qa", "money-accrual-rate-r2056.md")
TMP = os.path.join(ROOT, "results", "_r2056bmc_tmp")


def run(*args):
    p = subprocess.run([sys.executable] + list(args), cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    os.makedirs(TMP, exist_ok=True)
    face_bak = os.path.join(TMP, "face.json")
    up_bak = os.path.join(TMP, "upstream.json")
    shutil.copy2(FACE, face_bak)
    shutil.copy2(UP, up_bak)
    lines = ["# QA evidence -- scripts/money_accrual_rate.py (r2056 bm-c)", ""]
    try:
        rc0, out0 = run(SCRIPT, "run")
        rc1, out1 = run(SCRIPT, "check")
        lines += ["## 1. baseline", "", "```", "run rc=%d" % rc0, out0.strip()[:400], "",
                  "check rc=%d" % rc1, out1.strip()[:400], "```", ""]

        # control A: poison one printed number -> CHECK FAILED, never STALE
        face = json.load(io.open(FACE, encoding="utf-8"))
        target = next(r for r in face["rows"] if r.get("measurable"))
        target["floor_accrual_pct"] = round((target["floor_accrual_pct"] or 0.0) + 0.9, 4)
        with io.open(FACE, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1)
        rcA, outA = run(SCRIPT, "check")
        lines += ["## 2. control A: one row's floor moved by +0.90pp", "",
                  "```", "rc=%d" % rcA, outA.strip()[:800], "```", "",
                  "- verdict: %s" % ("PASS (FAILED without STALE)" if rcA == 1 and "FAILED" in outA
                                     and "STALE" not in outA else "FAIL")]
        shutil.copy2(face_bak, FACE)

        # control B: move the upstream shelf face -> STALE, never CHECK FAILED
        with io.open(UP, "ab") as f:
            f.write(b"\n")
        rcB, outB = run(SCRIPT, "check")
        lines += ["", "## 3. control B: one byte appended to results/money_shelf_placement.json", "",
                  "```", "rc=%d" % rcB, outB.strip()[:800], "```", "",
                  "- verdict: %s" % ("PASS (STALE without FAILED)" if rcB == 3 and "STALE" in outB
                                     and "FAILED" not in outB else "FAIL")]
        shutil.copy2(up_bak, UP)

        # control C: bytes restored -> rc0 again
        rcC, outC = run(SCRIPT, "check")
        rcS, outS = run(SCRIPT, "selftest")
        lines += ["", "## 4. restored", "", "```", "check rc=%d" % rcC, outC.strip()[:400], "",
                  "selftest rc=%d" % rcS, outS.strip().splitlines()[0] if outS.strip() else "", "```", "",
                  "- verdict: %s" % ("PASS" if rcC == 0 and rcS == 0 else "FAIL")]
        ok = (rc1 == 0 and rcA == 1 and "STALE" not in outA and rcB == 3
              and "FAILED" not in outB and rcC == 0 and rcS == 0)
        lines += ["", "## 5. summary", "", "- all controls as designed: **%s**" % ("YES" if ok else "NO")]
    finally:
        shutil.copy2(face_bak, FACE)
        shutil.copy2(up_bak, UP)

    with io.open(QA, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
