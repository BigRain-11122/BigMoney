# r670 bm-a S7: state round_no increment + heartbeat update (programmatic write + self-check laws)
import json, time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))

# --- state-bm-a.json: round_no 669 -> 670, strict json.dump + loads self-check
P = "state-bm-a.json"
st = json.load(open(P, encoding="utf-8"))
st["round_no"] = int(st.get("round_no", 669)) + 1
tmp = P + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
import os
os.replace(tmp, P)
chk = json.load(open(P, encoding="utf-8"))
assert chk["round_no"] == 670, chk["round_no"]
print("state round_no=670 landed, strict parse self-check PASS")

# --- heartbeat fleet/machines/bm-a.json (own file only)
H = "fleet/machines/bm-a.json"
hb = json.load(open(H, encoding="utf-8"))
hb["last_seen"] = datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["current_task"] = ("T-167 s3 THEME-JUDGE-P1 burn crash-healed+relit "
                      "(r670 fix: ci k-start semantics + checkpoint scanner; "
                      "fuse auto-clear 10:16; C8 launch pid=12372 10:19; finalize "
                      "on burn_state landing = next round first move)")
hb["verdict"] = "green: THEME-JUDGE-P1 reburn in flight after r670 crash-fix; S6 39/39 rc0"
hb["heartbeat_epoch_utc"] = int(time.time())          # int law (R170/R178)
hb["clock_read"] = datetime.now(CST).isoformat(timespec="seconds")  # T-sep law (R262)
tmp = H + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
os.replace(tmp, H)
chk2 = json.load(open(H, encoding="utf-8"))
e = chk2.get("heartbeat_epoch_utc")
assert isinstance(e, int) and not isinstance(e, bool), f"epoch type={type(e)}"
assert "T" in chk2["clock_read"] and "+" in chk2["clock_read"], chk2["clock_read"]
print(f"heartbeat landed: epoch={e} (int PASS) clock={chk2['clock_read']} (T-sep PASS)")
