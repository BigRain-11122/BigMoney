line = (
    "2026-09-29T10:12:00+08:00 | r423 bm-a addendum-2 (dept:eng+fleet) | SECOND push rejection (origin advanced to bm-c r208 merge-back 24a699548 in-storm) -> per fleet law terminal step (two rejections consumed: rebase-retry done once) + r207 bm-c storm precedent: ESCAPE BRANCH PUSH origin machine/bm-a-r423 (c078d48c: full r423 round incl. addendum-1 collision resolve + reconcile closure); "
    "NO force-push; r424 S0 FIRST ACTION = merge-back two-step per r419/bm-c-r208 precedent (single merge of origin/main into local, resolve regen faces take-origin-freshest, push main) — do NOT rebase-replay the co-located batch; "
    "fleet visibility: bm-a r423 content is complete and green on the escape branch, harvest-ready by any healthy machine per dead-session protocol if bm-a next round stalls"
)
with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line + '\n')
print('addendum-2 appended', len(line))
