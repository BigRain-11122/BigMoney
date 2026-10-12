# -*- coding: utf-8 -*-
"""r908 bm-b closeout: state + heartbeat + O-0739 receipt + round report + pit entry + commit/push."""
import json, os, subprocess, time

ROOT = os.path.dirname(os.path.abspath(__file__))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def w(path, text):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


# ---------- 1. O-20261012-0739 receipt line (bm-b leg) ----------
p = os.path.join(ROOT, "fleet", "orders", "O-20261012-0739-bm-c.md")
t = open(p, encoding="utf-8").read()
old = "- [ ] bm-b resume+animatic 回执："
new = ("- [x] bm-b resume+animatic 回执（r908·2026-10-13 00:2x）：resume 已确认（r907 复电复活+本轮循环在跑）"
       "·animatic 53 单 int4 在烧（批 9/53·KN08 in-flight；双断电+llama VRAM 挤压两度停摆均同轮复活·根因已治"
       "=resume 重生 llama-server 补杀+keepwarm.pause marker 在位）·O-1917 三件回执=G 系/热点池评分件已产"
       "（POOL-SCORED topics 重落地 surgery 在飞）+BigHouse 首件 r896 已交·orders_ack 已更新。")
if old in t and new.split("：")[0] not in t:
    w("fleet/orders/O-20261012-0739-bm-c.md", t.replace(old, new, 1))
    print("O-0739 receipt line filled")
else:
    print("O-0739 receipt line: already/absent (skip)")

# ---------- 2. state.json ----------
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = st.get("round_no", 908) + 1
st["round_no_label"] = "r908"
st["clock_read"] = NOW
st["last_round_at"] = NOW
st["last_seen"] = NOW
st["last_action"] = "r908: i2v batch revival #2 (llama VRAM squeeze root-caused+remediated) + predecessor absorb + orders/D-19 consume + RAM slot receipt"
st["last_action_at"] = NOW
st["now_active"] = "i2v animatic batch re-burning (9/53, KN08 in-flight, ComfyUI r908c + driver r908c, GPU 100%/7.4GB/176W under 180W cap)"
st["current_task"] = "r908 closeout: i2v batch watch (9/53 burning) + group surgery push in flight"
st["latest_artifact"] = "KN_KN07.mp4 @00:2x (batch 9/53, revival #2 proof) + results/_r908bmb_ram_slots.json (O-2250 receipt)"
st["next"] = ("r909: i2v batch watch (KN08+ -> 53/53 ETA 10-13 morning, then remove keepwarm.pause marker) > "
              "surgery push verify (POOL-SCORED topics re-land + token ledger row) > Speech-02+Music3 装机验证批 (bm-b lane, O-2215 承接) > "
              "trial-labor standing line (pool refill >=3) > unity-mcp POC due 10-13 12:00 > W18+E15 48h CEO reports (10-13 11:2x / 10-14 00:44) > BigHouse T-2 <=10-15")
st["next_milestone"] = ("i2v 53/53 ETA 10-13 morning under 180W cap; E15 48h report 10-13 11:2x; W18 48h report 10-14 00:44; "
                        "unity-mcp POC due 10-13 12:00; RAM upgrade install on delivery (2 free DIMM slots confirmed)")
