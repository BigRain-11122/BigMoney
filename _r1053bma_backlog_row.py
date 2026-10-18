#!/usr/bin/env python
# r1053 bm-a: append bm-b unlock row 14 to fleet/backlog.md (multi-writer
# ledger: fresh-read-modify-write one-shot per the 2026-10-06 law).
# r1046 recipe piece 1/3: a claimable bm-b-lane row turns
# claimable_pool_lines 0->1 and breaks the idle fast-path gate at bm-b's
# round head, so its stalled loop (origin face frozen 07:54 -> 3h+)
# resumes the FULL path: S0 pull (gets O-20261018-0948-bm-a + v2) +
# S0.5 orders scan (P0 debt surfaces) + closeout push (receipt lands).
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, 'fleet', 'backlog.md')

ROW = (
    "14. \u3010BigMoney\u3011bm-b O-0948 rootfix \u91c7\u7eb3\u6536\u53e3\u89e3\u9501\u5355"
    "\uff08O-20261018-0948-bm-a \u00a71/\u00a73 \u56de\u6267\u7a97=\u672c\u673a\u62c9\u53d6\u540e 2 "
    "\u8f6e\u5185\u00b7bm-b bigmoney \u5faa\u73af\u9762 origin \u505c\u66f4 07:54\u21923h+"
    "\u00b7r1046 fast-path \u89e3\u9501\u914d\u65b9\u4e8c\u8fde\u00b7\u53d1\u4ee4\u673a=bm-a r1053"
    "\uff09\u2014\u2014\u4ea7=\u2460S0 \u62c9\u53d6\u540e\u6838 v2 \u91c7\u7eb3"
    "\uff08spawning \u884c\u65b0\u8bdd\u672f hard-cap 240min/silence-kill 25min \u5f15\u7528\u539f\u6587\uff09"
    "\u2461\u672c\u673a run_*.log TIMEOUT \u5386\u53f2\u6e05\u8d26\uff08\u603b\u6570+\u6700\u8fd1\u4e00\u4f8b\uff09"
    "\u2462MSG-20261018-<HHMM>-bmb-rootfix.md \u56de\u6267+O-0948 \u56de\u6267\u8282\u8ffd\u52a0"
    "\u2463\u5fc3\u8df3/\u72b6\u6001/\u8f6e\u62a5\u544a\u5e38\u89c4\u6536\u53e3\u2014\u2014"
    "lane=bm-b \u4e13\u5c5e\uff08\u672c\u673a\u65e5\u5fd7\u672c\u673a\u6e05\u8d26\u00b7\u4ed6\u673a\u4e0d\u53ef\u4ee3\u5de5\uff09"
    "\u2014\u2014\u53ef\u9886\n"
)

with io.open(PATH, encoding='utf-8') as fh:
    text = fh.read()
assert 'bm-b O-0948 rootfix' not in text, 'row already present'
assert text.endswith('\n'), 'ledger must end with newline'
text = text + ROW
with io.open(PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(text)
with io.open(PATH, encoding='utf-8') as fh:
    check = fh.read()
assert 'bm-b O-0948 rootfix' in check
print('BACKLOG-APPEND-OK bytes=%d' % len(check.encode('utf-8')))
