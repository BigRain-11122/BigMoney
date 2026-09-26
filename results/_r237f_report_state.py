# r237 (bm-a): round report line append + state file update (CRLF/no-BOM probes)
import io
import json

# --- round report line (logs/iteration-loop/round_reports-bm-a.md) ---
# EOL: CRLF is the dominant producer convention (400 CRLF vs 1 lone trailing
# LF from a prior addendum); append with CRLF per r223 lineage law.
REPORT = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    "R237 | 2026-09-26T09:5x | bm-a (dept:数据·T-39 moneyflow R236 修正案族移植+S0 冲突解) "
    "| verdict: GREEN (WM red=false lane healthy @08:50:02; probe 09:05 py_low_board_clear=合法 idle 板 0 open/bandit 0/bars present; "
    "compute_audit FLAG:pool_starvation=idle-starvation 合法白名单同态 R236〔板全闭环·池 ready 0〕非违令; smoke 25/25; "
    "orders 75/75 首扫零差集〔全名制 r220 律〕; decisions mtime 00:15 尾零新行·D-20260925-10 R206 已闭口) "
    "| did: S0 stash→pull-rebase→pop 撞 1-UU autofill_state（binding==源 R219 律先验+配方：launches union pre-cap 50=|A∪B| 全重叠零丢弃、"
    "last_tick 内 ts 整 dict 取新 bm-b 08:50:02〔r161/R203 禁 str 化〕、CRLF 镜像 560/560、isinstance dict 断言、kept⊆union 零发明断言; "
    "resolver=results/_r237a_resolve.py）; S1 smoke 25/25; S2 板 0 open/23 claimed 全有主+job_list 空; "
    "S3 主闭环 **T-39 moneyflow R235 双潜伏缺陷同构确认+R236 修正案族移植**: 触发链=rank 道只写 st.rank 不写 panel.cutoff"
    "→daykline 20td 门在首拉完成后 ~10-27 准时触发死码面（todo=not-done 恒空=复拉死码+零符号轮终态 None 覆写 mirror=真值毁+30min spawn 永动）"
    "→四件配方 1:1 移植 _is_repull/_todo_for〔done-reset·attempts 累计=隔离律不放宽〕/_panel_cutoff_from_bytes〔512B 尾读 derive〕/"
    "_terminal_cutoff〔零符号轮禁 None 覆写〕+gate spawn_mode 披露+refresh-repull 子命令分流+selftest 20/20→**21/21**〔S21 死码夹具=r157 镜像律〕"
    "+live 探针三面（现役 mirror classify=first-pull=零行为变化·合成 complete+stale cutoff=repull True·lane owner bm-a）"
    "+options 实查=pass-scoped done 集结构性免疫（假说「同族双病」修正=免疫判据是 done 集重置语义非家族名）; "
    "**E1 自捕 1 件**: T-39 ticket 插入器 anchor 前缀未保留=r116 尾文本被截（fail-closed verify assert 当场捕获于 commit 前）"
    "→_r237c2 字节修复 r116 内容恒等+仅必要尾逗号（r230 最小 diff 律达标）; 交付面=MF_COLLECTOR.md §9 注记+T-39 progress_r237"
    "+iteration_prompt.txt moneyflow 腿 R237 条款〔byte 精准单行插入·幂等守卫〕; "
    "S4 记忆 1 行（家族免疫判据·CODELY 40.9KB<50KB 无整编触发）; "
    "S6 周末链全绿 17 腿: daily 0 新行 cutoff 09-24·regime ORANGE d2 shadow〔hs300<MA200+breadth 0.77〕·lhb/heat 周末 no-op·"
    "futures/options/sina_mf/ths 零网络覆盖 no-op·moneyflow gate 新代码路径生产首跑=rank throttle no-op 面零变化·"
    "AH spawn 节流〔已知 EM 间歇族〕·fp bm-c 车道诚实 no-op·fundamental 11.7h fresh skip·blf mask 再生·"
    "scorecard 6 traders·build_status 10f/432combos·token delta=-45 "
    "| evidence: scripts/update_moneyflow.py selftest 21/21+S21·research/shortline/MF_COLLECTOR.md §9·"
    "fleet/tasks/T-2026-09-25-39-P1.json progress_r237·results/_r237a-e·S6 各状态件 "
    "| next: 09-28 周一新 bar 全链中继（moneyflow gate 腿将随窗过重试 rank 面）; ~10-27 复拉双窗观测面"
    "（sina R236+moneyflow R237 spawn_mode=re-pull 实况入轮报告）; 10-01 月界三件套"
    "（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门; T-70 中期判读 10-09; "
    "P1E-NULLS 等 bm-b lane 观察不越界"
)
nl = "\r\n"
with io.open(REPORT, "a", encoding="utf-8", newline="") as f:
    f.write(line + nl)
print("report appended (CRLF)")

# --- state file (state-bm-a.json) ---
STATE = "state-bm-a.json"
sraw = open(STATE, "rb").read()
has_bom = sraw[:3] == b"\xef\xbb\xbf"
s = json.loads(sraw.decode("utf-8-sig"))
s["round_no"] = 237
s["did"] = ("R237: T-39 moneyflow hardening = R236 amendment family ported (stale-repull dead-code + "
            "zero-symbol None-cutoff latent defects confirmed isomorphic via rank-lane-writes-rank-not-panel "
            "trigger chain, fuse ~10-27; fixed pre-arm: _is_repull/_todo_for/_panel_cutoff_from_bytes/"
            "_terminal_cutoff + spawn_mode + refresh-repull dispatch; selftest 21/21; live probe zero "
            "behavior change on in-flight first-pull; options checked = pass-scoped done set = structurally "
            "immune). S0 1-UU autofill resolved per skill (union 50, last_tick take-new bm-b 08:50:02, CRLF "
            "mirror). S6 17 legs green weekend no-ops. spec MF_COLLECTOR sec9 + ticket progress_r237 + "
            "prompt leg amended.")
out = json.dumps(s, ensure_ascii=False, indent=1) + "\r\n"
with io.open(STATE, "w", encoding="utf-8", newline="") as f:
    f.write(out)
back = json.loads(io.open(STATE, encoding="utf-8").read())
assert back["round_no"] == 237
print("state round_no=237 written (indent=1, CRLF, no BOM)")
