# -*- coding: utf-8 -*-
# r1007 bm-b: group-repo (FluxGroup) surgery push — P2 word-anchor receipt package
#   faces: 2 official lyrics + 4 calibrated outputs + lyric_calibration.py argv filter
#          + LEDGER union heal (bm-b memory-gate first-run lines + bm-a lines preserved)
#          + receipt md. Temp-index CAS surgery on fresh origin tip (r950/r982 law),
#          zero worktree rebase, content-verified via diff-tree face-set assert.
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = r"C:\Fluxgroup\FluxGroup"
BASE_REF = "origin/main"
ALB = "cph4/fleet/mv-album-001-jay"
LEDGER = "cph4/fleet/memory-slim/LEDGER.md"
TMP = os.path.join(REPO, "results") if os.path.isdir(os.path.join(REPO, "results")) else REPO
os.makedirs(os.path.join(REPO, "results"), exist_ok=True)
TMPIDX = os.path.join(REPO, "results", "_r1007bmb_group_tmpindex")
MSG = os.path.join(REPO, "results", "_r1007bmb_group_msg.txt")
LEDGER_UNION = os.path.join(REPO, "results", "_r1007bmb_ledger_union.md")


def git(*args, **kw):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, **kw)
    return r


def out(r):
    return r.stdout.decode("utf-8", "replace").strip()


def die(msg):
    print("FATAL:", msg)
    sys.exit(1)


# ---------- 1) base tip ----------
tip = out(git("rev-parse", BASE_REF))
if not (len(tip) == 40 and all(c in "0123456789abcdef" for c in tip)):
    die("bad base tip %r" % tip)
print("base tip:", tip)

# ---------- 2) LEDGER union ----------
origin_ledger = git("show", BASE_REF + ":" + LEDGER).stdout.decode("utf-8", "replace")
local_path = os.path.join(REPO, LEDGER.replace("/", os.sep))
with io.open(local_path, encoding="utf-8") as f:
    local_lines = [ln.rstrip("\r") for ln in f.read().splitlines()]
# bm-b receipt lines = the BIGMONEY gate rows (last two on local disk)
bmb_rows = [ln for ln in local_lines if "BIGMONEY" in ln and ln.startswith("|")]
if len(bmb_rows) != 2:
    die("expected 2 bm-b BIGMONEY rows on local LEDGER, got %d" % len(bmb_rows))
origin_rows = origin_ledger.splitlines()
already = [ln for ln in origin_rows if "BIGMONEY" in ln]
if already:
    print("bm-b rows already on origin (%d) — union is append-guarded" % len(already))
union = "\n".join(origin_rows + bmb_rows) + "\n"
with io.open(LEDGER_UNION, "w", encoding="utf-8", newline="\n") as f:
    f.write(union)
