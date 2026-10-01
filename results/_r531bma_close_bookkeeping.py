"""r531 bm-a round close: state/heartbeat/report/CODELY bookkeeping (surgical, format-preserving)."""
import json, os, time, datetime

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

def rw(path, fn):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    txt = raw.decode("utf-8")
    txt = fn(txt)
    data = txt.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    with open(path, "wb") as f:
        f.write(data)

# --- state-bm-a.json ---
def state_fn(t):
    d = json.loads(t)
    d["round_no"] = 531
    d["did"] = ("r531 bm-a: r530 crashed-session W18 freeze adopted (r314 law: liveness 3-check, "
                "ADMIT independently re-verified vs HEAD 15-row table incl. r529 N3 leg) + W18 prereg + "
                "n1 W18 materializer selftest leg + canon sec.4 row + banned gate ADMIT + freeze; "
                "push collision with bm-b W19 v3 re-band same-window -> CONSTRUCTIVE merge (theirs base "
                "+ 3 anchored blocks; mechanical hunk-union frankenstein caught), bands machine-verified "
                "DISJOINT contiguous 76_001..82_000, W19 stale prior-wave pin minimal disclosed fix (+18), "
                "surgical commit-tree replay 3a46f2b51 onto 431373dc; engine ignited W18 12-shard burn "
                "in flight (~60s/shard); S6 36 legs rc0 holiday no-op honest")
    d["verify"] = ("ADMIT reverify receipt + merge AST/compile/selftest 3-face (n1 W18+W19 dual faces, "
                   "pf 8/8, engine 7 legs) + smoke 47/47 pre-freeze + S6 36/36 rc0 + dualrun "
                   "ZERO-DRIFT streak 8/3 + attrition CLEAN + claw MATCH + origin==local 3a46f2b51")
    d["next"] = ("r532: W18 finalize window after 12/12 (S5 four-prediction verdicts + S7/S8 backfill + "
                 "ledger append +2,200 -> 404,148 expected + skill_line K-lift @37,520); W19=bm-b "
                 "finalize ordered AFTER W18 finalize (FAIL-CLOSED cumulative dep); 10-03 RW-5 -> "
                 "T-126 REEVAL18 prereg; N3-R2 draft second; CODELY 77.5KB water-level flag (GM face)")
    d["current_task"] = ("r531 closed: W18 EIGHTH engine wave frozen + merged with bm-b W19 v3 "
                         "(both stand, disjoint bands); W18 burn in flight")
    d["updated"] = iso
    d["last_round"] = 530
    d["last_round_at"] = "2026-10-01T18:24:11+08:00"
    return json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if not t.endswith("\n") else "\n")

rw(os.path.join(REPO, "state-bm-a.json"), state_fn)

# --- heartbeat fleet/machines/bm-a.json ---
def hb_fn(t):
    d = json.loads(t)
    d["last_seen"] = iso
    d["current_task"] = ("r531 closed: W18 EIGHTH engine wave frozen (adopted r530 crash draft after "
                         "ADMIT re-verify) + constructive-merged with bm-b W19 v3 re-band (disjoint "
                         "bands, both stand); W18 engine burn in flight; next = W18 finalize window")
    d["verdict"] = ("engine_wave W18 in flight (12-shard burn); board clear; rotation W20+ per law "
                    "sec.4; governance holds T-142/W14/N2-W15 unchanged (GM)")
    d["task"] = d["current_task"]
    d["heartbeat_epoch_utc"] = epoch
    d["clock_read"] = iso
    d["round_no"] = 531
    d["last_round"] = 530
    d["notes"] = ("r531: W18 freeze adopted from r530 crash (ADMIT re-verified); W18xW19 same-window "
                  "collision resolved by CONSTRUCTIVE merge (bands disjoint, both stand)")
    return json.dumps(d, ensure_ascii=False, indent=2) + "\n"

hb_path = os.path.join(REPO, "fleet", "machines", "bm-a.json")
rw(hb_path, hb_fn)

