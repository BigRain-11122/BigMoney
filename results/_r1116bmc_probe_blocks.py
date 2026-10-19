# r1116 bm-c: staircase-block ownership probe (chain-floor pin safety evidence, one-shot)
import io
T0 = io.open("results/_w278bmc_w277_frozen_face.txt", encoding="utf-8", newline="").read().replace("\r\n", "\n")
sc = T0.index("W251 起 staircase affects A")
blocks = {
 "b_title": ("engine_owner 行 265 注册在册（表尾", "owner per chain-order law）**】】）"),
 "b_prev": ("prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
 "b_band": ("（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
 "b3_a": ("entry rng seed=**622_501+j**", "；p=`BASELINE_P"),
 "b3_b": ("exit rng=**624_501+j**", "；p_exit=`P_EXIT=0.05`"),
 "b_claim_proj": ("probe W277+ 投影 A naive 624_501..626_500 CLEAN hops=0", "never transcribe r587**）"),
 "b5_projection": ("5. **W277+ 投影（probe 机证 leg4", "verify at W277 prereg，hop 链逐跳在 probe 回执。"),
 "b_gated": ("本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
}
print("staircase pos:", sc)
for name, (sm, em) in blocks.items():
    try:
        i = T0.index(sm)
        j = T0.index(em, i)
        print("%-14s %6d..%6d  staircase-inside: %s" % (name, i, j, i < sc < j))
    except ValueError:
        print("%-14s MARKER NOT FOUND IN T0" % name)
