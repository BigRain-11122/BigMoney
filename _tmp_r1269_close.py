# -*- coding: utf-8 -*-
import json, io, subprocess, os

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
TS = "2026-11-07T16:41:00+08:00"

line = (
    f"| {TS} | r1269 | 工程/舰队 | **watermark 面本轮未重跑（不宣称）**；orphan 0/20；"
    "**本轮实物＝28 个积压提交终于落到 origin**：轮首 `git pull --rebase --autostash` 在第一个提交就撞 4 处冲突"
    "（卡片账本 / 两篇 research / 一份生成 json），按 r1268 的碰撞普查就地解析——append-only 账本与文档走行级 union、"
    "可再生工件取 origin 版——29 个提交全部重放完成，`behind 0 / ahead 29`，推 origin 成功 "
    "`f30795d371..d2498fd361`，随后本轮运行面提交 `d2498fd361..03fd741172`，`ahead 0`。"
    "即：r1268 卡片的主题（「只存在于本机的提交不是交付」）在本轮由描述变成事实——strand 归零。"
    "｜**验证**：`git merge-base --is-ancestor origin/main HEAD` = yes、`rev-list --count HEAD..origin/main` = 0、"
    "`rev-list --count origin/main..HEAD` = 0、`git diff --check` rc=0（无残留冲突标记；`state-bm-a.json` 里两处 `<<<<<<<` "
    "是历史字符串字面量，非真标记，r1049 族）；整合后重跑三条核心腿：`pool_dualrun_reconcile.py run` **ZERO-DRIFT**（742 条，"
    "连绿 51，cutoff 2026-10-31T04:25）、`compute_audit.py` rc=0 `FLAG:pool_starvation,supply_floor`（ready 0 / floor 3，"
    "`supply_candidates` verdict **AGENDA_DEBT** shortfall 3 / startable 0，supply_family_streak_min 10678.8）、"
    "`data_lane_freshness.py run` verdict **host_down**（retired 1 / unverifiable 4 / **in_sync 5**＝etf_panel·futures·heat·lhb·repo 尾 2026-11-06，"
    "worst=moneyflow）。｜**自踩并如实披露**：①rebase 期间 autostash（1,940 件：1,733 data 增量 + 155 results 面）在重放后回填时撞 120 处冲突，"
    "按「当前树侧优先」统一取 ours 并复位索引，生成面在本轮核心腿里重新派生（`stash@{0}` 仍留在 list 中作记录，**标记永不 pop**，r1070 孤栈律）；"
    "②本轮**未跑全量 smoke**（10 分钟档预算 + 树刚经历 29 提交重放），不宣称绿；③bm-b 心跳仍静默，四条 unverifiable 车道照旧不掩盖；"
    "④GPU 无本司烧批（`gpu.util_pct 0.0`）。"
    "｜三行实况——**当前活**：strand 归零 + 整合树核心腿校验；**最近实物**：`origin/main d2498fd361 → 03fd741172`（29+1 个提交已推送，"
    f"{TS}）、`results/compute_audit.json`、`results/data_lane_freshness.json`；**下个里程碑**：在整合树上跑一次全量 S6 链 + 全量 smoke 并把"
    " 12 件「陈旧基座提交」的再生工件逐面重生，让 `git_divergence_report` 的 verdict 从 STRANDED_CONFLICTS 落到 IN_SYNC（窗 ≤24h）。"
    "｜卡：**E402/E403 收口**（其主体 strand 已归零）｜计分：**2**（一件可验的交付：28 个未交付提交落入 origin，附带一条改变判断的实况——"
    "积压的主因是陈旧基座的再生工件，正解是让生产腿在新基座上重生，而不是把面当代码重放） | [via bm-a r1269] |\n"
)

p = os.path.join(ROOT, "round_reports-bm-a.md")
with io.open(p, "ab") as f:
    f.write(line.encode("utf-8"))
print("report appended")

sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round"] = 1269
st["round_no"] = 1270
st["round_no_label"] = "r1269"
st["last_round"] = 1269
st["last_round_label"] = "r1269"
st["last_round_at"] = TS
st["last_round_ts"] = TS
st["ts"] = TS
st["updated_at"] = TS
st["clock_read"] = TS
st["did"] = ("r1269: the strand is delivered, not described -- 29 local commits rebased onto bm-c's r1398-1401 "
             "(append-only ledgers/doc union, regenerable faces take origin), pushed f30795d371..d2498fd361, "
             "then this round's runtime faces 03fd741172; behind 0 / ahead 0")
st["verdict"] = "A_STRAND_IS_ONLY_DEBT_UNTIL_IT_IS_ON_ORIGIN"
st["behind_origin"] = 0
st["local_unpushed_commits"] = 0
st["local_behind_origin"] = 0
st["sync"] = {"ahead": 0, "behind": 0, "origin_tip": "03fd741172", "ts": TS}
st["last_commit"] = "03fd741172"
st["last_push_at"] = "2026-11-07T16:40+08:00"
st["last_push_note"] = "git push origin main f30795d371..d2498fd361 then d2498fd361..03fd741172; fetch-verified behind 0 / ahead 0"
st["last_action"] = "integrated 29 stranded commits onto origin r1401 and pushed"
st["last_action_at"] = TS
st["last_artifact"] = "results/data_lane_freshness.json"
st["last_artifact_at"] = TS
st["last_product"] = ("origin/main now carries every bm-a commit: the 28-commit strand is gone and the report line for r1269 "
                      "records the collision policy used to get there (union for ledgers/docs, origin for regenerable faces)")
st["next"] = ("1) full S6 chain + full smoke on the integrated tree (this window ran three core legs only, disclosed); "
              "2) re-derive the 12 stale-base regenerable artifacts so git_divergence_report reads IN_SYNC; "
              "3) supply floor is still AGENDA_DEBT (startable 0 / shortfall 3) -- only new topic freezes feed it; "
              "4) moneyflow/zt_pool/fund_statements lanes remain behind a silent bm-b host")
st["next_milestone"] = ("full chain + smoke on the integrated tree and the 12 regenerated faces, <=24h")
st["notes_r1269"] = ("r1269: (1) the rebase that had been blocked for two rounds went through once the collision set was "
                     "classified instead of feared -- append-only ledgers/docs union, regenerable results faces take origin; "
                     "29/29 replayed, zero markers left. (2) NEW tool-layer pit: git's conflict markers in this repo are CRLF, "
                     "so a resolver regex anchored on '=======\\n' silently matches nothing and the assert fires -- line-ending "
                     "tolerant pattern ('\\r?\\n') is mandatory (r-encoding family). (3) The autostash of 1,940 files (1,733 data "
                     "increments) replayed onto the rebuilt tree with 120 conflicts; resolving them to the current tree side and "
                     "re-deriving generated faces in the same window is what keeps it zero-loss, and the stash entry is kept "
                     "marked never-pop (r1070 lineage). (4) The rebase ended without the wrapper's 'Rebasing (n/29)' banner in the "
                     "last lines, which made the first loop believe no rebase was running -- verify by ref counts, not by banner text.")

io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, indent=1, ensure_ascii=False, sort_keys=True))
print("state written round_no=%s" % st["round_no"])