# -*- coding: utf-8 -*-
"""r360 bm-a 5x HANDOVER reconciliation editor (R355 pattern commit 4f6bc885):
- L4 promote: new '最近核对=bm-a round 360(...)' line for the R356-360 window
- demote: current R355 line re-embedded as '上一次核对=bm-a round 355(...)'
- drop: R350 tail-text (preserved in git per standing convention)
- verify: exact-one-line replacement, read-back, byte-delta audit"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "research/HANDOVER.md"
lines = io.open(P, encoding="utf-8").read().splitlines()
assert lines[3].startswith("> 最近核对=bm-a round 355"), "L4 is not the R355 line: " + lines[3][:60]

old4 = lines[3]
# R355 core = strip its own demoted tail ('；上一次核对=bm-a round 350（' onward)
idx = old4.find("；上一次核对=bm-a round 350（")
assert idx > 0, "R355 demoted-tail anchor not found"
r355_core = old4[:idx]
# re-embed as 上一次核对 with the '最近核对=' prefix swapped
r355_prev = "；上一次核对=bm-a round 355（" + r355_core[len("> 最近核对=bm-a round 355（"):]

new4 = ("> 最近核对=bm-a round 360（2026-09-27T22:2x·对账增量=本窗 bm-a R356-360 行【bm-a R356-360 窗："
        "**发射前夜绿灯窗+控制面 W2B 池行静默丢失缺陷修复窗·产物清单零漂移·统一链 286,551 实读平持**"
        "（_r295bmb_ledger_scan.py 复跑：head=sina_construct_p1 prev=286546+5=286,551 与 R350/R355 基线恒等·"
        "INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0·GAP 19 项与既往核对同谱·本窗零批 finalize=W2-A bm-b 侧燃烧中未收割）——"
        "R356-358 绿灯维护三连（orders 96/96 双扫零未回执+decisions 零新动作面〔D-10 非 BigMoney 域·council C-01 我席 F-02 已出零重发·窗至 09-29 12:00〕+"
        "smoke 25/25+S6 30/30 rc=0 周日 no-op 家族零掩盖+T-91 armed 零漂移复验+fundamental 24h 全刷新诚实回退链 SUCCESS〔vendor-EM-fail→direct-UA-fail→sina_name_markers〕+"
        "MF/AH EM 阻断自愈道续窗+bm-b W2-A busy-not-dead r341 双证看护）；"
        "R359 控制面缺陷修复轮=W2B 池行被 bmb r340 网络死窗整件提交静默吞（git -S 实证 add f5822d92→remove 50ea26ef 零中间编辑·4 轮报告看护面描述已不存在行）→"
        "f5822d92 逐字恢复 commit 2a687a81 推送+语义零损失验（79 共享行字节恒等+仅 W2B 行与 updated_at 增）+MSG-2215 通知+classify_conflicts.py 本机孪生同步 selftest 26/26+"
        "S4 坑律 r359（网络死窗整件提交吞共享池行·看护面每轮实读复验）+CODELY.md 三十批热冷整编 14,690→10,210B ≤10KB 硬线；"
        "R359 addendum 双程推送风暴 18-UU per skill 正典解（快照深探针 take-new+孪生同侧耦合+账本 union+W2B d8_receipt 超集保形 r322 律+CODELY 批号 30→31 r176 让号）推 1d707d2a；"
        "R360=本核对轮：orders 96/96 双扫+decisions 零新行+smoke 25/25+post_review 3192 行 15 NO 全有同 id 后续 YES=零未决红+"
        "水位 py_low_board_clear 合法闲置+S6 30/30 rc=0 周日 no-op 家族零掩盖（+3 新 bar 门控腿合法跳）+"
        "池实读 80 条恒等（W2-A ready lane=bm-b 燃烧中〔bmb r341-344 燃烧+折叠窗·r344 close 22:04:52 收口〕+W2-B waiting 双 dep 已解一=D8 回执 d8_receipt 在案·dep-2 W2-A finalize 待）+"
        "T-91 发射前最终复验 ARMED（IntradayMarks Mon 09-28 09:25 Ready·周一 09:15 自动点火在位）】"
        "产物清单实况=runnable_pool 80 条（78 done+W2-A ready lane=bm-b+W2-B waiting dep-1 已录=与 R355 基线恒等）+纸盘/采集/维护链全绿+smoke 25/25）"
        + r355_prev)

lines[3] = new4
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

# read-back verify
chk = io.open(P, encoding="utf-8").read().splitlines()
assert chk[3].startswith("> 最近核对=bm-a round 360"), "read-back promote failed"
assert "上一次核对=bm-a round 355（" in chk[3], "read-back demote failed"
assert "上一次核对=bm-a round 350" not in chk[3], "R350 tail not dropped"
assert len(chk) == len(lines), "line count changed"
print("OK promote=R360 demote=R355 drop=R350-tail lines=", len(chk))
print("L4 bytes:", len(chk[3].encode("utf-8")), "| R355 core bytes:", len(r355_core.encode("utf-8")))
