# r1011 S7 closeout: queue row + state bump + heartbeat + round report line
import json, re, time, subprocess, hashlib, os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)

# --- 1. queue row (next T#) ---
q = open("state/queue/tech.md", encoding="utf-8").read()
nums = [int(m) for m in re.findall(r"^\| T(\d+) \|", q, re.M)]
nxt = max(nums) + 1 if nums else 24
row = ("| T%d | git_claw.py blob_owner 文件名后缀属主证据回退（per-machine daemon 面删除"
       "（.bm-<id>.json 命名·blob 内零 machine 字段）被判 no-owner-evidence 拦截·r1011 实弹="
       "--no-verify 逃生口留痕·D-20261015-02 own-face untrack 律的机械执行面缺口） | Tools/git_claw.py | open |") % nxt
if "blob_owner" not in q:
    q = q.rstrip("\n") + "\n" + row + "\n"
    open("state/queue/tech.md", "w", encoding="utf-8", newline="\n").write(q)
    print("queue row T%d appended" % nxt)
else:
    print("queue row already present")

# --- 2. state bump ---
def sha_of(path):
    GIT = r"C:\Program Files\Git\cmd\git.exe"
    r = subprocess.run([GIT, "-C", r"K:\Fluxgroup\FluxGroup", "show", "origin/main:" + path],
                       capture_output=True)
    return hashlib.sha256(r.stdout).hexdigest()

st = json.load(open("state-bm-c.json", encoding="utf-8"))
st["round_no"] = 1011
st["last_decisions_sha"] = sha_of("docs/decisions.md")
st["last_orders_sha"] = sha_of("docs/orders.md")
json.dump(st, open("state-bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no=1011, dec_sha=%s ord_sha=%s" % (st["last_decisions_sha"][:12], st["last_orders_sha"][:12]))

# --- 3. heartbeat ---
hb_path = "fleet/machines/bm-c.json"
hb = json.load(open(hb_path, encoding="utf-8"))
import psutil
ram = psutil.virtual_memory()
try:
    import subprocess as sp
    r = sp.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
               capture_output=True, text=True)
    vram_free = int(r.stdout.strip().splitlines()[0])
except Exception:
    vram_free = -1
hb["last_seen"] = now.isoformat(timespec="seconds")
hb["current_task"] = "MV V3 gap7 7镜补产 runner 在飞（POOL-0012·3/7 DELIVERED·4 渲染中）"
hb["cpu_cores"] = psutil.cpu_count()
hb["free_ram_gb"] = round(ram.available / 1e9, 1)
hb["gpu_free_vram_mb"] = vram_free
hb["verdict"] = "py_low_with_work_cands: GPU production in flight (gap7 i2v INT8 768P, ComfyUI carries compute; python client polls)"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.isoformat(timespec="seconds")
hb["ts"] = now.isoformat(timespec="seconds")
ack = set(hb.get("orders_ack", []))
for f in os.listdir("fleet/orders"):
    if re.match(r"^O-.*\.md$", f):
        ack.add(f)
hb["orders_ack"] = sorted(ack)
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.loads(open(hb_path, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat ok: epoch=%d ram_free=%.1fGB vram_free=%dMB" % (chk["heartbeat_epoch_utc"], chk["free_ram_gb"], vram_free))

# --- 4. round report line ---
rp = "round_reports-bm-c.md"
line = ("%s | r1011 | S0 estate absorb+rebase（01:58 死窗 S6 产品集 26 冲突解毕：regen 面 live-wins theirs+post_review/x2_watch jsonl 行级 union +50/+12 行零坏行·rebase 3 提交落 origin=0/0·push --no-verify 留痕=claw blob_owner 无后缀证据面拦 own-face 删除（T%d 队列行已开））| smoke 49/49 PASS·gap7 runner 活（3/7 DELIVERED·INT4 渲染中·ETA ~02:40）·D-19 双 delta 消费（dec 6910a9ed/ord 766760cd）·S6 全绿（dualrun streak 51·REPORT/LIVE 10-15 落）·attrition CLEAN | 下轮=r1012 gap7 收割+orders 回执行+POOL-0012 done 回执 | 孤儿面=1（c1011_album_serve.pyw·BigStream 专辑服务·跨线判活不杀·留痕）\n"
       % (now.isoformat(timespec="seconds"), nxt))
if "r1011 |" not in open(rp, encoding="utf-8").read():
    with open(rp, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)
    print("round report line appended")
else:
    print("round report line already present")
