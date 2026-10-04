"""r481 bm-c S7 closeout: orders rescan + W3 shard claim probe + heartbeat
IN-PLACE (roundtrip-gated r678) + state full-write (json.loads self-check
r645) + round report dual-line append (EOL-detected)."""
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

# --- W3 shard claim probe (engine pickup evidence) ---
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
w3e = [e for e in pool["entries"]
       if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD")]
assert len(w3e) == 4, len(w3e)
claim = {e["id"]: {"status": e["status"],
                   "owner": e["shards"][0].get("owner"),
                   "owner_since": e["shards"][0].get("owner_since")}
         for e in w3e}
print("W3_CLAIM", json.dumps(claim, ensure_ascii=False))

# --- heartbeat roundtrip gate (r678: load->dump->bytes compare) ---
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
    "当前活: W3 screen 4 分片已入池待引擎点火（MASS-TRIAL-W3-SCREEN-SHARD-0..3, n_rows 4909, "
    "bounds [0,1227)/[1227,2454)/[2454,3681)/[3681,4909), pool 368->372, 主产品 commit 48dbb31d6 已送达）"
    "— O-1440 sec.3 供料预置 + T-158 post-judge 消费面 | 最近实物: results/mass_trial/w3_candidates.json "
    "(4814 候选 sha16 见 enrollment 证据件) + w3_generate_summary.json (cw-dedup 1274 >600 带上沿如实披露) "
    "+ results/runnable_pool.json (+4 分片) + results/_r481bmc_w3_screen_enroll.json + "
    "results/_r481bmc_s6_log.txt (38/38 rc0) @ " + clock + " | 下个里程碑: W3 screen 烧录+finalize "
    "(4/4 分片 done 后 finalize+sec.7/8 回填+attrition 行) -> sec.9 s3 段冻结 <=10-12; fund-trio finalize "
    "10-05 10:30 (bm-b); O-2115/O-2030 验收 10-08; 开市 10-09")
hb2["heartbeat_epoch_utc"] = epoch
hb2["clock_read"] = clock
hb2["verdict"] = (
    "W3 supply->burn handoff landed same-round: generate complete (4814/75, "
    "pid 3484 15:18:49->15:38:03) + 4 screen shards enrolled per prereg sec.6 "
    "frozen c2141d6c1 (raw-text surgical, fail-closed x2 on CRLF/$ + substring-"
    "count false-fail, zero pool pollution); cw-dedup 1274 >600 band disclosed "
    "per sec.5.6 (rate 21.9% vs w2 28.6% base-consistent); quota_short 3 "
    "families honest; N2-W15 red card maintained (bm-b seat); S6 38/38 rc0; "
    "orders 154/154 dual-scan zero unacked; smoke 48/48")
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
    # line surgery fallback (r678 law: heartbeat roundtrip NOT stable --
    # e.g. legacy duplicate keys; keepends line swap preserves every other
    # byte incl. duplicates; ALL duplicate lines of a key get the fresh
    # value so json.loads last-wins face = fresh (smoke F7 safe)
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
    print("HEARTBEAT line-surgery: %d keys swapped, roundtrip was unstable"
          % len(swaps))

