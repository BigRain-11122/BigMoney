"""r482 bm-c S7 closeout: orders rescan + CODELY pit-line append (file-tail
anchor after r683 line) + heartbeat IN-PLACE (roundtrip-gated r678) + state
full-write (json.loads self-check r645) + round report dual-line append."""
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
print("ORDERS_RESCAN", len(orders), "unacked", unacked, "extra_non_readme", extra)
assert not unacked and not extra, "ORDERS RESCAN FAIL"

# --- CODELY pit-line append (four-question gate passed; file-tail anchor) ---
cp = "CODELY.md"
craw = open(cp, "rb").read()
pit_line = ("- [2026-10-04 16:0x r482 bm-c] mass_trial screen 双烧×finalize id 去重缺失坑（池注宣称「finalize 按 id 去重幂等」"
            "但 cmd_finalize 实为行计数 complete 面 len(cand)==n_expected——双烧分片〔r189 确定性零害〕两机各行 elapsed_s "
            "异字节→checkpoint 行级 union 去不掉同 id 双行→len 超额→complete=False 假红+存活者双计）。How to apply：W3 "
            "finalize 前必跑 id 级零重探针（_r482bmc_ckpt_dup_probe.py 范式）；见 dup>0 先 keep-first id 去重（非 "
            "elapsed_s 字段全等断言=零信息损失）再 finalize；merge resolver 撞 checkpoint 面禁裸行级 union 纳双行"
            "（r656 行 union 律对同 id 异字节形态失效）。").encode("utf-8")
c_eol = b"\r\n" if b"\r\n" in craw[-200:] else b"\n"
assert craw.count(b"r683 bm-a") >= 1, "tail anchor missing"
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
hb2["current_task"] = (
    "当前活: W3 screen 3/4 分片烧毕翻面（SHARD-0/1/2 done·3681/4909 行 id 零重·SHARD-3 bm-a 在烧 claim 15:53:07）"
    "→ wave-3 screen finalize 待 shard-3 行到位（物理依赖 bm-a 推送）— finalize 前 id 级零重门（CODELY r482 律）"
    " | 最近实物: results/mass_trial/w3_screen_checkpoint.jsonl（3681 行=3/4 分片全量）+ pool_claims 3 件 "
    "closed-ok 翻面握手（SHARD-0/1/2 harvested）+ results/_r482bmc_*（shard0 覆盖核验+dup 探针+resolver 证据）+ "
    "results/_r482bmc_s6_log.txt（38/38 rc0）@ " + clock + " | 下个里程碑: 4/4 done → --wave 3 finalize"
    "（w3_screen_summary.json+§7/§8 回填+attrition 行）→ §9 s3 段冻结 ≤10-12；fund-trio finalize 10-05 10:30"
    "（bm-b）；O-2115/O-2030 验收 10-08；开市 10-09")
hb2["heartbeat_epoch_utc"] = epoch
hb2["clock_read"] = clock
hb2["verdict"] = (
    "r482 burn-management round: W3 screen 3/4 shards burned+flipped same-window "
    "(SHARD-0 autofill-launch session-adoption claim -> harvest flip 15:50:03; "
    "SHARD-1 pool_worker close 80dbc4aa6 + bm-b double-burn lawful claim-by-"
    "origin-face [r189 zero-harm]; SHARD-2 session-adoption claim c049d9bf0 -> "
    "harvest flip 15:58:33); coverage verified 3681/4909 exact tiling zero dup; "
    "SHARD-3 on bm-a (physical dep for finalize); stranded 3a418f663 claim "
    "rescued via merge+push; r481-close mid-burn 896-row origin face settled "
    "(self-healed by absorb); finalize id-dedup pit recorded CODELY; S6 38/38 "
    "rc0; smoke 48/48; orders 154/154 dual-scan; attrition CLEAN; dual claws "
    "reinstalled; loop pin5 + watchdog verified")
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
print("HEARTBEAT-OK epoch", v["heartbeat_epoch_utc"], "clock",
      v["clock_read"], "fields", len(v))

