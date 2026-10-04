"""r690 bm-b merge resolver: single UU results/crash_fuse.json.
Pre-merge analysis (results/_r690bmb_fuse_cmp.py + git diff origin/main):
local absorbed version == origin version EXCEPT one shard entry
sigs["scripts/contest_ytd_legs.py|revcensus"] where ours (bm-b, last_refusal_ts
19:32:14, refusals=36) is NEWER than origin (bm-a, 19:27:04, refusals=8).
r474 per-face newer-wins -> take ours wholesale for this face (== origin content
+ single ours-newer shard row = per-face max-merge result).
Canon: git show HEAD:/MERGE_HEAD: raw bytes via subprocess (r657-2, r660 no PS pipe).
Gates: reparse JSON + all-keys-except-shard equality assert + marker scan.
Receipt -> results/_r690bmb_merge_resolve.json"""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = "results/crash_fuse.json"
SHARD = "scripts/contest_ytd_legs.py|revcensus"


def git_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                        capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={r.returncode} "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                      cwd=ROOT, capture_output=True).returncode == 0, "MERGE_HEAD absent"

ours_b = git_bytes("HEAD", PATH)
theirs_b = git_bytes("MERGE_HEAD", PATH)
ours = json.loads(ours_b.decode("utf-8"))
theirs = json.loads(theirs_b.decode("utf-8"))

# structural equality everywhere except the single contested shard
assert set(ours.keys()) == set(theirs.keys()), ("top keys differ", sorted(ours.keys()), sorted(theirs.keys()))
diff_keys = []
for top in ours.keys():
    o, t = ours[top], theirs[top]
    if isinstance(o, dict) and isinstance(t, dict):
        assert set(o.keys()) == set(t.keys()), (top, "sub keys differ")
        for k in o:
            if o[k] != t[k]:
                diff_keys.append(f"{top}/{k}")
    elif o != t:
        diff_keys.append(top)
assert diff_keys == [f"sigs/{SHARD}"], ("unexpected delta set", diff_keys)

# newer-wins on the contested shard: last_refusal_ts compare (ts_norm per r461)
o_sh = ours["sigs"][SHARD]
t_sh = theirs["sigs"][SHARD]
o_ts = str(o_sh.get("last_refusal_ts", "")).replace("T", " ")[:19]
t_ts = str(t_sh.get("last_refusal_ts", "")).replace("T", " ")[:19]
assert o_ts > t_ts, ("ours not newer", o_ts, t_ts)

# write ours (== per-face max-merge: origin content + ours-newer shard)
open(os.path.join(ROOT, PATH), "wb").write(ours_b)

# reparse gate + marker scan
data = open(os.path.join(ROOT, PATH), "rb").read()
json.loads(data.decode("utf-8"))
assert b"<<<<<<<" not in data and b">>>>>>>" not in data, "markers present"

receipt = {
    "resolver": "r690 bm-b merge (single UU crash_fuse.json)",
    "face": PATH,
    "decision": "ours (per-face newer-wins r474)",
    "contested_shard": SHARD,
    "ours": {"machine": o_sh.get("machine"), "last_refusal_ts": o_ts, "refusals": o_sh.get("refusals")},
    "theirs": {"machine": t_sh.get("machine"), "last_refusal_ts": t_ts, "refusals": t_sh.get("refusals")},
    "delta_scope_proof": diff_keys,
    "verification": "reparse OK + markers clean + all-other-keys byte-equal assert",
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
}
open(os.path.join(ROOT, "results", "_r690bmb_merge_resolve.json"), "wb").write(
    (json.dumps(receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
print(json.dumps(receipt, ensure_ascii=False))
