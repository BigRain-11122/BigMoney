"""r298 bm-b final resolver #5: autostash-pop worktree conflict on
results/autofill_state.json (mixed-dict+ledger, r203/R208/r215/r220/r245).
Stash 3ffb5b61 holds the local watchdog face (last_tick 04:50:01
claim_lost_yield + bm-b tick ledger rows). HEAD (d50395ee == 0dc12a4f face)
holds bm-a r294's committed autofill state (their 05:00:0x tick face).
Union both: launches = |A union B| canonical-dedup -> ts desc cap 50 ->
re-sort ts asc for write-back; last_tick = internal-ts compare take-newer
(same-second tie -> HEAD, r140), dict-assert; newline+indent byte-mirror
from HEAD blob. Then clear index conflict stages and return the file to the
lane-owned unstaged state (autofill watchdog self-commit law r290).
"""
import io
import json
import subprocess


def cano(r):
    return json.dumps(r, ensure_ascii=False, sort_keys=True)


stash_sha = subprocess.run(["git", "rev-parse", "stash@{0}"],
                           capture_output=True, text=True, check=True).stdout.strip()
head_raw = subprocess.run(["git", "show", "HEAD:results/autofill_state.json"],
                          capture_output=True, check=True).stdout
snap_raw = subprocess.run(["git", "show", stash_sha + ":results/autofill_state.json"],
                          capture_output=True, check=True).stdout
head = json.loads(head_raw.decode("utf-8-sig"))
snap = json.loads(snap_raw.decode("utf-8-sig"))

lh, ls = head.get("launches") or [], snap.get("launches") or []
union = {cano(r): r for r in lh}
union.update({cano(r): r for r in ls})
rows = list(union.values())
n_union = len(rows)
rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
rows = rows[:50]
rows.sort(key=lambda r: r.get("ts", ""))

th = (head.get("last_tick") or {}).get("ts", "")
tsn = (snap.get("last_tick") or {}).get("ts", "")
last_tick = snap.get("last_tick") if tsn > th else head.get("last_tick")  # r140 tie->HEAD
assert isinstance(last_tick, dict)

crlf = b"\r\n" in head_raw[:2000]
text = json.dumps({"last_tick": last_tick, "launches": rows},
                  ensure_ascii=False, indent=1) + "\n"
data = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
with io.open("results/autofill_state.json", "wb") as f:
    f.write(data)

chk = json.load(io.open("results/autofill_state.json", encoding="utf-8-sig"))
assert isinstance(chk["last_tick"], dict) and len(chk["launches"]) == len(rows)
assert cano(chk["last_tick"]) == cano(last_tick)
print("autofill pop-conflict union: head %d + snap %d -> |union| %d -> cap50 %d; "
      "last_tick ts=%s (head %s / snap %s); crlf=%s"
      % (len(lh), len(ls), n_union, len(rows), last_tick.get("ts"), th, tsn, crlf))
print("stash sha:", stash_sha)
