import subprocess, json
def blob(rev, path):
    r = subprocess.run(["git","show",f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8","replace") if r.returncode==0 else None
for f in ["results/compute_audit.json","results/regime_state.json"]:
    o = blob(":2", f); t = blob(":3", f)
    jo, jt = json.loads(o), json.loads(t)
    print("==", f)
    if "latest" in jo: 
        print("  ours latest ts:", jo["latest"].get("ts", jo["latest"].get("time","?")), "| entries:", len(jo.get("history",[])))
        print("  origin latest ts:", jt["latest"].get("ts", jt["latest"].get("time","?")), "| entries:", len(jt.get("history",[])))
    else:
        print("  ours keys:", {k: str(v)[:60] for k,v in list(jo.items())[:6]})
        print("  origin keys:", {k: str(v)[:60] for k,v in list(jt.items())[:6]})
f = "results/post_review.jsonl"
o = blob(":2", f); t = blob(":3", f); b = blob(":1", f)
ol, tl, bl = set(o.splitlines()), set(t.splitlines()), set(b.splitlines())
print("== post_review.jsonl: base", len(bl), "ours", len(ol), "origin", len(tl))
print("  ours-only:", len(ol-bl), "origin-only:", len(tl-bl), "both-added-identical:", len((ol-bl)&(tl-bl)))
# peek ours-only ids
import re
for l in list(ol-bl)[:4]:
    m = re.search(r'"id":\s*"([^"]+)"', l)
    print("   ours-only id:", m.group(1) if m else l[:80])
for l in list(tl-bl)[:4]:
    m = re.search(r'"id":\s*"([^"]+)"', l)
    print("   origin-only id:", m.group(1) if m else l[:80])
