# -*- coding: utf-8 -*-
"""r725 bm-c: prepend 5x HANDOVER row (window r721-725) after the file
header line. Python-utf8 safe path (PS string surgery pitfalls per pit-ps
law family; write-then-read-back assert)."""
import io

path = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\HANDOVER.md"
row = (
    "> bm-c round 725 五倍数核对（2026-10-08 03:5x·增量窗 r721-725 五轮）：增量窗 "
    "r721-725=bm-c 面（**复市 T-0 盘前值守主线（第 41-45 bm-c 连守轮·09:15 复市首交易日"
    "盘前零盲动）+QA 确定性包 41-45 连证（显式 --round 起步零误标连守）+S6 40 腿正典再生 "
    "streak 42-45 连营+孤儿探针共享名 UU 冲突判例（r724）+HQ-FEEDBACK 改进行（r724）+5x "
    "HANDOVER 核对（r725 本行）**——r721 值守轮〔QA 41st 包+inbox MSG-2026-10-08-0250 "
    "bm-a S5_01_ZT_PILOT 批认领处理归档+QA 标号自纠：缺省 state+1 误标 r722 双件"
    "→treasure_guard prescan 零命中→quarantine results/_quarantine/qa_mislabel_r721/"
    "→显式 --round 721 重产正标包零信息损失〕；r722 值守轮〔QA 42nd 包（显式 --round "
    "722 起步=零误标·r721 教训当轮持律）+S6 40 腿正典克隆 streak 42〕；r723 值守轮〔QA "
    "43rd 包+S6 40 腿 streak 43+S0 轮首脏 4 定向吸收 c960d3523〕；r724 值守轮〔QA 44th 包"
    "+S6 40 腿 streak 44 @407 条+S0 撞 1-UU（results/_orphan_face_probe.json 他机 "
    "03:08:12 vs 本机 03:35:19 共享名探针对撞）→treasure_guard restore-class rc0"
    "→live-wins newer-ts take-theirs→rebase rc0 86b7cb21f（进件 bm-a r858/859 "
    "W16-SCREEN enroll）+inbox MSG-2026-10-08-0330 bm-a W16-SCREEN 座位声明处理归档"
    "+HQ-FEEDBACK F-20261008-02 改进行（孤儿探针共享名 UU 税→per-machine 后缀建议·集团普"
    "适律）〕；r725=本核对轮〔5x HANDOVER 本行+QA 45th 包（qa/smoke-r725.md 5/5"
    "+equity-curve-r725.png 66,274B·determinism=True·93 trades·equity 1,017,839 冻结恒等"
    "·market_clock cell=ORA·latest_panel_bar 2026-09-30 金周合法·显式 --round 725 FIRST "
    "TRY）+S6 40 腿正典再生 Tools/_r725bmc_s6.py（r724 正典克隆·40/40 rc0·dualrun "
    "ZERO-DRIFT streak 45 @407 条·cta_p1_paper bar-门控诚实 no-op〔panel cutoff "
    "2026-09-30<paper_start 2026-10-08→今晚首 bar 轮自动接线〕·fund_premium pre-15:30 "
    "no-op→今日 15:30 bm-c 车道首采·全 lane 守卫诚实 no-op）+S0 干净窗（轮首脏 5+轮中 "
    "dispatcher churn=定向吸收 93530f5ad+3695d8aae→rebase up-to-date 零 UU→push 送达）"
    "〕。维护面全窗：smoke 49/49 链；orders 51 disk 双扫零未回执链（176 ack）；DEC "
    "EE659451/ORD 17accc40 双水位 UNCHANGED 链（算法对按 r716 钉·hex-case 归一 r711 律）"
    "；SAT 活 rc0 链；attrition CLEAN 链；四件套绿链（pin=5+watchdog+双爪）；孤儿面=1 链"
    "（本机常驻 ComfyUI 服务面·CEO 私产·只读披露不击杀）；idle NOT-GREEN 链（RAM "
    "~15-19%<40% 常驻 ComfyUI·idle_rounds=0·--worked 申报）；compute_audit 旗标 "
    "supply_gap/supply_floor 照录=池 ready 1〔W16-SCREEN owner bm-a〕<floor 3·处置在册"
    "=引擎常供线+今晚盘后 bar 面天然候选供给〔never-dry 常设律·禁手工代烧〕。指针：**今晚"
    "盘后面（≤10-08 23:59）=数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce"
    "+fund_premium 15:30 首采（bm-c 车）+QDII watch 长假差分重跑+CTA_P1 首 bar 自动接线"
    "+首 marks 验证（S6 cta_p1_paper 腿·验证=marks 1 行+state trial-live+复利恒等）**"
    "+O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00）+O-2245 OSS gate 续作（≤10-16）"
    "+cloudF 收取窗 ≤10-14+月界首考 10-31；下一 5x=bm-c r730。 [via bm-c r725]\n"
)

with io.open(path, encoding="utf-8") as f:
    lines = f.readlines()
assert lines[0].startswith("# Bigmoney"), "header line missing"
assert not any(l.startswith("> bm-c round 725 ") for l in lines), "r725 row already present"
lines.insert(1, row)
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)
with io.open(path, encoding="utf-8") as f:
    back = f.readlines()
assert back[1].startswith("> bm-c round 725"), "prepend failed"
assert back[2].startswith("> bm-c round 720"), "r720 row displaced"
print("HANDOVER r725 row prepended OK; total lines=%d; L2 head=%s"
      % (len(back), back[1][:60]))
