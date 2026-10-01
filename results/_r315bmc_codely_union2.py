"""r315 bm-c S0 v2: CODELY.md union for re-pick of dd774df83 onto fresh origin tip.

Origin side was rewritten by bm-a r514 hot-cold re-archival (not a pure append),
so v1's pure-append assert no longer holds. v2 = stage-aware:
  ours (stage :2:)   = current detached HEAD (= fresh origin tip) full text
  theirs (stage :3:) = my pick1 commit text -> extract the single r314 entry
Union = ours + blank line + r314 entry at EOF (de-facto append-at-end convention).
Fail-closed: exactly one r314 entry must exist in theirs and must NOT already be in ours.
"""
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ENTRY_PREFIX = "- [2026-10-01 12:3x r314 bm-c]"


def stage(n, path):
    return subprocess.check_output(["git", "-C", REPO, "show", f":{n}:{path}"]).decode("utf-8")


def main():
    ours = stage(2, "CODELY.md")
    theirs = stage(3, "CODELY.md")
    hits = [l for l in theirs.splitlines() if l.startswith(ENTRY_PREFIX)]
    assert len(hits) == 1, f"expected exactly 1 r314 entry in theirs, got {len(hits)}"
    entry = hits[0]
    assert entry not in ours, "r314 entry already present on ours side - dedupe skip needed"
    out = ours
    if not out.endswith("\n"):
        out += "\n"
    out += "\n" + entry
    if theirs.endswith("\n"):
        out += "\n"
    with open(REPO + r"\CODELY.md", "wb") as f:
        f.write(out.encode("utf-8"))
    print(f"codely v2 union written: ours={len(ours)}B + r314 entry -> {len(out)}B")


if __name__ == "__main__":
    main()