v = json.load(open(p, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock not T-sep"
assert len(v.get("orders_ack", [])) == len(ack), "ack count drift"
print("HEARTBEAT-OK epoch", v["heartbeat_epoch_utc"], "clock",
      v["clock_read"], "fields", len(v))

# --- state full-write (own file, single-writer; json.loads self-check r645) ---
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
n_ack = len(v.get("orders_ack", []))
st["round_no"] = 481
st["last_round"] = ("r481 bm-c: W3 generate products + screen 4-shard pool enrollment "
                    "(prereg sec.6, n_rows 4909 bounds tiling, raw-text surgical 368->372, "
                    "cw-dedup 1274 >600 disclosed, quota_short 3 honest); S6 38/38 rc0; "
                    "orders 154/154 dual-scan; post_review zero active red; attrition CLEAN")
st["last_round_at"] = clock
st["last_round_ts"] = clock.replace("T", " ")[:19]
st["last_seen"] = clock
st["updated"] = clock
st["updated_at"] = clock
st["next"] = ("(a) r482: W3 screen burn watch (4 shards on pool, engine-tick claim; 4/4 done "
              "-> screen finalize + sec.7/8 backfill + attrition row). (b) fund-trio finalize "
              "window 10-05 10:30 opens (bm-b owner; V ETA 10-06 / Q long-pole 10-07). "
              "(c) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. (d) O-2115/O-2030 + "
              "T-158/T-162 acceptance 10-08; market reopen 10-09. (e) W3 sec.9 s3 judge-face "
              "freeze <=10-12 (O-2115 standing supply line).")
st["did"] = ("r481 bm-c W3 supply-line round: (1) S0 daemon lane absorb 68ff8fcce + merge "
             "origin x2 (bm-b r678 S6/W117-118 wave + bm-a r683 W117 gate wave) zero UU "
             "x2; push#1 REJECTED (fleet wave) -> merge#2 -> push_verify DELIVERED. "
             "(2) S0.5 orders 154/154 dual-scan zero unacked; D-19 decisions 4E5BE321 + "
             "group orders 68947C17 double MATCH (per-key raw-blob) -> zero consumption; "
             "inbox 3 (W117/W118 seats + N4-B4 landmine MSG-1600) read + archived. "
             "(3) S1 smoke 48/48. (4) S2 boards empty (job_list 0, fleet 0 open). "
             "(5) S3 satengine rc0 alive (Tools registration face); MAIN PRODUCT = W3 "
             "generate completion verified (4814 cand / 75 fam, summary landed) -> "
             "MASS-TRIAL-W3-SCREEN-SHARD-0..3 enrolled per prereg sec.6 (n_rows 4909 = "
             "4814+75+20, exact tiling bounds, raw-text surgical +162/-2, anti-double gate, "
             "coverage-tile guard, fail-closed aborts x2 zero pollution) + generate products "
             "committed same commit (deps green fleet-wide) -> commit 48dbb31d6 push_verify "
             "DELIVERED ahead=0/behind=0. Cross-wave dedup 1274 (916 param + 358 signal) "
             ">600 band -> sec.5.6 mechanism-review disclosure (rate 21.9% vs w2 28.6% = "
             "base-growth-consistent). (6) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 51 "
             "pre-enrollment cutoff; market_regime ORANGE shadow days=2; golden-week no-new-"
             "bar legs honest no-op; token delta=0). (7) S7 loop pin5 phase-ok + watchdog "
             "re-registered + dual claws LF-normalized + attrition CLEAN + post_review "
             "45Y/0N/5W zero active red.")
st["verify"] = ("W3 enrollment evidence = results/_r481bmc_w3_screen_enroll.json (bounds/tiling/"
                "difflib +162/-2, pool 368->372, cw 1274 flag) + commit 48dbb31d6 push_verify "
                "DELIVERED (tip==remote, ahead=0/behind=0); smoke 48/48; S6 38/38 rc0 "
                "(_r481bmc_s6_log.txt, chain-end marker, NON-ZERO=none); orders 154/154 "
                "S0.5+S7 double-scan same-shape zero-diff; D-19 dual MATCH per-key raw-blob; "
                "post_review REPORT-20261004 45Y/0N/5W; attrition CLEAN (4 ledgers); claws "
                "LF-normalized x2; loop pin5 phase-ok; watchdog present; heartbeat epoch int "
                "+ clock T-sep + ack-count in-place assertion POST-WRITE; state json.loads "
                "self-check")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = clock
st["cpu_pct"] = 68.4
st["current_task"] = hb2["current_task"]
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 481 and isinstance(chk["heartbeat_epoch_utc"], int)
print("STATE-OK round_no", chk["round_no"])

# --- round report dual-line append (EOL-detected, r641 newline='' law) ---
rp = "round_reports-bm-c.md"
rp_raw = open(rp, "rb").read()
rp_eol = b"\r\n" if b"\r\n" in rp_raw[-200:] else b"\n"
now_hm = clock.replace("T", " ")[:19]
main_line = (
    now_hm + "｜r481｜dept:策略/研究（W3 供给线 generate 收割+screen 分片入池轮·O-1440 §3 供料预置）｜"
    "watermark verdict=绿（red=false healthy·py_watermark 复探 py_low_with_work_cands=供给同窗响应："
    "work cands=W3-SCREEN 4 分片刚入池待引擎 tick 领〔非违令·r480 同型〕·采样窗 py 68.4%=本机 S6 链自身）｜"
    "当前活=W3 generate 完成核验+screen 4 分片入池+主产品送达｜最近实物=results/mass_trial/w3_candidates.json"
    "（4814 候选）+w3_generate_summary.json（cw-dedup 1274）+results/runnable_pool.json（+4 分片·368→372）+"
    "results/_r481bmc_w3_screen_enroll.json+results/_r481bmc_s6_log.txt（38/38 rc0）@ " + clock + "｜"
    "下个里程碑=W3 screen 烧录+finalize（4/4 done 后 §7/§8 回填+attrition 行）→ §9 s3 段冻结 ≤10-12+fund-trio "
    "finalize 10-05 10:30（bm-b）+O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜"
    "S0: 无 rebase 残留·轮首 3 脏面=本机 daemon 车道面→absorb 68ff8fcce+merge origin（bm-b r678 wave：S6 件+"
    "W117/W118 座席+MSG-1532）零 UU→push REJECTED rc1（fleet wave）→merge#2（bm-a r683 W117 带闸面+CODELY 1 行）"
    "零 UU→push_verify DELIVERED tip 0b6281c16｜S0.5: 令差集 0（154/154 同形态集合比对双扫）·D-19 decisions "
    "4E5BE321+group orders 68947C17 双 MATCH（per-key raw-blob SHA-256/SHA-1）零消费·inbox 3 件读毕归档"
    "（MSG-1600 N4-B4 梯子地雷披露=未来 N4 开窗必带 horizon 门·零本机动作；MSG-1532/1535 W117/W118 座席="
    "bm-a/bm-b N1 线·与本机 W3 域零撞）｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 0 open）｜S3: satengine rc0 活"
    "（Tools 注册面）·N2-W15 红牌维持（bm-b 属主未交禁碰）·W14 停泊维持 per O-0808｜主产出：W3 generate 完成核验"
    "（pid 3484 15:18:49→15:38:03·4814 候选/75 族·quota_short 3 族诚实 ceiling-not-quota）→screen 4 分片入池"
    "（prereg §6 冻结面：n_rows 4909=4814 候选+75 对照+20 null·精确铺瓦 bounds [0,1227)/[1227,2454)/[2454,3681)/"
    "[3681,4909)·r678 行级外科 +162/-2·反双录门+铺瓦守卫+reparse+计数断言）→generate 产物同 commit 送达"
    "（deps 全机绿）→主产品 commit 48dbb31d6 push_verify DELIVERED（ahead=0/behind=0）·fail-closed 两拦实录"
    "（CRLF $ 撞+updated_at 子串计数假败〔entries 自带 7 处〕——两次写前断言拦·零池污染·行级手术 keepends 形治愈）｜"
    "§5.6 披露：跨波去重坍缩 916 param+358 signal=1274>600 带上沿→机制复核披露（率 21.9% vs w2 28.6%=去重基扩至 "
    "5811 的基增长一致面·非机制异常·§7/§8 回填时对账）｜S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51"
    "〔368 entries·入池前采样 cutoff 13:26:30=时序合法〕·update_daily 金周零新行 cutoff 2026-09-30·"
    "market_regime ORANGE shadow days=2·post_review REPORT-20261004 45Y/0N/5W 零活红·REPORT/LIVE-2026-10-04 "
    "幂等再生·金周无新 bar 腿诚实 no-op·token delta=0）｜S7: loop pin5 phase-ok（first fire 15:45）·watchdog "
    "重注册（幂等·first fire 15:44）·双爪 LF 归一安装到位·attrition CLEAN（4 ledgers·healed 注记照录）·orders S7 "
    "二扫 154/154 零差｜S4: 零新坑律行（四问门：CRLF-$ 形=r402/r657 在册 EOL 域族的应用面失误·fail-closed 自愈"
    "=在册律运转实录·无新机制不 append）｜记分: 2（W3 screen 4 分片入池=可跑实物面〔引擎即领即烧〕+generate 产物"
    "4814 候选+S6 38 腿管线产出·非空转）｜记账预算: 3/5（state+心跳+轮报·CODELY 零行）｜本地未达 origin commit 数: "
    "收口 push 后 push_verify 自证（DELIVERED 后=0）｜登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作"
    "（treasure_guard 零调用面·五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实〔screen finalize "
    "时再评〕）｜下轮指针=r482 W3 烧录监烧（引擎 tick 认领+keepalive+checkpoint 增长三证）→4/4 done 后 finalize"
    "（§7/§8 回填+attrition 行+宝捕获问）+fund-trio finalize 10-05 10:30（bm-b 正主）")
close_line = (
    clock + "｜r481 bm-c S7-close｜本地未达 origin commit 数=0（收口 push 后 push_verify 单源自证·DELIVERED 后=0）｜"
    "收口实录：round commit 48dbb31d6（12 面：W3 生成产物 3 件+池 +4 分片+grammar w3 行+S6 件 4+enroll 证据 2+"
    "generate log）→push_verify DELIVERED tip 48dbb31d6（ahead=0/behind=0·主产品先达=fleet 可领面）→close commit"
    "（S6 管线产物+簿记三写+inbox 归档 3+daemon 车道 absorbs）→push_verify 终证｜W3 分片认领态（收口时点探针）="
    "见 _r481bmc_s7close.py stdout（W3_CLAIM 面）·引擎 tick 领取属下轮证据面｜零清扫/归档/删除/恢复类动作轮：登记册"
    "零命中断言照实｜轮产品计分：2（可跑/能看实物=入池 4 分片+4814 候选生成产物+S6 38 腿产出·等待态声明："
    "screen 烧录归引擎 autofill 域非空转）")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write((main_line + "\n").replace("\n", rp_eol.decode()))
    f.write((close_line + "\n").replace("\n", rp_eol.decode()))
lines_now = open(rp, encoding="utf-8").read()
assert lines_now.count("r481 bm-c S7-close") == 1, "close line count"
assert lines_now.count("｜r481｜") == 1, "main line count"
print("REPORT-OK r481 dual-line appended, file lines",
      len(lines_now.splitlines()))