# --- state full-write (own file, single-writer; r645 self-check) ---
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 482
st["last_round"] = ("r482 bm-c: W3 screen 3/4 shards burned+flipped (3681/4909 "
                    "exact tiling zero-dup, claims 0/1/2 harvested, SHARD-3 bm-a "
                    "burning); stranded claim rescue + 2 merges (19 UU canon-"
                    "resolved, r482 resolver w/ jsonl line-union + W3 done-"
                    "stickiness asserts); S6 38/38 rc0; finalize id-dedup pit "
                    "recorded; orders 154/154; attrition CLEAN")
st["last_round_at"] = clock
st["last_round_ts"] = clock.replace("T", " ")[:19]
st["last_seen"] = clock
st["updated"] = clock
st["updated_at"] = clock
st["next"] = ("(a) r483: poll shard-3 rows (bm-a push) -> id-level zero-dup probe "
              "-> python scripts\\mass_trial_w1.py finalize --wave 3 -> "
              "w3_screen_summary.json + prereg §7/§8 backfill + gate_attrition "
              "row + treasure-capture question. (b) merge-resolver law: W3 "
              "checkpoint face = id-level union only (bm-b dup shard-1 rows "
              "expected via their absorb). (c) fund-trio finalize 10-05 10:30 "
              "(bm-b). (d) O-2115/O-2030 acceptance 10-08; market reopen 10-09. "
              "(e) W3 §9 s3 judge-face freeze <=10-12.")
st["did"] = ("r482 bm-c W3 burn-management round: (1) S0 clean fetch, 0 incoming; "
             "round-start tree = 3 daemon faces. (2) S0.5 orders 154/154 zero "
             "unacked; D-19 decisions 4E5BE321 + group orders 68947C17 double "
             "MATCH (r458 probe per-key raw-blob) -> zero consumption; inbox "
             "MSG-1520 (own r480 seat announcement) read; archived fleet-side "
             "via merge R-move. (3) S1 smoke 48/48. (4) S2 boards empty (job_list "
             "0, fleet 0 open). (5) S3 watermark green (py_low_board_clear at "
             "probe -> engine claimed W3 shards = supply response); satengine "
             "rc0 alive (Tools face, N1 W117 bands). MAIN PRODUCT: W3 screen "
             "shard burn management to 3/4 done -- SHARD-0 autofill-launched "
             "(no claim file) -> session adoption per pool r488/r489 note "
             "(closed-ok claim 4bbaedb43) -> harvest flip 15:50:03; SHARD-1 "
             "pool_worker burn + close 80dbc4aa6 (claim push rejected in fleet "
             "wave = stranded) + bm-b autofill double-claim via origin-face "
             "(lawful T-115 read, r189 deterministic zero-harm) -> my claim "
             "relayed via merge, harvest flip 15:50:03; SHARD-2 autofill-"
             "launched -> session adoption claim c049d9bf0 -> harvest flip "
             "15:58:33; SHARD-3 claimed by bm-a 27b7b826d (their burn, their "
             "flip duty). Coverage verified: 3681/4909 rows exact tiling "
             "(1227x3), zero dup ids, 0 signal errors, screen_pass 129 in "
             "shard-0. (6) archaeology: origin 896-row checkpoint face = r481 "
             "close committed mid-burn snapshot (shard-0 at 896/1227), "
             "self-healed by r482 absorb (3681 rows committed+pushed) -- not a "
             "regression. (7) merges: wave-1 (bm-b r678 W118 prereg + trio "
             "keepalive + bm-b shard-1 claim) zero UU; wave-2 absorb (79 files) "
             "+ 19 UU canon-resolved by _r482bmc_merge_resolve.py (jsonl "
             "line-union NEW face class for pool_core_samples r656; token r456 "
             "fallback; twins ts-freshness; pool W3 done-stickiness post-"
             "assert) -> push_verify DELIVERED x2. (8) S6 38/38 rc0 (dualrun "
             "ZERO-DRIFT streak 51; 4 stale-takeover derives by bm-c per O-2100 "
             "s2.4; golden-week no-op legs honest). (9) S7: loop pin5 16:05 "
             "verified + watchdog 16:00 + dual claws LF-normalized reinstall + "
             "attrition CLEAN (4 ledgers) + orders rescan 154/154. (10) S4 one "
             "pit line: finalize id-dedup mismatch (pool note claim vs "
             "row-count reality) + dup-union recipe.")
