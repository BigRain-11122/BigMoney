# r670 bm-a: append THEME-JUDGE-P1 consumption row to TRIAL_GRAMMAR_LEDGER.md (PERSIST-row format)
P = "research/TRIAL_GRAMMAR_LEDGER.md"
row = ("| THEME_JUDGE_P1（题材环 R4 判决批·消费带声明行·非生成波次·T-2026-10-04-167-P1/"
       "O-20261001-2103 R4 判负线+O-20260928-1522 CEO 研究导向律·E28 集群分层首判） | "
       "prereg freeze r667 (research/THEME_JUDGE_P1.md·banned_direction_gate ADMIT rc0 BAN-04 词面"
       "改写'全父代数变体族暴露'·出场轴①策略自有出场 M02 双件门·证据截止 2026-09-22 双口径披露) | "
       "judged cells 4（{FULL,SOLO} 分层×{x1,x2} 成本·N_rows=8,004）+ same-mask random-ignition "
       "nulls 4×2000（K=2000·rng([20585000,k]) 子流律）+ sens 16（bl{0.75,0.80,0.85}×rb{1.20,1.25,1.30}"
       "去冻结格）+ LOO 796 折 + D6 real 复核 | —（冻结格非生成语法·census v0.3 sha16 51b1b8226afc74b1 "
       "恒等锚·裸码+前缀双胞胎去重 1,919→1,822〔−97〕·D6 max|corr| 0.3682<0.7 ENGULF-CE-01 公共族·"
       "48/48 双胞胎价格恒等） | nulls=20585000（新带 [20585000,20587000)·disjoint 实证·registry 一行） | "
       "serialized r667 freeze (s2 双跑字节恒等 01f644a2ce4210ea)·consumed 2026-10-04 10:19→10:26 "
       "(bm-a r670·首烧 10:00:31 死于 runner ci 语义双轨 bug=fuse 确认·修复+守卫腿后 10:19:01 重燃 87s "
       "26workers 全绿·judgment single-shot·工程修复留痕=prereg §7 首行)；judgment 读数=**judged_negative "
       "族级诚实关线**（主面 TJ-SOLO-x1 Sharpe 0.2735<null μ 0.3734·skill_line 1.3172 未达·g1/g2/DSR "
       "×4 全 fail·PBO 0.4286·t 1.19<3·12/20 点火年 cohort 负边→撤回判定成立·famous 幸存者溢价塌缩 "
       "rest 边 −4.64pp） | same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4·judgment single-shot·"
       "深破线 bl=0.75 变体读数已披露=改道候选面须另立预注册) |\n")

raw = open(P, "rb").read()
assert raw.endswith(b") |\n") or raw.endswith(b"\n"), "unexpected tail"
assert b"THEME_JUDGE_P1" not in raw, "row already present"
with open(P, "ab") as fh:
    fh.write(row.encode("utf-8"))
chk = open(P, "rb").read().decode("utf-8")
assert chk.count("THEME_JUDGE_P1") == 1
assert "judged_negative" in chk.split("THEME_JUDGE_P1")[1][:2000]
print("grammar-ledger consumption row appended, utf-8 self-check PASS")
