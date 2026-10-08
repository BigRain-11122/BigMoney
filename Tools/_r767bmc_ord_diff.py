# -*- coding: utf-8 -*-
"""r767 bm-c ORD delta extractor (S7 closeout second sweep found ord_delta
true: 6C0018CC -> 35560092, +2,636B on group-tree docs/orders.md). Read-only
probe: locate the commit pair straddling the watermark change, extract added
lines, classify BigMoney-relevance. Group ledgers stay group-owned (no
write to group tree). Facts -> results/_r767bmc_ord_diff.txt."""
import hashlib
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
OLD_SHA = "6C0018CCB51341C745316D4F63AA1165B044BB3B"
NEW_SHA = "35560092AC76E933B7E0EF5FC3700AB5D380C497"


def git_out(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def main():
    rc, out, _ = git_out(["log", "origin/main", "--format=%H|%ad|%s",
                          "--date=format:%Y-%m-%d %H:%M:%S", "-10"])
    commits = []
    for line in out.decode("utf-8", "replace").strip().splitlines():
        sha, date, subj = line.split("|", 2)
        rc2, blob, _ = git_out(["show", sha + ":docs/orders.md"])
        blob_sha = hashlib.sha1(blob).hexdigest().upper()
        commits.append((sha, date, subj, blob_sha))

    old_c = new_c = None
    for sha, date, subj, blob_sha in commits:
        if blob_sha == OLD_SHA and old_c is None:
            old_c = sha
        if blob_sha == NEW_SHA:
            new_c = sha
    if new_c is None:
        # newest commit IS the new blob; old may be older than window
        new_c = commits[0][0] if commits and commits[0][3] == NEW_SHA else None

    lines_out = ["ORD delta 6C0018CC -> 35560092 extraction (r767 closeout sweep)"]
    for sha, date, subj, blob_sha in commits:
        mark = ""
        if sha == old_c:
            mark = "  <= OLD watermark"
        if sha == new_c:
            mark = "  <= NEW watermark"
        lines_out.append("%s %s %s [orders.md sha1=%s]%s" % (sha[:9], date, subj[:80],
                                                             blob_sha[:8], mark))

    added = []
    if old_c and new_c:
        rc3, diff, err = git_out(["diff", old_c, new_c, "--", "docs/orders.md"])
        if rc3 == 0:
            for ln in diff.decode("utf-8", "replace").splitlines():
                if ln.startswith("+") and not ln.startswith("+++"):
                    added.append(ln[1:])
        else:
            lines_out.append("diff rc=%d err=%s" % (rc3, err.decode("utf-8", "replace")[:200]))
    else:
        lines_out.append("locate failed: old_c=%s new_c=%s -- falling back to tail probe"
                         % (old_c, new_c))
        rc4, blob, _ = git_out(["show", "origin/main:docs/orders.md"])
        tail = blob.decode("utf-8", "replace").splitlines()[-60:]
        added = tail

    lines_out.append("")
    lines_out.append("=== added lines (%d) ===" % len(added))
    lines_out.extend(added)

    text = "\n".join(lines_out)
    hits = [ln for ln in added
            if any(k in ln for k in ("BigMoney", "bigmoney", "quant", "bm-c", "量化"))]
    verdict = ("BIGMONEY-RELEVANT: %d hit(s)" % len(hits)) if (old_c and new_c) \
        else "LOCATE-FAILED tail-probe fallback"
    lines_out.append("")
    lines_out.append("verdict: " + verdict)
    with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r767bmc_ord_diff.txt",
              "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines_out) + "\n")
    print("old_c=%s new_c=%s added=%d bigmoney_hits=%d"
          % ((old_c or "None")[:9], (new_c or "None")[:9], len(added), len(hits)))
    for ln in hits[:20]:
        print("HIT: " + ln[:200])


if __name__ == "__main__":
    main()
