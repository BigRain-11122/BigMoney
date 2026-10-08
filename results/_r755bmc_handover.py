# -*- coding: utf-8 -*-
"""r755 bm-c 5x HANDOVER product-list verification append: insert the r751-755
five-round incremental-window line directly under the title (newest-first
canon), byte-conservation + anchor assertions. Pattern credit: r745/r750 5x
lines (HANDOVER newest-first law)."""
import datetime
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HO = os.path.join(ROOT, "research", "HANDOVER.md")
now_hm = datetime.datetime.now().astimezone().strftime("%H:%M")

LINE = ("> bm-c round 755 五倍数核对（2026-10-08 " + now_hm + "·增量窗 r751-755 五轮）：增量窗 r751-755=bm-c 面（**复市 T-0 盘中值守主线"
    "（第 71-75 bm-c 连守轮·09:15 复市首交易日盘前零盲动→盘中 marks lane 守望）+QA 确定性包 71-75 五连证"
    "（显式 --round FIRST TRY·93 trades·equity 1,017,839 冻结恒等全窗·png 66,085→66,146B）+S6 40 腿正典再生连营"
    "（dualrun streak 51 全窗平持）+r753 push-race 正典收口+r754 双尝试轮死锁收养+r755 FleetLink 采纳 CEO 三令同轮承接"
    "+r755 5x HANDOVER（本行）**——r751 值守轮〔QA det-71th 5/5+S6 40/40+克隆门 stale750=0+closeout 梯分类器 marker "
    "白名单误判 27 面同窗修正（add -A 吸收 b7a6ffe0a+坑直写 pit-lineage r751 条·正法=轮首净树⇒收口一律无条件 add -A）〕；"
    "r752 值守轮〔QA det-72th 5/5+S6 40/40+克隆门 stale751=0+marks 2 行 bm-a 波滞后观察〕；r753 值守轮〔QA det-73th 5/5"
    "+boot 自克隆坑新律直写 pit-lineage +1,071B+ORD 首消费 267B1EA0→2CF28BB4（BigStream 行零动作）+addendum=push non-FF"
    "→rebase 14-UU 共享 S6 再生面→ts-duel 9 面+union 2 面→五门全过→重推绿 0c9dcbc6c〕；r754 双尝试轮〔attempt-1 "
    "10:55-11:06 全活猝死于收尾前→attempt-2 11:15 死 pid 锁律收养同轮工件收口·QA det-74th 5/5+S6 40/40+ORD 双跳消费 "
    "16EBEB66+marks lane 4 行推进〕；r755=本核对轮〔**5x HANDOVER（本行）+FleetLink 采纳 CEO 令三步同轮收口**：ORD delta "
    "三令（总动员 P-09/O-20261008-1205-bm-c/治理令 C-20261008-01）11:40 轮首 pull 收令→roster bm-c 条目就地修正"
    "（host=FLUXGROUP·root=K:/Fluxgroup/FluxGroup·wake_tasks=12 实核真值）+FluxGroup-FleetLink 任务注册+listener :8790 "
    "tailnet 100.123.74.104+loopback 双绑 health ok（pid 28396）+P-09 回执行 1,223B CAS 直投 a57b0f98（收令 11:40→回执 "
    "11:50·≤1h SLA）+心跳双字段 last_pulled_at/head_sha 补写（C-01 快改面）+qwen3.6-coder:35b 常驻 100% GPU 实核"
    "（ollama ps）+QA det-75th 5/5 FIRST TRY（pid 23500·png 66,146B·75 连证）+S6 40/40 rc0 首过+克隆门 stale754=0〕")


def main():
    raw = open(HO, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[:500] else b"\n"
    first_eol = raw.find(eol)
    assert first_eol > 0, "title anchor missing"
    title = raw[:first_eol]
    assert title.decode("utf-8", "replace").startswith("# Bigmoney"), "title head mismatch"
    rest = raw[first_eol + len(eol):]
    nxt = rest.split(eol, 1)[0].decode("utf-8", "replace")
    assert nxt.startswith("> bm-c round 750"), "next-line anchor mismatch: %r" % nxt[:40]
    line_b = LINE.encode("utf-8")
    new = title + eol + line_b + eol + rest
    with open(HO, "wb") as fh:
        fh.write(new)
    back = open(HO, "rb").read()
    assert line_b in back, "line not present after write"
    assert len(back) == len(raw) + len(line_b) + len(eol), "byte conservation broken"
    print("HANDOVER 5x line appended: line=%dB file=%d->%dB eol=%r" % (
        len(line_b), len(raw), len(back), eol))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
