"""W13 freeze transform: candidate DRAFT -> frozen prereg (W12 r444 precedent mirror).

Surgery only: (1) title de-candidated; (2) draft berth status line replaced by
FROZEN banner block (trigger re-verify + collision-3-check + checklist 1-10
replay + freeze-four-pieces); (3) adopter checklist section folded into banner
replay (W12 precedent); (4) body targeted updates: 13-source declare window,
sec-5.2 W12 SCREEN readout, sec-4 DSR live head, sec-9 freeze landing line.
All other body lines carried verbatim (byte-preserving inheritance).
"""
import io

DRAFT = r"research\TRIAL_LABOR_W13_CANDIDATE_SUMN_PREREG_DRAFT.md"
OUT = r"research\TRIAL_LABOR_W13_PREREG.md"

TITLE = ("# TRIAL_LABOR_W13 —— T-99 千人试用期大考 wave-13 波级预注册"
         "（MASS CANDIDATE TRIAL PROGRAM 第十三波·上行纯度门）")

BANNER = """> **【状态：FROZEN——已冻结·2026-09-30 07:2x·bm-a r461（起草机次轮自冻结·泊位先到持有：r456 03:5x 声明 commit 先落 origin〔c81d3cc2c〕·bm-c r251/r252 独立交叉验证撞带让路=r232 W10 先例同款·digest DIGEST-20260930-w13-sumn-yield-crossvalidation.md 在册；起草机次轮自冻结=W5 r247→r248/W6 r458→r459/W7 r254→r255 时间线镜像·首例起草机自冻结沿泊位先到持有条款兑现）。】**起草=bm-a r456（2026-09-30 03:5x·DRAFT 泊位声明·TRIAL_LABOR_LAW §1 常供律·锦标赛预先承诺姿态·DECISION_CHAIN v1.2 §四.7：下一批假设必须在上一批 verdict 落地前冻结——W13 泊位起于 W12 verdict 未落地窗〔03:56 < W12-JUDGE 05:22:37〕=合法·JUDGE 落地=泊位窗死线非前置·r228/r237/r447 泊位先例）。
> **冻结触发器活读复验（①条·冻结轮当场再读·活条件非历史条件）**：W12 全链消费落地 ✓（TRIAL-LABOR-W12-JUDGE judge-finalize 2026-09-30 05:22:37 exit 0·w12_judge.json 188/188 judged 零 G1 零 G2〔G1' 0/188·G2 0〕·w12_intake.json lawful-zero〔n_eligible=0·零 TRIAL-RSQR-* 袖盘〕·CEO-REPORT-WAVE12-20260930.md 落地〔48h 窗止 2026-10-02 05:22:37〕·attrition 两行 both faces guard CLEAN·TRIAL_GRAMMAR_LEDGER wave-12 行在册〔67c86c9cf4ef1ca7·raw 5,000→dedup 859〕·W12 prereg §7/§8 已回填 bm-b r447）∧ 判官零在飞批 ✓（池面机械核冻结轮实读 runnable_pool 全 entries done·零 ready 零在飞；INNOVATION-QUOTA-* 面=创新配额车道非 trial-labor 判官批·如实披露不构成 W13 判官在飞）。
> **撞批三查扩四查（冻结轮实读·r252 泊位四查律）**：job_list 零 open ✓+fleet\\tasks 零 open 票 ✓+git pull --rebase 冻结窗实读 Already up to date（HEAD=origin/main=85acbe73d）零 rival W13 冻结面 ✓+SEED_REGISTRY live-read 135 键 max=20325000（innovation_quota_w7_nlnl bm-c r255 注册·与泊位三键异值零精确撞带）✓+inbox 未读清零 ✓。
> **收编必做清单十项逐项兑现回放（冻结轮实读·draft 清单 ①-⑩）**：①触发器活读 ✓（见上横幅）；②轴系=十六元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUM=**282,175,488** 轴组（SUM∈{none,sumn20_lo,sumn10_lo} 三值轴·W12 94,058,496×3；镜像孪生 SUMN_q10≡SUMP_q90≡SUMD_q90 三写面语法不可达=零额外去重负担如实披露）✓；③排除簿=十三源（generate 时点实读·W1/MASS/W2-W12 十三源全落地在位）✓；④G-SUMN 探锚复验=**本轮冻结窗探针确定性重跑 SHA256 字节恒等**（rc=0·sha16 C2E5AAB0AC05906F==r456 首跑全摘 C2E5AAB0AC05906FB633DBFE0B1E87F475B4DBC16ED5DF91776D545055452F81·decidable 3,363/open 387/开窗率 11.11%/首可判 bar-idx==120 fail-closed 断言过/sumn10 368·10.57%/512 格 empty 409·非空 103/斜率拆分 387 up/0 down/镜像 XOR=0 全锚复现）✓；⑤seeds 三步律 ✓（135 键全盘零精确撞带+三键首元 142952215/350730315/901874307 互异 vs 全部既有基+null 派生带 20323500..20323699 与 unc 派生带 20324000..20324200 干净+rg 全仓命中=泊位/冻结文档+registry 占位注释〔全可分类·W7 r255 先例族〕；facts=results/_r461bma_w13_seed_law_facts.json；registry 三键注册同 commit〔R250 一步律〕）✓；⑥判读参照带 W1-W11+**W12 SCREEN 实读 p95=0.513208 随冻结横幅携带**（2026-09-30 05:00 SCREEN 落地·p50 0.5116 七波>0.50 延续·p95 带内 [0.50,0.52] ✓·survivors 188/859=21.88%·rsqr 轴富集面 rsqr10_hi 1.04× MISS/rsqr20_hi 0.32× 反富集 toxic=RSQR 先验屏级不兑现先例·W13 §5.1② sumn 富集预测的可证伪对照面）✓；⑦机制段五披露 (a)-(e) 随本冻结横幅携带 ✓（见下）；⑧judged 供结 declare 窗=十三源全在位 ✓（W12-JUDGE 已落地 05:22:37·generate 跑前仍重读 live prev 增量并入加权 declare）；⑨外源 digest 复用零重扫 ✓（O-1721 同源律·r234 digest+A158-TSGATE-P1/GATE-RECHECK 双源仓内件整体有效·09-29 外源面已由 bm-a T-102 lane-1/lane-4 覆盖）；⑩波级票 **T-2026-09-30-125** 开票+同轮认领（O-1730 即时律·W8=T-120/W9=T-121/W10=T-122/W11=T-123/W12=T-124 谱系）✓。
> **冻结步四件齐**：commit 冻结+SEED_REGISTRY 三键同 commit（20323000/20323500/20324000·R250 一步律）+波级票同轮开票认领+F-04 MSG 声明同轮（D-02 双信号：leg1=本 commit·leg2=MSG）。**冻结时点起本件烧批效力生效**（fill_ladder prereq_frozen 门放行·Tools/fill_ladder_catalog.json TRIAL-LABOR-W13-GENERATE 门控条目本轮预宣布〔三查镜像 W12 条目：prereg_frozen:<路径>+runner_exists+standing_no_judge_inflight+workers_plan+runner_args=['generate']〕·runner_exists 门待 runner 构建切片）；TRIAL_GRAMMAR_LEDGER wave-13 行=GENERATE 消费时落（W11 实践先例 8d03c4126）。**runner 构建切片=r446 手术坑律面**：prep/finalize/judge-prep 真数据 identity-face 三命令首跑=宣布 runner landed 前置律（bm-b r446 CODELY 新律）。"""

