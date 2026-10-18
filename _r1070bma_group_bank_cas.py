import subprocess, json, os, tempfile, re, sys

G = r"C:\Users\sjs20\Desktop\FluxGroup"
PATH = "cph4/fleet/work-bank/bm-a-gpu-bank.json"
MSG = ("fleet: bm-a-gpu-bank.json work-bank instance (O-20261018-2236 sec.2.2 "
       "canon adopt; empty jobs = producer-pending honest face; schema verbatim "
       "from bm-c-gpu-bank.json per MSG-20261019-0102) [via bm-a r1070]")

def git(*a, env=None):
    return subprocess.run(["git", "-C", G, *a], capture_output=True, env=env)

def sha40(s):
    return re.fullmatch(r"[0-9a-f]{40}", s or "") is not None

BANK = {
    "_law": "工作银行 v1.0（CEO 2026-10-18 令「不要出现10分钟以上的闲置」）：产线收官前生产者必预挂后继波到本银行（预挂律）·IdleGuard 10分钟两跳认领·空闲时银行空=生产者违例记账·活件必须预过闸（授权链写auth字段）·claimed/expire状态由守卫维护",
    "jobs": [],
}

tmpf = os.path.join(tempfile.gettempdir(), "r1070bma_bank.json")
with open(tmpf, "w", encoding="utf-8", newline="\n") as f:
    json.dump(BANK, f, ensure_ascii=False, indent=1)
    f.write("\n")

msgf = os.path.join(tempfile.gettempdir(), "r1070bma_bank_msg.txt")
with open(msgf, "w", encoding="utf-8", newline="\n") as f:
    f.write(MSG + "\n")

idx = os.path.join(tempfile.gettempdir(), "r1070bma_group_cas.idx")
if os.path.exists(idx):
    os.remove(idx)

r = git("hash-object", "-w", tmpf)
blob = r.stdout.decode().strip()
assert r.returncode == 0 and sha40(blob), ("blob", r.returncode, blob, r.stderr[:200])

delivered = None
for attempt in (1, 2):
    r = git("fetch", "origin")
    assert r.returncode == 0, ("fetch", r.stderr[:300])
    base = git("rev-parse", "origin/main").stdout.decode().strip()
    assert sha40(base), ("base", base)
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    if os.path.exists(idx):
        os.remove(idx)
    r = git("read-tree", base, env=env)
    assert r.returncode == 0, ("read-tree", r.stderr[:300])
    r = git("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, PATH), env=env)
    assert r.returncode == 0, ("update-index", r.stderr[:300])
    r = git("write-tree", env=env)
    tree = r.stdout.decode().strip()
    assert r.returncode == 0 and sha40(tree), ("tree", tree)
    r = git("commit-tree", tree, "-p", base, "-F", msgf)
    newc = r.stdout.decode().strip()
    assert r.returncode == 0 and sha40(newc), ("commit-tree", r.returncode, newc, r.stderr[:300])
    r = subprocess.run(["git", "-C", G, "push", "origin", newc + ":refs/heads/main"],
                       capture_output=True)
    out = (r.stdout + r.stderr).decode(errors="replace")
    push_ok = r.returncode == 0 and not any(
        w in out for w in ("fatal", "rejected", "failed", "error"))
    if push_ok:
        delivered = (base, newc)
        break
    print("push attempt %d rejected (rc=%s): %s" % (attempt, r.returncode, out[:200]))

assert delivered, "CAS push failed both attempts"
r = git("fetch", "origin")
assert r.returncode == 0
tip = git("rev-parse", "origin/main").stdout.decode().strip()
blob_check = git("rev-parse", "origin/main:" + PATH).stdout.decode().strip()
assert blob_check == blob, ("blob mismatch", blob_check, blob)
print(json.dumps({"push": "ok", "base": delivered[0][:10], "new": delivered[1][:10],
                  "tip": tip[:10], "path": PATH,
                  "blob_equality": "ok", "attempts": attempt}))