# --- round report append ---
report_line = (
    "2026-10-01T19:1x+08:00 | r531 | dept:策略/工程 | WM=insufficient_history（尾窗翻转采样面·"
    "board_clear 基线非红）｜当前活=W18 引擎波烧录在飞（引擎队列 12 分片·~60s/片·点火 18:5x 起）"
    "｜最近实物=PERPETUAL-N1-W18 冻结件集落 origin 3a46f2b51（prereg+canon §4 行+N1_BANDS+"
    "WAVE_CONFIGS+n1 W18 materializer 腿+ADMIT 双回执）+results/p2cal_ext/n1_w18/shard-*.json 烧录中"
    "｜下里程碑=W18 12/12→finalize 窗（§5 四项判定+§7/§8 回填+ledger +2,200→预期 404,148+"
    "skill_line K-lift@37,520·窗≤48h）+10-03 RW-5 解冻→T-126 prereg | did: (1) S0-1 锚定 bm-a+S0 "
    "fetch+rides commit c0c632b22 推送解阻+S0.5 双扫 orders 140/140 零未回执（README 非令件）+D-19 "
    "sha 753F99E8 MATCH 零新决策；(2) **主产品=W18 第八枚引擎波冻结**：r530 猝死会话遗产收编"
    "（r314 律 liveness 三查无活会话→ADMIT 独立复核 _r531bma_w18_admit_reverify.py vs HEAD 15 行"
    "真值面全绿复现=r322 悬空引用核查→补 prereg 件+n1 W18 腿（r529 N3 种子集腿含）+canon 行→"
    "banned gate ADMIT→冻结 commit）；(3) **W18×W19 同窗双冻撞面收口**：push 撞 bm-b W19 v3 "
    "re-band（23667218e 18:54）→机械 hunk-union 乱序 frankenstein 当场抓回（AST 坏）→**构式合并"
    "正法**（theirs 底+我三块内容锚定插入）+W19 腿 stale prior-wave pin 最小披露修（no 15/18→+18"
    "·derive 律原文不动）→带域机证双波不相交连续 76_001..82_000（同带才让路·异带共存=W17xW19 判例"
    "边界）→外科 commit-tree 推 3a46f2b51（parent 431373dc=bm-c r329 中段增量·未碰我三件核验）→"
    "selftest 三面绿（n1 W18+W19 双 face/pf 8/8/engine 7 legs）；(4) 引擎实点火验证（r325 律产物面"
    "非 state 面）：materialize→1of12 18:5x 点火→shards_done_total 19→28 增长实证；(5) S6 36 腿 rc0"
    "（dualrun ZERO-DRIFT streak 8/3·假日采集全 no-op 合法·scorecard/dscore/build_status host=bm-a "
    "再生·REPORT/LIVE-2026-10-01 再生） | verify: ADMIT 复核回执+merge AST/selftest 三面+smoke "
    "47/47+S6 36/36 rc0+心跳 epoch int json.loads 自证 | 计分：2 分（W18 冻结件集+引擎烧录=能跑能"
    "看实物）·记账 4 处 | 本地未达 origin commit 数=commit 后自证 | next: r532 W18 finalize 窗"
    "（12/12 后）+W19 finalize 序（FAIL-CLOSED 待 W18 先行）+10-03 T-126 门 [via bm-a]\n")
rp = os.path.join(REPO, "round_reports-bm-a.md")
raw = open(rp, "rb").read()
crlf = b"\r\n" in raw
with open(rp, "ab") as f:
    data = report_line.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    f.write(data)

# --- stale n1_w19 old-band shards: discard per yield ruling (untracked locally,
#     not tracked on origin at 23667218e/431373dc/HEAD; provenance = git history
#     at c0c632b22 rides commit; content = old-band 76_001..78_000 products) ---
n19 = os.path.join(REPO, "results", "p2cal_ext", "n1_w19")
removed = []
if os.path.isdir(n19):
    for fn in os.listdir(n19):
        p = os.path.join(n19, fn)
        if os.path.isfile(p):
            os.remove(p)
            removed.append(fn)
    os.rmdir(n19)
print("stale n1_w19 discarded:", len(removed), "files (yield ruling, untracked, history-preserved)")

# --- heartbeat self-verify (epoch int law) ---
d = json.loads(open(hb_path, encoding="utf-8").read())
assert isinstance(d["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in d["clock_read"], "clock_read missing T separator"
print("heartbeat self-verify OK: epoch=", d["heartbeat_epoch_utc"], "clock=", d["clock_read"])
