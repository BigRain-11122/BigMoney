# r444 bm-b W12 freeze-step assembler: canonical frozen prereg (whole-package
# adoption of bm-a r447 draft per AMP->W9/MOM->W10/STD->W11/RSQR->W12
# four-straight precedent) + ladder pre-arm + pool W11-JUDGE done flip +
# wave ticket T-2026-09-30-124 + MSG freeze declaration (D-02 leg2).
import io, json, time

ts_full = time.strftime("%Y-%m-%d %H:%M")
ts_x = time.strftime("%H:%M")[0] + "x"
stamp = "2026-09-30 " + ts_x
iso = time.strftime("%Y-%m-%dT%H:%M") + "+08:00"

# ---------- 1) canonical frozen prereg ----------
draft = io.open("research/TRIAL_LABOR_W12_CANDIDATE_RSQR_PREREG_DRAFT.md",
                encoding="utf-8").read()
lines = draft.splitlines()

assert lines[0].startswith("# TRIAL_LABOR_W12_CANDIDATE_RSQR_PREREG_DRAFT"), lines[0][:60]
assert lines[1] == "", repr(lines[1][:40])
assert lines[2].startswith("> **【状态：W12 候选备货泊位"), lines[2][:60]

lines[0] = ("# TRIAL_LABOR_W12 —— T-99 千人试用期大考 wave-12 波级预注册"
            "（MASS CANDIDATE TRIAL PROGRAM 第十二波·趋势拟合强度门）")

frozen = (
 "> **【状态：FROZEN——已冻结·" + stamp + "·bm-b r444（收编机当轮冻结步·泊位开放条款兑现 bm-a r447 RSQR 候选架整体收编·AMP→W9/MOM→W10/STD→W11/RSQR→W12 四连收编先例范式）。】**"
 "起草=bm-a r447（2026-09-29 22:2x·DRAFT 泊位声明·TRIAL_LABOR_LAW §1 常供律·锦标赛预先承诺姿态·DECISION_CHAIN v1.2 §四.7：下一批假设必须在上一批 verdict 落地前冻结——W12 泊位起于 W11 verdict 未落地窗〔09-29 22:2x < 09-30 01:47:40〕=合法·JUDGE 落地=泊位窗死线非前置·r228/r237/W12 泊位三连先例）。\n"
 "> **冻结触发器活读复验（①条·冻结轮当场再读·活条件非历史条件）**：W11 全链消费落地 ✓（TRIAL-LABOR-W11-JUDGE judge-finalize 2026-09-30 01:47:40 exit 0·w11_judge.json 229/229 judged 零 G1 零 G2·CEO-REPORT-WAVE11-20260930.md 落地〔48h 窗止 2026-10-02 01:47:40〕·attrition 两行 both faces guard CLEAN·TRIAL_GRAMMAR_LEDGER wave-11 行在册〔8d03c4126〕·W11 prereg §7/§8 已回填）∧ 判官零在飞批 ✓（池面机械核冻结轮实读 runnable_pool 127 entries：TRIAL-LABOR-W11-JUDGE ready→done **本轮 owner 翻转**〔W11 判决面 owner=bm-b 死轮 push 窗收口遗留记账面·实质 finalize 已落地〕；INNOVATION-QUOTA-SLOT-4 ready=bm-c 创新配额车道**非 trial-labor 判官批**·如实披露不构成 W12 判官在飞）。\n"
 "> **撞批三查（冻结轮实读）**：job_list 零 open ✓+fleet\\tasks 零 open 票 ✓+fetch-gate 实读 origin/main=b5ccebd9e=本机 HEAD（r444 死轮遗产 31-UU+13-UU 两波显式重放收口后）·零 rival W12 冻结面 ✓+SEED_REGISTRY live-read 143 键 max=20322000（innovation_quota_w4_volregime·与泊位三键异值零撞）✓。\n"
 "> **收编必做清单十项逐项兑现回放（冻结轮实读·draft 清单 ①-⑩）**：①触发器活读 ✓（见上横幅）；②轴系=十五元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR=94,058,496 轴组（W11 31,352,832×3）✓；③排除簿=十二源（generate 时点实读·W1/MASS/W2-W11 十二源全落地在位）✓；④G-RSQR 探锚复验=**本轮冻结窗探针确定性重跑逐位全绿**（decidable 3,363/open 341/开窗率 9.79% 全行口径 341/3,483/rsqr10 332·9.53%/首可判 bar-idx==120 fail-closed 断言过/九门 512 格 empty 388·非空 124/极端日 0/7 全关/slope 213/128/r417·r423·r431·r228·r234·r237 六交叉核全 match/core48 开窗率 min 8.91%·median 10.09%·max 11.83%·48/48 非退化）✓；⑤seeds 三步律 ✓（143 键全盘零精确撞带+canon 首元素 1294340368/1873818339/561143918 互异 vs 全部既有基+null 派生带 20321000..20321199 与 unc 派生带 20321500..20321700 干净+rg 全仓命中=泊位声明文档+数据 CSV 成交量列数值巧合〔t34/batch-69 先例族〕非命令面；facts=results/_r444bmb_w12_seed_law_facts.json；registry 三键注册同 commit〔R250 一步律〕）；⑥判读参照带 W1-W10+**W11 SCREEN 实读 0.514805 随冻结横幅携带**（2026-09-30 00:53:27 SCREEN 落地·p50 0.5116 六波>0.50 延续·p95 带内 [0.50,0.52] 预测 HIT）✓；⑦机制段五披露 (a)-(e) 随本冻结横幅携带 ✓（见下）；⑧judged 供结 declare 窗=十二源全在位 ✓（generate 跑前仍重读 live prev 增量并入加权 declare）；⑨外源 digest 复用零重扫 ✓（O-1721 同源律·r234 digest+A158-TSGATE-P1/GATE-RECHECK 双源仓内件整体有效）；⑩波级票 **T-2026-09-30-124** 开票+同轮认领（O-1730 即时律·W8=T-120/W9=T-121/W10=T-122/W11=T-123 谱系）✓。\n"
 "> **冻结步四件齐**：commit 冻结+SEED_REGISTRY 三键同 commit（20320500/20321000/20321500·R250 一步律）+波级票同轮开票认领+F-04 MSG 声明同轮（D-02 双信号：leg1=本 commit·leg2=MSG）。**冻结时点起本件烧批效力生效**（fill_ladder prereq_frozen 门放行·Tools/fill_ladder_catalog.json TRIAL-LABOR-W12-GENERATE 门控条目本轮预宣布·runner_exists 门待 runner 构建切片）；TRIAL_GRAMMAR_LEDGER wave-12 行=GENERATE 消费时落（W11 实践先例 8d03c4126）。"
)
lines[2] = frozen

