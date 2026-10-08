# -*- coding: utf-8 -*-
"""r871 bm-a: capture-law closeout appends (METHODOLOGY_ASSETS E47 +
TREASURE_REGISTRY ledger row). Multi-writer shared ledgers -> in-file
fresh read-modify-write (r806 law), UTF-8, append-only."""
import io

ASSET = (
    "\n- **E47 REGIME 路由判别器验证批方法族（防抖校准成本-机会双面公式/Σd 符号直和分区恒等零陷阱/深熊 t+1 反弹多视界教训）**：proven（REGIME5-VALIDATION-P1 判决批）——"
    "①防抖层校准 N_CONF\*=argmin L(N)，L=C(N)+O(N) 双面：C=Σ翻面 dw×2×COST_X1、O=Σ错态日 |d_conf−d_raw|（固定态差表机读），翻面频发标签下机会成本增速远超成本节省→N\*=1 旗标实证；"
    "②任何 regime 路由 net 判据禁用 Σd_s 符号直和——状态分区下 Σ n_s·d_s≡0 恒等（条件均值望远镜），判据必用 |d| 路由值读法或差分对读法并 audit 披露读法选择；"
    "③深熊标签日 t+1 视界无负漂移（BEAR 全史 d=+0.97bp 实测·急跌反弹结构吞噬漂移·非防抖伪影）——阶段判别器验证批必须显式测多持有视界（t+1/t+5/t+20），单视界判负≠标签面无信息（CHOP −1.87bp p=0.0060/GRIND +18.3bp 结构性信号存在）。\n"
    "- 2026-10-08 08:4x·bm-a r871·REGIME5-VALIDATION-P1 判决批收口步（O-20261002-2100 捕获律）·append E47 REGIME 路由验证方法族（live 实证：results/regime5_validation/REGIME5-VALIDATION-2026-09-30.json）\n"
)

TREASURE = (
    "- 2026-10-08 08:4x bm-a r871 REGIME5-VALIDATION-P1 验证批 finalize 收口捕获：E47 REGIME 路由验证方法族入方法论资产（防抖 L(N)=C+O 校准/Σd 符号直和分区恒等零陷阱/深熊 t+1 反弹多视界教训）；主门 BULL/BEAR 方向性三面判负如实照报·判负≠放弃方向（CHOP/GRIND 结构性信号在案·修订窗=另批预注册·O-2215 回访 10-21）\n"
)

p1 = "knowledge/METHODOLOGY_ASSETS.md"
src = io.open(p1, encoding="utf-8").read()
assert "E47" not in src, "E47 already present (double append refused)"
if not src.endswith("\n"):
    src += "\n"
io.open(p1, "w", encoding="utf-8", newline="").write(src + ASSET)

p2 = "knowledge/TREASURE_REGISTRY.md"
src2 = io.open(p2, encoding="utf-8").read()
assert "REGIME5-VALIDATION-P1" not in src2, "treasure row already present"
if not src2.endswith("\n"):
    src2 += "\n"
io.open(p2, "w", encoding="utf-8", newline="").write(src2 + TREASURE)
print("appended: METHODOLOGY_ASSETS E47 + TREASURE_REGISTRY row")
