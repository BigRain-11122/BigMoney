# -*- coding: utf-8 -*-
"""r455 bm-c closeout stage 4: merge commit (receipts included) + push +
delivery self-proof (fetch + ahead==0 per r436 push_verify contract; four-word
fatal check per r454 GM law)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["add", "results/_r455bmc_close1.py", "results/_r455bmc_close2.py",
             "results/_r455bmc_close_survey.py", "results/_r455bmc_uu_survey.py",
             "results/_r455bmc_uu_peek.py", "results/_r455bmc_merge_resolve.py"])
    print("ADD_RECEIPTS rc=%d" % r.returncode)
    r = run(["commit", "-m",
             "merge origin/main bm-a r665/bm-b r658 waves (14 UU per r450/r452 "
             "recipes: 12 regen take-ours by honest ts 08:39-41>08:35-37, "
             "lhb_update_status take-theirs 08:36>08:20, compute_audit cross-"
             "machine union 201+201->212 zero-loss, token_usage per-m union "
             "==ours newer; marker+JSON guards PASS)"])
    print("MERGE_COMMIT rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:300]))
    r = run(["rev-parse", "HEAD"])
    head = r.stdout.strip()
    print("HEAD:", head)
    r = run(["push", "origin", "main"])
    print("PUSH rc=%d" % r.returncode)
    out = (r.stdout or "") + (r.stderr or "")
    print(out[:800])
    if r.returncode == 0:
        r = run(["fetch", "origin"])
        r = run(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
        behind, ahead = r.stdout.strip().split("\t")
        print("DELIVERY behind=%s ahead=%s" % (behind, ahead))
        fatal_words = [w for w in ("fatal", "rejected", "failed", "error")
                       if w in out.lower()]
        ok = (ahead == "0") and not fatal_words
        print("PUSH_VERIFY:", "DELIVERED" if ok else
              "NOT-DELIVERED(fatal=%s ahead=%s)" % (fatal_words, ahead))
    print("STAGE4_DONE")


if __name__ == "__main__":
    main()
