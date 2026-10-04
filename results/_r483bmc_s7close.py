"""r483 bm-c S7 closeout: orders rescan + CODELY pit-line append + heartbeat
IN-PLACE (roundtrip-gated r678) + state full-write (r645 self-check) +
round report dual-line append (r679 marker-count gates)."""
import datetime
import json
import os
import time

# --- orders S7 double-scan (same-shape set diff, r477 law) ---
orders = set(f for f in os.listdir("fleet/orders")
             if f.startswith("O-") and f.endswith(".md"))
hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
unacked = sorted(orders - ack)
extra = sorted(e for e in (ack - orders) if not e.startswith("README"))
print("ORDERS_RESCAN", len(orders), "unacked", unacked, "extra", extra)
assert not unacked and not extra, "ORDERS RESCAN FAIL"

# --- CODELY pit-line append (four-question gate passed) ---
cp = "CODELY.md"
craw = open(cp, "rb").read()
pit_line = ("- [2026-10-04 16:2x r483 bm-c] 池面 r668 补翻四连律（W3 SHARD-3 收口实弹·零 origin 伤害）："
            "①r668 补翻他机分片前必先 fetch+ls-tree origin 实核正主翻面是否已在途已推（本窗 bm-a r685 "
            "16:04:54 正主 burner-side 翻面已推·本机 16:12:57 补翻=同语义冗余·push-prep 才发现→r474 "
            "SAME-change 弃本地取 origin verbatim+删冗余 claim）；②treasure_guard prescan rc3 硬拒后禁同批 "
            "`;` 链续跑手术步（r657 ②律重犯实录——本窗 rc3 命中与去重手术同命令批执行·幸 r482 律在先+零丢失"
            "断言过=r441 仪式补全收口；正法=rc3 即停→裁定→另批执行）；③多行元素替换×del 混合行级手术=删除步"
            "必须后置（del 先行=索引移位吃掉闭合行→JSON 永不闭合·in-memory 解析门当场拦零盘伤）；④CRLF json "
            "roundtrip 探针必须含内部换行转换（只测行尾=假不恒定→误判需行级手术·fail-closed 方向无害但探针错）。"
            "How to apply：补翻前 fetch 实核+rc3 停批+手术 del 后置+roundtrip 内转换四件套。").encode("utf-8")
c_eol = b"\r\n" if b"\r\n" in craw[-200:] else b"\n"
assert craw.count(pit_line) == 0, "pit line already present"
open(cp, "ab").write(pit_line + c_eol)
chk = open(cp, "rb").read()
assert chk.count(pit_line) == 1
assert chk.startswith(craw), "codely prefix identity FAIL"
print("CODELY-APPEND ok")

# --- heartbeat roundtrip gate (r678) ---
p = "fleet/machines/bm-c.json"
raw = open(p, "rb").read()
d0 = json.loads(raw.decode("utf-8"))
rt = json.dumps(d0, ensure_ascii=False, indent=1).encode("utf-8")
roundtrip_ok = (rt == raw)
print("ROUNDTRIP_IDENTICAL", roundtrip_ok)

epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

hb2 = json.loads(raw.decode("utf-8"))
hb2["last_seen"] = clock
hb2["round_no"] = 483
hb2["current_task"] = (
    "当前活: W3 wave-3 screen finalize complete=true 全链收口（4814 候选/785 幸存 16.31%·null p95 0.5333·"
    "账本 646,799·池面 4/4 done〔bm-a r685 正主翻面在位·本机同窗补翻冗余已弃置 r474〕·§7/§8 回填+attrition "
    "行 98+r441 仪式四件齐） | 最近实物: results/mass_trial/w3_screen_summary.json（finalize 产品）+"
    "results/mass_trial/w3_screen_checkpoint.jsonl（4909 唯一行=r482 律去重后·1227 双烧行零信息损失剔除）+"
    "results/_r483bmc_w3_recon.json（六对账证据）+results/_r483bmc_ckpt_dedup.json（去重 receipt）+"
    "results/_r483bmc_s6_log.txt（38/38 rc0）@ " + clock + " | 下个里程碑: W3 §9 s3 判决面段冻结起草 ≤10-12"
    "（N_eff=646,799 链头·判线 science_gates 单源·种子 R250 一步律）；fund-trio finalize 10-05 10:30（bm-b）；"
    "O-2115/O-2030 验收 10-08；开市 10-09")
