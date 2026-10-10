# r825 bm-b: post_review stale-criteria P0 repair (T-81-LANDING-HOOKS pin).
# Family precedent: r638 stale-criteria repair (337137157) / r809 P0 fix
# (89c83e7e1) -- idempotent repoint + reviewer re-derive to green + receipt.
# Face: r817 committed LANDING_HOOKS_P1.md v1.1 addendum (2be696154,
# v1.0 three-family verdict lines untouched, changelog row added per
# single-source law) -> file sha16 moved 150ce7a7c54cbc19 ->
# cdcebae5b9f7fed5; the criteria pin still expects the pre-amendment
# sha -> persistent false NO on every post_review run.
# Fix scope: shared criteria.json + machine-local criteria.bm-b.json only
# (criteria.bm-a.json / bm-c = their own lanes, untouched per ownership).
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join(ROOT, "research", "LANDING_HOOKS_P1.md")
OLD_PIN = "150ce7a7c54cbc19"
# candidate historical blobs whose LF face may equal OLD_PIN (freeze
# 174be4b88 -> legal sec.6/progress backfill 8b3927718 -> citation fix
# fa0126893); the pin was captured post-backfill, not at bare freeze.
PIN_BASIS_CANDIDATES = ["fa0126893", "8b3927718", "174be4b88"]
FILES = ["results/post_review_criteria.json",
         "results/post_review_criteria.bm-b.json"]


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    out = {"old_pin": OLD_PIN, "files": {}, "checks": {}}
    # 1) working-tree file must be committed-clean (no in-flight edits)
    r = subprocess.run(["git", "status", "--porcelain", "--", PREREG],
                       capture_output=True, text=True)
    out["checks"]["prereg_clean"] = (r.stdout.strip() == "")
    # 2) current sha16
    cur = open(PREREG, "rb").read()
    new_pin = sha16(cur)
    out["new_pin"] = new_pin
    # 3) some historical committed blob must hash (EOL-normalized) to the
    #    OLD pin -- proves the repoint basis (old pin was a real file state)
    pin_basis = None
    basis_map = {}
    for c in PIN_BASIS_CANDIDATES:
        r2 = subprocess.run(["git", "show", "%s:research/LANDING_HOOKS_P1.md"
                             % c], capture_output=True)
        if r2.returncode == 0:
            h = sha16(r2.stdout.replace(b"\r\n", b"\n"))
            basis_map[c] = h
            if h == OLD_PIN and pin_basis is None:
                pin_basis = c
    out["checks"]["pin_basis_map"] = basis_map
    out["checks"]["pin_basis_commit"] = pin_basis
    out["checks"]["freeze_matches_old_pin"] = (pin_basis is not None)
    if not (out["checks"]["prereg_clean"]
            and out["checks"]["freeze_matches_old_pin"]):
        json.dump(out, open(os.path.join(ROOT, "results",
                         "_r825bmb_pr_pinfix.json"), "w",
                        encoding="utf-8"), ensure_ascii=True, indent=1)
        print("ABORT: basis checks failed: %s" % out["checks"])
        return 2
    # 4) idempotent repoint per file (exact one-occurrence swap)
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        b = open(p, "rb").read()
        n = b.count(OLD_PIN.encode())
        rec = {"occurrences_before": n}
        if n == 0:
            rec["action"] = "none (already current or absent)"
        elif n == 1:
            b2 = b.replace(OLD_PIN.encode(), new_pin.encode())
            tmp = p + ".tmp"
            open(tmp, "wb").write(b2)
            os.replace(tmp, p)
            rec["action"] = "repinned"
            rec["new_pin"] = new_pin
        else:
            rec["action"] = "REFUSED (multiple occurrences)"
        # verify roundtrip
        b3 = open(p, "rb").read()
        rec["old_pin_remaining"] = b3.count(OLD_PIN.encode())
        rec["new_pin_count"] = b3.count(new_pin.encode())
        out["files"][rel] = rec
    ok = all(v.get("old_pin_remaining") == 0 for v in out["files"].values())
    out["repoint_ok"] = ok
    json.dump(out, open(os.path.join(ROOT, "results",
                     "_r825bmb_pr_pinfix.json"), "w",
                    encoding="utf-8"), ensure_ascii=True, indent=1)
    print(json.dumps({"new_pin": new_pin, "repoint_ok": ok,
                      "files": out["files"]}))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
