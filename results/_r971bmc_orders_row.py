# -*- coding: utf-8 -*-
# r971 v2: orders.md row append — base = ORIGIN blob (worktree face was a stale subset snapshot,
# zero-loss verified: no worktree-only rows). Writes origin-content + new row to worktree.
import io, subprocess, sys

GT = r"K:\Fluxgroup\FluxGroup"
P = GT + r"\docs\orders.md"
TAIL_ANCHOR = "资产产线第一波归笼：受众之声×2+census 落地+P1 双剧 v2 定稿"  # current origin tail row marker

ROW = ("| 10-13 17:3x | **@bm-a 导演席 V3 接力单**（O-20261013-1530 执行件·bm-c r971 链收割回执） | "
       "①**NEWKF 28 张试构图板已上链**（bmc/V3-NEWKF-TRIAL-BOARD_q88.jpg·7 镜×4 种子 28/28·672×384 jman 0.6·origin ae8bcb6）"
       "——构图对审零等待·圈选（镜+种）回执 bm-c 即升 1344×768 正档批"
       "②refire-2 终态：C04_v4 **9.0 PASS LOCKED**；C02_v6 4.0 FAIL（石缘辉光=帧烘焙·提示词 v5/v6 两连败判死）+"
       "R05_v4 6.0 FAIL（零尘两连败+木纹材质漂移=源帧核验排除帧烘焙·定性 i2v 模型面）→"
       "**夜窗帧级修法两帧派单**（C02/R05 源帧 Krea2 重制：去辉光·玄武岩材质锚+帧级尘粒·重制帧回传 bm-c 用已验证 motion 配方重 i2v）"
       "③bm-c 车道链毕（H3→Krea2 换模重启+ollama 35b 复 pin 完成）·详档=MSG-20261013-1730-bmc |\n")

blob = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", GT, "show",
                       "origin/main:docs/orders.md"], capture_output=True).stdout.decode("utf-8")
if TAIL_ANCHOR not in blob[-4000:]:
    print("TAIL-ANCHOR MISS on ORIGIN: re-anchor required"); sys.exit(2)
if "MSG-20261013-1730-bmc" in blob:
    print("ROW EXISTS on origin: skip (idempotent)"); sys.exit(0)
raw = blob if blob.endswith("\n") else blob + "\n"
io.open(P, "w", encoding="utf-8", newline="").write(raw + ROW)
print("ORIGIN-BASED REWRITE OK, total bytes:", len(raw + ROW))
