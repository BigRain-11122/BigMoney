# -*- coding: utf-8 -*-
"""r440 bm-c: direct-write new pit into research/pit-git.md (post-split convention, r429/r427 pattern).
New pit: pre-align window in-flight re-staging swallows the checkout-aligned faces -> real merge UU.
Atomic write (os.replace per r614), LF-core md5 accounting, self-verify (r419 assertion-care).
"""
import hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT = os.path.join(ROOT, "research", "pit-git.md")

ENTRY = ("- [2026-10-04 02:4x r440 bm-c] 预对齐窗内再staging 吞 checkout 净面坑（r437 预对齐净路律窗内竞态实弹·r434 同日幂等再生态双机竞写族新触发面）："
 "`git checkout origin/main -- <交集共享面>` 预对齐（staged=origin blob）与 absorb commit 之间窗内，在途写手（satengine/autofill keepalive tick·或死轮遗留腿）"
 "重写工作树且其自身 git add 刷新 index——absorb commit 捕走本地新版本而非预对齐 origin 版→「双写同改动=平凡合并零冲突」前提破坏→merge 真 UU 17 面两连实弹"
 "（首跑盲信预对齐假设未预判 UU→merge --abort 全回滚损失一轮窗；重跑按 r434 逐面解=13 个 S6 可再生面 origin 新者胜〔本机 S6 链随后重生成·侧选谁赢皆分钟级自愈〕"
 "+3 个 bm-c 车道 daemon 面 ours live-wins〔r626d-② 他机属主钉律镜像：己方车道活写面禁取他机陈旧快照〕→全解 commit 零残留 push DELIVERED）。"
 "判别法=absorb commit 后逐面 `git rev-parse HEAD:<face>` vs `origin/main:<face>` 恒等断言——DIFF 即预对齐已被吞·merge 必 UU 预判成立。"
 "How to apply：预对齐窗后禁盲信平凡合并；merge 前逐面 blob 恒等断言；UU 即按「S6 可再生面 origin-newer-wins / 己方车道 daemon 面 ours-live-wins」两分法直接逐面解，勿 abort-重试循环。")

core_lf = ENTRY.encode("utf-8")
core_md5 = hashlib.md5(core_lf).hexdigest()
acct = ("> 直写行（r440 bm-c·post-split convention direct-write）：+1 条（预对齐窗内再staging 吞 checkout 净面坑·absorb 后逐面 blob 恒等断言判别律"
        "+UU 两分法〔S6 可再生面 origin-newer-wins/己方车道 daemon 面 ours-live-wins〕）·追加核 %d B（LF blob 面·md5=%s）·尾部整行追加·件内对账行为准。"
        % (len(core_lf), core_md5))

raw = open(PIT, "rb").read()
before_len = len(raw)
before_lines = raw.count(b"\r\n")
# file is CRLF throughout; ensure separator before append
sep = b"" if raw.endswith(b"\r\n") else b"\r\n"
payload = sep + core_lf.replace(b"\x0a", b"\x0d\x0a") + b"\r\n" + acct.encode("utf-8").replace(b"\x0a", b"\x0d\x0a") + b"\r\n"
new = raw + payload
tmp = PIT + ".tmp440"
open(tmp, "wb").write(new)
os.replace(tmp, PIT)

# self-verify (r419 assertion-care: read back, count, tail equality)
raw2 = open(PIT, "rb").read()
assert len(raw2) == before_len + len(payload), "byte delta mismatch"
assert raw2.count(b"\r\n") == before_lines + 2 + (1 if sep else 0), "line delta mismatch"
lines2 = raw2.split(b"\r\n")
tail_entry = lines2[-3].decode("utf-8")
tail_acct = lines2[-2].decode("utf-8")
assert tail_entry == ENTRY, "tail entry round-trip mismatch"
assert tail_acct == acct, "tail acct round-trip mismatch"
print("DIRECT-WRITE PASS: core %d B md5=%s; file %d -> %d B, +%d lines" % (len(core_lf), core_md5, before_len, len(raw2), 2 + (1 if sep else 0)))
