# -*- coding: utf-8 -*-
"""R265 bm-a S4 memory entry (ts-probe format-bias pit) + round-report collision addendum."""
import json

now_min = '2x'

CODELY_ENTRY = (
    '- [2026-09-26 19:2x] 坑律（bm-a R265·S7 撞车快照 ts 探针格式偏置面·r267 家族新参·E1 解后自捕）：'
    '**快照冲突解器的 ts 探针在混合格式候选上做字符串 max()=恒偏置——ISO T 分隔（2026-09-26T19:09:06）与空格分隔'
    '（2026-09-26 19:14:34）同池比较时 T>空格 使 T 型恒胜，与真实时间无关**；连带：确定性零墙钟视图'
    '（daily_scorecard 族）顶层无 generated 面，probe 递归读到的「最大 ts」实为内嵌引用面（post_review latest-run ts），'
    '两侧同字段同格式=比较仍真，但「探针读数≠墙钟面」必须先核字段身世再定「更新」语义；正律=①探针候选集先归一格式'
    '（T↔空格统一再比）②零墙钟件的新旧判定=同产者配对律（json 孪生 governs，html/md 同侧整字节）非 ts 探针'
    '③UNKNOWN 件禁默认取侧，逐件手工定性。指针=results/_r265bma_resolve.py probe_ts+手工定性段'
)

ADDENDUM = (
    '2026-09-26 19:2x | R265 addendum | S7 push rejected same-window (bm-b r268 close chain pushed first) '
    '-> single pull --rebase -> 18 UU (11 classified + 7 UNKNOWN hand-adjudicated per skill): '
    'resolver results/_r265bma_resolve.py = compute_audit history union 202|201->203 zero-loss ts-asc '
    '+ post_review.jsonl line-union 1039|1038->1067 zero-loss (re-derived-verdict family, house r188/r217 recipe) '
    '+ regime_state history 2|2 identity zero-loss (fields take mine 19:13:34 newer) '
    '+ daily_report pair r242 precedent (json twin generated_at governs, md same-side whole bytes, mine 19:14:33 > bm-b 19:09:04) '
    '+ 13 snapshots take-new by recursive-two-level ts probe (all mine 19:13-19:14 newer than bm-b 19:07-19:09) '
    '+ dashboard js whole-byte same-side R209 + daily_scorecard.html UNKNOWN -> hand-adjudicated :3 '
    'producer-pair consistency (deterministic no-wall-clock view, json twin governs) '
    '+ probe-bias note: T-form vs space-form ts string max() trap (daily_scorecard.json probe read nested post_review ref, '
    'not wall clock -- both sides same field so decision true; lesson -> CODELY.md S4 entry); '
    'parse-verify before every add (r185); rebase landed 0ad808a1 pushed clean; '
    'post-push double-scan orders 83/83 zero diff + inbox 0 + tree clean'
)

# CODELY.md append (CRLF, no BOM, trailing newline)
raw = open('CODELY.md', 'rb').read()
assert not raw.startswith(b'\xef\xbb\xbf')
text = raw.decode('utf-8')
assert CODELY_ENTRY[:40] not in text, 'idempotence guard'
if not text.endswith('\r\n'):
    text += '\r\n'
text += CODELY_ENTRY + '\r\n'
open('CODELY.md', 'wb').write(text.encode('utf-8'))
print('CODELY.md appended, size', len(raw), '->', len(text.encode('utf-8')))

# round report addendum (EOL mirrored)
rp = 'logs/iteration-loop/round_reports-bm-a.md'
raw = open(rp, 'rb').read()
sep = '\r\n' if raw.count(b'\r\n') > 0 else '\n'
out = raw if raw.endswith(sep.encode()) else raw + sep.encode()
out = out + ADDENDUM.encode('utf-8') + sep.encode()
open(rp, 'wb').write(out)
print('round report addendum appended')
print('S4+S7 OK')
