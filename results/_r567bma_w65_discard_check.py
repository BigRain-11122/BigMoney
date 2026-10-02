import json, glob
# attribution check before discard (r525/r563 law: verify ownership at the moment of the knife)
for f in sorted(glob.glob(r"results\p2cal_ext\n1_w65\shard-*.json")):
    d = json.load(open(f, encoding="utf-8"))
    audit = d.get("audit") or {}
    print(f.split("\\")[-1], "| audit.machine =", audit.get("machine"),
          "| workers =", audit.get("workers"))
st = json.load(open(r"results\saturation_engine\state_bm-a.json", encoding="utf-8"))
q = st.get("queue") or []
act = st.get("active") or []
print("engine queue rows:", len(q), "| W65 in queue:",
      [e.get("key") for e in q if e.get("wave") == 65][:3])
print("active burns:", [(b.get("key"), b.get("pid")) for b in act])
