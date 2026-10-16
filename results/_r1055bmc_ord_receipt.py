# -*- coding: utf-8 -*-
# _r1055bmc_ord_receipt.py -- O-20261016-2110 @bm-c receipt flip + V5 phase2 delivery receipt row
# Multi-writer law: fresh read -> single anchored replace + single append -> write; CRLF preserved.
import io, sys

ORD = r"K:\Fluxgroup\FluxGroup\docs\orders.md"

raw = io.open(ORD, "r", encoding="utf-8", newline="").read()

# --- edit 1: flip the O-20261016-2110 bm-c receipt (unique anchor) ---
old_anchor = "回执节：(bm-c: pending / bm-b: pending)"
new_text = ("回执节：(bm-c: DONE — CDN 已上传+HEAD 字节验证 2689431B 恒等 — "
            "https://tuanjie-ai-prd.tos-cn-shanghai.volces.com/mcp-upload/7764c438fc9745fc929afd660e7836c0/v1-sucheng-brake-final.mp4 "
            " [bm-c r1055 21:3x] / bm-b: pending)")
cnt = raw.count(old_anchor)
assert cnt == 1, "anchor count=%d (expect 1)" % cnt
raw = raw.replace(old_anchor, new_text)

# --- edit 2: append V5 phase2 delivery receipt row (single append at tail) ---
row = ("| 2026-10-16 21:3x | **【@bm-c 认领+交付回执】V5 修片 Phase 2 交付（17 镜 768P INT8 正片·18:0x phase2 解锁令）** | "
       "①**收片=bmc/i2v/v5redo/ 17/17 mp4 全名落位**（INT1-5/B01/C01/D01/D03b/D05/E01c/E03/E04/C04/R06/SIL1/SIL4·导演 winners 种子：INT1@9901/INT2@9904/INT3@9905/INT4@9907/INT5@9910/B01@9911）；"
       "②**交付契约全绿**：17/17 时长 5.17s（min_duration≥5.0 断言 PASS）+零音轨（音轨禁令合规·工作流零 audio 链）+441KB-1.8MB 字节全过；"
       "③**QC 三板全绿**：INT4 双轮廓红线 100% 复检=PASS（6 帧条带单轮廓零重影·9907 种子修复生效=s9908 dual-contour 缺陷消除）/CHK-E2 女主锚比对板=8.5/10 PASS（E03/E04/R06 骨相同人零漂移·R06 玻璃反射+碑文伪字=观察项非阻塞）/17 格总板 GO 17/17（SIL4 剪影风=V5-REBURN-SPEC L28「ID_F 剪影级」明文设计·非缺陷）；"
       "④B01 凿槌道具复核=总板帧级过（手未入画·道具风险面清）；歌名卡选位=INT2 正片帧已交付候装配站实定（TYPOGRAPHY-SPEC §一）；"
       "⑤产物=QC-v5redo-harvest-r1055-step2.json 判读收据+V5-QC-SHEET-17-r1054.jpg+4 张 QC 板本批上链；"
       "⑥delivery-watch v5redo-bmc-17i2v 契约 17/17 满足（死线 23:30 前达标）+poke 装配站；执行窗=bm-c r1055 | "
       "executed（收片+QC+上链+poke 本批完成·V5 装配站解锁） |\n")

if not raw.endswith("\n"):
    raw += "\n"
raw += row

io.open(ORD, "w", encoding="utf-8", newline="").write(raw)
print("orders.md updated: receipt flip + V5 row appended, new size=%d" % len(raw.encode("utf-8")))
