line = ('2026-10-01T23:04:00+08:00 | r541 缺记补注（r542 next 指针收口；r541 冻结窗会话在 closeout part-2 push 后退出、报告行未及落笔=非事故·r535 先例设计选择）'
        '| dept:研究/工程 | r541 实况（git 证据链 reconstruct）：W30 冻结=第十九枚引擎波 bm-a 第六枚自有波（614575701 22:19·band gate DUAL-SKIP ADMIT 回执 _r541bma_w30_band_gate.py：A=跳过 W29 公示投影 101_004..103_003〔r518 published=reserved〕·B=带内点跳位避 p4_batch1=41_000→41_001..41_200〔W26-B 重基族谱系〕·26 行 pre-W30 扫描+N3-R1 腿+探针簇 r335 腿；法典 §4 W30 行+W31+ 警示投影 A 105_004..107_003/B 41_201..41_400〔W31=bm-b 槽〕+N1_BANDS[30] engine_owner=bm-a+prereg PERPETUAL_N1_W30_PREREG.md）'
        '→tick 自燃 12/12 烧毕（22:15-22:29·audit.machine=bm-a）→closeout part-2（145ab1ea5 22:41·12/12 分片产物+S6 链再生+prereg §7/§8 回填+r541 工具件）→finalize 首跑撞 r518 同窗撞车（本机 22:29 prev=426,148 对 bm-c W29 finalize 22:34 origin 先达盲视=断链双头）=n1_w30_results.json EXCLUDED 诚实延至 r542 重 derive 终稿（430,548 链线性·K=63,920·r542 已落账）'
        '| 验证证据：git log r541 两 commit（614575701/145ab1ea5）+ls-tree W30 12/12 origin 完备+法典 W30 行在场 | 下轮指针：已由 r542 next 承接（W31=bm-b 槽观察·W33=本机下槽） [补记 via bm-a r543]')
with open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\r\n' + line + '\r\n')
print('appended r541 backfill line')
