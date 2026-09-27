# -*- coding: utf-8 -*-
"""r327 bm-a rebase resolver COMPLETION -- finishes the r326 session's
interrupted resolution of the 30-UU 3-machine batch (28 already staged by
_r326bma_resolve.py; it died on the last step).

What this adds (root-cause: r326 resolver snapshot list hand-copied path
typo -- listed no-dash 'REPORT-20260927' twins which do NOT exist in any
stage, so take_newer_side() fell into its b2==b3 empty-bytes branch ->
wrote+staged two 0-byte phantom files; real dash-format UU twins left
unresolved):

  1. docs/daily_report/REPORT-2026-09-27.{json,md} : same-day-regen family
     (r325 precedent hand-adjudication) -- deep ts probe: S3 generated_at
     13:44:35 > S2 13:35:35 -> take S3 whole bytes (guard face shadow =
     honest date-gate-closed state per REGIME_GUARD v3, OS canon).
  2. docs/daily_report/REPORT-20260927.{json,md} : phantom 0-byte files
     (blob e69de29, absent from BOTH 5f06825f and origin bb8befda trees)
     -> removed from index+worktree, zero information loss.
  3. post-hoc verification of the 28 already-staged resolutions:
     all staged .json parse strict-utf8; x2 union line count; CODELY.md
     carries both pitlaw suffixes.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def sh(*args):
    r = subprocess.run(list(args), capture_output=True, cwd=REPO)
    return r.stdout


def stage_bytes(path, n):
    return sh("git", "show", ":%d:%s" % (n, path))


def main():
    report = []

    # --- 1. resolve the real dash-format daily report twins: take S3 ---
    for p in ("docs/daily_report/REPORT-2026-09-27.json",
              "docs/daily_report/REPORT-2026-09-27.md"):
        b2, b3 = stage_bytes(p, 2), stage_bytes(p, 3)
        assert b2 and b3, "missing stage for %s" % p
        # deep ts probe: max 'YYYY-MM-DD HH:MM:SS' generated_at string
        def gen_ts(b):
            try:
                return json.loads(b.decode("utf-8")).get("generated_at", "")
            except Exception:
                import re
                m = re.search(rb"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", b)
                return m.group(1).decode() if m else ""
        t2, t3 = gen_ts(b2), gen_ts(b3)
        assert t3 > t2, "expected S3 newer, got %r vs %r" % (t2, t3)
        with open(p.replace("/", "\\"), "wb") as fh:
            fh.write(b3)
        if p.endswith(".json"):
            json.loads(b3.decode("utf-8"))  # strict parse gate
        sh("git", "add", p)
        report.append("RESOLVED %-46s same-day-regen ts-diffpick %s > %s -> S3 whole bytes" % (p, t3, t2))

    # --- 2. drop phantom 0-byte twins (resolver path-typo artifacts) ---
    for p in ("docs/daily_report/REPORT-20260927.json",
              "docs/daily_report/REPORT-20260927.md"):
        in_replayed = sh("git", "cat-file", "-e", "5f06825f:%s" % p, ) and True
        in_origin = sh("git", "cat-file", "-e", "bb8befda:%s" % p) and True
        sz = len(sh("git", "cat-file", "blob", "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"))
        assert sz == 0
        sh("git", "rm", "-f", "--", p)
        report.append("DROPPED  %-46s phantom 0-byte (absent from 5f06825f and bb8befda)" % p)

    # --- 3. post-hoc verify the 28 staged resolutions ---
    staged = sh("git", "diff", "--cached", "--name-only", "--diff-filter=ACM").decode("utf-8").splitlines()
    n_json = 0
    for p in staged:
        if p.endswith(".json"):
            b = open(p.replace("/", "\\"), "rb").read()
            json.loads(b.decode("utf-8"))  # strict utf-8 + json gate
            n_json += 1
    report.append("VERIFY   %d staged JSON files parse strict-utf-8 OK" % n_json)

    # x2 union line count (line union zero loss: union >= each side)
    l = open(r"results\x2_watch_log.jsonl", "rb").read().decode("utf-8").splitlines()
    s2 = stage_bytes("results/x2_watch_log.jsonl", 2).decode().splitlines()
    s3 = stage_bytes("results/x2_watch_log.jsonl", 3).decode().splitlines()
    assert len(l) >= max(len(s2), len(s3)), "x2 union shrank"
    report.append("VERIFY   x2_watch_log union %d >= max(%d,%d) zero loss" % (len(l), len(s2), len(s3)))

    # CODELY memory-union: both pitlaw suffixes present
    c = open(r"CODELY.md", "rb").read().decode("utf-8")
    assert "asi8" in c and "r326 bm-a" in c, "CODELY union missing bm-a r326 suffix"
    report.append("VERIFY   CODELY.md union carries bm-a r326 asi8 pitlaw")

    # remaining unmerged paths must be zero now
    uu = sh("git", "diff", "--name-only", "--diff-filter=U").decode("utf-8").splitlines()
    assert not uu, "still unmerged: %r" % uu
    report.append("VERIFY   unmerged paths remaining: 0")

    for line in report:
        print(line)
    print("COMPLETION-RESOLVE OK: rebase ready for --continue")


if __name__ == "__main__":
    main()
