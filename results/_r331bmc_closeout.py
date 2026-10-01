import json, time, datetime, io, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_local = datetime.datetime.now().astimezone()
ts = now_local.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

REPORT_LINE = (
    ts + "｜r331｜dept:研究（N1-W20 finalize 波收口）｜watermark verdict=绿（probe loaded_ok·窗均 39.8%·假日板清态）｜"
    "S0-1 bm-c 锚定·S0 收敛=落后 9 commits 预置 ride rebase（15 UU 共享派生面取 origin 新侧〔CODELY 超集锚验 r315 律〕+r305 二连假拒绝→r501 净路 commit -C+quit+update-ref CAS·daemon 60s 竞态两次预置 ride 治愈）·"
    "S0.5 令差集=0（139 全 ack·轮首双扫）·D-19 水位 SHA MATCH-unchanged（753F99E8 raw-blob python 法）·S1 smoke 47/47｜"
    "主产出=**N1-W20 FINALIZE 一发闭环**（r310 完备性门：W18/W19 终稿件+W20 12/12 分片三面 ls-tree origin 核验全绿〔bm-a r532 W18 K=37,520·bm-b r518 W19 K=39,720 均落〕→finalize **K=41,920**·merged mu −0.0921/sigma 0.2444·W20-only mu −0.0905·"
    "**S5 四预测 4/4 PASS**〔K-lift +0.0006·skill_line 1.1496→1.1502 如实报正〕·账本 prev 406,348→+2,200→**408,548 链性**·prereg §7/§8 同窗回填〔r307 两态律〕·4 件套自证 n1 PASS+pf 8/8+engine 36/36+attrition CLEAN）→push b1e585dff 送达自证 0 未达（W21 bm-a 同窗冻结 20af40468 零撞·其机闸含我 W20 行）｜"
    "inbox=190x/194x processed+1922 双拷贝清理+MSG-195x 自发（r330 外科重播删 bm-a W18 产物=r516 镜像面认账+外科 ls-tree 对账承诺+W21 续带预告 84_001..86_000/38_900..39_099）｜"
    "S6 37/37 rc0（假日合法 no-op 群·dualrun streak 17 连绿·compute_audit 旗 pool_starvation/supply_floor=已知态〔引擎波车道旁路+供给线=W21 bm-a 在飞〕·scorecard/paper/export/dashboard 四面 stale-takeover 合法〔bm-a 心跳 30min>20min 阈〕·月度三件 15:03 已跑零双跑）·"
    "S7 绿（IterLoop 19:55 下一跑/Watchdog 19:50 两 schtask 活·claw MATCH·attrition CLEAN 双扫）｜"
    "坑律一枚入 CODELY（外科 rebroadcast stale 基静默删他机新增件=r516 镜像面）·CODELY 体量 83.7KB 水位旗（>50KB 触发线·r504 律=勿为字节数归档在役律·阈值重锚=GM/集团裁定面·本轮如实上旗）｜"
    "实况三行：当前活=W20 已落账·W21（bm-a）冻结在飞=引擎波供给线连转｜最近实物=results/perpetual_faces/n1_w20_results.json+prereg §7/§8 回填（origin b1e585dff·19:44）｜下个里程碑=T-134 s2 第八件+W21 finalize 跟踪（窗≤48h）·月界首考 10-31｜"
    "产品分=2（finalize 合并件+账本链节+S5 判定可验实物）｜本地未达 origin commit 数=0｜"
    "next: (r332)(a) T-134 s2 第八件 evidence-order rescan（t33/t36 自然 accrue·r304 律）(b) W21 finalize 跟踪（观察面·bm-a 主）(c) 月界首考清单 10-31（六员+SYSTEM-V1+REV-OSC+27 实验账户）(d) HANDOVER 5x stamp r335 (e) MSG-195x 回执观察"
)

CODELY_LINE = (
    "- [2026-10-01 19:5x r331 bm-c] 外科 rebroadcast 整树面 stale 基=静默删除他机新增件（r516 镜像面实弹定谳·r513/r516/r525 族第四犯变体·MSG-194x bm-b 恢复案）：r330 外科重播树自本机 stale 树面构建→bm-a r532 新增 n1_w18_results.json 被整树覆写静默删（bm-b r518 字节恢复+归属验·bm-a r533 自恢复·零科学污染=W19 已在场消费 W18 值）；与 r525「untracked 同路径覆写」互为镜像=「在册新增件蒸发」变体。正法（MSG-195x 承诺·本窗实证）：一切外科 rebroadcast/commit-tree 全树面动作=diff-based payload staging，或写树后对新基做「他机在册件 ls-tree 对账」断言（r331 W20 finalize 前置=W18/W19/W20 三面 ls-tree 核验后才动手）。How to apply：外科推送脚本必带 post-write ls-tree 对账腿（r516 律镜像腿），缺腿=禁推。"
)

VERIFY = (
    "r331: N1-W20 FINALIZE one-pass closed loop (r310 gate: W18/W19 finals + W20 12/12 shards ls-tree verified on origin -> "
    "K=41,920, merged mu -0.0921 sigma 0.2444, S5 4/4 PASS [K-lift +0.0006 honest positive], ledger 406,348+2,200=408,548 "
    "chain-linear; prereg sec.7/8 backfilled same window per r307 two-state law; selftests n1 PASS + pf 8/8 + engine 36/36 + "
    "attrition CLEAN; push b1e585dff delivered, 0 behind), S6 37/37 rc0 (holiday honest no-ops, dualrun streak 17), smoke 47/47"
)

# ---- state-bm-c.json ----
sp = REPO + r"\state-bm-c.json"
with open(sp, encoding="utf-8") as f:
    state = json.load(f)
