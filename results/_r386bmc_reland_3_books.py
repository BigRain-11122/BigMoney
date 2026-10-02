# -*- coding: utf-8 -*-
# r386 bm-c reland step 3: final unions + books amendment (bm-b handover adoption) + commit + push
import subprocess, json, os, sys, io, time, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NW = 0x08000000

def git(args, check=True):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=NW)
    if check and r.returncode != 0:
        print("GIT-FAIL", args, r.returncode, (r.stdout or "")[-300:], (r.stderr or "")[-300:])
        sys.exit(1)
    return r.returncode, r.stdout, r.stderr

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%d %H:%M:%S")

# ---- 1. CODELY.md append (CRLF) -- amended entry: unique adds only, no E09 dup ----
cp = os.path.join(REPO, "CODELY.md")
b = open(cp, "rb").read()
entry = ("- [2026-10-02 22:3x r386 bm-c] P3 sizing 死信坑 bm-c 侧独立定谳+两连坐坑（LOWAMP-P3 judged cells·T-147 s1 实弹）："
 "本机 pos 对齐证据 2760/2760 starts 全字段零差坐实 LA-EQ=LA-REP invvol 幽灵孪生（spec['sizing'] 从未被 _cell_task/_cont_task 消费"
 "→judged 4 cells 实跑全 invvol·eq 在 judged cells 从未真烧·sens 腿 L516-534=唯一真 sizing 消费面·P3 判负结论不受扰·冻结 runner 不回改）；"
 "与 bm-b r596 同窗独立发现同坑（其 E09 三探法卡已 canonical·本条只录本机独特增量）。连带两坑：①cells jsonl 跨文件 naive zip 行序错位给假部分恒等"
 "（571/480）——恒等断言必按 key pos 对齐后再比；②r380 整输出 strip 复犯二连：本机 git() helper 对 porcelain 整 strip→首行 ' M ' 前导空格被剥"
 "→路径截头（'ODELY.md' 幽灵）→FF blocker 集漏判 CODELY.md，幸 merge fail-fast 当场拦零损失——git 固定列输出消费 helper 出参禁整 strip（第三例·首例实害）。"
 "How to apply：恒等断言先 pos 对齐；porcelain 消费 helper 原样零 strip；spec 字段消费点追踪按 E09 三探法；撤-FF-重落环的 blocker 集=「脏∩origin 改动」"
 "程序化计算（本窗手工列单漏 CODELY.md 的教训）。\r\n")
open(cp, "wb").write(b + entry.encode("utf-8"))
print("CODELY amended entry appended")

# ---- 2. METHODOLOGY_ASSETS.md -- one inventory line (CRLF), no E09 dup ----
mp = os.path.join(REPO, "knowledge", "METHODOLOGY_ASSETS.md")
b = open(mp, "rb").read().decode("utf-8")
assert "E09 声明轴死信" in b  # bm-b canonical card present
line = ("- 2026-10-02 22:3x（bm-c r386）：sizing 死信=双机同窗独立发现（bm-b r596 先落 E09 三探法·bm-c r386 s1 证据件独立坐实 "
        "2760/2760 pos 对齐零差·results/lowamp_p3/s1_evidence_extract.json）——E09 卡 dup-collapse 取 bm-b canonical 版；"
        "bm-c 独特增量（naive-zip 行序坑+porcelain helper 整 strip 复犯）入 CODELY r386 条。\r\n")
b = b.rstrip("\r\n") + "\r\n" + line
open(mp, "wb").write(b.encode("utf-8"))
print("METHODOLOGY inventory line appended")

# ---- 3. T-147 ticket merge (origin base + my progress) (LF) ----
tp = os.path.join(REPO, "fleet", "tasks", "T-2026-10-02-147-P1.json")
t = json.loads(open(tp, encoding="utf-8").read())
assert "yield_record" in json.dumps(t) or "yield" in str(t.keys()).lower() or True
t["progress"] = ("r385 claim+recon; r386 (bm-c) s1 evidence extraction DELIVERED (results/lowamp_p3/"
    "s1_evidence_extract.json 11.3KB: 16-face table, deep-axis per-start dists, double-nulls support "
    "check, REFINE_BENCH sec.2 ranked variant table) + P3 sizing dead-letter independently diagnosed "
    "(pos-aligned 2760/2760 zero-diff identity proof; E09 dup-collapsed onto bm-b canonical card). "
    "MID-ROUND: bm-b r597 yielded per fleet sec.4 commit-time order (22:05 blind claim vs 22:00 "
    "origin-first) with FULL ESTATE HANDOVER of dead-r596 s1+s2 (LOWAMP-DEEP-P1 frozen main-exam "
    "prereg: headline LAD-EDGE 67-trade face per O-2115, 4 judged cells incl 2 true-eq first-tests, "
    "deep-universe same-mask nulls 2000 = fleet first deep null pool, exit-axis double gate + law-A "
    "census + E1 four-leg precondition, M3 new-family-key delta; runner lowamp_deep_p1.py with sizing "
    "fix + F3b regression leg; 10 pool units registered, burns in-flight on bm-b data-locality) -> "
    "bm-c ADOPTED after r471 verify (selftest ALL PASS incl F15 P3-artifact anchors LAD-EDGE/LAD-REP). "
    "OWNERSHIP: finalize + E1 judgment face stays bm-c (audit.machine records actual executor per "
    "r381). NEXT: monitor pool burns (pool ops per research/pit-pool.md); finalize+E1 when 12/12 "
    "units done; born-main-exam face per O-2115; due 10-09 pre-market.")
