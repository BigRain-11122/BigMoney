# SHARD-1 done-flip (r180 dual-flip) + verification
import json, os, datetime

POOL = "results/runnable_pool.json"
pool = json.load(open(POOL, encoding="utf-8-sig"))
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# three-way verification first
p = "results/wild_route/checkpoint-1of8.jsonl"
keys = set()
for line in open(p, encoding="utf-8"):
    line = line.strip()
    if line:
        r = json.loads(line)
        assert r["done"] is True
        keys.add(r["key"])
files = set(f[:-5] for f in os.listdir("results/wild_route/cells") if f.endswith(".json"))
expect = {k.replace("|", "_") for k in keys}
assert expect <= files, sorted(expect - files)[:3]
assert len(keys) == 196, len(keys)
print("three-way OK: 196 ckpt keys all done:true, all files present")

for e in pool["entries"]:
    if e["id"] == "WILD-S1-SHARD-1":
        assert e["status"] == "ready", e["status"]
        e["status"] = "done"
        e["done_at"] = now
        e["done_note"] = ("196/196 cells complete: ckpt-1of8 196 unique keys all done:true, "
                          "196 cell files on disk (three-way verified r200); runner pid 20900 "
                          "finished ~19:50:00, 19:50:01 tick pid 12044 = resume no-op same "
                          "pattern as SHARD-0 r161 lag residual")
        for sh in e["shards"]:
            assert sh["key"] == "wr-1of8"
            sh["status"] = "done"
        break
else:
    raise SystemExit("SHARD-1 entry not found")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)
pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"] if x["id"] == "WILD-S1-SHARD-1"][0]
print("flip OK:", e2["status"], e2["done_at"], "| shard:", e2["shards"][0]["status"])

# append round report addendum line
REPORT = "logs/iteration-loop/round_reports.md"
raw = open(REPORT, "rb").read()
eol = b"\r\n" if raw[-2:] == b"\r\n" else b"\n"
addendum = (
    "2026-09-25 19:56 | r200 addendum bm-b | 同窗撞车实录+SHARD-1 闭合：①push 撞 bm-a R185 三连"
    "（088970a3/caa4ffcb/fbe3fc55 同窗先推）→pull --rebase 12-UU 全解：S6 六镜像+dashboard 双件"
    "全取我侧（实钟 19:34 vs 19:32 逐件 newest-wins）+autofill launches 43+44→45 union（**bm-a "
    "19:30:02 tick 已发射 SHARD-2 pid 49780=双机并行填装实证**）+compute_audit history 201+201→202 "
    "union+token machines union+**HANDOVER 双 5x 同窗双核对 union**（header=最近 R185+r200 同窗"
    "双核对·上一次 R175 原文保全·双 bullet 全保 31 条·bm-a 「上一次核对=最近核对=」双标签怪癖"
    "归一化·r200 主 commit 重放 68d72dc→f0c2897a 旧号 dangling r139 注记）+marker 终扫 0+"
    "smoke 25/25 复绿+推送在册 fbe3fc55..f0c2897a；②SHARD-1 196/196 完成于 ~19:50:00（runner "
    "pid 20900 19:40:03 起 10min 干完）→19:50:01 tick pid 12044=resume no-op（r161 翻面滞后残"
    "余同 SHARD-0 形态）→本轮当窗翻面 entry+shard 双 done r180 律+cells/checkpoint 随后 commit"
    "；③池态=2/8 done（SHARD-0/1 bm-b）+SHARD-2 bm-a 在跑（其盘）+SHARD-3..7 open 20:00 tick "
    "续填"
)
with open(REPORT, "ab") as f:
    f.write(eol + addendum.encode("utf-8"))
print("addendum appended")
