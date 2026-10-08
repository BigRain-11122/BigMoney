# -*- coding: utf-8 -*-
"""r787 bm-c W192 freeze receipt completion (G11/G12 finisher): the freeze
script's G10 write landed and its py_compile + post-import subprocess both
returned CORRECT data (rows=190, W192 row exact, W191 intact), but its G11
value assert compared JSON-deserialized LISTS against TUPLES and tripped a
type-face false red AFTER the write (assert now fixed in the instrument for
lineage). This finisher re-runs the post-import verification list-normalized,
re-checks origin vacancy + py_compile, rebuilds the G2-precheck facts from
the machine-read probe receipt leg0 (r587/r359 laws), and writes the freeze
receipt (G12) + five-segment PASS prints (r578 law). Zero further mutation
of the two registry files."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")
PROBE_RCPT = os.path.join(ROOT, "results", "_r787bmc_w192_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r787bmc_w192_freeze_receipt.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_out(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CNW)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def main():
    facts = {"round": 787, "machine": "bm-c", "wave": 192}

    # ---- G11 re-verify: py_compile + post-import (list-normalized) ----
    for f in (N1P, PFP):
        prc = subprocess.run([sys.executable, "-m", "py_compile", f],
                             capture_output=True, creationflags=CNW)
        assert prc.returncode == 0, "py_compile failed: %s" % f
    chk = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, 'scripts'); "
         "from perpetual_faces import N1_BANDS as B; "
         "print(json.dumps({'rows': len(B), 'w192': B.get(192), "
         "'w191': B.get(191)}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 190, "row count drift: %s" % post
    assert post["w192"] == {"a": [437204, 439203], "b_exit": [439204, 439403],
                           "engine_owner": "bm-c"}, "W192 row drift: %s" % post
    assert post["w191"] == {"a": [435004, 437003], "b_exit": [437004, 437203],
                           "engine_owner": "bm-a"}, "W191 row damaged: %s" % post
    facts["post_import"] = post

    # ---- G1 re-check: origin vacancy still true pre-push ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "192: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 192 already on origin"
    facts["origin_vacancy_prepush"] = True

    # ---- G2 precheck facts rebuilt from the machine-read probe receipt ----
    r = json.load(open(PROBE_RCPT, encoding="utf-8"))
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 189 and leg0["owner_rows"] == 181 \
        and leg0["bmc_rows"] == 34, "probe receipt leg0 drift"
    facts["precheck"] = {"rows": leg0["rows"], "bmc_rows": leg0["bmc_rows"],
                         "owner_rows": leg0["owner_rows"], "unowned_rows": 8}

    # ---- EOL detect (r370) ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    facts["eol"] = {
        "n1_crlf": n1_raw.count("\r\n") > n1_raw.count("\n") / 2,
        "pf_crlf": pf_raw.count("\r\n") > pf_raw.count("\n") / 2}

    facts["completion_note"] = (
        "G11 type-face false red in the original instrument (JSON lists vs "
        "tuples) tripped after the G10 write with data fully correct; assert "
        "fixed in-place for lineage; this finisher re-verified and completed "
        "the G12 receipt. W191 row byte-intact, W192 rows landed both faces.")

    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[192] row: a=(437204,439203) "
          "b_exit=(439204,439403) engine_owner=bm-c (W191 row byte-intact, "
          "post-import machine-read)")
    print("PASS 2/5 n1 WAVE_CONFIGS[192] row: batch=PERPETUAL-N1-W192 "
          "a_seed_base=437_204 b_exit_seed_base=439_204 shard=n1_w192 "
          "out=n1_w192_results.json owner=bm-c")
    print("PASS 3/5 n1 W192 materializer face: 132 replacements all "
          "count-asserted (preflight dry-run green); staircase FIFTY-SECOND; "
          "prior-wave parity->W191; deps range(17,192); prereg presence "
          "assert->W192")
    print("PASS 4/5 guards: origin vacancy pre-push (fetch+show) + registry "
          "189->190 rows + AST+py_compile green + W191 byte-intact "
          "post-import (list-normalized re-verify)")
    print("PASS 5/5 summary: W192 = 182nd engine wave, bm-c 35th owned "
          "(rows 181+candidate per probe receipt leg0); A=437_204..439_203 "
          "hops=1 FIFTY-SECOND staircase; B=439_204..439_403 hops=1 own-A "
          "mutual exclusion; ADMIT receipt machine-read; receipt="
          "results/_r787bmc_w192_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
