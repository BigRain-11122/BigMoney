# r331 bm-b S7 close-out: state bump + heartbeat + round report line
import json, time, datetime, os

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

state = {
 "round_no": 331,
 "did": "R331(重跑场·15:10 场 25min 超时死亡未收尾): S0 tick-撞-rebase 死场收敛(designed-tail 丢弃+FF 27138221+salvage-union 零丢失: autofill 46/46+x2 774; resolver=_r331bmb_resolve.py; 本地尾 3b8bb712 丢弃有界留痕) + S3 主闭环 SINA_CONSTRUCT_P1 prereg DRAFT v0.1 起草落盘(MSG-1210 option-c 开工门开: bm-a ready-panel 收讫+本地 complete=true/N250 98.13% 复核; 五构造+行为偏差机制段+D6 三族实证+IC 三门 h10/IS167/OOS83+K100 null+极端日先验; 零引擎零账本) + F-04 认领 MSG 落 inbox 兼回执 + W2-A 复燃 45min 存活过崩点窗无新崩 + S4 tick-竞态坑律入册+CODELY 十七批整编 9608B + S6 32/32 rc=0",
 "verdict": "green",
 "next": "W2-A checkpoint/finalize 验证(再崩=count2 转 OOM 深探) + bm-a 执行车道裁定回执->scripts/sina_construct_ic.py 起草+SEED_REGISTRY 登记 SINA_CONSTRUCT_P1 + Mon 09-28 09:15 T-91 s3 首队列 + 15:30 T-87 astock 首拉+新 bar 全链(_r329bmb_s6_chain.ps1 周一形态直复用) + R335 5x HANDOVER + 10-01 月首轮三件套+REGIME_GUARD v3 日期门",
 "last_round_ts": iso,
 "last_result": "ok",
 "current_task": "W2-A rerun monitoring (pid13148) + sina_construct IC script drafting pending bm-a execution-lane pick + Mon T-91 s3/T-87 first-pull pre-armed",
 "updated_at": iso,
 "last_seen": iso,
 "ts": now.strftime("%Y-%m-%d %H:%M:%S"),
}
with open(r"logs\iteration-loop\state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

hb_path = r"fleet\machines\bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8-sig"))
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["round_no"] = 331
hb["round"] = 331
hb["loop_round"] = 331
hb["current_task"] = state["current_task"]
hb["verdict"] = "healthy"
hb["cpu_cores"] = hb.get("cpu_cores", 16)
hb["cores"] = hb.get("cores", 16)
try:
    import psutil
    hb["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 1)
    hb["idle_ram_gb"] = round(vm.available / 1e9, 1)
except Exception:
    pass
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat ok: epoch=%d(int) clock=%s round=%d ack=%d" % (chk["heartbeat_epoch_utc"], chk["clock_read"], chk["round_no"], len(chk.get("orders_ack", []))))

line = (
 "2026-09-27T16:0x+08:00 | r331 bm-b | dept:研究+数据+舰队 | 水位=绿 red=false@15:30:16 lane healthy（probe 15:14 py_low_with_work_cands=W2-A 燃程合法占用供给线；15:10 场 API 错误烧尽 25min 预算 15:35 被 kill 未收尾=本轮 331 重跑场）| did: (1) S0 死场收敛：15:40:02 autofill tick 自提交撞穿我 S0 pull --rebase 中途（UU 被 tick git add 静默解+孤儿 8b01f718+abort 弹回 3b8bb712，reflog 定谳）→ 收敛=丢本地 keepalive 尾（designed-tail 有界留痕）+FF 至 27138221+salvage-union 零丢失回执（autofill launches 复合键 union 45+46→46·last_tick 15:40:02+x2 行级 +6→774，resolver=results/_r331bmb_resolve.py）(2) S0.5 双扫 orders 96/96 零未回执+集团/本司 decisions 两面零新行=诚实 no-op (3) S1 smoke 25/25 (4) S2 job_list 0+fleet tasks 0 open (5) S3 主闭环：**SINA_CONSTRUCT_P1 prereg DRAFT v0.1 起草落盘**（research/SINA_CONSTRUCT_P1.md——MSG-1210 option-(c) 开工门开：bm-a 15:07 ready-panel MSG 收讫+本地复核 panel.complete=true cutoff 09-24+accept 5/5+N250 普查 98.13%；五构造 TIER_r0/r1/r2/r3+MAIN=(r0_net+r1_net)/turnover R225 官方主力配方；α机制段=行为偏差勾选；D6 vs EM/ths/lhb 三族+批内=实证 max|corr|≥0.7 per-construct 拒收；IC 三门 V1 max(0.02,null p95)/V2 IC_IR≥0.30/V3 OOS 同号留存·h10 主口径 IS167/OOS83·资格 N≥150；K=100 同掩码置换 null+seed 基 SINA_CONSTRUCT_P1 待 SEED_REGISTRY 登记；极端日先验含 2026-01-19 涨跌停结构豁免路径；零引擎零持仓零账本；执行车道三选一工程面待 bm-a 裁定不触判据）+F-04 认领声明 MSG-20260927-1556 落 inbox（兼 ready-panel 回执+GM 抄送·MF_IC_P1 维持 parked）(6) W2-A 复燃监控：pid13148 45min 存活 CPU 1628s·已过 27min 崩点窗无新崩（log 尾 RuntimeWarning=NaN 良性面）·checkpoint 面未现=下轮验证 (7) S4 坑律入册（tick 自提交 vs 轮 git 操作竞态窗律：:X0:02 避窗/abort 后 designed-tail+FF+salvage 收敛/reflog 定谳留痕/根治向=tick rebase 感知）+CODELY 十七批当窗整编（r328/r329 verbatim 外迁 archive 202609.md·指针行留册·9608B<10KB 断言过）(8) S6 32/32 rc=0（_r329bmb 链谱系·周日 no-op 腿合法·_r331bmb_s6_chain.log）(9) S7 收尾：inbox 处理（bm-a ready-panel 收讫移 processed+回复 MSG-1556 落 inbox）+state round_no→331+心跳三面自证（epoch int/T 分隔/ack 96）| evidence: resolver 断言输出三连+SINA_CONSTRUCT_P1.md 落盘+smoke 25/25+S6 32x rc=0 链板+CODELY multiset 断言（十七批脚本输出 r328/r329 in_archive=True）| 下轮: W2-A checkpoint/finalize 验（再崩=count2→OOM/环境深探）；bm-a 执行车道裁定回执→scripts/sina_construct_ic.py 起草+SEED_REGISTRY 登记；周一 09:15 T-91 s3 首队列+15:30 T-87 astock 首拉+新 bar 全链（周一形态链直复用）；R335 5x HANDOVER；10-01 月首轮三件套+REGIME_GUARD v3 日期门"
)
rp = r"logs\iteration-loop\round_reports.md"
raw = open(rp, "rb").read()
eol = "\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else "\n"
if not raw.endswith(eol.encode()):
    raw = raw + eol.encode()
with open(rp, "wb") as f:
    f.write(raw + (line + eol).encode("utf-8"))
print("round report line appended, eol=%r, size=%d" % (eol, os.path.getsize(rp)))
