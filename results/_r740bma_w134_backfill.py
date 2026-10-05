import io

P = 'research/PERPETUAL_N1_W134_PREREG.md'
raw = io.open(P, 'rb').read()
txt = raw.decode('utf-8')
eol = '\r\n' if '\r\n' in txt else '\n'

s7_old = '## §7 跑后实证。【占位·finalize 收口机械回填】'
s8_old = '## §8 批后复盘。【占位·跑前为空·终 7-T】'
assert txt.count(s7_old) == 1, 's7 anchor count %d' % txt.count(s7_old)
assert txt.count(s8_old) == 1, 's8 anchor count %d' % txt.count(s8_old)

s7_new = '''## §7 跑后实证。【finalize 收口机械回填·bm-a r740 2026-10-05 19:2x】
- finalize one-pass rc=0；12/12 分片 2,200/2,200 位取（A=2,000/B=200 算术检·分片名去重门 dup-free）；上游链 derive 复核 PASS（W1..W133 落账已在位·W133 total 688,611 为 prev 键头〔零在飞上游=键序前置净空·键序合法〕）；r708 预检三腿在场（回执 results/_r740bma_w134_preflight.json）：文件完备 12/12+finalize 输出缺位 + 活进程探针 v2 零命中（python.exe N1 runner 全扫·本窗全程串行执行 r738 律）+ 席位 MSG-2026-10-05-1857-bma-w134-seat 在 git 史（published=reserved r565 律·d6b64dddd 预推）=GREEN_FINALIZE_READY 先行。
- w134_only mu **−0.094033** sigma 0.248603（K=2,200）；pre-W134 池 mu −0.092875 sigma 0.244961（K=290,520）；merged mu **−0.092883** sigma **0.244989**（K=**292,720**=290,520+2,200 算术检·与 §0 投影恒等）。
- skill_line_v2 @n_eff 686,411 持平键位 688,611：1.1773 → **1.1774**（K-lift **+0.0001**·正负交替如实报正号）；se_mu 收窄链 W131 0.000458 → W132 0.000456 → W133 0.000454 → **0.000453**（@K292,720）。
- A 档 full_sharpe_p95 **0.3117** / p99 0.4690（A mu −0.085564）；账本 append 单发：prev 688,611 + 2,200 = **690,811**（单记·voids LOWAMP-P1/P2）。
- §5 断言对账：①|w134_only−merged|=0.001221<0.02 **PASS**（null_pool.mu_delta_w134_vs_w133ext 机器键）；②sigma 相对变化 +0.0114%<±10% **PASS**；③A p95 vs W133 键 0.3156 差 −0.0039<0.05 **PASS**；④K-lift +0.0001≤0.02 **PASS**——四断言全 PASS。
- audit.machine=bm-a·finalize_only=true；evidence_cutoff=2026-09-22 顶层+ cutoff_meta 双写在场。'''

s8_new = '''## §8 批后复盘。【占位·跑前为空·终 7-T】→ 回填 2026-10-05 r740
- 零异常零补获：freeze r739（W134 FREEZE 链 d6b64dddd·席位 MSG-2026-10-05-1857 r565 律先推·引擎 tick 19:05:16 自燃实证 shard-0 落地·r325 产物增长面）→分片连续烧全落地（12/12 @19:16:16 shard-11 实证·~1 分片/分钟）→finalize 本窗 r740 one-pass（19:2x·跨轮生命周期：r739 死会话冻结+点火→r740 尾吸收+收口·W132/W133 同构·r713 死会话尾部律）。
- 方法论捕获：无新方法论（测量加深面零新发现宣称）；宝藏捕获：无。
- 遗留：W135=表尾后下个自由号——**A 313_004..315_003 CLEAN / B 69_502..69_701 CLEAN 双 hops=0**（见本件 §5.5 投影·r739 gate 回执尾行·下波冻结窗必复核非镜像 r587 律）。'''

txt = txt.replace(s7_old, s7_new).replace(s8_old, s8_new)
io.open(P, 'wb').write(txt.encode('utf-8'))
chk = io.open(P, 'rb').read().decode('utf-8')
assert 'GREEN_FINALIZE_READY' in chk and '690,811' in chk and s7_old not in chk and s8_old not in chk
print('backfill OK, eol=', repr(eol), 'bytes=', len(chk.encode('utf-8')))
