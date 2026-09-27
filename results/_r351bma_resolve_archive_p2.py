"""R351 pass-2 archive union resolver (bmc 27th batch kept + our 27th renumbered to 28th, r176).

Rebase stage semantics: :1: = original parent (old archive), :2: = HEAD (bmc r101 face,
their 27th-batch section), :3: = replayed commit (our fold face, OUR 27th-batch section).
r176 yield: bmc landed first (20:14:50) -> OUR section renumbers to 二十八批.
Union = base + bmc suffix + our renumbered suffix; zero-loss = every line of both suffixes present.
"""
import subprocess

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout

def main():
    base = blob(":1", "research/memory-archive/202609.md")
    oB = blob(":2", "research/memory-archive/202609.md")   # bmc face
    tB = blob(":3", "research/memory-archive/202609.md")   # fold face (our section)
    assert oB.startswith(base), "bmc face not superset of base"
    assert tB.startswith(base), "fold face not superset of base"
    bmc_suffix = oB[len(base):]
    our_suffix = tB[len(base):]
    our_renum = our_suffix.replace("二十七批".encode("utf-8"), "二十八批".encode("utf-8"))
    result = base + bmc_suffix + our_renum

    rtxt = result.decode("utf-8", errors="replace")
    rtxt_rev = rtxt.replace("二十八批", "二十七批")  # renumber-aware zero-loss: check pre-renumber form too
    for tag, sfx in (("bmc", bmc_suffix), ("ours", our_suffix)):
        for l in sfx.decode("utf-8", errors="replace").splitlines():
            if l.strip() and l not in rtxt and l not in rtxt_rev:
                raise SystemExit(f"zero-loss violation ({tag}): {l[:80]!r}")

    with open("research/memory-archive/202609.md", "wb") as f:
        f.write(result)
    print(f"archive pass2 union: base={len(base)} + bmc={len(bmc_suffix)} + ours-renum28={len(our_renum)} = {len(result)}B; zero-loss verified")

if __name__ == "__main__":
    main()