hb2["heartbeat_epoch_utc"] = epoch
hb2["clock_read"] = clock
hb2["verdict"] = (
    "r483 W3 screen-finalize round: r482-law keep-first id-dedup gate "
    "(6136->4909, 1227 double-burn rows elapsed_s-only diff, zero-loss "
    "asserted; treasure_guard prescan rc3 hit on results/mass_trial/ family "
    "-> r441 ritual four-piece: rc3 record + registry line + assertion "
    "battery + receipt; same-batch proceed-after-rc3 execution-order fault "
    "recorded honestly) -> finalize complete=true (785/4814 = 16.31% third-"
    "wave stable, controls 5/75 same list as w2, null p95 0.5333, ledger "
    "646,799 append single-chain) -> six-recon 4/6 in-band + 2 disclosed "
    "(R-axis 4.22x, cross-wave collapse 1274>600 mechanism review) -> "
    "prereg sec.7/8 backfilled + attrition row 98 -> pool SHARD-3 final = "
    "bm-a r685 rightful flip (my same-window r668 supplement flip 16:12:57 "
    "made redundant by their 16:04:54 push, local discarded per r474 "
    "SAME-change); S6 38/38 rc0; smoke 48/48; orders 155/155 dual-scan; "
    "attrition CLEAN; loop pin5 + watchdog + dual claws verified")
try:
    import psutil
    hb2["cpu_cores"] = psutil.cpu_count(logical=True)
    hb2["idle_ram_gb"] = round(psutil.virtual_memory().available / (1 << 30), 1)
except Exception as ex:
    print("psutil face skip:", ex)

hb_eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
if roundtrip_ok:
    out = json.dumps(hb2, ensure_ascii=False, indent=1).encode("utf-8")
    open(p, "wb").write(out)
else:
    lines = raw.decode("utf-8").splitlines(True)
    swaps = {
        "last_seen": json.dumps(clock, ensure_ascii=False),
        "round_no": "483",
        "current_task": json.dumps(hb2["current_task"], ensure_ascii=False),
        "heartbeat_epoch_utc": str(epoch),
        "clock_read": json.dumps(clock, ensure_ascii=False),
        "verdict": json.dumps(hb2["verdict"], ensure_ascii=False),
    }
    for key, jval in swaps.items():
        pref = ' "%s": ' % key
        hits = [k for k, ln in enumerate(lines) if ln.startswith(pref)]
        assert hits, "key line missing: %s" % key
        for k in hits:
            lines[k] = '%s%s,%s' % (pref, jval, hb_eol.decode())
    open(p, "wb").write("".join(lines).encode("utf-8"))
    print("HEARTBEAT line-surgery: %d keys swapped" % len(swaps))

