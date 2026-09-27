# -*- coding: utf-8 -*-
"""r325 addendum: push-collision receipt line append to round_reports.md (tail CRLF form)."""
import io, datetime

RR = 'logs/iteration-loop/round_reports.md'
rr = io.open(RR, encoding='utf-8', newline='').read()
assert rr.endswith('\r\n'), 'tail form changed'

ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M') + '+08:00'
LINE = ('- %s | r325 addendum bm-b | S7 push-collision receipt: first push rejected vs bm-a r325 (T-86 wave-2 roster FREEZE + S6 32/32 rerun + REBASE-RECEIPT faces) + bm-c r82 addendum same-window (independent 13th-batch CODELY archival = dual-13th-batch collision disclosed) -> pull --rebase 18-UU canon-resolved per bigmoney-conflict-resolve (classifier 12 auto + 6 UNKNOWN hand-adjudicated same-day-regen family; probe=results/_r325bmb_probe.py deep ts paths; resolver=results/_r325bmb_resolve.py 18/18): '
'autofill launches key-union 50+50->44 cap50 asc-r245 + last_tick take-inner-newer 13:20:02; '
'compute_audit history ts-key union 209+201->210 (collisions 200 content-identical per r322) + latest take-newer 13:14:57; '
'regime history asof-union 2+2->2 + top take-new updated 13:15:07; '
'CODELY memory-union 8659B (origin face + r320bm-a subsume-remove verbatim-in-archive + my 13th-batch idx line + my r325 entry; bm-c r82 entry kept); '
'archive 202609.md append-union both 13th-batch sections (r82 bm-c header no-##-prefix form + r325 bm-b; entries x-dup honest double-execution record); '
'13 measurement faces take-:3 probed-newer whole bytes (dashboard js whole-bytes R209 + json / fundamental / futures / heat / lhb / update_status / prospect _summary / scorecard_v1 / strategy_scorecard / daily twins same-side coherent / token_usage machines 5|5 key-set equal); '
'D-05③ conflict-marker check clean (whitespace warnings = CRLF face noise); post-resolve reparse all json strict PASS; '
'second push rejected vs bm-a r325 close-out (their own ledger face) -> pull --rebase clean zero-UU -> push landed 1b966bf2..b2d908a0; '
'process forensics: concurrent codely pids 13:19/13:20/13:24 = Minigame sibling loops (HomeWreck/BiuNiYiXia/PhantomEscapeGo/tick-navigator), zero Bigmoney concurrent round (round.lock single-instance held by pid 20380 13:10:02 = this session; 13:20 scheduled round correctly skipped); 13:21:01 worktree writes = my own rebase checkout (origin face + pick-2 partial merge), initial missing-file scare = probe path typo (no-dash vs script dashed REPORT naming) '
'| evidence: resolver receipt 18/18 + reparse strict + git log b2d908a0 == origin/main tip | 下轮: 同 r325 主行\r\n' % ts)

rr2 = rr + LINE
io.open(RR, 'w', encoding='utf-8', newline='').write(rr2)
v = io.open(RR, encoding='utf-8', newline='').read()
assert v.endswith('同 r325 主行\r\n')
assert v.count(LINE) == 1
print('addendum appended OK')
