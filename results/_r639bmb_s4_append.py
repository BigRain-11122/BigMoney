#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r639 bm-b S4 memory append: pit-ps +1 entry (false-alarm trio), CODELY r639 line.

Follows _r639bmb_pitgit_append.py convention (direct-write + reconciliation
line with byte count + md5 of the appended core, LF blob face).
"""
import hashlib
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PIT_ENTRY = (
    "- [2026-10-04 00:1x r639 bm-b] 共享记忆面「回归假警」三连坑（CODELY.md 差点被假 P0 修复实弹·字节 diff 当场定谳自愈零盘污）："
    "①PS Measure-Object -Line 不计空行（59 原始行=43 非空）——两计数口径混用=假行数漂移；"
    "②平台会话注入记忆的版面结构（Project/Reference 分节顺序）≠文件物理结构（物理文件 Reference 区含后追加的域拆件/r6xx 行）——按展示结构对文件=假缺行；"
    "③真值判据=字节级 git diff <旧> HEAD -- <path>（零删除=零回归）——共享 append-only 面回归警报必先 diff 定谳再动手修复（treasure_guard restore 门外的第二道闸）。"
    "How to apply：跨版本行数/结构比对一律 git diff 字节定谳；Measure-Object 计数注明口径（-Line 非空 vs .Count 原始）；勿以会话注入记忆的版面结构推断文件结构。\n"
)
core_bytes = PIT_ENTRY.encode("utf-8")
md5 = hashlib.md5(core_bytes).hexdigest()

ZRX = (
    "> 直写行（r639 bm-b·post-split convention direct-write）：+1 条（Measure-Object 空行不计×记忆展示结构≠文件结构×git diff 字节定谳先行=共享面假回归三连坑）"
    "·追加核 %d B（LF blob 面·md5=%s）·尾部整行追加·件内对账行为准。\n" % (len(core_bytes), md5)
)

pp = os.path.join(REPO, "research", "pit-ps.md")
with open(pp, "a", encoding="utf-8", newline="\n") as f:
    f.write(PIT_ENTRY)
    f.write(ZRX)

CODELY_LINE = (
    "- [2026-10-04 00:1x r639 bm-b] **D-19 共享决策面回归首观察+收养轮 S0 push-race 重放律**："
    "①FluxGroup docs/decisions.md origin tip 实测回退至 10-03 批前字节（r637 旧 sha 复现·D-20261003-01~04 行消失）——正法=水位随 origin 实况更新+已消费回执以轮报/台账为准不重诉+MSG 总控定谳（有意清理 vs 意外改写·MSG-20261004-0030）；"
    "②收养轮 S0=前体已推合并后，后继轮面对新 push-race（autofill 自 commit 亦自推 vs origin 前移）——r630 净路整重放零 UU 实弹（worktree merge→CAS push→reset --mixed→wtsync2 定向 checkout 复用·OLD_HEAD 换参即用·push 后 ls-remote 复核）；"
    "③共享 append-only 面回归警报必先字节 diff 定谳（本轮 CODELY.md 假警三连坑已入 pit-ps·差点假 P0 修复）。"
    "How to apply：D-19 水位遇 sha 回退=记录+上报勿静默跟随；收养轮 S0 直接复用 r630 净路勿发明新合并式；记忆面警报先 git diff 再动手。\n"
)
cp = os.path.join(REPO, "CODELY.md")
with open(cp, "a", encoding="utf-8", newline="\n") as f:
    f.write(CODELY_LINE)

print("pit-ps append: core=%dB md5=%s" % (len(core_bytes), md5))
print("CODELY r639 line appended: %dB" % len(CODELY_LINE.encode("utf-8")))