state["round_no"] = 331
state["last_round_at"] = "r331"
state["last_round_ts"] = ts
state["updated"] = ts
state["cpu_pct"] = 69.0
state["idle_ram_gb"] = 3.0
state["gpu_free_vram_mib"] = 2686
state["verify"] = VERIFY
state["did"] = "r331 W20 finalize K=41,920 ledger 408,548 chain-linear + prereg sec.7/8 backfill + inbox 190x/194x processed + MSG-195x surgical ls-tree commitment + S6 37/37 rc0 + one CODELY law (r516 mirror face)"
state["current_task"] = "r331 delivered; W21 (bm-a slot) frozen same window and in-flight; bm-c next own wave = W23 per rotation law"
state["next"] = ("(r332)(a) T-134 s2 eighth conversion pick evidence-order rescan (t33/t36 natural accrual per r304 measurement-first law); "
                 "(b) watch W21 (bm-a) burn+finalize chain -- rotation slot law, bm-c observation only; "
                 "(c) month-boundary first-exam checklist 10-31 (six members + SYSTEM-V1 + REV-OSC + 27 experimental accounts); "
                 "(d) HANDOVER 5x stamp at r335; (e) watch MSG-195x replies (bm-b/bm-a ack on surgical commitment)")
state["heartbeat_epoch_utc"] = epoch
state["clock_read"] = ts
state["note"] = ("r331: W20 ninth engine wave fully closed (freeze r330 -> burn 12/12 r330 -> finalize r331 two-round window); "
                 "chain W18 404,148 -> W19 406,348 -> W20 408,548 all on origin; r330 rebroadcast deletion face (bm-a W18 product) "
                 "acknowledged + surgical ls-tree commitment per MSG-194x/MSG-195x; W21 frozen by bm-a same window with own band gate "
                 "(zero collision, their 19-row scan included my W20 row); CODELY at 83.7KB water-level flagged (GM threshold face per r504)")
state["last_ts"] = ts
state["last_decisions_sha"] = "753f99e81a27db3e1b4f2c76cd991ca50d52b80aa7faa63d6412cc2da1f5fb01"
state["last_decisions_read_at"] = ts
state["last_decisions_sha_method"] = "python subprocess.check_output raw-blob bytes SHA-256 (PS-pipeline join method = transcoding false-drift, see CODELY r292 pit)"
state["last_round"] = "2026-10-01 r331 bm-c: W20 finalize K=41,920 ledger 408,548 chain-linear + S5 4/4 PASS + inbox processed + S6 37/37 rc0"
state["last_seen"] = ts
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")

# ---- heartbeat fleet/machines/bm-c.json ----
hp = REPO + r"\fleet\machines\bm-c.json"
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
for k in ("cpu_util_pct", "cpu_pct"):
    hb[k] = 69.0
hb["cpu_idle_pct"] = 31.0
for k in ("free_ram_gb", "ram_free_gb", "idle_ram_gb"):
    hb[k] = 3.0
for k in ("gpu_free_vram_mb", "gpu_vram_free_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_free_vram_mib"):
    hb[k] = 2686
hb["prod_lanes"] = "r331: N1-W20 FINALIZE closed loop (K=41,920, S5 4/4 PASS, ledger 408,548 chain-linear, prereg sec.7/8 backfill) + inbox 190x/194x processed + MSG-195x surgical commitment + S6 37/37 rc0"
hb["round_no"] = 331
for k in ("updated_at", "last_seen", "last_seen_at"):
    hb[k] = ts
hb["current_task"] = "round 331 closeout: N1-W20 finalize delivered (K=41,920, ledger 408,548) + inbox processed + surgical commitment filed"
hb["verdict"] = ("healthy: N1-W20 finalize landed (K=41,920, S5 4/4 PASS, ledger chain 406,348->408,548, push delivered 0 behind), "
                 "engine alive (heartbeat fresh), S6 37/37 rc0, smoke 47/47, WM green (holiday board-clear), "
                 "supply line rotating = W21 (bm-a) frozen same window in-flight")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["health"] = "ok"
hb["activity_now"] = "W20 ninth engine wave FULLY CLOSED (freeze r330 -> burn 12/12 -> finalize r331 K=41,920 ledger 408,548); W21 (bm-a slot) frozen same window and in-flight on bm-a engine; bm-c idle per rotation law (next own wave W23)"
hb["latest_artifact"] = "results/perpetual_faces/n1_w20_results.json + research/PERPETUAL_N1_W20_PREREG.md sec.7/8 backfill (origin b1e585dff, 2026-10-01T19:44)"
hb["next_milestone"] = "T-134 s2 eighth conversion pick + W21 finalize tracking (window <=48h); month-boundary first exam 10-31"
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)
    f.write("\n")

# ---- appends ----
with io.open(REPO + r"\round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(REPORT_LINE + "\n")
with io.open(REPO + r"\CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write("\n" + CODELY_LINE + "\n")

# ---- self-cert: json.loads re-read + epoch int assertion ----
with open(sp, encoding="utf-8") as f:
    s2 = json.load(f)
with open(hp, encoding="utf-8") as f:
    h2 = json.load(f)
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(s2["heartbeat_epoch_utc"], int), "state epoch must be int"
assert isinstance(h2["round_no"], int) and h2["round_no"] == 331
print("WROTE ts=" + ts + " epoch=" + str(epoch))
print("state round_no=331, heartbeat round_no=" + str(h2["round_no"]) + ", epoch int OK")
print("CODELY size after append =", end=" ")
import os
print(os.path.getsize(REPO + r"\CODELY.md"), "bytes")
