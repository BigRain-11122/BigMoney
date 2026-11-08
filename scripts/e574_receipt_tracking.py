# -*- coding: utf-8 -*-
"""E574 -- does a round's chain run leave any evidence git can carry?

Source (E572, r1600 bm-b): 2 of the 3 receipts it priced are not tracked in git at all, so the
only evidence that nobody rewrote them was a modification time.  A receipt git never sees also
never reaches the delivery channel (the machine branch), so the round-report row becomes the only
surviving witness of that run -- and if no row names it either, the run leaves nothing behind but
a file that disappears with the worktree.

This study prices that for every chain receipt the fleet has written:

  population     results/_r<round>bm<machine>_s6_chain.json on disk (the same population
                 E561/E572 used, so the join is against the receipts those studies priced)
  tracked        git carries the file (git ls-files membership; a name can be tracked without the
                 bytes still being in the worktree, so presence and tracking are separate fields)
  cited          a round-report row names the receipt's own log token '<round>bm<X>_s6'
  round          the integer round parsed out of the name, and whether any commit subject names
                 "round N" at all (one git log pass, not one call per round)

Classes (first match wins, each row keeps the witness that fired):
  carried_by_git              git has the file
  named_but_not_carried       untracked, but a round-report row names it (the row is the witness)
  vanishing                   untracked and unnamed -- the class the card asks to price

A name that does not parse as an integer round (_r--all, _r0, _rrun, _rverify, ...) is published
as its own flag and kept out of the round-reachability arm rather than folded in as zero: those
are ad-hoc/test receipts written into the live directory, which is itself a finding (E562 pit).

Usage: python scripts/e574_receipt_tracking.py [build|check|verify|selftest]
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-11-08"
NAME_RE = re.compile(r"^_r(.+?)bm([abc])_s6_chain\.json$")
REPORT_DIR = os.path.join(ROOT, "logs", "iteration-loop")

C_CARRIED = "carried_by_git"
C_NAMED = "named_but_not_carried"
C_VANISHING = "vanishing"
CLASSES = (C_CARRIED, C_NAMED, C_VANISHING)


def _git(args, timeout=300):
    try:
        out = subprocess.run(["git"] + args, cwd=ROOT, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, timeout=timeout)
    except Exception:
        return ""
    return out.stdout.decode("utf-8", "replace")


def receipt_paths():
    """Chain receipts present in the worktree, as forward-slash repo paths."""
    found = []
    for p in glob.glob(os.path.join(ROOT, "results", "_r*bm*_s6_chain.json")):
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        found.append(rel)
    return sorted(found)


def tracked_set():
    out = _git(["ls-files", "results/_r*bm*_s6_chain.json"])
    return set(line.strip() for line in out.splitlines() if line.strip())


def report_corpus():
    """Every round-report file, as one text blob.  The row is read as a blob on purpose: a
    citation is a name somewhere in a row, not a column that could be parsed."""
    blob = []
    for p in sorted(glob.glob(os.path.join(REPORT_DIR, "round_reports*.md"))):
        try:
            with io.open(p, encoding="utf-8", errors="replace") as fh:
                blob.append(fh.read())
        except OSError:
            continue
    return "\n".join(blob)


def rounds_named_in_commits():
    """One git pass: every round number any commit subject names."""
    out = _git(["log", "--format=%s", "-n", "40000"])
    seen = {}
    rx = re.compile(r"round\s+(\d+)", re.I)
    for line in out.splitlines():
        for m in rx.finditer(line):
            n = int(m.group(1))
            seen[n] = seen.get(n, 0) + 1
    return seen


def ignored_map(paths):
    """Which receipts git is told never to carry, and by which .gitignore rule.

    This matters for the verdict: if the ignore rule is deliberate then git is not a lost carrier
    but a carrier that was switched off, and the round-report row is the *designed* witness.
    """
    if not paths:
        return {}
    out = _git(["check-ignore", "-v", "--"] + paths)
    m = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        src = parts[0].rsplit(":", 2)
        m[parts[-1].replace("\\", "/")] = {
            "source": src[0].replace("\\", "/"),
            "line": src[1] if len(src) > 1 else None,
            "pattern": src[2] if len(src) > 2 else None,
        }
    return m


def log_token(rel):
    base = os.path.basename(rel)
    for suffix in ("_chain.json",):
        if base.endswith(suffix):
            base = base[:-len(suffix)]
            break
    return base.lstrip("_")


def build():
    paths = receipt_paths()
    tracked = tracked_set()
    corpus = report_corpus()
    rnd_seen = rounds_named_in_commits()
    ignored = ignored_map(paths)

    rows = []
    for rel in paths:
        name = os.path.basename(rel)
        m = NAME_RE.match(name)
        rnd_raw = m.group(1) if m else None
        machine = m.group(2) if m else None
        rnd = int(rnd_raw) if (rnd_raw and rnd_raw.isdigit()) else None
        token = log_token(rel)
        run_token = token[:-3] if token.endswith("_s6") else token
        is_tracked = rel in tracked
        cited = token in corpus
        run_cited = run_token in corpus
        on_disk = os.path.exists(os.path.join(ROOT, rel))
        if is_tracked:
            klass, witness = C_CARRIED, "git ls-files carries this path"
        elif cited:
            klass, witness = C_NAMED, ("untracked, but a round-report row names %r" % token)
        else:
            klass, witness = C_VANISHING, ("untracked and no round-report row names %r" % token)
        rows.append({
            "path": rel,
            "round_raw": rnd_raw,
            "round": rnd,
            "round_is_an_int": rnd is not None,
            "machine": machine,
            "token": token,
            "run_token": run_token,
            "on_disk": on_disk,
            "tracked": is_tracked,
            "ignored_by": ignored.get(rel),
            "cited": cited,
            "run_token_cited": run_cited,
            "round_named_by_a_commit": (rnd_seen.get(rnd, 0) if rnd is not None else None),
            "class": klass,
            "witness": witness,
        })

    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    unparsed = [r["path"] for r in rows if not r["round_is_an_int"]]
    vanishing_int = [r for r in rows if r["class"] == C_VANISHING and r["round_is_an_int"]]
    vanish_unreachable = [r["path"] for r in vanishing_int
                          if r["round_named_by_a_commit"] == 0]
    vanish_reachable = [r["path"] for r in vanishing_int
                        if (r["round_named_by_a_commit"] or 0) > 0]

    if by_class[C_VANISHING] == 0:
        verdict = "every_chain_receipt_on_disk_is_either_in_git_or_named_by_a_round_row"
    elif vanish_unreachable:
        verdict = ("some_runs_leave_no_reachable_trace: a receipt git does not carry, no row "
                   "names, and no commit subject names its round")
    else:
        verdict = ("untracked_and_unnamed_receipts_exist_but_their_rounds_are_named_by_a_commit")

    face = {
        "cutoff": CUTOFF,
        "card": "E574",
        "machine": "bm-b",
        "study": "E574_whether_a_round_chain_run_leaves_evidence_git_can_carry",
        "population": {
            "glob": "results/_r*bm*_s6_chain.json",
            "on_disk": len(paths),
            "tracked": len(tracked),
            "note": ("on_disk counts the worktree; tracked counts git ls-files membership, so a "
                     "tracked path whose bytes are gone would still be counted here"),
        },
        "summary": dict(by_class,
                        vanishing_whose_round_no_commit_names=len(vanish_unreachable),
                        vanishing_whose_round_a_commit_names=len(vanish_reachable),
                        vanishing_whose_run_token_a_row_mentions=sum(
                            1 for r in rows if r["class"] == C_VANISHING and r["run_token_cited"]),
                        names_that_are_not_an_integer_round=len(unparsed)),
        "citation_rule": (
            "cited = the receipt's own token '<round>bm<machine>_s6' appears in a round-report "
            "row; run_token_cited is the wider '<round>bm<machine>' match and is published "
            "separately because a row that names only the round can be naming a different "
            "artifact of that round"),
        "verdict": verdict,
        "verdict_recompute": "from_summary",
        "ignore_rule": {
            "receipts_git_never_carries": sum(1 for r in rows if r["ignored_by"]),
            "distinct_rules": sorted({"%s:%s" % ((r["ignored_by"] or {}).get("source", ""),
                                                 (r["ignored_by"] or {}).get("line"))
                                      for r in rows if r["ignored_by"]}),
            "note": ("a receipt matched by .gitignore is not a carrier git lost; it is a carrier "
                     "switched off on purpose, so the round-report row is the designed witness "
                     "for that class and an unnamed one has no witness at all"),
        },
        "unparsed_names": unparsed,
        "vanishing_rounds_with_no_commit": sorted(
            {r["round"] for r in vanishing_int if r["round_named_by_a_commit"] == 0}),
        "rows": rows,
    }
    return face


def out_paths():
    return (os.path.join(OUTDIR, "RECEIPTTRACK-%s.json" % CUTOFF),
            os.path.join(OUTDIR, "RECEIPTTRACK_latest.json"))


def recompute(face):
    """The gate recomputes the verdict from the rows; a hand-written verdict is refused."""
    rows = face.get("rows") or []
    by_class = {c: sum(1 for r in rows if r.get("class") == c) for c in CLASSES}
    vanishing_int = [r for r in rows if r.get("class") == C_VANISHING
                     and r.get("round_is_an_int")]
    unreachable = [r for r in vanishing_int if r.get("round_named_by_a_commit") == 0]
    if by_class[C_VANISHING] == 0:
        v = "every_chain_receipt_on_disk_is_either_in_git_or_named_by_a_round_row"
    elif unreachable:
        v = ("some_runs_leave_no_reachable_trace: a receipt git does not carry, no row "
             "names, and no commit subject names its round")
    else:
        v = "untracked_and_unnamed_receipts_exist_but_their_rounds_are_named_by_a_commit"
    return v, by_class, unreachable


def cmd_build():
    face = build()
    dated, latest = out_paths()
    for p in (dated, latest):
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    s = face["summary"]
    print("rows=%d carried=%d named=%d vanishing=%d unparsed=%d"
          % (len(face["rows"]), s[C_CARRIED], s[C_NAMED], s[C_VANISHING],
             s["names_that_are_not_an_integer_round"]))
    print("verdict: %s" % face["verdict"])
    print("vanishing_with_no_commit_naming_round=%d rounds=%s"
          % (len(face["vanishing_rounds_with_no_commit"]), face["vanishing_rounds_with_no_commit"]))
    print("wrote %s" % os.path.relpath(dated, ROOT).replace("\\", "/"))
    return 0


def cmd_check():
    problems = []
    dated, latest = out_paths()
    if not os.path.exists(dated):
        print("CHECK FAIL no face at %s" % dated)
        return 1
    with io.open(dated, encoding="utf-8") as fh:
        face = json.load(fh)
    rows = face.get("rows") or []
    if not rows:
        problems.append("face carries no rows")
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("%s: class %r outside %s" % (r.get("path"), r.get("class"), CLASSES))
        if r.get("tracked") and r.get("class") != C_CARRIED:
            problems.append("%s: tracked but class %r" % (r.get("path"), r.get("class")))
        if r.get("class") == C_NAMED and not r.get("cited"):
            problems.append("%s: named class without a citation" % r.get("path"))
        if r.get("class") == C_VANISHING and r.get("cited"):
            problems.append("%s: vanishing class with a citation" % r.get("path"))
        if r.get("cited") is False and r.get("class") == C_NAMED:
            problems.append("%s: named without cited flag" % r.get("path"))
    v, by_class, unreachable = recompute(face)
    if v != face.get("verdict"):
        problems.append("verdict does not re-derive: stored %r recomputed %r"
                        % (face.get("verdict"), v))
    stored = face.get("summary") or {}
    for c in CLASSES:
        if stored.get(c) != by_class[c]:
            problems.append("summary[%s]=%r but rows give %d" % (c, stored.get(c), by_class[c]))
    if stored.get("vanishing_whose_round_no_commit_names") != len(unreachable):
        problems.append("summary unreachable count does not re-derive")
    if problems:
        print("CHECK FAIL %d problem(s)" % len(problems))
        for p in problems[:20]:
            print(" - %s" % p)
        return 1
    print("CHECK PASS %d rows re-derived" % len(rows))
    return 0


def cmd_verify():
    """Re-walk the disk and refuse a face that no longer matches the live population."""
    fresh = build()
    dated, latest = out_paths()
    with io.open(dated, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    fp = {r["path"]: r["class"] for r in fresh["rows"]}
    sp = {r["path"]: r["class"] for r in face["rows"]}
    for p in sorted(set(fp) - set(sp)):
        problems.append("new receipt on disk not in the face: %s" % p)
    for p in sorted(set(sp) - set(fp)):
        problems.append("face names a receipt that is not on disk: %s" % p)
    for p in sorted(set(fp) & set(sp)):
        if fp[p] != sp[p]:
            problems.append("%s: class drifted %s -> %s" % (p, sp[p], fp[p]))
    if fresh["verdict"] != face["verdict"]:
        problems.append("verdict drifted: %r -> %r" % (face["verdict"], fresh["verdict"]))
    if problems:
        print("VERIFY FAIL %d problem(s)" % len(problems))
        for p in problems[:20]:
            print(" - %s" % p)
        return 1
    print("VERIFY PASS %d rows, population unchanged, verdict=%s"
          % (len(fresh["rows"]), fresh["verdict"]))
    return 0


def cmd_selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # name parsing
    m = NAME_RE.match("_r1246bmb_s6_chain.json")
    leg("name parses round", m and m.group(1) == "1246")
    leg("name parses machine", m and m.group(2) == "b")
    leg("non-integer round is not parsed as one",
        not NAME_RE.match("_r--allbmc_s6_chain.json").group(1).isdigit())

    # token extraction
    leg("token strips the leading underscore",
        log_token("results/_r1246bmb_s6_chain.json") == "r1246bmb_s6")
    leg("token keeps the machine letter",
        "bmb" in log_token("results/_r7bmb_s6_chain.json"))

    # class assignment in each arm, on synthetic rows
    def cls(tracked, cited):
        if tracked:
            return C_CARRIED
        return C_NAMED if cited else C_VANISHING

    leg("tracked wins over citation", cls(True, True) == C_CARRIED)
    leg("tracked without citation still carried", cls(True, False) == C_CARRIED)
    leg("untracked with citation is named", cls(False, True) == C_NAMED)
    leg("untracked without citation vanishes", cls(False, False) == C_VANISHING)

    # verdict arms
    def verdict_for(rows):
        by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
        vanishing_int = [r for r in rows if r["class"] == C_VANISHING
                         and r.get("round_is_an_int")]
        unreachable = [r for r in vanishing_int if r.get("round_named_by_a_commit") == 0]
        if by_class[C_VANISHING] == 0:
            return "clean"
        return "unreachable" if unreachable else "reachable"

    leg("no vanishing => clean verdict",
        verdict_for([{"class": C_CARRIED}]) == "clean")
    leg("vanishing with an unnamed round => unreachable",
        verdict_for([{"class": C_VANISHING, "round_is_an_int": True,
                      "round_named_by_a_commit": 0}]) == "unreachable")
    leg("vanishing whose round a commit names => reachable",
        verdict_for([{"class": C_VANISHING, "round_is_an_int": True,
                      "round_named_by_a_commit": 3}]) == "reachable")
    leg("non-integer round keeps out of the reachability arm",
        verdict_for([{"class": C_VANISHING, "round_is_an_int": False,
                      "round_named_by_a_commit": None}]) == "reachable")

    # the live face, if present, must re-derive
    dated, _ = out_paths()
    if os.path.exists(dated):
        with io.open(dated, encoding="utf-8") as fh:
            face = json.load(fh)
        v, by_class, _u = recompute(face)
        leg("live face verdict re-derives", v == face.get("verdict"))
        leg("live face class counts re-derive",
            all(face["summary"].get(c) == by_class[c] for c in CLASSES))
        leg("live face rows are non-empty", len(face.get("rows") or []) > 0)
    else:
        leg("live face absent (skipped)", True)

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print("  %s %s" % ("PASS" if ok else "FAIL", n))
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "build"
    if cmd == "build":
        return cmd_build()
    if cmd == "check":
        return cmd_check()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print("unknown command %r (use build|check|verify|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))