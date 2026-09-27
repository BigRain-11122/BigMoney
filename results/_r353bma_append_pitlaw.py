# r353 bm-a: append pitlaw line to CODELY.md + round-report storm addendum (r185 discipline)
import os

line = (
    "- [2026-09-27 20:4x r353 bm-a] 坑律：resolver ts 探针键 normalize 字面 strip 陷阱"
    "（r345/r100/R350 三修后第五缺陷变体）——Python strip 只剥两端不剥中间，"
    "'as_of'.strip('_-')=='as_of'!='asof'→as_of 族整族漏探→探针降级到次新键值→假 tie"
    "（16-UU 实弹：daily_scorecard 报 tie 15:40:23，真 freshest=嵌套 traders[].forward_guard.as_of 20:38:48；"
    "幸 tie→HEAD 恰取对侧，修后 probe 复验确认）；正典=键名 re.sub(r'[_\\-/]','',k) 全剥再前配"
    "（SKILL.md 措辞 strip 是意图非实现，字面照抄=坑）；连带=js 包装件探针禁 json.loads 直吞"
    "（包装面 parse 崩→探针空→假 tie→与 .json 孪生杂交 r329 违例，dashboard_status.js 当场翻正同侧"
    "+终验孪生 generated_at 恒等）。指针=results/_r353bma_resolve.py+commit 5281397b。"
)
with open('CODELY.md', 'a', encoding='utf-8') as f:
    f.write('\n' + line + '\n')
print('CODELY.md bytes after append:', os.path.getsize('CODELY.md'))

rr = (
    "2026-09-27T20:4x | R353 addendum bm-a | push-cycle storm resolved: 16-UU vs same-window "
    "S6 chain of another machine (origin 97b8958e), classify 16/16 zero-UNKNOWN, recipes: "
    "snapshot take-new x11 (fresher 20:4x>20:3x), twin-regen REPORT json+md same-side :3:, "
    "js-wrapper + dashboard .json twin-coupled :3: (hybrid caught+fixed in-round), autofill "
    "launches 48+48 union cap50 asc, compute_audit history 201+201->202 zero-loss, regime "
    "history 2+2->2 | probe strip->replace fix live-fired (r353 pitlaw, CODELY.md appended) "
    "| pushed 5281397b"
)
with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(rr + '\n')
print('addendum written')