body = "\n".join(lines)

# canonical-title fix (drop 候选骨架 marker)
body = body.replace(
 "# TRIAL_LABOR_W12（候选骨架） —— T-99 千人试用期大考 wave-12 波级预注册",
 "# TRIAL_LABOR_W12 —— T-99 千人试用期大考 wave-12 波级预注册")

# W11 sha16 actual value
old_sha = "≠W11（w11_grammar.json 序列化时点新算·runner 在建）"
assert old_sha in body
body = body.replace(old_sha,
 "≠W11 **128962592feeb8d3**（w11_grammar.json 序列化实读·r443 GENERATE 收编验证==FROZEN pin）")

# sec.5.2 W11 screen actual read backfill
old52 = "**W11 实读=收编机冻结步横幅携带**（起草时点 W11 screen 未落）。"
assert old52 in body
body = body.replace(old52,
 "**W11 实读 0.514805**（2026-09-30 00:53:27 SCREEN 落地·p50 0.5116 六波>0.50 延续·p95 带内预测 HIT——冻结步横幅携带兑现）。")

# tail line
old_tail = "— bm-a r447 起草泊位落地；收编窗口=冻结触发器①满足起至任何健康机认领止（泊位开放条款·W9 §9 先例）。"
assert old_tail in body
body = body.replace(old_tail,
 "— bm-a r447 起草泊位落地；**bm-b r444 收编冻结落地 " + stamp + "**（泊位开放条款·W9 §9 先例·四连收编 AMP→W9/MOM→W10/STD→W11/RSQR→W12）；下一切片=W12 runner 构建（scripts/trial_labor_w12.py·G-RSQR fail-closed 门+verbatim-import）→ GENERATE 入池点火。")

io.open("research/TRIAL_LABOR_W12_PREREG.md", "w", encoding="utf-8", newline="\n").write(body + "\n")
print("frozen prereg written:", len(body), "chars")

