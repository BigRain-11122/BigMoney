# r415 bm-b: HANDOVER 5x check line + round-report push addendum (file-face, FFFD assert)
import io

# ---------- 1) HANDOVER.md: insert r415 5x check line at top of increment entries ----------
H = 'research/HANDOVER.md'
LINE = (
"> bm-b round 415 五倍数核对（2026-09-29 08:2x）：增量窗 r411-415=bm-b 侧（**W6 判决链全环收口+死会话收割双连+池面首次全清**"
"——r411 T-105 v1.1 桌钟接线+V3 点火解锁 rebase 双批；r412 死会话收割+V3 判定三件收口+T-105 v1.4 盘中柜；r413 W6-SCREEN 链收口"
"（screen-finalize 293 survivors/ledger 333139）+V3 池面双面翻清环+T-116 同窗三事件让路；r414 W6-JUDGE judge-0of1 合法 stale-takeover"
"烧 293/293+pit-89 shard 同轮翻+town.html 十一楼 ETF-ops；r415=本核对轮 **W6-JUDGE 判决链收口**=死会话 detached judge-finalize"
" pid2432 存续落地 w6_judge.json（293 judged·四面 G1 全零 0/293·E[FP]=14.65·G2 eligible 0·账本 333139+293=333432 线性）+pit-89 池双面"
" entry flip+intake 零面 w6_intake.json+48h CEO 钟起算 deadline 2026-10-01 08:14+CODELY 热冷整编 10089→8167B 零丢失）；"
"产物清单漂移=results/trial_labor_w6/{w6_judge,w6_intake}.json+results/_r415bmb_*（flip/intake/heartbeat/report/codely/resolve×2）+"
"池双面 done-flip+坑律九十四批（archive r415 窗批）；统一链 **333,432 实读**（live head=trial_labor_w6/w6_judge.json "
"trials_ledger.total；W6-JUDGE +293 入链后链头与 r414 shard 烧批同辙；**W1-W6 六波判定面全负定谳+V2/V3 链族全负=千人试用期机制级"
"结论零注册**）；**池 110 条=110 done·0 open·0 ready·0 waiting 首次全清**（TRIAL_LABOR 常设线=board 空+池清+零在飞判决批→"
"W7 起草窗=下一供给步·T-117 §9 open slice）；orders 122/122 双扫零未回执；smoke 26/26；指针：W6 48h CEO 报告窗内起草"
"（deadline 2026-10-01 08:14·W1-W6 合并口径延 CEO-REPORT-WAVE2-5 先例）·09:15 T-105 盘中首拍窗·10-01 月界三件套"
"（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门自动激活；下一 5x=bm-b r420。\n"
)
with io.open(H, encoding='utf-8') as fh:
    content = fh.read()
anchor = '> 2026-09-23 11:35 整理'
idx = content.find(anchor)
assert idx >= 0, 'header anchor missing'
hdr_end = content.find('\n', idx) + 1
content = content[:hdr_end] + LINE + content[hdr_end:]
with io.open(H, 'w', encoding='utf-8', newline='') as fh:
    fh.write(content)
with io.open(H, encoding='utf-8') as fh:
    back = fh.read()
assert LINE in back and '\ufffd' not in LINE
print('HANDOVER r415 5x line inserted OK')

# ---------- 2) round report push addendum ----------
R = 'logs/iteration-loop/round_reports.md'
ADD = (
"2026-09-29T08:3x | r415 bm-b addendum | push-time origin movement (bm-a r420 5-commit window + bm-c r204 landed during-round): "
"pull --rebase hit 20-UU same-window S6 twin faces -> classifier 10 classified + 10 UNKNOWN manual-qualified (REPORT/LIVE doc-twins "
"same-day idempotent regen r404 precedent; archive=append-union; _summary/scorecard faces=snapshot ts-probe) -> resolver "
"results/_r415bmb_resolve.py pass-1 (12 snapshots+js-wrapper+3 md-twins all take stage3 by deep-ts probe 07:57>07:47; "
"compute_audit history union 192 rows + regime_state union 2 zero-loss; CODELY memory-union) -> **pass-1 archive branch bug caught "
"by fail-closed probe** (startswith heuristic false-merged header-identical files -> my section lost -> assert rejected) -> "
"pass-2 results/_r415bmb_resolve2.py (line-level append-union fixed + CODELY 2nd integration: bm-a-side window batches 91/92/93 "
"re-archived verbatim per <=10KB hard line -> 10237->8167B, pointer line kept) -> 14 json faces parse-clean + js wrapper intact "
"-> rebase --continue (GIT_EDITOR=true) -> push LANDED 14c51c28f..4ee98f5d4. Post-push pool census: 110/110 ALL-done first "
"full-clear (six-wave TRIAL_LABOR + V2/V3 + all shards closed). | evidence: resolver outputs x2 + union assertions + push receipt "
"4ee98f5d4 + pool Counter(done=110) | next: unchanged (W6 48h CEO report window; 09:15 T-105 first-live; W7 prereg draft window open "
"per TRIAL_LABOR_LAW sec.1) [r415 bm-b addendum]\n"
)
with io.open(R, 'a', encoding='utf-8', newline='') as fh:
    fh.write(ADD)
with io.open(R, encoding='utf-8') as fh:
    tail = fh.read()
assert '\ufffd' not in tail[-len(ADD):] and '[r415 bm-b addendum]' in tail[-len(ADD):]
print('report addendum appended OK, no-FFFD')
