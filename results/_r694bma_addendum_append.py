"""r694 bm-a addendum: round-report addendum + heartbeat posture lines
(yield state) + CODELY second pit line (whole-file needle collision)."""
import io
import json
import re
import time
import datetime

now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

addendum = (
    "2026-10-04T20:1x+08:00 | r694 (bm-a) addendum | 收口波实录（push-race+席位让路+双烧击杀·全链零 --no-verify 双爪零拦）: "
    "①push 首推被拒（bm-b r690 波 6 commits 19:42-19:49 同窗）→merge 17-UU per-face resolver "
    "（_r694bma_merge_resolve.py·runnable_pool=席位让路 theirs 正典〔bm-b MSG-1940 19:42:01 origin-first "
    "vs 本机 19:5x 后到让路·其条目载活烧认领 owner=bm-b 19:44:22·同 id/runner/args 实核零语义损失〕+CODELY 块级 union "
    "〔r453 全文行=他机热冷迁移面·指针在位→防 clobber 弃·本机坑律 1 行保〕+token_usage r466 per-key side_pick=0→整面 "
    "generated 新鲜度 ours 19:46:43>19:45:47+pool_core_samples 行级 union+12 再生面 ts-freshness）→commit f237983de "
    "→push_verify DELIVERED（tip==remote·ahead0 behind0）②**重复烧录事故当场自愈**: 本机 daemon 19:54:08 认领孤儿分片 "
    "generate-0of1（本机入池件的分片·merge 前窗）19:54:16 起烧 pid 50372=与 bm-b 活烧双机并发同批→本机后到=Stop-Process "
    "击杀（双形验死 CIM 全量+CSV·end-only 写面·candidates 未落零盘伤）③**sync_face settle 后孤儿分片 key-union 回流共享面** "
    "（owner=bm-a 残留认领=daemon 潜在重烧口）→双面外科摘除（共享+车道镜·**全文 needle 撞针实弹**: ' \"key\": "
    "\"generate-0of1\"' 在 TRIAL-LABOR-W2-GENERATE 史上分片同名·全文 find 首中=W2 done 分片错块——幸 per-entry 分片计数断言 "
    "fail-closed 零写入·锚定 N2 条目区后正删·r678 行级手术+seam 逗号缝合）→GENERATE 条目现仅存 n2-w15-generate-0of1 "
    "owner=bm-b 活烧正主④yield 事故 MSG-2026-10-04-2010-bma-all 发出⑤教训 2 条入 CODELY（入池席位动作 fetch 实核+公示窗"
    "等待窗·同 key 分片名跨批复用=needle 撞针面外科必锚定条目区）| 记分修正: r694 final=2（主产出=席位让路+双烧击杀+池面"
    "清创=可验协调证据实物〔同语义供给已由 bm-b 落地在飞·本机贡献=评审前置实核+selftest 17/17 复跑+事故零伤收口〕）| "
    "记账预算累计: 5/5+补 3（yield MSG+轮报补记+心跳 posture）| 本地未达 origin commit 数: __PUSH_STAMP2__ | "
    "登记册零命中: 本补记窗 treasure_guard 未触发（击杀=MSG 指令的活进程治理 r426 谱系·池外科=己方孤儿认领面）| "
    "下轮指针不变（W3 产物首查+N2 generate harvest 观察归 bm-b burner-side+trio finalize watch）"
)

codely2 = (
    "- [2026-10-04 20:1x r694 bm-a] 入池席位 fetch 实核窗+同 key 分片名跨批 needle 撞针律（r694 收口波两连实弹）："
    "①池面席位动作（入池/认领/开烧）=fetch 实核后仍有 15min 级 push-race 盲窗（本机 19:39 fetch→19:42 bm-b origin 先占"
    "→19:54 本机 daemon 撞认领开烧）——正法=入池前 MSG 公示后等一拍（≥5min 或下个 daemon tick）再 commit+daemon 认领门"
    "加『入场 ts 晚于最新 fetch 的条目=延后一 tick 认领』护栏候选；②shard key 跨批复用（generate-0of1 自 W2 先例抄入 N2）"
    "=全文级行手术 needle 撞针面——find 全文首中=W2 done 分片错块（幸 per-entry 计数断言 fail-closed 零写入零错删）；"
    "正法=池面行级手术 needle 一律锚定条目 id 区（entry_pos=find(id) 后再 find(needle, entry_pos)+唯一性断言）+分片 key "
    "命名带批次前缀（n2-w15-generate-0of1 形）禁裸复用先例名。How to apply: 新池条目分片 key 一律批次前缀形；池面手术脚本"
    "needle 先锚定条目区再找。"
)

# --- round report append ---
p = "round_reports-bm-a.md"
raw = io.open(p, encoding="utf-8", newline="").read()
assert raw.count("r694 (bm-a) addendum") == 0
with io.open(p, "a", encoding="utf-8", newline="") as fh:
    fh.write(addendum + "\n")
raw2 = io.open(p, encoding="utf-8", newline="").read()
assert raw2.count("r694 (bm-a) addendum") == 1
print("report addendum OK count=1")

# --- CODELY append ---
p = "CODELY.md"
raw = io.open(p, encoding="utf-8", newline="").read()
assert raw.count("入池席位 fetch 实核窗") == 0
with io.open(p, "a", encoding="utf-8", newline="") as fh:
    if not raw.endswith("\n"):
        fh.write("\n")
    fh.write(codely2 + "\n")
raw2 = io.open(p, encoding="utf-8", newline="").read()
assert raw2.count("入池席位 fetch 实核窗") == 1
print("codely pit line OK count=1")

# --- heartbeat posture lines (line surgery, eol re-emit per this window law) ---
p = "fleet/machines/bm-a.json"
raw = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw[:2000] else "\n"


def set_key(raw, key, val_json):
    pat = re.compile('^ "%s": .*?(,?)%s' % (re.escape(key), re.escape(eol)), re.M)
    hits = pat.findall(raw)
    assert len(hits) == 1, "key %s count=%d" % (key, len(hits))
    return pat.sub(' "%s": %s%s%s' % (key, val_json, hits[0], eol),
                   raw, count=1)


CUR = ("r694 close: N2 supply seat YIELDED to bm-b (19:42:01 "
       "origin-first); my duplicate orphan burn KILLED (pid 50372, "
       "end-only zero-disk); pool orphan-shard cleaned both faces; "
       "W3 judge verdict watch ETA ~22:1x")
VER = ("yield closed clean: bm-b canonical N2 generate live; local "
       "board-clear golden-week legal; W3 judge in-flight bm-c")
raw = set_key(raw, "current_task", json.dumps(CUR, ensure_ascii=False))
raw = set_key(raw, "verdict", json.dumps(VER, ensure_ascii=False))
raw = set_key(raw, "heartbeat_epoch_utc", str(epoch))
raw = set_key(raw, "clock_read", json.dumps(now_iso, ensure_ascii=False))
raw = set_key(raw, "last_seen", json.dumps(now_iso, ensure_ascii=False))
with io.open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(raw)
hb = json.loads(io.open(p, encoding="utf-8").read())
assert isinstance(hb["heartbeat_epoch_utc"], int)
assert hb["round_no"] == 694 and len(hb["orders_ack"]) == 154
print("heartbeat posture OK epoch=%d" % hb["heartbeat_epoch_utc"])
