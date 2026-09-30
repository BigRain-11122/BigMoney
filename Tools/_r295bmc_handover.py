"""r295 bm-c HANDOVER 5x check (295 = 5x multiple): prepend check line onto
ORIGIN's blob (local copy is 40 commits behind; building on origin content
keeps next-round rebase conflict-free). Covers r276-295 with missed-window
backfill annotation per pit-79 precedent."""
import subprocess

raw = subprocess.check_output(['git', 'show', 'origin/main:research/HANDOVER.md'])
txt = raw.decode('utf-8', errors='ignore')
lines = txt.split('\n')
# find title line
title_i = 0
for i, l in enumerate(lines):
    if l.startswith('# Bigmoney'):
        title_i = i
        break

check = ('> bm-c round 295 五倍数核对（2026-10-01 01:4x·**r280/r285/r290 三窗 5x 漏核对补账=坑-79「指针写了≠执行」'
         '族再犯实录·本行一并覆盖增量窗 r276-295**）：增量窗 r276-295=bm-c 面（**Bonsai 机队试用呈报+D-19 集团决策'
         '消费步接线+LOWAMP 深扫证据+同仓退避窗主线**——r283/r284 T-99/T-100 Bonsai 机队分发试用实跑〔bm-c 3070 魔改 '
         '16GB tg128=40.52±1.10 tok/s 共驻态·官方 16GB「30+」宣称达标·D-20261001-02 已并卷 observe 维持·深度问答/'
         '复杂一审 14b 对照档·编码产线除外=T-70 判负在案〕+F-20260930-01 呈报落 GM 队列；r289 S6 38 腿驱动件 '
         '_r289bmc_s6.py 复用范式落地；r290 D-19 集团决策新鲜读接线〔git show origin/main 直读+内容寻址水位 '
         'last_decisions_sha〕；r291 BEHAVIOR_GUARDRAILS 锚校验〔U+2212 全角负号假阴坑律〕；r292 D-19 接线正典面'
         '〔迭代步+state 水位键在役〕+PS 管道转码假漂移坑律〔raw-blob 哈希律〕；r293 **O-2340 §三双腿执**'
         '〔PoolWorker schtask 核验+LOWAMP-DEEPSCAN-P1 本机烧 31.2s 2450 cells·冻结带邻域 121/121 robust·'
         'top cells w79-85 topN2 eq/invamp val +181-203% vs EW +58.7%·perm_p 0.0003-0.0015·x2 成本存活='
         'T-132 输入证据〕+D-41 材料 #2/#3 探针闭〔delist 全史 tx 3/3+ST 改名 derive·DATA_GAP 行翻面〕+'
         'T-131 撞号修复；r294 月首轮三件套〔science_audit/monthly_briefing/self_review〕+runner 多核普查 s1'
         '〔单核 65/多核 9·census 刷新 75〕+三坑律〔union 去重域/amend 撞劫/stale-takeover 梯子〕；r295=本核对轮'
         '〔同仓单执行体退避〔交互会话持 T-134 s2 cross_start 改造 WIP·未碰未载运〕+红牌诊断〔00:50 runnable-'
         'work-idle-low-cpu=LOWAMP-NULLS 烧批 00:47 起在飞加载窗采样+单核 runner 族=O-2355 整改面·bm-a r496 '
         's3 多核门已落〕+D-20261001-03 消费步 ack+post_review T-78-WINNER-WIRING 机制翻绿核验〔RW-1 前视修复'
         '重锚 0.862/1.5605 与本轮 smoke 逐位一致〕+S6 38 腿 rc0+push main 拒→machine/bm-c-r295 逃逸分支〕）'
         '产物清单漂移=Tools/_r289bmc_s6.py+Tools/_r295bmc_{s6,close}.py+results/_r295bmc_s6_log.txt+'
         'results/lowamp_deepscan_p1/〔r293〕+results/_r293bmc_probe_delist_st_sources.json〔r293〕+'
         'CODELY 坑律族〔r291 字符面/r292 raw-blob/r294 三条〕+archive 202609.md 各窗批节；统一链 **362,389 实读**'
         '〔bm-a r490 锚·W13-JUDGE 362,083 本地基+origin 在飞面〕；池 LOWAMP-P1 campaign 18 分片烧制中'
         '〔bm-a r496 0→2/18 done·harvest-flip 证实〕+PERPETUAL-N1-W2 12 分片队列；orders 133/133 双扫零未回执'
         '〔r293 起维持〕；smoke 47/47；指针：**T-134 s2 多核改造〔交互会话 WIP 落地核验→闭片或接管〕+T-131 仍候 '
         'GM 署名〔P1 禁认领〕+D-20261001-03 ack 窗 10-03 12:00+RW-5 外审复核 10-03→解冻供料线+Q4 marks 瘦身首 '
         'live-fire=10-08 假后首交易日+10-01~10-07 假期等待态轮一行收轮律**；下一 5x=bm-c r300。')

new_lines = lines[:title_i + 1] + [check] + lines[title_i + 1:]
with open('research/HANDOVER.md', 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(new_lines))
print('HANDOVER line prepended, origin base + 1 line, total lines', len(new_lines))