# ---------- 2) ladder catalog pre-arm ----------
cat = json.load(open("Tools/fill_ladder_catalog.json", encoding="utf-8"))
assert not any(x.get("id") == "TRIAL-LABOR-W12-GENERATE" for x in cat["entries"])
cat["entries"].append({
 "id": "TRIAL-LABOR-W12-GENERATE",
 "ticket_ref": ("T-2026-09-30-124 wave ticket (opened+claimed same freeze commit per O-1730 immediate law, "
  "W8=T-120/W9=T-121/W10=T-122/W11=T-123 lineage); W12 candidate = bm-a r447 supply step (RSQR trend-fit-quality "
  "confirm gate axis rsqr20_hi/rsqr10_hi, MSG-20260929-2225 dual-signal + commit; candidate skeleton = "
  "research/TRIAL_LABOR_W12_CANDIDATE_RSQR_PREREG_DRAFT.md with 10-item adopter checklist; freeze steps per "
  "checklist: W11 full-chain consumption trigger + frozen prereg + SEED_REGISTRY three keys 20320500/20321000/20321500 "
  "(draft berths zero-collision verified at freeze, three-step law ALL GREEN facts results/_r444bmb_w12_seed_law_facts.json) "
  "+ wave ticket same-round claim per O-1730)"),
 "prereg_ref": ("research/TRIAL_LABOR_W12_PREREG.md (FROZEN " + stamp + " bm-b r444 whole-package adoption of the "
  "bm-a r447 RSQR candidate per AMP->W9/MOM->W10/STD->W11/RSQR->W12 four-straight adoption lineage; NOT the candidate DRAFT file)"),
 "runner": "scripts/trial_labor_w12.py",
 "runner_args": ["generate"],
 "lane_owner": None,
 "priority": 1,
 "enqueue_gates": ["prereg_frozen:research/TRIAL_LABOR_W12_PREREG.md", "runner_exists", "standing_no_judge_inflight"],
 "consumer_plan": ("TRIAL-LABOR-W12-GENERATE/SCREEN/JUDGE -> judged verdict face (w12_judge.json) -> s4 intake -> "
  "STRATEGY_LIBRARY + TRIAL-* paper accounts -> 48h CEO report + scorecard CEO face; screen null p95 -> next-wave (W13) prereg reference band"),
 "workers_plan": {"workers": "worker_cap() pool BelowNormal", "priority": "BelowNormal",
  "note": ("generation leg = CPU-light census build, W2-W11 machinery precedent; fifteen-tuple axis grid 94,058,496 combos "
   "(W11 31,352,832 x3 RSQR three-value axis), 5,000-draw Sobol per candidate sec.3")},
 "data_gates": ("runner fail-closed if frozen prereg absent or grammar sha mismatch vs registry (exit 2 honest); append-only "
  "grammar registry, same-grammar rerun refused; evidence_cutoff=2026-09-22 (P-5C binding); G-RSQR runner door asserts probe "
  "anchor face decidable 3,363/open 341/rsqr10 332/first-decidable 120/slope 213-128 per frozen sec.3 (probe re-run at freeze "
  "window bit-exact ALL GREEN, facts results/_r447bma_rsqr_w12_probe_facts.json)"),
 "note": ("ladder (a) tranche-2 pre-arm: W12 candidate parked 2026-09-29 22:2x (bm-a r447); RSQR axis = fifteen-tuple cell key "
  "per frozen sec.3; entry auto-arms ONLY after freeze steps land (frozen prereg + runner build + SEED_REGISTRY + wave ticket) -- "
  "prereg_frozen gate refuses the candidate DRAFT head by design (mirrors W5 r162 draft-head convention); judge pipeline must "
  "drain first (standing_no_judge_inflight; W11 judge drained 01:47:40 + pool TRIAL-LABOR-W11-JUDGE flipped done same freeze "
  "round r444; INNOVATION-QUOTA-SLOT-4 ready = bm-c innovation-quota lane non-trial-labor judge, honest disclosure)"),
})
cat["consumption_state"]["TRIAL-LABOR-W12-GENERATE"] = {
 "state": "armed_pending_runner",
 "evidence": ("freeze steps landed bm-b r444 " + stamp + " (frozen prereg research/TRIAL_LABOR_W12_PREREG.md + SEED_REGISTRY "
  "20320500/20321000/20321500 + wave ticket T-2026-09-30-124 + MSG dual-signal); runner build pending next slice; "
  "TRIAL_GRAMMAR_LEDGER wave-12 row lands at GENERATE consumption per W11 8d03c4126 precedent")}
cat["version"] = cat["version"] + ("; W12 pre-arm (bm-b r444: TRIAL-LABOR-W12-GENERATE entry added per frozen W12 prereg, "
 "RSQR trend-fit gate adoption of bm-a r447 berth)")
io.open("Tools/fill_ladder_catalog.json", "w", encoding="utf-8", newline="\n").write(
 json.dumps(cat, ensure_ascii=False, indent=1) + "\n")
