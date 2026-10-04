# -*- coding: utf-8 -*-
"""r515 bm-c close-2: close-window merge bookkeeping -- CODELY pit line,
state/heartbeat DID amendments, round-report addendum line. Byte-surgery
with EOL probes + assertions. Bloodline: _r515bmc_close.py / r485 law."""
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ts = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

CODELY_LINE = (
    "- [2026-10-05 05:2x r515 bm-c] **zealous-merge 冲突呈现面单侧公共尾坑（merge 窗新族·r505 v2 "
    "工作树重建律盲区·r515 收口窗 13-UU 实弹）**：git 默认 zealous 3-way merge 的冲突文件 `>>>>>>>` "
    "后「公共尾」可实为单侧内容（实弹=regime_state.json：theirs 后 45 行整段被当 common 发出·ours "
    "后半完全不在工作树文本）→「sides 一律从工作树重建」律产出可解析但混侧伪内容——phase-1（r512 "
    "血统）已写 6 面与 :2: blob CR 归一比对全分叉（parse 门只拦下 regime_state 一面·其余险些静默提交"
    "假内容）。正法=**merge 态完整侧源一律 index stage**（:1:/:2:/:3:·r701-③ 语义·r405 禁 stage 读="
    "rebase 面专用不适用）+工作树重建仅参考+写盘后 CR 归一恒等 stage blob 断言（r704 反读律扩展腿）。"
    "How to apply：复制 merge resolver 血统先加 stage 恒等校验腿；「resolve 后 parse 通过」≠「side "
    "完整」——zealous 盲区唯一可靠判据=与 stage blob 逐字节比对。")

ADDENDUM = (
    ts + " | r515-addendum | dept:工程（收口窗波合流+zealous 坑实弹治愈） | 收口窗实录: 开轮 commit "
    "aa39998aa 后 fetch behind=5（bm-b r711 族波轮中抵达：autofill trio keepalive×2+churn-absorb "
    "S6 34 腿产品 05:02 族+merge r711=bm-c r514 波合流）→merge-mode 13-UU S6 同族面停靠→phase-1 "
    "正典 resolver（r512 血统）踩 zealous 盲区（git 冲突呈现公共尾实为 theirs 单侧内容·ours 后半缺席"
    "工作树文本）→regime_state parse 门拦截·已写 6 面为可解析混侧伪内容（与 :2: blob 逐字节比对全分叉）"
    "→phase-2 stage 基 resolver（merge 态 :1:/:2:/:3: 完整侧源·r701-③）13/13 修复（8 take-ours "
    "ts-newer-wins·3 twin-lock·compute_audit history-union 201+203→204·token per-key-union）+反读"
    "==stage 断言 13/13+残留标记屏 13/13 PASS | 坑律入册: zealous-merge 单侧公共尾→CODELY.md r515 行"
    "（merge 态 resolver 必带 stage 恒等校验腿·parse 通过≠side 完整）；观察注记=regime_state 双机缩进分叉"
    "（bm-b 1-space vs bm-c 2-space 写器血统）=后续波窗复发源·下轮 census 面呈 GM | 记分:1（merge 修复="
    "实际文件改动）| 验证: results/_r515bmc_merge_resolve.json+_r515bmc_merge_resolve2.json 双回执+探针族 "
    "Tools/_r515bmc_regime_probe{,2,3,4}.py | 部门:工程")

DID_ADD = (
    " (8) close-window: post-commit fetch behind=5 (bm-b r711-family wave: autofill trio keepalive "
    "x2 + churn-absorb S6 34-leg 05:02 products + merge r711 of bm-c r514 wave) -> merge-mode "
    "13-UU S6-family stop. NEW PIT caught live: git zealous-merge conflict presentation emits a "
    "one-side-only pseudo-common tail (theirs back-half; ours back-half ABSENT from working-tree "
    "text) -> r505-v2 working-tree rebuild law blind spot: phase-1 (r512 lineage) rebuilt 6 faces "
    "as parseable-but-diverged frankensteins (vs :2: blobs), regime_state caught by parse gate -> "
    "phase-2 stage-based resolver (merge-mode :1:/:2:/:3: complete side source, r701-iii) repaired "
    "13/13: 8 take-ours ts-newer-wins (regime_state 05:10:18, update_status 05:10:17, "
    "REPORT/LIVE/b_layer/futures/lhb) + 3 twins locked + compute_audit history-union 201+203->204 "
    "+ token per-key union; read-back==stage assertions + residual screen 13/13 PASS; pit -> "
    "CODELY.md r515 line; regime_state indent divergence (bm-b 1-space vs bm-c 2-space writer "
    "lineage) = recurring-conflict source noted for next census.")

VERIFY_ADD = (
    " + close-window: results/_r515bmc_merge_resolve.json (phase-1 fail-stop receipt) + "
    "results/_r515bmc_merge_resolve2.json (phase-2 13/13 receipts) + probe family "
    "Tools/_r515bmc_regime_probe{,2,3,4}.py + merge commit (this close).")

# ---- CODELY.md pit line (byte append, EOL probe) --------------------------
cp = os.path.join(REPO, "CODELY.md")
raw = open(cp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
assert raw.rstrip(b"\r\n").decode("utf-8", "replace",).count("zealous-merge 冲突呈现面单侧公共尾坑") == 0, \
    "pit line already present (double-run)"
if not raw.endswith(b"\n"):
    raw += eol
raw += CODELY_LINE.encode("utf-8") + eol
with open(cp, "wb") as f:
    f.write(raw)
after = open(cp, "rb").read()
assert CODELY_LINE.encode("utf-8") in after, "codely append missing"
assert len(after) < 50 * 1024, "codely over 50KB watermark line (D-20260925-01-4)"

# ---- state + heartbeat amendments ------------------------------------------
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8-sig"))
assert st["round_no"] == 515
st["did"] = st["did"] + DID_ADD
st["verify"] = st["verify"] + VERIFY_ADD
st["last_round"] = st["last_round"] + " Close-window: merged bm-b r711-family wave (13-UU S6 faces, zealous-pit stage-repair 13/13)."
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["verdict"] = hb["verdict"] + DID_ADD
hb["activity_now"] = hb["activity_now"] + " + close-window merge of bm-b r711 wave (13-UU, zealous-pit stage-repair 13/13, pit -> CODELY)"
hb["latest_artifact"] = ("results/_r515bmc_merge_resolve2.json (13/13 stage-repair receipts) + "
                         "research/HANDOVER.md (r511-515 window line) + "
                         "results/_r515bmc_s6_log.txt (38 legs rc0)")
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- round report addendum (byte append, EOL probe) ------------------------
rp = os.path.join(REPO, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
with open(rp, "ab") as f:
    f.write(ADDENDUM.encode("utf-8") + eol)
assert ADDENDUM.encode("utf-8") in open(rp, "rb").read(), "addendum missing"

# ---- self-checks ------------------------------------------------------------
chk = json.loads(open(sp, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int)
chk2 = json.loads(open(hp, encoding="utf-8-sig").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int)
print("CLOSE2_OK", ts, "codely_len=", len(after), "eol=", repr(eol))
