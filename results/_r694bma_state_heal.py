"""r694 bm-a: state round_no double-increment heal (first run wrote 693->694
then crashed at heartbeat step; fixed rerun re-incremented 694->695). Round
number is ABSOLUTE (r694) not delta -- set back to 694, reparse proof."""
import json

SP = "state-bm-a.json"
with open(SP, encoding="utf-8-sig") as fh:
    st = json.load(fh)
assert st["round_no"] == "695", st["round_no"]
st["round_no"] = "694"
with open(SP, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
st2 = json.loads(open(SP, encoding="utf-8-sig").read())
assert st2["round_no"] == "694", st2["round_no"]
assert st2["last_round"] == "r694" and st2["round"] == "r694"
print("state heal OK: round_no 695->694 (absolute), reparse proof pass")
