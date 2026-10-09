# r945 bm-a closeout: heartbeat + state + round-report bookkeeping.
# r818 law: load file -> modify fields -> dump (orders_ack list never retyped).
import datetime
import json

EPOCH = int(datetime.datetime.now().timestamp())
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
R = 945

DID = ("r945: PARKING-P1 dead-session estate absorbed + judgment batch closed "
       "(0/3 register, 0/24 full-chain, honest negative; prereg sec7/8 one-shot "
       "backfill + RETAIL_QUANT_TRACK 348/500 + rolling-window descriptives) + "
       "32-face rebase storm canon-resolved + push 0/0 verified")
ART = ("research/PARKING_P1_PREREG.md sec7/8 backfilled (17,291->29,515B, commit "
       "40acbc2f1 on origin) + results/parking_p1.json (24-cell verdict) + "
       "results/_r945bma_resolve.py (32-face receipt)")
NEXT = ("r946: watch window (W17 funnel bm-c lane; W204 arm bm-c seat owner; "
        "bm-a next N1 seat = W205 after W204 first-burn) + B-pool sub-batch "
        "awaits bm-c jsl scanner >=10-16; PARKING-P1 closed verdict-gated")
VERDICT = ("green (r945: parking judgment closed honest-negative; smoke 49/49; "
           "S6 39/39 rc0 absorbed; attrition CLEAN; quartet GREEN; push 0/0; "
           "engine ALIVE idle; DEC b87a92b1/ORD 0ddb01d9 MATCH)")


