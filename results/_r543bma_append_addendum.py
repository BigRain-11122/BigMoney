line = ('2026-10-01T23:14:00+08:00 | r543 补表（mid-round observation superseded·r537 addendum 先例）| dept:研究/工程 | '
        '本报告行主体〔W31=bm-b 观察窗〕在 S3 时点（23:0x origin 尚无 W31 行）准确，同窗被超越：本机 S6 运行窗内 bm-b r525 已一步全链完成 W31（12/12 烧录 22:39-22:51·冻结 commit 22:57·finalize 23:00 origin·链头 432,748·K=66,120==prereg §0 投影逐字·W32=bm-c 槽交接·bm-b 下一自有波=W34）；'
        '本机推送撞拒 8 commit→rebase 冲突 14 件=全 r512 stale-base 派生面家族（本机 S6 于 pre-W31 基派生 vs origin post-W31 新版）→逐件取 origin 侧（--ours·非 union·r505 幂等面法）+r501 净路①（git 2.55 假拒绝 commit -C 手工落 pick）+③（update-ref 锚 main）；'
        '落定后在新鲜基（post-W31）补跑 3 个 host=bm-a 派生腿（scorecard/dscore/build_status·他机禁写面）消除 stale 显示；W33=本机下槽现仅隔 W32=bm-c 一座（bm-c 活跃 22:58/23:05 双证）'
        '| 验证证据: 400a6a359 落定 1 ahead 0 behind+host 三腿 post-W31 重跑+attrition CLEAN | next: W32=bm-c 观察勿重扫·W33=本机下槽（W32 行落地后接枪） [via bm-a]')
with open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\r\n' + line + '\r\n')
print('appended r543 addendum')
