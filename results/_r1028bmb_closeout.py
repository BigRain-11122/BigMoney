# r1028 bm-b S7 closeout: round report row + dual-face state + heartbeat (r1020 law) + CODELY row
import json, time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())
RN = 1028

DID = ("r1028: (a) S0 clean: fetch behind=0/ahead=0 (r1027 estate fully landed pre-round, zero delivery burden); orphan probe 0/7 faces. "
       "(b) D-19 FIRST ACTION + S7-tail dual-scan: ORD advanced 57e209fd->3311145e->bd527746 (sprint-window bm-a high cadence, mid-round "
       "new rows landed between probes -- tail re-scan consumed them per law); 5 rows total consumed: 16:1x NATS bus dispatch 【@bm-b】 "
       "(EXECUTED this round, see (c)); 16:14 bm-d hardware arrival row (informational, zero bm-b action); 16:26 daily-output-report order "
       "(carrier cph4/fleet/DAILY-OUTPUT-REPORT.md live on origin -- BigMoney row explicitly deferred by bm-a to 22:0x self-report, "
       "obligation carried in state next); 16:39 unified-quality-soul law (content-production domain, zero BigMoney obligation); 16:4x MV "
       "directors research closeout (BigStream domain, zero action). dec 95879dd9 hold, mirrors synced 3 (r1090 dual-face). BM-side S0.5: "
       "orders diff EMPTY (all O-files acked), inbox 0 unread. (c) NATS bus node dispatch EXECUTED (3 steps, all green): bootstrap pinned "
       "nats-server v2.15.1 + natscli 0.5.0 -- direct github.com HUNG 5min zero-output (auto-cancel) -> machine recipe gh-proxy.com prefix "
       "used, idempotent re-run 'NATS-BIN OK'; register FluxGroup-NatsHB via canonical task-register (hidden wscript chain, every:1m, "
       "LogonType=S4U readback-enforced, deploy=ignite observed fire 16:46:12 result=0); BUS OK role=node node=bm-b; tailscale netcheck+status "
       "full (UDP true, UPnP mapping, nearest DERP sfo 129.7ms, bm-a active relay sin); KV FLEET_STATE state.bm-b live rev 66->79 continuous "
       "1-min publishing (state.bm-a present, state.bm-c pending bm-c side -- three-machine green acceptance waits on bm-c); receipt "
       "MSG-1648-bmb-natsbus.md written to group inbox (new unique filename zero pull-hazard). Install divergence: stable root "
       "C:\\Fluxgroup\\Tools\\nats (OUTSIDE any repo -- group tree 32-behind with Tools/nats in incoming set; tree-write would abort fleet "
       "worker pull), 5 ps1 blob-sha-verified vs origin + task-register/InvisibleRunner/fleet-nodes companions; tradeoff documented in "
       "receipt (ps1 upgrades need poke + re-extract, bm-a aware). card-lint exception: --min rc=2 (missing hard receipt-window + O-number) "
       "-> CEO-order-immediacy precedence (card carries CEO 12:0x verbatim order + sprint window), defects cured in receipt (window= "
       "same-round met; lineage=CEO 12:0x + R-20261019-fleet-realtime-comm-01 + orders row), exception honestly recorded for dispatcher. "
       "(d) S6 chain 43 legs rc0 2.5min (_r1028bmb_s6chain.ps1, papers conditional): papers family honest SKIP x4 (10-19 bar not landed at "
       "16:49, cutoff 10-16, sina evening window ~20:4x; evening rounds auto-fire on panel advance); smoke 49/49; idle --worked declared "
       "idle_rounds=0 agenda_starved=false; pool_dualrun ZERO-DRIFT streak 51; supply_floor 0/3 honest starvation standing (W279 prereg "
       "derive = bm-c r1121 first action, bm-b N1 feed gated after prereg lands); lane guards r701 third-signal veto x4 (scorecard/"
       "paper_export/daily_scorecard/build_status, bm-a origin fresh 18-19min); REPORT-2026-10-19 + LIVE-2026-10-19 regen (ORANGE cap 50%); "
       "token_meter saved; attrition healed-clean rc0; regime_gate_dualarm idempotent same-asof (DUALARM-2026-09-30 unchanged bytes). "
       "(e) closest-to-external-release step (16:04 KPI order): paper-lane daily scoreboard faces live (REPORT/LIVE regen) + month-boundary "
       "10-31 first exam unchanged standing.")

