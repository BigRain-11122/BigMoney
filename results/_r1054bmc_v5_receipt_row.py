# -*- coding: utf-8 -*-
# Append V5 phase1 receipt row to group orders.md (root repo, post-unwedge git path)
import io
ROW = "| 2026-10-16 18:1x | **【@bm-c 认领+进度回执】V5 修片重烧 Phase 1 烧毕（16:3x 派单·P0 2h 回执窗）** | ①认领=17 镜重烧单受理（V5-REBURN-SPEC 正身·V5-REDO-PACK-r1054.py lint 零否定 17/17·jman 0.8 骨相锚+ID_F_2001 女主锚按 spec §三·三段式表演全嵌）；②进度=KF 批 22/22 烧毕+480P INT4 trials 12/12（6 试镜×2 种子·总则⑥构图/坐姿验证）——V5-TRIALS-BOARD-r1054.jpg+manifest 本批上链；③卡点=phase1 原子推送双 FAIL（gate 输出 GBK 编码炸+bm-a :8790 载波事故窗）→本窗 root 仓解楔后 git 正道补落（O-20261016-1745 同窗治愈）；④ETA=trials 多模态过审出 winners→768P INT8 正片 17 条串行约 3.5-4.5h→bmc/i2v/v5redo/ 收片+QC 拼板+poke 装配站；执行窗=bm-c r1054 | in-flight（trials-QC→phase2 768P 点火） |\n"
p = r"K:\Fluxgroup\FluxGroup\docs\orders.md"
with io.open(p, "r", encoding="utf-8", newline="") as f:
    cur = f.read()
assert "V5 修片重烧 Phase 1 烧毕" not in cur, "row already present"
assert cur.endswith("\n"), "orders.md tail not newline-terminated"
with io.open(p, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
with io.open(p, "r", encoding="utf-8") as f:
    tail = f.read()[-120:]
print("APPENDED-OK tail ends:", tail[-60:])
