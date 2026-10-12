# -*- coding: utf-8 -*-
# r954 CAS direct-deposit to group tree: orders.md dispatch row + QC-r954.json
# Method: temp-index + commit-tree + push sha:main (no working-tree touch, race-safe)
import subprocess, sys, os

G = r"C:\Program Files\Git\cmd\git.exe"
TREE = r"K:\Fluxgroup\FluxGroup"
QC_FILE = os.path.join(TREE, r"cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\QC-r954.json")

def run(args, cwd=None, inp=None, binary=False):
    r = subprocess.run([G] + args, cwd=cwd, capture_output=True,
                       input=inp, text=not binary, encoding=None if binary else "utf-8")
    if r.returncode != 0:
        print("GITFAIL", args[:3], (r.stderr or b"").decode("utf-8", "replace")[:400] if binary else str(r.stderr)[:400])
        sys.exit(2)
    return r.stdout.strip()

# 1. origin tip + orders.md blob
tip = run(["rev-parse", "origin/main"], cwd=TREE)
orders = run(["show", "origin/main:docs/orders.md"], cwd=TREE)  # text utf-8
assert "03:4x" in orders.splitlines()[-1], "anchor row (03:4x Seedance) not at tail"
if not orders.endswith("\n"):
    orders += "\n"

ROW = ("| 10-13 04:3x | **@bm-a track-2 帧级再生派单（C03+C04+C09 三帧·夜窗 Krea2·死线 05:15）**"
       "（O-20261012-2330 执行件·bm-c r954 QC 巡检后拍板） | "
       "**三镜全帧级伤=i2v 治不了·bm-c 本机无 Krea2 权重（实测仅 H3 INT8）→ bm-a 夜窗 Krea2=唯一帧源**："
       "①处方全文=BigMoney 仓 fleet/inbox/MSG-20261013-0430-bmc.md"
       "（C03=BANDS 楔形显性锚照 MSG-0215 原案·C04=横排离散楔行+玄武岩哑光黑+正面平视〔禁放射盘/禁沙土/禁斜切〕"
       "·C09=双人中景盟誓主体+回纹墙降背景≤30%画幅+誓约→天变运动·人物 ID 块导演席终定）；"
       "②帧成 TJGenerators file_upload → CDN 直链回执投 BigMoney 仓 fleet/inbox/（bma 署名件）·bm-c 即刻下载投 i2v FIFO（INT8 768P）；"
       "③**死线 05:15 前回帧**（进 06:30 收口窗·07:00 装配·08:30 呈片不变）——无回帧=06:30 如实披露 FAIL·导演席裁量 retime/omit"
       "（bm-c 无自生帧能力·H3 t2v 兜底仅器物镜且需导演点头才启用）；"
       "④r954 QC 四片全 PASS 已锁：R04_river_dry 8.0 / C06_forever_cut_v2 7.5 压线锁（凿锤未入画+碎屑静态+匀速三轻度披露·v1 6.5 早落锤段可备选）"
       "/ D02_she_reads 8.0（人脸镜本地 INT8 首过=Seedance 拒审镜活路实证）/ D03_two_worlds 8.0（自倒影合规·玻璃反光锚建议披露）——详 bmc/QC-r954.json；"
       "在烧 R05/C07_v2/R02_v2/B01/E03·ETA ~05:00 排尽 | dispatched（bmc r954·poke 已发） |\n")
orders_new = orders + ROW

# 2. hash blobs
b1 = run(["hash-object", "-w", "--stdin"], cwd=TREE, inp=orders_new)
b2 = run(["hash-object", "-w", QC_FILE], cwd=TREE)

# 3. temp index from origin/main, update two paths
idx = os.path.join(TREE, ".git", "cas-index-r954")
env_run = ["--work-tree", TREE]  # not needed; use env via GIT_INDEX_FILE
os.environ["GIT_INDEX_FILE"] = idx
if os.path.exists(idx):
    os.remove(idx)
run(["read-tree", tip], cwd=TREE)
run(["update-index", "--add", "--cacheinfo", "100644,%s,docs/orders.md" % b1], cwd=TREE)
qc_rel = "cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012/bmc/QC-r954.json"
run(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (b2, qc_rel)], cwd=TREE)
tree = run(["write-tree"], cwd=TREE)
del os.environ["GIT_INDEX_FILE"]

# 4. commit + push
msg = ("orders: @bm-a track-2 3-frame regen dispatch (C03/C04/C09, Krea2, dl 05:15) + QC-r954.json "
       "(4 clips PASS: R04 8.0 / C06v2 7.5 / D02 8.0 / D03 8.0) [bm-c r954]")
commit = run(["commit-tree", tree, "-p", tip, "-m", msg], cwd=TREE)
out = run(["push", "origin", commit + ":refs/heads/main"], cwd=TREE)
print("PUSH_OK", commit[:12], "parent", tip[:12])