def heartbeat():
    p = "fleet/machines/bm-a.json"
    d = json.load(open(p, encoding="utf-8"))
    assert isinstance(d.get("orders_ack"), list) and len(d["orders_ack"]) >= 199
    d["machine_id"] = "bm-a"
    d["last_seen"] = CLOCK
    d["ts"] = CLOCK
    d["clock_read"] = CLOCK
    d["heartbeat_epoch_utc"] = EPOCH
    d["last_heartbeat_epoch_utc"] = d.get("heartbeat_epoch_utc", EPOCH)
    d["round_no"] = R
    d["round"] = R
    d["loop_round"] = R
    d["last_round"] = 944
    d["last_round_at"] = CLOCK
    d["last_round_ts"] = CLOCK
    d["last_run"] = CLOCK
    d["updated"] = CLOCK
    d["updated_at"] = CLOCK
    d["did"] = DID
    d["last_action"] = "r945 closeout: parking estate absorbed + verdict finalized"
    d["current_task"] = NEXT
    d["now_active"] = NEXT
    d["current"] = NEXT
    d["task"] = NEXT
    d["next"] = NEXT
    d["last_artifact"] = ART
    d["latest_artifact"] = ART
    d["recent_artifact"] = ART
    d["next_milestone"] = ("W204 arm by bm-c owner -> bm-a W205 seat; "
                           "W17 funnel bm-c; month-exam 10-31 (T-143 assembly 10-29)")
    d["verdict"] = VERDICT
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["cpu_pct"] = 14.1
    d["cpu_total_pct"] = 14.1
    d["cpu_load_pct"] = 14.1
    d["ram_free_pct"] = 65.2
    d["free_ram_pct"] = 65.2
    d["vram_free_gb"] = 8.6
    d["gpu_free_vram_gb"] = 8.6
    d["last_decisions_sha"] = ("b87a92b1b445fd1dab4daa9250c9d52eb85e0ac"
                               "122c7b870ce5f83e822c67374")
    d["last_orders_sha"] = ("0ddb01d9aca7588382fb4341651f6d7548503070d"
                             "4a12cf98c2774346d48276e")
    d["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH r945 scan; zero new BigMoney dispatch"
    d["last_orders_seen"] = "r945 scan zero unacked (60 files vs 199 ack, ORD 0ddb01d9 unchanged)"
    d["last_decisions_at"] = "2026-10-10"
    d["last_orders_at"] = "2026-10-10"
    d["last_decisions_ts"] = CLOCK
    d["last_orders_ts"] = CLOCK
    d["push_verified"] = {"ts": CLOCK, "origin_tip": "40acbc2f1",
                          "ahead_behind": "0/0",
                          "note": "r945 delivered via 32-UU rebase canon-resolve "
                                  "(S3-newest x24 + twins x4 ours + CODELY union + "
                                  "compute_audit history union 204-cap + regime union "
                                  "3 + x2 jsonl union 1565 + attrition-scan theirs-newer) "
                                  "+ clean second rebase onto bm-b r820 addendum; "
                                  "post-push fetch+rev-list 0/0 verified"}
    d["sync"] = dict(d["push_verified"])
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    d2 = json.load(open(p, encoding="utf-8"))
    assert isinstance(d2["heartbeat_epoch_utc"], int)
    assert "T" in d2["clock_read"]
    assert len(d2["orders_ack"]) >= 199
    print("heartbeat OK epoch=%d clock=%s" % (d2["heartbeat_epoch_utc"], d2["clock_read"]))


def state():
    p = "state-bm-a.json"
    d = json.load(open(p, encoding="utf-8"))
    d["round_no"] = R
    d["round"] = R
    d["loop_round"] = R
    d["last_round"] = 944
    for k in ("clock_read", "last_seen", "ts", "updated", "updated_at",
              "last_round_at", "last_round_ts", "last_run", "last_round_closed"):
        d[k] = CLOCK
    d["did"] = DID
    d["last_action"] = "r945 closeout: parking estate absorbed + verdict finalized"
    d["current_task"] = NEXT
    d["now_active"] = NEXT
    d["task"] = NEXT
    d["current"] = NEXT
    d["next"] = NEXT
    d["last_artifact"] = ART
    d["latest_artifact"] = ART
    d["verify"] = VERDICT
    d["verdict"] = VERDICT
    d["next_milestone"] = d.get("next_milestone", "")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_faces"] = 1
    d["heartbeat_epoch_utc"] = EPOCH
    d["last_heartbeat_epoch_utc"] = EPOCH
    d["round_no_label"] = "r945"
    d["last_orders_seen"] = "r945 scan zero unacked (60 files vs 199 ack, ORD 0ddb01d9 unchanged)"
    d["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH r945 scan; zero new BigMoney dispatch"
    d["push_verified"] = {"ts": CLOCK, "origin_tip": "40acbc2f1",
                          "ahead_behind": "0/0",
                          "note": "r945 delivered via 32-UU rebase canon-resolve; post-push 0/0 verified"}
    d["sync"] = dict(d["push_verified"])
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    d2 = json.load(open(p, encoding="utf-8"))
    assert d2["round_no"] == R and isinstance(d2["heartbeat_epoch_utc"], int)
    print("state OK r945")


def report():
    p = "round_reports-bm-a.md"
    line = (
        "2026-10-10T07:1x+08:00 | r945 | bm-a | dept:研究 (PARKING-P1 停泊域首判决批全程收口·死会话遗产吸收) | "
        "WM-VERDICT: insufficient_history 非红 07:03:59（pool_ready=[] 空=THERMO 关链保持·r943 教训零复发；"
        "idle trigger GREEN-IDLE RAM 65%/VRAM 8.59GB + idle_rounds=2 two_read_red → 本轮实际产出工 --worked 清零·"
        "池 ready 全=W17 族 lane-pinned bm-c 不可跨机认领·backlog 0 未领） | "
        "当前活: PARKING-P1 判决批收口完成·守望窗续（W17 funnel bm-c/W204 bm-c seat/bm-a 下波 W205 待 W204 首烧） | "
        "最近实物: research/PARKING_P1_PREREG.md §7/§8 机器回填一次定稿（17,291→29,515B·commit 40acbc2f1 on origin）"
        "+results/parking_p1.json（24 格判决·sha16 e8abd542）+research/parking_p1_results.csv+"
        "RETAIL_QUANT_TRACK §四行 348/500+results/_r945bma_resolve.py（32 面 rebase 收据） | "
        "下个里程碑: W204 arm（bm-c owner）→bm-a W205 席位；B-直池子批待 bm-c 集思录采集器 ≥10-16；"
        "10-21 PARKING 回访首报数+10-31 月考停泊增益面（零增益如实）·月界首考 10-31（T-143 装配 10-29） | "
        "did: S0-1 anchor bm-a + orphan_face=1（ComfyUI 8188 MV-lane 豁免只读）+ "
        "**r945 死会话遗产吸收**（前窗 06:2x-06:42 跑完 5x 戳+S6 39 腿链+PARKING runner build+run 后猝死·state/轮报零写——"
        "吸收链=runner selftest 20/20 后继复验 PASS+results/CSV/账本行（gate_attrition entries[107] 06:42:14 +24→862,175）"
        "字节验证+六员面锚逐项恒等（3,273/797/2,204/1,570/3,266/3,273 行·首读 511090=597 系 GBK 乱码吞字误读·UTF-8 复读=797 精确恒等）"
        "+G1' 线 5.1562 极端值公式验真（skill_line_v2=max(passive+0.10, μ+σ√(2lnN_eff))·N_eff=862k 级→√=5.228·"
        "−2.6542+1.4939×5.228=5.157 ✓ 共享库冻结公式如实运转）+滚动 3/5y 最差窗描述面（runner 机械 import 复算零重实现·"
        "三幸存者最差窗全落 2025+ 段=非平稳实锚）→ **prereg §7/§8 一次定稿回填**（§7.1 24 格全列+§7.2 Face-2 三员拒收+"
        "§7.3 全起点分布+滚动窗+§7.4 试验量归因 24 格+§5 对账 对6/部分7/错4+§8 判负收线+runner 三缺口诚实披露"
        "〔prereg_sha256_at_run 未落·后继补算 851e43fe+§5 块由本件承载+probe 超集〕）+RETAIL_QUANT_TRACK §四闸记账 324→348/500+"
        "HANDOVER 5x 戳（死窗草稿面收编时三段合并补全 parking 事实·未提交面补全=非史改）+CODELY.md 行级追加（29,377B 帽内）"
        "+**判决=0/3 instrument 注册·0/24 格过全链**（Face-1 幸存 3 格 511090/120 t=3.26·511260/120 t=5.56·511380/120 t=4.92 "
        "全被 G1' 极端值线 5.1562 拒·PBO 136 行<CSCV 160 底=诚实缺输入→G2 拒收·DSR 0.9307/0.9999/0.9999·D6 零拒收 "
        "max|corr| 0.136/0.300/0.163/0.270 全<0.70）+判负收线=停泊 vehicle 维持 C2 repo 代理（GC001）·"
        "复活条件=复权面板数据债清后另开 prereg+exit-to-asset 工程腿 verdict-gated 不放线）+ "
        "S0 双 rebase 风暴正典解（32 UU：CODELY union 45+45→46+docs 双胞胎×4 同侧 ours 06:55>06:25+平面 json S3-newest ×24 "
        "〔attrition scan 例外取 theirs 07:03>06:58〕+compute_audit history union 201+3=204 窗帽保真+regime union 3+x2 jsonl "
        "union 1559+6=1565·E42 写者停窗 4 任务 disable→rebase→enable·GIT_EDITOR=true continue）+clean 二段 rebase onto "
        "bm-b r820 addendum d8ca428c7 + push 40acbc2f1→fetch+rev-list **0/0 送达自证** + S0.5 双扫：orders 0 unacked"
        "（60 files vs 199 ack）+DEC b87a92b1/ORD 0ddb01d9 python-raw 双 MATCH 零消费零动作+inbox 0 未读 + S1 smoke 49/49 "
        "（真退出码 0·Select-Object 管道伪码 1 面勘破）+ S6 39 腿 rc0 receipt 吸收（死窗 06:22-06:26 链·周六 no-new-bar "
        "面板尾 2026-10-09 pre==post）+attrition guard 4 台账 CLEAN+SatEngine ALIVE rc0 idle queue0+四件套 GREEN"
        "（loop pin=8 no-op first-fire 07:18/watchdog -Force 07:13/双爪字节等 True）+post_review 尾 3 行全 YES 零红+"
        "treasure capture：零新方法零新宝藏（stint 机械=血统复用·判据=共享库零重实现·结论型入正典件承载——如实留痕） | "
        "verification: smoke 49/49 + runner selftest 20/20 + 面锚六员恒等 + S6 39/39 rc0 + attrition CLEAN + "
        "quartet GREEN + push 0/0 自证 + heartbeat epoch int 自证 + T 分隔钟 | "
        "scoring: 2（判决批全链收口=能跑能看能用：runner+24 格判决 JSON+CSV+§7/§8 回填正典件+滚动窗面+RESOLVER 收据） | "
        "bookkeeping: 5/5（state 944→945+轮报行+心跳+CODELY 行+RQT 行） | "
        "treasure-capture: 零 append 如实 | orphan_face=1（MV 车道豁免） | unacked_orders=0（S0.5+S7 双扫） | "
        "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | token: L1 零 API（死窗链 token_usage 面已并） | "
        "[r945 bm-a]\r\n")
    b = open(p, "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n"), "CRLF face"
    text = b.decode("utf-8")
    assert "[r945 bm-a]" not in text, "already reported"
    if not text.endswith("\r\n"):
        text += "\r\n"
    text += line
    open(p, "wb").write(text.encode("utf-8"))
    b2 = open(p, "rb").read()
    assert b2.count(b"\r\n") == b2.count(b"\n")
    assert "[r945 bm-a]" in b2.decode("utf-8")
    print("report OK", len(b), "->", len(b2))


if __name__ == "__main__":
    heartbeat()
    state()
    report()
