# -*- coding: utf-8 -*-
"""r2054 evidence pack: run the four verification legs and write qa/money-shelf-placement-r2054.md."""
from __future__ import annotations

import io
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(ROOT, "qa", "money-shelf-placement-r2054.md")

LEGS = [
    ("run", [sys.executable, r"scripts\money_shelf_placement.py", "run"]),
    ("check", [sys.executable, r"scripts\money_shelf_placement.py", "--check"]),
    ("selftest", [sys.executable, r"scripts\money_shelf_placement.py", "--selftest"]),
    ("negative controls", [sys.executable, r"results\_r2054bmc_placement_negative.py"]),
]


def main() -> int:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    parts = [
        "# QA evidence — money_shelf_placement (bm-c r2054)",
        "",
        "Scope: one new face plus its two upstream reproductions. The charter's comp line is",
        "`python -m smoke_test`, which could not be run this round (a peer host was writing shared",
        "faces, so the round was restricted to new-file landings); these four legs are what can be",
        "verified in isolation, and they are printed verbatim below rather than summarised.",
        "",
    ]
    rc_all = 0
    for name, cmd in LEGS:
        p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        rc_all |= p.returncode
        parts.append("## %s — rc=%d" % (name, p.returncode))
        parts.append("")
        parts.append("```")
        parts.append((p.stdout or "").rstrip())
        if p.stderr:
            parts.append("--- stderr ---")
            parts.append(p.stderr.rstrip())
        parts.append("```")
        parts.append("")
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts) + "\n")
    print("wrote qa/money-shelf-placement-r2054.md rc_all=%d" % rc_all)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