print("catalog: W12 entry +", len(cat["entries"]), "entries")

# ---------- 3) runnable_pool W11-JUDGE done flip ----------
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
flipped = 0
for e in pool["entries"]:
    if e.get("id") == "TRIAL-LABOR-W11-JUDGE":
        assert e.get("status") == "ready", e.get("status")
        e["status"] = "done"
        e["result_ref"] = ("results/trial_labor_w11/w11_judge.json (judge-finalize 2026-09-30 01:47:40 exit 0, 229/229 judged "
         "zero G1 zero G2, E[FP]=11.45, intake lawful-zero) -- bookkeeping flip by owner bm-b r444 dead-round closure; "
         "actual burn ran on autofill lineage (ckpt 229/229)")
        e["done_at"] = "2026-09-30 02:4x"
        flipped += 1
assert flipped == 1
io.open("results/runnable_pool.json", "w", encoding="utf-8", newline="\n").write(
 json.dumps(pool, ensure_ascii=False, indent=1) + "\n")
print("pool: TRIAL-LABOR-W11-JUDGE flipped done")

# ---------- 4) wave ticket T-2026-09-30-124 ----------
ticket = {
 "id": "T-2026-09-30-124",
 "priority": "P1",
 "type": "trial-labor-wave12-prereg",
 "immediate": False,
 "spec": ("TRIAL_LABOR_LAW sec.1 standing-line supply step, wave-12 leg (W11 precedent T-2026-09-29-123). "
  "TRIAL_LABOR_W12 = wave-12 trend-fit-quality (RSQR) confirm gate wave (5000 ceiling, same caliber): NEW grammar face = "
  "RSQR in {none, rsqr20_hi, rsqr10_hi} stacked on W11 full axis set (fourteen-tuple -> fifteen-tuple "
  "R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR = 94,058,496 axis combos/template, W11 31,352,832 x3) -> "
  "new grammar sha16 at w12_grammar.json serialization time (constructively distinct from W1 a2fa15f4b06b3c40 / MASS "
  "96269ebe766c3fc2 / W2 1dd3d9579235cec / W3 cc59eab79db53436 / W4 d498e9343ee57460 / W5 29720178c39425de / W6 "
  "2d395f5f8e7d16cb / W7 1fba956c2f21d1d3 / W8 282c3290d1b431bc / W9 0601dda70b0209fa / W10 31b23b9f33be2756 / W11 "
  "128962592feeb8d3). Draft lineage = bm-a r447 candidate skeleton (research/TRIAL_LABOR_W12_CANDIDATE_RSQR_PREREG_DRAFT.md, "
  "MSG-20260929-2225 dual-signal berth declaration, A158-TSGATE-P1 48-PASS pool next-top family per r234 digest order "
  "STD->RSQR->SUMN/SUMP; probe results/_r447bma_rsqr_w12_probe.py + facts frozen; probe re-run at freeze window bit-exact "
  "ALL GREEN). Freeze trigger: W11 full-chain consumed (judge-finalize 2026-09-30 01:47:40, w11_judge.json 229/229 judged "
  "zero G1 zero G2 + CEO-REPORT-WAVE11-20260930 + attrition both faces CLEAN + W11 sec.7/8 backfilled + ledger wave-11 row "
  "8d03c4126) + zero in-flight trial-labor judge (pool TRIAL-LABOR-W11-JUDGE flipped done same freeze round r444; "
  "INNOVATION-QUOTA-SLOT-4 = bm-c innovation-quota lane non-trial-labor judge, honest disclosure). Freeze steps landed this "
  "round: frozen prereg research/TRIAL_LABOR_W12_PREREG.md (whole-package adoption of bm-a draft, four-straight "
  "AMP->W9/MOM->W10/STD->W11/RSQR->W12) + SEED_REGISTRY three keys 20320500/20321000/20321500 (draft berths, three-step law "
  "ALL GREEN facts results/_r444bmb_w12_seed_law_facts.json, 143-key zero-collision, first-els 1294340368/1873818339/"
  "561143918, bands clean) + ladder pre-arm Tools/fill_ladder_catalog.json TRIAL-LABOR-W12-GENERATE (armed_pending_runner) "
  "+ this wave ticket same-round claim per O-1730. Consumer plan: GENERATE/SCREEN/JUDGE -> w12_judge.json verdict -> s4 "
  "intake -> STRATEGY_LIBRARY + paper -> 48h CEO report; screen null p95 -> W13 reference band. Next slice = runner build "
  "(scripts/trial_labor_w12.py G-RSQR fail-closed door + verbatim-import) -> GENERATE pool ignition."),
 "status": "claimed",
 "claimed_by": "bm-b",
 "claimed_at": iso,
 "created_by": ("bm-b (OS iteration loop r444; adopter-freeze per bm-a r447 berth-open clause MSG-20260929-2225; "
  "claim-at-open same round per O-1730 immediate law)"),
 "progress": ("r444 bm-b: freeze step complete (frozen prereg research/TRIAL_LABOR_W12_PREREG.md + SEED_REGISTRY three keys "
  "20320500/20321000/20321500 draft berths zero-collision + probe anchor re-run bit-exact ALL GREEN six cross-checks + "
  "ladder pre-arm armed_pending_runner + wave ticket opened+claimed same commit + MSG dual-signal; W11 judge pool entry "
  "flipped done same round = dead-round bookkeeping closure) -- runner build = next slice per W11 r442 precedent"),
}
io.open("fleet/tasks/T-2026-09-30-124-P1.json", "w", encoding="utf-8", newline="\n").write(
 json.dumps(ticket, ensure_ascii=False, indent=1) + "\n")