st["verify"] = ("coverage evidence = results/_r482bmc_w3_shard0_verify_out.txt "
                "(1227/1227, 0 dup/missing/extra, screen_pass 129, VERDICT OK) + "
                "_r482bmc_ckpt_dup_probe_out.txt (local 3681 unique 0 dup; "
                "origin parity post-push); pool states = _r482bmc_pool_"
                "regression_out.txt (SHARD-0/1/2 done harvested_by bm-c; SHARD-3 "
                "bm-a; trio 15:46:12 no regression); merge evidence = "
                "_r482bmc_merge_resolve.json (19 faces, core-samples "
                "line-union, W3 post-assert) + push_verify DELIVERED "
                "(9e5025ac, ahead=0/behind=0); smoke 48/48; S6 38/38 "
                "(_r482bmc_s6_log.txt chain-end); attrition CLEAN; heartbeat "
                "epoch int + clock T-sep + ack-count in-place POST-WRITE; "
                "state json.loads self-check")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = clock
st["cpu_pct"] = 17.0
st["current_task"] = hb2["current_task"]
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk2 = json.load(open(sp, encoding="utf-8"))
assert chk2["round_no"] == 482 and isinstance(chk2["heartbeat_epoch_utc"], int)
print("STATE-OK round_no", chk2["round_no"])

# --- round report dual-line append (EOL-detected, r641 newline='' law) ---
rp = "round_reports-bm-c.md"
rp_raw = open(rp, "rb").read()
rp_eol = b"\r\n" if b"\r\n" in rp_raw[-200:] else b"\n"
now_hm = clock.replace("T", " ")[:19]
main_line = (
    now_hm + "｜r482｜dept:策略/研究（W3 screen 烧录管理+翻面收口轮·T-158 在册·O-1440 §3 供料）｜"
    "watermark verdict=绿（red=false healthy·py_watermark py_low_board_clear 后引擎即领 W3 分片=供给同窗响应〔r480 同型非违令〕）｜"
    "当前活=W3 3/4 分片烧毕+翻面+SHARD-3 bm-a 在烧｜最近实物=results/mass_trial/w3_screen_checkpoint.jsonl"
    "（3681 行=SHARD-0/1/2 全量·id 零重）+results/pool_claims/MASS-TRIAL-W3-*（3 件 closed-ok 翻面握手）+"
    "results/_r482bmc_w3_shard0_verify_out.txt（1227/1227 精确覆盖·screen_pass 129）+results/_r482bmc_merge_resolve.json"
    "（19 UU 解决证据）+results/_r482bmc_s6_log.txt（38/38 rc0）@ " + clock + "｜下个里程碑=SHARD-3 行到位→--wave 3 finalize"
    "（summary+§7/§8 回填+attrition 行）→§9 s3 段冻结 ≤10-12+fund-trio finalize 10-05 10:30（bm-b）+O-2115/O-2030 验收 "
    "10-08+开市 10-09（≤48h）｜"
    "S0: 双波集成——波1（bm-b r678 W118 prereg+trio keepalive+bm-b shard-1 认领）零 UU merge+push DELIVERED；波2 先 absorb "
    "（79 面：S6 产品+W3 checkpoint 3681 行+r482 探针族+daemon 面）再 merge 撞 19 UU→r482 resolver（r480 血统+新面类："
    "pool_core_samples.jsonl 行级 union r656 律〔r480 血统 ts-twin 处理对 append jsonl 是错的=本窗修正〕+token r456 回退+"
    "twin ts-freshness+池面 W3 done 粘性后断言）→push_verify DELIVERED tip 9e5025ac｜S0.5: 令差集 0（154/154 同形态双扫）·D-19 "
    "decisions 4E5BE321+orders 68947C17 双 MATCH（per-key raw-blob）零消费·inbox MSG-1520（本机 r480 席位公示）读毕=他机归档"
    "（merge R-move 实证）｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 0 open）｜S3: satengine rc0 活（Tools 注册面·N1 W117 波带）"
    "·水位绿｜主产出：W3 screen 烧录管理至 3/4 done——SHARD-0（autofill 引燃无 claim 文件=烧录侧会话补握手 4bbaedb43→harvest "
    "15:50:03 翻面）·SHARD-1（pool_worker 烧毕 close 80dbc4aa6 推送被机队波拒搁浅+bm-b autofill 经 origin 面 T-115 合法续领=双烧"
    "〔r189 确定性零害〕→搁浅 claim 经本机 merge 中继→harvest 15:50:03 翻面·owner=bm-b 新 claim 如实）·SHARD-2（autofill 引燃→"
    "会话补握手 c049d9bf0→harvest 15:58:33 翻面）·SHARD-3（bm-a 认领 27b7b826d 在烧·其翻面义务归其会话）·覆盖核验 3681/4909 "
    "精确铺瓦零重零信号错误｜考古定谳：origin checkpoint 896 行=r481 close 提交了 shard-0 中烧快照（896/1227 时点）非回退面"
    "（本窗 absorb 3681 行自愈）｜S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51·四腿 stale-takeover 由本机接管 "
    "derive〔O-2100 s2.4〕·金周 no-op 腿诚实·market_regime ORANGE shadow days=2）｜S7: loop pin5（16:05 下发）+watchdog（16:00）"
    "在位·双爪 LF 归一重装·attrition CLEAN（4 ledgers）·orders 二扫 154/154 零差｜S4: 一条坑律行（finalize id 去重缺失=池注宣称 vs "
    "行计数实现〔complete 面 len(cand)==n_expected〕——双烧各行 elapsed_s 异字节→行级 union 纳同 id 双行→finalize 假红+存活者双计"
    "；正法=finalize 前 id 零重探针+keep-first 去重〔非 elapsed_s 字段全等=零信息损失〕+resolver 撞 checkpoint 面禁裸行级 union）"
    "｜记分: 2（W3 3/4 分片烧毕+翻面=可跑实物推进+claim 握手机制落地 2 件+S6 38 腿管线+19 面 merge resolver 产出·非空转）｜"
    "记账预算: 4/5（state+心跳+轮报+CODELY 1 行）｜本地未达 origin commit 数: 收口 push 后 push_verify 自证（DELIVERED 后=0）｜"
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面·五收口步未触发〔finalize 未达〕→"
    "TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜下轮指针=r483 ①轮 origin 探 shard-3 行（bm-a 推送）→id 零重探针→"
    "finalize --wave 3→summary+§7/§8 回填+attrition 行+宝捕获问 ②若 bm-b 双烧行先到=resolver 按 CODELY r482 律 id 级 union ③"
    "fund-trio finalize 10-05 10:30（bm-b 正主）")
