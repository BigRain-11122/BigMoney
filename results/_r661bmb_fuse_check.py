# Check crash fuse state: is any refusal loop actively growing?
import json, time

f = json.load(open("results/crash_fuse.json", encoding="utf-8"))
print("keys:", list(f.keys())[:10])
# structure-adaptive: look for refusals / entries
def show(obj, depth=0):
    if depth > 2: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("refusals", "fuse_refusals", "refusal_count", "count", "sig"):
                print(" ", k, "=", str(v)[:100])
            elif isinstance(v, (dict, list)) and k not in ("history",):
                print(" ", k, ":", type(v).__name__, (str(v)[:120] if not isinstance(v,(dict,list)) else ""))
                show(v, depth+1)
show(f)
# entries with refusal counts
if isinstance(f, dict):
    ents = f.get("entries", {})
    if isinstance(ents, dict):
        for k, v in list(ents.items())[:20]:
            if isinstance(v, dict):
                print("ENTRY:", k, "| refusals=", v.get("refusals", v.get("fuse_refusals")), "| last=", str(v.get("last_refusal", v.get("ts", "")))[:25])
