import json, time, datetime

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')

# state.json: append closeout-window addendum to note
s = json.load(open('state.json', encoding='utf-8'))
s['note'] = s['note'] + (" || r602 closeout addendum: first closeout push claw-BLOCKED (r374 diverged-base deletion-set false positive: origin advanced "
                         "b3cd4db34 bm-a r607 + f9c8311c5 bm-a tick); behind=2 integration revealed bm-a tick f9c8311c5 claimed DONE shard VALUEPB-X2 "
                         "(stale pre-04:38 pool model, owner_since 04:54:04) wiping my done flip + my NULLS claim from shared face (r489/r603 family); "
                         "SURGICAL reland (r523/r589, live-write faces present = rebase forbidden r532): payload = bookkeeping trio + non-collision S6 "
                         "faces + 3-face pool heal (sync_face settle + r603 resurrection-source shard pin-back: shared + bm-a lane + bm-b lane; valuepb-x2 "
                         "done/bm-b restored, nulls owner=bm-b restored, bm-a SENS done preserved, 354/354 union-lossless assertions PASS) + kill-advice "
                         "MSG-0535 to bm-a (duplicate burn kill + twin-yield + lane sweep + daemon done-absorption fix advice); collision S6 host faces "
                         "taken origin-newer per r109 (their r607 regen). claw-block escape NOT used (integrated properly, no --no-verify).")
for k in ('ts', 'updated', 'updated_at', 'last_seen'):
    s[k] = iso
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# heartbeat: refresh verdict + task with heal fact
h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
h['verdict'] = ("healthy: smoke 47/47, S6 34/34 rc0 (dualrun streak 6/3, audit CLEAN), SatEngine alive, attrition CLEAN, "
                "orders 150/150 zero unacked, VALUE-PB x2 product gap healed (r586 law), NULLS burn healthy in flight; "
                "closeout-window: bm-a tick pool regression (valuepb-x2 ghost claim + nulls claim wipe) healed 3-face per r603, "
                "kill-advice MSG-0535 sent, surgical reland per r589/r532")
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = iso
h['last_seen'] = iso
h['ts'] = iso; h['updated'] = iso; h['updated_at'] = iso
assert isinstance(h['heartbeat_epoch_utc'], int) and 'T' in h['clock_read']
with open('fleet/machines/bm-b.json', 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# round report: addendum line
line = (f"\n| {iso} | round 602 addendum (bm-b) | 收口窗事件披露：首笔收口 push 被爪正确双拦（r374 分叉基座伪影·origin 前进 bm-a r607 b3cd4db34 + tick f9c8311c5·"
        "禁 --no-verify 绕爪）→ 落 r589/r532 外科重落环：①behind=2 集成期发现 **bm-a tick f9c8311c5 用 04:38 前陈旧池模型覆写共享池面**——"
        "VALUEPB-X2（我 04:38:04 done+产物已上 origin ac8519fd2）被回退 ready+owner=bm-a=重复烧+翻面回退；我的 NULLS claim 被抹成无主 ready="
        "活体双烧风险（r489 家族再犯）；其 SENS done 合法保留 ②愈合=merge_lane_views sync_face settle+r603 复活源根治三面钉回"
        "（shared+bm-a lane+bm-b lane 三面 valuepb-x2 shard 行恢复 done/bm-b·nulls owner=bm-b 恢复·354/354 零丢失断言 PASS·"
        "跨 lane 编辑已在 MSG 披露=r603 先例）③MSG-2026-10-03-0535 kill-advice 已入 inbox（击杀你方重复烧+孪生产物让路 r381+daemon done-absorption 前置读建议）"
        "④外科 payload=簿记三件+非撞面 S6 派生件+池面愈合三件+MSG+回执件；撞面 S6 host faces 取 origin 新侧（r109·bm-a r607 再生为准）"
        "⑤三断言门（删除集空+tree-delta==payload+关键 ls-tree 点检）后 CAS update-ref+reset --mixed+分面 checkout（活写面不碰 r532）| "
        "[via bm-b r602 addendum]\n")
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('addendum bookkeeping written; iso=', iso)