v = json.load(open(p, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock not T-sep"
assert len(v.get("orders_ack", [])) == len(ack), "ack count drift"
print("HEARTBEAT-OK epoch", v["heartbeat_epoch_utc"], "clock", v["clock_read"])

# --- state full-write (own file, single-writer; r645 self-check) ---
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 483
st["last_round"] = ("r483 bm-c: W3 screen finalize complete=true (785/4814 = "
                    "16.31%, null p95 0.5333, ledger 646,799, controls 5/75 "
                    "same-list-as-w2); r482-law dedup gate 6136->4909 zero-loss "
                    "(treasure rc3 hit -> r441 ritual); six-recon 4/6 in-band "
                    "+ 2 disclosed (R-axis 4.22x, cross-wave 1274>600); prereg "
                    "sec.7/8 + attrition row 98; pool SHARD-3 = bm-a r685 "
                    "rightful flip (local supplement superseded per r474); "
                    "S6 38/38 rc0; orders 155/155; attrition CLEAN")
st["last_round_at"] = clock
st["last_round_ts"] = clock.replace("T", " ")[:19]
st["last_seen"] = clock
st["updated"] = clock
st["updated_at"] = clock
st["next"] = ("(a) r484: W3 sec.9 s3 judge-face freeze draft (criteria from "
              "science_gates g1_prime_v2/g2_registration_v2 shared lib, seeds "
              "R250 one-step law, N_eff ledger-head 646,799 never reset, "
              "T-22 caliber x {6m,12m,24m} x x2 cost x regime segs x dual "
              "nulls>=2000, |corr|>=0.999 collapse gate; freeze commit then "
              "pool burn <=10-12). (b) fund-trio finalize 10-05 10:30 (bm-b "
              "owner, watch only). (c) O-2115/O-2030 acceptance 10-08. "
              "(d) market reopen 10-09. (e) judge --wave 3 CLI extension "
              "lands with the sec.9 freeze (choices=[1,2] today).")
st["did"] = ("r483 bm-c W3 screen-finalize round: (1) S0 FF clean merge "
             "(dirty-intersect empty); product commit 790d4c1ea (18 faces); "
             "push-prep found origin +4 (bm-a r685 SHARD-3 rightful flip "
             "16:04:54 + bm-b keepalive + bm-a autofill faces) -> r474 "
             "disposition: pool face checkout origin verbatim, my 16:12:57 "
             "same-window r668 supplement flip discarded (redundant), "
             "redundant claim file deleted; merge zero UU; push_verify "
             "DELIVERED tip aa5a35d6b. (2) S0.5 orders 155/155 zero unacked "
             "dual-scan; D-19 decisions 4E5BE321 + group orders 68947C17 "
             "double MATCH -> zero consumption; inbox empty. (3) S1 smoke "
             "48/48. (4) S2 boards empty. (5) S3 satengine rc0 alive; "
             "watermark green. MAIN PRODUCT: r482-law keep-first id-dedup "
             "gate on w3 checkpoint (6136->4909 rows, 1227 double-burn dup "
             "rows bm-b shard-1 absorb face, elapsed_s-only diff asserted "
             "= zero information loss; treasure_guard prescan rc3 hit "
             "results/mass_trial/ family L27 -> r441 ritual adjudication "
             "zero-loss class, four-piece complete: rc3 record + registry "
             "pre-registration line + assertion battery + receipt "
             "_r483bmc_ckpt_dedup.json; 6136-row pre-dedup face preserved "
             "in git history 1990102fa) -> mass_trial_w1.py finalize --wave "
             "3 complete=true (785 survivors / 4814 candidates, screen line "
             "0.60/30/-0.35, null p50 0.45 p95 0.5333, controls 5/75 "
             "byte-same list as w2 + 2 month-arg errors, ledger 646,799 "
             "append single-chain idempotent) -> six-recon evidence "
             "(_r483bmc_w3_recon.json): survival 16.31% in-band 10-18% "
             "(third-wave stable), null in-band, R-bear 4.22x marginally "
             "above 2-4x band disclosed (~4x stable 3rd wave), family "
             "direction HIT 3rd consecutive, controls in-band, cross-wave "
             "collapse 1274 vs band 150-600 OUT 2.1x -> mechanism review "
             "disclosed (rate 21.9% vs w2 28.6% on base 5811 = base-growth-"
             "consistent sublinear) -> prereg sec.7/8 backfilled (4/6 "
             "in-band, 2 out disclosed) -> gate_attrition entries 98 "
             "(MASS_TRIAL_W3 row, roundtrip-identity-gated append, guard "
             "scan CLEAN). (6) S6 38/38 rc0 (dualrun streak 51; 4 "
             "stale-takeover derives by bm-c per O-2100 s2.4; golden-week "
             "no-op legs honest). (7) S7: loop pin5 no-op verified + "
             "watchdog present + dual claws reinstalled + attrition CLEAN "
             "+ orders rescan 155/155. (8) S4 one pit line: r668 "
             "supplement-flip four-part law (pre-flip fetch check / rc3 "
             "stop-batch / del-after-index surgery order / roundtrip "
             "interior-CRLF probe).")
st["verify"] = ("finalize evidence = results/mass_trial/w3_screen_summary.json "
                "(complete=true, trials_ledger 646799, evidence_cutoff "
                "meta) + _r483bmc_w3_recon.json (six-recon) + "
                "_r483bmc_ckpt_dedup.json (dedup receipt, zero-loss "
                "assertions) + prereg sec.7/8 backfill source pointers; "
                "pool state = origin verbatim face (bm-a r685 rightful flip "
                "16:04:54/16:05:03 in place, 4/4 W3 entries done); attrition "
                "row = gate_attrition.json entries 98 + attrition_ledger_"
                "guard scan CLEAN; push_verify DELIVERED (790d4c1ea + merge "
                "aa5a35d6b, ahead=0/behind=0); smoke 48/48; S6 38/38 "
                "(_r483bmc_s6_log.txt); heartbeat epoch int + clock T-sep "
                "POST-WRITE; state json.loads self-check")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = clock
st["current_task"] = hb2["current_task"]
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk2 = json.load(open(sp, encoding="utf-8"))
assert chk2["round_no"] == 483 and isinstance(chk2["heartbeat_epoch_utc"], int)
print("STATE-OK round_no", chk2["round_no"])

# --- round report dual-line append (EOL-detected, marker-count gates) ---
rp = "round_reports-bm-c.md"
rp_raw = open(rp, "rb").read()
rp_eol = b"\r\n" if b"\r\n" in rp_raw[-200:] else b"\n"
now_hm = clock.replace("T", " ")[:19]
main_line = (
    now_hm + "｜r483｜dept:策略/研究（W3 screen finalize 收口轮·T-158 在册）｜"
    "watermark verdict=绿（red=false·py_low_board_clear 板闭环合法 idle·W3 池 4/4 done 无待烧面）｜"
    "当前活=W3 wave-3 screen finalize complete=true 全链收口｜最近实物=results/mass_trial/w3_screen_summary.json"
    "（4814 候选/785 幸存 16.31%·null p95 0.5333·账本 646,799）@ " + clock + "｜下个里程碑=W3 §9 s3 判决面段冻结起草 "
    "≤10-12（N_eff=646,799 链头实读·判线 science_gates 单源·种子 R250 一步律）+fund-trio finalize 10-05 10:30（bm-b）"
    "+O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜"
    "S0: FF 净路（脏∩入向=∅）→产品 commit 790d4c1ea（18 面）→push-prep 发现 origin 进 4 commit（bm-a r685 SHARD-3 "
    "正主翻面 16:04:54+bm-b keepalive+bm-a autofill 面）→r474 处置：池面 checkout origin verbatim+本机同窗 r668 补翻"
    "（16:12:57）冗余弃置+冗余 claim 文件删除→merge 零 UU→push_verify DELIVERED tip aa5a35d6b｜S0.5: 令差集 0"
    "（155/155·轮首+S7 双扫）·D-19 decisions 4E5BE321+orders 68947C17 双 MATCH（per-key raw-blob）零消费·inbox 空｜"
    "S1 smoke 48/48｜S2 板空（job_list 0·fleet 0 open）｜S3: satengine rc0 活（Tools 注册面）·水位绿｜主产出：r482 律"
    "去重门（checkpoint 6136→4909·1227 双烧行 elapsed_s-only 零信息损失断言过·prescan rc3 命中 results/mass_trial/ "
    "全族〔L27〕→r441 仪式四件裁定零丢失类：rc3 留痕+预登记行+断言电池+receipt _r483bmc_ckpt_dedup.json·6136 行原面 git "
    "史保全 1990102fa·执行序过误〔rc3 后未停批〕如实入坑律）→finalize complete=true（785/4814·16.31% 三波稳态·对照 5/75 "
    "与 w2 逐字同清单·账本 append 单链幂等）→六对账 4/6 带内+2 出带披露（R 轴 4.22× 超带 0.22×〔三波 ~4× 稳态〕·跨波坍缩 "
    "1274>600 机制复核〔21.9% vs w2 28.6%=基 5811 增长一致次线性〕）→§7/§8 回填（source=_r483bmc_w3_recon.json）→attrition "
    "行 98（roundtrip 恒等门+guard 扫 CLEAN）→池面终态=bm-a r685 正主翻面（本机补翻冗余弃置如实）｜S6 38/38 rc0 NON-ZERO=none"
    "（dualrun streak 51·4 腿 stale-takeover derive〔O-2100 s2.4〕·金周 no-op 腿诚实）｜S7: loop pin5 no-op（16:25 下发在位）"
    "+watchdog 在位+双爪 LF 归一重装·attrition CLEAN·orders 二扫 155/155 零差｜S4: 一条坑律行（补翻前 fetch 实核+rc3 停批+手术 "
    "del 后置+roundtrip 内转换四件套）｜记分: 2（finalize 全链=可跑可看实物：summary+recon+attrition+§7/§8）｜记账预算: 5/5"
    "（registry 仪式行+state+心跳+轮报+CODELY）｜本地未达 origin commit 数: 收口 push 后 push_verify 自证｜在册面行删除类"
    "断言: 本轮 1 件（checkpoint 去重·r441 仪式四件齐+零丢失断言+git 史保全·非清扫类如实披露）｜下轮指针=r484 ①W3 §9 s3 "
    "判决面冻结起草（判线=science_gates 共享库禁手抄·种子 R250 一步律·N_eff=646,799 链头·出场轴门 §3 声明已带·冻结 commit "
    "后池烧 ≤10-12）②fund-trio finalize 10-05 10:30（bm-b 正主·观察面）③O-2115/O-2030 验收 10-08")
close_line = (
    clock + "｜r483 bm-c S7-close｜本地未达 origin commit 数=0（push_verify DELIVERED tip aa5a35d6b·ahead=0/behind=0）｜"
    "收口实录：主产品 commit 790d4c1ea（18 面：w3_screen_summary.json finalize 产品+去重 checkpoint -1227 行+attrition "
    "行 98+§7/§8 回填+registry 仪式行+探针族 8 件）+merge aa5a35d6b（origin 4 commit 零 UU·bm-a r685 正主翻面随 merge "
    "落树）→close commit（簿记三写+CODELY 行+轮报双行）→push_verify 终证｜W3 池面收口态=4/4 done（bm-a 正主翻面在位·"
    "本机同窗补翻冗余已弃置 r474 SAME-change 如实）｜在册面行删除类=1（checkpoint 去重·仪式四件齐）｜轮产品计分：2"
    "（finalize 全链可跑可看实物·非等待态）")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write((main_line + "\n").replace("\n", rp_eol.decode()))
    f.write((close_line + "\n").replace("\n", rp_eol.decode()))
lines_now = open(rp, encoding="utf-8").read()
assert lines_now.count("r483 bm-c S7-close") == 1, "close line count"
assert lines_now.count("｜r483｜") == 1, "main line count"
print("REPORT-OK r483 dual-line appended, file lines",
      len(lines_now.splitlines()))
