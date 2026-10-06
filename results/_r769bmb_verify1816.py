# _r769bmb_verify1816.py -- verify restored null|1816 row content == stash original (adopting session check)
import json, subprocess
P = "results/fund_value_p1/nulls.jsonl"
disk = [l for l in open(P, encoding="utf-8").read().splitlines() if '"null|1816"' in l]
st = subprocess.run(["git", "show", "stash@{0}:" + P], capture_output=True).stdout.decode("utf-8")
stash = [l for l in st.splitlines() if '"null|1816"' in l]
assert len(disk) == 1 and len(stash) == 1
print("disk_row:", disk[0][:180])
print("content_equal:", json.loads(disk[0]) == json.loads(stash[0]))
