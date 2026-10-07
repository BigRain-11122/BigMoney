# -*- coding: utf-8 -*-
"""r680 bm-c: HANDOVER swallow-heal verification - compare r675 entry line
(current worktree L3) against git HEAD version byte-for-byte, and check
r680 entry completeness. Facts to stdout, ascii-safe prints."""
import subprocess

def git_show(path):
    r = subprocess.run(["git", "show", "HEAD:%s" % path], capture_output=True)
    return r.stdout.decode("utf-8")

head = git_show("research/HANDOVER.md")
cur = open("research/HANDOVER.md", encoding="utf-8").read()

head_lines = head.split("\n")
cur_lines = cur.split("\n")
print("head_lines=%d cur_lines=%d" % (len(head_lines), len(cur_lines)))

# r675 line in HEAD: starts with the known prefix
prefix = "> bm-c round 675"
head_675 = [l for l in head_lines if l.startswith(prefix)]
cur_675 = [l for l in cur_lines if l.startswith(prefix)]
print("head_675_count=%d cur_675_count=%d" % (len(head_675), len(cur_675)))
if head_675 and cur_675:
    same = head_675[0] == cur_675[0]
    print("r675_line_identical=%s" % same)
    if not same:
        # compare tails since cur was reconstructed with header
        print("head_675_len=%d cur_675_len=%d" % (len(head_675[0]), len(cur_675[0])))
        # find first diff
        for i, (a, b) in enumerate(zip(head_675[0], cur_675[0])):
            if a != b:
                print("first_diff_at=%d head=%r cur=%r" % (i, head_675[0][i-20:i+20], cur_675[0][i-20:i+20]))
                break
        if len(head_675[0]) != len(cur_675[0]):
            longer, shorter = (head_675[0], cur_675[0]) if len(head_675[0]) > len(cur_675[0]) else (cur_675[0], head_675[0])
            print("extra_tail_of_longer=%r" % longer[len(shorter):][:120])

# r680 entry present and complete (starts with prefix, ends with r685 pointer)
cur_680 = [l for l in cur_lines if l.startswith("> bm-c round 680")]
print("cur_680_count=%d" % len(cur_680))
if cur_680:
    print("r680_tail=%r" % cur_680[0][-60:])
# header intact
print("header_ok=%s" % cur_lines[0].startswith("# Bigmoney"))
# all HEAD lines still present in current (no other swallow)
missing = [i for i, l in enumerate(head_lines) if l and l not in cur_lines]
print("head_lines_missing_in_cur=%s" % (missing[:5] if missing else "none"))