st["did"] = ("r908: (1) i2v batch death #2 root-caused: machine-state resume respawned llama-server 23:24:31 (4.7GB VRAM held, "
             "keepwarm.pause marker ignored by resume actor) -> ComfyUI r907c int4 render OOM death ~00:05:51 -> driver POLL-LOST+ABORT "
             "(KN07-12 retried); remediated per r903/r904 valve law: llama-server killed (VRAM 4696->1014MiB), ComfyUI r908c + driver r908c "
             "relaunched -> SKIP-resume proof (KN01-06 skipped, KN07 SUBMITTED->SAVED, KN08 burning, GPU 100%/176W); "
             "(2) predecessor r908-attempt absorbed (r878/r881 continuation precedent): full S6 chain products (10-12 bar pulled cutoff=2026-10-12, "
             "paper family accrued 23:46, export 00:04, REPORT/LIVE-2026-10-13 built) + hung surgery script killed+relaunched; "
             "(3) S0: fetch clean (night net recovered), r907 detached push landed (ahead=0/behind=0); "
             "(4) S0.5: orders_ack +3 (O-20261010-2325 own + O-20261012-0739-bm-c consumed+receipt line filled + O-20261012-0940-bm-a read=bm-a ticket); "
             "D-19 dual delta consumed (dec 358ba69b->fb378423: D-20261012-03 BigDomain/D-20261013-01/02 HQ domain zero bigmoney-action rows "
             "except six-task E1 window evidence=this loop; ord 33aee170->bd29c5c5: 10-12 22:0x-23:5x batch, bm-b faces=定岗承接单 "
             "(ComfyUI revived/监听:8790 alive/heartbeat=revived/Speech-02+Music3=pending) + O-2250 RAM slot receipt executed "
             "(AB350M-Gaming 3-CF, 2/4 DIMM 16+8GB 2666MHz, 2 free slots, results/_r908bmb_ram_slots.json) + 满载包 GPU telemetry wired); "
             "(5) fresh S6 evidence legs: dualrun streak 51 ZERO-DRIFT, compute_audit flags pool_starvation/supply_floor (pool empty=standing line, "
             "GPU burn legal per O-1612), py_watermark py_low_with_work_cands (burn window); "
             "(6) IntradayMarks Monday 09:25 missed-fire accounted (machine off 03:03-22:20, honest; Tuesday 10-13 09:25 armed); "
             "(7) smoke 49/49, SAT alive idle rc0, FleetLink :8790 alive post-reboot, idle_trigger --worked (idle_rounds=0)")
st["verdict"] = ("GREEN-with-flags: i2v batch revived #2 and burning at full cadence (9/53, GPU 100%/176W under cap = CEO 榨干令 compliance); "
                 "flags=pool_starvation/supply_floor (pool empty, standing line next round; O-1612 burn-window waiver applies) + "
                 "py_low_with_work_cands (honest: CPU lanes have astock refresh + backfill workers running); observe=group surgery push in flight")
st["task"] = st["next"]
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["orphan_face"] = 1
st["orphan_face_note"] = ("r908 round probe 00:12: py_faces=19 orphans=1 = i2v driver face (false-positive on 60s poll sleep); "
                          "driver then self-exited cleanly (POLL LOST->ABORT) after server death; no kill needed; legal detached = ComfyUI r908c + driver r908c (relaunched)")
st["orphan_faces"] = 1
st["last_decisions_sha"] = "fb378423fedeaaa7138d6cb3dcfc885703f5c333"
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_decisions_sha_method"] = ("r908 probe via results/_r686bmb_d19_check.py (r537 SHA-1 raw-blob PIN); dec delta 358ba69b->fb378423 consumed: "
                                   "C-20261012-01 顶层梳理 (HQ owner) + D-20261012-03 (BigDomain) + D-20261013-01 (bigmoney 六任务 E1 复启窗 00:00-08:00 "
                                   "在飞=本循环即证据) + D-20261013-02 (HQ Phase0) -- 零 bm-b 执行行如实; 零新增待执行")
st["last_orders_at"] = NOW
st["last_orders_read_at"] = NOW
st["last_orders_sha"] = "bd29c5c5f3cada6b1afc4dee9a2ad75f64170270"
st["last_orders_sha_note"] = ("r908 probe: ord delta 33aee170->bd29c5c5 consumed (10-12 22:0x-23:5x batch); bm-b 执行面 = 定岗承接单四项 "
                              "(ComfyUI=revived/监听:8790=alive/心跳=revived/Speech-02+Music3=pending next rounds) + O-2250 RAM 槽位回执单 executed "
                              "(results/_r908bmb_ram_slots.json) + O-0739 §3 animatic/O-1917 回执行 filled; MV 死线令/榨干令=standing (animatic 批即执行面)")
st["heartbeat_epoch_utc_face"] = "kept in fleet/machines/bm-b.json"
st["sync"] = {"last_push_ts": NOW, "note": "r908 closeout push in-round; delivery self-proof = fetch+rev-list below"}
w("state.json", json.dumps(st, ensure_ascii=False, indent=1))
print("state.json written, round_no ->", st["round_no"])

# ---------- 3. heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
acks = hb.get("orders_ack", [])
for a in ["O-20261010-2325-bm-b.md", "O-20261012-0739-bm-c.md", "O-20261012-0940-bm-a.md"]:
    if a not in acks:
        acks.append(a)