VERDICT = ("GREEN: r1028 NATS 总线节点铺装轮（本机直派工执行）+D-19 冲刺窗 5 行消费轮+papers 诚实跳过轮——【@bm-b】NATS 派单三步全绿"
           "（bootstrap 钉版双验·直连 GitHub 挂死 5min→gh-proxy 机律配方；FluxGroup-NatsHB 注册=隐藏链+S4U+读回验证+点火 result=0；"
           "BUS OK node=bm-b·KV state.bm-b rev 66→79 每分钟活状态在链·state.bm-c 候 bm-c 侧铺装后三机全绿）；安装面=仓外稳定根 "
           "C:\\Fluxgroup\\Tools\\nats（集团树 32 落后+Tools/nats 在 incoming 集内·树写必炸 worker pull——git show 直提+blob sha 恒等+伴生件"
           "复制·升版走 poke+重提·差异已入回执）；card-lint --min rc=2（缺回执窗+O 号）→CEO 令即时律位阶执行+回执内治愈+例外留痕；"
           "D-19 5 行全收（NATS 派单=执行/bm-d 到位行=信息面/16:26 每日产出汇报令=BigMoney 行挂 22:0x 自报〔bm-a 明示不代填〕/"
           "16:39 质量灵魂律+16:4x MV 收口=内容域零 BM 义务）·水位 57e209fd→bd527746（dec 95879dd9 hold·mirrors synced 3）；"
           "S6 43 腿 rc0 2.5min（papers 族 SKIP x4=bar 未落 cutoff 10-16·晚间轮条件重试；supply_floor 0/3 常设饿 W279 prereg 候 bm-c）；"
           "下窗=r1029 D-19 首动作+papers 条件重试+22:0x 日进化班 DOR BigMoney 行自报（真实律四条）+ST-012 夜窗 v2Pro 门")

NEXT = ("r1029: 1) D-19 fresh probe FIRST ACTION per law (ord=bd527746 through 16:4x; sprint window bm-a high cadence -- expect more rows) "
        "2) papers conditional retry when 10-19 bar lands (evening window ~20:4x-21:xx; live.paper+t35_open_fill+t24 prospect+export family) "
        "3) 22:0x daily evolution shift: DAILY-OUTPUT-REPORT.md BigMoney row self-report per CEO 16:26 order (真实律四条: 对外产出 0 件如实/"
        "内部交付物单列/在飞一句; carrier is a TRACKED group file -- zero-touch law: deliver row content via cph4/fleet/inbox MSG to bm-a or "
        "FleetLink pusher channel, never raw tree edit) 4) ST-012 night window 22:0x: REBUILD-PLAN-v2 full read + v2Pro profile adaptation gate "
        "BEFORE first LoRA train run (8G VRAM profile) 5) supply_floor watch: W279 prereg = bm-c first action -> bm-b N1 pool feed after it lands "
        "6) NATS follow-ups: watch state.bm-c appear (three-machine green acceptance pending bm-c side); if bm-a upgrades nats ps1s, re-extract "
        "per MSG-1648 recipe (poke + blob sha + git show re-materialize) 7) RepoSlim first daily run tomorrow 09:03 live-anchor verify "
        "8) audit-order KPI line carried every round (closest-to-external-release step)")

ARTIFACT = ("NATS bus node LIVE: FluxGroup-NatsHB (S4U every:1m, fire result=0) + KV FLEET_STATE state.bm-b rev 79 continuous + MSG-1648-bmb-natsbus.md "
            "(group inbox receipt with full netdiag + install divergence + lint exception) + _r1028bmb_nats_install.py (blob-sha verified extraction) "
            "+ _r1028bmb_s6chain.ps1/_r1028bmb_s6_log.txt (43 legs rc0) + D-19 ord advance bd527746 (5 rows) + REPORT/LIVE-2026-10-19 regen")