R1_OLD = "D=judged 供结变体面=generate 时点实读 declare 窗——**十三源**（W1-JUDGE+MASS judged+W2-W12-JUDGE〔W12 落地后〕）逐源 declare 不可得零行如实（**起草时点十二源在位=W12-JUDGE 未烧如实**；generate 跑前重读 live prev 增量并入加权 declare）。"
R1_NEW = "D=judged 供结变体面=generate 时点实读 declare 窗——**十三源**（W1-JUDGE+MASS judged+W2-W12-JUDGE）逐源 declare 不可得零行如实（**冻结时点十三源全在位=W12-JUDGE 已落地 2026-09-30 05:22:37 ✓**；generate 跑前重读 live prev 增量并入加权 declare）。"
R2_OLD = "；**W12 实读=收编机冻结步横幅携带**（起草时点 W12 screen 未落）。"
R2_NEW = "；**W12 实读 p95=0.513208 带内 ✓**（2026-09-30 05:00 SCREEN 落地·p50 0.5116 七波>0.50 延续·survivors 188/859=21.88%·rsqr 轴富集面 rsqr10_hi 1.04× MISS/rsqr20_hi 0.32× 反富集 toxic——RSQR A158 OOS 强先验屏级不兑现先例=W13 §5.1② sumn 富集预测 [≥1.3x] 的可证伪对照面如实注记）。"
R3_OLD = "DSR n_trials=活链头跨波不重置（跑时 live 读=W12-JUDGE 落地后链头·冻结步实读携带）"
R3_NEW = "DSR n_trials=活链头跨波不重置（跑时 live 读·**冻结步实读活链头=355,375**〔2026-09-30 r460 同窗活读=355,371+4 W6 verdict linear·judge 跑时再活读〕）"
R4_OLD = "— bm-a r456 起草泊位落地；收编窗口=冻结触发器①满足起至任何健康机认领止（泊位开放条款·W9 §9 先例）。"
R4_NEW = (R4_OLD + "\n— **bm-a r461 收编冻结落地 2026-09-30 07:2x**（起草机次轮自冻结·泊位先到持有·W5/W6/W7 时间线镜像）；"
          "触发器①活读复验 ✓+seeds 三步律 ALL GREEN+探针重跑字节恒等；下一切片=W13 runner 构建"
          "（scripts/trial_labor_w13.py·G-SUMN fail-closed 门+verbatim-import+r446 手术坑律真数据三命令首跑前置）"
          "→ GENERATE 入池点火。")


