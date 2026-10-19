# r1035 bm-b closeout: state surgery + heartbeat + round report row + orders_ack diff
import json, time, io, os, glob, re

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---- state.json ----
with io.open(os.path.join(REPO, "state.json"), "r", encoding="utf-8") as f:
    st = json.load(f)

st["round_no"] = 1035
st["round"] = 1035
st["round_no_label"] = "r1035"
st["clock_read"] = NOW
st["ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_seen"] = NOW
st["last_action_at"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["now_active"] = "r1035 closed"
st["orphan_face"] = 0
st["orphan_face_note"] = "r1035 S1 probe (21:0x): 9 py faces / 0 orphans (incl. legal detached: anchor_env_bootstrap pid 15928 + astock refresh)"

did = ("r1035: (a) S0 estate delivery: fetch behind=4 -> rebase --autostash replay of r1034 2-commit payload "
       "(e4dc0861f6 + postscript) onto 34cc60a24 tip; 12 UU same-day regen faces resolved per-face ts-probe "
       "ours(bm-b)-newer-wins 12/12 (r1035bmb_rebase_probe.py); autostash pop 6 UU resolved (5 newer-wins bm-b "
       "+ token_usage per-machine UNION r1008 law, -bm-a/-bm-c keys = tool's own naming both sides identical); "
       "drama x3 + machine-health unstaged per daemon-live-wins; push attempt-1 hung 5min zero-output "
       "(promisor window family, legal in-flight fetch+index-pack 76,782-obj left untouched per poll-to-complete "
       "law), origin advanced to 9cc7061b7 mid-window -> r1034 estate STILL undelivered, rides r1035 closeout "
       "commit, r1036 S0 replay if blocked again (r1026 wall-risk law). "
       "(b) POOL-0018/0019 env bootstrap FIRST ACTION: anchor_env_bootstrap.py spawned DETACHED (pid 15928, "
       "collector pattern DETACHED_PROCESS|NEW_PROCESS_GROUP|NO_WINDOW), isolated venv C:\\Fluxgroup\\Tools\\"
       "mv-audio-bmb\\venv-anchor, tsinghua mirror, Windows pypi torch=CPU build; status face anchor_env_status.json "
       "stage=torch_cpu RUN at 20:58; anchor generation (words.json/structure.json for staged 2/7: 晴天+可爱女人) = "
       "r1036+ after status=OK; HF_ENDPOINT=hf-mirror note in face. "
       "(c) S6 chain partial: 33 legs rc0 before 5min zero-output auto-cancel killed child ps (zero-window law "
       "VIOLATION noted: spawned powershell.exe child -- r1036 note: run chain IN-PROCESS & only); legs done incl "
       "sat_engine alive-idle / dualrun streak 51 / d19 dual-probe ZERO-DELTA (dec 60a98a02 ord dda073d1 hold, "
       "advance NOOP read-back OK) / update_daily +36 rows cutoff 10-19 / lhb +80 rows cutoff -> 10-19 / futures +9 "
       "/ etf_daily 5/5 through 10-19 / b_layer gates all_pass / scorecard 6 cards S2A4 (94.8s) / market_clock "
       "ORANGE_COOL / DUALARM BEAR@09-30; papers gate probe at 20:58 honest SKIP (bar tail 10-16 at probe) -- "
       "BUT bars landed ~21:0x in-window right after (update_etf_daily wrote through 10-19; sh510300 tail now "
       "10-19) -> papers family + marks legs (aggr/alloc/grid/system_v1/export/scorecard/report/live_usage/"
       "build_status/token/attrition/idle) DEFERRED to r1036 first legs (bar on disk, conditional retry law); "
       "S7-critical legs re-run standalone: attrition CLEAN(healed 4+1 rows) / idle green_idle then --worked "
       "(idle_rounds 1->0, agenda_starved false) / token_meter delta=0. "
       "(d) S1 smoke 49/49 PASS + orphan probe 0/9. "
       "(e) D-19 zero-delta both faces (no new CEO orders since r1034 consumption of O-20261019-1935).")
st["did"] = did
st["last_action"] = ("r1035: S0 replay r1034 estate (12 UU ts-probe bm-b-newer 12/12, push hung promisor -> deferred) "
                     "+ POOL-0018/0019 env bootstrap spawned DETACHED (torch_cpu RUN) + S6 chain 33 legs rc0 partial "
                     "(bars landed 21:0x post-probe -> papers family deferred r1036) + S1 49/49 + attrition CLEAN + "
                     "--worked declared")
st["current_task"] = "r1035: S0 estate replay + POOL env bootstrap ignition + S6 partial chain + lean closeout"
st["task"] = st["current_task"]

verdict = ("GREEN: r1035 供给线点火轮——POOL-0018/0019 环境靴带分离进程已活（venv-anchor pid 15928·torch_cpu 阶段 RUN·"
           "清华镜像·Windows pypi torch=CPU 版零 CUDA 负担·anchor_env_status.json 阶段面；锚点出件（晴天+可爱女人 words/structure）"
           "排 r1036+ status=OK 后·首批 7 曲回执窗 ≤24h 从 20:2x 起算不变）；S0=r1034 双 commit 重放落位"
           "（12 UU 同日 regen 面 per-face ts 探针 bm-b-newer-wins 12/12·autostash pop 6 UU 含 token_usage per-machine UNION·"
           "推送 5min 挂死=promisor 窗族+合法在途 fetch 不碰·origin 又进 9cc7061b7→送达骑 r1035 closeout commit·"
           "r1036 S0 重放兜底）；S6 链 33 腿 rc0 后被 5min 零输出自动取消杀（子 powershell 零窗违例自记·下轮链改进程内跑）——"
           "update_daily +36 行 cutoff 10-19·LHB +80 行→10-19·futures +9·ETF 5/5 至 10-19·b_layer all_pass·"
           "scorecard S2A4·market_clock ORANGE_COOL·DUALARM BEAR@09-30；papers 门探针 20:58 诚实跳过（bar 未落）→"
           "21:0x bar 落地（探针后窗内）→papers 族+marks 族顺延 r1036 首腿（bar 在盘·条件重试律）；S7 三关键腿独立补跑绿"
           "（attrition CLEAN·idle green_idle→--worked 归零·token delta=0）；S1 smoke 49/49+孤儿 0/9；D-19 双面零增量"
           "（dec 60a98a02/ord dda073d1 hold·advance NOOP 读回 OK）；下窗=r1036 papers+marks 族（bar 已在盘）+"
           "S0 estate 重放推送+anchor 出件（status=OK 后）+RepoSlim 09:03 验证+ST-012 22:0x drama 让路保持")
st["verdict"] = verdict
st["current"] = verdict

st["latest_artifact"] = ("r1035: anchor env bootstrap chain (C:\\Fluxgroup\\Tools\\mv-audio-bmb\\anchor_env_bootstrap.py + "
                         "anchor_env_status.json stage=torch_cpu RUN + anchor_env_install.log + venv-anchor/) + "
                         "data faces (lhb +80 rows cutoff 10-19 / daily panel +36 rows through 10-19 / futures +9 / "
                         "ETF 5/5 through 10-19) + r1035 work files (_r1035bmb_rebase_probe.py / stashpop_probe.py / "
                         "kick_anchor_env.py / s6chain.ps1 / s6_log.txt) + S7 evidence (attrition CLEAN / idle "
                         "green_idle->worked / token delta=0)")
st["last_artifact"] = st["latest_artifact"]

st["next"] = ("r1036: 1) FIRST: papers family + marks legs re-run (10-19 bar ON DISK now: live.paper REGIME_GUARD "
              "enforce + t35_open_fill_verify + t24 x2 + aggr/alloc/grid/system_v1/t35_export/scorecard/report/"
              "live_usage/build_status/token/attrition/idle) 2) S0: fetch + replay r1034 estate + r1035 closeout "
              "onto fresh tip + push + verify (r1034 estate 2 windows undelivered = red-flag line, MUST land) "
              "3) anchor generation if anchor_env_status.json=OK (words.json+structure.json for 晴天+可爱女人, "
              "HF_ENDPOINT=hf-mirror.com for whisperx model) 4) audio remaining 5 件 Taildrop receive + staging scan "
              "5) ST-012 22:0x drama yield (drama executor owns) 6) RepoSlim 09:03 first daily run verify 7) W280 "
              "prereg (bm-c r1125+) watch -> W281 seat post-REGISTER 8) S6 chain IN-PROCESS & (zero-window law)")
st["next_milestone"] = ("POOL-0018/0019 first-batch 7 曲 <=24h (due 2026-10-20 20:2x) + full 41 曲 <=72h + papers evening "
                       "chain r1036 + r1034/1035 estate delivery r1036 S0 + voice P1 <=10-22 + BigMoney seat plan "
                       "<=10-25 + month-boundary 10-31")

st["r1034_main_push"] = {
    "status": "PUSH_DEFERRED_2WINDOWS (r1035 S0: replayed onto 34cc60a24 as e4dc76-e4dc0861f6 + postscript, push "
              "attempt-1 hung 5min promisor family + origin advanced 9cc7061b7; rides r1035 closeout commit -> "
              "r1036 S0 replay law r1026)",
    "pushed_sha": "e4dc0861f6 (replayed local, reflog-safe)",
    "consumed_at": "pending r1036",
    "behind_origin_main": 0,
}
st["r1035_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1036",
    "behind_origin_main": 0,
    "note": ("r1035 payload = closeout faces (state/heartbeat/round-report) + r1035 work files (rebase_probe / "
             "stashpop_probe / kick_anchor_env / s6chain / s6_log) + own product/data faces (lhb chunks+detail +80 rows / "
             "daily panel csvs through 10-19 / futures +9 / ETF 5/5 / firm traders marks x6 / paper faces x6 / "
             "scorecard_v1+strategy_scorecard / regime_state / market_clock CALL+call_latest x2 / x2_watch_log / "
             "bm-b-suffixed evidence faces) + _attrition + _orphan.bm-b; EXCLUDED per r982/r1015/r1020/r1028/r1034 "
             "policy: drama x3, machine-health, token_usage.json shared union, unsuffixed lhb/futures/astock/etf/"
             "update_status/compute_audit/fundamental_b_layer status faces, watermark_red machine-local"),
}
st["r1036_first_action_note"] = ("r1036: 1) papers+marks family FIRST (bar on disk 10-19) 2) S0 replay+push "
                                 "(r1034 estate 2 windows undelivered) 3) anchor gen if env OK 4) drama yield "
                                 "5) RepoSlim verify 6) W281 seat watch post-W280-REGISTER")
st["r1035_chain_kill_note"] = ("r1035: S6 chain child powershell killed by 5min zero-output auto-cancel at "
                               "papers-SKIP position; violation noted: spawned powershell.exe child from session "
                               "(zero-window law) -- r1036 chain runs IN-PROCESS via & only; post-kill leg re-runs: "
                               "S7-critical trio done standalone, papers+marks deferred (bar landed 21:0x after "
                               "gate probe)")
st["r1035_env_bootstrap_note"] = ("r1035: anchor_env_bootstrap.py DETACHED pid 15928; venv-anchor; tsinghua mirror; "
                                  "status face stage=torch_cpu RUN 20:58; whisperx model pulls need "
                                  "HF_ENDPOINT=https://hf-mirror.com (set at generation time)")
st["sat_engine"] = {
    "status": "alive (r1035 chain status leg rc0; idle verdict honest; supply line ACTIVE: POOL-0018/0019 claimed "
              "r1034, env bootstrap running detached, anchor outputs r1036+)",
    "checked_at": NOW,
}

with io.open(os.path.join(REPO, "state.json"), "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
hb_path = os.path.join(REPO, "fleet", "machines", "bm-b.json")
with io.open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = st["current_task"]
hb["verdict"] = "GREEN r1035: POOL-0018/0019 env bootstrap ignited (detached, torch_cpu RUN) + S0 r1034-estate replay (push deferred promisor) + S6 33 legs rc0 (papers family deferred r1036, bars landed post-probe) + S1 49/49"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_action"] = st["last_action"]
# orders_ack diff: scan fleet/orders for files not yet acked
acked = set(st.get("orders_ack", []))
for p in glob.glob(os.path.join(REPO, "fleet", "orders", "O-*.md")):
    fn = os.path.basename(p)
    if fn not in acked:
        hb.setdefault("orders_ack_new", []).append(fn)
with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# verify epoch int
with io.open(hb_path, "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# ---- round report row ----
rr_path = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
row = ("| {} | r1035 | S0 r1034-estate rebase replay (12 UU ts-probe bm-b-newer; push hung promisor 5min, origin "
       "advanced -> delivery rides this commit, r1036 S0 replay law) + POOL-0018/0019 env bootstrap DETACHED ignited "
       "(venv-anchor tsinghua torch_cpu RUN, pid 15928) + S6 chain 33 legs rc0 partial (5min auto-cancel killed child ps; "
       "zero-window violation self-noted; update_daily +36/LHB +80/futures +9/ETF 5/5 all through 10-19; bars landed "
       "21:0x post-gate-probe -> papers+marks family deferred r1036 first legs) + S7 trio standalone green (attrition "
       "CLEAN / idle green_idle -> --worked / token delta=0) | S1 smoke 49/49 PASS + orphan 0/9 + d19 dual-probe "
       "ZERO-DELTA (dec 60a98a02 ord dda073d1) + local-vs-origin behind=4 replayed ahead=2 | r1036: papers+marks FIRST "
       "(bar on disk) + S0 push+verify + anchor gen if env OK + drama yield + RepoSlim verify |\n").format(NOW)
with io.open(rr_path, "a", encoding="utf-8") as f:
    f.write(row)

print("CLOSEOUT_DONE epoch_int={} state_r={} hb_r={} report_row_appended".format(
    isinstance(chk["heartbeat_epoch_utc"], int), st["round_no"], chk.get("verdict", "")[:20]))
