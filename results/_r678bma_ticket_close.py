import json
P = r"fleet\tasks\T-2026-10-04-169-P1.json"
raw = open(P, "rb").read()
d = json.loads(raw.decode("utf-8"))
dumped = json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8")
print("roundtrip_same=", dumped == raw, len(raw), len(dumped))
if dumped != raw:
    # try with trailing newline
    dumped2 = (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    print("with_nl_same=", dumped2 == raw)
    if dumped2 != raw:
        raise SystemExit("ABORT roundtrip")
assert d["status"] == "claimed"
d["status"] = "done"
d["result_ref"] = ("results/theme_judge_p2/theme_judge_p2_results.json "
                   "(judged_negative theme-family FULL closure incl 0.75 "
                   "deep-break face E24-ii; burn 381s/26w budget-ok; prereg "
                   "sec.7/8 backfill + attrition row 8004/641985 + pool "
                   "entry+shard flip done_at 13:14:13 r668; r678)")
d["progress_r678"] = ("s3 complete: autofill-pool burn 13:07:52->13:14:13 "
                      "(381s/26 workers, BelowNormal, 600s budget ok); "
                      "finalize verdict judged_negative (g1 false x4, g2 "
                      "false x4, DSR 0 x4, M1 t=1.2652<3.0, PBO 0.3857); "
                      "pool double-flip same-window r668; prereg sec7/8 "
                      "backfilled (mirror-fidelity 4-way byte-identical "
                      "P2-frozen==P1-sens / P2-sens==P1-frozen)")
out = (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
open(P, "wb").write(out)
chk = json.loads(open(P, "rb").read().decode("utf-8"))
assert chk["status"] == "done" and chk["result_ref"].startswith("results/")
print("TICKET_DONE_OK")
