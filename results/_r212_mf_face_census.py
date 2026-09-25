import os, sys, datetime, io, json
sys.stdout.reconfigure(encoding="utf-8")
d = "data/moneyflow/per"
files = [(f, os.path.getmtime(os.path.join(d, f))) for f in os.listdir(d)]
files.sort(key=lambda x: -x[1])
print("per-file count:", len(files))
print("newest 10 by mtime:")
for f, m in files[:10]:
    print("  ", f, datetime.datetime.fromtimestamp(m).strftime("%m-%d %H:%M"))
print("oldest 5:")
for f, m in files[-5:]:
    print("  ", f, datetime.datetime.fromtimestamp(m).strftime("%m-%d %H:%M"))
# status history: last_refresh started times
st = json.load(open("results/moneyflow_update_status.json", encoding="utf-8"))
lr = st.get("last_refresh", {})
print("last_refresh started:", lr.get("started"), "appended:", lr.get("appended"), "failures:", lr.get("failures"))
print("last_spawn_attempt:", st.get("last_spawn_attempt"))
print("mode:", st.get("mode"))
