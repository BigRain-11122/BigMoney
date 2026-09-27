# -*- coding: utf-8 -*-
# r335 bm-a: close-out artifacts (addendum line + one CODELY pitlaw entry)
import io, os

# 1) round report ADDENDUM line
addendum = (
    '2026-09-27T16:2x+08:00 | R335 bm-a ADDENDUM (S7 push-collision receipt, 28-UU canon-resolved one-pass rebase) | '
    'first push rejected (origin moved: bm-b r332 window {564e5594 tick-keepalive, 6ff89ddd tick-keepalive, '
    '538cf74e round-332 full S6 33-leg double-run} same-window, R322 family) -> pull --rebase 28-UU one-pass: '
    'classifier 12-classified + 16-UNKNOWN adjudicated as per-round regenerated measurement faces (R322/R330/r334 '
    'precedent); resolver results/_r335bma_resolve.py (r334 lineage + NEW CODELY.md memory-union face) -- '
    'CODELY direct-concat 7567+1120+603=9290B zero-loss byte-account / compute_audit (ts,machine)-union '
    '201|201->202 / regime asof-union 2|2->2 / x2 line-union 792|792->798 / 24 measurement faces take-mine '
    '(my chain 16:10:28-16:11:11 later than bm-b 16:08 window; producer-path probes primary, blanket+future-sentinel '
    'fallback) / twin daily_report json+md same-side PASS + dashboard js+json pair-law same-side PASS / '
    'autofill_state git-automerge == canon (launches 46 composite-key union zero-dup, last_tick 16:10:02 '
    'later-side dict) ZERO-FIX r334-precedent / intersection audit inter(29) == UU(28) + MSG-1552 identical-move '
    'both-sides (bm-b consumed + archived same window per their r332 commit msg) | two live catches in-resolver: '
    '(1) future-sentinel T-form bug -- ISO-T sorts after space-form (T 0x54 > space 0x20), r334 blanket sentinel '
    'raw-compare falsely excluded ALL T-form ts (futures_update_status ts=T-form, resolver v1 fail-closed assert '
    'caught, _norm_ts pos-10 normalization fix); (2) daily_report true index paths are DASHED '
    '"REPORT-2026-09-27.json" not compact "REPORT-20260927" (git show :2: refuses mismatched path form -- '
    'resolver paths must be byte-exact vs ls-files repr, not transcribed from spec memory) | pre-push amend window '
    'used (receipt in commit body) + push LANDED 538cf74e..c8f8f535 + post-merge smoke 25/25\n'
)
p = 'logs/iteration-loop/round_reports-bm-a.md'
s = io.open(p, encoding='utf-8').read()
io.open(p, 'w', encoding='utf-8', newline='').write(s + addendum)
print('addendum appended:', os.path.getsize(p), 'bytes')

# 2) CODELY.md one pitlaw entry (two catches, one rebase batch)
entry = (
    '\n- [2026-09-27 16:2x r335 bm-a] 坑律：**resolver 两坑（r335 28-UU 批实弹）**：①未来哨卫比较必须先归一位 10 分隔符（T→空格）——ISO-T 形排序恒后于空格形（\'T\'0x54>\' \'0x20），r334 哨卫原串直比会把一切 T 形 ts 误判「未来」剔除（实弹：futures_update_status.ts=T 形被剔、探针断言 fail-closed 兜住、_norm_ts 修）；②resolver 路径串必须与 ls-files 输出逐字节核对，禁按规格记忆转写——daily_report 真实 index 路径=带连字符 REPORT-2026-09-27（S6 规格面写的是紧凑 REPORT-YYYYMMDD），紧凑形 git show :2: 直接拒绝（实弹：daily_report 双件 blob() 失败回溯定位）。How to apply：新 resolver 先 python repr(ls-files -u) 对拍路径再动手；哨卫一律 _norm_ts 后比较。指针=results/_r335bma_resolve.py+round_reports r335 addendum+commit c8f8f535。'
)
p2 = 'CODELY.md'
s2 = io.open(p2, encoding='utf-8').read()
assert 'resolver 两坑' not in s2, 'idempotent guard'
io.open(p2, 'w', encoding='utf-8', newline='').write(s2 + entry)
print('CODELY:', os.path.getsize(p2), 'bytes; over 10KB line:', os.path.getsize(p2) > 10240)
