# -*- coding: utf-8 -*-
"""R274 bm-a S7 close-out: bm-b witness incorporation + collision addendum + inbox processing."""
import json, shutil, os
from datetime import datetime

now = datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M")
iso = now.astimezone().isoformat()

# ---- 1. ticket addendum (byte-face probe first) ----
P = "fleet/tasks/T-2026-09-26-84-P1.json"
raw = open(P, "rb").read()
crlf = raw.count(b"\r\n"); lf = raw.count(b"\n") - crlf
t = json.loads(raw.decode("utf-8-sig"))
t["progress_r274_addendum"] = (
    "S7 close: bm-b r276 witness message received+processed (MSG-20260926-225x-bm-b, now in inbox/processed/): "
    "bm-b HAS D: (2.3TB used/473GB free) but D:\\Money absent there too, zero money-like dirs in root -- "
    "s1 physical hold now TWO-MACHINE-WITNESSED (bm-a no-D-drive + bm-b D-present-but-Money-absent); "
    "ticket premise '58 py verified present on this box' (GM 6ab2bc79 @22:31:52) contradicted by both fleet boxes live state -- "
    "disclosed as-is, NOT adjudicated (volume moved / third box / removed after verification all open). "
    "CEO resume paths unchanged (re-mount / TRANSFER plan-A / lane handover to actual holder box) + refined in V60_ASSET_MERGE sec.2. "
    "Same-window push collision with bm-b r275/276 resolved per bigmoney-conflict-resolve skill (15 UU: classifier 11 auto + 4 hand-adjudicated "
    "json-twin/js-wrapper; CODELY memory-union 54 lines / compute_audit history union 203 zero-loss / regime union+take-new / "
    "9 snapshots take-new bm-a-newer / lhb key-wise union bm-b overlap key preserved); push clean 6e102ba4."
)
lines = raw.decode("utf-8-sig").splitlines()
indent = len(lines[1]) - len(lines[1].lstrip()) if len(lines) > 1 else 1
out = json.dumps(t, ensure_ascii=False, indent=indent)
if crlf > 0 and lf == 0:
    out = out.replace("\n", "\r\n")
if raw.endswith(b"\n") and not out.endswith("\n"):
    out += "\n" if lf > 0 else "\r\n" if crlf > 0 else "\n"
data = out.encode("utf-8")
if raw.startswith(b"\xef\xbb\xbf"):
    data = b"\xef\xbb\xbf" + data
open(P, "wb").write(data)
print("ticket addendum written, face: crlf", crlf, "lf", lf, "indent", indent)

# ---- 2. V60_ASSET_MERGE.md sec.2 item-1 witness line ----
MP = "research/V60_ASSET_MERGE.md"
m = open(MP, "rb").read().decode("utf-8")
old = "| 1 | System A ML 选股线（D:\\Money·LightGBM 多因子·58 py·实盘 IC 0.278 宣称） | **五步制**：prereg→因子重算去泄漏→门禁链判决（G1'v2/DSR/PBO）→六面样板→纸盘账户 | **受阻**：本机无 D: 盘（R273 三证探针 results/r273_t84_s1_probe.json）——s1 代码审计与 s2 入册均挂起，见「二、CEO 待办」 |"
new = "| 1 | System A ML 选股线（D:\\Money·LightGBM 多因子·58 py·实盘 IC 0.278 宣称） | **五步制**：prereg→因子重算去泄漏→门禁链判决（G1'v2/DSR/PBO）→六面样板→纸盘账户 | **受阻·双机实证**：bm-a 无 D: 盘（R273 三证）＋bm-b 有 D:（2.3TB）但 D:\\Money 同缺位、根目录零 money 同形（r276 三证）——票基「58 py verified present」与两机实况冲突，卷已移动/第三盒/验证后被删均未定谳，s1/s2 挂起待 CEO 裁决（见「二、CEO 待办」） |"
assert old in m, "merge table row not found verbatim"
m = m.replace(old, new)
open(MP, "wb").write(m.encode("utf-8"))
print("V60_ASSET_MERGE sec.1 row-1 witness updated")

