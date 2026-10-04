"""r501 bm-c S7-close line append (delivery proof + close record).
Idempotent marker gate per r679 law."""
import time

REPORT = "round_reports-bm-c.md"
MARK = "r501 bm-c S7-close"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

LINE = (
    NOW + "｜" + MARK + "｜本地未达 origin commit 数=0（DELIVERED：round commit "
    "4d879f3c7→首推被拒〔origin 窗内进 5 commit：bm-a r700 churn absorb+merge 06d1828a7"
    "+bm-b autofill keepalive 22:54+bm-b r700 round 6bd42c5fc 23:01+merge 49284833d〕→"
    "merge 8519cc8cc 14-UU 同窗双 S6 再生面族逐面解〔_r501bmc_merge_resolve.py r698 血统："
    "10 JSON per-face ts-newer-wins 全 theirs-fresh 22:56-57>ours 22:51-52（bm-b r700 同内容"
    " regen 8 分钟更新鲜=正判）+3 md twins twin-locked to json side+token per-key union "
    "side_pick theirs=21 全 tie 零信息损失（三侧字节恒等探针 _r501bmc_token_probe2.py：bm-c "
    "machines 条目三侧相等 state_bytes=1961·r456 side_pick>0 断言满足）〕→push_verify "
    "DELIVERED tip 8519cc8cc ahead=0/behind=0·零强推零 --no-verify）｜收口实录：round "
    "commit 38 文件（簿记三件+探针族 7 件+S6 再生面族+MSG-2245 100% rename 入 processed）"
    "+merge commit 14 面解+close commit（本行+satengine daemon 双面 absorb）｜在册面行删除"
    "类=0（MSG-2245 rename 入 processed=移动模式白名单·无清扫无 quarantine·登记册零命中断言"
    "=不适用〔无清扫动作〕）｜轮产品计分：1（S6 38 面 CEO 面再生+看护证据面=实际文件改动·"
    "等待态轮如实计）"
) + "\n"

with open(REPORT, "r", encoding="utf-8", errors="replace") as f:
    body = f.read()
assert body.count(MARK) == 0, "close marker already present (idempotent gate)"
with open(REPORT, "a", encoding="utf-8", newline="\n") as f:
    f.write(LINE)
with open(REPORT, "r", encoding="utf-8", errors="replace") as f:
    assert f.read().count(MARK) == 1, "close marker must be exactly 1"
print("CLOSE LINE OK")
