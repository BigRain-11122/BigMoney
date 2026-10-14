# -*- coding: utf-8 -*-
# r996 bm-c: V3 wave-1 receipt relay -> group-tree docs/orders.md (worktree append, zero main-tree touch)
import io

P = r"K:\Fluxgroup\FluxGroup\.wt-r996bmc\docs\orders.md"
ROW = (u"| 10-14 14:3x | **@bm-c V3 波 1 回执（O-20261014-1035 执行件·死窗吸收窗落账）** | "
       u"①波 1 6/6 签章镜全落盘：SIL1_v4b_s9021/SIL2_v4_s9018/SIL3_v2_s9013（存量）+"
       u"SING1_v2_s9013/SING2_s9014/SING3b_v4_s9019（本窗新烧·CDN 三条已传）——"
       u"mp4=mv0001-handover\\outbound\\krea2\\kf-demo-20261012\\bmc\\i2v\\·CDN 全索引=bmc\\I2V-URL-INDEX.md·"
       u"3 帧自检板=bmc\\wave1_qc_sheet_r996.jpg；"
       u"②波 1.5 SIL4 强度探针格 1/8 落盘（SIL4_probe_str04_s9011）后 runner 会话死+脚本盘面灭失"
       u"——波 1.5 余 7 帧+波 2 32 条待 runner 重建接续（bm-c 下窗首动作·GPU 现况=ComfyUI 活队列空模型常驻）；"
       u"③装配站（bm-a）波 1 六镜已齐=预览剪可装；"
       u"④软著 B/C 机 18 款复跑批 11:48 已跑（log 尾达 G28_ArrowOut）·完成核验+commit+push 随 bm-c 下窗收口 | relayed |\n")

raw = io.open(P, "r", encoding="utf-8", newline="").read()
tail_anchor = u"B站频道评论自动回复上线"
assert raw.count(tail_anchor) >= 1, "tail anchor missing"
assert u"@bm-c V3 波 1 回执" not in raw, "row already present"
# append after the last line, keep original trailing-newline shape
if not raw.endswith("\n"):
    raw += "\n"
raw += ROW
io.open(P, "w", encoding="utf-8", newline="").write(raw)
check = io.open(P, "r", encoding="utf-8").read()
assert u"@bm-c V3 波 1 回执" in check
print("ORDERS-RELAY-APPENDED", len(ROW), "bytes row")