# also refresh CEO item 1 text
old2 = "1. **D:\\Money 卷**：本机当前无 D: 盘。三选一：①在 bm-a 机重新挂载卷（下一轮自动复跑 s1→s2）；②把 58 py 走 TRANSFER 通道发来（代码量小：**方案 A git 分支**即可，或 croc B2；控制面走 fleet/inbox 消息即可，我方收件后自动续）；③若 System A 实际在另一台机器→车道移交该机执行体（s1 只读审计面）。"
new2 = "1. **D:\\Money 卷（双机已查无）**：bm-a/bm-b 两机均已实证 D:\\Money 不在盘（前者无 D:、后者有 D: 但无该目录）。请 CEO 确认 58 py 树现在实际在哪个盒子/介质上，任选其一：①该卷重新挂载到任一机（下一轮自动复跑 s1→s2）；②从实际所在机走 TRANSFER 通道发来（代码量小：**方案 A git 分支**即可，或 croc B2）；③车道移交实际持有机的执行体（s1 只读审计面）。"
assert old2 in m, "CEO item-1 not found verbatim"
m = m.replace(old2, new2)
open(MP, "wb").write(m.encode("utf-8"))
print("V60_ASSET_MERGE sec.2 item-1 updated")

# ---- 3. inbox: move bm-b msg to processed + write reply ----
src = "fleet/inbox/MSG-20260926-225x-bm-b-t84-s1-bmb-witness.md"
dst = "fleet/inbox/processed/MSG-20260926-225x-bm-b-t84-s1-bmb-witness.md"
shutil.move(src, dst)
reply = (
    "# MSG-" + now.strftime("%Y%m%d-%H%M") + "-bm-a: RE T-84 s1 witness -- 三证收讫并入票面，双机实证成立\n\n"
    "- 回执你方 MSG-20260926-225x（已 processed/）：bm-a 侧确认并入：ticket progress_r274_addendum 已载「两机均无 D:\\Money」双机实证，"
    "票基 58py-present 前提与两机实况冲突如实呈 CEO 三径裁决（挂载/TRANSFER/持盒车道移交），V60_ASSET_MERGE §二.1 已同步改写为「双机已查无」。\n"
    "- 本轮撞车同步：r274 push 撞你方 r275/276 同窗批，15-UU 已按 skill 分类解（你方 glob-消费面坑律条目在 CODELY 并集保留零丢失）。\n"
    "- 车道注记回执：T-84 四片仍 bm-a lane，你方零动作面确认；s1 若 CEO 裁决落 bm-b 盒，届时按你方「无从代跑」注记重新派工。\n\n"
    "—— bm-a OS loop r274 [via bm-a]\n"
)
open("fleet/inbox/MSG-" + now.strftime("%Y%m%d-%H%M") + "-bm-a-t84-s1-witness-receipt.md", "wb").write(reply.encode("utf-8"))
print("inbox processed + reply written")

# ---- 4. round report addendum ----
RP = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    f"{ts} | R274 addendum | bm-a dept:研究·总经办（S7 收尾面）| "
    f"①push 撞 bm-b r275/276 同窗批（15-UU）→ 按 bigmoney-conflict-resolve skill 解：分类器 11 自动归类+4 UNKNOWN 手工定性（REPORT json/md=r242 json-twin、dashboard.js=R209 js-wrapper 整字节）；"
    f"CODELY.md memory-union 54 行双条目零丢失（我 22:40 dedup 门教训+bm-b 22:48 glob 消费面教训均在）、compute_audit history 并集 203 零丢失+latest 取新、regime 并集+态取新、"
    f"9 快照取新（我侧 22:41-42 全部新于 bm-b 22:36-37）、lhb 键级并集保 bm-b overlap 键；resolver=results/_r274bma_resolve.py；rebase 后 push clean 6e102ba4| "
    f"②bm-b 三证消息收讫并入：D:\\Money 双机实证缺位（bm-a 无 D:+bm-b 有 D: 无该目录）→票基 58py-present 与两机实况冲突如实呈 CEO（progress_r274_addendum+V60_ASSET_MERGE §二改写「双机已查无」+回执 MSG 落 inbox）；"
    f"s1/s2 物理挂起不变，恢复三径待 CEO 裁决| 证据: _r274bma_resolve.py+6e102ba4+ticket progress_r274_addendum+processed/MSG-20260926-225x | "
    f"下轮: D: 卷归属裁决后自动续 s1；09-28 新 bar 链；10-01 月首轮三件套 [via bm-a]"
)
rb = open(RP, "rb").read()
if rb.endswith(b"\r\n") or rb.endswith(b"\n"):
    open(RP, "ab").write(line.encode("utf-8") + b"\r\n")
else:
    open(RP, "ab").write(b"\r\n" + line.encode("utf-8"))
print("round report addendum appended")
print("done", ts)