ROW = (f"{ts} | r1028 | WM verdict: GREEN（red=false @16:48 lane=insufficient_history 1-sample window）| 距对外发布最近一步=纸盘战绩面日更"
       f"已上线（REPORT/LIVE-2026-10-19 regen ORANGE cap 50%·月界 10-31 首考=A5 验收面·常设线不动）| 当前活=【@bm-b】NATS 总线铺装派单"
       f"三步全绿收口（bootstrap 钉版 v2.15.1/v0.5.0·直连 GitHub 挂死 5min→gh-proxy 机律配方救活；FluxGroup-NatsHB 注册=隐藏链+S4U+读回验证+"
       f"点火 16:46:12 result=0；BUS OK node=bm-b·KV state.bm-b rev 66→79 每分钟活状态在链·netdiag 全文入回执）+D-19 冲刺窗 5 行消费"
       f"（NATS 派单=执行/bm-d 到位行=信息面/16:26 每日产出汇报令=BigMoney 行挂 22:0x 自报〔bm-a 明示不代填〕/16:39 质量灵魂律+16:4x MV 收口="
       f"内容域零 BM 义务）·水位 57e209fd→bd527746（dec 95879dd9 hold·mirrors synced 3）| 安装面差异=仓外稳定根 C:\\Fluxgroup\\Tools\\nats"
       f"（集团树 32 落后+Tools/nats 在 incoming 集内·树写必炸 worker pull→git show 直提 5 ps1 blob sha 恒等+task-register/InvisibleRunner/"
       f"fleet-nodes 伴生复制·升版走 poke+重提·已入回执）；card-lint --min rc=2（缺回执窗+O 号）→CEO 令即时律位阶执行+回执内治愈+例外留痕"
       f"（建议 dispatcher 行内单带齐五要素）| S6 43 legs rc0 2.5min（papers 族 SKIP x4=10-19 bar 未落 cutoff 10-16·晚间轮条件重试；smoke 49/49；"
       f"orphan 0/7 面；idle --worked idle_rounds=0 agenda_starved=false；pool_dualrun streak 51；supply_floor 0/3 常设饿 W279 prereg 候 bm-c；"
       f"lane guards r701 third-signal veto×4〔bm-a origin fresh 18-19min〕）| S0.5 BM 侧=orders 差集空+inbox 0 | evidence: KV get state.bm-b "
       f"rev 79 实证+S4U 读回+fire result=0+d19 advance read-back OK mirrors synced 3+未达 origin commit 数=0（closeout commit 后 push+fetch 验证）"
       f"| r1029: 1) D-19 fresh probe 首动作 2) papers 条件重试（bar 晚间窗）3) 22:0x DOR BigMoney 行自报（真实律四条·经 inbox MSG 通道零树触碰）"
       f"4) ST-012 夜窗 22:0x REBUILD-PLAN-v2+v2Pro 门后 LoRA 首训 5) W279 prereg 观察→bm-b N1 喂料 6) NATS state.bm-c 观察（三机全绿候 bm-c）"
       f"7) RepoSlim 明晨 09:03 首跑验证")

# 1) round report row (append via fresh-read-modify-write; multi-writer file law)
p = "logs/iteration-loop/round_reports.md"
with open(p, encoding="utf-8") as f:
    txt = f.read()
if not txt.endswith("\n"):
    txt += "\n"
txt += ROW + "\n"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(txt)

