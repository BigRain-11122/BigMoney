"""r493 bm-c final delivery amendment: record the 3-wave push-race window
closure (first two pushes rejected non-FF by in-flight bm-b r690 closeout /
bm-a r694 close; merges ed33aa069 + 68deb1c9e resolved 14+22 UU per-face)
and the push_verify DELIVERED proof (tip 68deb1c9e, ahead=0) into
state.verify / state.did / heartbeat.verdict. r645 programmatic write +
reparse self-proof. Zero console CJK."""
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")

DELIV = ("push-race 3-wave window closed: push#1 rejected non-FF (bm-b r690 "
         "closeout in flight) -> merge ed33aa069 14-UU resolve -> push#2 "
         "rejected non-FF (bm-a r694 close + autofill claim in flight) -> "
         "merge wave-2 68deb1c9e 22-UU resolve -> push#3 push_verify "
         "DELIVERED tip 68deb1c9e ahead=0 behind=0")

st = json.load(open(STATE, encoding="utf-8"))
st["verify"] = (st.get("verify", "") + "; r493 final: " + DELIV
                + " (receipts _r493bmc_merge_resolve.json + "
                "_r493bmc_merge_resolve2.json)")
st["did"] = (st.get("did", "") + "; (7) " + DELIV + ".")
with open(STATE, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
json.loads(open(STATE, encoding="utf-8").read())

hb = json.load(open(HB, encoding="utf-8"))
hb["verdict"] = (hb.get("verdict", "") + "; " + DELIV)
with open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
hb2 = json.loads(open(HB, encoding="utf-8").read())
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock T-sep"
print("AMEND_OK state+hb r493 delivery recorded; epoch_int="
      f"{hb2['heartbeat_epoch_utc']}")
