# -*- coding: utf-8 -*-
"""R248 bm-a: append one CODELY.md pit entry (attrition dual-list defect)."""
import io

P = "CODELY.md"
entry = (
    " - [2026-09-26 14:0x] 坑律（bm-a R248·gate_attrition 双列表消费链缺陷·r239 族新维·E1 收割期自捕）："
    "**追加型共享台账存在双列表名分裂时，行写进 misnamed 列表而消费面全读正名列表=静默丢失"
    "（实弹 3 批：CE-ADMISSION-B1/DIV_LOWVOL_P1/CN-REV-TILT-P1 落 `history` 而 bandit_queue/"
    "monthly_briefing/science_audit C4 全读 `entries`，缺陷自 09-25 15:06 存活跨 3 轮无红项——"
    "消费者不崩只是看不见）**；正律=①追加型共享台账落笔前先 grep 消费面读取键名（消费面定义正典"
    "列表名，生产者镜像之，勿凭记忆猜）②收割/对账门必须核「行对消费面可见」非仅「行已追加」"
    "③根修=生产者改写正确列表+孤行按 ts 升序零损归并（旧列表原样留档=append-only 零丢失）"
    "④收割门在池翻面前全查（门败=不翻=fail-closed）。指针=results/_r248bma_attrition_merge.py"
    "+results/_r248bma_cnrev_harvest.py+scripts/{cn_rev_tilt_p1,ce_admission_intake,"
    "div_lowvol_backtest}.py history→entries 修正段"
)
with io.open(P, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(entry + "\n")
print("appended", len(entry), "chars")
