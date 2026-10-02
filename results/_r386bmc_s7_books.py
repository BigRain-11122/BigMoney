# -*- coding: utf-8 -*-
# r386 bm-c S7 books: state-bm-c.json + round_reports-bm-c.md + heartbeat + inbox move
import json, os, io, sys, time, shutil, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + now.strftime("%z")[-2:]
epoch = int(time.time())

# ---- 1. state-bm-c.json (LF) ----
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 386
st["last_round_at"] = "r386"
st["last_round_ts"] = ts
st["updated"] = ts_iso
st["updated_at"] = ts_iso
st["verify"] = ("r386: T-147 s1 DONE (results/lowamp_p3/s1_evidence_extract.json 11,292B: 16-face table + "
    "deep-axis per-start dists + double-nulls support + REFINE_BENCH sec.2 ranked variant table) + "
    "P3 sizing dead-letter diagnosed (spec['sizing'] never consumed by _cell_task/_cont_task -> judged 4 "
    "cells all ran invvol; LA-EQ = mislabeled invvol twin, pos-aligned 2760/2760 starts zero-diff; eq "
    "never truly burned in judged cells; sens L516-534 = only true sizing evidence, invvol p50 1.2135 > "
    "eq p50 1.1192; P3 judged-negative verdict unaffected) -> CODELY pit law + METHODOLOGY E09 card; "
    "S0 realign (GM 3 local commits = CAS twins on origin, content-superseded -> CAS update-ref + "
    "reset --mixed + 21 foreign faces origin-verbatim + 5 D restored, r585/r593/r595 laws); S0.5 orders "
    "147/147 zero-pending + D-19 MATCH 937A373D + no new group physical items for BigMoney; smoke 47/47; "
    "S6 28 legs rc0 (dualrun ZERO-DRIFT 51/3; bm-a heartbeat fresh 6min -> scorecard/dscore/build_status "
    "guards honest skip); attrition CLEAN 4 ledgers; self-heal 4/4 (pin=5 no-op, watchdog re-reg, both "
    "claws); watermark RED py_low_with_work_cands honest = O-2115 transition window (pool ready=0, N1 "
    "parked; work-cands T-146 GM-in-flight + T-147 mine; remedy = s2 prereg -> s3 pool by 10-09, s1 "
    "delivered this round = first leg of remedy)")
st["did"] = ("r386: T-147 s1 evidence extraction delivered + P3 sizing dead-letter found/diagnosed/law'd; "
    "S0 GM-twin realign; S6 28 rc0; books updated")
st["current_task"] = ("r386 wrap: closeout commit+push (s1 product + books + estate tools r382/383/385/386)")
st["next"] = ("(r387)(a) T-147 s2 family prereg draft from research/PREREG_TEMPLATE.md: new-evidence-delta "
    "declaration vs closed lowamp_daily_xs (M3 reopen channel), deep-axis named face (W {89,104} x N=2 x "
    "invvol evidenced sizing) as main judge 67-trade face per O-2115, deep-axis same-mask nulls in batch, "
    "exit-axis sec.0.6 double-channel verbatim, born-main-exam gates (g1_prime_v2/g2_registration_v2 "
    "shared lib no hand-copy), new runner MUST consume sizing explicitly + production-path selftest leg "
    "(assert eq != invvol through cell executor per E09); (b) prereg freeze -> s3 pool entry (>5min batch "
    "-> runnable_pool per O-20260924-2100); (c) T-144(c) protocol+flow domain sinking due 10-07; "
    "(d) watermark RED transition-window observation (expect green when new-family batches enter pool); "
    "(e) T-143 month-exam prep 10-29; month-boundary first exam 10-31")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts_iso
st["last_ts"] = ts
st["last_round"] = ("2026-10-02 r386 bm-c: T-147 s1 evidence extract + sizing dead-letter law'd + S0 GM-twin "
    "realign + S6 28 rc0 + smoke 47/47 + orders 147/147 + D-19 MATCH")
