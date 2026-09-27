# r377 bm-a: append the push-storm addendum line (UTF-8 safe path; the
# PS-console inline append mangled Chinese earlier this round -- r352
# family, fixed via _r377bma_report_fix.py).
import io

PATH = r"logs/iteration-loop/round_reports-bm-a.md"
LINE = (
    "2026-09-28T03:47:30+08:00 | R377 addendum bm-a (dept:工程+舰队) | "
    "两笔补录：①主行时间戳 04:20:00 系估算误差（实钟=本 addendum 时间戳，epoch 1790538432 "
    "= 03:47:12+08:00 双源同证），台账真值锚=git %ci；②push-storm+新工具首产实弹="
    "初始 push 被拒（origin 推进 bmb r357 addendum 4cdc710f：V2-P1 defer waiting·RAM serialize "
    "behind W2B+MSG-0350/0355 processed）→ pull --rebase 1-UU（autofill_state）→ "
    "**merge_lane_views.py resolve 首次生产实弹**（本同轮落地件自食其律：一行命令收口，"
    "复合键去重+字段并集 50 保 1 弃=cap50 语义、last_tick 03:40:01 取新、parse-verify 过、"
    "零手写 union）→ $env:GIT_EDITOR='true' rebase --continue 干净 → 同窗 reconcile --face "
    "autofill_state ZERO-DRIFT（4 源）→ PUSHED 4cdc710f..0da6c9df tip-verified；S7 双扫 "
    "orders 99/99 零未回执 + inbox 零入站 + 心跳 epoch int/T 分隔自证 | verify: resolve "
    "rc=0 + reconcile exit 0 + push FAST | next: 不变（①批3 C 族 ②B 面三源读数累计 "
    "③批1 撤共享写面 ④今日 09:15 T-91 s3 首标自动点火 ⑤V2-P1 finalize 守望 ⑥judge 分片 "
    "翻 ready 守望 ⑦council 两窗 09-29；next 5x=R380）"
)
with io.open(PATH, encoding="utf-8") as fh:
    text = fh.read()
assert text.rstrip().endswith("next 5x=R380 HANDOVER"), "tail unexpected -- abort"
with io.open(PATH, "a", encoding="utf-8", newline="") as fh:
    fh.write(LINE + "\n")
with io.open(PATH, encoding="utf-8") as fh:
    back = fh.read()
assert LINE in back, "read-back mismatch"
print("addendum appended cleanly")
