# -*- coding: utf-8 -*-
"""r515 bm-c HANDOVER 5x check (515 = 5x multiple): prepend r511-515 window
check line after title. Local tree == origin (S0 behind=0), so local base is
current. Byte-surgery with EOL probe + self-verify assertions (r485 law)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "research", "HANDOVER.md")

CHECK = ('> bm-c round 515 五倍数核对（2026-10-05 05:1x·增量窗 r511-515 五轮）：增量窗 r511-515=bm-c 面'
         '（**金周看护主线+S7 集成窗 merge-mode 正典切换+N2-W15 JUDGE 舰队烧完收官面**——r511 S7 集成窗'
         '四坑律+merge-mode 终局〔PS 函数形参 $args 自动变量冲突坑/rebase 基座 checkout 删本轮新提交'
         '跟踪新件→集成期 resolver/手术脚本一律外置仓外 scratch+ROOT 硬编码/silent-git 包装器 stdout+stderr '
         '合流污染 git diff --name-only=UU 假数→冲突路径清单一律 python subprocess stdout-only 或 git ls-files '
         '-u/r420 heal 门双 Test-Path False 前置误触险情经 rebase --abort orig-head 全量恢复零丢失；'
         'merge-mode（bm-b r708 正典）替代 9-pick rebase treadmill=churn-absorb 前置→merge 22-UU 单停→'
         'canonical resolve 22/22（merge_lane_views 8 面+ts-newer-wins 8 面+twin-lock 4 面+jsonl 容差 '
         'union 2 面）→单 merge commit 过爪推送〕+N2-W15 judge 本机 daemon claim 5/7/8/9/10 在途烧录；'
         'r512 看护轮〔S6 38/38+N2-W15 judge-finalize 席位=bm-a F-04（04:1x 起）+fund-trio finalize='
         'bm-b canonical=双判决链席位他机·本机零席位动作定调〕；r513 看护轮+**S6 canon driver 落地**'
         '〔Tools/_r513bmc_s6.py=38 腿正典驱动·r514 copy 沿用〕；r514 看护收口轮〔S0 FF-only 合流 bm-b '
         'r708 波（churn-absorb bm-a r709/710 死会话面+13-commit 集成·零冲突零 UU）+bm-a 心跳 stale '
         '113-114min 第 2 连轮→bm-c stale-takeover derive O-2100 s2.4 四面+S6 38/38 CEO 面再生〕；'
         'r515=本核对轮〔S0 behind=0 零集成免手术+orders 154/154 双扫零未回执+D-19 MATCH+smoke 48/48+'
         'S6 38 腿+本行〕）产物清单漂移=Tools/_r513bmc_s6.py+Tools/_r514bmc_s6.py〔S6 正典驱动族〕+'
         'Tools/_r514bmc_s3.py〔S3 扫描件〕+CODELY.md r511 S7 集成窗四坑律行；零新产品行（看护窗零批 '
         'finalize 零判决零新链入=如实注记）；统一链 **648,730 实读平持**〔live head=results/mass_trial/'
         'w3_judge.json trials_ledger.total〔MASS_TRIAL_W3_JUDGE〕·本窗零入链·N2-W15 JUDGE finalize 未落'
         '〔bm-a F-04 席·≤10-12〕落地后按 judged-cells 口径前移〕；orders 154/154 双扫零未回执全窗维持；'
         'smoke 48/48 全窗维持；D-19 755428F8 MATCH 零消费全窗；池态=N2-W15 全 26 entries done〔SCREEN '
         '13+JUDGE 13 收官面·judge-finalize=bm-a F-04 席候收〕+FUND 三族 NULLS bm-b canonical keepalive '
         '在飞〔3 ready·r487 禁手工代烧〕+W14-GENERATE governance-parked〔O-2115 维持〕+403 总量 399 done；'
         'post_review 5,697 行 unresolved-NO=0〔38 NO 全被同 id 后续 YES re-derive 压制〕；下窗锚='
         'N2-W15 judge-finalize〔bm-a 席·≤10-12·r482 id-dup probe 先行〕+fund-trio finalize〔bm-b·'
         '10-05..09〕+D-20261002-05 selftest 席位窗 10-06 00:00+D-20261002-06 拆件收口窗 10-07 12:00+'
         'W3 下一波方向 CEO 裁定〔呈报已交〕+复市 10-09 数据链重挂〔G3〕+月界首考 10-31；下一 5x=bm-c r520。')

raw = open(P, "rb").read()
before_len = len(raw)
# EOL probe: find first line ending
i = raw.find(b"\n")
title = raw[:i]
eol = b"\r\n" if title.endswith(b"\r") else b"\n"
lines = raw.split(eol)
assert lines[0].startswith(b"# Bigmoney"), "title line not first: %r" % lines[0][:40]
assert lines[1].startswith(b"> bm-c round 510"), \
    "expected round 510 line at pos 2, got %r" % lines[1][:40]
assert CHECK.encode("utf-8") not in raw, "check line already present (double-run)"
new = eol.join([lines[0], CHECK.encode("utf-8")] + lines[1:])
with open(P, "wb") as f:
    f.write(new)
after = open(P, "rb").read()
assert len(after) == before_len + len(CHECK.encode("utf-8")) + len(eol), \
    "byte delta mismatch: %d vs %d" % (len(after) - before_len,
                                      len(CHECK.encode("utf-8")) + len(eol))
after_lines = after.split(eol)
assert after_lines[1] == CHECK.encode("utf-8"), "line 2 not the new check"
assert after_lines[2].startswith(b"> bm-c round 510"), "round 510 line displaced"
print("HANDOVER_OK eol=%r lines %d->%d delta=%d"
      % (eol, len(lines), len(after_lines), len(after) - before_len))
