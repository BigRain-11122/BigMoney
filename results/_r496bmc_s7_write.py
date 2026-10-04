"""r496 bm-c S7 bookkeeping writer: heartbeat line-level field surgery
(r678 no-roundtrip law), round-report main-row append (r679 idempotence gate),
state reparse self-proof (F7 epoch int + clock T-form). Zero console CJK."""
import json
import os
import re

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
HB = "fleet/machines/bm-c.json"
RR = "round_reports-bm-c.md"
ST = "state-bm-c.json"
TS = "2026-10-04T20:55:20+08:00"
TS_SP = "2026-10-04 20:55:20"
EPOCH = 1791118520

CTASK = ("当前活: N2-W15 generate 产品首落收口完成（bm-c daemon 盲窗认领第三次复发→烧录落地→双层翻面"
         "+claim 回填+MSG-2100 通报）；W3 judge 看护持续（pid 33768·ETA ~22:1x）"
         "| 最近实物: results/n2_w15/n2_w15_candidates.json（954 候选·sha256 440db865…·20:45:29 "
         "首落 canonical per r486）+池面双层翻面（entry+own shard=done）@ 2026-10-04T20:55:20+08:00 "
         "| 下个里程碑: N2 screen-prep+12 SCREEN 分片入池（下轮起·≤10-05 晚）；"
         "w3_judge.json 判决落地→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）")

HB_SET = {
    "activity_now": ("r496 N2-W15 generate first-land canonical closeout (bare-shard blind-window "
                     "3rd recurrence on bm-c face -> burn landed n=954 -> two-layer flip + claim file "
                     "+ MSG-2100) + W3 judge custody (pid 33768, ETA ~22:1x) + S6 38/38 rc0"),
    "clock_read": TS,
    "cpu_idle_pct": 95.2,
    "cpu_pct": 4.8,
    "cpu_util_pct": 4.8,
    "current_task": CTASK,
    "free_ram_gb": 9.2,
    "idle_ram_gb": 9.2,
    "ram_free_gb": 9.2,
    "heartbeat_epoch_utc": EPOCH,
    "last_seen": TS,
    "last_seen_at": TS,
    "current_task_at": TS,
    "latest_artifact": ("results/n2_w15/n2_w15_candidates.json (n=954, sha256 440db8656e3b0b2e..., "
                        "first-land canonical per r486, 20:45:29) + pool two-layer flip 20:54:57 "
                        "+ S6 38-face regen (REPORT/LIVE-2026-10-04, dualrun streak 51)"),
    "next_milestone": ("N2 screen-prep + 12 SCREEN shard enrollment (<=10-05 evening, bm-c seat MSG-1955); "
                       "w3_judge.json lands ~22:1x -> ADOPT_PASS -> 48h CEO report clock (<=10-06 evening); "
                       "bm-b sibling waiter closeout (their face); fund-trio 10-05 (bm-b); "
                       "acceptance 10-08; market reopen 10-09"),
    "prod_lanes": ("W3-JUDGE lane: judge-finalize --wave 3 in flight on bm-c (pid 33768, spawn 17:44:04, "
                   "ETA ~22:1x, sole finalize per MSG-1810/1745 seat chain); N2-W15 lane: generate LANDED "
                   "first-land canonical on bm-c (n=954 candidates, entry+own-shard flipped done 20:54:57, "
                   "sibling n2-w15-generate-0of1 owner=bm-b untouched -> waiter refuse/early-kill at bm-b "
                   "closeout); screen-prep + 12 SCREEN enrollment = bm-c next round (seat MSG-1955); "
                   "fund-trio NULLS burning on bm-b keepalive; boards empty; 0 new orders"),
    "round_no": 496,
    "round_no_label": "r496",
    "ts": TS_SP,
    "updated": TS,
    "updated_at": TS,
    "verdict": ("r496 bm-c: N2-W15 generate first-land canonical closeout round -- S0 r437 pre-alignment "
                "(absorb 6100bbf44 + zero-UU merge 044f7b213 + DELIVERED first-try) + S0.5 dual MATCH + "
                "MSG-2025 consumed + S1 48/48 + satengine alive + W3 IN_FLIGHT (pid 33768, cpu 10931s, "
                "pool 4/4, ckpt 777/0dup) + N2 bare-shard blind-window 3rd recurrence (bm-c daemon claim "
                "20:35:13) -> burn complete (n2_w15_candidates.json n=954, 20:45:29) -> vendor-caliber "
                "validation -> burner-side two-layer flip (entry+own shard done, origin-freshest base, "
                "sibling bm-b untouched r626d-2) + claim file r497 + MSG-2100 guard-upgrade + S6 38/38 rc0"),
}


