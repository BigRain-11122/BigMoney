"""r413 CODELY.md: append pit-law batch-83 + same-window hot/cold reorg (<=10KB hard line).

Archives 3 aged entries verbatim -> research/memory-archive/202609.md (new section
『坑律归档 2026-09-29 r413 bm-a 窗批』), replaces with one pointer line. Line-level
zero-loss verified (each archived line byte-identical in archive, removed exactly once
from hot file). Single-line-status edits use minimal unique fragments (adjacent-line
swallow law): entries are full lines, matched exactly, count==1 asserted.
"""
import io

HOT = "CODELY.md"
COLD = "research/memory-archive/202609.md"

ARCHIVE_HEADERS = [
    "\u3010坑律归档 2026-09-29 r413 bm-a 窗批\u3011",  # decorative header variant tolerated
]
SECTION = "\n## 坑律归档 2026-09-29 r413 bm-a 窗批（水位律当窗整编·行级零丢失校验）\n\n"

# exact full-line entries to archive (byte-identical, each asserted count==1)
ENTRIES = [
    "- [2026-09-29 r407 bm-b] 坑律八十一批（收割回执路径必须源码常量解析律·静默长活死亡推断禁律）：W5-JUDGE finalize 收割时以直觉路径 results\\w5_judge.json Test-Path 探活→「pid3108 死亡无回执」假诊断，险致误重启双 finalize（真路径=results\\trial_labor_w5\\w5_judge.json，JUDGE_FILE 常量在 scripts/trial_labor_w5.py:118）；实况=分离 finalize 03:26:33→03:48:39 正常 22min 静默烧（W2/W4 同构 25-27min，静默段零日志写+mtime 停更≠死亡），err 空非崩溃证据。姊妹面：PS `git show >` 重定向=UTF-16 转码，git blob 字节级取证必须 python subprocess 直取（本轮 indent 假差异两连坑皆直觉路径+转码所致）。How to apply：分离长活收割判据=先 rg runner 源码定产物路径常量再探活；重启前必先读代码序（_dump 先于 print=日志 print 齐≠未落盘）。",
    "- [2026-09-29 04:1x] 坑律·自开票认领字段面（r197 bm-c 实录·T-116）：开票同轮自认领必须落 claimed_by/claimed_at 两字段——认领事实只写进 note/created_by 散文=他机「他人 claimed 禁碰」守卫读字段时看到 None=碰撞风险面（T-116 r193 开票漏字段·r197 补登时 origin 零竞争认领实证）；范式=票面 JSON 字段即法，散文注记非法源。How to apply：任何机器开票+自认领，同 commit 必带两字段；缺字段票=发现即补登+验证 origin 无竞争。",
    "- [2026-09-29 r408 bm-b] 坑律八十二批（append-log 零丢失=超集律非行数比较律）：28-UU 同窗 S6 双胞胎解中 x2_watch_log.jsonl 以「union 行数≥max(两面行数)」断言假红拦截——同源滚动日志两面各 1506 行、面内 90 行历史重复（set 面 1416），dedup 并集 1422<1506=断言必假非数据损；r188「行级 union 零丢失」的机器判据在面内重复行场景不可用行数比较，必须=set 超集等式（set(out)==set(A)∪set(B)）+stage2 verbatim 前缀保面内多重性+l3 新行追加（保序保重），保重复本身是生产者字节流的忠实面非损失。姊妹面：rebase --continue 撞哑终端（GIT_EDITOR 未设=editor 启动失败 commit 不落）→`$env:GIT_EDITOR='true'` 覆写即愈；本窗方向核证=rebase stage 反转面（stage2=基座=bm-c r197·stage3=重放件=本机 r408）与坑律七十五/七十六批 take-NEW 方向无关解一致（探双 stage ts 新者胜·tie→stage2）。How to apply：jsonl 滚动日志撞 UU 先 python 复算 set(2)∪set(3) 与面内重复度再写断言；rebase continue 前恒设 GIT_EDITOR=true。",
]

POINTER = "冷层指针：坑律正典 2026-09-29 r407 bm-b 八十一批（收割回执路径源码常量解析律）+r197 bm-c 自开票认领字段面（T-116）+r408 bm-b 八十二批（append-log 超集律·GIT_EDITOR 哑终端姊妹面）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r413 bm-a 窗批』节（r413 bm-a 窗水位律当窗整编·行级零丢失校验）。"

B83 = "- [2026-09-29 04:4x] r413 bm-a 坑律八十三批（事件型 jsonl union 多重性律·stale-takeover 取侧律·卡死 rebase 复活实弹）：①x2_watch 等双机同窗事件型滚动日志撞 UU：union=多重集 union（逐行 max(双侧计数) 保持+按行内 ts 稳定排序落盘）——面内同秒同内容重复行=双机同窗双跑的合法多重事件非冗余，set 去重丢真事件（本窗 set 计 1428 vs 多重集 1518=1512+6 实弹、90 重复行全保）；与八十二批「stage2 前缀+l3 尾追」形态语义等价（多重集恒等）但 ts 序保时序单调，批 82 尾追形态在 l3 独行更旧时破尾时序——ts 序为正。②bm-a 单写守卫件（daily_scorecard 族）撞 UU 取侧禁按写者身份推断——他机 lawful stale-takeover（本窗 bm-b r408 于 bm-a 死窗 51min 后接管执笔）后 origin 侧反较新，取侧唯一判据=深探双侧 staged blob wall-clock ts（R350 全套律）。③死亡会话遗留卡死 rebase 的复活正路=接续正典解非 abort：分类器先行→ALL_FACES merge_lane_views resolve→快照深探取新→jsonl 多重集→同窗 reconcile（本窗三连撞 7→18→6 UU 推板风暴窗全解 e14911215 上链）。How to apply：jsonl union 断言=set(出)==set(2)∪set(3)∧逐行计数 max 保持∧出态 ts 单调；快照取侧先探双 stage ts 再定谳；卡死 rebase 发现即分类器起步勿 abort 弃已解面。"

hot = io.open(HOT, encoding="utf-8").read()
for e in ENTRIES:
    assert hot.count(e) == 1, f"entry not unique/present: {e[:40]}..."
    hot = hot.replace(e + "\n", "", 1) if (e + "\n") in hot else hot.replace(e, "", 1)

# append batch-83 at file end (established bottom-append practice)
hot = hot.rstrip("\n") + "\n" + B83 + "\n"
# insert pointer line into Reference section (after the canonical-pointer law line)
anchor = "冷层指针：坑律正典 2026-09-28 六十七/六十八批"
assert anchor in hot
hot = hot.replace(anchor, POINTER + "\n" + anchor, 1)

io.open(HOT, "w", encoding="utf-8", newline="\n").write(hot)

cold = io.open(COLD, encoding="utf-8").read()
assert SECTION.strip() not in cold, "section already exists"
cold = cold.rstrip("\n") + "\n" + SECTION + "\n".join(ENTRIES) + "\n"
io.open(COLD, "w", encoding="utf-8", newline="\n").write(cold)

# verify: zero-loss (archived lines present verbatim in cold, absent-in-hot count 0, hot <= 10240B)
cold_now = io.open(COLD, encoding="utf-8").read()
hot_now = io.open(HOT, encoding="utf-8").read()
for e in ENTRIES:
    assert e in cold_now, "archive lost a line"
    assert e not in hot_now, "hot still has archived line"
assert B83 in hot_now and POINTER in hot_now
import os
print(f"hot={len(hot_now.encode('utf-8'))}B cold_section_added=3_entries pointer+batch83 landed; hot<=10240: {len(hot_now.encode('utf-8')) <= 10240}")
