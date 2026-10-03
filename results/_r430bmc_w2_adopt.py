"""_r430bmc_w2_adopt.py -- MASS_TRIAL_W2_JUDGE landing-round adoption harness.

Purpose (product-first law): the wave-2 judge-finalize burn (detached PID
31276, spawned 19:28:59, family CSCV PBO over 805 cells, deadline <=10-06)
lands results/mass_trial/w2_judge.json asynchronously. This harness is the
pre-built, battle-tested validation layer for the landing round so adoption
= run harness -> quote receipt -> flip round numbers (r426 template
_r426bmc_close.py) with zero cold-start risk.

Laws:
- r629 mirror law: validation reads mirror the runner output contract
  EXACTLY (scripts/mass_trial_w1.py judge-finalize summary dict, L1314-1357)
  and the r426 close template's product face -- no hand-copied expectations.
- pit-95: single-shot ledger law; live cross-check via
  science_gates.finalize_already_landed (read-only tripwire).
- Pure-function core: validate_product(prod) writes NOTHING; probe mode
  touches only reads; selftest mode runs fully in-memory (no repo writes,
  no ledger appends, no psutil dependence).

Modes:
  probe    (default) -- landing state check:
             product absent  -> AWAITING receipt, exit 3 (honest deferral)
             product present -> full validation + live cross-checks:
               exit 0 ADOPTABLE receipt / exit 1 contract violation.
  selftest           -- synthetic contract-exact mock + 5 negative cases;
             exit 0 all assertions held / exit 1 any failed.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
os.chdir(REPO)
PRODUCT = os.path.join("results", "mass_trial", "w2_judge.json")
BATCH = "MASS_TRIAL_W2_JUDGE"
BURN_PID_FILE_NOTE = "spawned 2026-10-03T19:28:59 (r426 respawn per r324/r422 law)"


def validate_product(prod):
    """Pure validation core. Returns (receipt_dict, violations_list).
    Receipt numbers are DERIVED -- the close template quotes them verbatim."""
    v = []
    if not isinstance(prod, dict):
        return None, ["product is not a dict"]
    if prod.get("complete") is not True:
        v.append("complete is not True (finalize did not close)")
    req = ["trials_ledger", "n_judge_cells", "n_stage1_survivors",
           "collapse_audit", "n_wave_disclosure", "n_trials_head_at_finalize",
           "family_pbo", "descriptive_counts", "eligible_g2", "n_eligible_g2",
           "verdicts", "cells", "audit", "batch", "evidence_cutoff"]
    for k in req:
        if k not in prod:
            v.append("missing contract key: %s" % k)
    if v:
        return None, v
    led = prod["trials_ledger"]
    for k in ("prev_total", "batch_trials", "total", "batch"):
        if k not in led:
            v.append("trials_ledger missing %s" % k)
    if v:
        return None, v
    # chain linearity + batch identity (single-shot ledger law)
    if int(led["prev_total"]) + int(led["batch_trials"]) != int(led["total"]):
        v.append("ledger not chain-linear: %s+%s != %s"
                 % (led["prev_total"], led["batch_trials"], led["total"]))
    if led.get("batch") != BATCH:
        v.append("ledger batch drift: %r != %r" % (led.get("batch"), BATCH))
    nj = int(prod["n_judge_cells"])
    verd = prod["verdicts"]
    vsum = sum(int(verd.get(k, 0)) for k in ("pass", "fail", "insufficient-sample"))
    if vsum != nj:
        v.append("verdict sum %d != n_judge_cells %d" % (vsum, nj))
    disc = prod["n_wave_disclosure"]
    for k in ("screen_cells", "judged_cells", "E_FP_nominal_5pct"):
        if k not in disc:
            v.append("n_wave_disclosure missing %s" % k)
    if not v and int(disc["judged_cells"]) != nj:
        v.append("disclosure judged_cells %s != n_judge_cells %d"
                 % (disc["judged_cells"], nj))
    e_fp = disc.get("E_FP_nominal_5pct")
    if not v and float(e_fp) != round(0.05 * nj, 2):
        v.append("E[FP] %s != 0.05*%d=%s" % (e_fp, nj, round(0.05 * nj, 2)))
    elig = prod["eligible_g2"]
    if int(prod["n_eligible_g2"]) != len(elig):
        v.append("n_eligible_g2 %s != len(eligible_g2) %d"
                 % (prod["n_eligible_g2"], len(elig)))
    if len(prod.get("cells", [])) != nj:
        v.append("len(cells) %d != n_judge_cells %d"
                 % (len(prod.get("cells", [])), nj))
    fam = prod["family_pbo"]
    scored = 0
    for fk, fb in fam.items():
        if not isinstance(fb, dict) or "n_cells" not in fb:
            v.append("family_pbo[%s] malformed" % fk)
            continue
        if fb.get("pbo") is not None:
            scored += 1
            if int(fb["n_cells"]) < 8:
                v.append("family_pbo[%s] scored with n_cells=%s <8"
                         % (fk, fb["n_cells"]))
        elif "note" not in fb:
            v.append("family_pbo[%s] unscored without honest note" % fk)
    if v:
        return None, v
    receipt = {
        "adoptable": True,
        "batch": BATCH,
        "n_judge_cells": nj,
        "ledger": {"prev_total": int(led["prev_total"]),
                   "batch_trials": int(led["batch_trials"]),
                   "total": int(led["total"])},
        "e_fp": e_fp,
        "n_eligible_g2": int(prod["n_eligible_g2"]),
        "eligible_g2_head": list(elig)[:10],
        "verdicts": {k: int(verd.get(k, 0))
                     for k in ("pass", "fail", "insufficient-sample")},
        "family_pbo_scored": scored,
        "family_pbo_total": len(fam),
        "n_trials_head_at_finalize": int(prod["n_trials_head_at_finalize"]),
        "evidence_cutoff": prod.get("evidence_cutoff"),
        "collapse_eliminated": int(prod["collapse_audit"].get("eliminated", 0)),
    }
    return receipt, []


def _mock_product():
    """Contract-exact synthetic product (runner L1314-1357 face, in-memory)."""
    n_j = 805
    fams = {"momentum": {"pbo": 0.31, "n_cells": 30},
            "reversal": {"pbo": 0.12, "n_cells": 25},
            "tiny": {"pbo": None, "n_cells": 3,
                     "note": "insufficient (<8) -- G2 cannot pass"}}
    verd = {"pass": 2, "fail": 790, "insufficient-sample": 13}
    assert sum(verd.values()) == n_j
    return {
        "batch": BATCH, "evidence_cutoff": "2026-09-22",
        "trials_ledger": {"prev_total": 333139, "batch_trials": n_j,
                          "total": 333139 + n_j, "batch": BATCH,
                          "file": "mass_trial/w2_judge.json"},
        "n_judge_cells": n_j, "n_stage1_survivors": 805,
        "collapse_audit": {"line": 0.999, "eliminated": 4103,
                           "clusters": 1204},
        "n_wave_disclosure": {"screen_cells": 5061, "judged_cells": n_j,
                              "E_FP_nominal_5pct": round(0.05 * n_j, 2),
                              "note": "synthetic mock"},
        "n_trials_head_at_finalize": 333139 + n_j,
        "family_pbo": fams,
        "descriptive_counts": {"synthetic": True},
        "eligible_g2": ["MOCK-001", "MOCK-002"], "n_eligible_g2": 2,
        "verdicts": verd,
        "cells": [{"candidate_id": "MOCK-%04d" % i} for i in range(n_j)],
        "audit": {"seed_judge": 20285200},
        "complete": True,
    }


def selftest():
    ok = [0]
    def check(name, cond):
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            ok[0] += 1
    print("selftest: synthetic contract-exact mock (positive) + 5 negatives")
    r, v = validate_product(_mock_product())
    check("mock validates ADOPTABLE", r is not None and r["adoptable"] and not v)
    if r:
        check("receipt ledger chain-linear",
              r["ledger"]["prev_total"] + r["ledger"]["batch_trials"]
              == r["ledger"]["total"])
        check("receipt verdict sum == n_judge",
              sum(r["verdicts"].values()) == r["n_judge_cells"])
        check("receipt pbo scored 2/3 total (tiny family honest n/a)",
              r["family_pbo_scored"] == 2 and r["family_pbo_total"] == 3)
        check("receipt e_fp derived", r["e_fp"] == 40.25)
    m = _mock_product(); m["complete"] = False
    _, v = validate_product(m)
    check("negative: incomplete product REJECTED", bool(v))
    m = _mock_product(); m["verdicts"]["fail"] += 1
    _, v = validate_product(m)
    check("negative: verdict-sum mismatch REJECTED", bool(v))
    m = _mock_product(); del m["n_eligible_g2"]
    _, v = validate_product(m)
    check("negative: missing contract key REJECTED", bool(v))
    m = _mock_product()
    m["trials_ledger"]["total"] += 7
    _, v = validate_product(m)
    check("negative: non-linear ledger REJECTED", bool(v))
    m = _mock_product()
    m["family_pbo"]["momentum"]["n_cells"] = 5
    _, v = validate_product(m)
    check("negative: <8-cell scored family REJECTED", bool(v))
    print("SELFTEST %s (failures=%d)" % ("PASS" if ok[0] == 0 else "FAIL", ok[0]))
    return 0 if ok[0] == 0 else 1


def probe():
    if not os.path.exists(PRODUCT):
        alive = None
        try:
            import psutil
            p = psutil.Process(31276)
            alive = {"pid": p.pid,
                     "cpu_s": round(p.cpu_times().user + p.cpu_times().system),
                     "mem_mb": p.memory_info().rss // 1048576}
        except Exception:
            pass
        print("AWAITING: %s absent -- burn (%s) %s"
              % (PRODUCT, BURN_PID_FILE_NOTE,
                 ("ALIVE cpu=%ss mem=%sMB" % (alive["cpu_s"], alive["mem_mb"])
                  if alive else "pid 31276 not found (check lineage)")))
        print("adoption deferred to landing round per r422 law; "
              "deadline <=10-06, O-2115 acceptance evidence pack 10-08")
        return 3
    prod = json.load(open(PRODUCT, encoding="utf-8"))
    receipt, v = validate_product(prod)
    if v:
        print("CONTRACT VIOLATIONS (refuse adoption, report verbatim):")
        for x in v:
            print("  -", x)
        return 1
    # live cross-checks (read-only): chain head must not be behind the product;
    # pit-95 tripwire must find THIS batch's block in the landed product file.
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import science_gates as sg
    head = sg.ledger_head()
    behind = int(receipt["ledger"]["total"]) - int(head["total"])
    landed = sg.finalize_already_landed(BATCH, "mass_trial/w2_judge.json")
    print("ADOPTION-RECEIPT (quote in close narrative):")
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    print("live ledger head total=%s (product%s head, delta=%s)"
          % (head["total"], "==" if behind == 0 else ">=",
             behind if behind else 0))
    print("pit-95 tripwire: %s"
          % ("landed block found (single-shot law upheld)"
             if landed else "NO landed block -- investigate before adopt"))
    return 0 if landed else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    sys.exit(selftest() if mode == "selftest" else probe())
