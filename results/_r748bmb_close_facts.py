# r748 bm-b close-facts line: measured delivery facts only (r532 law: no pre-written tails).
# Appended AFTER push self-verification; left for r749 churn-absorb per r746 lineage convention.
import json, io, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
hhmm = now.strftime("%H:%M")

tri = json.load(io.open(ROOT + r"\results\finalize_trio_readiness.json", encoding="utf-8"))
fam = tri["families"]
v = fam["fund_value_p1"]["have"]; q = fam["fund_quality_p1"]["have"]; d = fam["fund_divlowvol_p1"]["have"]

line = (
    "%s | round 748 close-facts (bm-b) | local undelivered-to-origin commit count: 0 "
    "(post-push fetch+rev-list 0/0 self-verified at %s) | delivery: r748 round commits "
    "ac5d99880 (r747 dead-tail churn-absorb) + 3c3a170e8 (merge w1 14-UU canon resolver) + "
    "745556b06 (S6 35-leg products + chain bloodline, bookkeeping deferred by S6 log flush delay) + "
    "8b4b9d98e (merge w2 17-UU round-2 resolver, receipt w1+w2 preserved) + 81e654fa2 "
    "(bookkeeping: state honest jump 746->748 + heartbeat + r747 POST-MORTEM backfill line + r748 line) "
    "-> push non-FF behind-7 window-2 -> LANDED 5bb6f0030..81e654fa2 | trio V%d/Q%d/D%d of 2000 "
    "(+24/+21/+19 vs r746 probe) | product score 2 (S6 chain 35 legs all rc0 + trio burn advance + "
    "CEO faces regen ours-fresher through window-2 + r747 dead-tail recovery)\n" % (iso, hhmm, v, q, d)
)
marker = b"round 748 close-facts"
raw = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert marker not in raw, "close-facts line already present"
assert raw.endswith(b"\n") or raw.endswith(b"\r\n")
with io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "ab") as f:
    f.write(line.encode("utf-8"))
raw2 = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert raw2 == raw + line.encode("utf-8") and raw2.count(marker) == 1
print("close-facts appended: %s | trio V%d/Q%d/D%d" % (iso, v, q, d))
