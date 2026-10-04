# r670 bm-a S5: round report append (UTF-8 binary-safe, GBK console bypass per pit-encoding)
import json

entry = (
    "watermark: green (red=false; satengine alive rc0 queue 0; pool floor 3/3 no breach -- "
    "THEME-JUDGE-P1 reburn IN FLIGHT daemon-claimed 10:19:01 pid=12372 after r670 crash-fix, "
    "fuse auto-clear code_changed 10:16:04 tombstone; fund trio NULLS bm-b canonical in-flight "
    "keepalive; W14 GM-parked; compute_audit flags=[supply_gap] observation = the reburn IS "
    "the supply, self-resolves on burn landing) | 2026-10-04T10:2x+08:00 | r670 | "
    "dept:策略+研究 | 当前活: T-167 s3 判决批烧录崩溃治愈+重燃 —— 首烧 10:00:31 死于空族装配断言"
    "（fuse 确认 10:05:36·拒重燃 4 次=设计面正确工作），根因=runner ci 语义双轨：task 生成发 k 起点 "
    "{0,100..1900}，_null_chunk 按 chunk 序号算 ks=range(ci*CHUNK,..) → 38/40 块 ks 空 → 装配 len==2000 "
    "断言炸；连带二坑：checkpoint 扫描器 startswith('chunk_') 永不匹配实际件名 TJ-*_chunk_*.json（断点"
    "续跑永不跳过），且若匹配则空毒块会被当 done 跳过=二次毒化。修法（零冻结量触碰：同 K=2000·同 "
    "rng([20585000,k]) 子流·ks 每层铺瓦 0..1999 恰一次）：ks=range(ci,min(ci+CHUNK,K)) + 扫描器 "
    "endswith('.json')+非空 ks 守卫；selftest 加腿 mini-pipeline ks 铺瓦==0..K-1（该腿本可拦此 "
    "bug）→ 16/16。验证件：AST 门+每层 2000-ks 铺瓦算术+盘上 2 健康 chunk_00 可复用+38 空块重算清单"
    "（_r670bma_fix_verify.py ALL PASS·含同 mask 跨层=冻结设计面勘注）。点火链实证：commit sha 变更→"
    "fuse 自动清除 10:16:04（code_changed 墓碑·autofill 日志原文）→ daemon claim OK 10:19:01 → "
    "C8 LAUNCH pid=12372（进程活性 CIM 双形实证·非空 frags 2=烧中） | S0: 两段净路（首段 churn-absorb "
    "8 daemon 面+rebase 4 commit 零 UU；后段 S6 产出吸收+S7 daemon claim-yield 面吸收×2·一次 CAS "
    "撞我自推 daemon 代推自愈=Everything up-to-date 实证）；S0.5 orders 双扫 153/153 零未回执"
    "（ls-tree 同口径集合比对）；D-19 双面 MATCH（decisions eb14b510/orders 82a0cef9·desktop 实径 "
    "fetch+show 原字节法·K: 缺席 S4U 窗） | S1 smoke 48/48 | S6: 39/39 腿全绿 rc0（dualrun "
    "ZERO-DRIFT streak45；compute_audit supply_gap 观察面如实携带；scorecard 6/28/7；CALL "
    "ORANGE_COOL sleeves4 activated0；LIVE-20261004 ORANGE cap50 + REPORT-20261004 faces5 + "
    "daily_scorecard + dashboard 全刷新；t35 PASS 0 pending；t24 22/22+晋升门 0/22 合法 "
    "NOT-ELIGIBLE；金周采集族全合法 no-op；fund-statement gate spawn 节流诚实 no-op（T-166 后台回填"
    "在飞）；live.paper 无新 bar 诚实腿过 r660 判例） | S7: 自愈 4/4（loop pin8 no-op+watchdog 重注+"
    "双爪 CR 归一重装）；attrition CLEAN 4 台账（healed 4 行注记照录）；T-167 票面 progress_r670 "
    "落地；state strict loads 自证 round_no=670 + 心跳 epoch int 1791080452 + clock T 分隔自证；"
    "orders 收尾复扫零未回执 | 记分: 2（可跑判决批 runner 崩溃修复+重燃=CEO 点名 T1 研究线判决批从死亡"
    "拉回在飞·finalize 就绪件=下轮首动） | 记账预算: 4/5（state+心跳+轮报+票面） | 本地未达 origin "
    "commit 数: 0（push_verify DELIVERED tip 24fcddb0e ahead=0 behind=0） | ceo-visibility: "
    "[当前活] 题材战法判决批烧录 crashed 后已修复重燃——上次崩溃是代码把 38/40 个随机基线块算成了"
    "空块（编号语义笔误），已修+加守卫腿+断点复用 2 健康块，烧批正在跑 [最近实物] scripts/"
    "theme_judge_p1.py 修复+selftest 16/16（10:1x）+ results/_r670bma_fix_verify.py [下个里程碑] "
    "烧批 ~10:29 落地 → judged finalize 出判决（题材战法线首个判决，<=48h 首节点 10-05 内）；"
    "fund 三族 V-NULLS 烧完 ETA 10-05 → finalize；10-08 开市窗 run-11/run-7 双跳\n"
)
with open("round_reports-bm-a.md", "ab") as fh:
    fh.write(entry.encode("utf-8"))
raw = open("round_reports-bm-a.md", "rb").read()
raw.decode("utf-8")
assert b"r670" in raw.split(b"\n")[-2]
print("round report r670 appended, utf-8 self-check PASS, tail line ok")