st["last_seen"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("state written, epoch type check:", isinstance(st["heartbeat_epoch_utc"], int))

# ---- 2. round_reports-bm-c.md append (CRLF) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
line = f"""## r386 | 2026-10-02 {ts[11:]} | bm-c (OS iteration loop)
watermark verdict=RED（py_low_with_work_cands·py 1.8%·O-2115 转换窗如实披露：池 ready=0+N1 停靠；work-cands=T-146 GM 在飞+T-147 本机已领；整改=T-147 s2 prereg→s3 入池 ≤10-09，本轮 s1 交付=整改第一腿落地）
- 当前活：T-147 深轴新家族线 s2 prereg 起草（下轮首动作）
- 最近实物：results/lowamp_p3/s1_evidence_extract.json（11,292B·22:2x）+ sizing 死信定谳件
- 下个里程碑：深轴新家族 prereg 冻结入池 ≤10-08（治理日验收·O-2115 §三）
做了什么：S0 纯重锚手术（本机滞留 3 个 GM 会话 commit=CAS 孪生已在 origin 等价收纳→执行时 rev-parse CAS update-ref+reset --mixed+21 外属主面 origin-verbatim checkout+5 个 D 面恢复·r585/r593/r595 律·树对齐 232ff349e）；S0.5 orders 全扫差集 147/147 零未回执+D-19 水位 MATCH 937A373D+集团 orders.md 物理件区无本司新行（最新 4 行均 Biggame/交互窗业务）；S1 smoke 47/47；S3 主活 T-147 s1 完成=LOWAMP-P3 深轴探索面证据提取件（16 面全表+深轴逐 start 分布 LA-REP 12m 85.1% 正窗/46.5% beat/median +3.2%+双 nulls 支持核对 block bootstrap B2000 p05 0.977 稳/sign-flip p≈0 强正+深轴 same-mask nulls 未烧=s2 必含如实披露+REFINE_BENCH §2 四轴排序变体表）+**P3 sizing 死信定谳**（spec['sizing'] 从未被 _cell_task/_cont_task 消费→judged 4 cells 实跑全 invvol·「LA-EQ」=错标 invvol 孪生 pos 对齐 2760/2760 starts 全字段零差·eq 在 judged cells 从未真烧·sens 腿 L516-534=唯一真 sizing 证据面 invvol p50 1.2135>eq p50 1.1192·headline LA-REP 按申报 invvol 实跑→P3 判负结论不受扰·冻结批 runner 不回改）→坑律入 CODELY+方法论资产卡 E09（捕获律第三次 live 实证）；S6 28 legs rc0（dualrun ZERO-DRIFT streak 51/3·bm-a 心跳 6min 新鲜→scorecard/dscore/build_status 守卫诚实跳过·Golden Week paper 腿 r588/r592/r595 判例跳过）；S7 attrition CLEAN 4 台账+自愈 4/4（loop pin=5 no-op·watchdog 重注册 22:18·pre-commit/pre-push 双爪字节验装）+inbox 自发 W115 PARK 公示收 processed。
验证证据：results/lowamp_p3/s1_evidence_extract.json 11,292B 落盘+恒等断言 pos 对齐 max_abs_diff=0.0；S6 log _r386bmc_s6.log 28/28 rc0；smoke 47/47；watermark.jsonl 22:14:42 verdict=py_low_with_work_cands。
下轮指针：(a) T-147 s2 家族 prereg 起草（PREREG_TEMPLATE 起·新证据 delta 声明 vs 已闭合 lowamp_daily_xs·深轴 same-mask nulls 入批·出场轴 §0.6 双通道逐字·一出生即主考格·新 runner 显式消费 sizing+产线路径 selftest 腿 E09）；(b) prereg 冻结→s3 入池（>5min 写 runnable_pool）；(c) T-144(c) 协议+流水域下沉 due 10-07；(d) 水位 RED 转换窗观察（新家族批入池预期翻绿）；(e) T-143 月考准备 10-29。
本地未达 origin commit 数=0（收口推送后 fetch+ls-tree 自证）

"""
with open(rp, "ab") as fh:
    fh.write(line.replace("\n", "\r\n").encode("utf-8"))
print("round report appended")

# ---- 3. heartbeat fleet/machines/bm-c.json (dynamic fields only, r583 law) ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["current_task"] = ("T-2026-10-02-147 s2 family prereg draft next (s1 evidence extraction DELIVERED r386: "
    "results/lowamp_p3/s1_evidence_extract.json + P3 sizing dead-letter law'd)")
import psutil
hb["cpu_pct"] = psutil.cpu_percent(interval=2)
vm = psutil.virtual_memory()
hb["idle_ram_gb"] = round(vm.available / 1e9, 1)
import subprocess
r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, creationflags=0x08000000)
try:
    hb["gpu_free_vram_mib"] = int(r.stdout.strip().splitlines()[0])
except Exception:
    pass
hb["verdict"] = ("r386 product round: T-147 s1 DELIVERED (deep-axis evidence extract + REFINE_BENCH sec.2 "
    "variant table) + P3 sizing dead-letter diagnosed (judged cells all ran invvol, LA-EQ mislabeled twin, "
    "eq never burned; P3 verdict unaffected; law'd CODELY+E09). Watermark RED = O-2115 transition window "
    "honest (pool ready=0, N1 parked per supply-priority; remedy on track: s2 prereg next round, pool by 10-09)")
assert isinstance(hb["heartbeat_epoch_utc"], int)
acks = hb.get("orders_ack")
print("orders_ack preserved:", len(acks) if acks is not None else None)
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
print("heartbeat written, epoch int OK:", hb["heartbeat_epoch_utc"], hb["clock_read"])

# ---- 4. inbox: own r385 W115 park broadcast -> processed ----
src = os.path.join(REPO, "fleet", "inbox", "MSG-2026-10-02-2200-bmc-ALL-w115-park.md")
dst = os.path.join(REPO, "fleet", "inbox", "processed", "MSG-2026-10-02-2200-bmc-ALL-w115-park.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox MSG moved to processed")