def main():
    src = io.open(DRAFT, encoding="utf-8").read()
    lines = src.splitlines()

    status_idx = next(i for i, l in enumerate(lines)
                      if l.startswith("> **【状态：W13 候选备货泊位"))
    checklist_idx = next(i for i, l in enumerate(lines)
                          if l.startswith("## 收编机复用前必做清单"))
    sep_idx = next(i for i, l in enumerate(lines)
                   if l.startswith("——以下正文="))
    body_title_idx = next(i for i, l in enumerate(lines)
                          if l.startswith("# TRIAL_LABOR_W13（候选骨架）"))
    assert status_idx < checklist_idx < sep_idx < body_title_idx, "anchor order"

    carry = lines[status_idx + 1: checklist_idx]  # lineage/main-evidence/(a)-(e)
    body = lines[body_title_idx + 1:]

    body_txt = "\n".join(body)
    for old, new, tag in ((R1_OLD, R1_NEW, "R1"), (R2_OLD, R2_NEW, "R2"),
                          (R3_OLD, R3_NEW, "R3"), (R4_OLD, R4_NEW, "R4")):
        assert body_txt.count(old) == 1, f"{tag} anchor not unique"
        body_txt = body_txt.replace(old, new)

    out = [TITLE, ""] + BANNER.split("\n") + [""] + carry + [""] + \
        body_txt.split("\n")
    out_txt = "\n".join(out) + "\n"
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(out_txt)

    # self-checks
    chk = io.open(OUT, encoding="utf-8").read()
    assert "候选骨架" not in chk, "candidate remnant"
    assert chk.count("FROZEN——已冻结") == 1
    assert "0.513208" in chk and "355,375" in chk
    assert "T-2026-09-30-125" in chk
    assert "收编机复用前必做清单" not in chk
    assert chk.count("## §7") == 1 and chk.count("## §9") == 1
    s7 = chk.split("## §7")[1].split("## §8")[0]
    assert "（空" in s7, "sec-7 placeholder discipline"
    print("frozen file written:", OUT)
    print("lines:", len(chk.splitlines()))
    print("banner ok, body replacements R1-R4 applied, self-checks PASS")


if __name__ == "__main__":
    main()