hb["orders_ack"] = acks
hb["last_seen"] = NOW
hb["now_active"] = "i2v animatic batch burning (9/53, KN08 in-flight) + group surgery push in flight"
hb["current_task"] = "r908 closeout; r909 = batch watch + Speech-02/Music3 lane + trial-labor refill"
hb["verdict"] = "GREEN-with-flags (batch revived #2 burning; pool_starvation/supply_floor flags = standing line, O-1612 waiver)"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["gpu"] = {"util_pct": 100.0, "mem_used_mb": 7887, "power_w": 176.2, "face": "i2v int4 animatic batch (ComfyUI r908c)"}
hb["ram"] = {"total_gb": 24, "slots_populated": 2, "slots_free": 2, "board": "Gigabyte AB350M-Gaming 3-CF", "receipt": "results/_r908bmb_ram_slots.json"}
w("fleet/machines/bm-b.json", json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written; epoch int OK:", chk["heartbeat_epoch_utc"], "; acks:", len(acks))

# ---------- 4. round report ----------
line = (
    NOW + " | r908 bm-b (continuation round - predecessor r908-attempt 25min-kill absorbed same round, r878/r881 precedent) | "
    "dept:engineering (i2v batch revival #2 root-caused+remediated + predecessor S6 absorb + S0/S0.5/S7 full chain) + dept:舰队 (D-19 dual delta + O-2250 RAM 回执单 + 定岗承接单) | "
    "实况三行：当前活=i2v animatic 批 9/53 在烧（KN08 in-flight·ComfyUI r908c·GPU 100%/7421MiB/176W under 180W cap）+group surgery push 在飞；"
    "最近实物=KN_KN07.mp4 @00:2x（批二次复活实证）+results/_r908bmb_ram_slots.json（O-2250 槽位回执·AB350M-Gaming 3-CF·2/4 DIMM 16+8GB 2666·2 空槽）+REPORT/LIVE-2026-10-13（前身吸收）；"
    "下个里程碑=i2v 53/53 ETA 10-13 晨（批毕移 keepwarm.pause marker）·E15 48h 报 10-13 11:2x·W18 48h 报 10-14 00:44·unity-mcp POC due 10-13 12:00 | "
    "orphan-faces=1（probe 00:12·py_faces=19·孤儿=i2v driver 面假阳[60s 轮询假眠]·驱动随后 POLL LOST→ABORT 自清退出零击杀·合法分离态=ComfyUI r908c+driver r908c） | "
    "WM-VERDICT: red=true, lane=pool-batch-runnable-idle-low-cpu = i2v burn window (O-1612 GM waiver 合法·GPU 100%=CEO 榨干令合规面; "
    "py_low_with_work_cands 如实: astock refresh+backfill workers CPU 在飞; 池空=试用劳动力常设线下轮补 ≥3) | "
    "did: ①批二次死亡根因定谳=machine-state resume 23:24:31 重生 llama-server（无视 keepwarm.pause marker·占 4.7GB VRAM）→ComfyUI r907c int4 渲染 33min OOM 死 ~00:05:51→"
    "driver POLL LOST→ABORT（KN07-12 待重烧）——按 r903/r904 释放阀律同轮治愈=杀 llama-server（VRAM 4696→1014MiB）+ComfyUI r908c+driver r908c 重落→"
    "SKIP-resume 实证（KN01-06 skip·KN07 SUBMITTED→SAVED·KN08 烧中·GPU 100%/176W）·坑例直写 research/pit-machine.md；"
    "②前身 r908 尝试吸收（S6 全链产物：10-12 bar 已拉 cutoff=2026-10-12·paper family 23:46 计提·export 00:04·REPORT/LIVE-10-13·post_review 10-13）+hung surgery 脚本杀后重飞（POOL-SCORED topics 重落地+token ledger 首行）；"
    "③S0=fetch 净（夜网已愈）·r907 detached push 已落地（ahead=0/behind=0 送达自证闭环）；"
    "④S0.5=orders_ack +3（O-20261010-2325 自有全面开工令[已执行+push 落地] + O-20261012-0739-bm-c 全量消费[§3 bm-b 腿=animatic 线在跑+O-1917 三件回执行已填] + O-20261012-0940-bm-a 实读[bm-a 工单零 bm-b 动作]）·"
    "D-19 双 delta 消费（dec 358ba69b→fb378423=C-20261012-01/D-20261012-03/D-20261013-01/02·零 bm-b 执行行[六任务 E1 复启窗证据=本循环]；ord 33aee170→bd29c5c5=10-12 22:0x-23:5x 批·bm-b 面=定岗承接单[ComfyUI 已复/监听 :8790 alive/心跳复活/Speech-02+Music3 候下轮]+O-2250 RAM 回执单 executed+满载包 GPU 遥测已入心跳）；"
    "⑤S6 新鲜证据腿=dualrun streak 51 ZERO-DRIFT+compute_audit flags pool_starvation/supply_floor（池空常设线·O-1612 豁免面）+py_watermark py_low_with_work_cands（烧录窗）；"
    "⑥IntradayMarks 周一 09:25 missed-fire 记账（03:03-22:20 断电关机·诚实漏烧·周二 10-13 09:25 已 armed 实读）；"
    "⑦smoke 49/49+SAT alive idle rc0+loop pin=2 no-op+watchdog 重载+双爪幂等重装+FleetLink :8790 alive+idle_trigger --worked（idle_rounds=0） | "
    "验证证据=log-bmb-r908c.out.txt（SKIP×6+KN07 SUBMITTED/SAVED+KN08 SUBMITTED）+nvidia-smi 100%/7421MiB/176W+results/_r908bmb_ram_slots.json+"
    "results/_orphan_face_probe.bm-b.json+watermark.jsonl 两 Probe+_r908bmb_s6 证据面+smoke 49/49 | "
    "unacked_orders=0 | 登记簿零命中声明：本轮无清扫/归档/删除动作（前身 surgery 脚本=新增件非清理类） | "
    "本地未达 origin commit 数=N（收口 push 后 fetch+rev-list 自证，见下） | "
    "下轮指针=r909：i2v 批值守（KN08+→53/53·停滞>4h 单按 README §4 让渡评）>surgery push 验证（ls-remote+out 件）>Speech-02+Music3 装机验证批（bm-b lane·O-2215 承接·许可先核）>"
    "试用劳动力常设线（池补 ≥3·W 带链状态盘点）>unity-mcp POC due 10-13 12:00>W18+E15 48h CEO 报（10-13 11:2x/10-14 00:44）>BigHouse T-2 ≤10-15 | [r908 bm-b]\n"
)
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report appended")

# ---------- 5. pit-machine entry ----------
pit = os.path.join(ROOT, "research", "pit-machine.md")
entry = (
    "- [2026-10-13 00:2x r908 bm-b] **machine-state resume 无视 keepwarm.pause marker 重生 llama-server→重 GPU 批 VRAM 挤压致死坑**"
    "（i2v 批二次停摆实弹）：machine-state.ps1 -Mode resume 按其设计重钉 Ollama 常驻（10-13 23:24:31 实录 StartTime），"
    "但不消费 Tools\\Ollama\\keepwarm.pause marker（marker 只门 KeepWarm/serve-warm 监督族）→llama-server 4.7GB 驻留与 ComfyUI int4 渲染 7.4GB 需求同挤 8GB 卡"
    "→r907c 渲染 33min 后 OOM 死（comfy 日志零落账·驱动侧 POLL LOST→ABORT 自清链）→律=**resume 后若 marker 在位，点任何重 GPU 批前必先补杀 llama-server "
    "（Stop-Process llama-server→nvidia-smi 验 free≥7GB）再点火**；驱动 h3_i2v_album.py 轮询假眠面=孤儿探针 60s 假阳已知面（CPU delta 0≠死·看 log 尾+mp4 落盘判活）。\n"
)
with open(pit, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
sz = os.path.getsize(pit)
print("pit-machine.md appended, size:", sz, "(<=30720 required)")

# ---------- 6. commit + push + delivery self-proof ----------
def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

rc, out = run("git add -A")
print("add rc:", rc)
rc, out = run('git commit -m "round 908: i2v batch revival #2 (llama VRAM squeeze root-caused via machine-state-resume respawn, r903/r904 valve law remediation, 9/53 burning) + predecessor S6 absorb + O-2250 RAM slot receipt + orders/D-19 consume + O-0739 receipt line"')
print("commit rc:", rc, "|", out.strip().splitlines()[-1] if out.strip() else "")
rc, out = run("git push")
print("push rc:", rc, "|", out.strip()[:200])
rc, out = run("git fetch origin")
print("fetch rc:", rc)
rc, out = run("git rev-list --count origin/main..HEAD")
ahead = out.strip()
rc, out = run("git rev-list --count HEAD..origin/main")
behind = out.strip()
print("DELIVERY: ahead=%s behind=%s" % (ahead, behind))
