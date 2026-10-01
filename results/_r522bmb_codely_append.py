# -*- coding: utf-8 -*-
# r522 bm-b: S4 pit-law append (two entries, memory four-question gate passed)
import os

entries = (
    "- [2026-10-01 21:5x r522 bm-b] 引擎点火 tick 崩溃丢 burn 记录=孤儿产物台账行永失坑"
    "（W25 shard-0 实弹·W10/W13 三处历史孤儿同窗回补）：saturation_engine 点火序="
    "Popen 分离子进程→内存 st['active'] 追加→tick 尾统一持久化——点火 tick 在持久化前"
    "死亡（20:27 tick 整行缺席=history 铁证）即 burn 记录全丢；下一 tick _reap_active "
    "只扫 st['active']（无记录=无行），队列物化按产物在场静默跳过该分片=台账行永失"
    "（科学面无恙：finalize 按产物计数 2,200 逐位吻合）。修法=孤儿对账腿 _orphan_rows"
    "（产物在场+台账/缓冲/在役三键集全缺席→补一条 reconstructed 行，"
    "orphan_reconciled=true·pid/started_at 诚实 None·elapsed/machine 从产物 audit·"
    "done_at 从 mtime）+tick 接线+selftest 1b 腿（幂等/在役/缓冲/owner 过滤五面）；"
    "实弹 4 孤儿（W10-7/W13-0/W13-1/W25-0）全补、shards_done_total 102→106。"
    "How to apply：一切「点火→异步探测完成」型引擎/守护（bm-c Tools/saturation_engine.py "
    "同源缺陷面待移植）完成对账必须能从产物在场单独重建台账行——burn 记录单点持久化="
    "遥测单点故障。\n"
    "- [2026-10-01 21:5x r522 bm-b] perpetual_faces_n1.py selftest 必须 --wave 缺省"
    "调用坑（W25 收口窗首犯·近误定性冻结面漂移）：runner selftest 腿「law band parity」"
    "断言 pf.N1_BANDS[2]==当前 A_SEED_BASE——腿为 W2 锚定设计（WAVE=2 缺省），"
    "--wave 25 selftest 即假红 AssertionError: law band A drift；正解=finalize 后验证"
    "一律缺省波调用 python scripts/perpetual_faces_n1.py selftest；--wave N 只用于 "
    "run/finalize/status 面。假红出现时排除序=先查调用面再疑 canon 漂移"
    "（r538 净路同族：宣称-实况一致律）。\n"
)

with open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write(entries)
print("CODELY.md size after append:", os.path.getsize("CODELY.md"))
