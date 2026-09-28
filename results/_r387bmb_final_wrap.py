# r387 bm-b final wrap: heartbeat touch (targeted fields, proven formulas)
# + round report addendum line for push-storm + storm-repair + lane re-mirror.
import json, os, time, datetime, io

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# ---- heartbeat targeted touch (resource fields kept from 14:33 write) ----
p = r"fleet\machines\bm-b.json"
h = json.load(open(p, encoding="utf-8-sig"))
h["last_seen"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = int(time.time())
h["current_task"] = (
    "r387 wrap: storm-repair landed (W1/W2-JUDGE shard status re-assert "
    "done 6a1ec060 + lane authority re-mirror 28ae07fa; autofill 14:33 "
    "stale keepalive regression closed both faces) -> next: W2 finalize "
    "(pid 23800) w2_judge.json harvest + entry done-flip -> W1 finalize "
    "detach -> W1 intake; 15:30 new-bar dual lanes; CEO 48h 09-29 22:45"
)
h["verdict"] = (
    "healthy: smoke 25/25; orders 99/99; S6 33 legs rc=0; storm face "
    "resolved in-window (shard done x2 re-asserted shared+lane, checkpoint "
    "evidence 149/404 re-verified zero science damage, idempotent-relaunch "
    "safety proven); W2 finalize in-flight pid 23800; W1 finalize queued "
    "behind (chain-linearity); CODELY 4 batch-reorgs verified zero-loss"
)
tmp = p + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
os.replace(tmp, p)
h2 = json.load(open(p, encoding="utf-8-sig"))
assert isinstance(h2["heartbeat_epoch_utc"], int)
assert "T" in h2["clock_read"]
print("heartbeat touch OK:", h2["clock_read"])

# ---- round report addendum ----
line = (
    f"{now_iso} | round 387 addendum bm-b | dept:工程 (push-storm 收口回执·"
    "三段) | 收口 push 拒 1（origin 进三件：bm-c r169 坑律条 2e51e974+本机 "
    "autofill 14:33 tick 双件 f4dbd31b/9f85b309 同窗）→ pull --rebase 撞 "
    "CODELY.md 单 UU→分类器 memory-union（我侧含 reorg 换行=前缀恒等败→手工"
    "定性正解：前缀 31 行恒等+bm-c r169 条 verbatim 保位+我方双条 verbatim "
    "并集→并集后 10,519B 复超线→五十四批当窗再整编（我方两条→archive 双指"
    "针·9,431B）→GIT_EDITOR=true continue→push LANDED d8a6e339）| 风暴次生"
    "面=池记账双重复原（14:33 tick 陈旧 keepalive 把 W1/W2-JUDGE shard status "
    "done→waiting·done_at/result_ref dict-merge 存活=浅损害·checkpoint 149/404 "
    "完备=重跑幂等零细胞 no-op 科学面零损）+我 14:33 轮尾 add -A 自吞回退面"
    "（tick 在我 mid-round push 后改写工作树）→storm-repair 双 status 重断言"
    "6a1ec060 推 LANDED→lane 权威面探测=14:34:51 tick rollback 字节还原仍持 "
    "waiting=14:43 tick 必复发→_pool_lane_sync 语义当窗补镜像 28ae07fa 推 "
    "LANDED=shared+lane 双 done+keepalive 代码跳 done+claim 只认 waiting=复发"
    "路径三重闭合 | verify: 分类器 1 件 GREEN 零 UNKNOWN+前缀恒等断言+verbatim "
    "计数=1 逐件+池 json 重载断言×2+lane json 重载断言+checkpoint 行数重验 149/"
    "404+CODELY 9,981B<10KB | 教训固化=CODELY r387 第三条（池修复双面同步律+"
    "add -A 前 reload 断言）| 14:43 tick 观察项：若 status 再回滚=autofill "
    "claim-refresh 结构性 bug→fix-first P0 票 [via bm-b]\n"
)
with io.open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("addendum line appended")
