"""R298 bm-a: T-85 ticket close -- all four slices discharged
(s1 NAV harvest done R283; s2/s3 fusion grid judged batch landed+harvested
R296-R298; s4 survivor face naturally empty 0/45 -> zero intake, zero
paper-account proposal, honest close). Byte face probed before write."""
import io, json, re

TP = "fleet/tasks/T-2026-09-26-85-P1.json"
raw = open(TP, "rb").read()
print("faces: bom=%s crlf=%d lf=%d tail_nl=%s" % (
    raw[:3] == b"\xef\xbb\xbf", raw.count(b"\r\n"), raw.count(b"\n"),
    raw.endswith(b"\n")))
crlf = raw.count(b"\r\n") == raw.count(b"\n") and raw.count(b"\n") > 0

t = json.load(io.open(TP, encoding="utf-8-sig"))
assert t["status"] == "claimed" and t["claimed_by"] == "bm-a"
t["status"] = "done"
t["progress_r298"] = (
    "s2/s3 CLOSED: FUSION_GRID_P1 judged batch full arc R99-chain compliant -- "
    "prereg frozen 7cf87f13 (R295) -> runner 95f4e95d selftest 22/22 + real-data "
    "gate (R296) -> first burn crash 05:50 (KeyError sharpe_full, zero judged "
    "products) -> fix 64023a42 + B7b contract leg selftest 23/23 (R297) -> "
    "relaunch 06:10:01 pid 18524 new sha 0cce3192 (fuse cleared) -> landed "
    "06:10:37 elapsed 28.8s workers 4 -> VERDICT NEGATIVE 0/45 G1'v2 (best "
    "EW__DEDUP 0.5301 vs own-null line 1.7825, mu_null 0.4209 sigma 0.2754 "
    "K2000; CI lower -0.3299) + 0/45 G2 (DSR 0.0, PBO 0.4857 observe) = "
    "config-family no-increment over random same-mask portfolios; member-alpha "
    "claim NOT falsified (sec.1 pre-embedded). Harvest same round R298: "
    "prereg s7/s8 single-finalization (5-prediction reconciliation: P1 MISS "
    "diversification arithmetic, P2 HIT, P3 magnitude-MISS premise face "
    "falsified by exact v3 regime ORANGE+RED 10% not 61%, P4 HIT, P5 clean) + "
    "gate_attrition entries row 55 (r248 law, PBO recompute zero-drift "
    "0.4857) + pool done-flip (r291 live-read assert) + post_review row "
    "T-85-FUSION-GRID-P1 registered+derived 29/29 YES. s4 SURVIVOR FACE: "
    "0/45 -> zero STRATEGY_LIBRARY intake, zero FUSION-* paper-account "
    "proposal, naturally closed (activation path moot); slot closed "
    "no-reopen law, new evidence = new prereg. Ticket DONE all four slices."
)
t["result_ref"] = (
    "results/fusion_grid_p1/p1_results.json (judged verdict 0/45) + "
    "research/FUSION_GRID_P1_PREREG.md s7/s8 + results/fusion_p1/navs.jsonl "
    "(s1 NAV face, FUSION-P1-NAV pool done) + results/gate_attrition.json "
    "entries row FUSION_GRID_P1 + results/post_review.jsonl "
    "T-85-FUSION-GRID-P1 29/29 YES"
)
t["done_at"] = "2026-09-27 06:1x"
txt = json.dumps(t, ensure_ascii=False, indent=1)
raw_out = txt.encode("utf-8")
if crlf:
    raw_out = raw_out.replace(b"\n", b"\r\n")
with io.open(TP, "wb") as fh:
    fh.write(raw_out)
chk = json.load(io.open(TP, encoding="utf-8-sig"))
assert chk["status"] == "done" and chk["result_ref"]
print("ticket T-85 -> done (result_ref set, face crlf=%s)" % crlf)
