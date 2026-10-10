# r828 bm-b: resolve rebase conflicts (cfcc318b2 replay onto d625b2157)
# Forms: tech.md = adjacent-row union (HEAD T19 done + mine T20 open);
#        queue_head_collision_probe.json = snapshot take-HEAD (bm-a side =
#        operative fleet evidence: bm-a probe saw bm-b in-flight on E8 and
#        yielded -- the outcome face; mine CLEAR is superseded, E8 now done).
# Laws: r185 (validate before writeback), r140 (tie->HEAD), R208 (snapshot
# take-new/take-landed), fleet README s4 (commit-order, bm-a landed first).
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---- 1. tech.md: reconstruct union row block -------------------------------
p = r"state\queue\tech.md"
t = open(p, "rb").read().decode("utf-8")
lines = t.split("\n")
i_start = next(i for i, l in enumerate(lines) if l.startswith("<<<<<<<"))
assert lines[i_start + 2].startswith("======="), "unexpected conflict shape"
i_mid = i_start + 2
i_end = next(i for i in range(i_mid + 1, len(lines)) if lines[i].startswith(">>>>>>>"))
head_block = lines[i_start + 1:i_mid]
mine_block = lines[i_mid + 1:i_end]
assert len(head_block) == 1 and head_block[0].startswith("| T19 ") and head_block[0].endswith("| done |"), head_block
assert len(mine_block) == 2 and mine_block[0].startswith("| T19 ") and mine_block[0].endswith("| open |") \
    and mine_block[1].startswith("| T20 "), mine_block
# union: HEAD's T19 (done, bm-a r950 delivery flip) + mine T20 (open)
merged = [head_block[0], mine_block[1]]
# zero-loss assertions: T19 HEAD row == T19 mine row except status token
h, m = head_block[0], mine_block[0]
assert h[: h.rfind("| open |")] == m[: m.rfind("| open |")] or h.replace("| done |", "| open |") == m, \
    "T19 rows differ beyond status"
new_lines = lines[:i_start] + merged + lines[i_end + 1:]
new = "\n".join(new_lines)
open(p, "wb").write(new.encode("utf-8"))
print("tech.md: T19(done,HEAD)+T20(open,mine) union OK,",
      len(lines), "->", len(new_lines), "lines")

# ---- 2. probe json: take HEAD side ------------------------------------------
p2 = r"results\queue_head_collision_probe.json"
t2 = open(p2, "rb").read().decode("utf-8")
lines2 = t2.split("\n")
# two conflict hunks: (machine_id) and (queues tail + verdict). Take HEAD side
# for both; validate final JSON parses and carries bm-a COLLISION_RISK face.
out = []
side = None  # None=keep, 'HEAD'=keep, 'MINE'=drop
for l in lines2:
    if l.startswith("<<<<<<<"):
        side = "HEAD"
        continue
    if l.startswith("======="):
        side = "MINE"
        continue
    if l.startswith(">>>>>>>"):
        side = None
        continue
    if side in (None, "HEAD"):
        out.append(l)
new2 = "\n".join(out)
d = json.loads(new2)  # r185: parse-validate before writeback
assert d["machine_id"] == "bm-a" and d["verdict"] == "COLLISION_RISK", d["verdict"]
assert d["queues"][0]["queue"].endswith("tech.md") and d["queues"][1]["queue"].endswith("explore.md")
open(p2, "wb").write(new2.encode("utf-8"))
print("probe json: take-HEAD (bm-a COLLISION_RISK face), machine_id=%s verdict=%s"
      % (d["machine_id"], d["verdict"]))
print("RESOLVED both files")
