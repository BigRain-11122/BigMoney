"""r315 bm-c S0: CODELY.md union resolver for cherry-pick b8881296b onto origin/main.

r314 union recipe (md append-block = common base block + both sides' unique lines,
no dedup loss). Both sides must be pure appends over the merge-base block;
sanity asserts fail-closed if either side rewrote history lines.
"""
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
BASE = "576fd2c1ec41ee8e625e5a59ee27a262b55c8432"  # merge-base (origin..b8881296b)
OURS = "94ac4ecbc"   # origin/main tip at pick time (bm-b r503 codely pit entry)
THEIRS = "b8881296b"  # round 314 commit (r314 bm-c CAS entry)


def show_bytes(ref, path):
    return subprocess.check_output(["git", "-C", REPO, "show", f"{ref}:{path}"])


def main():
    b = show_bytes(BASE, "CODELY.md").decode("utf-8")
    o = show_bytes(OURS, "CODELY.md").decode("utf-8")
    t = show_bytes(THEIRS, "CODELY.md").decode("utf-8")
    bl, ol, tl = b.splitlines(), o.splitlines(), t.splitlines()
    assert tl[: len(bl)] == bl, "theirs not a pure append over base"
    assert ol[: len(bl)] == bl, "ours not a pure append over base"
    add_o, add_t = ol[len(bl):], tl[len(bl):]
    dup = {x for x in (set(add_o) & set(add_t)) if x.strip()}
    assert not dup, f"duplicate non-blank added lines between sides: {dup}"
    union_lines = bl + add_o + add_t
    out = "\n".join(union_lines)
    if t.endswith("\n"):
        out += "\n"
    with open(REPO + r"\CODELY.md", "wb") as f:
        f.write(out.encode("utf-8"))
    print(f"union written: base={len(bl)} ours_add={len(add_o)} theirs_add={len(add_t)}")


if __name__ == "__main__":
    main()
