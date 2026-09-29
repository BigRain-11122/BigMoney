"""r444 bm-a close-out: state bump, heartbeat, round report, CODELY pit entry (UTF-8 safe)."""
import json, time, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
now = time.time()
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(now))
seen = time.strftime("%Y-%m-%d %H:%M", time.localtime(now))

# --- state-bm-a.json ---
s = json.load(open("state-bm-a.json", encoding="utf-8"))
s["round_no"] = 445
s["did"] = ("r444: fleet-consistency repair round -- inherited r443 dead-session rebase heritage "
            "(19-UU tree, fork-point replayed onto stale base 7eaa55cf5 while origin advanced 3x in "
            "fleet push-storm window 19:26-19:49); topology forensics: merge-base(3ca84fcb6,9298c2cb8)"
            "=0408db785 = my base fully inside origin chain, zero force-rewind (bm-c r235 absorbed "
            "r438/r439 relands + bm-b ticks); abort stale rebase -> explicit rebase --onto origin/main "
            "0408db785 -> 20-UU resolved per canon (merge_lane_views ALL_FACES x7 incl compute_audit "
            "207-row zero-loss union; snapshot/twin deep-ts take-new all origin-side newer 19:40-19:45 "
            "vs 19:35-19:39; CODELY entry-level memory-union skeleton=mine 5768B adopted 2 uncovered=0; "
            "archive line-union A+9/M+4) -> 3x push-reject chase -> safety branch machine/bm-a-r444 -> "
            "push SUCCESS main=99d442369 r443 verdicts fully landed")
s["verify"] = ("HEAD==origin==99d442369; smoke 26/26; marker-scan 20 files zero residue; all JSON "
               "parse-verified; orders 122/122 zero unacked; CODELY ~6.4KB under 10KB line")
s["next"] = ("r445: (a) predictor/conditional-face candidate draft (vol/risk conditioning, fresh "
             "prereg + D6 first); (b) 09-30 bar landing watch -> trigger chain; (c) 10-01 month-first "
             "triple (science_audit+monthly_briefing+self_review); 5x r445 HANDOVER check")
s["current_task"] = "r444 closed: r443 verdicts landed on main 99d442369; next predictor/conditional draft"
s["last_round_at"] = clock
s["updated"] = clock
json.dump(s, open("state-bm-a.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-a.json ---
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
try:
    import psutil
    h["cpu_pct"] = round(psutil.cpu_percent(interval=0.3), 1)
    h["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    pass
h["last_seen"] = seen
h["current_task"] = "r444 closed: r443 verdicts landed on main 99d442369; next predictor/conditional draft"
h["verdict"] = "healthy"
h["heartbeat_epoch_utc"] = int(now)
h["clock_read"] = clock
h["round_no"] = 444
assert isinstance(h["heartbeat_epoch_utc"], int)
json.dump(h, open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# --- round report line ---
rr = ("2026-09-29 20:2x | r444 | WM verdict: GREEN (red=false lane=healthy; probe from r443 wrap 19:35 "
      "insufficient_history 合法=板空+W10 harvest bm-b 在飞) | 当前活: r443 遗产修复收口——r443 会话 19:41 push "
      "被拒后 pull --rebase fork-point 落在过时基点 7eaa55cf5 上、解冲突窗内 origin 三连推进（bm-c r235 吸收 "
      "r438/r439 reland 19:26-19:46+bm-b tick 19:31/19:47）、会话死亡遗留 19-UU 脏树; 本轮拓扑取证 "
      "merge-base(3ca84fcb6,9298c2cb8)=0408db785=我方基点全在 origin 链内·零 force 回卷→abort 过时 rebase→"
      "rebase --onto origin/main 0408db785 显式重放→20-UU 正典解（merge_lane_views ALL_FACES×7=compute_audit "
      "207 行 union 零丢失+5 take-new deep-ts; snapshot×5+twin×3+js-twin 全 origin 侧 19:40-45 更新; CODELY 条目级 "
      "memory-union 骨架=我方 5,768B 采纳 2 条 uncovered=0; archive line-union A+9/M+4）→push 拒（origin 进 "
      "c936721d1）→二次 rebase 6-UU 解→push 拒（origin 进 423043a54）→安全分支 machine/bm-a-r444 先落→三次零冲突→"
      "push 成功 main=99d442369 | 最近实物: main 99d442369（A11 verdict 0/24 四子线全谱关闭+臂表 A11 行+attrition "
      "27/73+SEED+prereg §7/8）+ results/_r444bma_resolve.py（20-UU 解证据件）+ machine/bm-a-r444 安全分支 | "
      "下个里程碑: ①预测器/条件化面候选起草（vol/风险条件化·新 prereg+D6 先行·窗≤48h）②09-30 bar 落地→触发链 "
      "③10-01 月首轮三件套+5x r445 HANDOVER 核查。did: S0.5 orders 122/122 零未回执+双板零 open 票; S1 smoke "
      "26/26; S6 链本轮未重跑（r443 wrap 19:3x 全链 <40min 新鲜·09-29 bar klc2 仍 pending=触发腿合法跳过·下轮恢复"
      "常链）| verify: push 后 HEAD==origin==99d442369 实读; marker-scan 20 文件零残留; JSON parse-verify 全过; "
      "CODELY ~6.4KB 线内 | 下轮指针: 常链恢复+预测器/条件化起草三查先行（job_list+tasks 板+git log 30min 撞批扫）\n")
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(rr)

# --- CODELY pit entry (Feedback section, <=1.5KB, one matter) ---
pit = ("- [2026-09-29 20:2x r444 bm-a] fork-point 过时基点重放坑+风暴窗拒推收口律（r443 死亡遗产实弹）：S7 push "
       "被拒→pull --rebase 的 fork-point 落在 fetch 瞬间的 origin 位置上；解冲突期间 origin 再推进（机队风暴窗 "
       "19:26-19:49 bm-c reland+bm-b tick 三连推）则基点已过时=continue 后 push 三连拒、会话若死遗留 UU 脏树。正解="
       "①continue 前先 fetch 比对 origin/main 是否越过 onto 基点，越过→abort 后 `git rebase --onto origin/main "
       "<merge-base>` 显式重放（fork-point 风暴窗不可预测）；②二次拒推→先推 machine/<id>-r<N> 安全分支保产物再追"
       "主链；③遇 UU 遗产先拓扑取证（merge-base+origin reflog+双方 parent 链）判明零回卷再动手。本轮 20-UU+6-UU 两轮"
       "正典解全零丢失收口（resolver=results/_r444bma_resolve.py）。\n")
txt = open("CODELY.md", encoding="utf-8").read()
lines = txt.splitlines()
# insert into ### Feedback section (after last entry of that section, before ### Project)
try:
    fi = next(i for i, l in enumerate(lines) if l.startswith("### Feedback"))
    pi = next(i for i, l in enumerate(lines) if i > fi and l.startswith("### "))
    # walk back over trailing blanks
    k = pi
    while k > fi + 1 and lines[k - 1].strip() == "":
        k -= 1
    lines.insert(k, pit.rstrip("\n"))
    out = "\n".join(lines) + "\n"
except StopIteration:
    out = txt + "\n" + pit
open("CODELY.md", "w", encoding="utf-8", newline="").write(out)
print("close-out written: state 445, heartbeat epoch int, round report r444, CODELY pit entry")
print(f"CODELY size: {len(out.encode('utf-8'))}B")
