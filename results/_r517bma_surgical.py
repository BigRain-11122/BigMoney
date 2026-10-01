# r517 surgical push builder (r512 law): temp index on origin/main, per-file overlay, CODELY entry-union
import subprocess, os, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
IDX = os.path.join(REPO, "results", "_r517bma_surgical.idx")
os.environ["GIT_INDEX_FILE"] = IDX
if os.path.exists(IDX):
    os.remove(IDX)

def git(*args, **kw):
    return subprocess.check_output(["git", "-C", REPO] + list(args), **kw)

ORIGIN = git("rev-parse", "origin/main").decode().strip()
print("parent (origin/main):", ORIGIN)

# 1) temp index = origin/main tree
git("read-tree", ORIGIN)

# 2) CODELY.md union: origin blob + my one entry inserted after "### Feedback"
MY_LINE = "- [2026-10-01 13:4x r517 bm-a] O-1332 CEO 算力饱和恢复令回执（S7 双扫截获·同轮 ack）：T-139 点火 SLA 违例定谳=census stage-A 6/6（r512 产品）≠炉开烧；stage-B judged prereg（survivors=census_ranking.json top10_independent·D6 已过）为点火前置禁跳 → r518 首动作=prereg 冻结+池登记+开烧（ProcessPool+核分布行）；T-131 批准=bm-c 车道（r292 探针）；NULLS 烧录 TEMP 头/活尾分裂（r220 移件）→ 重聚律=烧录 EXIT 后才碰产物件（活句柄面禁中途合并）。正典=fleet/orders/O-20261001-1332-bm-c.md；回执=round_reports-bm-a.md r517 行+心跳 orders_ack。"
origin_codely = git("show", f"{ORIGIN}:CODELY.md").decode("utf-8")
if MY_LINE not in origin_codely:
    marker = "### Feedback\n"
    assert marker in origin_codely, "Feedback section missing on origin CODELY"
    union = origin_codely.replace(marker, marker + MY_LINE + "\n", 1)
    open(os.path.join(REPO, "CODELY.md"), "w", encoding="utf-8", newline="").write(union)
    print("CODELY union written:", len(union), "chars")
else:
    print("CODELY: my line already on origin (skip)")

# 3) overlay every file from my 3 unpushed commits (my committed versions)
mine = set(git("diff", "--name-only", f"{ORIGIN}...HEAD").decode().split())
print("my changed files:", len(mine))
for p in sorted(mine):
    p = p.strip()
    if not p or p == "CODELY.md":
        continue
    # use my committed blob (HEAD version)
    blob = git("show", f"HEAD:{p}")
    sha = git("hash-object", "-w", "--stdin", input=blob).decode().strip()
    git("update-index", "--add", "--cacheinfo", f"100644,{sha},{p}")

# autofill_state.bm-a.json: ride the daemon's latest working-tree version instead (fresher)
p = "results/autofill_state.bm-a.json"
wt = os.path.join(REPO, p.replace("/", "\\"))
if os.path.exists(wt):
    with open(wt, "rb") as f:
        data = f.read()
    import json as _json
    _json.loads(data)  # parse-verify (r185)
    sha = git("hash-object", "-w", "-").decode().strip() if False else git("hash-object", "-w", "--stdin", input=data).decode().strip()
    git("update-index", "--add", "--cacheinfo", f"100644,{sha},{p}")
    print("autofill_state rode latest WT version")

# also overlay CODELY union blob
with open(os.path.join(REPO, "CODELY.md"), "rb") as f:
    data = f.read()
import json as _json2
sha = git("hash-object", "-w", "--stdin", input=data).decode().strip()
git("update-index", "--add", "--cacheinfo", f"100644,{sha},CODELY.md")

# 4) write-tree + commit-tree on origin/main
tree = git("write-tree").decode().strip()
msg = """round 517 close + O-1332 CEO order ack (surgical push r512 law: crashed-rebase recovery delivered r516 P2 wave 34 files, NULLS kill-advice MSG-1345, 15-UU canon-resolved, S6 28 legs rc0, smoke 47/47; T-139 stage-B prereg+ignite = r518 first action per O-1332; T-131=bm-c lane; NULLS burn healthy w/ TEMP-head reunion plan) [via bm-a]"""
open(os.path.join(REPO, "results", "_r517bma_msg.txt"), "w", encoding="utf-8", newline="").write(msg)
commit = subprocess.check_output(["git", "-C", REPO, "commit-tree", tree, "-p", ORIGIN, "-F", os.path.join(REPO, "results", "_r517bma_msg.txt")], env={**os.environ}).decode().strip()
print("surgical commit:", commit)
# push
r = subprocess.run(["git", "-C", REPO, "push", "origin", f"{commit}:refs/heads/main"], capture_output=True, text=True)
print("push rc:", r.returncode)
print((r.stderr or "")[-300:])
