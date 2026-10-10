import json, io, os, glob
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
def hb(mid):
    try:
        j = json.load(io.open(os.path.join(ROOT,"fleet","machines",mid+".json"), encoding="utf-8-sig"))
        return {"current_task": str(j.get("current_task",""))[:200], "did": str(j.get("did",""))[:150]}
    except Exception as e:
        return {"err": str(e)[:80]}
print("bm-a:", json.dumps(hb("bm-a"), ensure_ascii=False))
print("bm-b:", json.dumps(hb("bm-b"), ensure_ascii=False))
# locate O-1725 inputs
cands = ["results/regime5_labels/REGIME5-2026-09-30.json",
         "results/corebook_closeout_p1.json",
         "results/regime_thermo",
         "research/COREBOOK_CLOSEOUT_P1.md"]
for c in cands:
    p = os.path.join(ROOT, c)
    print(c, "->", os.path.exists(p))
print("--- search corebook/oversold/theme streams ---")
for pat in ["*corebook*", "*oversold*", "*theme*", "*lowvol*defensive*", "*defensive*"]:
    hits = glob.glob(ROOT+"/results/**/"+pat+".json", recursive=True)[:4] + glob.glob(ROOT+"/research/**/"+pat+"*", recursive=True)[:3]
    for h in hits[:5]:
        print("  ", h.replace(ROOT,""), os.path.getsize(h) if os.path.isfile(h) else "<dir>")
