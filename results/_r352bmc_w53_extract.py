# r352 bm-c: extract W53 finalize exact values for prereg s7/s8 backfill + W55 s5 anchors.
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
fp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w53_results.json"
d = json.load(open(fp, encoding="utf-8"))
print("top_keys:", sorted(d.keys()))
npc = d.get("null_pool_cumulative") or {}
for k, v in npc.items():
    print("NPC|", k, "|", json.dumps(v, ensure_ascii=False))
fams = d.get("families") or {}
for k, v in fams.items():
    meta = {kk: vv for kk, vv in v.items() if kk != "runs"}
    print("FAM|", k, "|", json.dumps(meta, ensure_ascii=False))
sg = d.get("science_gates") or {}
led = sg.get("ledger") or {}
print("LEDGER|", json.dumps(led, ensure_ascii=False))
for k in ("k_lift", "skill_line", "skill_line_v2", "k_lift_face", "audit"):
    if k in d:
        print(k.upper(), "|", json.dumps(d[k], ensure_ascii=False)[:1200])
print("generated|", d.get("generated"), "| evidence_cutoff|", d.get("evidence_cutoff"))
