import subprocess, json
for stage, tag in ((2, "ours(bm-a-r419)"), (3, "bm-b-r414")):
    j = json.loads(subprocess.run(["git", "show", ":%d:results/runnable_pool.json" % stage], capture_output=True).stdout)
    e = j["entries"]
    print(tag, "entries:", len(e), "entry keys:", sorted(e[0].keys()) if e else None)
    print(tag, "schema:", j.get("schema"), "| version:", j.get("version"), "| stamp_note:", str(j.get("_stamp_note"))[:100])
    print(tag, "first entry:", json.dumps(e[0], ensure_ascii=False)[:220])
    print(tag, "updated_at:", j.get("updated_at"))
