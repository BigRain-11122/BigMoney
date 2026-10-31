"""Delivery divergence audit for this machine.

Answers one question with git facts only: of the local commits that ``origin/main``
does not contain, how many are reachable from an already-pushed ``origin/machine/*``
branch (= delivered somewhere, merely unmerged) and how many exist only on this
disk (= undelivered)?

Motivation (r1328 bm-b): the round report carries "local commits not on origin = N",
but N alone cannot distinguish "the merge is pending elsewhere" from "the push never
landed". Those are different problems with different owners.

Deterministic: no wall clock, no network, no writes outside ``results/``.
Evidence cutoff is derived from the fetched ``origin/main`` tip date, so re-running
on the same fetched tree byte-reproduces the same file.

Usage:
    python scripts/delivery_divergence_audit.py run
    python scripts/delivery_divergence_audit.py selftest
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "delivery_divergence.json")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout


def _git_optional(*args: str) -> str:
    """Like ``_git`` but a non-zero exit yields an empty string (e.g. unset config)."""
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout if proc.returncode == 0 else ""


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def split_delivered(ahead: list[str], undelivered: list[str]) -> tuple[list[str], list[str]]:
    """Pure set arithmetic: undelivered must be a subset of ahead."""
    undelivered_set = set(undelivered)
    stray = sorted(undelivered_set - set(ahead))
    if stray:
        raise ValueError(f"undelivered commits not in ahead set: {stray[:3]}")
    delivered = [sha for sha in ahead if sha not in undelivered_set]
    return delivered, [sha for sha in ahead if sha in undelivered_set]


def refspec_covers_machine(specs: list[str]) -> bool:
    """A plain ``+refs/heads/main:...`` refspec leaves local machine refs stale.

    r1328 bm-b: with only the main refspec fetched, every ahead commit reads as
    undelivered (109/109) although each is reachable from a pushed machine branch.
    The reading is an artifact of the refspec, not a delivery failure.
    """
    return any("machine/" in s for s in specs)


def build() -> dict:
    machine_id = json.load(
        open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8")
    )["machine_id"]

    head_sha = _git("rev-parse", "HEAD").strip()
    origin_tip = _git("rev-parse", "origin/main").strip()
    origin_date = _git("log", "-1", "--format=%cd", "--date=short", "origin/main").strip()

    ahead = _lines(_git("rev-list", "origin/main..HEAD"))
    behind = _lines(_git("rev-list", "HEAD..origin/main"))

    machine_tips = _lines(
        _git("for-each-ref", "--format=%(objectname)", "refs/remotes/origin/machine/")
    )

    if ahead and machine_tips:
        undelivered = _lines(
            _git("rev-list", "origin/main..HEAD", "--not", *machine_tips)
        )
    else:
        undelivered = list(ahead) if ahead else []

    delivered, undelivered = split_delivered(ahead, undelivered)

    # Split machine branches by owner so the face names how many pushed branches
    # exist per machine alongside the undelivered count.
    by_machine: dict[str, int] = {}
    branches = _lines(
        _git(
            "for-each-ref",
            "--format=%(refname:short)|%(objectname)|%(committerdate:short)",
            "refs/remotes/origin/machine/",
        )
    )
    latest: dict[str, dict] = {}
    for line in branches:
        name, tip, when = line.split("|")
        short = name.replace("refs/remotes/origin/", "")
        owner = short.split("machine/", 1)[1].rsplit("-r", 1)[0] if "machine/" in short else short
        row = latest.get(owner)
        round_no = int(short.rsplit("-r", 1)[1]) if short.rsplit("-r", 1)[-1].isdigit() else -1
        if row is None or (when, round_no) > (row["date"], row["round_no"]):
            latest[owner] = {"branch": short, "tip": tip, "date": when, "round_no": round_no}
        by_machine[owner] = by_machine.get(owner, 0) + 1

    verdict = "all_delivered" if not undelivered else "undelivered_on_this_disk"
    specs = _lines(_git_optional("config", "--get-all", "remote.origin.fetch"))
    covered = refspec_covers_machine(specs)
    if not covered:
        # Without the machine refspec the local tips are frozen at whatever
        # fetch last wrote, so an "undelivered" count cannot be believed.
        verdict = "machine_refs_stale_do_not_read_as_undelivered" if undelivered else verdict

    return {
        "face": "delivery_divergence",
        "machine_id": machine_id,
        "evidence_cutoff": origin_date,
        "head": head_sha,
        "origin_main": origin_tip,
        "ahead_of_origin_main": len(ahead),
        "behind_origin_main": len(behind),
        "delivered_via_machine_branch": len(delivered),
        "undelivered_on_this_disk": len(undelivered),
        "undelivered_shas": undelivered,
        "machine_branch_counts": dict(sorted(by_machine.items())),
        "latest_machine_branch": dict(sorted(latest.items())),
        "machine_branch_tips_considered": len(machine_tips),
        "machine_refs_covered_by_fetch_refspec": covered,
        "machine_refs_note": (
            "false = 'git fetch' alone does not refresh origin/machine/*; run "
            "`git fetch origin +refs/heads/machine/*:refs/remotes/origin/machine/*` "
            "before trusting an undelivered count. This face is read after that fetch."
        ),
        "verdict": verdict,
        "unmerged_backlog_note": (
            "ahead_of_origin_main counts commits main has not merged; delivery is "
            "what machine/* carries. A large ahead figure with undelivered=0 means "
            "the merge is owed to whoever owns main, not a lost push."
        ),
    }


def run() -> int:
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(
        f"ahead={face['ahead_of_origin_main']} behind={face['behind_origin_main']} "
        f"delivered={face['delivered_via_machine_branch']} "
        f"undelivered={face['undelivered_on_this_disk']} verdict={face['verdict']}"
    )
    return 0 if face["verdict"] == "all_delivered" else 1


def selftest() -> int:
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except Exception as exc:  # noqa: BLE001
            legs.append((name, False, str(exc)))

    def l1():
        d, u = split_delivered(["a", "b", "c"], ["b"])
        assert d == ["a", "c"] and u == ["b"], (d, u)

    def l2():
        d, u = split_delivered(["a"], [])
        assert d == ["a"] and u == [], (d, u)

    def l3():
        try:
            split_delivered(["a"], ["z"])
        except ValueError:
            return
        raise AssertionError("stray undelivered commit was accepted")

    def l4():
        d, u = split_delivered([], [])
        assert d == [] and u == [], (d, u)

    def l5():
        assert refspec_covers_machine(["+refs/heads/main:refs/remotes/origin/main"]) is False
        assert refspec_covers_machine(
            ["+refs/heads/main:refs/remotes/origin/main",
             "+refs/heads/machine/*:refs/remotes/origin/machine/*"]
        ) is True

    for name, fn in [("delivered/undelivered split", l1), ("nothing undelivered", l2),
                     ("stray commit rejected", l3), ("empty both", l4),
                     ("main-only refspec is not machine coverage", l5)]:
        leg(name, fn)

    ok = sum(1 for _, passed, _ in legs if passed)
    for name, passed, msg in legs:
        print(f"{'PASS' if passed else 'FAIL'}  {name}{'' if passed else ': ' + msg}")
    print(f"{ok}/{len(legs)} legs")
    return 0 if ok == len(legs) else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))