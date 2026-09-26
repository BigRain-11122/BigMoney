"""r266 closeout: state bump + heartbeat + round report append (byte-face mirrored).

Faces (probed): state-bm-a.json + fleet/machines/bm-a.json = LF, no BOM, no
trailing newline; round_reports-bm-a.md = BOM + LF + trailing newline.
Roundtrip-assert each JSON face against the standing bytes BEFORE field edits
(fail-closed), heartbeat epoch must be JSON int (R170/R178) + clock_read
T-separated (R262).
"""
import datetime as dt
import json

now = dt.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%d %H:%M")
epoch = int(now.timestamp())
clock = now.isoformat()


def rewrite(path, mutate):
    raw = open(path, "rb").read()
    obj = json.loads(raw.decode("utf-8-sig"))
    bom = raw[:3] == b"\xef\xbb\xbf"
    crlf = b"\r\n" in raw
    for ind in (1, 2):
        for asc in (False, True):
            b = json.dumps(obj, indent=ind, ensure_ascii=asc).encode("utf-8")
            if crlf:
                b = b.replace(b"\n", b"\r\n")
            if bom:
                b = b"\xef\xbb\xbf" + b
            if b == raw:
                break
        if b == raw:
            break
    else:
        raise SystemExit(f"FAIL face probe {path}: no dumps recipe reproduces standing bytes")
    mutate(obj)
    out = json.dumps(obj, indent=ind, ensure_ascii=asc).encode("utf-8")
    if crlf:
        out = out.replace(b"\n", b"\r\n")
    if bom:
        out = b"\xef\xbb\xbf" + out
    json.loads(out.decode("utf-8-sig"))  # parse gate
    open(path, "wb").write(out)
    print(f"[ok] {path} rewritten (indent={ind}, ascii={asc}, crlf={crlf}, bom={bom}, {len(out)}B)")


# ---- state-bm-a.json: round bump ----
def st(o):
    o["round_no"] = 266
    o["did"] = ("R266 dead-round residue adopted + same-window double-fix yield: "
                "stash-pop 3-UU vs bm-b r269 unioned (jsonl 1129, criteria 34), "
                "sha-face P0 independent CRLF fix YIELDED to bm-b r270 LF-canonical "
                "root-fix (x4 sites + criteria re-anchor), T-83 s4 quarterly wiring adopted")
    o["verdict"] = ("R266: post_review re-derive 29 YES/0 NO/5 WAIT full green; "
                    "smoke 25/25; S6 all legs exit 0 weekend no-ops; watermark red=false "
                    "lane healthy; audit pool_starvation 45min adjudicated legal-idle per O-1137 "
                    "(weekend no-new-bar, judgment lines closed, no-fabrication law)")
    o["next"] = ("(1) 09-28 Monday new-bar chain (cutoff 09-24); (2) MF_IC_P1 IC batch "
                 "waits moneyflow panel completion (53/5222, bm-a lane self-heal) = the one "
                 "real pool payload; (3) 10-01 monthly trio + REGIME_GUARD v3 date gate "
                 "(governance-review slot already discharged, no double-run)")
    o["ts"] = o["last_round_ts"] = o["updated_at"] = o["last_run"] = o["last_round_at"] = o["updated"] = ts
    o["last_round"] = o["round_no"]
    o["current_task"] = "R266 closed (residue adoption + sha-fix yield)"


rewrite("state-bm-a.json", st)

# ---- heartbeat ----
def hb(o):
    o["last_seen"] = ts
    o["current_task"] = "R266 closed (residue adoption + sha-fix yield to bm-b r270)"
    o["heartbeat_epoch_utc"] = epoch
    o["clock_read"] = clock


rewrite("fleet/machines/bm-a.json", hb)
m = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(m["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in m["clock_read"], "clock_read must be T-separated (R262)"
print("[ok] heartbeat epoch int + clock T-sep self-verified")

# ---- round report append (BOM + LF + trailing newline) ----
line = (
    "2026-09-26 19:52 | R266 bm-a | (dept:工程/舰队) 水位=绿（watermark red=false lane=healthy；"
    "审计旗 pool_starvation 45min 结构性池饿——按 O-1137 白名单裁决如实呈：周末无新 bar、判线全闭、"
    "禁造数凑烧，唯一真载体=MF_IC_P1 待 moneyflow 面板完备 53/5222 阻断自愈中）。"
    "S0 死轮 R266 残骸收养（R241/R246 范式：run_192801 已结束于 19:32:47）：stash-pop 3-UU vs bm-b r269 "
    "按技能配方解（jsonl 行 union 1100+33+29=1129 零丢失、criteria items 33+1=34 单插入字节验证、"
    "REPORT re-derive 非手工）；post_review 3 NO（T-81 sha 跨机面）本机独立根修 CRLF 面后 push 撞 bm-b r270 "
    "同窗同 P0 双修——完备度裁决让路（checkout --ours 保 origin LF 正典 x4 站+判据重锚 fact-proof，"
    "union 保本机 T-83-S4 判据行+97 账本行零丢失，推前 amend 翻正消息 ee5a5d01）；"
    "T-83 s4 季度治理接线收养落地（票面 progress_r266 行级 splice 2+/1- 字节镜像保 escaped \\u00a7 面+散在 CR 尾、"
    "prompt 季度腿=活口令面、判据 T-83-S4-QUARTERLY-WIRING 4 检查注册）；S0.5 orders 83/83 双扫空、"
    "decisions D-09..11 零新行（R265 回执边界内）｜证据=commit ee5a5d01+re-derive 29 YES/0 NO/5 WAIT+"
    "smoke 25/25+S6 全链 exit 0（周末 no-op 群、regime ORANGE shadow、clock ORANGE_COOL sleeves 4/0、"
    "token delta=53）+results/_r266bma_{stashpop_resolve,rebase_resolve,t83_splice,rebase_probe}.py｜"
    "下轮指针：(1) 09-28 周一新 bar 链（cutoff 09-24）；(2) MF_IC_P1 面板完备后 IC 参考批=池饿真载体；"
    "(3) 10-01 月首轮三件套+REGIME_GUARD v3 日期门（治理审视槽位已 discharge 勿双跑）"
)
p = "logs/iteration-loop/round_reports-bm-a.md"
raw = open(p, "rb").read()
assert raw[:3] == b"\xef\xbb\xbf" and raw.endswith(b"\n"), "report face drifted"
open(p, "ab").write(line.encode("utf-8") + b"\n")
print("[ok] round report line appended")
