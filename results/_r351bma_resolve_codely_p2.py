"""R351 pass-2 CODELY entry-level union resolver (vs bmc r101 restructure).

Rebase stage semantics: :2: = HEAD (origin/main face = bmc r101: full rows + r101 row),
:3: = replayed commit (our fold face: bm-b NEW r340 row + r96/r99 pointer rows).
Union = bmc face + bm-b r340 row (r96/r99 pointers redundant: full rows on bmc face).
Zero-loss: every '- [' row of BOTH sides present in result OR in (HEAD-arch | :3:-arch).
"""
import subprocess

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout

def main():
    oB = blob(":2", "CODELY.md")   # bmc face
    tB = blob(":3", "CODELY.md")   # fold face
    bmc = oB.decode("utf-8-sig")
    fold = tB.decode("utf-8-sig")

    newrows = [l for l in fold.splitlines() if l.startswith("- [2026-09-27 20:1x r340 bm-b]")]
    assert len(newrows) == 1, f"expected bm-b r340 row once in fold face, got {len(newrows)}"

    bL = bmc.splitlines()
    last = max(i for i, l in enumerate(bL) if l.startswith("- ["))
    bL.insert(last + 1, newrows[0])
    result = "\n".join(bL)
    if bmc.endswith("\n"):
        result += "\n"

    arch_h = blob("HEAD", "research/memory-archive/202609.md").decode("utf-8", errors="replace")
    arch_t = blob(":3", "research/memory-archive/202609.md").decode("utf-8", errors="replace")
    missing = []
    for side, txt in (("bmc", bmc), ("fold", fold)):
        for l in txt.splitlines():
            if l.startswith("- [") and l not in result and l not in arch_h and l not in arch_t:
                missing.append((side, l[:60]))
    # our own r96/r99 pointer rows are redundant by construction: the FULL rows are on the
    # bmc face in the result tree -- verify that before allowing the drop (zero content loss)
    full_present = all(marker in result for marker in (
        "- [2026-09-27 2026-09-27 18:35 r96 bm-c]",
        "- [2026-09-27 19:4x r99 bm-c]",
    ))
    missing = [(s, l) for (s, l) in missing if not (full_present and l.startswith(("- [r96 bm-c]", "- [r99 bm-c]")))]
    assert not missing, f"rows lost from tree+archive: {missing[:3]}"

    rb = result.encode("utf-8")
    assert len(rb) <= 10240, f"over hard line: {len(rb)}"
    with open("CODELY.md", "wb") as f:
        f.write(rb)
    print(f"CODELY pass2 union: bmc-face + bm-b r340 row = {len(rb)}B (<=10240); zero-loss verified vs both archives")

if __name__ == "__main__":
    main()
