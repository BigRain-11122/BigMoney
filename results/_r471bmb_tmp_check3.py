import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
att = json.load(open(r"results/gate_attrition.json", encoding="utf-8"))
ents, hist = att["entries"], att["history"]
print("entries len:", len(ents), "| history len:", len(hist))
print("entries batches tail 8:", [e.get("batch") for e in ents[-8:]])
w13j_e = [i for i, e in enumerate(ents) if "W13" in str(e.get("batch", ""))]
w13j_h = [i for i, e in enumerate(hist) if "W13" in str(e.get("batch", ""))]
print("entries idx with W13:", w13j_e)
print("history idx with W13:", w13j_h)
# W13 screen p50/p95 + sumn segmented survival from w13_screen.json
s13 = json.load(open(r"results/trial_labor_w13/w13_screen.json", encoding="utf-8"))
nf = s13["null_family"]
print("null_family keys:", list(nf.keys()))
for k in ("p50", "p95", "n", "seed"):
    if k in nf:
        print("  null", k, "=", nf[k])
print("screen top keys:", list(s13.keys()))
# look for segmented / axis faces
def find_seg(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if "segment" in str(k) or "axis" in str(k) or "sumn" in str(k):
                print("SEG", p + "/" + k, ":", json.dumps(v, ensure_ascii=False)[:400])
            find_seg(v, p + "/" + str(k))
find_seg(s13)
