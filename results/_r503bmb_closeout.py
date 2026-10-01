import json
import time
import datetime

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# ---- state.json (bm-b) ----
p = "state.json"
d = json.load(open(p, encoding="utf-8"))
d["round_no"] = 503
d["note"] = ("r503: furnace elig semantic re-pin (prereg SA1) -> LOWAMP 144/144 done + REV/LOWAMP finalize (n=121/n=144, robust=0/0 honest negatives); "
             "daemon claim push deadlock broken (7-commit pile rebased+pushed, origin 3c97fffe8) -> claim OK 12:34, MOM unfuse relaunch; "
             "watermark py_low_with_work_cands remediated; S6 42 legs rc0 + monthly trio idempotent rerun; D-19 753F99E8 MATCH-unchanged")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at", "last_decisions_at"):
    d[k] = now
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
d2 = json.load(open(p, encoding="utf-8"))
assert d2["round_no"] == 503 and d2["last_decisions_sha"].upper() == "753F99E81A27DB3E1B4F2C76CD991CA50D52B80AA7FAA63D6412CC2DA1F5FB01"
print("state ok round", d2["round_no"])

# ---- heartbeat fleet/machines/bm-b.json ----
p = r"fleet\machines\bm-b.json"
h = json.load(open(p, encoding="utf-8"))
h["last_seen"] = now
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
h["current_task"] = "r503 closeout: furnace elig semantic re-pin landed, LOWAMP 144/144 + MOM relaunch racing, REV/LOWAMP finalize done"
h["round_no"] = 503
h["loop_round"] = 503
h["verdict"] = ("r503 products: furnace elig semantic re-pin (SA1, universe byte-identical evidence) + LOWAMP-108 burn complete "
                "(144/144, harvest+entry flips) + REV/LOWAMP family finalize (robust=0/0 honest negatives) + daemon push-deadlock "
                "broken (7-commit pile -> origin 3c97fffe8) + S6 42 legs rc0")
try:
    import psutil
    h["free_ram_gb"] = round(psutil.virtual_memory().available / (1 << 30), 1)
    h["idle_ram_gb"] = h["free_ram_gb"]
    h["ram_free_gb"] = h["free_ram_gb"]
    h["cpu_util_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass
json.dump(h, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
h2 = json.load(open(p, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]
print("heartbeat ok epoch-int", isinstance(h2["heartbeat_epoch_utc"], int), "ram", h2.get("free_ram_gb"))

# ---- round report line ----
line = (now + " | r503 bm-b | dept:研究/策略 | "
        "[watermark verdict: 12:27 探针 RED=runnable-work-idle-low-cpu——可跑批唯一候选=STOCKFURN 5 分片全被 elig raw-sha 假阳性 fuse；"
        "本轮根治=语义钉+re-probe+prereg §A1；12:34:15 起实测解除：LOWAMP-108 claim OK pushed→launch→12:36:03 harvest+entry 双翻 144/144 done→MOM 熔断清→续烧中] | "
        "本轮主产出（实物）："
        "(1) scripts/stock_face_furnace.py 语义钉修复——r502 收尾 S6 日快照（12:13）轮换 eligibility.csv 字节→raw-sha 探针假阳性→LOWAMP-108/MOM-0/MOM-4 三分片 crash-fuse+daemon claim push 非FF×脏树 rebase 拒死锁（7 孤儿 claim commit）；"
        "定谳=eligible 码集 7273/7273 逐位恒等+mask 零 diff（消费面未变）；修法=elig_face_sha16（_universe 消费码集哈希·raw sha 降 provenance·码集增删仍 fail-closed）+re-probe 12:28:26 面等价复核（universe_n 3514/panel_rows 3242/elig_median 1565.5 逐值恒等）+prereg §A1 修订（数据面再锚·判据零改动·已烧/续烧分界披露）；"
        "(2) LOWAMP 尾分片烧毕（144/144）+REV/LOWAMP finalize 落地：rev_summary n=121 robust=0（预期假阳性~6.1）、lowamp_summary n=144 robust=0（预期~7.2）——双族诚实负结果（robust 门=双 nulls p<0.05+同号+验证窗 Sharpe>0；§5 预测面=REV 首阳轴负增量证真+LOWAMP「三族最强」在个股全 A 面证伪），负结果照报=REFINE_BENCH §3 合法产出，零判决宣称零 skill_line 零纸盘开舱照 prereg；"
        "(3) daemon push 死锁破局：7 孤儿 commit rebase（1 UU=pool_core_samples.jsonl ts 序 union 解·resolver 留痕 results/_r503bmb_union_resolver.py·r501 假拒净路 commit -C 再实证）+round commit 推 origin 3c97fffe8→daemon claim OK 12:34:15；"
        "(4) S6 42 腿全 rc0（reconcile ZERO-DRIFT streak 5/3·clock ORANGE_COOL·collectors 车道护栏诚实跳过·LIVE/REPORT 当日再生）+月度三件套幂等重跑（r502 记载今晨 09:12 已毕·本轮重 derive 零双计如实注记） | "
        "验证：S1 47/47；probe rc0；finalize 双 rc0；attrition scan CLEAN（4 台账·1 healed 照录）；schtasks 双任务健康（pin=2 no-op·watchdog S4U）；pre-commit claw OK；D-19 753F99E8 MATCH-unchanged（python raw-bytes·temp partial clone）；orders 轮首+S7 双扫 EMPTY（C-01 fleet transfer order 仍未落件·持续观察）；本地未达 origin commit 数=0 | "
        "坑律（S4 已入 CODELY.md 一条）：S6 日刷数据面×prereg raw-file 钉=假阳性 drift 熔断族（钉实际消费面勿钉整文件字节）；观察项=autofill _runner_alive 无 args 面（probe 误判 runner alive 挡 launcher 一 tick·本轮侥幸当锁） | "
        "下轮指针：(1) MOM 16 格烧完→finalize mom→T-139 三族 verdict/census ranking 面对（bm-a r512 REV ranking 先例·窗≤48h）(2) r297 daemon push-blocked 暂停新认领 guard 评估（本轮 yield 行为正确但孤儿 commit 堆积面）(3) 观察项持续：token crash-fuse 45 sigs 历史惰性面 | "
        "executive 三行面：当前活=股票炉三族收口（MOM 分片续烧中）；最近实物=results/stock_face_furnace/{rev,lowamp}_summary.json@12:39（121+144 格双 nulls 排序表）+origin 3c97fffe8；下个里程碑=T-139 三族 finalize 全落+股票语法显著带判定（窗≤48h·下轮起）"
        )
with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("round report appended", len(line))
