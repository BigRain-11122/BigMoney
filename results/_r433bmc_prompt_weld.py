# -*- coding: utf-8 -*-
"""r433 bm-c O-2030 protocol weld: iteration_prompt.txt byte surgery (one
guarded inline insert, count==1 anchor, r432 _r432bmc_prompt_weld.py pattern)
+ T-162 progress_r433_bmc append (weld remainder item 2 delivered).
In-line insert only -> EOL form untouched."""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = os.path.join(REPO, 'Tools', 'iteration_prompt.txt')
TICKET = os.path.join(REPO, 'fleet', 'tasks', 'T-2026-10-03-162-P1.json')

ANCHOR = "bm-b r606 治愈）"
INSERT = ("；**S0-restore 分类门（O-2030 焊面·r433 bm-c）**：一切 restore/重落/池面恢复类动作前必过 "
          "python Tools\\treasure_guard.py restore <path...>——登记簿命中或记忆/账本/轮报/票面类=rc3 硬拒"
          "（只可行级 union 或先摘录存旁），可再生工件（探针/daemon live-wins 态面/代码面）=rc0 放行")


def main():
    raw = open(PROMPT, 'rb').read()
    text = raw.decode('utf-8')
    n = text.count(ANCHOR)
    if n == 1:
        text = text.replace(ANCHOR, ANCHOR + INSERT, 1)
        status = 'WELDED'
    else:
        status = 'MISS(count=%d)' % n
    text.encode('utf-8')  # strict round-trip gate
    if n == 1:
        open(PROMPT, 'wb').write(text.encode('utf-8'))
    print('INSERT s0_restore_gate: %s (+%d bytes)' % (status, len(INSERT.encode('utf-8')) if n == 1 else 0))

    # T-162 progress append (weld remainder item 2 record)
    with open(TICKET, encoding='utf-8-sig') as f:
        t = json.load(f)
    t['progress_r433_bmc'] = (
        "weld remainder item 2 DELIVERED r433: S0-restore-class guard mode "
        "Tools/treasure_guard.py restore subcommand (LAW s2.4 classification: "
        "registry/memory/state-ledger/round-report/ticket-face/append-only-"
        "ledger classes = rc3 hard reject, line-level union or extract-aside "
        "only; reproducible artifacts incl. daemon live-wins faces & code = "
        "rc0). selftest 21->40 legs ALL PASS rc0; live-fire mixed-set rc3 "
        "hard reject + clean-set rc0 (read-only demos) -> "
        "results/_r433bmc_restore_guard_demo.json; protocol weld "
        "s0_restore_gate inlined into iteration_prompt.txt S0 law section. "
        "Remaining to 10-08: item1 canon sweep driver (hot-cold, embedded "
        "gate) + item3 per-runner finalize capture comments.")
    with open(TICKET, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(t, f, ensure_ascii=False, indent=1)
    print('T-162 progress_r433_bmc appended')
    return 0 if n == 1 else 1


if __name__ == '__main__':
    sys.exit(main())
