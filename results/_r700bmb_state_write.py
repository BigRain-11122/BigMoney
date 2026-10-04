# r700 bm-b: state.json + heartbeat write (json.dump + json.loads self-check per r645 law)
import json, time, os

NOW = "2026-10-04T23:36:00+08:00"
EPOCH = int(time.time())

# ---- state.json ----
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 700
st["note"] = ("r700: D-20261004-05 four-leg receipt closed on bm-b face (D-02 principal three-source "
              "self-attest: XML direct read 5 tasks = S4U x4 kept per r576 lineage + InteractiveToken x1, "
              "register scripts default-principal single-source headers in place, zero unilateral action, "
              "deviation in CEO re-adjudication lane; D-03 scripts-face selftest 11 legs PASS live-verify; "
              "D-05 pf selftest 9/9 PASS re-run evidence; D-06 rebound handling = CODELY.md main "
              "102,013->23,907B via batch-1: 87 dated pit entries verbatim -> 11 pit-* domain files, "
              "zero-loss assertions + receipt _r700bmb_d06_batch1_receipt.json). Group decisions.md "
              "regression observed (23:08 commit 06e9a1a wiped 10-03/10-04 batches, -16,964B vs 12:06 "
              "blob 4E5BE321; r639 family; MSG-2026-10-04-2330-bmb-ALL sent, watermark follows origin "
              "current state, obligations survive in round reports). S1 smoke 48/48; S6 33/33 rc0 "
              "(legs 25-28 golden-week honest skip); post_review x0; orders ack 154/0 unacked both scans.")
st["last_round_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_seen"] = NOW
st["last_decisions_sha"] = "937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1"
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_sha"] = "814D93C47857513A304C03C939917642E936E0E5"
st["decisions_regression_note"] = ("r700: origin decisions.md tip 937A373D is a -16,964B rollback vs 12:06 blob "
                                   "4E5BE321 (commit 06e9a1a 23:08 wiped D-20261003/10-04 batch rows); "
                                   "r639-family handling: consumed receipts live in round reports; active "
                                   "BigMoney obligations tracked in state.next; MSG-2026-10-04-2330-bmb-ALL")
st["round_no_label"] = "round 700 (bm-b)"
st["clock_read"] = NOW
st["next"] = ("(a) 10-05 morning: W3 judge finalize landing watch (bm-c seat, ETA ~10-05T02:00, verify chain "
              "_r487bmc_w3_judge_verify.py); (b) N2 SHARD-2 (mine) RAM-gated -> daemon auto-ignite when trio "
              "V closes ~10-06T17; (c) after screen 12/12 + bm-a finalize: N2-W15 sec.9.1 concretize freeze "
              "window <=10-08, judge pool burn <=10-12; (d) MF IC reference batch (next_pick) source-blocked "
              "on bm-a lane (30-min self-heal in flight); (e) D-06 domain-file rebalance (pit-* <=30KB flow "
              "sink leg) before 10-07 closeout window + decisions.md regression adjudication follow-up "
              "(await bm-a/GM ruling on MSG-2330); (f) 10-09 post-holiday data-chain check")
json.dump(st, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.loads(open("state.json", encoding="utf-8").read())
assert chk["round_no"] == 700, "round_no not 700"

# ---- heartbeat ----
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 700
hb["round_no_label"] = "round 700 (bm-b)"
hb["current_task"] = ("r700 closed: D-20261004-05 four-leg bm-b receipt (D-02 principal three-source "
                      "self-attest zero unilateral action + D-03 selftest 11 legs + D-05 9/9 + D-06 CODELY "
                      "rebound batch-1: main 102,013->23,907B, 87 pit entries verbatim -> domain files, "
                      "receipt _r700bmb_d06_batch1_receipt.json); decisions.md rollback MSG-2330 sent; "
                      "S6 33/33 rc0; trio NULLS V/Q/D burning to 10-06/07/08")
hb["verdict"] = ("healthy burning (trio NULLS three-family in flight RAM-held + N2 SHARD-2 RAM-gated ready; "
                 "py_low_with_work_cands = legal RAM-gated window per r691 cap law; D-06 main-file budget "
                 "met 23.9KB<=30KB)")
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
json.dump(hb, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk2 = json.loads(open("fleet/machines/bm-b.json", encoding="utf-8").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch not int"
print("state round_no=700; heartbeat epoch=", chk2["heartbeat_epoch_utc"], "clock=", chk2["clock_read"])
