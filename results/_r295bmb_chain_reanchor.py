"""r295 bm-b 5x chain re-anchor: CN-TREND phantom append + CENSUS 3x same-batch append.

Facts (all real-read this round):
- attrition continuity: CN_SOE 02:06:20 =191,864 -> CENSUS row declares +4,518 but
  records ledger_total_after=205,418 (jump +13,554 = exactly 3x4,518);
  surviving census w1_results.json carries prev=200,900 (=191,864 + 2x4,518)
  i.e. the census batch was appended THREE times (re-run re-finalize family,
  same file overwritten); true single-count head after census = 196,382.
- CN_TREND phantom: losing-side burn (local pid 10544, not killed after the r288
  claim-race adjudication) re-finalized 03:42:52 -> +2,007 twice-counted
  (canonical bm-a 03:27:59 row kept; phantom attrition row removed separately).

Correction per R252 chain-head re-anchor precedent (move the anchor, leave 4dp
science values untouched, no re-run, no verdict change):
  census  w1_results.json: prev_total 200900->191864, total 205418->196382
  cn_trend p1_results.json: prev_total 205418->196382, total 207425->198389
  gate_attrition census row: ledger_total_after 205418->196382
  gate_attrition cn_trend row: ledger_total_after 207425->198389
  post_review_criteria json_field anchors: 205418->196382, 200900->191864,
  207425->198389 (r290 criteria-fix legal sequence; claims stay as history).

Every edit: byte-surgical text replacement with uniqueness assertion, then
full-file json.loads validation.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def surgical(path, pairs):
    raw_bytes = open(path, "rb").read()
    bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    raw = raw_bytes.decode("utf-8-sig" if bom else "utf-8")
    for old, new in pairs:
        n = raw.count(old)
        assert n == 1, "expected exactly 1 occurrence of %r in %s, found %d" % (old, path, n)
        raw = raw.replace(old, new)
    json.loads(raw)  # full-file validation
    out = raw.encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    with open(path, "wb") as fh:
        fh.write(out)
    print("OK %s: %s" % (os.path.relpath(path, ROOT), ", ".join(
        "%s->%s" % (o.replace('"', ""), nw.replace('"', "")) for o, nw in pairs)))


surgical(os.path.join(ROOT, "results", "census_fusion_s2", "w1_results.json"), [
    ('"prev_total": 200900', '"prev_total": 191864'),
    ('"total": 205418', '"total": 196382'),
])
surgical(os.path.join(ROOT, "results", "cn_trend_ETF", "p1_results.json"), [
    ('"prev_total": 205418', '"prev_total": 196382'),
    ('"total": 207425', '"total": 198389'),
])
surgical(os.path.join(ROOT, "results", "gate_attrition.json"), [
    ('"ledger_total_after": 205418', '"ledger_total_after": 196382'),
    ('"ledger_total_after": 207425', '"ledger_total_after": 198389'),
])
surgical(os.path.join(ROOT, "results", "post_review_criteria.json"), [
    ('"205418"', '"196382"'),
    ('"200900"', '"191864"'),
    ('"207425"', '"198389"'),
])

# post-fix chain verification
head = None
for path in (os.path.join(ROOT, "results", "cn_trend_ETF", "p1_results.json"),):
    d = json.load(open(path, encoding="utf-8-sig"))
    led = d["trials_ledger"]
    assert led["prev_total"] == 196382 and led["total"] == 198389
    assert led["prev_total"] + led["batch_trials"] == led["total"], "cn_trend balance"
    head = led["total"]
d = json.load(open(os.path.join(ROOT, "results", "census_fusion_s2", "w1_results.json"),
                   encoding="utf-8-sig"))
led = d["trials_ledger"]
assert led["prev_total"] == 191864 and led["total"] == 196382
assert led["prev_total"] + led["batch_trials"] == led["total"], "census balance"
print("REANCHORED HEAD=%d (chain: ...191864 CN_SOE -> +4518=196382 CENSUS -> +2007=198389 CN_TREND)" % head)
