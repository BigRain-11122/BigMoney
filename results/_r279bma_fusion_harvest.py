# R279 bm-a FUSION-P1-NAV harvest flip (r244 landed-marker law: products on chain -> flip entry+shard done)
# Products: results/fusion_p1/navs.jsonl (64 lines) + navs_summary.json (anchor_all_ok=true,
# evidence_cutoff 2026-09-22, 12 workers 5.0s) + anchor_report.json, landed 2026-09-26 23:52:59
# by dead-R278 direct fire (R41 <5min light-batch exemption), adopted 57a6d9fe.
# Claim race note: bm-a 23:50:03 first-claim + executor; bm-b 00:00:04 stale-read claim void
# (its own r280 pitfall family); entry+shard -> done moots the race for all watchdogs.
import json
import sys

PATH = "results/runnable_pool.json"

raw = open(PATH, "rb").read()
face = {"crlf": b"\r\n" in raw, "ends_nl": raw.endswith(b"\n")}
d = json.loads(raw.decode("utf-8-sig"))
e = [x for x in d["entries"] if x["id"] == "FUSION-P1-NAV"][0]
assert e["status"] == "ready", f"unexpected status {e['status']}"
e["status"] = "done"
for s in e.get("shards", []):
    s["status"] = "done"
e["harvest_note"] = ("landed 2026-09-26 23:52:59 bm-a (dead-R278 direct fire, R41 <5min exemption; "
                     "adopted 57a6d9fe): 64-line census all faces, anchor_all_ok=true, 12 workers 5.0s, "
                     "evidence_cutoff 2026-09-22 (per-member), overlay faces at RECORDED basis 09-24 "
                     "(zero-run amendment, anchor-to-source-of-truth r261); products "
                     "results/fusion_p1/{navs.jsonl,navs_summary.json,anchor_report.json}; "
                     "claim race: bm-a 23:50:03 first+executor, bm-b 00:00:04 stale-read void per S4")
body = json.dumps(d, ensure_ascii=False, indent=1)
if face["crlf"]:
    body = body.replace("\n", "\r\n")
if face["ends_nl"]:
    body += "\n"
open(PATH, "wb").write(body.encode("utf-8"))

d2 = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
e2 = [x for x in d2["entries"] if x["id"] == "FUSION-P1-NAV"][0]
assert e2["status"] == "done" and all(s["status"] == "done" for s in e2["shards"])
assert isinstance(e2["harvest_note"], str) and e2["harvest_note"]
print(f"harvest flip ok: FUSION-P1-NAV entry+shard done, face={face}, entries={len(d2['entries'])}")
sys.exit(0)
