import json, time, datetime

repo = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/'
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec='seconds')

# state patch: reflect fallback truth
sp = repo + 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
st['verify'] = ('S1 smoke 47/47; S6 35 legs rc0; D-19 753F99E8 CONSUMED; orders double-scan EMPTY; attrition CLEAN; '
                'wild_route adoption-verified 393-cell byte-identity; PUSH RACE x2 during close window (origin moved '
                '16->+11->+6 within 8min, bm-b daemon push rate ~1/min): cycle1 integration LANDED (3305af3ca..6cdaadba9 '
                'incl W8 products 5/12), cycle2 round-commit b8881296b raced twice -> LEGAL FALLBACK branch '
                'machine/bm-c-r314 pushed (N=1 on main, work safe on fallback)')
st['next'] = ('(S0 FIRST) integrate machine/bm-c-r314 into main at round start (fetch before fleet wakes backlog; '
              'cherry-pick b8881296b via CAS net path r314 CODELY entry; conflict recipes: derive=take-origin, '
              'ledger=history-union, lane-state=restore-first); then (a) W8 12/12 products -> finalize --wave 8; '
              '(b) T-134 s2 next-candidate rescan; (c) WM lane-blind red-flag backlog candidate')
st['last_round'] = ('2026-10-01 r314 bm-c: triple-crash adoption + CAS integration cycle1 landed (W8 products 5/12 '
                    'on origin) + round commit on machine/bm-c-r314 fallback after push race x2 + S6 35 legs rc0')
st['heartbeat_epoch_utc'] = int(time.time())
st['clock_read'] = now_iso
st['last_ts'] = now_iso
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# heartbeat patch
hp = repo + 'fleet/machines/bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['verdict'] = ('WM red = lane-blind stale signal (5 ready ALL bm-b-lane STOCKFURN, bm-c takeable=0, W8 12/12 done, '
                 'GM waiver O-1612); cycle1 integration landed N=0; round commit raced x2 -> machine/bm-c-r314 '
                 'fallback (N=1, next-round S0 first action)')
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now_iso
hb['last_seen'] = now_iso
hb['updated_at'] = now_iso
hb['next_milestone'] = ('next round S0: integrate machine/bm-c-r314; then W8 finalize at 12/12 products + T-134 s2 '
                        'rescan; window <=24h')
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# round report addendum (r314 附 line, r311 附 precedent)
rp = repo + 'round_reports-bm-c.md'
line = (
 now_iso + '｜r314 附｜送达核验终态修正（O-1108 §二.1 如实登记·禁静默收场）：close 窗 push race x2——cycle1 整合已落地'
 '〔3305af3ca..6cdaadba9·含 W8 产物 4 件→origin 5/12·N=0 窗口达成〕后 origin 8 分钟内再进 17 commit（bm-b daemon ~1 push/min），'
 'cycle2 round-commit b8881296b 两次被拒→**法定 fallback 分支 machine/bm-c-r314 已推**（19 冲突全解：'
 '7 派生面取 origin/2 台账 history-union〔science_audit 16+2·self_review_ledger 1+1〕/10 单块面按类解·marker sweep CLEAN）；'
 '终态=main N=1（悬挂件显式登记）+工作件全量安全在 fallback 分支；**下轮 S0 第一动作=整合 machine/bm-c-r314**'
 '〔先 fetch 后动笔·CAS cherry-pick 净路·冲突配方已留 results/_r314bmc_resolver2.py+_r314bmc_ledger_union.py〕；'
 '本机零丢失面=cycle1 主产出（W8 5/12+月度三件+收编件）已在 main，cycle2 面为轮收尾簿记+state/heartbeat/报告本体｜'
 '经验行：fleet 高频推送窗（≥1 push/min）内 close 段 push race 为常态——轮会话收尾 commit 宜在 S6 后立即做且预期一次 race；'
 '本窗两次 CAS 整合均零 orphan 零 force-push'
)
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')
print('R314-ADDENDUM-OK', now_iso)
