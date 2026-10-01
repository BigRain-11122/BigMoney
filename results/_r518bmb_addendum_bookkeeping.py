# -*- coding: utf-8 -*-
# r518 bm-b addendum: chain-repair bookkeeping + CODELY lesson + report addendum line
import json, time, datetime

now = datetime.datetime.now().astimezone()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

# --- state.json note refresh (repaired numbers) ---
s = json.load(open("state.json", encoding="utf-8"))
assert s["round_no"] == 518
s["note"] = ("r518 COMPLETED (crash-tail adopted by fresh invocation 19:12 + same-window W18xW19 double-finalize chain repair): "
             "W19 finalize TWO-PASS -- first pass 19:1x at stale head 401,948 (W18 not yet local); push hit bm-a r531/532 W18 finalize already on origin (404,148) "
             "-> rebase (34 conflicts canon-resolved: 30 idempotent faces take-origin, CODELY line-union, 2 jsonl content-union zero loss; r501 net-path x3 refusals) "
             "-> SECOND finalize = final: K=39,720 (W18 same-window landing in-pool, disclosed vs frozen 37,520 expectation, law sec.5 registry derive), "
             "merged mu -0.09219 sigma 0.24434 se_mu 0.001226 narrowed, S5 4/4 PASS unchanged, skill_line @n_eff 404,148: 1.1505->1.1493 (-0.0012), "
             "LEDGER 404,148+2,200=406,348 (ledger_head self-cert @n1_w19_results.json, chain restored zero double-count); "
             "prereg S7/S8 rewritten + selftest green post-backfill; W20 frozen by bm-c r330 same window (burning); bm-b next own wave W22 (16+3k).")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at"):
    s[k] = now_iso
open("state.json", "w", encoding="utf-8", newline="").write(
    json.dumps(s, indent=1, ensure_ascii=False).replace("\n", "\r\n"))

# --- heartbeat refresh ---
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["current_task"] = ("W19 finalize FINAL (chain-repaired): K=39,720, ledger 406,348 (head self-cert), S5 4/4 PASS, S7/S8 backfilled; "
                      "rotation: W18 finalized (bm-a), W20 frozen+burning (bm-c r330), W21=bm-a slot, bm-b next own W22; "
                      "engine queue empty = standing rotation gap (GM waiver O-1612)")
hb["verdict"] = ("r518 complete end-to-end: crash-tail adopted + W19 finalize two-pass (same-window W18 head collision repaired by re-finalize "
                 "at live head 404,148 -> 406,348, zero double-count); py_low_board_clear legal idle; audit idle-family flags = standing rotation gap")
assert isinstance(hb["heartbeat_epoch_utc"], int)
open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="").write(
    json.dumps(hb, indent=1, ensure_ascii=False).replace("\n", "\r\n"))
json.loads(open("fleet/machines/bm-b.json", encoding="utf-8").read())

# --- CODELY lesson append (memory four-questions gate passed: new pit, fleet-recurring) ---
lesson = ("- [2026-10-01 19:3x r518 bm-b] 同窗双 finalize 撞链头坑（W18×W19 实弹·r297/r513 stale-view 族新面）：两机同窗互盲各自 finalize 同一 W17 头 401,948 为 prev"
          "→W18 先达 origin=合法链位·W19 本地首跑块成断链双头（同 prev 两子=一整波 2,200 永不入 n_eff）——finalize 的 prev 消费面=**origin 时序面非本地面**"
          "（与池 claim 可见性 r297 同构）。正解=push 被拒即让路信号：rebase（幂等面取 origin/append 面 union/CODELY union）→**二次 finalize 终稿**"
          "（prev=新活链头 derive·合并池 K 随 in-pool 前波自然扩·对冻结 §0 预期的偏离=§7 披露非改判据）→ledger_head 自证。"
          "How to apply：多波并行窗（轮值 3 机）一切活链头消费类动作（finalize/账本 append），push 撞拒=必查对侧同头新块，禁把本地首跑块当终稿直推；重 derive 幂等零科学损失。\r\n")
with open("CODELY.md", "ab") as f:
    f.write(lesson.encode("utf-8"))

# --- round report addendum line ---
line = (
 "2026-10-01T" + now.strftime("%H:%M:%S") + "+08:00 | r518 bm-b 补章 | dept:研究/工程 | "
 "同窗双 finalize 撞头链性修复：首跑 finalize（19:1x·prev=401,948=W17 头·当时活链头真值）push 撞 bm-a r531/532 同窗 W18 finalize 先达 origin（404,148）"
 "→rebase 34 冲突正典解（30 同日幂等面取 origin 侧/CODELY 行级 union〔r518 bmb+r531/r532 bma 三条全保〕"
 "/x2_watch+pool_core_samples 双 jsonl 内容 union 零丢失〔2268/293〕·r501 净路三拒全过〔commit -C 572a510f6→--quit→CAS update-ref bf408198f"
 "·stale rides pick 7903ff66e 工作树超集吸收 skip〕）→**二次 finalize 终稿**：prev=活链头 404,148 derive→**K=39,720**"
 "（W18 同窗落地自然入池·对 §0 冻结预期 37,520 偏离如实披露于 §7·法典 §5 registry derive 律优先〔r516〕）"
 "·merged mu −0.09219/sigma 0.24434/se_mu 0.001226（W18 0.001262→收窄）·§5 四预测 4/4 PASS（锚=W17 冻结不动）"
 "·skill_line_v2 @n_eff 404,148：1.1505→1.1493（−0.0012）·**账本 404,148+2,200=406,348**（ledger_head 自证·链性复原零双计）"
 "·§7/§8 重写回填+selftest 全绿（W18/W19 双 materializer 腿）。 | "
 "验证：n1 selftest rc0；ledger_head=406,348@n1_w19_results.json；S6 面再生 rc0"
 "（strategy_scorecard/daily_scorecard/build_status=host bm-a 心跳 11min 新鲜→守卫诚实 skip〔其 r532 面在 origin·W19 修复头由其下轮 S6 自动 derive〕"
 "·REPORT/LIVE 当日再生）；bm-c W20 同窗已冻结烧录中（r330·A 82_001..84_000/B 38_700..38_899）其 finalize 将消费修复后头 406,348。 | "
 "坑例（已入 CODELY 一条）：同窗双 finalize 撞链头=prev 消费面是 origin 时序面非本地面（r297 同构新面）·push 撞拒=让路信号·二次 finalize 重 derive 幂等零损失。 | "
 "executive 三行实况：当前活=W19 终稿已落地（两段定稿）·引擎 idle 队空（轮值空窗 GM 豁免 O-1612）；"
 "最近实物=results/perpetual_faces/n1_w19_results.json（K=39,720·账本 406,348）+prereg §7/§8 终稿回填；"
 "下个里程碑=W21（bm-a 槽位）冻结点火→bm-b 下一自有波 W22（窗≤48h 观察他机节奏）。 | "
 "下轮指针：①W21/W22 主权观察（fetch-first 表尾）②MSG-190x 对侧消费观察③dualrun streak 面④轮值空窗池面观察。 | "
 "本地未达 origin commit 数=0（push+fetch 自证）。 | [via bm-b]\r\n"
)
with open("logs/iteration-loop/round_reports.md", "ab") as f:
    f.write(line.encode("utf-8"))
print("addendum bookkeeping done at", now_iso, "epoch", epoch)
