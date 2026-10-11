import io

p = 'state/queue/explore.md'
with io.open(p, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

row = ("| E17 | N2 U3 channel-1 alphagen RL 主考批（E16 census_holds=true 开窗承接·supply-floor chain leg-5："
       "T23 slice-1 POSITIVE-with-riders→E16 slice-2 廉价普查 holds=true〔obs family max |ICIR| 0.455>null p95 0.077·n_ok 200/200〕"
       "→本行=通道①「全新语法」RL 杠杆主考起草窗已开——DRAFT prereg research/N2U3_ALPHAGEN_RL_P1.md 已起草〔bm-b r889·"
       "T-19 gate hits=[] rc0·judged K=32 格 top-32 公式 core48 时序分位门消费·判线 g1_prime_v2/g2_registration_v2 共享库·"
       "D6≥0.7 拒收+协同池边际 IC 双面·出场轴③template_default 按设计测·种子提案带 20625000 族冻结窗 seed_admit_gate 实跑〕——"
       "下一窗=leg-1 RL 环 runner 建〔scripts/alphagen_rl_p1.py·表达式树+协同池+PPO·selftest〕→冻结门五条件〔N2-W15 先例〕→"
       "leg-2 训练探针→leg-3 完整训练→judged；负即止 RL 线〔EXCLUSION_BOOK 收口·G2 fallback〕） | "
       "research/N2U3_ALPHAGEN_RL_P1.md+results/alphagen_rg/CENSUS-2026-10-09.json+research/digests/DIGEST-20261010-t23-alphagen-paradigm-census.md | "
       "open（r889 bm-b 起草窗开+E17 登记+T-19 rc0） |")

out = []
inserted = False
for i, ln in enumerate(lines):
    out.append(ln)
    if not inserted and ln.startswith('| E16 '):
        out.append(row)
        inserted = True

if not inserted:
    raise SystemExit('E16 row not found - abort')

with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(out))
print('E17 inserted after E16. total lines:', len(out))