def fail(msg):
    print("ABORT:", msg)
    raise SystemExit(1)


def hb_surgery():
    text = open(HB, encoding="utf-8", newline="").read()
    pre = json.loads(text)
    for k, v in HB_SET.items():
        pat = re.compile(r'^(\s*)"%s": (.*?)(,?)$' % re.escape(k), re.M)
        hits = pat.findall(text)
        if len(hits) != 1:
            fail("hb key %s hits=%d (expected 1)" % (k, len(hits)))
        indent = hits[0][0]
        trailing = "," if hits[0][2] == "," else ""
        if isinstance(v, str):
            vv = json.dumps(v, ensure_ascii=False)
        else:
            vv = json.dumps(v)
        text = pat.sub(lambda m: "%s\"%s\": %s%s" % (indent, k, vv, m.group(3)), text, count=1)
    post = json.loads(text)
    assert post["heartbeat_epoch_utc"] == EPOCH and isinstance(post["heartbeat_epoch_utc"], int)
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$", post["clock_read"])
    assert post["round_no"] == 496
    assert len(post["orders_ack"]) == 155  # untouched face
    open(HB, "wb").write(text.encode("utf-8"))
    print("HB_SURGERY_OK epoch_int=%d clock=%s round=496 ack=155" % (post["heartbeat_epoch_utc"], post["clock_read"]))


