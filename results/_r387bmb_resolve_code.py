# r387 bm-b push-storm CODELY.md resolver (rebase replay vs bm-c r169 append):
# stage2 (rebase ours) = origin tip incl. bm-c r169 pitfall append
# stage3 (rebase theirs) = my 4c885d20 (reorg: r386 entry -> pointer + 2 new)
# final = base-prefix + pointer-53 + bm-c r169 entry + my 2 r387 entries,
# all verbatim, zero-loss byte-verified.
import subprocess, io, os

def blob(spec):
    b = subprocess.run(["git", "show", spec], capture_output=True).stdout
    return b.decode("utf-8")

base = blob(":1:CODELY.md")   # merge-base
ours = blob(":2:CODELY.md")   # origin side (bm-c r169 appended)
theirs = blob(":3:CODELY.md") # my replayed commit

bl, ol, tl = base.split("\n"), ours.split("\n"), theirs.split("\n")

# locate r386 entry + my pointer + new entries
r386_mark = "- [2026-09-28 14:2 r386 bm-b] 坑律：**judge-finalize"
ptr_mark = "冷层指针：坑律正典 2026-09-28 五十三批"
e1_mark = "- [2026-09-28 14:3 r387 bm-b] 坑律补章"
e2_mark = "- [2026-09-28 14:3 r387 bm-b] 坑律：**心跳/资源快照字段换算"
bmc_mark = "- [2026-09-28"  # generic; find bm-c r169 line in ours suffix

# origin side structure: base ... r386 entry ... [bm-c new lines]
oi = [i for i, ln in enumerate(ol) if ln.startswith(r386_mark)]
assert len(oi) == 1, oi
o_r386 = oi[0]
# bm-c suffix = lines after r386 entry (their appends)
o_suffix = [ln for ln in ol[o_r386 + 1:] if ln.strip()]
assert all(not ln.startswith(e1_mark) for ln in o_suffix), "unexpected overlap"
bmc_lines = o_suffix
print("origin suffix (bm-c appends):", len(bmc_lines), "line(s)")
for ln in bmc_lines:
    print("  >", ln[:100])

# my side structure: base ... pointer (replaced r386) ... my 2 new entries
ti = [i for i, ln in enumerate(tl) if ln.startswith(ptr_mark)]
assert len(ti) == 1, ti
t_ptr = ti[0]
m_suffix = [ln for ln in tl[t_ptr + 1:] if ln.strip()]
assert len(m_suffix) == 2, [ln[:60] for ln in m_suffix]
assert m_suffix[0].startswith(e1_mark) and m_suffix[1].startswith(e2_mark)
print("my suffix entries:", len(m_suffix))

# prefix identity: both sides identical up to r386-entry position
o_prefix = ol[:o_r386]
t_prefix = tl[:t_ptr]
assert o_prefix == t_prefix, "prefix mismatch -- manual review"
print("prefix identity OK:", len(o_prefix), "lines")

# final assembly: prefix + pointer + bm-c entries + my entries
ptr_line = tl[t_ptr]
final_lines = o_prefix + [ptr_line] + bmc_lines + m_suffix
final = "\n".join(final_lines)
if final.endswith("\n"):
    pass
else:
    final += "\n"

# zero-loss verbatim checks
assert final.count("\n".join(bmc_lines)) == 1 or all(
    final.count(ln) == 1 for ln in bmc_lines)
for ln in m_suffix:
    assert final.count(ln) == 1, "my entry lost/dup"
assert final.count(ptr_line) == 1
assert r386_mark not in final, "r386 full text must be archive-only"
# archive (my commit's other leg) still carries the verbatim entry
arch = io.open(r"research\memory-archive\202609.md", encoding="utf-8").read()
assert arch.count(r386_mark) >= 1, "archive leg missing r386 verbatim"

with io.open("CODELY.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(final)
print("resolved CODELY.md =", os.path.getsize("CODELY.md"), "B")
