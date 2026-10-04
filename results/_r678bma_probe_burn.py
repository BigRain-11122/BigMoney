import json, os, re
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
R = os.path.join(B, "results")
out = []
pool = json.load(open(os.path.join(R, "runnable_pool.json"), encoding="utf-8"))
for e in pool.get("entries", []):
    eid = str(e.get("id", ""))
    if "THEME" in eid.upper() or "TJ2" in eid.upper():
        out.append("entry=%s" % json.dumps({k: e.get(k) for k in ("id", "status", "worker_class", "shards") if k in e}, ensure_ascii=False)[:600])
# attrition ledger THEME-JUDGE-P2 entries
att = json.load(open(os.path.join(R, "gate_attrition.json"), encoding="utf-8"))
s = json.dumps(att, ensure_ascii=False)
n = s.count("THEME-JUDGE-P2")
out.append("gate_attrition_THEME_JUDGE_P2_mentions=%d" % n)
if isinstance(att, dict):
    out.append("gate_attrition_top_keys=" + ",".join(list(att.keys())[:20]))
    # find entries list
    for k, v in att.items():
        if isinstance(v, list):
            tjs = [x for x in v if isinstance(x, dict) and "THEME-JUDGE-P2" in json.dumps(x)]
            for x in tjs[:3]:
                out.append("attr_entry=%s" % json.dumps(x, ensure_ascii=False)[:400])
# crash fuse
cf = json.load(open(os.path.join(R, "crash_fuse.json"), encoding="utf-8"))
s2 = json.dumps(cf, ensure_ascii=False)
out.append("crash_fuse_TJ2_mentions=%d" % s2.count("THEME-JUDGE"))
# prereg s7/s8 state
p = os.path.join(B, "research", "THEME_JUDGE_P2.md")
if os.path.exists(p):
    txt = open(p, encoding="utf-8").read()
    out.append("prereg_len=%d" % len(txt))
    for sec in ("## s7", "## S7", "§7", "s7.", "## 7"):
        if sec in txt:
            out.append("prereg_has_%s" % sec)
    tail = txt[-1500:]
    out.append("prereg_tail=" + tail.replace("\n", " | ")[:1200])
open(os.path.join(R, "_r678bma_probe_burn.json"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