def rr_append():
    raw = open(RR, "rb").read()
    if b"| r496 |" in raw or b"r496 bm-c S7" in raw:
        fail("r496 marker already present (r679 idempotence gate)")
    eol = b"\r\n" if raw.endswith(b"\r\n") or raw[-5000:].count(b"\r\n") >= raw[-5000:].count(b"\n") - raw[-5000:].count(b"\r\n") else b"\n"
    row = ("2026-10-04T20:55:20+08:00 | r496 | dept:研究（N2-W15 generate 首落收口·W3 judge 看护·舰队维护） | "
           "watermark verdict=绿（red=false·healthy·20:49 probe） | "
           "当前活=N2-W15 generate 产品首落收口（发现→验证→翻面→通报全链）+W3 judge 看护（pid 33768·20:48 verify IN_FLIGHT·CPU 10931.2s·ETA ~22:1x·池 4/4·ckpt 777/0dup） | "
           "最近实物=results/n2_w15/n2_w15_candidates.json（n=954·sha256 440db8656e3b0b2e…·20:45:29·首落 canonical per r486）+池面双层翻面（entry+own shard done·20:54:57）@ 2026-10-04T20:55:20+08:00 | "
           "下个里程碑=N2 screen-prep+12 SCREEN 分片入池（≤10-05 晚）；W3 judge 落地→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚） | "
           "S0: r437 预对齐净路（树脏 6 面∩origin 波={pool_core_samples,pool_red_flags}≠∅→treasure_guard rc0→origin-verbatim checkout 共享2→absorb 6100bbf44→merge 044f7b213 零 UU→push_verify DELIVERED 首推即达） | "
           "S0.5: _r496bmc_s05_check 双扫双 MATCH（decisions 4E5BE321+orders 68947C17）+0 未回执令+MSG-2005 消费入 processed（bm-a 动作面·bm-c 零义务） | "
           "S1 smoke 48/48 | S2 板空（job_list 0·fleet 0 open） | "
           "S3: satengine rc0 活（Tools 面 r467 律）+post_review ✓45/✗0/🟡5 零活红+W3 verify IN_FLIGHT 三证（r487 工时标定） | "
           "N2 收口实录: 轮中发现裸分片 generate-0of1 owner=bm-c（20:35:13 盲窗认领=r694① 第三次复发·bm-c 面）→daemon 台账核（20:35:01 launch pid 32808·relaunch_cooldown·零 harvest）→产品 20:45:29 已落→"
           "结构验证（_r496bmc_n2_product_check：parse OK·n=954·candidate_id 全唯一·seed_gen=541500〔源码 L122-144 vendor 口径·provenance 全 541500=设计态·trio=三阶段 band 由 FREEZE-GATE 烧前核过〕·grammar sha16 与池冻结面恒等·evidence_cutoff 2026-09-22 在位）"
           "=首落 canonical（r486·seeded deterministic r189 字节恒等族·refuse-if-exists 随 push 全机队武装）→"
           "burner-side 双层翻面（_r496bmc_n2_flip.py：gate0 origin 单点实核+gate1 vendor 口径+gate2 fuse 净+origin-freshest base〔r474 newer-wins 合规〕+行级 needle 引号全行匹配〔r694② 防裸 key 子串撞针〕+reparse 双门→entry+own shard=done·sibling bm-b 严格未触〔r626d-②〕·entries=378）"
           "+claim 回填（r497·rc 未直接观测诚实注记）+MSG-2026-10-04-2100-bmc-ALL（复发三例实证·护栏紧迫度升格·bm-b waiter 可提前杀） | "
           "S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51·378 entries·REPORT/LIVE 再生·四车道 stale-takeover derive 合法〔O-2100 s2.4〕） | "
           "记分: 2（n2_w15_candidates.json=能用实物〔954 候选直接喂 screen〕+S6 38 面再生） | "
           "记账预算: 5（state+心跳+轮报×2+MSG=法定面） | "
           "方法论捕获=无新方法（复用 r688 翻面/r487 看护/r437 净路正典范式·gate1 断言口径校准教训〔r480/r675 族〕如实入 verify 行）·宝藏捕获=无（generate=供给步·无判决面收口） | "
           "在册面行删除类=0（MSG-2005 100% rename 入 processed=移动模式白名单·无清扫无 quarantine·登记册零命中断言=不适用〔无清扫动作〕） | "
           "本地未达 origin commit 数: 收口 push 后自证 | "
           "下轮指针=r497 ①N2 screen-prep（bounds 从 954 行 derive·r670 铺瓦+r481 配方）+12 SCREEN 分片入池（先 fetch 实核+MSG 公示窗）"
           "②W3 judge 产品落地首查（_r487bmc_w3_judge_verify→ADOPT_PASS→宝藏捕获问+prereg §7/§8 回填+池翻面复核〔r668〕+48h CEO 报告钟）"
           "③bm-b canonical sibling waiter 收口盯梢（early-kill 或 rc=2 refuse）④fund-trio finalize 10-05 10:30（bm-b 正主）⑤O-2115/O-2030 验收 10-08")
    with open(RR, "ab") as f:
        f.write(row.encode("utf-8"))
        f.write(eol)
    back = open(RR, "rb").read()
    if back.count(b"| r496 |") != 1:
        fail("post-append marker count != 1")
    print("RR_APPEND_OK r496 marker=1 eol=%r" % eol)


def state_selfproof():
    doc = json.loads(open(ST, encoding="utf-8").read())
    assert doc["round_no"] == 496
    assert isinstance(doc["heartbeat_epoch_utc"], int) and doc["heartbeat_epoch_utc"] == EPOCH
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$", doc["clock_read"])
    print("STATE_SELFPROOF_OK round=496 epoch_int=%d" % doc["heartbeat_epoch_utc"])


if __name__ == "__main__":
    state_selfproof()
    hb_surgery()
    rr_append()
    print("S7_BOOKKEEPING_DONE")
