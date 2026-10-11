import io
entry = ("- 2026-10-12 01:5x bm-b r902 研究判决批收口单获（TRIAL_LABOR_W18 judge-finalize 类·TREASURE_PROTECTION_LAW §1）："
 "results/trial_labor_w18/w18_judge.json 入册——**入册=W18 仓位 sizing 轴完整配对块隔离首烧诚实全负判词**"
 "（188 判腿全 fail=47 完整块×4 face·g1_pass=0·0 onboard vs E[FP]_nominal=9.4 名义期望假阳·"
 "eligible_v2/reform/onboard 全 []=零晋升 lawful-zero；配对差分四 face 中位差全≈0"
 "〔eq +0.0001/cap20 0.0/inv -0.0005/del 0.0·IQR 0.03-0.08〕=sizing 配置轴对 W16 判负池零 Sharpe 中位迁移·"
 "§0 consumer (2) 负读数兑现=X 轴降权正统性活弹依据；SCREEN 892 落链 879,189〔152/692 存活·null p95 0.5116 带内〕；"
 "JUDGE 188 落分叉支 883,777→r902 追加式重锚 885,789+188=885,977 上活链"
 "〔r807 推前防分叉窗捕获·receipt _r902bmb_w18_reanchor_receipt.json·判负 looser-side 零翻案〕；voids LOWAMP-P1/P2 applied）"
 "——供给面结论=W18 不产候选·sizing 轴不产候选不重烧（same-grammar rerun FORBIDDEN）·下一波另起新轴或新入场源。"
 "finalize 落地 00:44:02（bm-b detached PID25060·~3.3 CPU-时）+runner selftest 24/24+§7/§8 一次定稿回填收口。\n")
with io.open(r'knowledge\TREASURE_REGISTRY.md', 'a', encoding='utf-8', newline='') as f:
    f.write(entry)
print('APPENDED')
