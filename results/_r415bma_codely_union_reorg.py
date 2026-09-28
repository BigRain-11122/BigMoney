# r415 bm-a: CODELY.md memory-union + mandatory same-window hot/cold reorg.
# Situation: prefix identity HOLDS both sides (verified). Union = base +
# origin-suffix (bm-c pit batch-85 + bm-b pit batch-86, stay HOT per pit-law
# canon) + mine-suffix (r415 execution record, pipeline-type entry).
# Union blob would be 7,966 + 1,634 + 562 = 10,162B > 10KB hard line
# (bm-b fixup explicitly flagged "next appender must reorg"), so the
# same-window reorg moves MY OWN pipeline-type line verbatim into
# research/memory-archive/202609.md -> hot ends at 9,600B (== origin blob).
# Zero-loss proof: my line verbatim in archive; origin lines verbatim in hot;
# byte math exact.
import subprocess

def blob(stage):
    p = subprocess.run(["git", "show", f":{stage}:CODELY.md"], capture_output=True)
    assert p.returncode == 0
    return p.stdout

base, orig, mine = blob(1), blob(2), blob(3)
lb = base.split(b"\n")
lo = orig.split(b"\n")
lm = mine.split(b"\n")
assert lo[: len(lb) - 1] == lb[:-1], "origin prefix identity broken"
assert lm[: len(lb) - 1] == lb[:-1], "mine prefix identity broken"
origin_suffix = lo[len(lb) - 1 : -1]      # 2 pit-law lines (stay hot)
mine_suffix = lm[len(lb) - 1 : -1]         # 1 execution record (pipeline-type)
assert len(origin_suffix) == 2 and len(mine_suffix) == 1
assert all(l.startswith(b"- [2026-09-29") for l in origin_suffix + mine_suffix)

# hot = base + origin suffix (pit laws stay hot); my line leaves for archive
hot = base + b"\n".join(origin_suffix) + b"\n"
assert len(hot) == len(orig), (len(hot), len(orig))
assert len(hot) <= 10000, "hot still over 10KB after reorg"

# archive append: mirror on-disk CRLF convention of the archive file
arch_p = "research/memory-archive/202609.md"
arch_work = open(arch_p, "rb").read()
arch_blob_size = int(subprocess.run(
    ["git", "cat-file", "-s", "HEAD:research/memory-archive/202609.md"],
    capture_output=True).stdout.strip())
crlf_preserved = arch_blob_size == len(arch_work)
assert arch_work.endswith(b"\r\n")
line_lf = mine_suffix[0]
line = line_lf.replace(b"\n", b"\r\n") if crlf_preserved else line_lf + b"\n"
assert line not in arch_work, "line already archived (idempotency guard)"

open("CODELY.md", "wb").write(hot)
open(arch_p, "wb").write(arch_work + line)

# verify
v_hot = open("CODELY.md", "rb").read()
v_arch = open(arch_p, "rb").read()
assert v_hot == orig, "hot must equal origin blob byte-for-byte"
assert mine_suffix[0] in v_arch, "archived line lost"
assert v_arch[: len(arch_work)] == arch_work, "archive prefix mutated"
print("CODELY union+reorg OK:")
print("  hot blob", len(hot), "B (== origin, <=10KB); archive +", len(line), "B",
      "(crlf_preserved=%s)" % crlf_preserved)
