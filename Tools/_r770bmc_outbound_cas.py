# -*- coding: utf-8 -*-
"""r770 bm-c: O-1820 review-package CAS direct-invest to group repo.
Law: group-tree CAS direct-invest (temp-index + commit-tree + push sha:main,
zero worktree-index touch beyond staged adds, r814 precedent family).
Files: 5 jpgs + REVIEW-PACKAGE-v1.md -> fleet/mv0001-handover/outbound/.
Hard-verify: 40-hex shas, push output fatal/rejected/failed/error scan,
post-push fetch + ls-tree self-proof (O-20261001-1108 delivery gate)."""
import os
import re
import shutil
import subprocess
import tempfile

G = r"K:\Fluxgroup\FluxGroup"
SRC_JPG = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\outbound_jpg"
SRC_MD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\REVIEW-PACKAGE-v1.md"
DEST = os.path.join(G, "fleet", "mv0001-handover", "outbound")
MSG = ("mv0001 O-1820 style-sample + storyboard review package v1 (bm-c r770): "
       "5 representative scenes (goddess PASS / glass PASS / library "
       "double-exposure composite x2 beat-delivered-by-construction / carve "
       "best-attempt), honest 5-generation gate ledger incl. 2 locally-"
       "unreachable requirements + 3-option decision menu, storyboard tables "
       "A/B + SP 12-item checklist; video lane stays frozen until CEO OK")
RECEIPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r770bmc_outbound_cas.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def run(cwd, args, env=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def main():
    facts = {"legs": []}
    # 1. materialize files in group worktree (untracked; CAS stages via temp index)
    os.makedirs(DEST, exist_ok=True)
    files = []
    for n in sorted(os.listdir(SRC_JPG)):
        if n.endswith(".jpg"):
            shutil.copy2(os.path.join(SRC_JPG, n), os.path.join(DEST, n))
            files.append("fleet/mv0001-handover/outbound/" + n)
    shutil.copy2(SRC_MD, os.path.join(DEST, "REVIEW-PACKAGE-v1.md"))
    files.append("fleet/mv0001-handover/outbound/REVIEW-PACKAGE-v1.md")
    facts["files"] = files

    # 2. CAS loop (max 3 attempts against moving origin)
    idx = tempfile.mktemp(suffix=".idx")
    ok_push = False
    for attempt in range(1, 4):
        rc, _, err = run(G, ["git", "fetch", "origin"])
        if rc != 0:
            facts["legs"].append("fetch-fail-%d: %s" % (attempt, err[:200]))
            continue
        rc, base, err = run(G, ["git", "rev-parse", "origin/main"])
        base = base.strip()
        if rc != 0 or not HEX40.match(base):
            facts["legs"].append("base-bad-%d: %r %s" % (attempt, base, err[:120]))
            continue
        env = dict(os.environ, GIT_INDEX_FILE=idx)
        rc, _, err = run(G, ["git", "read-tree", base], env=env)
        if rc != 0:
            facts["legs"].append("read-tree-fail-%d: %s" % (attempt, err[:120]))
            continue
        rc, _, err = run(G, ["git", "add", "--"] + files, env=env)
        if rc != 0:
            facts["legs"].append("add-fail-%d: %s" % (attempt, err[:120]))
            continue
        rc, tree, err = run(G, ["git", "write-tree"], env=env)
        tree = tree.strip()
        if rc != 0 or not HEX40.match(tree):
            facts["legs"].append("tree-bad-%d: %r %s" % (attempt, tree, err[:120]))
            continue
        rc, newc, err = run(G, ["git", "commit-tree", tree, "-p", base, "-m", MSG])
        newc = newc.strip()
        if rc != 0 or not HEX40.match(newc):
            facts["legs"].append("commit-bad-%d: %r %s" % (attempt, newc, err[:120]))
            continue
        rc, out, err = run(G, ["git", "push", "origin", newc + ":refs/heads/main"])
        blob = (out + err)
        bad = re.search(r"fatal|rejected|failed|error", blob, re.I)
        if rc == 0 and not bad:
            facts["legs"].append("push-ok-%d base=%s newc=%s" % (attempt, base, newc))
            facts["base"] = base
            facts["newc"] = newc
            ok_push = True
            break
        facts["legs"].append("push-race-%d rc=%d: %s" % (attempt, rc, blob[:200]))
    facts["push_ok"] = ok_push

    # 3. post-verify: fresh fetch + ls-tree self-proof
    if ok_push:
        run(G, ["git", "fetch", "origin"])
        rc, tip, _ = run(G, ["git", "rev-parse", "origin/main"])
        facts["origin_tip_after"] = tip.strip()
        rc, ls, _ = run(G, ["git", "ls-tree", "origin/main",
                             "fleet/mv0001-handover/outbound/"])
        facts["ls_tree"] = ls.strip().splitlines()
        facts["delivered"] = (tip.strip() == facts.get("newc"))
    try:
        os.remove(idx)
    except OSError:
        pass
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        import json
        json.dump(facts, fh, indent=1)
    print("push_ok=%s delivered=%s newc=%s files=%d" %
          (facts["push_ok"], facts.get("delivered"), facts.get("newc"), len(files)))
    for leg in facts["legs"]:
        print(leg)
    return 0 if facts["push_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