# 2) root state.json (authoritative face)
with open("state.json", encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "last_round_at": ts, "last_round_ts": ts, "last_seen": ts,
    "round": RN, "round_no": RN, "round_no_label": "r1028",
    "current_task": "r1028: NATS bus node dispatch EXECUTED (3 steps green, KV state.bm-b live) + D-19 5 ORD rows consumed + S6 43 legs rc0 (papers skip round 3)",
    "task": "r1028: NATS bus node dispatch EXECUTED (3 steps green, KV state.bm-b live) + D-19 5 ORD rows consumed + S6 43 legs rc0 (papers skip round 3)",
    "did": DID, "last_action": "r1028: NATS node LIVE (S4U task + KV state.bm-b rev 79) + D-19 5 rows consumed+advanced + S6 43 rc0 + papers honest skip",
    "last_action_at": ts, "now_active": "r1028 closed (closeout commit+push this round)",
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT,
    "verdict": VERDICT, "current": VERDICT,
    "next": NEXT,
    "orphan_face": 0, "orphan_face_note": "r1028 S6 chain probe (16:47): 7 py faces / 0 orphans",
    "sat_engine": {"status": "alive (r1028 chain status leg rc0; idle verdict; supply floor honest starvation 0/3 -- W279 prereg derive = bm-c first action; bm-b N1 pool feeds after prereg lands)", "checked_at": ts},
    "r1028_ord_note": "r1028: ORD consumed 5 rows -- first delta 57e209fd->3311145e (16:1x NATS dispatch 【@bm-b】EXECUTED + 16:14 bm-d hardware row informational), S7-tail delta ->bd527746 (16:26 daily-output-report order: BigMoney row deferred to 22:0x self-report per carrier / 16:39 unified-quality-soul law: content domain zero BM obligation / 16:4x MV directors closeout: BigStream domain); advance read-back OK, dec 95879dd9 hold, mirrors synced 3 (r1090 dual-face)",
    "r1028_nats_note": "r1028: NATS bus node deployment -- stable install root C:\\Fluxgroup\\Tools\\nats (zero tree-touch: group tree 32-behind + Tools/nats in incoming set; 5 ps1 blob-sha verified vs origin + task-register/InvisibleRunner/fleet-nodes companions); FluxGroup-NatsHB S4U every:1m fire result=0; KV state.bm-b rev 79 continuous; bootstrap GitHub-direct hang 5min -> gh-proxy machine recipe; state.bm-c pending bm-c side; receipt MSG-1648-bmb-natsbus.md in group inbox; card-lint --min rc=2 exception (missing receipt-window + O-number) resolved by CEO-order-immediacy precedence + cure-in-receipt",
    "r1029_first_action_note": "r1029: 1) D-19 fresh probe FIRST ACTION (ord=bd527746 through 16:4x; sprint cadence) 2) papers conditional retry on bar landing (evening) 3) 22:0x shift: DOR BigMoney row self-report via inbox MSG channel (tracked-file zero-touch) 4) ST-012 night 22:0x REBUILD-PLAN-v2 + v2Pro gate 5) NATS state.bm-c watch 6) RepoSlim tomorrow 09:03",
    "state_face_note": "r1028: mirror-written per r1020 dual-face law. authoritative face.",
})
st["sync"]["r1028_main_push"] = {
    "status": "PENDING (this commit)", "pushed_sha": "pending", "consumed_at": "pending r1029",
    "behind_origin_main": 0,
    "note": "r1028 payload = NATS dispatch products (nats_card/nats_install/ord_tail/dor evidence + MSG receipt content pointer) + closeout faces (state/heartbeat/round-report dual-face + CODELY row) + r1028 work files (s6chain driver+log + closeout) + own regen/product faces (daily_report/live_usage docs + collectors bm-b-lane faces + compute_audit/regime_state/update_status/b_layer/attrition/orphan/d19 faces); EXCLUDED per r982/r1015/r1020 policy: drama lane 3 faces (other-lane in-flight), machine-health, unsuffixed lhb/futures/astock/etf status, token_usage.json shared union face; base = 8171ac40ea origin tip fresh at S0 (behind=0)",
}
st["sync"]["last_push_ts"] = ts
st["sync"]["behind_origin_main"] = 0
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# 3) logs mirror face (only state_face_note differs)
st["state_face_note"] = "mirror face; authoritative round_no = repo state.json (r1020 law)"
with open("logs/iteration-loop/state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# 4) heartbeat bm-b.json
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "last_seen": ts, "ts": ts, "clock_read": ts, "heartbeat_epoch_utc": epoch,
    "round_no": RN, "round": RN,
    "task": st["current_task"], "current_task": st["current_task"],
    "did": "r1028: NATS node LIVE (FluxGroup-NatsHB S4U every:1m fire result=0 + KV state.bm-b rev 79) + D-19 5 rows consumed + S6 43 rc0 + papers honest skip",
    "last_action": "r1028: NATS node LIVE + D-19 5 rows consumed+advanced + S6 43 rc0 + papers honest skip",
    "last_action_at": ts,
    "verdict": VERDICT, "current": VERDICT, "next": NEXT,
    "now_active": "r1028 closed",
    "idle_rounds": 0, "agenda_starved": False,
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT,
    "last_orders_sha": "bd52774643163544011d328777374dc5e41391cb89d8e7fd20324269d0fbcdce",
    "last_decisions_sha": "95879dd945a05117610cc8e85dc61481957b387d86d2a717e66156de0b5cd0db",
    "orphan_face": 0,
})
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# 5) CODELY.md row-level append (S0.5 execution record; multi-writer file law)
CODELY_ROW = ("- [2026-10-19 16:5x r1028 bm-b] **NATS 节点铺装判例族（【@bm-b】跨机派单执行实录）**：①bootstrap 直连 github.com 在 bm-b 挂死 "
              "5min 零输出——节点机 GitHub release 下载一律 gh-proxy.com 前缀（本机环境律·bm-a 脚本不知节点机代理配方·@bm-c 铺装会撞同坑）；"
              "②集团树落后 32 且 Tools/nats 在 incoming 集内=树写必炸 worker pull——仓外稳定安装根 C:\\Fluxgroup\\Tools\\nats（git show origin "
              "直提+blob sha 恒等验证+task-register/InvisibleRunner/fleet-nodes 伴生复制·注册任务指向稳定路径·升版不自动跟进=发 poke 附新 blob "
              "sha 重提）；③card-lint --min 对 orders 行内派单 rc=2（缺回执窗+O 号）时承 CEO 令原话的卡按 CEO 令即时律位阶执行+缺项回执内治愈"
              "+例外如实留痕（dispatcher 席后续行内单带齐五要素）。")
with open("CODELY.md", encoding="utf-8") as f:
    ct = f.read()
if "NATS 节点铺装判例族" not in ct:
    if "### Reference" in ct:
        ct = ct.replace("### Reference", CODELY_ROW + "\n\n### Reference", 1)
    else:
        if not ct.endswith("\n"):
            ct += "\n"
        ct += CODELY_ROW + "\n"
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(ct)

# verify
for p2 in ("state.json", "logs/iteration-loop/state.json", "fleet/machines/bm-b.json"):
    d = json.load(open(p2, encoding="utf-8"))
    assert d["round_no"] == RN, p2
    if p2.endswith("bm-b.json"):
        assert isinstance(d["heartbeat_epoch_utc"], int) and "T" in d["clock_read"], "epoch int + T-separator laws"
print("closeout written: round_no=1028 dual-face + heartbeat + report row + CODELY row; ts=", ts)