# heal the local disk face to the union (byte-honest, converges on next pull)
with io.open(local_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(union)
print("LEDGER union rows:", len(origin_rows), "+", len(bmb_rows))

# ---------- 3) receipt face ----------
receipt_path = os.path.join(REPO, ALB.replace("/", os.sep), "p2-wordanchor-receipt-r1007bmb.md")
receipt = """# P2 三曲词锚批回执 — @bm-b r1007（承 orders 2026-10-18 13:5x「利用好机队的本地算力！」令②派单）

**dispatch**: 13:5x 本地算力优先令②【@bm-b】P2 三曲 whisper 词锚批（龙卷风/斗牛/黑色幽默·word_timestamps·锚点入 anchors/ 同构·MV 面 480P animatic 备援位待命）
**回执窗**: 2 轮（本件=第 1 轮即窗回执）

## 1. 查重定位（零重跑）
- 三曲 `-words.json` word_timestamps 面已全部在册：commit 1bd21af（bm-b r992·POOL-0018 批·whisperX word-level 全 10 曲）——本派单的 words 面按反重复铁律不重烧。
- 音源披露：POOL-0018 批用 `audio/` 320k mp3 同源件（media/MUSIC/jay 无损源本机不存在）——词级对齐用途下与无损等效。

## 2. 本轮新增实物（校准面=MV 歌词层消费面）
| 曲 | 官方词面 | 校准面 | exact/approx/none |
|---|---|---|---|
| 斗牛 | `lyrics/斗牛.txt` 91 行 | `anchors/斗牛-calibrated.{json,txt}` | 66 / 19 / 6 |
| 黑色幽默 | `lyrics/黑色幽默.txt` 42 行 | `anchors/黑色幽默-calibrated.{json,txt}` | 36 / 6 / 0 |
| 龙卷风 | （v1 批已有） | （v1 批已校准） | — |

→ **P2 三曲校准面自此齐备**（v1 批六曲之外的两缺口补齐）。

## 3. 词面来源与交叉核验
- 斗牛：lyrics.net.cn/lyrics/24 全文 × TRACK05 锚句件（仓内已核原文）交叉一致（「有种不要走」定谳）。
- 黑色幽默：lyrics.net.cn/lyrics/73487 × mulanci.org sl114776 双源交叉；「心理→心里」按二源+听感判据修正为官方「心里」。
- 校准算法=仓内 lyric_calibration.py 现行 DP（whisper 行段 × 官方行单调对齐），确定性可复跑。

## 4. 诚实披露（斗牛曲首喊话段）
- 斗牛前奏喊话两轮（词面行 1-16，音频 ~15-44s）= whisper 掩蔽洞（crowd-noise 遮蔽·听写零覆盖；44.0-46.5s 仅有「有话就接受/马上三分钟」尾部误听碎片）→ 校准面 none=6 + approx=10，窗口压在 10.82-46.50。
- 词层消费建议：喊话段行按器乐段手定或入 animatic 时人工对齐；说唱/桥/副歌主体（行 17+，46.5-276s）exact 面扎实。
- 黑色幽默 42 行全带时窗零 none；行 26「败给你的黑色幽默」窗口 125.20-163.88 [approx] = 器乐间奏段（正确行为）。

## 5. 工具面
- `lyric_calibration.py` 新增 argv 过滤器：`python lyric_calibration.py 斗牛 黑色幽默` 只跑指名曲（单曲幂等重跑不动他曲产物）；裸跑=全集，行为不变。

## 6. 附带收口
- LEDGER union heal：本机记忆门首跑 2 回执行（BIGMONEY 记忆治理班 10:30 ×2）入账，bm-a 10:27/10:21-10:30 两行保位（陈旧基座写穿修复·行级 union）。

— via bm-b r1007（值守轮·2026-10-18 14:2x）
"""
with io.open(receipt_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(receipt)
print("receipt written:", receipt_path)

# ---------- 4) surgery: temp index on fresh tip ----------
faces = [
    (ALB + "/lyrics/斗牛.txt", os.path.join(REPO, ALB.replace("/", os.sep), "lyrics", "斗牛.txt")),
    (ALB + "/lyrics/黑色幽默.txt", os.path.join(REPO, ALB.replace("/", os.sep), "lyrics", "黑色幽默.txt")),
    (ALB + "/anchors/斗牛-calibrated.json", os.path.join(REPO, ALB.replace("/", os.sep), "anchors", "斗牛-calibrated.json")),
    (ALB + "/anchors/斗牛-calibrated.txt", os.path.join(REPO, ALB.replace("/", os.sep), "anchors", "斗牛-calibrated.txt")),
    (ALB + "/anchors/黑色幽默-calibrated.json", os.path.join(REPO, ALB.replace("/", os.sep), "anchors", "黑色幽默-calibrated.json")),
    (ALB + "/anchors/黑色幽默-calibrated.txt", os.path.join(REPO, ALB.replace("/", os.sep), "anchors", "黑色幽默-calibrated.txt")),
    (ALB + "/lyric_calibration.py", os.path.join(REPO, ALB.replace("/", os.sep), "lyric_calibration.py")),
    (ALB + "/p2-wordanchor-receipt-r1007bmb.md", receipt_path),
    (LEDGER, LEDGER_UNION),
]
env = dict(os.environ, GIT_INDEX_FILE=TMPIDX)
if os.path.exists(TMPIDX):
    os.remove(TMPIDX)
r = subprocess.run(["git", "-C", REPO, "read-tree", tip], capture_output=True, env=env)
if r.returncode != 0:
    die("read-tree: " + r.stderr.decode("utf-8", "replace"))
for path, disk in faces:
    if not os.path.exists(disk):
        die("missing disk face " + disk)
    h = subprocess.run(["git", "-C", REPO, "hash-object", "-w", "--no-filters", disk],
                       capture_output=True, env=env).stdout.decode().strip()
    if not (len(h) == 40 and all(c in "0123456789abcdef" for c in h)):
        die("bad blob %r for %s" % (h, path))
    r = subprocess.run(["git", "-C", REPO, "update-index", "--add", "--cacheinfo",
                         "100644,%s,%s" % (h, path)], capture_output=True, env=env)
    if r.returncode != 0:
        die("update-index %s: %s" % (path, r.stderr.decode("utf-8", "replace")))
    print("staged:", path, h[:12])
tree = subprocess.run(["git", "-C", REPO, "write-tree"], capture_output=True, env=env).stdout.decode().strip()
if not (len(tree) == 40 and all(c in "0123456789abcdef" for c in tree)):
    die("bad tree %r" % tree)
# face-set assert: diff-tree vs base must show exactly our 9 paths
dt = subprocess.run(["git", "-c", "core.quotePath=false", "-C", REPO, "diff-tree",
                     "--name-only", "-r", tip, tree],
                    capture_output=True, env=env).stdout.decode("utf-8", "replace").strip()
changed = set(ln for ln in dt.splitlines() if ln)
expected = set(p for p, _ in faces)
if changed != expected:
    die("face-set mismatch\n  changed: %s\n  expected: %s" % (sorted(changed), sorted(expected)))
print("face-set assert OK:", len(expected), "faces")

# ---------- 5) commit ----------
msg = """mv-album: @bm-b P2 词锚批回执 — 斗牛/黑色幽默 官方词面+校准面落地（承 orders 10-18 13:5x 本地算力令②）[via bm-b r1007]

- 查重定位: 三曲 -words.json word_timestamps 已在册 (1bd21af·POOL-0018) 零重跑; 音源=audio/ 320k mp3 同源
- 新增官方词面: lyrics/斗牛.txt 91行 (lyrics.net.cn/24 × TRACK05 锚句交叉) + lyrics/黑色幽默.txt 42行 (lyrics.net.cn/73487 × mulanci sl114776 双源, 「心理→心里」按二源修正)
- 新增校准面: 斗牛-calibrated 66/19/6 + 黑色幽默-calibrated 36/6/0 → P2 三曲校准面齐 (龙卷风 v1 批已有)
- 披露: 斗牛曲首喊话两轮 (~15-44s) whisper 掩蔽洞 → none6+approx10, 词层消费按器乐段手定; 主体 46.5-276s exact 扎实
- 工具: lyric_calibration.py argv 过滤器 (指名单曲幂等重跑, 裸跑=全集)
- LEDGER union heal: bm-b 记忆门首跑 2 行入账 + bm-a 两行保位 (陈旧基座写穿修复)
- 回执: p2-wordanchor-receipt-r1007bmb.md
"""
with io.open(MSG, "w", encoding="utf-8", newline="\n") as f:
    f.write(msg)
newc = subprocess.run(["git", "-C", REPO, "commit-tree", tree, "-p", tip, "-F", MSG],
                      capture_output=True, env=env).stdout.decode().strip()
if not (len(newc) == 40 and all(c in "0123456789abcdef" for c in newc)):
    die("bad commit %r" % newc)
print("commit:", newc)

# ---------- 6) push ----------
r = subprocess.run(["git", "-C", REPO, "push", "origin", newc + ":refs/heads/main"],
                   capture_output=True)
po = (r.stdout + r.stderr).decode("utf-8", "replace")
bad = [w for w in ("fatal", "rejected", "failed", "error") if w in po.lower()]
if r.returncode != 0 or bad:
    die("push failed rc=%d: %s" % (r.returncode, po))
print("push OK:", po.strip()[-200:])
# delivery verify (ls-remote line = "<sha>\t<ref>")
ls = out(git("ls-remote", "origin", "refs/heads/main")).split("\t")[0].strip()
if ls != newc:
    die("delivery mismatch: ls-remote=%r != %r" % (ls, newc))
print("DELIVERY VERIFIED:", ls)
print("SURGERY COMPLETE — 9 faces on", newc[:12])