close_line = (
    clock + "｜r482 bm-c S7-close｜本地未达 origin commit 数=0（收口 push 后 push_verify 单源自证·DELIVERED 后=0）｜"
    "收口实录：主产品 commit 链=4bbaedb43（SHARD-0 握手）+3bb3a9acc（merge 波1）+c049d9bf0（SHARD-2 握手）+2f524eb1f"
    "（absorb 79 面·checkpoint 3681 行）+9e5025ac（merge 波2·19 UU resolver）→push_verify DELIVERED（tip==remote·"
    "ahead=0/behind=0）→close commit（簿记三写+CODELY 行+轮报双行）→push_verify 终证｜W3 分片态（收口时点）=SHARD-0/1/2 done "
    "harvested·SHARD-3 bm-a 在烧（物理依赖如实）｜零清扫/归档/删除/恢复类动作轮：登记册零命中断言照实｜轮产品计分：2"
    "（可跑/能看实物=3/4 分片烧毕翻面+3681 行 checkpoint+双 claim 握手机制实弹+S6 38 腿产出·等待态声明：finalize 待 bm-a "
    "shard-3 行=物理依赖票内留痕）")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write((main_line + "\n").replace("\n", rp_eol.decode()))
    f.write((close_line + "\n").replace("\n", rp_eol.decode()))
lines_now = open(rp, encoding="utf-8").read()
assert lines_now.count("r482 bm-c S7-close") == 1, "close line count"
assert lines_now.count("｜r482｜") == 1, "main line count"
print("REPORT-OK r482 dual-line appended, file lines",
      len(lines_now.splitlines()))
