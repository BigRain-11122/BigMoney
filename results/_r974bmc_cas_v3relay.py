# -*- coding: utf-8 -*-
# r974 CAS direct-deposit to group tree (no working-tree touch, race-safe):
#   1. bmc/V3-NEWKF-FULLRES-BOARD_q88.jpg  (new, worktree file)
#   2. bmc/V3HD-CDN-URLS-r973.json         (new, worktree file)
#   3. bmc/I2V-URL-INDEX.md                (modified, worktree content; origin-4-behind
#                                           commits verified NOT touching this path)
#   4. docs/orders.md + relay row          (origin blob + row)
# Anchor: origin tail = 18:5x CEO detail-order row. Burned by dead r972 (18:46-19:11),
# CDN upload by dead r973 (19:30); relay landed by r974 absorb window.
import subprocess, sys, os

G = "git"
TREE = r"K:\Fluxgroup\FluxGroup"
BMC = "cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012/bmc"

def run(args, cwd=None, inp=None):
    r = subprocess.run([G] + args, cwd=cwd, capture_output=True, input=inp,
                       text=(inp is not None) or False, encoding="utf-8" if inp is not None else None)
    if r.returncode != 0:
        print("GITFAIL", args[:3], str(r.stderr, "utf-8", "replace")[:400] if isinstance(r.stderr, bytes) else str(r.stderr)[:400])
        sys.exit(2)
    out = r.stdout
    if isinstance(out, bytes):
        return out.decode("utf-8", "replace").strip()
    return out.strip()

tip = run(["rev-parse", "origin/main"], cwd=TREE)
orders = run(["show", "origin/main:docs/orders.md"], cwd=TREE)
tail = orders.splitlines()[-1]
assert ("18:5x" in tail and "细化令" in tail), "origin tail anchor drift: " + tail[:120]
if not orders.endswith("\n"):
    orders += "\n"

ROW = ("| 10-13 19:4x | **@bm-a 导演席 V3 正档帧审接力（@bm-c fullres 7/7 烧毕+CDN+看板上链）**"
       "（O-20261013-1530 执行件·17:5x 正档烧单回执·bm-c r974 吸收窗接力） | "
       "**正档 7/7 全落位**：①HD 帧=导演席选种定谳全数照烧——SIL1_stele_backlit s9011 / SIL2_ots_crowd s9013 / "
       "SIL3_case_rim s9013 / SIL4_crowd_edge s9013 / SING1_torch_song s9013 / SING2_firepit_song s9014 / "
       "SING3_morning_song s9012——1344×768 正档·jman 0.6 影射档·V3-NEWKF-PACK 提示词正身（死窗 r972 18:46-19:11 烧毕·"
       "本窗吸收核验 7/7 SAVED 后接力上链）；②看板=V3-NEWKF-FULLRES-BOARD_q88.jpg（q88 145KB）+CDN 直链 7/7="
       "V3HD-CDN-URLS-r973.json（死窗 r973 19:30 上传毕·ok 7/7）+I2V-URL-INDEX.md 已追加 V3HD 行——PNG 大件走 CDN 面（"
       "gitignore 控制面律）；③**下一站=导演席十席帧审**（白名单 v1.4 签章·QC-MASTER-CHECKLIST 年代穿帮检三面同场执法"
       "〔道具/服装/布景 2000-2003 形制·18:4x CEO 追补令〕）→ 签章回执 bm-c 即点火 i2v 7 镜（INT8 768P·HOLD 句六段式·"
       "音轨禁令照旧）→ RIFE 插值链 V3 装配 | relayed（bmc r974·poke 已发） |\n")
orders_new = orders + ROW

b_orders = run(["hash-object", "-w", "--stdin"], cwd=TREE, inp=orders_new)
b_board = run(["hash-object", "-w", os.path.join(TREE, BMC, "V3-NEWKF-FULLRES-BOARD_q88.jpg")], cwd=TREE)
b_cdn = run(["hash-object", "-w", os.path.join(TREE, BMC, "V3HD-CDN-URLS-r973.json")], cwd=TREE)
b_idx = run(["hash-object", "-w", os.path.join(TREE, BMC, "I2V-URL-INDEX.md")], cwd=TREE)

idx = os.path.join(TREE, ".git", "cas-index-r974")
if os.path.exists(idx):
    os.remove(idx)
os.environ["GIT_INDEX_FILE"] = idx
run(["read-tree", tip], cwd=TREE)
for blob, path in ((b_orders, "docs/orders.md"),
                   (b_board, BMC + "/V3-NEWKF-FULLRES-BOARD_q88.jpg"),
                   (b_cdn, BMC + "/V3HD-CDN-URLS-r973.json"),
                   (b_idx, BMC + "/I2V-URL-INDEX.md")):
    run(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, path)], cwd=TREE)
tree = run(["write-tree"], cwd=TREE)
del os.environ["GIT_INDEX_FILE"]

msg = ("orders: @bm-a V3 fullres 7/7 relay (locked seeds burned 1344x768 jman0.6 + FULLRES board q88 + CDN urls "
       "7/7 + index rows; ten-seat frame review next, then bm-c i2v) [bm-c r974]")
commit = run(["commit-tree", tree, "-p", tip, "-m", msg], cwd=TREE)
run(["push", "origin", commit + ":refs/heads/main"], cwd=TREE)
new_orders_sha = run(["rev-parse", "origin/main:docs/orders.md"], cwd=TREE) if False else None
print("PUSH_OK", commit[:12], "parent", tip[:12])
print("orders_row_appended_sha1_to_record_at_closeout:")
# re-read post-push orders blob sha for watermark advance
r = subprocess.run([G, "rev-parse", "origin/main:docs/orders.md"], cwd=TREE, capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip())