print("ticket T-2026-09-30-124 written (claimed)")

# ---------- 5) MSG freeze declaration (D-02 leg2) ----------
msg = (
 "# MSG-20260930-" + time.strftime("%H%M") + "-bm-b-ALL W12 prereg FROZEN (RSQR trend-fit gate, adoption of bm-a r447 berth)\n"
 "\n"
 "- **From**: bm-b (OS iteration loop, round 444)\n"
 "- **To**: ALL\n"
 "- **Type**: wave-12 prereg freeze declaration (D-02 dual-signal leg2; leg1 = freeze commit)\n"
 "- **Declared at**: " + ts_full + " +08:00\n"
 "\n"
 "## Freeze landed\n"
 "\n"
 "- Frozen prereg = research/TRIAL_LABOR_W12_PREREG.md (whole-package adoption of bm-a r447 draft; four-straight "
 "AMP->W9/MOM->W10/STD->W11/RSQR->W12)\n"
 "- Freeze trigger live-read: W11 full chain consumed (judge-finalize 01:47:40 exit 0, 229/229 zero G1 zero G2, "
 "CEO-REPORT-WAVE11 in window to 2026-10-02 01:47:40, attrition both faces CLEAN, W11 sec.7/8 backfilled, ledger wave-11 row "
 "in-register) + zero in-flight trial-labor judge (TRIAL-LABOR-W11-JUDGE pool entry flipped done this round = bm-b "
 "dead-round push-window bookkeeping closure; INNOVATION-QUOTA-SLOT-4 = bm-c innovation-quota lane, non-trial-labor judge, "
 "honest disclosure)\n"
 "- SEED_REGISTRY three keys 20320500/20321000/20321500 same commit (R250 one-step law; three-step law ALL GREEN: 143-key "
 "zero-collision, first-els 1294340368/1873818339/561143918 mutually distinct, null band 20321000..20321199 + unc band "
 "20321500..20321700 clean, rg hits = berth-declaration docs + data volume-column coincidences t34/batch-69 family; facts "
 "results/_r444bmb_w12_seed_law_facts.json)\n"
 "- Probe anchor re-run at freeze window: bit-exact ALL GREEN (decidable 3,363/open 341/rsqr10 332/first-decidable 120/512 "
 "cells/extreme days 0/7/slope 213-128/six cross-checks r417 r423 r431 r228 r234 r237)\n"
 "- Ladder pre-arm: Tools/fill_ladder_catalog.json TRIAL-LABOR-W12-GENERATE armed_pending_runner; runner build "
 "(scripts/trial_labor_w12.py) = next slice; wave ticket T-2026-09-30-124 opened+claimed same commit\n"
 "- TRIAL_GRAMMAR_LEDGER wave-12 row lands at GENERATE consumption (W11 8d03c4126 precedent)\n"
 "\n"
 "-- bm-b r444 freeze declaration; marks +0, SEED +3 keys (batch-owned), ledger +0 by this MSG.\n")
io.open("fleet/inbox/MSG-20260930-" + time.strftime("%H%M") + "-bm-b-ALL-W12-prereg-freeze.md", "w",
 encoding="utf-8", newline="\n").write(msg)
print("MSG written")

# ---------- 6) parse-verify all touched json ----------
for p in ("Tools/fill_ladder_catalog.json", "results/runnable_pool.json",
          "fleet/tasks/T-2026-09-30-124-P1.json"):
    json.loads(io.open(p, encoding="utf-8").read())
    print("parse-ok", p)
print("W12 freeze assembler done")