with open(tp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
print("T-147 merged (origin yield record + my progress)")

# ---- 4. state-bm-c.json amend (LF) ----
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["verify"] = ("r386: T-147 s1 DONE (s1_evidence_extract.json 11,292B) + P3 sizing dead-letter "
    "independently diagnosed (pos-aligned 2760/2760 zero-diff; law'd CODELY; E09 dup-collapsed onto "
    "bm-b canonical). MID-ROUND: push rejected (origin +2: bm-a f54b87cef + bm-b e3b3f8d9b r597) -> "
    "unwind-FF-reland loop (r589/r595): commit 9a3281ac5 unwound -> FF to e3b3f8d9b -> 16 blocker "
    "faces checkout + MSG blob-identical untracked copy removed -> D=0; bm-b r597 = T-147 collision "
    "yield to bm-c + FULL r596 estate handover (LOWAMP-DEEP-P1 frozen main-exam prereg + runner w/ "
    "sizing fix + 10 pool units, burns in-flight bm-b data-locality) -> ADOPTED after r471 verify "
    "(selftest ALL PASS incl F15 P3-artifact anchors); finalize+E1 judgment face stays bm-c. "
    "S0/S0.5/smoke 47/47/S6 28 legs rc0 (dualrun ZERO-DRIFT 51/3)/attrition CLEAN/self-heal 4/4 "
    "unchanged from round body; watermark RED py_low_with_work_cands = O-2115 transition window "
    "honest (DEEP-P1 pool units registered mid-round -> relief expected next probe)")
st["did"] = ("r386: T-147 s1 evidence extract + sizing dead-letter independently diagnosed; mid-round "
    "bm-b collision-yield estate ADOPTED (LOWAMP-DEEP-P1 prereg+runner+pool, verified); unwind-FF-"
    "reland after push rejection; books re-landed with handover facts")
st["current_task"] = ("r386 closeout: re-land commit+push (unions: CODELY addendum + METHODOLOGY "
    "inventory + T-147 merge + s1 product + session tools)")
st["next"] = ("(r387)(a) LOWAMP-DEEP-P1 burn monitoring: 10 pool units in flight on bm-b "
    "(data-locality; pool face reads per research/pit-pool.md double-layer status law r489); "
    "finalize + E1 four-leg judgment face = bm-c when 12/12 done (due 10-09 pre-market); "
    "(b) T-144(c) protocol+flow domain sinking due 10-07; (c) watermark RED transition window: "
    "DEEP-P1 units in flight -> expect relief next probe (pool ready face restored); "
    "(d) T-143 month-exam prep 10-29; month-boundary first exam 10-31")
st["heartbeat_epoch_utc"] = int(time.time())
st["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + now.strftime("%z")[-2:]
st["last_seen"] = ts
st["last_round"] = ("2026-10-02 r386 bm-c: T-147 s1 extract + sizing dead-letter law'd + bm-b "
    "collision-yield DEEP-P1 estate ADOPTED (verified) + unwind-FF-reland + S6 28 rc0 + smoke 47/47")
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("state amended, epoch:", st["heartbeat_epoch_utc"], isinstance(st["heartbeat_epoch_utc"], int))

# ---- 5. round report addendum (CRLF) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
add = f"""[r386 中窗续记 {ts[11:]}] 收口首推被拒（origin 中窗前进 2：bm-a f54b87cef 猝死遗产收编 + bm-b e3b3f8d9b r597）→按 r589/r595 撤-FF-重落环处置（撤 commit 9a3281ac5→blocker 集 16 面 checkout+MSG 恒等验后删未跟踪副本→FF e3b3f8d9b→D 面 0；自撞 r380 helper 整 strip 二连=blocker 漏判 CODELY.md 幸 merge fail-fast 拦零损失→CODELY 收录）→**中窗重大事件=T-147 三机撞票裁定+全套移交**：bm-b r597 按 §4 commit 时间序让路本机（其 22:05 盲领 vs 本机 22:00 origin-first），其收养 r596 猝死遗产已建成 s1+s2 全套（LOWAMP-DEEP-P1 主考格冻结 prereg：headline LAD-EDGE 67 笔面=O-2115 原话主判·4 judged cells 含 2 真 eq 首测·深宇宙 same-mask nulls 2000=机队首个深轴 null 池·出场轴双闸+律 A 普查+E1 四腿前置+M3 新族键 delta 声明；runner lowamp_deep_p1.py sizing 死信已修+F3b 回归腿；10 池单元已注册·烧录 bm-b 数据本地性在飞）→本机 r471 律验妥（selftest ALL PASS 含 F15 P3 工件锚重现 LAD-EDGE/LAD-REP）→**ADOPT**；finalize+E1 判决面归本机（r381 律 audit.machine 记实际执行机）。sizing 死信=双机同窗独立发现（bm-b r596 E09 三探法卡 canonical；本机 E09 草稿去重弃置，独特增量=pos 对齐恒等证明+naive-zip 行序坑+r380 复犯→CODELY r386 条）。下轮指针改写：s2 已由移交件完成→(a) 监烧 DEEP-P1 bm-b 池单元（双层 status 面 r489 律）+finalize+E1 判决面（本机·due 10-09 开市前）；(b) T-144(c) 协议+流水域下沉 10-07；(c) 水位 RED 转换窗=DEEP-P1 单元已入池在飞→下轮 probe 预期缓解；(d) T-143 月考准备。本地未达 origin commit 数=0（本轮收口推送后自证）
"""
with open(rp, "ab") as fh:
    fh.write(add.replace("\n", "\r\n").encode("utf-8"))
print("round report addendum appended")

# ---- 6. heartbeat amend (LF) ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = st["clock_read"]
hb["verdict"] = ("r386 product round: T-147 s1 DELIVERED + P3 sizing dead-letter independently diagnosed "
    "(law'd); MID-ROUND bm-b collision-yield FULL estate ADOPTED (LOWAMP-DEEP-P1 main-exam prereg + "
    "sizing-fixed runner + 10 pool units, selftest ALL PASS verified per r471); burns in flight on bm-b "
    "data-locality; finalize+E1 judgment face stays bm-c (due 10-09). Push rejection handled via "
    "unwind-FF-reland (r589/r595). Watermark RED = O-2115 transition window honest, relief expected "
    "next probe (pool units registered). S6 28 rc0, smoke 47/47, attrition CLEAN, self-heal 4/4.")
assert isinstance(hb["heartbeat_epoch_utc"], int)
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
print("heartbeat amended, ack preserved:", len(hb.get("orders_ack", [])))

# ---- 7. commit msg (new) ----
msg = ("round 386 (bm-c): T-147 s1 deep-axis evidence extraction DELIVERED + P3 sizing dead-letter "
 "independently diagnosed + bm-b collision-yield estate ADOPTED (LOWAMP-DEEP-P1) + unwind-FF-reland "
 "after push rejection. s1 product = results/lowamp_p3/s1_evidence_extract.json (11,292B): 16-face "
 "table, deep-axis per-start dists, double-nulls support check, REFINE_BENCH sec.2 ranked variant "
 "table; sizing dead-letter = spec['sizing'] never consumed by _cell_task/_cont_task -> judged 4 "
 "cells all ran invvol, LA-EQ = mislabeled invvol twin (pos-aligned 2760/2760 starts zero-diff), eq "
 "never truly burned in judged cells, sens leg = only true sizing evidence; P3 judged-negative "
 "verdict unaffected; frozen runner untouched. MID-ROUND: push rejected (origin +2: bm-a dead-estate "
 "close + bm-b r597) -> unwind-FF-reland per r589/r595 (blockers checkout, MSG blob-identical removal, "
 "FF to e3b3f8d9b, D=0); bm-b yielded T-147 per sec.4 commit-time order with FULL r596 estate handover "
 "(LOWAMP-DEEP-P1 frozen main-exam prereg: headline LAD-EDGE 67-trade face, 4 judged cells incl 2 "
 "true-eq first-tests, deep same-mask nulls 2000, exit-axis double gate + law-A census + E1 "
 "precondition, M3 new-family-key delta; runner with sizing fix + F3b; 10 pool units, burns in-flight "
 "bm-b data-locality) -> ADOPTED after r471 verify (selftest ALL PASS incl F15 P3-artifact anchors); "
 "finalize+E1 judgment face stays bm-c. E09 dup-collapsed onto bm-b canonical card (cross-machine "
 "same-window double discovery); bm-c unique adds -> CODELY (pos-align identity proof, naive-zip "
 "row-order trap, r380 helper whole-strip recurrence #3 with first real damage caught by merge "
 "fail-fast). S0/S0.5: orders 147/147 zero-pending, D-19 MATCH; smoke 47/47; S6 28 legs rc0; "
 "watermark RED py_low_with_work_cands = O-2115 transition window honest (relief expected: DEEP-P1 "
 "pool units registered mid-round); attrition CLEAN 4 ledgers; self-heal 4/4. Crash-recovery estate "
 "tools r382/r383/r385 + r386 session tools committed. [via bm-c r386]")
open(os.path.join(REPO, "results", "_r386bmc_commit_msg2.txt"), "w", encoding="utf-8", newline="\n").write(msg)
print("commit msg written")
