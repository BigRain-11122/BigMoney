"""r495 bm-c close: state final-face touch (push-race closure facts into
did/verify/last_round). RR close row appended separately via PS (marker
gate). Laws: r645 programmatic write + reparse / r694 absolute values."""
import json
import os
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
NOW = datetime.datetime.now().astimezone()
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

st = json.load(open(STATE, encoding="utf-8"))
assert st["round_no"] == 495, f"unexpected round_no {st['round_no']}"
st["did"] = (st["did"] +
             "; (7) S7-close: merge commit 06f42125a (31 UU S6 shared-regen faces "
             "resolved per-face ts newer-wins all-ours 20:27-31 vs 20:20-22 + "
             "md/js twins locked + token per-key union side_pick>0 + x2 line-union "
             "keep-first, receipt _r495bmc_merge_resolve.json; bespoke ts key "
             "generated_from_state_updated on paper_export faces = new face this "
             "window) + push_verify DELIVERED tip 06f42125a ahead=0/behind=0 "
             "first-try clean.")
st["verify"] = (st["verify"] +
                " + close: push_verify DELIVERED tip 06f42125a + RR close row "
                "marker==1 + resolver receipt 31-face table.")
st["last_round"] = (st["last_round"] +
                    " + S7-close DELIVERED tip 06f42125a (round commit 7887847bd -> "
                    "merge 31-UU resolve -> push first-try clean).")
st["updated"] = CLOCK
st["updated_at"] = CLOCK
st["last_ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
json.loads(open(STATE, encoding="utf-8").read())
print("STATE_CLOSE_OK", CLOCK)
