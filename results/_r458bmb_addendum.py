import io

# fix commit-hash references (rebase replay changed freeze hash)
for p, expect in (('logs/iteration-loop/round_reports.md', 2), ('state.json', 1)):
    s = io.open(p, encoding='utf-8').read()
    n = s.count('7880b0eff')
    assert n == expect, (p, n, expect)
    s = s.replace('7880b0eff', 'c88e7dea4')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print(p, 'hash refs fixed:', n)

ADDENDUM = (
    "\n2026-09-30T11:32:xx+08:00 | r458 ADDENDUM bm-b | push-collision note: r457 push was "
    "NEVER landed (r457 addendum resolved a UU batch but final push failed twice and round closed "
    "before retry) -> r458 push rejected (origin gained bm-c r265 SLOT-10 freeze steps1-5 + bm-a "
    "r467 W13 GENERATE/SCREEN receipts + JUDGE pool waiting lane=bm-b) -> rebase replayed THREE "
    "commits (r457 + r458 freeze + r458 closing) in two conflict batches resolved per "
    "bigmoney-conflict-resolve skill: batch-1 (r457 replay, 17 UU) resolver _r458bmb_resolve.py = "
    "REPORT/LIVE twins take-c 11:05 (origin bm-a r467 faces newer than my r457 10:45 replay face) "
    "+ 6 plain snapshots take-c + fundamental_status MANUAL take-m truth-wins (mine 10:55 post-fix "
    "rc0 full face vs origin 11:05 bm-a pre-fix-code rc2 error face {ok,updated,error} -- rebase "
    "carries my fix so truthful face = mine; r457 addendum precedent) + compute_audit history union "
    "203+205->207 + regime_state union 3+3->3 + marks jsonl union 18+17->20 sorted-by-ts + CODELY.md "
    "edit-union (my r457 reorg + origin r265 entry/r467 entry+2 pointers - origin 8 pointer drops "
    "per r467 r444-dedupe re-arch; 8917B <10KB no trim) ; batch-2 (r458 closing replay, 19 UU) "
    "resolver _r458bmb_resolve2.py = ALL take-m (my 11:18-11:27 faces newest: REPORT/LIVE twins + "
    "dashboard js+json group whole-bytes R209 + scorecard_v1/strategy_scorecard group + 6 snapshots) "
    "+ compute_audit union 207+201->208 + regime union 3+3->3 + marks union 20+20->22; freeze commit "
    "replayed clean (hash 7880b0eff -> c88e7dea4, refs in state/report fixed); r459 queue grown: "
    "W13-JUDGE pool entry waiting lane=bm-b (bm-a r467 assignment) + BP2 runner -- W13-JUDGE takes "
    "trial-labor standing-line priority per S3 order\n"
)

p = 'logs/iteration-loop/round_reports.md'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(ADDENDUM)
print('addendum appended')
