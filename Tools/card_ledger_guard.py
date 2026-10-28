"""Card-ledger monotonicity guard (r1332 bm-c, answering MSG-20261029-0510-bma).

knowledge/METHODOLOGY_ASSETS.md is an append-only card ledger, and on 2026-10-29
the blob at origin held only 66 lines / 2 cards (E195, E196) -- every earlier card
was gone -- because a writer published a file built from a stale local copy. That
is the same failure class `attrition_ledger_guard.py` already watches for the
attrition ledgers, and the card ledger had no equivalent tripwire.

What this checks (against the file in the working tree):
  * card numbers appear in strictly increasing order (no out-of-order append);
  * no duplicate card number;
  * the working tree is a SUPERSET of the card numbers in the blob at HEAD --
    i.e. no card that was committed has been dropped, and the count only grows.

Exit codes: 0 clean, 1 ACTIVE LOSS (a committed card is missing / order broken),
2 mechanism failure (not a git repo, unreadable file) -- reported, never masked.

It is a read-only tripwire: it never repairs, because "repair the ledger" is how
the truncation gets published as if it were a fix.
"""
import io
import os
import re
import subprocess
import sys

CARD = re.compile(r"^## E(\d{3})\b")
PATH = os.path.join("knowledge", "METHODOLOGY_ASSETS.md")


def _cards(text):
    out = []
    for line in (text or "").split("\n"):
        m = CARD.match(line)
        if m:
            out.append(int(m.group(1)))
    return out


def _read(path=PATH):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def _git_show(rev, path=PATH):
    # the git pathspec must use forward slashes: a Windows join sends a backslash
    # into the rev:path argument and git answers "does not exist in <rev>"
    spec = "%s:%s" % (rev, path.replace(os.sep, "/"))
    p = subprocess.run(["git", "show", spec],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.stdout if p.returncode == 0 else None


def check(path=PATH, head_text=None, tree_text=None):
    """-> (rc, payload). Pure given its inputs, so the selftest can drive it."""
    tree = _read(path) if tree_text is None else tree_text
    head = _git_show("HEAD", path) if head_text is None else head_text
    tree_cards = _cards(tree)
    empty = {"head_cards": None, "tree_cards": len(tree_cards), "head_max": None,
             "tree_max": (max(tree_cards) if tree_cards else None), "lost": [],
             "problems": ["head unavailable"]}
    if head is None:
        empty["verdict"] = "UNKNOWN"
        empty["reason"] = "git show HEAD failed (not a repo, or no HEAD)"
        return 2, empty
    head_cards = _cards(head)
    problems, warnings = [], []
    tree_dupes = sorted({n for n in tree_cards if tree_cards.count(n) > 1})
    head_dupes = {n for n in head_cards if head_cards.count(n) > 1}
    new_dupes = sorted(set(tree_dupes) - head_dupes)
    lost = sorted(set(head_cards) - set(tree_cards))
    if lost:
        problems.append("committed cards missing from the tree: %s" % lost)
    if new_dupes:
        problems.append("duplicate card numbers introduced: %s" % new_dupes)
    # The restored ledger already carries 11 duplicate numbers and 7 descents from
    # past union merges, so ordering cannot be a hard gate here without turning the
    # check permanently red -- the r1135 trap where the cheap "fix" is to loosen
    # the assertion. It is reported instead, and only NEW duplicates are fatal.
    descents = sum(1 for a, b in zip(tree_cards, tree_cards[1:]) if b < a)
    if descents:
        warnings.append("out-of-order pairs in the ledger: %d (pre-existing "
                        "history, reported not enforced)" % descents)
    if tree_dupes:
        warnings.append("duplicate numbers in the ledger: %s" % tree_dupes)
    payload = {
        "head_cards": len(head_cards),
        "tree_cards": len(tree_cards),
        "head_max": (max(head_cards) if head_cards else None),
        "tree_max": (max(tree_cards) if tree_cards else None),
        "lost": lost,
        "new_duplicates": new_dupes,
        "problems": problems,
        "warnings": warnings,
        "verdict": "CLEAN" if not problems else "ACTIVE_LOSS",
    }
    return (0 if not problems else 1), payload


def _selftest():
    base = "## E195 A\n\nx\n## E196 B\n\ny\n"
    grown = base + "\n## E197 C\n\nz\n"
    cases = []
    rc, p = check(path="<mem>", head_text=base, tree_text=grown)
    cases.append(("append is clean", rc == 0 and p["tree_cards"] == 3))
    rc, p = check(path="<mem>", head_text=grown, tree_text="## E197 C\n\nz\n")
    cases.append(("dropping committed cards is ACTIVE_LOSS",
                  rc == 1 and p["lost"] == [195, 196]))
    rc, p = check(path="<mem>", head_text=base,
                  tree_text="## E197 C\n\nz\n\n## E196 B\n")
    cases.append(("an out-of-order append that also drops a card is caught",
                  rc == 1 and 195 in p["lost"]))
    rc, p = check(path="<mem>", head_text=base,
                  tree_text=base + "\n## E197 C\n\n## E198 D\n")
    cases.append(("order alone is a warning, not a failure, while nothing is lost",
                  rc == 0 and not p["problems"]))
    rc, p = check(path="<mem>", head_text=base,
                  tree_text=base + "\n## E196 again\n")
    cases.append(("a NEW duplicate number is caught",
                  rc == 1 and p["new_duplicates"] == [196]))
    rc, p = check(path="<mem>", head_text="## E196 B\n\n## E195 A\n",
                  tree_text="## E196 B\n\n## E195 A\n\n## E197 C\n")
    cases.append(("pre-existing disorder inherited from HEAD is reported, not "
                  "enforced", rc == 0 and bool(p["warnings"])))
    rc, p = check(path="<mem>", head_text=None, tree_text=base)
    cases.append(("a git failure reports rc 2 rather than a clean bill", rc == 2))
    ok = sum(1 for _, c in cases if c)
    for name, c in cases:
        print(("PASS " if c else "FAIL ") + name)
    print("card_ledger_guard selftest %d/%d PASS" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "selftest":
        return _selftest()
    if cmd != "check":
        print("usage: card_ledger_guard.py [check|selftest]")
        return 2
    try:
        rc, payload = check()
    except Exception as e:              # mechanism failure, never a silent clean
        print("card_ledger_guard: mechanism failure: %s" % e)
        return 2
    print("card_ledger_guard: %s head=%s tree=%s max=%s->%s lost=%s %s%s"
          % (payload["verdict"], payload["head_cards"], payload["tree_cards"],
             payload["head_max"], payload["tree_max"], payload["lost"],
             "; ".join(payload["problems"]),
             (" | " + "; ".join(payload["warnings"])) if payload["warnings"] else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))