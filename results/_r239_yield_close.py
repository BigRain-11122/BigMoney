# -*- coding: utf-8 -*-
"""R239 post-rebase closing: yield addendum (round report + CODELY correction) + heartbeat task fix."""
import io
import json

RR = "logs/iteration-loop/round_reports-bm-a.md"
addendum = (
    "\nR239 addendum (bm-a): S7 push 撞车 -> rebase 重放撞 15 件（T-77 票 + CODELY/LOCAL_FIRST + 12 共享态件）全按正典解："
    "**T-77 认领撞车裁定=bm-b 先到让路**（bm-b claim commit 09:42:01 早于我 09:47 claim，且 bm-b ae2e3379 已全量交付 "
    "T-77 四切片——路由表+crash-fuse+selftest 20/20+L2 台账+GPU 代码面；我的 09:39 pull 早于其 claim 落地=不可见窗竞态，"
    "我后到=按 fleet/README §4 让路：T-77 票保 bm-b claim+yield_note_r239 留痕、我的重复 progress 撤、我的 "
    "LOCAL_FIRST v2 重复稿弃（bm-b 版为正典）；bm-a 保留面=T-75 token 行协同（daily_report 消费面）+承接 "
    "GPU-FACTOR-LANE-PROOF 池翻面（bm-a-box GPU 物理依赖，bm-b 已留 pool entry 待 bm-a）**；CODELY=行级 union 零丢失"
    "（bm-b 1 条+我 3 条全保）；12 共享态件按分类器配方（autofill launches union cap50+last_tick 内 ts 整 dict；"
    "compute_audit history union 200 帽；regime transitions union+态取新；dashboard 对按 .json 孪生 generated_at 判侧取整字节"
    "（我侧 09:55:10 新）；7 snapshot 取新；scorecard 无墙钟键=按 post_review 面新鲜度取我侧 09:50:04 sweep）——"
    "解析验证过才写回，推前 4 提交行首口径毒化扫 CLEAN。resolver 工料=results/_r239_resolve_{t77,replay,mega}.py+poison_scan。\n")
with io.open(RR, "a", encoding="utf-8", newline="") as f:
    f.write(addendum)

CM = "CODELY.md"
corr = (
    "- [2026-09-26 10:1x] 勘误（bm-a R239 addendum·T-77 撞认领让路）：本日 10:0x 执行记录中「T-77 LOCAL_FIRST v2.0 路由表落地」"
    "一条系竞态窗重复交付——bm-b claim commit 09:42:01 先于我 09:47（我 09:39 pull 未见其票），bm-b 已全量交付四切片"
    "（ae2e3379），我按 fleet/README §4 让路撤回该面宣称；bm-a 保留=T-75 token 行协同+GPU-FACTOR-LANE-PROOF 池翻面承接。"
    "指针=fleet/tasks/T-2026-09-26-77-P1.json yield_note_r239。\n")
with io.open(CM, "a", encoding="utf-8", newline="") as f:
    f.write(corr)

HB = "fleet/machines/bm-a.json"
hb = json.load(open(HB, encoding="utf-8"))
hb["current_task"] = ("T-74 s2 full-history backtest batch next (prereg frozen) + GPU-FACTOR-LANE-PROOF pool flip "
                      "(bm-a-box torch probe, bm-b T-77 slice-4 physical dep) + T-75 Monday 15:45 first live-day report verify; "
                      "C-arm T-70/T-73 batch in-flight parallel; T-77 yielded to bm-b per s4 (their 09:42 claim first)")
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("addendum+correction+heartbeat done")
