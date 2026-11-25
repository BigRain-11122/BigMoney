import subprocess, json

key = "\u9001\u8fbe\u81ea\u8bc1_r2117"
state = subprocess.run(["git", "show", "origin/main:state-bm-c.json"], capture_output=True).stdout
rep = subprocess.run(["git", "show", "origin/main:logs/iteration-loop/round_reports-bm-c.md"],
                     capture_output=True).stdout
print("state bytes", len(state))
st = json.loads(state.decode("utf-8"))
print("origin state has delivery key:", key in st, "| round_no:", st.get("round_no"))
print("origin report has delivered row:", "r2117-delivered" in rep.decode("utf-8", "replace"))
print("origin report r2117 main row:", "| 2117 |" in rep.decode("utf-8", "replace"))
# and the local working copy must agree with origin on this key
local = json.loads(open("state-bm-c.json", encoding="utf-8").read())
print("local == origin on key:", local.get(key) == st.get(key))
