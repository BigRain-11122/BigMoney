# -*- coding: utf-8 -*-
"""r432 bm-c O-2030 protocol weld: iteration_prompt.txt byte surgery (three
guarded inline inserts, count==1 per anchor, partial-success honest report)
+ T-162 progress_r432_bmc append. In-line inserts only -> EOL form untouched."""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = os.path.join(REPO, 'Tools', 'iteration_prompt.txt')
TICKET = os.path.join(REPO, 'fleet', 'tasks', 'T-2026-10-03-162-P1.json')

INSERTS = [
    # (anchor, insert-after-text, id)
    ("（捕获律 O-20261002-2100·判决批 finalize收口步：本批有无新方法？有→append 方法论资产卡 knowledge/METHODOLOGY_ASSETS.md 并定向 add）",
     "（宝藏捕获律 O-20261003-2030·TREASURE_PROTECTION_LAW §1 五类收口步=判决 finalize/族炉收口/考面冻结/名单进出/方法论卡 append——各收口轮问「本批有无新宝藏？」有→knowledge/TREASURE_REGISTRY.md 出入记录 append 一行）",
     "five_collection_points"),
    ("水位触发检查（D-20260925-01④）：append 后 repo 根 CODELY.md >50KB=当窗即办热冷整编（流水型条目整编入 research/memory-archive/<YYYYMM>.md+行级零丢失校验，D-20260924-01 范式），不等周日周轮",
     "；一切清扫/归档/保留/回收/恢复类脚本动作前必过 python Tools/treasure_guard.py prescan（登记簿命中=硬拒 rc3 红线·禁绕过）+删除一律 quarantine 隔离区模式（results/_quarantine/ manifest·7 天观察窗）+扫后 assert manifest 恒等（TREASURE_PROTECTION_LAW §2·O-20261003-2030）",
     "sweep_hard_gate"),
    ("轮报告/轮账本行必带「本地未达 origin commit 数=N」一行（O-20261001-1108 送达核验门·N>0 跨两轮=红旗；commit 后 push+fetch+ls-tree 自证送达）",
     "；清扫/归档动作轮的轮报告必带「登记簿零命中」断言行（O-20261003-2030 §二.3 自证）",
     "report_zero_hit_assert"),
]


def main():
    raw = open(PROMPT, 'rb').read()
    text = raw.decode('utf-8')
    results = []
    for anchor, ins, wid in INSERTS:
        n = text.count(anchor)
        if n == 1:
            text = text.replace(anchor, anchor + ins, 1)
            results.append((wid, 'WELDED', len(ins)))
        else:
            results.append((wid, 'MISS(count=%d)' % n, 0))
    text.encode('utf-8')  # strict round-trip gate
    open(PROMPT, 'wb').write(text.encode('utf-8'))
    for wid, st, ln in results:
        print('INSERT %s: %s (+%d bytes)' % (wid, st, ln))
    welded = sum(1 for _, st, _ in results if st == 'WELDED')

    # T-162 progress append (weld owner first-chip record)
    with open(TICKET, encoding='utf-8-sig') as f:
        t = json.load(f)
    t['progress_r432_bmc'] = (
        "weld owner first chip r432: protocol welds in iteration_prompt.txt "
        "(five-collection-point treasure-capture line + sweep hard-gate line + "
        "report zero-hit assert line, %d/3 welded) + demo pack 6/6 (engine selftest "
        "re-verify, live hard-reject rc3 replay, clean-face rc0, quarantine manifest "
        "demo + identity assert, sweep-class mixed-set rc3) -> "
        "results/_r432bmc_treasure_weld.json + milestone tag "
        "treasure/g2-slot-tail-p1-20261003 (s4 first anchor) + POST_REVIEW s5 "
        "assertion wiring + registry milestone row. Remaining to 10-08: "
        "canon sweep driver (hot-cold) with embedded gate, S0-restore-class "
        "guard mode, per-runner finalize capture comments." % welded)
    with open(TICKET, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(t, f, ensure_ascii=False, indent=1)
    print('T-162 progress_r432_bmc appended')
    return 0 if welded == len(INSERTS) else 1


if __name__ == '__main__':
    sys.exit(main())
