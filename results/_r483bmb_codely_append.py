line = (
 "\n- [2026-09-30 23:4x r483 bm-b] LOWAMP-P1 s1 冻结交付（CEO 即时令认领+开动同轮：T-132 认领 a78b69bc5·预注册冻结 0c100400f·"
 "正典=research/LOWAMP-P1.md·N_eff=2008·种子 20330000/20330500 同 commit 登记·closed_family open；"
 "让号残票 T-131-P1 已 void+superseded 指针=单活票防双认领）。坑律：预注册 §0.5 复述禁向词面/BAN 编号→"
 "banned_direction_gate 否证模式无否定语义=词面自撞 REJECT——写法=人工预读行只给机制对照结论，零禁向词零 BAN 字样"
 "（本窗实弹 REJECT→清洗→ADMIT exit0）。"
)
with open("CODELY.md", "a", encoding="utf-8") as fh:
    fh.write(line)
import os
print("APPENDED size=", os.path.getsize("CODELY.md"))
